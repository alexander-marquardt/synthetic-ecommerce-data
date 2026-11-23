"""scripts/ci_cancel_run.py cancels only a pull request's run, and the replay of red runs (#1175).

The cancel job runs after a required job already failed, so the script must never turn a red check
into anything else: every answer it gets (a fork's 403, a run already cancelled, a network error)
is a line and exit 0. The replay reads recorded runs (tests/fixtures/red_runs_1175.json, the jobs
API's answer for four red runs, trimmed to the fields it reads) and prints what a cancel at each
run's first red required check frees.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "red_runs_1175.json"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


ci_cancel_run = _load("ci_cancel_run")
ci_red_run_replay = _load("ci_red_run_replay")

ENV = {
    "GITHUB_EVENT_NAME": "pull_request",
    "GITHUB_API_URL": "https://api.github.com",
    "GITHUB_REPOSITORY": "o/r",
    "GITHUB_RUN_ID": "42",
    "GH_TOKEN": "t",
}


def test_a_red_pull_request_job_cancels_its_own_run():
    sent = []
    line = ci_cancel_run.cancel(ENV, lambda url, token: sent.append((url, token)) or 202)
    assert sent == [("https://api.github.com/repos/o/r/actions/runs/42/cancel", "t")]
    assert line == "ci_cancel_run: a required job is red: the rest of run 42 is cancelled (#1175)"


@pytest.mark.parametrize("event", ["push", "merge_group", "workflow_dispatch", "schedule", ""])
def test_a_run_that_is_not_a_pull_request_s_is_never_cancelled(event):
    """The job's ``if:`` names the event; the script checks it again, so a main run stays."""

    sent = []
    line = ci_cancel_run.cancel(
        {**ENV, "GITHUB_EVENT_NAME": event}, lambda url, token: sent.append(url) or 202
    )
    assert sent == [], f"a {event!r} run was cancelled"
    assert "never cancelled" in line


@pytest.mark.parametrize(
    "answer, says",
    [
        (409, "already cancelled or done (409)"),
        (403, "a fork's read-only token"),
        (500, "answered 500"),
        (OSError("unreachable"), "the cancel request failed (unreachable)"),
    ],
)
def test_a_cancel_that_does_not_go_through_is_a_line_never_a_new_failure(answer, says, monkeypatch):
    def send(url, token):
        if isinstance(answer, Exception):
            raise answer
        return answer

    try:
        line = ci_cancel_run.cancel(ENV, send)
    except Exception as error:  # noqa: BLE001  # an escape is the failure this test names
        line = f"raised {error!r}"
    assert says in line
    monkeypatch.setattr(ci_cancel_run, "post", send)
    for key, value in ENV.items():
        monkeypatch.setenv(key, value)
    assert ci_cancel_run.main() == 0


def test_no_token_cancels_nothing():
    line = ci_cancel_run.cancel({**ENV, "GH_TOKEN": ""}, lambda url, token: 202)
    assert "unset" in line


def test_the_replay_frees_every_job_s_runtime_after_the_first_red_required_check(capsys):
    """The three red runs of the 2026-11-23 04:56Z queue and one from 2026-11-22."""
    assert ci_red_run_replay.main(["--fixture", str(FIXTURE)]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "45102749533: tests (10) red at 2026-11-23T04:26:22Z, run ended 05:04:04Z; "
        "8 jobs ran on, 39.9 runner-min freed",
        "45103039265: red-commit-proof red at 2026-11-23T03:54:17Z, run ended 05:13:14Z; "
        "19 jobs ran on, 144.2 runner-min freed",
        "45106728542: red-commit-proof red at 2026-11-23T04:00:15Z, run ended 05:08:33Z; "
        "19 jobs ran on, 128.8 runner-min freed",
        "45084861912: red-commit-proof red at 2026-11-22T23:53:42Z, run ended 01:08:43Z; "
        "23 jobs ran on, 135.5 runner-min freed",
        "total: 448.3 runner-min freed",
    ]


def _job(name, conclusion, start, end):
    return {"name": name, "conclusion": conclusion, "started_at": start, "completed_at": end}


def test_the_first_red_is_a_required_check_and_a_skipped_job_frees_nothing():
    """main-merged-tree is not required: its red is not a cancel point. A skipped job's
    started_at can follow its completed_at; it frees nothing."""
    required = ci_red_run_replay.required_checks()
    jobs = [
        _job("main-merged-tree", "failure", "2026-11-23T00:00:00Z", "2026-11-23T00:01:00Z"),
        _job("tests (2)", "failure", "2026-11-23T00:00:00Z", "2026-11-23T00:10:00Z"),
        _job("tests (3)", "success", "2026-11-23T00:05:00Z", "2026-11-23T00:20:00Z"),
        _job("lint", "skipped", "2026-11-23T00:30:01Z", "2026-11-23T00:30:00Z"),
        # Cancelled before the first red: no red check itself (#1175).
        _job("file-size", "cancelled", "2026-11-23T00:00:00Z", "2026-11-23T00:02:00Z"),
    ]
    result = ci_red_run_replay.replay(jobs, required)
    assert result.first_red == "tests (2)"
    # main-merged-tree ended before the cancel; tests (3) ran 10 more minutes.
    assert (result.jobs_after_red, result.freed_minutes) == (1, 10.0)


def test_a_green_run_frees_nothing():
    jobs = [_job("lint", "success", "2026-11-23T00:00:00Z", "2026-11-23T00:01:00Z")]
    result = ci_red_run_replay.replay(jobs, ci_red_run_replay.required_checks())
    assert ci_red_run_replay.line("1", result) == "1: no red required check, nothing to free"
