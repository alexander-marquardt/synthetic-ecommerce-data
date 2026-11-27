"""Every test runs under a per-test time limit (elastic/prism#10032).

Without one, a test that hangs or grows its memory without end holds the
machine until something outside pytest kills it. ``tests/per_test_timeout.py``
turns that into one failed test. It replaced ``pytest-timeout``, which had no
release in 18 months (#1103). These guards fail if the plugin stops being
loaded, if the configured limit is removed, or if a hang is no longer stopped.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
import tomllib
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
#: A timed-out case's line in its traceback (the short summary may repeat the message).
_TIMED_OUT = re.compile(r"^E +Failed: Timeout \(>1s\)", re.MULTILINE)

#: A test body that hangs, a fixture that hangs, and a test that ends at once,
#: each under a one-second limit.
_INNER = """
import time

import pytest


@pytest.fixture
def slow_setup():
    time.sleep(3)


@pytest.mark.timeout(1)
def test_the_body_hangs():
    time.sleep(30)


def test_the_fixture_hangs(slow_setup):
    pass


def test_a_quick_one():
    pass


@pytest.mark.timeout(0)
def test_a_zero_limit_is_none():
    time.sleep(1.5)
"""


def _run_inner(tmp_path: Path, *options: str) -> tuple[str, float]:
    """The inner file's run under the plugin alone (no config file), its log and seconds."""
    (tmp_path / "test_inner_1103.py").write_text(_INNER)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTEST_", "GEN_LOCAL_CI"))}
    env["PYTHONPATH"] = str(TESTS)
    started = time.monotonic()
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", "-c", os.devnull, "--rootdir", str(tmp_path),
            "-p", "no:cacheprovider", "-p", "per_test_timeout", "-o", "timeout=1",
            *options, "-rA", str(tmp_path / "test_inner_1103.py"),
        ],
        env=env, cwd=tmp_path, capture_output=True, text=True, check=False, timeout=120,
    )  # fmt: skip
    return result.stdout + result.stderr, time.monotonic() - started


def test_the_timeout_plugin_is_loaded(pytestconfig: pytest.Config) -> None:
    assert pytestconfig.pluginmanager.has_plugin("per_test_timeout") is True


def test_every_test_has_a_300_second_limit(pytestconfig: pytest.Config) -> None:
    assert pytestconfig.getini("timeout") == "300"


def test_pytest_timeout_is_not_a_dependency() -> None:
    pyproject = tomllib.loads((TESTS.parent / "pyproject.toml").read_text())
    dev = pyproject["dependency-groups"]["dev"]
    assert not [d for d in dev if d.startswith("pytest-timeout")], dev


def test_a_hang_in_the_body_or_a_fixture_fails_at_its_limit(tmp_path: Path) -> None:
    log, seconds = _run_inner(tmp_path)
    assert "FAILED test_inner_1103.py::test_the_body_hangs" in log, log
    assert "ERROR test_inner_1103.py::test_the_fixture_hangs" in log, log
    assert len(_TIMED_OUT.findall(log)) == 2, log
    assert "PASSED test_inner_1103.py::test_a_quick_one" in log, log
    assert "PASSED test_inner_1103.py::test_a_zero_limit_is_none" in log, log
    assert seconds < 25, f"the run took {seconds:.0f} s: a limit did not stop its test"


def test_func_only_leaves_the_fixtures_out_of_the_limit(tmp_path: Path) -> None:
    log, _ = _run_inner(tmp_path, "-o", "timeout_func_only=true")
    assert "FAILED test_inner_1103.py::test_the_body_hangs" in log, log
    assert len(_TIMED_OUT.findall(log)) == 1, log
    assert "PASSED test_inner_1103.py::test_the_fixture_hangs" in log, log
