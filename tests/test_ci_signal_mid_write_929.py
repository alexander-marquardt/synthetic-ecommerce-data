"""A stop signal landing while the wrapper writes pytest's output still prints the evidence (#929).

``scripts/ci_run_pytest.py`` relays each line of pytest's output and, on SIGTERM, prints its memory
and kernel-OOM evidence from the signal handler (#918). Both wrote through ``sys.stdout``. A signal
that landed while the main thread was inside ``sys.stdout.flush()`` ran the handler inside that
flush, and its own write raised ``RuntimeError: reentrant call inside <_io.BufferedWriter>``. The
error escaped the handler before ``os._exit``, the wrapper then waited on the hung pytest, and the
job's log showed no evidence at all. That made ``test_ci_timeout_evidence_918`` fail now and then
(main red at 970b97373168).

This test makes that timing certain. The hung pytest writes more than a pipe holds, and the test
reads nothing until the wrapper is blocked writing a line. SIGTERM then interrupts that write.
"""

from __future__ import annotations

import contextlib
import fcntl
import os
import signal
import subprocess
import sys
import termios
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "ci_run_pytest.py"

#: A hung pytest whose output fills the pipe: 4 MB of lines, then a sleep past the test's patience.
FLOODING_PYTEST = (
    "import sys, time\n"
    "for i in range(40000): sys.stdout.write(f'line {i:05d} ' + 'x' * 88 + chr(10))\n"
    "sys.stdout.flush(); time.sleep(30)\n"
)


def _unread(fd: int) -> int:
    """Bytes waiting in the pipe behind ``fd``."""
    return int.from_bytes(fcntl.ioctl(fd, termios.FIONREAD, b"\0\0\0\0"), sys.byteorder)


def _wait_until_the_pipe_stops_filling(fd: int, deadline: float) -> None:
    """Return once the bytes waiting stay the same for half a second: the writer is blocked."""
    last, steady_since = -1, time.monotonic()
    while time.monotonic() < deadline:
        now = _unread(fd)
        if now != last:
            last, steady_since = now, time.monotonic()
        elif now > 0 and time.monotonic() - steady_since >= 0.5:
            return
        time.sleep(0.05)
    raise AssertionError(f"the wrapper's pipe never filled: {last} bytes waiting")


def test_a_sigterm_during_a_blocked_write_prints_the_evidence_and_exits(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    dmesg = bin_dir / "dmesg"
    dmesg.write_text("#!/bin/sh\necho '[1.0] Out of memory: Killed process 7'\n", encoding="utf-8")
    dmesg.chmod(0o755)
    env = os.environ | {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    command = [sys.executable, str(SCRIPT), "--", sys.executable, "-c", FLOODING_PYTEST]
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, bufsize=0,
        start_new_session=True,
    )  # fmt: skip
    assert proc.stdout is not None
    try:
        _wait_until_the_pipe_stops_filling(proc.stdout.fileno(), time.monotonic() + 20)
        proc.send_signal(signal.SIGTERM)
        try:
            out, _ = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(proc.pid, signal.SIGKILL)
            out, _ = proc.communicate()
    finally:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, signal.SIGKILL)
    log = out.decode("utf-8", errors="replace")
    tail = log[-2000:]
    assert "reentrant call" not in log, tail
    assert "ci_run_pytest: SIGTERM at " in log, tail
    assert "Out of memory: Killed process 7" in log, tail
    assert proc.wait() == 128 + signal.SIGTERM, tail
