"""A pull request's first red required check cancels the rest of its CI run (#1175).

A red run used to keep its runners until every shard ended: on 2026-11-23 three red pull request
runs held 19 jobs between them for up to 80 minutes after their first red check, while the merge
path's run queued behind them. Every required job of ci.yaml (scripts/merge_pr/config.sh
REQUIRED_CI) now has a job of its own, ``cancel-on-red-<job>``, that starts once that job has ended
red on a ``pull_request`` run and asks GitHub to cancel the run (scripts/ci_cancel_run.py). The two
matrix jobs fail fast on a pull request, so a red leg ends its siblings. A push to main, a
merge-group run and a dispatched run never cancel: their result is a merged sha's proof (#1029,
agent-ops#1743).

The cancel is never a step of the red job: GitHub then records that job as ``cancelled``, not as
``failure`` (tests/fixtures/cancelled_from_inside_1175.json), and nothing reads the run as red.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
CI = REPO / ".github" / "workflows" / "ci.yaml"
CONFIG = REPO / "scripts" / "merge_pr" / "config.sh"
INSIDE = REPO / "tests" / "fixtures" / "cancelled_from_inside_1175.json"

CANCEL_IF = "failure() && github.event_name == 'pull_request'"
CANCEL_RUN = "python3 scripts/ci_cancel_run.py"
FAIL_FAST = "${{ github.event_name == 'pull_request' }}"


def _jobs() -> dict:
    return yaml.safe_load(CI.read_text())["jobs"]


def _required() -> list[str]:
    match = re.search(r"^REQUIRED_CI=\(([^)]*)\)", CONFIG.read_text(), re.MULTILINE)
    assert match, "config.sh lost its REQUIRED_CI line"
    return match.group(1).split()


def _cancel_name(name: str) -> str:
    return f"cancel-on-red-{name}"


def _cancel_jobs() -> dict:
    """The jobs that ask GitHub to cancel the run, by id."""
    return {
        name: job
        for name, job in _jobs().items()
        if any("ci_cancel_run" in step.get("run", "") for step in job.get("steps", []))
    }


def _holds(expression: str, event: str, failed: bool) -> bool:
    """GitHub's value for the expression; ``failure()`` is true once a job it needs failed."""
    body = expression.replace("failure()", "FAILED").replace("github.event_name", "EVENT")
    return eval(body.replace("&&", " and "), {"FAILED": failed, "EVENT": event})


def test_a_job_cancelled_from_inside_is_recorded_cancelled_though_its_step_failed():
    """The recorded reason the cancel is a job of its own: job 137725634488, whose ``Tests`` step
    failed and whose own last step sent the cancel, ended ``cancelled``."""
    job = json.loads(INSIDE.read_text())
    steps = {step["name"]: step["conclusion"] for step in job["steps"]}
    assert steps["Tests"] == "failure"
    assert steps["Cancel the rest of this pull request's run"] == "cancelled"
    assert job["conclusion"] == "cancelled"


@pytest.mark.parametrize("name", _required())
def test_no_required_job_cancels_its_own_run_or_may(name):
    job = _jobs()[name]
    assert name not in _cancel_jobs(), "a job that cancels its own run ends cancelled, not red"
    assert "actions" not in job.get("permissions", {})


@pytest.mark.parametrize("name", _required())
def test_every_required_job_has_its_own_cancel_job(name):
    """One job each: a job that needs them all would start only once every one had ended."""
    job = _jobs().get(_cancel_name(name))
    assert job is not None, f"no job {_cancel_name(name)}"
    assert job["needs"] == [name]
    assert job["if"] == CANCEL_IF
    assert job["permissions"] == {"contents": "read", "actions": "write"}
    # Hosted, so it does not queue behind the self-hosted pool (the issue's 2 minutes).
    assert job["runs-on"] == "ubuntu-latest"
    runs = [step for step in job["steps"] if "run" in step]
    assert [step["run"] for step in runs] == [CANCEL_RUN]
    assert runs[0]["env"] == {"GH_TOKEN": "${{ github.token }}"}
    assert "if" not in runs[0] and "strategy" not in job


def test_only_the_cancel_jobs_cancel_and_the_workflow_stays_read_only():
    """main-merged-tree runs only on a push to main and has no cancel job; the cancel jobs are no
    required check; only they are granted actions: write."""
    want = {_cancel_name(name) for name in _required()}
    assert set(_cancel_jobs()) == want
    assert not want & set(_required())
    writing = {n for n, job in _jobs().items() if "actions" in job.get("permissions", {})}
    assert writing == want
    assert yaml.safe_load(CI.read_text())["permissions"] == {"contents": "read"}


def test_no_job_needs_a_cancel_job():
    for name, job in _jobs().items():
        needs = job.get("needs", [])
        assert not set([needs] if isinstance(needs, str) else needs) & set(_cancel_jobs()), name


EVENTS = [
    ("pull_request", True, True),
    ("pull_request", False, False),
    ("push", True, False),
    ("merge_group", True, False),
    ("workflow_dispatch", True, False),
]


@pytest.mark.parametrize("event, failed, runs", EVENTS)
def test_only_a_red_pull_request_run_is_cancelled(event, failed, runs):
    jobs = _cancel_jobs()
    assert {_holds(job.get("if", "True"), event, failed) for job in jobs.values()} == {runs}


@pytest.mark.parametrize("name", ["tests", "ceiling-catalogue"])
def test_a_matrix_job_fails_fast_on_a_pull_request_and_on_nothing_else(name):
    """A red leg keeps ``failure`` and GitHub cancels its siblings, so the job ends and its cancel
    job starts; a push or a dispatched run runs every leg to its end."""
    value = _jobs()[name]["strategy"]["fail-fast"]
    assert value == FAIL_FAST
    expression = value.removeprefix("${{ ").removesuffix(" }}")
    fast = {event: _holds(expression, event, False) for event, _, _ in EVENTS}
    assert fast == {
        "pull_request": True, "push": False, "merge_group": False, "workflow_dispatch": False,
    }  # fmt: skip


def test_every_matrix_job_of_the_workflow_fails_fast_on_a_pull_request():
    matrix = {name for name, job in _jobs().items() if "strategy" in job}
    assert matrix == {"tests", "ceiling-catalogue"}


def _local(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/local_ci_jobs.py", *argv],
        cwd=REPO, capture_output=True, text=True, check=False,
    )  # fmt: skip


def test_a_local_run_has_every_required_job_and_no_cancel_job():
    """merge_pr.sh --local-ci has no GitHub run to cancel, so it lists no cancel job."""
    done = _local("--list")
    assert done.returncode == 0, done.stderr
    listed = done.stdout.split()
    assert set(_required()) <= set(listed)
    assert not set(listed) & {_cancel_name(name) for name in _required()}


@pytest.mark.parametrize(
    "old, new",
    [
        ("  cancel-on-red-lint:\n", "  lint-again:\n"),
        (CANCEL_RUN, "uv run --locked mypy ."),
        (CANCEL_IF, "github.event_name == 'pull_request'"),
        ("        run: " + CANCEL_RUN, "        run: " + CANCEL_RUN + "\n      - run: echo hi"),
    ],
    ids=["another name", "another command", "another condition", "a second command"],
)
def test_only_a_job_that_does_nothing_but_cancel_is_left_out_of_a_local_run(tmp_path, old, new):
    """A check put in a job of that name, or a cancel under another name, is still listed."""
    head, sep, tail = CI.read_text().partition("  cancel-on-red-lint:\n")
    assert sep, "ci.yaml has no cancel-on-red-lint job"
    first, gap, rest = (sep + tail).partition("\n\n")
    assert old in first
    (tmp_path / "ci.yaml").write_text(head + first.replace(old, new) + gap + rest)
    name = "lint-again" if "lint-again" in new else "cancel-on-red-lint"
    done = _local("--workflows", str(tmp_path), "--list")
    assert done.returncode == 0, done.stderr
    assert name in done.stdout.split()
