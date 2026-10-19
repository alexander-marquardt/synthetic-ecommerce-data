"""The CI tests job is sharded, and every test file runs in exactly one shard (#348).

``.github/workflows/ci.yaml`` runs the suite as a matrix of N shards on GitHub-hosted
runners; ``scripts/ci_shards.py`` deals the test files out. A file in no shard is a test
that never runs in CI; a file in two runs twice. Neither is visible in a green check, so
this guard reads the real workflow and the real tests directory:

* the matrix is ``1..N`` and every shard gets ``--of ${{ strategy.job-total }}``;
* the shards are disjoint, together they are every test file pytest collects, and none
  is empty;
* no CI job runs pytest on one worker: the hosted run's options (``PYTEST_ADDOPTS`` in
  the job's ``env``) carry ``-n`` and ``--dist loadgroup``, and a pytest line with no file
  list belongs only to a job that runs a named handful of checks;
* the shards stay balanced by the committed weights;
* a file too heavy for one shard (``SPLIT_FILES``: ``tests/test_merge_pr.py`` and its
  ``--github-ci`` sibling, 75 minutes of independent tests) is listed in every shard, and
  ``tests/ci_shard_split.py`` deals its test ids out modulo the shard, so each node id runs
  in exactly one shard;
* no job-level ``env`` reads the ``runner`` context, which GitHub rejects there (the
  whole workflow then fails in 0 s with no check run).

It times nothing, which would be red or green by the machine it ran on.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest
import yaml

from test_ci_tests_job_parallel_348 import is_parallel, option

REPO = Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "ci.yaml"

_spec = importlib.util.spec_from_file_location("ci_shards", REPO / "scripts" / "ci_shards.py")
assert _spec is not None and _spec.loader is not None
ci_shards = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("ci_shards", ci_shards)
_spec.loader.exec_module(ci_shards)


def _jobs() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]


def _shard_count() -> int:
    matrix = _jobs()["tests"]["strategy"]["matrix"]["shard"]
    assert matrix == list(range(1, len(matrix) + 1)), f"the shard matrix is not 1..N: {matrix}"
    return len(matrix)


def test_the_tests_job_is_a_matrix_of_shards_that_each_know_the_shard_count() -> None:
    job = _jobs()["tests"]
    assert job["strategy"]["fail-fast"] is False, "one red shard must not hide the others' reds"
    assert _shard_count() >= 2
    runs = " ".join(step.get("run", "") for step in job["steps"])
    assert "scripts/ci_shards.py --plan ${{ matrix.shard }} --of ${{ strategy.job-total }}" in runs
    assert "pytest" in runs and '"${files[@]}"' in runs, "the shard's files must reach pytest"


@pytest.mark.parametrize("count", [1, 2, 3, 6, 11])
def test_every_test_file_is_in_exactly_one_shard(count: int) -> None:
    files = ci_shards.collected_test_files()
    shards = ci_shards.deal(files, count, ci_shards.load_weights())
    flat = Counter(name for shard in shards for name in shard)
    # A split file is in every shard (its test ids are dealt out in ci_shard_split.py); any
    # other file is in exactly one.
    assert flat == {n: count if n in ci_shards.SPLIT_FILES else 1 for n in files}, (
        "a test file is in no shard, or in two"
    )
    assert all(shards), f"a shard of {count} is empty: a runner with nothing to run"


def test_the_workflow_s_own_shard_count_covers_every_file_through_the_script() -> None:
    count = _shard_count()
    seen: list[str] = []
    for number in range(1, count + 1):
        done = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "ci_shards.py"), "--shard", str(number)]
            + ["--of", str(count)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert done.returncode == 0, done.stderr
        seen += done.stdout.split()
    expected = {
        n: count if n in ci_shards.SPLIT_FILES else 1 for n in ci_shards.collected_test_files()
    }
    assert Counter(seen) == expected


def test_the_all_shard_is_every_file_for_a_run_that_is_not_sharded() -> None:
    done = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "ci_shards.py"), "--shard", "all"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.stdout.split() == ci_shards.collected_test_files()


@pytest.mark.parametrize("args", [["--shard", "0", "--of", "3"], ["--shard", "4", "--of", "3"], []])
def test_a_shard_outside_the_count_is_refused(args: list[str]) -> None:
    done = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "ci_shards.py"), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode != 0 and done.stdout == ""


def test_the_files_the_script_deals_are_the_files_pytest_collects() -> None:
    """The glob in ci_shards.py is pytest's collection rule, not a guess at it."""
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-o", "addopts=", "-p"]
        + ["no:cacheprovider", "-n", "0", "tests"],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stdout[-600:] + done.stderr[-600:]
    collected = {line.split("::")[0] for line in done.stdout.splitlines() if "::" in line}
    assert collected == set(ci_shards.collected_test_files())


def test_a_file_with_no_weight_weighs_the_default_so_a_new_test_file_needs_no_edit() -> None:
    weights = {"tests/test_a.py": 100.0, "tests/test_b.py": 100.0}
    files = ["tests/test_a.py", "tests/test_b.py", "tests/test_new.py"]
    # The two measured files fill a shard each; the new one is dealt, as a file of
    # DEFAULT_SECONDS, to the first (tied) shard.
    assert ci_shards.deal(files, 2, weights) == [
        ["tests/test_a.py", "tests/test_new.py"],
        ["tests/test_b.py"],
    ]
    assert 0 < ci_shards.DEFAULT_SECONDS < 100


def test_the_deal_is_the_same_every_time_so_a_rerun_runs_the_same_shards() -> None:
    files = ci_shards.collected_test_files()
    weights = ci_shards.load_weights()
    assert ci_shards.deal(files, 6, weights) == ci_shards.deal(list(reversed(files)), 6, weights)


def test_the_shards_stay_balanced_by_the_committed_weights() -> None:
    """The longest-first deal is within one file of perfect; a weight table that is not
    (one file that dwarfs the rest) is the signal to split that file or add shards."""
    count = _shard_count()
    weights = ci_shards.load_weights()
    files = ci_shards.collected_test_files()
    loads = ci_shards.shard_loads(count)
    total = sum(weights.get(f, ci_shards.DEFAULT_SECONDS) for f in files)
    heaviest = max(weights.get(f, ci_shards.DEFAULT_SECONDS) for f in files)
    assert max(loads) <= total / count + heaviest + 1e-6
    assert max(loads) <= 1.35 * total / count, (
        f"the shards are lopsided: {[round(x) for x in loads]} seconds of work; "
        "refresh scripts/ci_shard_weights.json (docs/ci-sharding.md) or add a shard"
    )


def _addopts(job: dict) -> list[str]:
    return str(job.get("env", {}).get("PYTEST_ADDOPTS", "")).split()


def test_no_ci_job_runs_pytest_on_one_worker() -> None:
    """The hosted run's workers, read from the workflow as GitHub reads it."""
    ran = 0
    for job_id, job in _jobs().items():
        if "pytest" not in " ".join(step.get("run", "") for step in job.get("steps", [])):
            continue
        ran += 1
        tokens = _addopts(job)
        assert is_parallel(["pytest", *tokens]), (
            f"job {job_id!r} runs pytest on one worker on GitHub: set PYTEST_ADDOPTS "
            f"'-n auto --dist loadgroup' in its env (#348): {tokens}"
        )
        assert option(tokens, "--dist") == "loadgroup", (
            f"job {job_id!r} does not keep a module's tests on one worker (--dist loadgroup)"
        )
    assert ran >= 2, "the workflow no longer runs pytest in the tests and merged-tree jobs"


def test_the_pytest_line_of_a_sharded_job_names_the_shard_files_not_the_whole_directory() -> None:
    tests = _jobs()["tests"]
    (step,) = [s for s in tests["steps"] if "pytest" in s.get("run", "")]
    pytest_lines = [line for line in step["run"].splitlines() if "pytest" in line]
    assert pytest_lines and all('"${files[@]}"' in line for line in pytest_lines), pytest_lines


def test_a_job_level_env_reads_no_runner_context() -> None:
    """GitHub rejects the whole workflow (a run that fails in 0 s, no checks) when a job's
    ``env`` holds ``${{ runner.* }}``: the context exists from step level only (#348)."""
    for job_id, job in _jobs().items():
        for key, value in (job.get("env") or {}).items():
            assert "runner." not in str(value), (
                f"job {job_id!r} env {key} reads the runner context, which is not available "
                "at job level: use $RUNNER_TEMP in the run script"
            )


def test_the_tests_step_tells_the_split_plugin_which_shard_it_is() -> None:
    (step,) = [s for s in _jobs()["tests"]["steps"] if "pytest" in s.get("run", "")]
    assert step.get("env", {}).get("CI_SHARD") == "${{ matrix.shard }}"
    assert step.get("env", {}).get("CI_SHARDS") == "${{ strategy.job-total }}"


@pytest.mark.parametrize("count", [2, 3, 10])
def test_a_split_file_is_listed_in_every_shard_and_weighs_its_share_in_each(count: int) -> None:
    weights = {"tests/test_big.py": 900.0, "tests/test_a.py": 100.0, "tests/test_b.py": 100.0}
    files = sorted(weights)
    shards = ci_shards.deal(files, count, weights, split=frozenset({"tests/test_big.py"}))
    assert all("tests/test_big.py" in shard for shard in shards)
    # Every other file is dealt once, and the big file's share is already in each load.
    assert Counter(n for shard in shards for n in shard if n != "tests/test_big.py") == {
        "tests/test_a.py": 1,
        "tests/test_b.py": 1,
    }


@pytest.mark.parametrize("count", [2, 3, 10])
def test_the_loads_hold_a_split_file_s_share_in_every_shard(count: int, tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    for name in ("test_big.py", "test_a.py", "test_b.py"):
        (tmp_path / "tests" / name).write_text("")
    weights = {"tests/test_big.py": 900.0, "tests/test_a.py": 100.0, "tests/test_b.py": 100.0}
    loads = ci_shards.shard_loads(count, tmp_path, weights, split=frozenset({"tests/test_big.py"}))
    assert sum(loads) == pytest.approx(1100.0)
    assert min(loads) >= 900 / count - 1e-6, "the split file's share is missing from a shard"


@pytest.mark.parametrize("count", [1, 2, 3, 7])
def test_the_split_index_deals_each_position_to_exactly_one_shard(count: int) -> None:
    dealt = [[i for i in range(20) if ci_shards.keeps(i, k, count)] for k in range(1, count + 1)]
    assert sorted(i for part in dealt for i in part) == list(range(20))
    assert dealt[0] == list(range(0, 20, count))


def _collect(files: list[str], extra_env: dict[str, str]) -> list[str]:
    dropped = ("PYTEST_ADDOPTS", "CI_SHARD", "CI_SHARDS")
    env = {k: v for k, v in os.environ.items() if k not in dropped}
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-o", "addopts=", "-p"]
        + ["no:cacheprovider", "-n", "0", *files],
        cwd=REPO,
        env={**env, **extra_env},
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stdout[-600:] + done.stderr[-600:]
    return [line for line in done.stdout.splitlines() if "::" in line]


def test_each_test_id_of_a_split_file_runs_in_exactly_one_shard() -> None:
    """The guard behind splitting ``tests/test_merge_pr.py``: collected under each shard's
    own environment, its node ids are disjoint and together are the whole file's."""
    count = _shard_count()
    assert ci_shards.SPLIT_FILES, "no file is split, so the slowest shard is that one file"
    files = sorted(ci_shards.SPLIT_FILES)
    whole = _collect(files, {})
    assert whole
    per_shard = [
        _collect(files, {"CI_SHARD": str(k), "CI_SHARDS": str(count)}) for k in range(1, count + 1)
    ]
    assert Counter(i for ids in per_shard for i in ids) == Counter(whole), (
        "a test id of a split file is in no shard, or in two"
    )
    assert all(per_shard), "a shard holds none of the split file's tests"
