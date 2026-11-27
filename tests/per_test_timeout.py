"""The per-test time limit (elastic/prism#10032), in place of ``pytest-timeout`` (#1103).

A test that hangs, or grows its memory without end, would hold the machine until something
outside pytest kills it; here it fails at its limit. The limit is ``timeout`` under
``[tool.pytest.ini_options]`` in seconds, or ``@pytest.mark.timeout(<s>)`` on a slow test; 0 is
none. It counts the test's setup, call and teardown together, or the call alone under
``timeout_func_only = true``.

SIGALRM on the main thread, as pytest-timeout's signal method was: the alarm raises
``pytest.fail`` wherever the test is, so its ``finally`` blocks and fixture teardowns still run,
and the other threads' stacks go to stderr. The message starts ``Timeout``, which
``vendor/prism/scripts/mutant_run_plugin.py`` reads. With no SIGALRM, or off the main thread,
a test has no limit. ``tests/conftest.py`` registers it; a run without that conftest passes
``-p per_test_timeout`` with this directory on ``PYTHONPATH``.
"""

from __future__ import annotations

import signal
import sys
import threading
import traceback
from collections.abc import Generator
from contextlib import contextmanager

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addini("timeout", "a test's limit in seconds, its fixtures included; 0 for none")
    parser.addini("timeout_func_only", "the limit counts the test's call alone", type="bool")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "timeout(seconds): this test's limit, in place of the ini's")


def _seconds(item: pytest.Item) -> float:
    marker = item.get_closest_marker("timeout")
    return float((marker.args[0] if marker and marker.args else item.config.getini("timeout")) or 0)


def _other_threads() -> None:
    for ident, frame in sys._current_frames().items():
        if ident != threading.get_ident():
            sys.stderr.write(f"--- thread {ident}\n{''.join(traceback.format_stack(frame))}")


@contextmanager
def _limit(item: pytest.Item) -> Generator[None, None, None]:
    seconds = _seconds(item)
    main = threading.current_thread() is threading.main_thread()
    if seconds <= 0 or not main or not hasattr(signal, "SIGALRM"):
        yield
        return

    def expired(signum: int, frame: object) -> None:
        _other_threads()
        pytest.fail(f"Timeout (>{seconds:g}s): the per-test limit (tests/per_test_timeout.py)")

    previous = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(item: pytest.Item) -> Generator[None, object, object]:
    if item.config.getini("timeout_func_only"):
        return (yield)
    with _limit(item):
        return (yield)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item: pytest.Item) -> Generator[None, object, object]:
    if not item.config.getini("timeout_func_only"):
        return (yield)
    with _limit(item):
        return (yield)
