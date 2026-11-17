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

import fcntl
import os
import signal
import subprocess
import sys
import termios
import time
from pathlib import Path

import wrapper_process

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
    proc = wrapper_process.start(["--", sys.executable, "-c", FLOODING_PYTEST], env=env, bufsize=0)
    assert proc.stdout is not None
    try:
        _wait_until_the_pipe_stops_filling(proc.stdout.fileno(), time.monotonic() + 20)
        proc.send_signal(signal.SIGTERM)
        done = wrapper_process.finish(proc, timeout=15)
    finally:
        wrapper_process.reap(proc)
    log = done.stdout.decode("utf-8", errors="replace")
    tail = log[-2000:]
    assert "reentrant call" not in log, tail
    assert "ci_run_pytest: SIGTERM at " in log, tail
    assert "Out of memory: Killed process 7" in log, tail
    assert done.returncode == 128 + signal.SIGTERM, tail


def test_an_error_in_the_relay_thread_ends_the_wrapper_with_its_traceback() -> None:
    # The relay's write fails once the log's pipe is gone: the error reaches the main thread,
    # not a thread's stderr note while the wrapper goes on as if pytest's output got through.
    child = "import time; time.sleep(0.5); print('pytest output', flush=True)"
    proc = wrapper_process.start(
        ["--", sys.executable, "-c", child], stderr=subprocess.PIPE, text=True
    )
    assert proc.stdout is not None and proc.stderr is not None
    proc.stdout.close()
    try:
        done = wrapper_process.finish(proc, timeout=30)
    finally:
        wrapper_process.reap(proc)
    err = done.stderr
    assert not done.gave_up and done.returncode != 0, err
    assert "BrokenPipeError" in err and "in run_once" in err, err
