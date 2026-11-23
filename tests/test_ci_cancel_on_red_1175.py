"""A pull request's first red required check cancels the rest of its CI run (#1175).

A red run used to keep its runners until every shard ended: on 2026-11-23 three red pull request
runs held 19 jobs between them for up to 80 minutes after their first red check, while the merge
path's run queued behind them. Every required job of ci.yaml (scripts/merge_pr/config.sh
REQUIRED_CI) now ends with one step that runs only when the job failed on a ``pull_request`` run,
and asks GitHub to cancel the run (scripts/ci_cancel_run.py). A push to main, a merge-group run and
a dispatched run never cancel: their result is a merged sha's proof (#1029, agent-ops#1743).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
CI = REPO / ".github" / "workflows" / "ci.yaml"
CONFIG = REPO / "scripts" / "merge_pr" / "config.sh"

STEP_IF = "failure() && github.event_name == 'pull_request'"
STEP_RUN = "python3 scripts/ci_cancel_run.py"


def _jobs() -> dict:
    return yaml.safe_load(CI.read_text())["jobs"]


def _required() -> list[str]:
    match = re.search(r"^REQUIRED_CI=\(([^)]*)\)", CONFIG.read_text(), re.MULTILINE)
    assert match, "config.sh lost its REQUIRED_CI line"
    return match.group(1).split()


def _cancel_steps(job: dict) -> list[dict]:
    return [s for s in job.get("steps", []) if "ci_cancel_run" in s.get("run", "")]


@pytest.mark.parametrize("name", _required())
def test_every_required_job_ends_by_cancelling_its_pull_request_run_when_red(name):
    """The cancel is the job's last step, so it follows the work that went red (and any rerun
    inside that work's own step) and every ``always()`` upload before it: the run's other jobs
    end within seconds of the red check, well inside the issue's 2 minutes."""
    job = _jobs()[name]
    last = job["steps"][-1]
    assert last.get("run") == STEP_RUN
    assert last.get("if") == STEP_IF
    assert last.get("env") == {"GH_TOKEN": "${{ github.token }}"}
    assert _cancel_steps(job) == [last], "one cancel step a job"
    # Cancelling a run needs actions: write; the job keeps what it read before.
    assert job["permissions"]["actions"] == "write"
    assert job["permissions"]["contents"] == "read"


def test_no_job_outside_the_required_checks_cancels_and_the_workflow_stays_read_only():
    """main-merged-tree runs only on a push to main: it never cancels anything. The workflow's
    default token stays read-only; only the jobs that cancel are granted actions: write."""
    required = set(_required())
    jobs = _jobs()
    cancelling = {name for name, job in jobs.items() if _cancel_steps(job)}
    assert cancelling == required
    writing = {
        name for name, job in jobs.items() if job.get("permissions", {}).get("actions") == "write"
    }
    assert writing == required
    assert yaml.safe_load(CI.read_text())["permissions"] == {"contents": "read"}


def _step_runs(event: str, failed: bool) -> bool:
    """GitHub's value for STEP_IF; ``failure()`` is true once an earlier step of the job failed."""
    body = STEP_IF.replace("failure()", "FAILED").replace("github.event_name", "EVENT")
    body = body.replace("&&", " and ")
    return eval(body, {"FAILED": failed, "EVENT": event})


@pytest.mark.parametrize(
    "event, failed, runs",
    [
        ("pull_request", True, True),
        ("pull_request", False, False),
        ("push", True, False),
        ("merge_group", True, False),
        ("workflow_dispatch", True, False),
    ],
)
def test_only_a_red_pull_request_run_is_cancelled(event, failed, runs):
    assert _step_runs(event, failed) is runs
