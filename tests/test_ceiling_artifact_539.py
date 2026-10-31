"""The ceiling catalogue is built once per CI run and every test worker loads it (#539).

45 test files built the ceiling for themselves, about a minute each, and each shard measured the
figures on top. ``scripts/build_ceiling.py`` builds both in the ``ceiling-catalogue`` job,
``retail_figures.ceiling`` reads them, and a run can be put in a random order on request.
"""

from __future__ import annotations

import contextlib
import fcntl
import importlib.util
import json
import os
import pickle
import re
import subprocess
import sys
import threading
import tomllib
from pathlib import Path

import yaml

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import retail_figures, scale

REPO = Path(__file__).resolve().parent.parent
CI = yaml.safe_load((REPO / ".github" / "workflows" / "ci.yaml").read_text(encoding="utf-8"))
TESTS = CI["jobs"]["tests"]
SMALL = scale.Scaled(records=[{"product_id": "A", "sku_count": 1, "sizes": ("S", "M")}],
                     template_of={"A": "B"})  # fmt: skip
ROOT_CONFTEST = "import worker_peak\n\n\ndef pytest_configure(config):\n" \
    '    config.pluginmanager.register(worker_peak, "worker_peak")\n'  # fmt: skip

#: A target past the ceiling, as the tests wrote one, or a name that held such a target.
PAST_THE_CEILING = re.compile(
    r"scale\.build\((10\*\*\d|\d{1,3}(_\d{3}){2,}|\d{7,}|CEILING\b|\w*\.?EXHAUST)"
)
#: The tests that need a build of their own: two builds compared, not one read.
OWN_BUILD = {"tests/test_retail_distractors.py"}


def _step(uses: str) -> dict:
    return next(s for s in TESTS["steps"] if s.get("uses", "").startswith(uses))


def _no_shared_build(monkeypatch) -> list[int]:
    """Count ``scale.build`` calls, each answering ``SMALL``, from an empty memo."""
    calls: list[int] = []

    def build(skus: int, seed: int = 0) -> scale.Scaled:
        calls.append(skus)
        return SMALL

    monkeypatch.setattr(scale, "build", build)
    monkeypatch.setattr(retail_figures, "_MEMO", {})
    return calls


def test_a_worker_loads_the_run_s_catalogue_and_never_builds(tmp_path, monkeypatch) -> None:
    calls = _no_shared_build(monkeypatch)
    (tmp_path / retail_figures.CEILING_FILE).write_bytes(pickle.dumps(SMALL))
    monkeypatch.setenv(retail_figures.CACHE_ENV, str(tmp_path))
    assert ceiling_build() == SMALL
    assert ceiling_build() is ceiling_build(), "a worker's files share one object"
    assert calls == []


def test_with_no_catalogue_the_first_worker_builds_and_shares(tmp_path, monkeypatch) -> None:
    calls = _no_shared_build(monkeypatch)
    monkeypatch.setenv(retail_figures.CACHE_ENV, str(tmp_path))
    assert ceiling_build() == SMALL
    monkeypatch.setattr(retail_figures, "_MEMO", {})
    loaded = ceiling_build()
    assert loaded == SMALL and loaded is not SMALL
    assert calls == [retail_figures.EXHAUST]


def test_with_no_cache_directory_the_ceiling_is_built_in_process(monkeypatch) -> None:
    calls = _no_shared_build(monkeypatch)
    monkeypatch.delenv(retail_figures.CACHE_ENV, raising=False)
    assert ceiling_build() is SMALL
    assert ceiling_build() is SMALL
    assert calls == [retail_figures.EXHAUST]


def test_the_figures_measure_the_shared_build_so_the_job_builds_once(tmp_path, monkeypatch) -> None:
    calls = _no_shared_build(monkeypatch)
    monkeypatch.setenv(retail_figures.CACHE_ENV, str(tmp_path))
    monkeypatch.setattr(retail_figures, "measure", lambda: {"built": retail_figures.ceiling().skus})
    assert retail_figures.figures() == {"built": 1}, "figures() and ceiling() must not deadlock"
    assert (tmp_path / retail_figures.CEILING_FILE).is_file()
    assert calls == [retail_figures.EXHAUST]


def test_the_build_waits_on_its_own_lock_not_the_one_figures_holds(tmp_path, monkeypatch) -> None:
    """``figures`` holds ``lock`` while ``measure`` asks for the ceiling: one lock would hang it."""
    _no_shared_build(monkeypatch)
    monkeypatch.setenv(retail_figures.CACHE_ENV, str(tmp_path))
    with open(tmp_path / "lock", "a+", encoding="utf-8") as held:
        fcntl.flock(held, fcntl.LOCK_EX)
        worker = threading.Thread(target=retail_figures.ceiling, daemon=True)
        worker.start()
        worker.join(10)
        assert not worker.is_alive(), "ceiling() waited on the lock figures() holds"


def _build_ceiling():
    spec = importlib.util.spec_from_file_location(
        "build_ceiling", REPO / "scripts" / "build_ceiling.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_job_s_script_leaves_the_two_files_and_nothing_from_an_older_tree(
    tmp_path, monkeypatch
) -> None:
    calls = _no_shared_build(monkeypatch)
    monkeypatch.setattr(retail_figures, "measure", lambda: {"built": retail_figures.ceiling().skus})
    # build() names the directory in the environment for its own process: put it back after.
    monkeypatch.setenv(retail_figures.CACHE_ENV, str(tmp_path / "unused"))
    out = tmp_path / "ceiling"
    out.mkdir()
    (out / retail_figures.FIGURES_FILE).write_text('{"built": 99}', encoding="utf-8")
    (out / retail_figures.CEILING_FILE).write_bytes(pickle.dumps(None))
    assert _build_ceiling().main(["--out", str(out)]) == 0
    assert json.loads((out / retail_figures.FIGURES_FILE).read_text("utf-8")) == {"built": 1}
    assert pickle.loads((out / retail_figures.CEILING_FILE).read_bytes()) == SMALL
    assert calls == [retail_figures.EXHAUST]


def test_the_job_s_script_refuses_a_measurement_that_left_no_build(tmp_path, monkeypatch) -> None:
    _no_shared_build(monkeypatch)
    monkeypatch.setattr(retail_figures, "measure", lambda: {"built": 0})
    monkeypatch.setenv(retail_figures.CACHE_ENV, str(tmp_path / "unused"))
    refusal = ""
    try:
        _build_ceiling().build(tmp_path / "ceiling")
    except SystemExit as refused:
        refusal = str(refused)
    assert retail_figures.CEILING_FILE in refusal


def test_the_job_s_script_measures_into_the_directory_it_was_given(tmp_path, monkeypatch) -> None:
    named: list[str] = []
    monkeypatch.setattr(
        retail_figures, "measure", lambda: named.append(os.environ[retail_figures.CACHE_ENV]) or {}
    )
    monkeypatch.setattr(retail_figures, "_MEMO", {})
    (tmp_path / "unused").mkdir()
    monkeypatch.setenv(retail_figures.CACHE_ENV, str(tmp_path / "unused"))
    with contextlib.suppress(SystemExit):
        _build_ceiling().build(tmp_path / "ceiling")
    assert named == [str(tmp_path / "ceiling")]


def test_the_measurement_reads_the_shared_build(monkeypatch) -> None:
    """Built by ``measure`` itself, the job would build twice and upload no ``ceiling.pickle``."""

    class Asked(Exception):
        pass

    asked: list[str] = []

    def shared() -> scale.Scaled:
        asked.append("shared")
        raise Asked

    def own_build(skus: int, seed: int = 0) -> scale.Scaled:
        asked.append("own")
        raise Asked

    monkeypatch.setattr(scale, "build", own_build)
    monkeypatch.setattr(retail_figures, "ceiling", shared)
    with contextlib.suppress(Asked):
        retail_figures.measure()
    assert asked == ["shared"]


def test_a_real_build_survives_the_pickle() -> None:
    """A tuple stays a tuple through the artifact, so a test reads what the build made."""
    built = scale.build(3000)
    assert pickle.loads(pickle.dumps(built, pickle.HIGHEST_PROTOCOL)) == built


def test_every_shard_with_a_file_to_run_downloads_the_catalogue() -> None:
    assert TESTS.get("needs") == "ceiling-catalogue"
    download = _step("actions/download-artifact")
    assert download.get("if") == "steps.select.outputs.run == 'true'"
    upload = next(
        s for s in CI["jobs"]["ceiling-catalogue"]["steps"]
        if s.get("uses", "").startswith("actions/upload-artifact")
    )  # fmt: skip
    assert download["with"]["name"] == upload["with"]["name"]
    assert download["with"]["path"] == upload["with"]["path"] == "build/ceiling"


def test_the_shards_point_the_workers_at_what_they_downloaded() -> None:
    run = next(s for s in TESTS["steps"] if s.get("name") == "Tests")["run"]
    assert 'export RETAIL_FIGURES_CACHE="$PWD/build/ceiling"' in run
    assert run.index("RETAIL_FIGURES_CACHE") < run.index("ci_run_pytest.py")


def test_the_catalogue_job_runs_on_every_event_and_builds_where_it_uploads() -> None:
    job = CI["jobs"]["ceiling-catalogue"]
    assert "if" not in job, "a push to main and a dispatched run have tests too"
    runs = " ".join(s.get("run", "") for s in job["steps"])
    assert "scripts/build_ceiling.py --out build/ceiling" in runs


def test_the_local_run_reaches_the_catalogue_job_before_the_tests() -> None:
    """``local_ci_jobs.py`` takes the jobs in file order, and ignores ``needs``."""
    names = list(CI["jobs"])
    assert names.index("ceiling-catalogue") < names.index("tests")


def test_no_test_builds_past_the_ceiling_itself() -> None:
    """A new file copying ``scale.build(10**6)`` costs a minute and a build per worker again."""
    tracked = subprocess.run(
        ["git", "ls-files", "tests/*.py"], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.split()
    own = Path(__file__).relative_to(REPO).as_posix()
    found = [
        path for path in tracked
        if path not in {*OWN_BUILD, own}
        and PAST_THE_CEILING.search((REPO / path).read_text(encoding="utf-8"))
    ]  # fmt: skip
    assert found == [], "take the build from tests/retail_ceiling.py (ceiling_build())"


def test_random_order_is_off_unless_a_run_asks() -> None:
    config = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    assert "-p no:randomly" in config["tool"]["pytest"]["ini_options"]["addopts"]


def test_a_child_run_that_clears_addopts_keeps_random_order_blocked() -> None:
    """``-o addopts=`` drops the block, and an installed pytest-randomly then shuffles the child."""
    tracked = subprocess.run(
        ["git", "ls-files", "tests/*.py"], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.split()
    own = Path(__file__).relative_to(REPO).as_posix()
    bare = []
    for path in tracked:
        lines = (REPO / path).read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines):
            near = "\n".join(lines[number : number + 4])
            if path != own and '"addopts="' in line and "no:randomly" not in near:
                bare.append(f"{path}:{number + 1}")
    assert bare == []


def test_a_dispatched_seed_turns_random_order_on() -> None:
    assert "random_seed" in CI[True]["workflow_dispatch"]["inputs"]  # YAML reads `on:` as True
    addopts = next(s for s in TESTS["steps"] if s.get("name") == "Tests")["env"]["PYTEST_ADDOPTS"]
    assert "format('-p randomly --randomly-seed={0}', inputs.random_seed)" in addopts


def _child_pytest(tmp_path: Path, *options: str) -> str:
    (tmp_path / "conftest.py").write_text(ROOT_CONFTEST, encoding="utf-8")
    (tmp_path / "test_two.py").write_text(
        "def test_one():\n    pass\n\n\ndef test_two():\n    pass\n", encoding="utf-8"
    )
    drop = ("PYTEST_ADDOPTS", "CI_SHARD", "CI_SHARDS")
    env = {k: v for k, v in os.environ.items() if k not in drop}
    env["PYTHONPATH"] = str(REPO / "tests")
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-o", "addopts=", "-p", "no:cacheprovider",
         "--rootdir", str(tmp_path), *options, "test_two.py"],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=120, check=False,
    )  # fmt: skip
    assert done.returncode == 0, done.stdout + done.stderr
    return done.stdout


def test_the_seed_option_comes_after_the_block_and_undoes_it(tmp_path) -> None:
    """``-p randomly`` after ``-p no:randomly``: the order ``addopts`` then ``PYTEST_ADDOPTS``."""
    assert "randomly-seed" not in _child_pytest(tmp_path, "-p", "no:randomly")
    on = _child_pytest(tmp_path, "-p", "no:randomly", "-p", "randomly", "--randomly-seed=7")
    assert "--randomly-seed=7" in on


def test_a_run_on_workers_prints_their_peak(tmp_path) -> None:
    printed = _child_pytest(tmp_path, "-n", "1")
    assert re.search(r"^peak worker memory: \d+ MB \(gw\d", printed, re.M)


def test_a_run_with_no_workers_prints_no_peak(tmp_path) -> None:
    assert "peak worker memory" not in _child_pytest(tmp_path)


def test_the_peak_is_the_high_water_mark_line_in_mb() -> None:
    import worker_peak  # noqa: PLC0415

    assert worker_peak.peak_mb("VmPeak:\t 9 kB\nVmHWM:\t 204800 kB\nVmRSS:\t 1 kB\n") == 200
    assert worker_peak.peak_mb("VmRSS:\t 1 kB\n") is None
    assert worker_peak.summary({"gw1": 7, "gw0": 9}) == "peak worker memory: 9 MB (gw0 9, gw1 7)"
