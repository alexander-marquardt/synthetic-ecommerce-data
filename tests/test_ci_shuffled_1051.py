"""A pull request's changed test files run again in seeded orders: the ``shuffled`` job (#1051).

The ``tests`` job runs every file in one fixed order, so on 2026-11-16 a test that passed only after
another one had run in its process passed on its PR (#988) and turned main red (#1040). The pass is
agent-ops' (agent-ops#1936), root-owned in the CI runner image at ``/opt/shuffled-pass/``, never a
copy here. These tests run the job's step as ``scripts/local_ci_jobs.py`` emits it, with a planted
pass and a planted ``uv`` in place of the image's, and read what it prints, what it exits and what
it writes to the check's summary.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CI = REPO / ".github" / "workflows" / "ci.yaml"
CONFIG = REPO / "scripts" / "merge_pr" / "config.sh"
IMAGE_PASS = "/opt/shuffled-pass/shuffled_pass.py"
BASE, HEAD = "73fb676d40e6", "391c047b3d0c"
#: The files the step leaves out of the pass: each takes over 1 min alone, serially. A seed gets
#: 10 min for all the changed files at once, with 8 seeds side by side: on this PR a seed holding
#: test_merge_pr_local_ci_guard_366.py (356 s) and test_merge_pr_red_log_453.py (121 s) timed out.
#: test_type_seam.py takes 254 s alone and test_nails_751.py 131 s (#790); with nails in, 8 seeds
#: of #790's other changed files ran out of the runner's 6g (exit 137).
OVER_BUDGET = [
    "tests/test_merge_pr.py",
    "tests/test_merge_pr_github_ci_348.py",
    "tests/test_merge_pr_local_ci_guard_366.py",
    "tests/test_merge_pr_red_log_453.py",
    "tests/test_type_seam.py",
    "tests/test_nails_751.py",
]
LEFT_OUT = "shuffled pass: left out (over the seed budget): " + " ".join(OVER_BUDGET)
PYTEST = "uv run -q --locked pytest" + "".join(f" --deselect {f}" for f in OVER_BUDGET)

sys.path.insert(0, str(REPO / "scripts"))
import local_ci_jobs  # noqa: E402

#: A stand-in for the image's pass: it records its argv and environment, prints a seed's log and
#: then the pass's last line, and exits as told.
FAKE_PASS = """\
import json, os, sys
with open(os.environ["FAKE_RECORD"], "w") as f:
    json.dump({"argv": sys.argv[1:], "addopts": os.environ.get("PYTEST_ADDOPTS")}, f)
print("== shuffled pass (agent-ops#1936), seed 2927495, 1 changed test file; reproduce:")
print("2 failed, 15 passed", file=sys.stderr)
print(os.environ["FAKE_LAST"])
sys.exit(int(os.environ["FAKE_RC"]))
"""


def _job() -> dict:
    jobs = yaml.safe_load(CI.read_text())["jobs"]
    assert "shuffled" in jobs, "ci.yaml has no shuffled job"
    return jobs["shuffled"]


def _run(tmp_path: Path, *, installed: bool, last: str = "", rc: int = 0):
    """-> (exit status, output, summary text, the pass's record or None)."""
    script = local_ci_jobs.emit("shuffled", _job(), BASE, HEAD)
    planted = tmp_path / "shuffled_pass.py"
    if installed:
        planted.write_text(FAKE_PASS)
    assert IMAGE_PASS in script
    script = script.replace(IMAGE_PASS, str(planted))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text('#!/bin/sh\necho "uv $*" >>"$FAKE_UV"\n')
    uv.chmod(0o755)
    summary, record = tmp_path / "summary.md", tmp_path / "record.json"
    env = {
        **{k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"},
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "GITHUB_STEP_SUMMARY": str(summary),
        "FAKE_RECORD": str(record),
        "FAKE_UV": str(tmp_path / "uv.log"),
        "FAKE_LAST": last,
        "FAKE_RC": str(rc),
    }
    done = subprocess.run(
        ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", script],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60, check=False,
    )  # fmt: skip
    text = summary.read_text() if summary.exists() else ""
    rec = json.loads(record.read_text()) if record.exists() else None
    return done.returncode, done.stdout + done.stderr, text, rec


def test_the_job_is_a_required_check_of_a_pull_request_and_of_merge_prs_dispatched_run():
    job = _job()
    assert job["if"] == (
        "github.event_name == 'pull_request' || "
        "(github.event_name == 'workflow_dispatch' && inputs.head != '')"
    )
    required = re.search(r"^REQUIRED_CI=\(([^)]*)\)", CONFIG.read_text(), re.MULTILINE)
    assert required and "shuffled" in required.group(1).split()
    checkout = next(s for s in job["steps"] if s.get("uses", "").startswith("actions/checkout"))
    assert checkout["with"]["fetch-depth"] == 0


def test_a_failing_seed_fails_the_job_and_the_summary_names_the_seed(tmp_path):
    last = (
        "shuffled pass: failure: shuffled order fails at seed 2927495 "
        "(1 test file; log has the command)"
    )
    status, out, summary, rec = _run(tmp_path, installed=True, last=last, rc=1)
    assert status == 1, out
    assert summary.splitlines() == [LEFT_OUT, last]
    assert "2 failed, 15 passed" in out and last in out
    assert rec["argv"] == ["--base", BASE, "--key", HEAD, "--pytest", PYTEST]
    # One process per seed: the local run's exported -n never reaches the pass.
    assert rec["addopts"] is None
    assert (tmp_path / "uv.log").read_text().split("\n")[0] == "uv sync --locked"


def test_a_green_pass_passes_and_the_summary_names_the_seeds(tmp_path):
    last = "shuffled pass: success: shuffled 1 test file, 8 seeds 2927495..2927502 ok (14s)"
    status, out, summary, _ = _run(tmp_path, installed=True, last=last, rc=0)
    assert status == 0, out
    assert summary.splitlines() == [LEFT_OUT, last]


def test_a_pass_that_errors_fails_the_job(tmp_path):
    last = "shuffled pass: error: shuffled seed 2927495: pytest exited 4"
    status, out, summary, _ = _run(tmp_path, installed=True, last=last, rc=2)
    assert status == 2, out
    assert summary.splitlines() == [LEFT_OUT, last]


def test_a_runner_without_the_pass_says_so_and_passes(tmp_path):
    status, out, summary, rec = _run(tmp_path, installed=False)
    assert status == 0, out
    assert "shuffled pass: not installed on this runner" in out
    assert summary.strip() == "shuffled pass: not installed on this runner"
    assert rec is None and not (tmp_path / "uv.log").exists()


def test_the_over_budget_merge_script_files_are_deselected_and_the_summary_names_them(tmp_path):
    """A seed gets 10 min and the cap stays ("Do not raise the timeout to go green",
    elastic/prism#15203) and holds every changed file of the seed at once; the test files that
    take over 1 min alone (four merge-script files and the type seam file) go to the pass's pytest
    as deselects until #1035 makes them fit, and the summary and the log say which."""
    last = "shuffled pass: success: shuffled 3 test files, 8 seeds 2927495..2927502 ok (40s)"
    status, out, summary, rec = _run(tmp_path, installed=True, last=last, rc=0)
    assert status == 0, out
    pytest = shlex.split(rec["argv"][rec["argv"].index("--pytest") + 1])
    deselected = [pytest[i + 1] for i, arg in enumerate(pytest) if arg == "--deselect"]
    assert deselected == OVER_BUDGET
    assert summary.splitlines()[0] == LEFT_OUT
    assert LEFT_OUT in out
