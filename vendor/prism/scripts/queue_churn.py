#!/usr/bin/env python3
"""Merge-queue churn: evictions per merged pull request over a time window (#10429).

    python3 scripts/queue_churn.py                       # the last 24 hours
    python3 scripts/queue_churn.py --since 2026-10-05 --until 2026-10-06
    python3 scripts/queue_churn.py --hours 72 --json

An eviction is a ``RemovedFromMergeQueueEvent`` whose ``reason`` is anything but
``merged``: GitHub writes that event for a merge too, so the reason is what
separates the two. The reasons measured on this repository (2026-10-02 to
2026-10-07, 337 events) are ``merged``, ``failed_checks``, ``merge_conflict``
and ``manual``; a reason this script has never seen still counts as an eviction
and is printed as GitHub spelled it.

Who removed it comes from the event's ``actor``: a ``User`` is a person who
dequeued the pull request, anything else (the ``github-merge-queue`` bot) is the
queue evicting it. Both count in the rate, because both rebuild every group
behind the removed entry, and the output splits them.

The rate divides by the pull requests MERGED to the base branch in the window,
so it reads as "removals paid per merge". It is ``None`` with nothing merged.

Cost: one ``gh api graphql`` call per 100 pull requests updated since the
window opened (one or two for a day), and no per-PR call. It only reads.

What it cannot see: GitHub has no repository-wide list of queue events, so the
pull requests are found by ``updatedAt``, and a removal does not always move
that field. ``UPDATED_AT_SLACK`` covers the lag measured; a pull request evicted
and then left untouched for longer than that is missed.

Exit status: 0 measured, 3 the read failed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass

Runner = Callable[[list[str]], tuple[int, str, str]]

DEFAULT_REPO = "elastic/prism"
DEFAULT_BASE = "main"
DEFAULT_HOURS = 24.0
PAGE_SIZE = 100
# Removal events kept per pull request; one with more is reported as cut, not
# silently undercounted. The most measured on one pull request is 9.
TIMELINE_LAST = 50
# A removal can be newer than its pull request's ``updatedAt``: 2 of 135
# evictions measured 2026-10-02 to 2026-10-07 were, by 100 and 173 minutes. The
# paging therefore reads back this far past the window's start.
UPDATED_AT_SLACK = dt.timedelta(hours=6)
# A window this script would page forever for is a mistyped date, not a request.
MAX_PAGES = 30
MERGED_REASON = "merged"
# The rate above which the board warns. Measured on this repository: 0.24 over
# the quiet 24 hours to 2026-10-07 08:00Z (0.17 overnight), against 0.74 on
# 2026-10-05, 1.00 on 2026-10-04 and 0.90 on 2026-10-03, the days the queue cost
# hours. 0.30 is above the quiet reading and far below the bad ones.
ALARM_RATE = 0.30
# Below this many merges one eviction moves the rate by more than 0.20, so the
# rate says nothing yet.
ALARM_MIN_MERGED = 5

QUERY = """
query($owner: String!, $name: String!, $cursor: String, $prs: Int!, $events: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: $prs, after: $cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number
        updatedAt
        mergedAt
        baseRefName
        timelineItems(last: $events, itemTypes: [REMOVED_FROM_MERGE_QUEUE_EVENT]) {
          pageInfo { hasPreviousPage }
          nodes {
            ... on RemovedFromMergeQueueEvent {
              createdAt
              reason
              actor { __typename login }
            }
          }
        }
      }
    }
  }
}
"""


class Unreadable(Exception):
    """A read failed or answered in a shape this script does not know."""


def run_command(argv: list[str]) -> tuple[int, str, str]:  # pragma: no cover - I/O
    completed = subprocess.run(  # noqa: S603  # "gh" with a fixed argv built here
        argv, capture_output=True, text=True, check=False
    )
    return completed.returncode, completed.stdout, completed.stderr


def parse_time(value: str) -> dt.datetime:
    """An ISO date or timestamp; one with no zone is UTC, as GitHub's are."""
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.UTC)


def _stamp(moment: dt.datetime) -> str:
    return moment.astimezone(dt.UTC).strftime("%Y-%m-%dT%H:%MZ")


@dataclass(frozen=True)
class Eviction:
    number: int
    at: dt.datetime
    reason: str
    by: str  # "person" or "queue"
    actor: str

    def as_dict(self) -> dict[str, object]:
        return {
            "number": self.number,
            "at": _stamp(self.at),
            "reason": self.reason,
            "by": self.by,
            "actor": self.actor,
        }


@dataclass(frozen=True)
class Churn:
    repo: str
    since: dt.datetime
    until: dt.datetime
    merged: tuple[int, ...]
    evictions: tuple[Eviction, ...]
    cut: tuple[int, ...]  # pull requests with more removal events than were read

    @property
    def rate(self) -> float | None:
        return len(self.evictions) / len(self.merged) if self.merged else None

    @property
    def by_reason(self) -> dict[str, int]:
        return dict(sorted(Counter(e.reason for e in self.evictions).items()))

    @property
    def by_who(self) -> dict[str, int]:
        counts = Counter(e.by for e in self.evictions)
        return {"queue": counts["queue"], "person": counts["person"]}

    @property
    def repeats(self) -> dict[int, int]:
        """Pull requests evicted more than once in the window, with the count."""
        counts = Counter(e.number for e in self.evictions)
        return {n: c for n, c in sorted(counts.items()) if c > 1}

    @property
    def alarm(self) -> bool:
        rate = self.rate
        return (
            rate is not None
            and len(self.merged) >= ALARM_MIN_MERGED
            and rate > ALARM_RATE
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "repo": self.repo,
            "since": _stamp(self.since),
            "until": _stamp(self.until),
            "merged": len(self.merged),
            "evictions": len(self.evictions),
            "evictions_per_merged": self.rate,
            "by_reason": self.by_reason,
            "by_who": self.by_who,
            "evicted": [e.as_dict() for e in self.evictions],
            "evicted_more_than_once": {str(n): c for n, c in self.repeats.items()},
            "cut": list(self.cut),
            "alarm": self.alarm,
            "alarm_rate": ALARM_RATE,
            "alarm_min_merged": ALARM_MIN_MERGED,
        }


def fetch(runner: Runner, repo: str, since: dt.datetime) -> list[dict]:
    """Every pull request updated since ``since`` less the slack, newest first."""
    owner, _, name = repo.partition("/")
    floor = since - UPDATED_AT_SLACK
    found: list[dict] = []
    cursor: str | None = None
    for _ in range(MAX_PAGES):
        argv = ["gh", "api", "graphql", "-F", f"owner={owner}", "-F", f"name={name}"]
        argv += ["-F", f"prs={PAGE_SIZE}", "-F", f"events={TIMELINE_LAST}"]
        if cursor is not None:
            argv += ["-f", f"cursor={cursor}"]
        argv += ["-f", f"query={QUERY}"]
        code, stdout, stderr = runner(argv)
        if code != 0:
            raise Unreadable(f"gh api graphql: exit {code}: {stderr.strip()[:200]}")
        try:
            page = json.loads(stdout)["data"]["repository"]["pullRequests"]
            nodes = page["nodes"]
            more = page["pageInfo"]["hasNextPage"]
            cursor = page["pageInfo"]["endCursor"]
            reached = any(parse_time(node["updatedAt"]) < floor for node in nodes)
        except (KeyError, TypeError, ValueError) as error:
            raise Unreadable(f"gh api graphql: unexpected answer: {error!r}") from error
        found.extend(nodes)
        if reached or not more:
            return found
    raise Unreadable(
        f"more than {MAX_PAGES} pages of pull requests updated since {_stamp(floor)}"
    )


def measure(
    nodes: list[dict],
    since: dt.datetime,
    until: dt.datetime,
    *,
    repo: str = DEFAULT_REPO,
    base: str = DEFAULT_BASE,
) -> Churn:
    """Count merges and evictions in ``[since, until)`` from fetched pull requests."""
    merged: list[int] = []
    evictions: list[Eviction] = []
    cut: list[int] = []
    for node in nodes:
        if node["baseRefName"] != base:
            continue
        number = node["number"]
        merged_at = node["mergedAt"]
        if merged_at is not None and since <= parse_time(merged_at) < until:
            merged.append(number)
        timeline = node["timelineItems"]
        if timeline["pageInfo"]["hasPreviousPage"]:
            cut.append(number)
        for event in timeline["nodes"]:
            reason = event["reason"] or "unknown"
            at = parse_time(event["createdAt"])
            if reason == MERGED_REASON or not since <= at < until:
                continue
            actor = event["actor"] or {}
            evictions.append(
                Eviction(
                    number=number,
                    at=at,
                    reason=reason,
                    by="person" if actor.get("__typename") == "User" else "queue",
                    actor=actor.get("login") or "unknown",
                )
            )
    return Churn(
        repo=repo,
        since=since,
        until=until,
        merged=tuple(sorted(merged)),
        evictions=tuple(sorted(evictions, key=lambda e: (e.at, e.number))),
        cut=tuple(sorted(cut)),
    )


def _rate_text(churn: Churn) -> str:
    return "n/a (nothing merged)" if churn.rate is None else f"{churn.rate:.2f}"


def _reasons_text(churn: Churn) -> str:
    return " ".join(f"{reason}={count}" for reason, count in churn.by_reason.items())


def _repeats_text(churn: Churn) -> str:
    return " ".join(f"#{number} x{count}" for number, count in churn.repeats.items())


def render(churn: Churn) -> list[str]:
    who = churn.by_who
    lines = [
        f"queue churn {churn.repo} {_stamp(churn.since)} .. {_stamp(churn.until)}",
        f"merged: {len(churn.merged)}",
        f"evictions: {len(churn.evictions)} "
        f"(evicted by the queue: {who['queue']}, dequeued by a person: {who['person']})",
        f"evictions per merged PR: {_rate_text(churn)}",
    ]
    if churn.evictions:
        lines.append(f"by reason: {_reasons_text(churn)}")
        lines.append("evicted:")
        lines += [
            f"  #{e.number} {_stamp(e.at)} {e.reason} by {e.by} ({e.actor})"
            for e in churn.evictions
        ]
    if churn.repeats:
        lines.append(f"evicted more than once: {_repeats_text(churn)}")
    if churn.cut:
        cut = " ".join(f"#{number}" for number in churn.cut)
        lines.append(
            f"NOT-COUNTED-WHOLE more than {TIMELINE_LAST} removal events, "
            f"only the newest read: {cut}"
        )
    return lines


def warning_line(churn: Churn) -> str | None:
    """The board's one line, or None while the rate is under the threshold."""
    if not churn.alarm:
        return None
    hours = (churn.until - churn.since).total_seconds() / 3600
    who = churn.by_who
    line = (
        f"WARNING {churn.repo} queue-churn {_rate_text(churn)} evictions per merged PR "
        f"over {hours:g}h, above {ALARM_RATE:.2f}: {len(churn.evictions)} evictions "
        f"(queue {who['queue']}, person {who['person']}; {_reasons_text(churn)}) "
        f"for {len(churn.merged)} merged"
    )
    if churn.repeats:
        line += f"; more than once: {_repeats_text(churn)}"
    return line + " -- details: python3 scripts/queue_churn.py"


def window(
    now: dt.datetime, since: str | None, until: str | None, hours: float
) -> tuple[dt.datetime, dt.datetime]:
    end = parse_time(until) if until else now
    start = parse_time(since) if since else end - dt.timedelta(hours=hours)
    if start >= end:
        raise ValueError(f"--since {_stamp(start)} is not before --until {_stamp(end)}")
    return start, end


def churn_for(
    runner: Runner,
    repo: str,
    since: dt.datetime,
    until: dt.datetime,
    base: str = DEFAULT_BASE,
) -> Churn:
    return measure(fetch(runner, repo, since), since, until, repo=repo, base=base)


def main(
    argv: list[str] | None = None,
    *,
    runner: Runner = run_command,
    now: dt.datetime | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--repo", default=DEFAULT_REPO, help="owner/name")
    parser.add_argument("--base", default=DEFAULT_BASE, help="the queue's branch")
    parser.add_argument("--since", help="ISO date or time, UTC (default: --hours ago)")
    parser.add_argument("--until", help="ISO date or time, UTC (default: now)")
    parser.add_argument(
        "--hours",
        type=float,
        default=DEFAULT_HOURS,
        help="window length when --since is not given (default: 24)",
    )
    parser.add_argument("--json", action="store_true", help="one JSON object")
    args = parser.parse_args(argv)
    try:
        since, until = window(
            now or dt.datetime.now(dt.UTC), args.since, args.until, args.hours
        )
    except ValueError as error:
        parser.error(str(error))
    try:
        churn = churn_for(runner, args.repo, since, until, args.base)
    except Unreadable as error:
        print(f"UNKNOWN {args.repo} queue churn could not be read: {error}")
        return 3
    if args.json:
        print(json.dumps(churn.as_dict(), indent=2))
    else:
        for line in render(churn):
            print(line)
    return 0


if __name__ == "__main__":  # pragma: no cover - thin CLI wrapper
    sys.exit(main())
