"""pytest plugin that ``scripts/mutant_run.py`` loads into each mutant's test run (#10512).

It records how every test ended, one JSON line per event, to the file named by
``PRISM_MUTANT_RUN_REPORT``. The runner reads those lines to tell a kill from a
broken run: pytest's exit status is 1 for an assertion failure and for a test
that raised ``TypeError`` alike, and only the first is a test that noticed the
mutant (contributing/testing-discipline.md, the per-mutation record, item 2).

An ``assertion`` is a call-phase failure raised as ``AssertionError`` or as
pytest's own ``Failed`` (``pytest.fail``, ``pytest.raises`` that did not raise),
except pytest-timeout's ``Failed``: a mutant that hangs a test was not detected
by an assertion. It must also be the TEST that raised it: the test function's
frame is in the traceback, and every frame inside it is in the test's own module or
in another ``test_*.py`` module (a helper imported from a sister suite, #10670),
except a closing run of frames pytest hides (``pytest.fail``, ``pytest.raises``)
or of the stdlib ``unittest`` helpers (``mock.assert_called_with``). An assert
in the code under test, in a fixture (even one in the same module, reached
through ``request.getfixturevalue``), in a conftest hook, or a guard such as
``tests/es_free_invocation.py`` refusing a connection, did not notice the mutant
from the test's side, so it is an ``error`` (#10525 review, F2 and F3). Every
other failure, and a failed collection, is an ``error``.

The runner copies this file into a temporary directory and puts only that
directory on ``PYTHONPATH``, so loading it shadows no module of the tree under test.
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import os
import unittest
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

REPORT_ENV = "PRISM_MUTANT_RUN_REPORT"
#: The message pytest-timeout passes to ``pytest.fail`` starts with this.
TIMEOUT_PREFIX = "Timeout"
#: The stdlib assertion helpers a test calls (``Mock.assert_called_with``,
#: ``TestCase.assertEqual``) raise from frames in this package.
_UNITTEST = Path(unittest.__file__).resolve().parent
#: ``pytest.fail``, ``pytest.raises`` and pytest-mock's assert wrappers hide
#: their own frames; a hidden frame counts as the test's only when it lives in
#: one of these packages, because code under test can set ``__tracebackhide__``
#: too and its crash-guard assert is not a detection.
_PYTEST = tuple(
    Path(spec.origin).resolve().parent
    for name in ("_pytest", "pytest_mock")
    if (spec := importlib.util.find_spec(name)) and spec.origin
)


def _record(outcome: str, nodeid: str, detail: str) -> None:
    path = os.environ.get(REPORT_ENV)
    if not path:
        return
    line = json.dumps({"outcome": outcome, "nodeid": nodeid, "detail": detail})
    # Append mode: xdist workers write the same file, a line at a time.
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _is_assertion(excinfo: pytest.ExceptionInfo[BaseException]) -> bool:
    value = excinfo.value
    if isinstance(value, AssertionError):
        return True
    if isinstance(value, pytest.fail.Exception):
        return not str(value).startswith(TIMEOUT_PREFIX)
    return False


def _same_file(path: Path | str, other: str) -> bool:
    return os.path.realpath(path) == os.path.realpath(other)


def _is_test_module(path: Path | str) -> bool:
    """A ``test_*.py`` or ``*_test.py`` file: a helper imported from one is the test's side (#10670)."""
    name = Path(path).name
    return name.startswith("test_") or name.endswith("_test.py")


def _foreign_origin(
    item: pytest.Item, excinfo: pytest.ExceptionInfo[BaseException]
) -> str | None:
    """Where an assertion came from when it was not the test's own, else None."""
    function = getattr(item, "function", None)
    module_file = getattr(getattr(item, "module", None), "__file__", None)
    if function is None or module_file is None:
        return "an item with no test function"
    try:
        code = inspect.unwrap(function).__code__
    except (AttributeError, ValueError):
        return "an item with no test function"
    entries = list(excinfo.traceback)
    start = next(
        (index for index, entry in enumerate(entries) if entry.frame.code.raw is code),
        None,
    )
    if start is None:
        # Raised before or after the test body ran: a hook or a wrapper.
        last = entries[-1] if entries else None
        return "outside the test" + ("" if last is None else f" ({last.path})")
    inside = entries[start + 1 :]
    while inside:
        frame = Path(os.path.realpath(inside[-1].path))
        if frame.is_relative_to(_UNITTEST) or (
            inside[-1].ishidden(excinfo)
            and any(frame.is_relative_to(package) for package in _PYTEST)
        ):
            inside.pop()
        else:
            break
    for entry in inside:
        if not _same_file(entry.path, module_file) and not _is_test_module(entry.path):
            return f"{entry.path}:{entry.lineno + 1}"
    return None


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, Any, Any]:
    report = yield
    if report.when == "call" and report.passed:
        _record("passed", item.nodeid, "")
    elif report.failed:
        excinfo = call.excinfo
        kind = "unknown" if excinfo is None else excinfo.typename
        detail = f"{report.when}: {kind}"
        assertion = (
            report.when == "call" and excinfo is not None and _is_assertion(excinfo)
        )
        if assertion and excinfo is not None:
            origin = _foreign_origin(item, excinfo)
            if origin is not None:
                assertion = False
                detail += f" raised in {origin}, not by the test"
        _record("assertion" if assertion else "error", item.nodeid, detail)
    return report


def pytest_collectreport(report: pytest.CollectReport) -> None:
    if report.failed:
        _record("error", report.nodeid or "<collection>", "collection failed")
