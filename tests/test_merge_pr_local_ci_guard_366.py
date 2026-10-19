"""merge_pr.sh runs every local CI command under scripts/local_ci_guard.py (#366).

Same worlds as tests/test_merge_pr.py. What is pinned is the wiring: a local CI job that
passes the memory ceiling fails the job and so refuses the merge, with the reason printed
next to the job's verdict; and a local CI run waits while another run holds the lock, a
``--dry-run`` included (it runs the same jobs, so it takes the same memory). The ceiling and
the lock themselves are tests/test_local_ci_guard_366.py's.
"""

from __future__ import annotations

import fcntl
import threading
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
    assert "memory ceiling" in done.stdout, done.stdout[-800:]
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


def _hold_for(path: str, seconds: float) -> threading.Thread:
    handle = open(path, "a+")  # noqa: SIM115 (closed by the thread when the time is up)
    fcntl.flock(handle, fcntl.LOCK_EX)

    def release() -> None:
        time.sleep(seconds)
        handle.close()

    thread = threading.Thread(target=release, daemon=True)
    thread.start()
    return thread


def test_a_local_ci_run_waits_while_another_holds_the_lock(world: dict, tmp_path) -> None:
    head = _open_pr(world, _plant("echo suite"))
    lock = str(tmp_path / "local-ci.lock")
    holder = _hold_for(lock, 4)
    started = time.monotonic()
    done = _run(
        world,
        head,
        _GREEN_CHECK,
        "--local-ci",
        "--label",
        "lbl",
        LOCAL_CI_LOCK=lock,
        LOCAL_CI_LOCK_WAIT="120",
        LOCAL_CI_LOCK_POLL="0.5",
    )
    holder.join()
    assert done.returncode == 0, done.stdout[-800:] + done.stderr[-800:]
    assert "waiting for another local CI run" in done.stdout + done.stderr
    assert time.monotonic() - started >= 3, "the run did not wait for the holder"
    assert _merged(world)


def test_a_dry_run_of_the_local_ci_takes_the_lock_too(world: dict, tmp_path) -> None:
    head = _open_pr(world, _plant("echo suite"))
    lock = str(tmp_path / "local-ci.lock")
    holder = _hold_for(lock, 6)
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
    holder.join()
    assert done.returncode != 0, "a dry run ran its jobs while another local CI run held the lock"
    assert "local CI lock" in done.stdout + done.stderr
