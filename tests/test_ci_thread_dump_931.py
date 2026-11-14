"""A test that gives up on a hung ``ci_run_pytest.py`` leaves the wrapper's thread dump (#931).

The tests of ``scripts/ci_run_pytest.py`` ended a wrapper that outlived their patience with
SIGKILL, which runs no handler, so the log never said where the wrapper's threads were. While
fixing #929 the reentrant flush was found by reading the code; a thread dump would have named it.
Every such test now starts the wrapper through ``tests/wrapper_process.py``, which runs it with
``PYTHONFAULTHANDLER=1`` and, on giving up, sends SIGUSR1 (the wrapper has faulthandler dump every
thread on it) before the SIGKILL.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import wrapper_process

TESTS = Path(__file__).resolve().parent
#: A pytest that hangs: it says it started, then sleeps past the test's patience.
HUNG_PYTEST = "import time; print('pytest running', flush=True); time.sleep(30)"
#: faulthandler's header for each thread it dumps: ``Thread 0x...`` or ``Current thread 0x...``.
THREAD = re.compile(r"^(?:Current thread|Thread) 0x[0-9a-f]+ \(most recent call first\):$", re.M)


def test_a_wrapper_the_test_gives_up_on_leaves_every_thread_s_stack() -> None:
    proc = wrapper_process.start(["--", sys.executable, "-c", HUNG_PYTEST], text=True)
    assert proc.stdout is not None
    try:
        first = proc.stdout.readline()
        done = wrapper_process.finish(proc, timeout=1)
    finally:
        wrapper_process.reap(proc)
    log = first + done.stdout
    assert done.gave_up, log
    # The main thread waits on the relay, the relay reads pytest, the timer waits its period.
    assert len(THREAD.findall(log)) >= 3, log
    for frame in ("in run_once", "in relay", "in tick"):
        assert frame in log, f"{frame!r} not in the dump:\n{log}"


def test_the_wrapper_s_python_runs_with_faulthandler_on() -> None:
    child = "import os; print('PYTHONFAULTHANDLER=' + os.environ.get('PYTHONFAULTHANDLER', ''))"
    done = wrapper_process.finish(
        wrapper_process.start(["--", sys.executable, "-c", child], text=True), timeout=60
    )
    assert "PYTHONFAULTHANDLER=1" in done.stdout.splitlines(), done.stdout


def test_every_test_starts_the_wrapper_through_the_helper() -> None:
    # A test that runs ``str(SCRIPT)`` itself would end it with a bare SIGKILL and no dump.
    bound = re.compile(r'^SCRIPT = REPO / "scripts" / "ci_run_pytest\.py"$', re.M)
    direct = [
        path.name
        for path in sorted(TESTS.rglob("*.py"))
        if path.name != "wrapper_process.py"
        and bound.search(text := path.read_text(encoding="utf-8"))
        and "str(SCRIPT)" in text
    ]
    assert direct == [], f"start ci_run_pytest.py through tests/wrapper_process.py: {direct}"
