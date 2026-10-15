"""The local CI's tests job runs pytest on several workers, grouped by file (#348).

``scripts/merge_pr.sh --local-ci`` runs every job of ``.github/workflows/ci.yaml`` as
``scripts/local_ci_jobs.py`` emits it, and the ``tests`` job is the whole suite. On one
worker that took 47 to 54 minutes per merge, and merges are serial by design (each one
changes main and the generated golden files), so the chain landed one pull request an
hour.

The guard runs the emitted script of the real ``tests`` job with a stand-in ``uv`` that
records the environment and arguments pytest would have got, then reads the workers and
the distribution the way pytest would: from the command line and from
``PYTEST_ADDOPTS``. It times nothing, which would be red or green by the machine it ran
on. The grouping is checked on its own: with ``--dist loadgroup``, a module's tests run
on one worker only if each carries ``xdist_group``, and a module's fixtures (a 100K
build, say, 45 s) are rebuilt on every worker its tests are scattered over.
"""

from __future__ import annotations

import importlib.util
import os
import shlex
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from xdist_groups import group_for

REPO = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO / ".github" / "workflows"

_spec = importlib.util.spec_from_file_location(
    "local_ci_jobs", REPO / "scripts" / "local_ci_jobs.py"
)
assert _spec is not None and _spec.loader is not None
local_ci_jobs = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("local_ci_jobs", local_ci_jobs)
_spec.loader.exec_module(local_ci_jobs)

_FAKE_UV = """#!/usr/bin/env bash
printf 'ADDOPTS=%s\\tARGS=%s\\n' "${PYTEST_ADDOPTS:-}" "$*" >> "$FAKE_UV_LOG"
"""


def pytest_invocations(job_id: str, workflows: Path, tmp_path: Path) -> list[list[str]]:
    """Each pytest the job's emitted script runs: `PYTEST_ADDOPTS` tokens, then arguments."""
    jobs = local_ci_jobs.load_jobs(workflows)
    script = local_ci_jobs.emit(job_id, jobs[job_id], "BASE", "HEAD")
    stub = tmp_path / "bin"
    stub.mkdir()
    (stub / "uv").write_text(_FAKE_UV, encoding="utf-8")
    (stub / "uv").chmod(0o755)
    log = tmp_path / "uv.log"
    log.write_text("", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    env["PATH"] = f"{stub}:{env['PATH']}"
    env["FAKE_UV_LOG"] = str(log)
    done = subprocess.run(
        ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", script],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    found = []
    for record in log.read_text(encoding="utf-8").splitlines():
        addopts, _, args = record.partition("\tARGS=")
        tokens = [*shlex.split(addopts.removeprefix("ADDOPTS=")), *shlex.split(args)]
        if "pytest" in tokens:
            found.append(tokens)
    return found


def option(tokens: list[str], long: str, short: str = "") -> str | None:
    """The last value given for an option: ``--dist loadgroup``, ``--dist=loadgroup``, ``-n4``."""
    value = None
    for index, token in enumerate(tokens):
        if token == long or (short and token == short):
            value = tokens[index + 1] if index + 1 < len(tokens) else ""
        elif token.startswith(long + "="):
            value = token.split("=", 1)[1]
        elif short and token.startswith(short) and not token.startswith("--"):
            value = token[len(short) :].lstrip("=")
    return value


def is_parallel(tokens: list[str]) -> bool:
    workers = option(tokens, "--numprocesses", "-n") or "0"
    return workers == "auto" or (workers.isdigit() and int(workers) > 1)


def test_the_tests_job_runs_pytest_on_several_workers_grouped_by_file(tmp_path: Path) -> None:
    runs = pytest_invocations("tests", WORKFLOWS, tmp_path)
    assert runs, "the tests job no longer runs pytest: the merge has no suite to wait for"
    for tokens in runs:
        assert is_parallel(tokens), (
            "the tests job runs pytest on one worker, so `merge_pr.sh --local-ci` spends the "
            f"suite's whole serial time (about 50 minutes) per merge (#348): {tokens}"
        )
        assert option(tokens, "--dist") == "loadgroup", (
            "the workers do not keep a module's tests together (`--dist loadgroup`), so each "
            f"rebuilds the module's fixtures and the run is twice as slow (#348): {tokens}"
        )


@pytest.mark.parametrize(
    ("tokens", "parallel"),
    [
        (["pytest"], False),
        (["pytest", "-n", "0"], False),
        (["pytest", "-n=1"], False),
        (["pytest", "--numprocesses", "1"], False),
        (["pytest", "-n", "auto"], True),
        (["pytest", "-n8", "-q"], True),
        (["pytest", "--numprocesses=4"], True),
        (["pytest", "-n", "4", "-n", "0"], False),
    ],
)
def test_the_guard_tells_one_worker_from_several(tokens: list[str], parallel: bool) -> None:
    assert is_parallel(tokens) is parallel


def test_a_module_s_tests_share_a_group_unless_the_module_asks_to_spread() -> None:
    plain = SimpleNamespace(__name__="test_price")
    spread = SimpleNamespace(__name__="test_merge_pr", XDIST_SPREAD=True)
    assert group_for(plain) == "test_price"
    assert group_for(spread) is None


def test_the_worker_count_is_one_per_core_unless_the_machine_sets_it() -> None:
    assert local_ci_jobs.pytest_options({}) == "-n auto --dist loadgroup"
    assert local_ci_jobs.pytest_options({"LOCAL_CI_WORKERS": "6"}) == "-n 6 --dist loadgroup"
    assert local_ci_jobs.pytest_options({"LOCAL_CI_WORKERS": ""}) == "-n auto --dist loadgroup"


def test_the_emitted_script_takes_the_worker_count_from_the_machine_that_runs_it(
    tmp_path: Path,
) -> None:
    jobs = local_ci_jobs.load_jobs(WORKFLOWS)
    script = local_ci_jobs.emit("tests", jobs["tests"], "BASE", "HEAD")
    probe = f'{script}\necho "ADDOPTS=$PYTEST_ADDOPTS"\n'.replace("uv run", "true uv run")
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    for workers, expected in (("3", "-n 3 --dist loadgroup"), (None, "-n auto --dist loadgroup")):
        env.pop("LOCAL_CI_WORKERS", None)
        if workers:
            env["LOCAL_CI_WORKERS"] = workers
        done = subprocess.run(
            ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", probe],
            cwd=tmp_path, env=env, capture_output=True, text=True, check=False,
        )  # fmt: skip
        assert f"ADDOPTS={expected}" in done.stdout.splitlines(), done.stdout + done.stderr


def test_merge_pr_checks_step_runs_on_the_same_workers() -> None:
    cli = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "local_ci_jobs.py"), "--pytest-options"],
        capture_output=True,
        text=True,
        check=False,
        env={k: v for k, v in os.environ.items() if k != "LOCAL_CI_WORKERS"},
    )
    assert cli.stdout.strip() == "-n auto --dist loadgroup", cli.stderr
    script = (REPO / "scripts" / "merge_pr.sh").read_text(encoding="utf-8")
    (step,) = [line for line in script.splitlines() if "no:cacheprovider" in line]
    assert '"${parallel[@]}"' in step, step
    assert "--pytest-options" in script
