#!/usr/bin/env python3
"""The efficiency ratchet: daily readings from GitHub data, held to baselines that may only improve (#10361).

    python .github/scripts/efficiency_ratchet.py                   # read GitHub, judge, print
    python .github/scripts/efficiency_ratchet.py --record in.json  # also keep every answer read
    python .github/scripts/efficiency_ratchet.py --replay in.json  # judge kept answers, read nothing
    python .github/scripts/efficiency_ratchet.py --post            # the workflow: post a finding

Run daily by ``.github/workflows/efficiency-metrics.yaml``. Every reading is
lower-is-better:

``queue-evictions-per-merged-pr`` (and ``evictions-per-merged-24h``, alarm only)
    merge-queue removals that are not a merge, per merged pull request, over 7
    days (24 hours), from ``churn_metric.summarize`` (the one eviction count;
    not re-derived here).
``queue-time-median``, ``queue-time-p90``
    minutes from first entry to the queue until merge, over 7 days, from the
    same summary.
``review-rounds-per-pr``
    verdict comments per reviewed pull request merged in 7 days. A verdict
    comment is one by a person whose first line is the verdict (``MERGE`` or
    ``FIX``) alone or after a ``review``/``verdict`` heading ending in a colon:
    see :data:`VERDICT_RE`. A merged pull request with no verdict is not in the
    denominator, and the count of them is printed.
``slowest-ci-job``
    minutes: the median duration of each ``ci.yaml`` job over its successful
    ``merge_group`` runs of the last 7 days (at most :data:`CI_RUNS_READ`), the
    largest of those medians.
``hot-file-prose-tokens``
    the token estimate ``bytes // 4`` (UTF-8 bytes, floor-divided by four: the
    proxy ``contributing/file-size-budget.md`` already uses) of ``CLAUDE.md``,
    each ``.claude/agents/*.md`` and ``CONTRIBUTING.md``, summed into one
    reading, read from the checked-out tree.

The names are the ``efficiency_metrics`` list of ``scripts/process_guards.json``
(#11032), the names a pull request's ``Efficiency-Metric:`` line may use.

The baselines are ``scripts/efficiency_baselines.txt``: ``<metric> <baseline>
<tolerance>``; a tolerance written ``0.5%`` is that share of the baseline. A
reading over baseline + tolerance is a REGRESSION. Raising a
baseline or a tolerance, or dropping a line, needs ``File-Size-Exception:
<metric> - <reason>`` in the pull request body, read by
``scripts/check_file_size.py`` as it reads a raised cap; lowering needs nothing.
The run prints each baseline a reading has beaten by more than its tolerance,
so a pull request can lower it: nothing is committed by the run.

A baselined metric whose reading is missing or empty is UNREAD, not a pass: its
watch is gone (``ci.yaml`` renamed, a verdict format changed), so the run
cannot judge it.

Two findings need no baseline: the CHURN ALARM, evictions per merged pull
request over 24 hours above :data:`CHURN_ALARM_RATE` with at least
``queue_churn.ALARM_MIN_MERGED`` merges, and the HOST REPORT check on the
newest comment on #10361 that BEGINS with :data:`HOST_REPORT_MARKER`: older than
:data:`HOST_REPORT_MAX_AGE` is STALE, none at all is UNREAD. That report is
posted by the coordinator host's nightly token job (#11031), since transcripts
are not in CI.

With ``--post``, the findings go to #10361 as ONE comment naming each metric,
before -> after, and its top contributors. The same set of findings is not
posted again within :data:`REPOST_AFTER` of the last such comment.

Exit status: 0 nothing regressed and the host report is fresh (a churn alarm
alone posts and still exits 0); 1 a regression or a stale host report; 3 a
baselined metric or the host report read nothing (each is named, and posted),
a read failed, or the baselines file is malformed: a metric could not be read.

What it cannot see: verdicts given as pull-request REVIEWS rather than
comments; a pull request with over 100 comments past its first 100 (it is
named, not guessed at); CI time of jobs that only run on ``pull_request``. An
unread metric is named, never judged: exit 3 says the run could not see it.

Where each rule lives:

- the rule, for readers: :data:`RULE_PAGE` (``contributing/efficiency-ratchet.md``)
- the baselines: ``scripts/efficiency_baselines.txt`` (:func:`parse_baselines`)
- the metric names: :data:`METRICS`, matching ``scripts/process_guards.json``
- a regression and an unread metric: :func:`judge`
- the churn alarm: :func:`churn_alarm`, with :data:`CHURN_ALARM_RATE`
- the host report, stale or unread: :func:`stale_host_report`
- the exit status: :attr:`Outcome.status`
- a raised or dropped baseline: ``scripts/check_file_size.py`` via
  :func:`raised_baselines`, cleared by ``File-Size-Exception: <metric> - <reason>``
- the daily run and its permissions: ``.github/workflows/efficiency-metrics.yaml``
- the tests: ``tests/test_efficiency_ratchet_10361.py``
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import statistics
import subprocess
import sys
import tempfile
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
for _path in (REPO_ROOT / ".github" / "scripts", REPO_ROOT / "scripts"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import churn_metric  # noqa: E402  (path is set up just above)
from queue_churn import ALARM_MIN_MERGED  # noqa: E402

Runner = Callable[[list[str]], str]

DEFAULT_REPO = "elastic/prism"
#: The issue the findings and the host token reports are posted on.
TRACKER_ISSUE = 10361
BASELINES_RELATIVE = "scripts/efficiency_baselines.txt"
#: The page that holds the rule; the comment, the baselines header and the
#: workflow header each point here.
RULE_PAGE = "contributing/efficiency-ratchet.md"

#: The maintainer's plan of 2026-10-09 on #10361: evictions per merged pull
#: request over 24 hours above this post an alarm, with or without a baseline.
CHURN_ALARM_RATE = 0.25
HOST_REPORT_MARKER = "<!-- host-token-report -->"
HOST_REPORT_MAX_AGE = dt.timedelta(days=8)
FINDING_MARKER = "<!-- efficiency-ratchet:"
REPOST_AFTER = dt.timedelta(days=7)
#: Successful merge_group runs of ci.yaml whose jobs are read.
CI_RUNS_READ = 10
CI_WORKFLOW = "ci.yaml"
#: How many contributors a finding names.
TOP = 3
#: The token estimate's formula, named in each prose reading's note.
ESTIMATE_FORMULA = "bytes // 4"

ALWAYS_LOADED = ("CLAUDE.md",)
AGENT_GUIDES_GLOB = ".claude/agents/*.md"
CONTRIBUTING = "CONTRIBUTING.md"

#: Every metric a baseline may name: the names ``scripts/process_guards.json``
#: lists under ``efficiency_metrics`` (#11032), which an ``Efficiency-Metric:``
#: line in a pull request body names. The 24-hour rate has no baseline: one bad
#: day is the churn alarm's to report, not the ratchet's.
METRICS = (
    "queue-evictions-per-merged-pr",
    "queue-time-median",
    "queue-time-p90",
    "review-rounds-per-pr",
    "slowest-ci-job",
    "hot-file-prose-tokens",
)

#: A verdict comment's first line, after ``*``, ``#``, ``>`` and backticks are
#: dropped: the verdict alone, or after a heading that names a review or a
#: verdict and ends in a colon. ``Handoff for the review FIX round`` and
#: ``Fix round at <sha>`` are not verdicts.
VERDICT_RE = re.compile(
    r"^(?:[^:\n]*\b(?i:review|verdict)\b[^:\n]*:\s*)?(?P<verdict>MERGE|FIX)\b"
)
_STRIP_RE = re.compile(r"[*#>`]")
_BASELINE_RE = re.compile(
    r"^(?P<metric>[a-z0-9-]+)\s+(?P<baseline>\d+(?:\.\d+)?)\s+(?P<tolerance>\d+(?:\.\d+)?)(?P<percent>%)?$"
)
_KEY_RE = re.compile(r"<!-- efficiency-ratchet: (?P<key>[^ ]*) -->")


class Unreadable(Exception):
    """A read failed, or the baselines file is malformed: the verdict is unknown."""


# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Baseline:
    metric: str
    value: float
    tolerance: float


def parse_baselines(text: str) -> dict[str, Baseline]:
    """``{metric: Baseline}``; comments and blank lines skipped, anything else refused."""
    found: dict[str, Baseline] = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = _BASELINE_RE.match(line)
        if match is None:
            raise Unreadable(
                f"{BASELINES_RELATIVE}:{number}: not '<metric> <baseline> <tolerance>'"
            )
        metric = match.group("metric")
        if metric not in METRICS:
            raise Unreadable(f"{BASELINES_RELATIVE}:{number}: unknown metric {metric}")
        if metric in found:
            raise Unreadable(f"{BASELINES_RELATIVE}:{number}: {metric} twice")
        value = float(match.group("baseline"))
        tolerance = float(match.group("tolerance"))
        if match.group("percent"):
            tolerance = value * tolerance / 100
        found[metric] = Baseline(metric, value, tolerance)
    return found


def raised_baselines(before: str | None, now: str | None) -> dict[str, str]:
    """``{metric: how}`` for each baseline or tolerance raised, or line dropped.

    What ``scripts/check_file_size.py`` asks a ``File-Size-Exception: <metric>``
    line for. A file absent at the base raises nothing, as a first cap file does.
    """
    if before is None:
        return {}
    was = parse_baselines(before)
    is_now = parse_baselines(now or "")
    raised: dict[str, str] = {}
    for metric, old in was.items():
        new = is_now.get(metric)
        if new is None:
            raised[metric] = f"baseline dropped; it was {old.value:g}"
        elif new.value > old.value:
            raised[metric] = f"baseline raised from {old.value:g} to {new.value:g}"
        elif new.tolerance > old.tolerance:
            raised[metric] = (
                f"tolerance raised from {old.tolerance:g} to {new.tolerance:g}"
            )
    return raised


# ---------------------------------------------------------------------------
# Readings (pure: every input is an answer already read)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Reading:
    metric: str
    value: float | None
    contributors: tuple[str, ...] = ()
    note: str = ""


def verdict_of(body: str) -> str | None:
    """``MERGE`` or ``FIX`` when the comment's first non-empty line is a verdict."""
    for raw in body.splitlines():
        line = _STRIP_RE.sub("", raw).strip()
        if line:
            match = VERDICT_RE.match(line)
            return match.group("verdict") if match else None
    return None


def _by_person(comment: Mapping[str, Any]) -> bool:
    author = comment.get("author") or {}
    return bool(author) and author.get("__typename") != "Bot"


def review_rounds(merged_prs: Sequence[Mapping[str, Any]]) -> Reading:
    """Verdict comments per reviewed merged pull request (see the module docstring)."""
    rounds: dict[int, int] = {}
    unreviewed = 0
    cut: list[int] = []
    for pr in merged_prs:
        comments = pr["comments"]
        if comments["pageInfo"]["hasNextPage"]:
            cut.append(pr["number"])
        count = sum(
            1
            for comment in comments["nodes"]
            if _by_person(comment) and verdict_of(comment["body"] or "") is not None
        )
        if count:
            rounds[pr["number"]] = count
        else:
            unreviewed += 1
    note = f"{len(rounds)} reviewed, {unreviewed} with no verdict comment"
    if cut:
        note += "; over 100 comments, first 100 read: " + " ".join(f"#{n}" for n in cut)
    if not rounds:
        return Reading("review-rounds-per-pr", None, (), note)
    top = sorted(rounds.items(), key=lambda item: (-item[1], -item[0]))[:TOP]
    return Reading(
        "review-rounds-per-pr",
        sum(rounds.values()) / len(rounds),
        tuple(f"#{number} {count} rounds" for number, count in top),
        note,
    )


def _minutes_between(start: str, end: str) -> float:
    return (churn_metric._ts(end) - churn_metric._ts(start)).total_seconds() / 60


def slowest_ci_job(runs: Sequence[Mapping[str, Any]]) -> Reading:
    """The largest per-job median, over the jobs of the runs read."""
    durations: dict[str, list[float]] = {}
    for run in runs:
        for job in run["jobs"]:
            if job.get("conclusion") != "success":
                continue
            started, completed = job.get("started_at"), job.get("completed_at")
            if not started or not completed:
                continue
            durations.setdefault(job["name"], []).append(
                _minutes_between(started, completed)
            )
    if not durations:
        return Reading("slowest-ci-job", None, (), "no successful job read")
    medians = sorted(
        ((statistics.median(values), name) for name, values in durations.items()),
        key=lambda item: (-item[0], item[1]),
    )
    return Reading(
        "slowest-ci-job",
        medians[0][0],
        tuple(f"{name} {minutes:.1f} min" for minutes, name in medians[:TOP]),
        f"median over {len(runs)} merge_group run(s) of {CI_WORKFLOW}",
    )


def token_estimate(data: bytes) -> int:
    """The named estimate, :data:`ESTIMATE_FORMULA`."""
    return len(data) // 4


def prose_tokens(root: Path) -> Reading:
    """The hot files' tokens summed: the always-loaded files and CONTRIBUTING.md.

    Each file is estimated on its own, then summed; the largest are named.
    """
    hot = [
        *(root / name for name in ALWAYS_LOADED),
        *sorted(root.glob(AGENT_GUIDES_GLOB)),
        root / CONTRIBUTING,
    ]
    sizes = {
        path.relative_to(root).as_posix(): token_estimate(path.read_bytes())
        for path in hot
        if path.is_file()
    }
    top = sorted(sizes.items(), key=lambda item: (-item[1], item[0]))[:TOP]
    return Reading(
        "hot-file-prose-tokens",
        float(sum(sizes.values())) if sizes else None,
        tuple(f"{path} {tokens}" for path, tokens in top),
        f"{len(sizes)} file(s), estimate {ESTIMATE_FORMULA}",
    )


def _queue_contributors(
    prs: Sequence[Mapping[str, Any]], since: dt.datetime, until: dt.datetime
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The most-evicted pull requests, and the longest queue-to-merge, in the window."""
    evicted: Counter[int] = Counter()
    waited: dict[int, float] = {}
    for pr in prs:
        events = pr["timelineItems"]["nodes"]
        entered = [
            e["createdAt"]
            for e in events
            if e["__typename"] == "AddedToMergeQueueEvent"
        ]
        for event in events:
            if event["__typename"] == "AddedToMergeQueueEvent":
                continue
            if (event["reason"] or "").lower() == "merged":
                continue
            if since <= churn_metric._ts(event["createdAt"]) < until:
                evicted[pr["number"]] += 1
        merged_at = pr.get("mergedAt")
        if merged_at and entered and since <= churn_metric._ts(merged_at) < until:
            waited[pr["number"]] = _minutes_between(min(entered), merged_at)
    most = sorted(evicted.items(), key=lambda item: (-item[1], -item[0]))[:TOP]
    longest = sorted(waited.items(), key=lambda item: (-item[1], -item[0]))[:TOP]
    return (
        tuple(f"#{n} x{c}" for n, c in most),
        tuple(f"#{n} {m:.0f} min" for n, m in longest),
    )


def queue_readings(
    prs: Sequence[dict[str, Any]], now: dt.datetime
) -> tuple[Reading, int, list[Reading]]:
    """The 24-hour rate with its merge count, and the 7-day queue readings."""
    day_since = now - dt.timedelta(hours=24)
    week_since = now - dt.timedelta(days=7)
    day = churn_metric.summarize(list(prs), day_since, now)["total"]
    week = churn_metric.summarize(list(prs), week_since, now)["total"]
    day_evicted, _ = _queue_contributors(prs, day_since, now)
    week_evicted, week_waited = _queue_contributors(prs, week_since, now)
    rate_24h = Reading(
        "evictions-per-merged-24h",
        day["evictions_per_merged"],
        day_evicted,
        f"{day['merged']} merged",
    )
    queue = week["queue_to_merge_min"]
    merged_note = f"{week['merged']} merged"
    return (
        rate_24h,
        day["merged"],
        [
            Reading(
                "queue-evictions-per-merged-pr",
                week["evictions_per_merged"],
                week_evicted,
                merged_note,
            ),
            Reading("queue-time-median", queue["p50"], week_waited, merged_note),
            Reading("queue-time-p90", queue["p90"], week_waited, merged_note),
        ],
    )


# ---------------------------------------------------------------------------
# Judging
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    #: "regression", "unread", "churn-alarm" or "stale-host-report".
    kind: str
    metric: str
    text: str

    @property
    def key(self) -> str:
        """What the repost check compares: the metric, the unread metric, or the kind."""
        if self.kind == "regression":
            return self.metric
        if self.kind == "unread":
            return f"unread:{self.metric}"
        return self.kind

    @property
    def fails(self) -> bool:
        return self.kind != "churn-alarm"


def _fmt(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}" if value < 10 else f"{value:.0f}"


def _top(reading: Reading) -> str:
    return f" Top: {', '.join(reading.contributors)}." if reading.contributors else ""


def judge(
    readings: Mapping[str, Reading], baselines: Mapping[str, Baseline]
) -> list[Finding]:
    """A regression for each reading over its baseline plus tolerance, and an
    ``unread`` finding for each baselined metric that read nothing: its watch is
    gone (a workflow renamed, a verdict format changed), which is not a pass."""
    findings: list[Finding] = []
    for metric, baseline in baselines.items():
        reading = readings.get(metric)
        if reading is None or reading.value is None:
            note = reading.note if reading is not None else "no reading at all"
            findings.append(
                Finding("unread", metric, f"`{metric}` read nothing ({note}).")
            )
            continue
        limit = baseline.value + baseline.tolerance
        if reading.value > limit:
            findings.append(
                Finding(
                    "regression",
                    metric,
                    f"`{metric}`: {_fmt(baseline.value)} -> {_fmt(reading.value)} "
                    f"(baseline {_fmt(baseline.value)} + tolerance "
                    f"{_fmt(baseline.tolerance)}; {reading.note}).{_top(reading)}",
                )
            )
    return findings


def lowerable(
    readings: Mapping[str, Reading], baselines: Mapping[str, Baseline]
) -> list[str]:
    """Each baseline a reading beat by more than its tolerance: lower it in a PR."""
    lines: list[str] = []
    for metric, baseline in baselines.items():
        reading = readings.get(metric)
        if reading is None or reading.value is None:
            continue
        if reading.value < baseline.value - baseline.tolerance:
            lines.append(
                f"{metric}: reading {_fmt(reading.value)} beats baseline "
                f"{_fmt(baseline.value)} by more than {_fmt(baseline.tolerance)}"
            )
    return lines


def churn_alarm(rate_24h: Reading, merged_24h: int) -> Finding | None:
    """The 24-hour alarm, which needs no baseline."""
    value = rate_24h.value
    if value is None or merged_24h < ALARM_MIN_MERGED or value <= CHURN_ALARM_RATE:
        return None
    return Finding(
        "churn-alarm",
        rate_24h.metric,
        f"`{rate_24h.metric}`: {_fmt(value)}, above {CHURN_ALARM_RATE:.2f} "
        f"({rate_24h.note}).{_top(rate_24h)}",
    )


def _comment_time(comment: Mapping[str, Any]) -> dt.datetime:
    return churn_metric._ts(comment["created_at"])


def stale_host_report(
    comments: Sequence[Mapping[str, Any]], now: dt.datetime
) -> Finding | None:
    """A finding when the newest host token report is too old, or there is none.

    A report is a comment that BEGINS with :data:`HOST_REPORT_MARKER`; a comment
    that only quotes it (a handoff naming the marker) is not one. With no report
    the host token readings were never read: ``unread``, not ``stale``.
    """
    reports = [
        c
        for c in comments
        if (c.get("body") or "").lstrip().startswith(HOST_REPORT_MARKER)
    ]
    limit_days = HOST_REPORT_MAX_AGE.days
    if not reports:
        return Finding(
            "unread",
            "host-token-report",
            f"the host token report is missing: no comment on #{TRACKER_ISSUE} "
            f"begins with `{HOST_REPORT_MARKER}`. The nightly host token job "
            "(#11031) produces it, so check that job ran; the readings it is "
            f"the source of cannot be judged (limit {limit_days} days).",
        )
    newest = max(reports, key=_comment_time)
    age = now - _comment_time(newest)
    if age <= HOST_REPORT_MAX_AGE:
        return None
    return Finding(
        "stale-host-report",
        "host-token-report",
        f"the newest host token report is {age.total_seconds() / 86400:.1f} days "
        f"old (limit {limit_days}): {newest.get('html_url', '')}",
    )


def finding_key(findings: Sequence[Finding]) -> str:
    return ",".join(sorted({f.key for f in findings}))


def render_comment(findings: Sequence[Finding], run_url: str) -> str:
    """The ONE comment a run posts."""
    lines = [
        f"{FINDING_MARKER} {finding_key(findings)} -->",
        f"**Efficiency ratchet: {len(findings)} finding(s)** ({run_url}).",
        "",
    ]
    lines += [f"- **{f.kind}** {f.text}" for f in findings]
    lines += [
        "",
        f"Baselines: `{BASELINES_RELATIVE}`; the rule: `{RULE_PAGE}`.",
    ]
    return "\n".join(lines) + "\n"


def should_post(
    comments: Sequence[Mapping[str, Any]], key: str, now: dt.datetime
) -> bool:
    """False when the newest ratchet comment, under :data:`REPOST_AFTER` old, has ``key``."""
    posted = [c for c in comments if FINDING_MARKER in (c.get("body") or "")]
    if not posted:
        return True
    newest = max(posted, key=_comment_time)
    match = _KEY_RE.search(newest.get("body") or "")
    recent = now - _comment_time(newest) < REPOST_AFTER
    return not (recent and match is not None and match.group("key") == key)


# ---------------------------------------------------------------------------
# Reading GitHub
# ---------------------------------------------------------------------------

_MERGED_QUERY = """
query($q: String!, $cursor: String) {
  search(query: $q, type: ISSUE, first: 50, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        number
        mergedAt
        comments(first: 100) {
          pageInfo { hasNextPage }
          nodes { author { __typename login } body }
        }
      }
    }
  }
}
"""


def run_gh(argv: list[str]) -> str:  # pragma: no cover - I/O
    completed = subprocess.run(  # noqa: S603  # "gh" with a fixed argv built here
        argv, capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise Unreadable(
            f"`{' '.join(argv[:3])}` exit {completed.returncode}: "
            f"{completed.stderr.strip()[:300]}"
        )
    return completed.stdout


def _stamp(moment: dt.datetime) -> str:
    return moment.astimezone(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_merged_prs(
    runner: Runner, repo: str, since: dt.datetime, until: dt.datetime
) -> list[dict[str, Any]]:
    """Every pull request merged to main in ``[since, until)``, with its comments."""
    query = (
        f"repo:{repo} is:pr is:merged base:main merged:{_stamp(since)}..{_stamp(until)}"
    )
    found: dict[int, dict[str, Any]] = {}
    cursor: str | None = None
    for _ in range(40):
        argv = [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={_MERGED_QUERY}",
            "-f",
            f"q={query}",
        ]
        if cursor:
            argv += ["-f", f"cursor={cursor}"]
        try:
            page = json.loads(runner(argv))["data"]["search"]
            for node in page["nodes"]:
                merged = node.get("mergedAt")
                if merged and since <= churn_metric._ts(merged) < until:
                    found[node["number"]] = node
            more, cursor = (
                page["pageInfo"]["hasNextPage"],
                page["pageInfo"]["endCursor"],
            )
        except (KeyError, TypeError, ValueError) as error:
            raise Unreadable(
                f"merged-PR search: unexpected answer: {error!r}"
            ) from error
        if not more:
            return sorted(found.values(), key=lambda node: node["number"])
    raise Unreadable("merged-PR search: more than 40 pages")


def fetch_ci_runs(
    runner: Runner, repo: str, since: dt.datetime
) -> list[dict[str, Any]]:
    """The newest :data:`CI_RUNS_READ` successful merge_group runs of ci.yaml, with jobs."""
    listing = json.loads(
        runner(
            [
                "gh", "api",
                f"repos/{repo}/actions/workflows/{CI_WORKFLOW}/runs?event=merge_group"
                f"&status=success&per_page={CI_RUNS_READ}&created=>={_stamp(since)}",
            ]
        )
    )  # fmt: skip
    runs: list[dict[str, Any]] = []
    for run in listing.get("workflow_runs") or []:
        pages = json.loads(
            runner(
                [
                    "gh", "api", "--paginate", "--slurp",
                    f"repos/{repo}/actions/runs/{run['id']}/jobs?per_page=100",
                ]
            )
        )  # fmt: skip
        jobs = [
            {
                k: job.get(k)
                for k in ("name", "conclusion", "started_at", "completed_at")
            }
            for page in pages
            for job in page["jobs"]
        ]
        runs.append({"id": run["id"], "jobs": jobs})
    return runs


def fetch_tracker_comments(runner: Runner, repo: str) -> list[dict[str, Any]]:
    """Every comment on #10361, newest last; only the fields judged are kept."""
    pages = json.loads(
        runner(
            [
                "gh", "api", "--paginate", "--slurp",
                f"repos/{repo}/issues/{TRACKER_ISSUE}/comments?per_page=100",
            ]
        )
    )  # fmt: skip
    return [
        {k: c.get(k) for k in ("created_at", "html_url", "body")}
        for page in pages
        for c in page
    ]


def fetch_answers(
    runner: Runner, repo: str, now: dt.datetime
) -> dict[str, Any]:  # pragma: no cover - I/O
    """Every answer the readings need, in the shape ``--record`` keeps."""
    week = now - dt.timedelta(days=7)
    return {
        "now": _stamp(now),
        "queue_prs": churn_metric.fetch_prs(repo, week),
        "merged_prs": fetch_merged_prs(runner, repo, week, now),
        "ci_runs": fetch_ci_runs(runner, repo, week),
        "tracker_comments": fetch_tracker_comments(runner, repo),
    }


# ---------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------


@dataclass
class Outcome:
    readings: dict[str, Reading]
    findings: list[Finding]
    lowerable: list[str] = field(default_factory=list)

    @property
    def status(self) -> int:
        """3 when anything went unread, else 1 when a finding fails, else 0."""
        if any(f.kind == "unread" for f in self.findings):
            return 3
        return 1 if any(f.fails for f in self.findings) else 0


def evaluate(
    answers: Mapping[str, Any], root: Path, baselines: Mapping[str, Baseline]
) -> Outcome:
    """Every reading and finding from recorded answers plus the tree at ``root``."""
    now = churn_metric._ts(answers["now"])
    rate_24h, merged_24h, queue = queue_readings(answers["queue_prs"], now)
    readings = [
        rate_24h,
        *queue,
        review_rounds(answers["merged_prs"]),
        slowest_ci_job(answers["ci_runs"]),
        prose_tokens(root),
    ]
    by_metric = {reading.metric: reading for reading in readings}
    findings = judge(by_metric, baselines)
    alarm = churn_alarm(rate_24h, merged_24h)
    if alarm is not None:
        findings.append(alarm)
    stale = stale_host_report(answers["tracker_comments"], now)
    if stale is not None:
        findings.append(stale)
    return Outcome(by_metric, findings, lowerable(by_metric, baselines))


def render_report(outcome: Outcome, baselines: Mapping[str, Baseline]) -> str:
    """The run summary: every reading against its baseline, then the findings."""
    lines = [
        "## Efficiency ratchet (#10361)",
        "",
        "| metric | reading | baseline | note |",
    ]
    lines.append("| --- | --- | --- | --- |")
    for metric, reading in outcome.readings.items():
        baseline = baselines.get(metric)
        held = (
            f"{_fmt(baseline.value)} + {_fmt(baseline.tolerance)}"
            if baseline
            else "none"
        )
        lines.append(f"| {metric} | {_fmt(reading.value)} | {held} | {reading.note} |")
    lines.append("")
    if outcome.findings:
        lines += [f"- **{f.kind}** {f.text}" for f in outcome.findings]
    else:
        lines.append("No finding.")
    if outcome.lowerable:
        lines += ["", "Baselines a pull request can lower:"]
        lines += [f"- {line}" for line in outcome.lowerable]
    return "\n".join(lines) + "\n"


def _readings_json(outcome: Outcome) -> dict[str, Any]:
    return {
        "readings": {
            metric: {
                "value": None if r.value is None else round(r.value, 4),
                "contributors": list(r.contributors),
                "note": r.note,
            }
            for metric, r in outcome.readings.items()
        },
        "findings": [
            {"kind": f.kind, "metric": f.metric, "text": f.text}
            for f in outcome.findings
        ],
        "status": outcome.status,
    }


def post(runner: Runner, repo: str, body: str) -> None:  # pragma: no cover - I/O
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
        handle.write(body)
    runner(
        [
            "gh",
            "issue",
            "comment",
            str(TRACKER_ISSUE),
            "-R",
            repo,
            "--body-file",
            handle.name,
        ]
    )


def main(argv: list[str] | None = None, *, runner: Runner = run_gh) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--root", default=str(REPO_ROOT), help="the tree measured")
    parser.add_argument("--replay", help="judge these recorded answers; read nothing")
    parser.add_argument("--record", help="also write every answer read here")
    parser.add_argument("--json-out", help="also write the readings and findings here")
    parser.add_argument(
        "--post", action="store_true", help=f"post findings on #{TRACKER_ISSUE}"
    )
    parser.add_argument("--run-url", default="a local run", help="named in the comment")
    args = parser.parse_args(argv)
    root = Path(args.root)
    try:
        baselines = parse_baselines(
            (root / BASELINES_RELATIVE).read_text(encoding="utf-8")
        )
        if args.replay:
            answers = json.loads(Path(args.replay).read_text(encoding="utf-8"))
        else:  # pragma: no cover - I/O
            answers = fetch_answers(runner, args.repo, dt.datetime.now(dt.UTC))
        if args.record:
            Path(args.record).write_text(json.dumps(answers), encoding="utf-8")
        outcome = evaluate(answers, root, baselines)
    except (Unreadable, OSError, KeyError, TypeError, ValueError) as error:
        print(f"UNKNOWN efficiency ratchet could not judge: {error!r}")
        return 3
    print(render_report(outcome, baselines), end="")
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(_readings_json(outcome), indent=1), encoding="utf-8"
        )
    if outcome.findings:
        now = churn_metric._ts(answers["now"])
        key = finding_key(outcome.findings)
        body = render_comment(outcome.findings, args.run_url)
        if not should_post(answers["tracker_comments"], key, now):
            print(
                f"Not posted: the last ratchet comment on #{TRACKER_ISSUE} has {key}."
            )
        elif args.post:  # pragma: no cover - I/O
            post(runner, args.repo, body)
            print(f"Posted on #{TRACKER_ISSUE}.")
        else:
            print("Would post:\n" + body, end="")
    return outcome.status


if __name__ == "__main__":
    sys.exit(main())
