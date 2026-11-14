"""Start ``scripts/ci_run_pytest.py`` in a test, and give up on it with its threads' stacks (#931).

A test that waits on the wrapper and runs out of patience used to end it with SIGKILL, which runs
no handler, so the log showed nothing of where the wrapper was stuck. While #929 was fixed, the
reentrant flush (the stop signal's handler waiting on the relay's write) was found by reading the
code. Every test that starts the wrapper does it here: ``start`` runs it with
``PYTHONFAULTHANDLER=1`` in a session of its own, and ``finish`` gives up on it by ``give_up``,
which sends SIGUSR1 first (the wrapper has faulthandler dump every thread on it), waits
``DUMP_GRACE`` seconds for that dump, and only then kills the session.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "ci_run_pytest.py"
#: Seconds the wrapper has to write its thread dump between SIGUSR1 and SIGKILL.
DUMP_GRACE = 3.0


@dataclass
class Run:
    """What a run of the wrapper left: its exit code, its output, and whether the test gave up."""

    returncode: int
    stdout: Any
    stderr: Any
    gave_up: bool


def start(
    args: Sequence[str], *, env: dict[str, str] | None = None, **popen: Any
) -> subprocess.Popen[Any]:
    """Start ``ci_run_pytest.py <args>``: output piped, stderr into stdout unless ``popen`` says."""
    opts: dict[str, Any] = {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT} | popen
    return subprocess.Popen(
        [sys.executable, str(SCRIPT), *args],
        env=(os.environ if env is None else env) | {"PYTHONFAULTHANDLER": "1"},
        start_new_session=True, **opts,
    )  # fmt: skip


def give_up(proc: subprocess.Popen[Any]) -> tuple[Any, Any]:
    """End a wrapper that outlived the test's patience: its whole output, stdout then stderr.

    The output read before the timeout is kept: ``communicate`` after ``TimeoutExpired`` loses none.
    """
    with contextlib.suppress(ProcessLookupError):
        os.kill(proc.pid, signal.SIGUSR1)
    try:
        return proc.communicate(timeout=DUMP_GRACE)
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, signal.SIGKILL)
        return proc.communicate()


def finish(proc: subprocess.Popen[Any], timeout: float) -> Run:
    """Wait ``timeout`` seconds for the wrapper; past that, ``give_up`` on it."""
    try:
        out, err = proc.communicate(timeout=timeout)
        gave_up = False
    except subprocess.TimeoutExpired:
        out, err = give_up(proc)
        gave_up = True
    return Run(proc.wait(), out, err, gave_up)


def reap(proc: subprocess.Popen[Any]) -> None:
    """Kill what is left of the wrapper's session (a hung pytest); a live wrapper gives its dump."""
    if proc.poll() is None:
        out, _ = give_up(proc)
        sys.stderr.write(out.decode("utf-8", "replace") if isinstance(out, bytes) else out or "")
    with contextlib.suppress(ProcessLookupError):
        os.killpg(proc.pid, signal.SIGKILL)
