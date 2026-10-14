"""Daily merge-queue churn metric (issue #10452).

Why this exists
---------------
Every churn fix on #10442 claims an effect and nothing measured it. The first
measurement was a hand-run GraphQL read, and it undercounted: it saw only the
pull requests that LATER merged. A pull request evicted and still open, or
closed, never entered the denominator or the numerator.

What it reports, per UTC day (and a window total)
-------------------------------------------------
* merged pull requests;
* merge-queue removals that are not a merge, split ``merge_conflict`` /
  ``failed_checks`` / ``other`` (``manual`` and any reason GitHub adds later
  land in ``other``, so the three buckets always sum to the total);
* evictions per merged pull request: evictions in the window divided by merges
  in the same UTC window, whichever pull request each belongs to;
* for every ``failed_checks`` removal, ONE cause: the failing job and the first
  failing test id of the ``merge_group`` run that failed nearest before it; the
  failing legs of that run are counted apart, as legs and not evictions;
* time from first entering the queue to merge, p50 and p90.

Sources
-------
Removals come from the GraphQL ``RemovedFromMergeQueueEvent`` timeline items
(the REST API has no merge-queue endpoint), read over ALL pull requests,
open and closed included. A removal whose reason is ``merged`` is the queue
completing, not churn, and is never counted.

The charged run is the failed ``merge_group`` run of that pull request's own
group created nearest before the removal, inside the stay that ended in it. An
earlier build of the same stay that failed and was rebuilt evicted nothing and is
not charged. The failing test is the first ``FAILED``/``ERROR path::test`` line
in the cause job's log; a gate job that only summarises (``test``) or a
non-pytest check (``audit-grep``) names no test, and is reported as such rather
than guessed at.

Output goes to stdout as Markdown (the workflow appends it to the run summary
and uploads it, the pattern ``flake-digest.yaml`` established). No data file is
committed: a committed data file is itself churn. ``--days N`` lets anyone run
it locally with an authenticated ``gh``.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from typing import Any

REASONS = ("merge_conflict", "failed_checks", "other")
NO_TEST = "(no test id in the log)"
NO_RUN = "(no merge_group run found)"
RUN_LIST_CAP = 1000
LOG_WORKERS = 8
FAILED_JOB_CONCLUSIONS = ("failure", "timed_out")
LOG_UNAVAILABLE = "(log unavailable)"
# The job that only summarises the legs; it fails alongside a real leg, so it is
# the cause only when nothing else failed.
GATE_JOB = "test"
# A queue event does not bump a pull request's ``updatedAt`` (measured: a removal
# 1h40 after it), so a stay on a PR untouched for days is found only by reading
# this far past ``since``.
QUEUE_LOOKBACK = timedelta(days=14)

_PRS_QUERY = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: 50, after: $cursor,
                 orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number state mergedAt updatedAt
        timelineItems(first: 100,
                      itemTypes: [ADDED_TO_MERGE_QUEUE_EVENT, REMOVED_FROM_MERGE_QUEUE_EVENT]) {
          pageInfo { hasNextPage }
          nodes {
            __typename
            ... on AddedToMergeQueueEvent { createdAt }
            ... on RemovedFromMergeQueueEvent { createdAt reason }
          }
        }
      }
    }
  }
}
"""

# ``[gw0] [ 37%] FAILED path::test`` (live, xdist) or ``FAILED path::test - msg``
# (the short summary). Both name the same id; the first one wins.
# A fixture or collection error prints ``ERROR path::test`` and is as much a
# test id.
_FAILED_RE = re.compile(r"Z (?:\[gw\d+\] \[ *\d+%\] )?(?:FAILED|ERROR) (\S+::\S+)")


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def bucket_reason(reason: str | None) -> str:
    """Fold GitHub's removal reason (nullable in the schema) into the three buckets."""
    lowered = (reason or "").lower()
    return lowered if lowered in ("merge_conflict", "failed_checks") else "other"


def _percentile(sorted_values: list[float], pct: float) -> float | None:
    if not sorted_values:
        return None
    rank = max(1, math.ceil(pct / 100 * len(sorted_values)))
    return sorted_values[rank - 1]


def _empty_day() -> dict[str, Any]:
    return {
        "merged": 0,
        "evictions": dict.fromkeys(REASONS, 0),
        "evictions_per_merged": None,
    }


def _finish(day: dict[str, Any], minutes: list[float]) -> None:
    total = sum(day["evictions"].values())
    day["evictions_per_merged"] = total / day["merged"] if day["merged"] else None
    ordered = sorted(minutes)
    day["queue_to_merge_min"] = {
        "p50": _percentile(ordered, 50),
        "p90": _percentile(ordered, 90),
    }


def summarize(
    prs: list[dict[str, Any]], since: datetime, until: datetime
) -> dict[str, Any]:
    """Aggregate pull-request timelines into per-day rows over ``[since, until)``."""
    days: dict[str, dict[str, Any]] = {}
    cursor = since.replace(hour=0, minute=0, second=0, microsecond=0)
    while cursor < until:
        days[cursor.date().isoformat()] = _empty_day()
        cursor += timedelta(days=1)
    minutes: dict[str, list[float]] = {key: [] for key in days}
    failed_checks: list[dict[str, Any]] = []

    for pr in prs:
        events = sorted(pr["timelineItems"]["nodes"], key=lambda e: e["createdAt"])
        entered = [
            _ts(e["createdAt"])
            for e in events
            if e["__typename"] == "AddedToMergeQueueEvent"
        ]
        merged_at = _ts(pr["mergedAt"]) if pr.get("mergedAt") else None
        if merged_at is not None and since <= merged_at < until:
            key = merged_at.date().isoformat()
            days[key]["merged"] += 1
            if entered:
                minutes[key].append((merged_at - min(entered)).total_seconds() / 60)
        last_entry: str | None = None
        for event in events:
            at = _ts(event["createdAt"])
            if event["__typename"] == "AddedToMergeQueueEvent":
                last_entry = event["createdAt"]
                continue
            if (event["reason"] or "").lower() == "merged" or not since <= at < until:
                continue
            bucket = bucket_reason(event["reason"])
            days[at.date().isoformat()]["evictions"][bucket] += 1
            if bucket == "failed_checks":
                failed_checks.append(
                    {
                        "pr": pr["number"],
                        "queued_at": last_entry,
                        "removed_at": event["createdAt"],
                    }
                )

    total = _empty_day()
    for key, day in days.items():
        total["merged"] += day["merged"]
        for reason in REASONS:
            total["evictions"][reason] += day["evictions"][reason]
        _finish(day, minutes[key])
    _finish(total, [m for values in minutes.values() for m in values])
    return {"days": days, "total": total, "failed_checks": failed_checks}


def match_failed_runs(
    removal: dict[str, Any], runs: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """The ONE failed ``merge_group`` run of that PR's group to charge, as a list.

    The run created nearest before the removal, inside the stay that ended in it.
    Earlier builds of the stay failed because a pull request ahead of it was bad
    or were rebuilt; none of them evicted this one. Runs created together (one
    group build, several workflows) tie, and the one that failed first is charged.
    """
    if removal.get("queued_at") is None:
        return []
    start, end = _ts(removal["queued_at"]), _ts(removal["removed_at"])
    marker = f"/pr-{removal['pr']}-"
    inside = [
        run
        for run in runs
        if marker in run["head_branch"] and start <= _ts(run["created_at"]) <= end
    ]
    if not inside:
        return []
    nearest = max(_ts(run["created_at"]) for run in inside)
    tied = [run for run in inside if _ts(run["created_at"]) == nearest]
    return [min(tied, key=lambda run: (_ts(run["updated_at"]), run["id"]))]


def first_failing_test(log: str) -> str | None:
    """First ``path::test`` id a job log reports as FAILED or ERROR, or None."""
    found = _FAILED_RE.search(log)
    return found.group(1) if found else None


def _legs_before(
    jobs: list[dict[str, Any]], removed_at: datetime
) -> list[dict[str, Any]]:
    """Failed jobs that had finished by the removal, earliest first.

    A leg that finishes after the removal did not cause it; the run keeps going
    for the pull requests behind.
    """
    done = [
        job
        for job in jobs
        if job["conclusion"] in FAILED_JOB_CONCLUSIONS
        and (job.get("completed_at") is None or _ts(job["completed_at"]) <= removed_at)
    ]
    return sorted(
        done,
        key=lambda job: _ts(job["completed_at"])
        if job.get("completed_at")
        else removed_at,
    )


def explain_failures(
    removals: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    jobs_of_run: Callable[[int], list[dict[str, Any]]],
    log_of_job: Callable[[int], str],
) -> list[dict[str, Any]]:
    """One row per removal: ``{pr, day, job, test, legs}``.

    ``job``/``test`` are the single cause (the first non-gate leg to fail before
    the removal); ``legs`` lists every non-gate such leg as ``{job, test}``.
    ``jobs_of_run`` and ``log_of_job`` are the two network reads, injected so the
    arithmetic above stays testable without them. An unreadable log is
    ``LOG_UNAVAILABLE`` for that leg and never ends the run.
    """
    plan: list[tuple[dict[str, Any], str, list[dict[str, Any]]]] = []
    for removal in removals:
        matched = match_failed_runs(removal, runs)
        legs = (
            _legs_before(jobs_of_run(matched[0]["id"]), _ts(removal["removed_at"]))
            if matched
            else []
        )
        plan.append((removal, removal["removed_at"][:10], legs))

    def read(job: dict[str, Any]) -> str | None:
        try:
            return first_failing_test(log_of_job(job["id"]))
        except GhError:
            return LOG_UNAVAILABLE

    # A pytest log is megabytes and a failed run has a failed leg per matrix cell,
    # so the log reads are the cost of the whole script: read them side by side.
    with ThreadPoolExecutor(max_workers=LOG_WORKERS) as pool:
        tests = iter(pool.map(read, [j for _, _, legs in plan for j in legs]))
    rows: list[dict[str, Any]] = []
    for removal, day, legs in plan:
        read_legs = [{"job": j["name"], "test": next(tests)} for j in legs]
        if not read_legs:
            rows.append(
                {
                    "pr": removal["pr"],
                    "day": day,
                    "job": NO_RUN,
                    "test": None,
                    "legs": [],
                }
            )
            continue
        real = [leg for leg in read_legs if leg["job"] != GATE_JOB]
        cause = (real or read_legs)[0]
        rows.append({"pr": removal["pr"], "day": day, **cause, "legs": real})
    return rows


def _fmt_ratio(value: float | None) -> str:
    return "n/a (nothing merged)" if value is None else f"{value:.2f}"


def _fmt_minutes(value: float | None) -> str:
    return "-" if value is None else f"{value:.0f} min"


def render(
    report: dict[str, Any], failures: list[dict[str, Any]], now: datetime
) -> str:
    today = now.date().isoformat()
    lines = [
        "## Merge-queue churn",
        "",
        f"Computed {now.strftime('%Y-%m-%dT%H:%MZ')}; the last day ({today}) is today, "
        "still in progress, so it and the window row are partial.",
        "",
        "| UTC day | merged | merge_conflict | failed_checks | other "
        "| evictions / merges, same UTC window | queue to merge p50 / p90 |",
        "|---|---|---|---|---|---|---|",
    ]
    labels = {today: f"{today} (partial)", "window": "window (includes partial today)"}
    for key, day in [*report["days"].items(), ("window", report["total"])]:
        ev, q = day["evictions"], day["queue_to_merge_min"]
        lines.append(
            f"| {labels.get(key, key)} | {day['merged']} | {ev['merge_conflict']} | {ev['failed_checks']} | {ev['other']} "
            f"| {_fmt_ratio(day['evictions_per_merged'])} | {_fmt_minutes(q['p50'])} / {_fmt_minutes(q['p90'])} |"
        )
    lines += ["", "### failed_checks evictions by cause (one cause per eviction)", ""]
    if not failures:
        return "\n".join([*lines, "None in the window."]) + "\n"
    lines += ["| evictions | check | first failing test |", "|---|---|---|"]
    causes = Counter((f["job"], f["test"] or NO_TEST) for f in failures)
    lines += [
        f"| {n} | {job} | {'-' if job == NO_RUN else test} |"
        for (job, test), n in causes.most_common()
    ]
    legs = Counter(
        (leg["job"], leg["test"] or NO_TEST) for f in failures for leg in f["legs"]
    )
    lines += ["", "### failing legs (not evictions)", ""]
    if not legs:
        lines.append("None.")
    else:
        lines += ["| failing legs | check | first failing test |", "|---|---|---|"]
        lines += [f"| {n} | {job} | {test} |" for (job, test), n in legs.most_common()]
    return "\n".join(lines) + "\n"


class GhError(SystemExit):
    """A ``gh`` call failed. A SystemExit so an unhandled one ends the run with
    its message; a caller that can go on without the read catches it."""


def _gh(args: list[str]) -> str:
    done = subprocess.run(  # noqa: S603  # `args` is a list reaching "gh" with no shell, from this file's own query strings
        ["gh", *args],  # noqa: S607  # "gh" resolved on PATH, as every workflow step resolves it
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode != 0:
        raise GhError(
            f"churn_metric: `gh {' '.join(args[:3])}` failed: {done.stderr.strip()[:300]}"
        )
    return done.stdout


def fetch_prs(repo: str, since: datetime) -> list[dict[str, Any]]:
    """Every PR with queue events since ``since``, each once, timelines whole or refused.

    Reads down to ``since - QUEUE_LOOKBACK`` by ``updatedAt`` because a queue
    event does not bump it. Keyed by number: the cursor drifts when a PR updates
    mid-read and the same PR can come back on the next page.
    """
    owner, name = repo.split("/")
    cut = since - QUEUE_LOOKBACK
    prs: dict[int, dict[str, Any]] = {}
    cursor: str | None = None
    while True:
        args = [
            "api",
            "graphql",
            "-f",
            f"query={_PRS_QUERY}",
            "-f",
            f"owner={owner}",
            "-f",
            f"name={name}",
        ]
        if cursor:
            args += ["-f", f"cursor={cursor}"]
        page = json.loads(_gh(args))["data"]["repository"]["pullRequests"]
        for pr in page["nodes"]:
            if _ts(pr["updatedAt"]) < cut:
                return list(prs.values())
            if pr["timelineItems"]["pageInfo"]["hasNextPage"]:
                raise SystemExit(
                    f"churn_metric: PR #{pr['number']} has over 100 queue events; raise the page size"
                )
            prs[pr["number"]] = pr
        if not page["pageInfo"]["hasNextPage"]:
            return list(prs.values())
        cursor = page["pageInfo"]["endCursor"]


def count_evictions(repo: str, since: datetime, until: datetime) -> dict[str, Any]:
    """Fetch every PR's queue timeline and count evictions per UTC day.

    The one eviction count for other scripts to import (``summarize``'s report:
    ``days``, ``total``, ``failed_checks``), so a second reader never re-derives it.
    """
    return summarize(fetch_prs(repo, since), since, until)


def fetch_failed_runs(
    repo: str, since: datetime, until: datetime
) -> list[dict[str, Any]]:
    """Failed ``merge_group`` runs, one UTC day per query so no day nears the 1000 cap.

    Starts a day early: a queue stay that began before ``since`` can end inside it.
    """
    runs: dict[int, dict[str, Any]] = {}
    day = since.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    while day < until:
        span = f"{day.strftime(fmt)}..{(day + timedelta(days=1)).strftime(fmt)}"
        out = _gh(
            [
                "api", "--paginate", "--slurp",
                f"repos/{repo}/actions/runs?event=merge_group&status=failure&per_page=100&created={span}",
            ]
        )  # fmt: skip
        found = [r for page in json.loads(out) for r in page["workflow_runs"]]
        if len(found) >= RUN_LIST_CAP:
            raise SystemExit(
                f"churn_metric: {span} hit the {RUN_LIST_CAP}-run list cap; narrow the span"
            )
        runs.update({r["id"]: r for r in found})
        day += timedelta(days=1)
    return list(runs.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Daily merge-queue churn metric (#10452)"
    )
    parser.add_argument(
        "--days", type=int, default=7, help="UTC days to report, ending with today"
    )
    parser.add_argument("--repo", default="elastic/prism")
    parser.add_argument("--now", help="ISO timestamp to treat as now (replays)")
    parser.add_argument(
        "--json-out", help="also write the machine-readable report here"
    )
    args = parser.parse_args(argv)
    if args.days < 1:
        parser.error("--days must be at least 1")

    now = _ts(args.now) if args.now else datetime.now(UTC)
    since = (now - timedelta(days=args.days - 1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    until = now + timedelta(seconds=1)

    report = count_evictions(args.repo, since, until)
    runs = fetch_failed_runs(args.repo, since, until) if report["failed_checks"] else []

    def jobs_of_run(run_id: int) -> list[dict[str, Any]]:
        out = _gh(
            [
                "api",
                "--paginate",
                "--slurp",
                f"repos/{args.repo}/actions/runs/{run_id}/jobs?per_page=100",
            ]
        )
        return [j for page in json.loads(out) for j in page["jobs"]]

    def log_of_job(job_id: int) -> str:
        return _gh(["api", f"repos/{args.repo}/actions/jobs/{job_id}/logs"])

    failures = explain_failures(report["failed_checks"], runs, jobs_of_run, log_of_job)
    sys.stdout.write(render(report, failures, now))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({**report, "failures": failures}, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
