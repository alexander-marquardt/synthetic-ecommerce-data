#!/usr/bin/env python3
"""Replay a red CI run: the runner-minutes a cancel at its first red required check frees (#1175).

    gh api "repos/<owner>/<repo>/actions/runs/<id>/jobs?per_page=100&filter=latest" > run.json
    ci_red_run_replay.py run.json [more.json ...]
    ci_red_run_replay.py --fixture tests/fixtures/red_runs_1175.json

Each file is the jobs API's answer (``{"jobs": [...]}``) or the fixture's ``{"runs": {id: {"jobs":
[...]}}}``. A run's first red check is the required job (scripts/merge_pr/config.sh REQUIRED_CI; a
matrix job ``tests (3)`` counts as ``tests``) whose ``completed_at`` is earliest among those that
ended ``failure``. scripts/ci_cancel_run.py cancels the run then, so every other job's runtime after
that moment is freed: a job running then frees what was left of it, and a job that started later
frees all of it. The red job itself frees nothing. A run with no red required check frees nothing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

CONFIG = Path(__file__).resolve().parent / "merge_pr" / "config.sh"


def required_checks(config: Path = CONFIG) -> list[str]:
    """REQUIRED_CI from scripts/merge_pr/config.sh: the checks a merge waits for."""
    match = re.search(r"^REQUIRED_CI=\(([^)]*)\)", config.read_text(), re.MULTILINE)
    if not match:
        raise ValueError(f"no REQUIRED_CI=(...) line in {config}")
    return match.group(1).split()


def check_name(job_name: str) -> str:
    """``tests (3)`` -> ``tests``: the check a matrix job stands for."""
    return re.sub(r" \(.*\)$", "", job_name)


def _time(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


@dataclass(frozen=True)
class Replay:
    first_red: str | None
    red_at: datetime | None
    run_end: datetime | None
    jobs_after_red: int
    freed_minutes: float


def replay(jobs: list[dict], required: list[str]) -> Replay:
    """What a cancel at the first red required check would have freed."""
    ends = [t for j in jobs if (t := _time(j.get("completed_at")))]
    run_end = max(ends) if ends else None
    red = [
        j
        for j in jobs
        if j.get("conclusion") == "failure"
        and check_name(j["name"]) in required
        and j.get("completed_at")
    ]
    if not red:
        return Replay(None, None, run_end, 0, 0.0)
    first = min(red, key=lambda j: _time(j["completed_at"]))
    red_at = _time(first["completed_at"])
    freed = 0.0
    after = 0
    for job in jobs:
        start, end = _time(job.get("started_at")), _time(job.get("completed_at"))
        if job is first or start is None or end is None or end <= red_at:
            continue
        seconds = (end - max(start, red_at)).total_seconds()
        if seconds > 0:
            freed += seconds
            after += 1
    return Replay(first["name"], red_at, run_end, after, freed / 60)


def _runs(path: Path) -> list[tuple[str, list[dict]]]:
    data = json.loads(path.read_text())
    if "runs" in data:
        return [(run_id, run["jobs"]) for run_id, run in data["runs"].items()]
    return [(path.stem, data["jobs"])]


def line(run_id: str, result: Replay) -> str:
    if result.first_red is None:
        return f"{run_id}: no red required check, nothing to free"
    return (
        f"{run_id}: {result.first_red} red at {result.red_at:%Y-%m-%dT%H:%M:%SZ}, run ended "
        f"{result.run_end:%H:%M:%SZ}; {result.jobs_after_red} jobs ran on, "
        f"{result.freed_minutes:.1f} runner-min freed"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="*", type=Path, help="jobs API answers, one run each")
    parser.add_argument(
        "--fixture", type=Path, action="append", default=[], help="a {runs: ...} file"
    )
    args = parser.parse_args(argv)
    required = required_checks()
    total = 0.0
    for path in [*args.files, *args.fixture]:
        for run_id, jobs in _runs(path):
            result = replay(jobs, required)
            total += result.freed_minutes
            print(line(run_id, result))
    print(f"total: {total:.1f} runner-min freed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
