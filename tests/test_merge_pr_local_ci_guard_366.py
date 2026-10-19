"""merge_pr.sh runs every local CI command under scripts/local_ci_guard.py (#366).

Same worlds as tests/test_merge_pr.py. What is pinned is the wiring: a local CI job that
passes the memory ceiling fails the job and so refuses the merge, with the reason printed
next to the job's verdict; and a local CI run waits while another run holds the lock, a
``--dry-run`` included (it runs the same jobs, so it takes the same memory). The ceiling and
the lock themselves are tests/test_local_ci_guard_366.py's.
"""

from __future__ import annotations

import fcntl
import subprocess
import time

import test_merge_pr
from test_merge_pr import _GREEN, _GREEN_CHECK, _merged, _open_pr, _run

world = test_merge_pr.world

#: Each case builds its own origin: spread over the workers (tests/xdist_groups.py).
XDIST_SPREAD = True

_JOBS = {
    "lint": "true",
    "commit-messages": "true",
    "file-size": "true",
    "red-commit-proof": "true",
    "customer-name-check": "true",
    "stats-roll": "true",
}
_HOG = 'python3 -c "import time; b = bytearray([1]) * (%d * 1024 * 1024); time.sleep(%d)"'


def _plant(tests: str) -> dict[str, str]:
    return {**_GREEN, **test_merge_pr._workflow(tests=tests, **_JOBS)}


def test_a_local_job_that_passes_the_memory_ceiling_refuses_the_merge(world: dict) -> None:
    head = _open_pr(world, _plant(_HOG % (1600, 60)))
    started = time.monotonic()
    done = _run(
        world, head, _GREEN_CHECK, "--local-ci", "--label", "lbl", LOCAL_CI_MEMORY_MB="1200"
    )
    assert done.returncode != 0
    assert "local CI tests: FAIL" in done.stdout, done.stdout[-800:]
    assert "memory ceiling exceeded" in done.stderr, done.stderr[-800:]
    assert not _merged(world)
    assert time.monotonic() - started < 150, "the job was not stopped at the ceiling"


def test_a_local_job_under_the_memory_ceiling_passes_and_merges(world: dict) -> None:
    head = _open_pr(world, _plant(_HOG % (50, 1)))
    done = _run(
        world, head, _GREEN_CHECK, "--local-ci", "--label", "lbl", LOCAL_CI_MEMORY_MB="1200"
    )
    assert done.returncode == 0, done.stdout[-800:] + done.stderr[-800:]
    assert "local CI tests: PASS" in done.stdout
    assert _merged(world)


def _hold(path: str):
    handle = open(path, "a+")  # noqa: SIM115 (closed by the caller when the case is done)
    fcntl.flock(handle, fcntl.LOCK_EX)
    return handle


def test_a_local_ci_run_waits_while_another_holds_the_lock(world: dict, tmp_path) -> None:
    """The holder lets go only once the run has said it is waiting: the wait is seen, not timed."""
    head = _open_pr(world, _plant("echo suite"))
    lock = str(tmp_path / "local-ci.lock")
    held = _hold(lock)
    env = {
        **world["env"],
        "FAKE_GH_HEAD": head,
        "MERGE_PR_CHECKS": _GREEN_CHECK,
        "LOCAL_CI_LOCK": lock,
        "LOCAL_CI_LOCK_WAIT": "300",
        "LOCAL_CI_LOCK_POLL": "0.2",
    }
    merge = subprocess.Popen(
        [str(world["checkout"] / "scripts" / "merge_pr.sh"), "--local-ci", "--label", "lbl", "54"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    lines: list[str] = []
    assert merge.stdout is not None
    for line in merge.stdout:
        lines.append(line)
        if "waiting for another local CI run" in line:
            held.close()
    held.close()
    code = merge.wait(timeout=300)
    text = "".join(lines)
    assert "waiting for another local CI run" in text, text[-800:]
    assert code == 0, text[-800:]
    assert "local CI tests: PASS" in text
    assert _merged(world)


def test_a_dry_run_of_the_local_ci_takes_the_lock_too(world: dict, tmp_path) -> None:
    head = _open_pr(world, _plant("echo suite"))
    lock = str(tmp_path / "local-ci.lock")
    held = _hold(lock)
    try:
        done = _run(
            world,
            head,
            _GREEN_CHECK,
            "--dry-run",
            "--local-ci",
            LOCAL_CI_LOCK=lock,
            LOCAL_CI_LOCK_WAIT="1",
            LOCAL_CI_LOCK_POLL="0.2",
        )
    finally:
        held.close()
    assert done.returncode != 0, "a dry run ran its jobs while another local CI run held the lock"
    assert "local CI lock" in done.stdout + done.stderr


def test_the_step_3_checks_past_the_ceiling_refuse_the_merge(world: dict) -> None:
    """The checks of step 3 are pytest on workers too: they run under the same ceiling."""
    hog = (
        "import time\n\n\ndef test_hog():\n"
        "    held = bytearray([1]) * (1600 * 1024 * 1024)\n"
        "    time.sleep(60)\n    assert held\n"
    )
    head = _open_pr(world, {"tests/test_planted_hog.py": hog})
    done = _run(world, head, "tests/test_planted_hog.py", LOCAL_CI_MEMORY_MB="1200")
    assert done.returncode != 0
    assert "memory ceiling exceeded" in done.stderr, done.stderr[-800:]
    assert "NOT merged" in done.stderr, done.stderr[-800:]
    assert not _merged(world)
