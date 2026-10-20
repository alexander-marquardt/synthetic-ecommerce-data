"""``--dist loadgroup`` keeps a module's tests on one worker, run through pytest itself (#442).

``tests/conftest.py`` marks each test with ``xdist_group(<module>)`` in its
``pytest_collection_modifyitems``, and ``tests/test_ci_tests_job_parallel_348.py`` checks that the
hook puts the mark on a test. That is the marker alone: xdist's worker-side hook suffixes the node
id with ``@<group>`` from the markers it sees, and it ran BEFORE the conftest hook, so it saw none
and a module's tests spread over the workers. These tests run a real ``-n 2 --dist loadgroup``
pytest, in a child process, over a two-test module whose module-scoped fixture records every build
and every test records its worker, and read what the workers did.

The child loads the repo's own ``tests/conftest.py`` hook function (not a copy), so the hook's
registration attributes travel with it.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

TESTS = Path(__file__).resolve().parent

CHILD_CONFTEST = f"""
import importlib.util
import sys

sys.path.insert(0, {str(TESTS)!r})
_spec = importlib.util.spec_from_file_location(
    "repo_tests_conftest", {str(TESTS / "conftest.py")!r}
)
_repo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_repo)
pytest_collection_modifyitems = _repo.pytest_collection_modifyitems
"""

CHILD_MODULE = """
import os
import pytest

{flag}

@pytest.fixture(scope="module")
def built(request):
    worker = request.config.workerinput["workerid"]
    with open(os.environ["BUILDS_LOG"], "a") as log:
        log.write(worker + "\\n")


def test_one(built, request):
    with open(os.environ["TESTS_LOG"], "a") as log:
        log.write(request.config.workerinput["workerid"] + "\\n")


def test_two(built, request):
    with open(os.environ["TESTS_LOG"], "a") as log:
        log.write(request.config.workerinput["workerid"] + "\\n")
"""


def _run_two_workers(tmp_path: Path, *, spread: bool) -> tuple[list[str], list[str]]:
    """The workers that built the module's fixture, and the workers that ran its two tests."""
    (tmp_path / "conftest.py").write_text(CHILD_CONFTEST)
    flag = "XDIST_SPREAD = True" if spread else ""
    (tmp_path / "test_two_tests.py").write_text(CHILD_MODULE.format(flag=flag))
    builds, ran = tmp_path / "builds.log", tmp_path / "tests.log"
    drop = ("PYTEST_ADDOPTS", "CI_SHARD", "CI_SHARDS")
    env = {k: v for k, v in os.environ.items() if k not in drop}
    env.update(BUILDS_LOG=str(builds), TESTS_LOG=str(ran))
    done = subprocess.run(
        [
            sys.executable, "-m", "pytest", "-o", "addopts=", "-p", "no:cacheprovider",
            "--rootdir", str(tmp_path), "-n", "2", "--dist", "loadgroup", "-v", "test_two_tests.py",
        ],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=120, check=False,
    )  # fmt: skip
    assert done.returncode == 0, done.stdout + done.stderr
    return builds.read_text().split(), ran.read_text().split()


def test_a_module_s_two_tests_run_on_one_worker_and_build_its_fixture_once(tmp_path: Path) -> None:
    builds, ran = _run_two_workers(tmp_path, spread=False)
    assert len(ran) == 2, f"both tests should have run once each: {ran}"
    assert len(set(ran)) == 1, (
        f"--dist loadgroup put the module's two tests on workers {sorted(ran)}: the "
        "xdist_group mark was added after xdist read the markers (#442)"
    )
    assert builds == [ran[0]], (
        f"the module-scoped fixture was built {len(builds)} times, on {sorted(builds)}; "
        "grouped, it is built once, on the worker that ran the tests"
    )


def test_a_module_that_asks_to_be_spread_is_still_spread(tmp_path: Path) -> None:
    """``XDIST_SPREAD = True`` (``tests/xdist_groups.py``) still spreads, hook first."""
    builds, ran = _run_two_workers(tmp_path, spread=True)
    assert len(ran) == 2, f"both tests should have run once each: {ran}"
    assert len(set(ran)) == 2, f"a module that asks to be spread ran on one worker: {ran}"
    assert sorted(builds) == sorted(ran), f"each worker builds its own fixture: {builds} vs {ran}"
