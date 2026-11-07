"""A CI shard runs three workers when no module of its plan was measured over 1500 MB (#790).

A self-hosted runner's container caps xdist at two workers (``PYTEST_XDIST_AUTO_NUM_WORKERS=2``
in a 6 GB container) because a few modules peak near 3 GB. Most shards run none of them, and a
light shard's busiest worker peaks under 1.5 GB, so three fit. ``scripts/ci_shards.py --workers``
reads the recorded per-module peaks (``scripts/ci_module_peaks.json``) and gives such a shard
three. A module measured over the line, or never measured, keeps the runner's count.
``--refresh-peaks`` rebuilds the table from the shards' ``module-peaks-*`` artifacts, which
``tests/worker_peak.py`` writes. It runs nothing heavy.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import worker_peak

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import ci_shards  # noqa: E402  (scripts/ is not a package)

SCRIPT = REPO / "scripts" / "ci_shards.py"
CI = yaml.safe_load((REPO / ".github" / "workflows" / "ci.yaml").read_text(encoding="utf-8"))
TESTS = CI["jobs"]["tests"]
CAP = "PYTEST_XDIST_AUTO_NUM_WORKERS"
#: Where a shard's run writes its module peaks, and the file its artifact uploads.
PEAKS_OUT = "${{ runner.temp }}/module-peaks-${{ matrix.shard }}.json"


def shards(*args: str, cap: str | None = "2") -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k != CAP}
    if cap is not None:
        env[CAP] = cap
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        env=env, capture_output=True, text=True, timeout=60, check=False,
    )  # fmt: skip


@pytest.fixture
def peaks(tmp_path: Path) -> Path:
    table = tmp_path / "peaks.json"
    table.write_text(
        json.dumps({"tests/test_a.py": 900, "tests/test_b.py": 1500, "tests/test_big.py": 2736}),
        encoding="utf-8",
    )
    return table


def test_a_shard_whose_modules_all_peak_at_most_1500_mb_gets_three_workers(peaks: Path) -> None:
    done = shards("--workers", "tests/test_a.py", "tests/test_b.py", "--peaks", str(peaks))
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "3"
    assert "no module of this shard's plan measured over 1500 MB" in done.stderr


def test_a_module_measured_over_1500_mb_keeps_the_runners_count(peaks: Path) -> None:
    done = shards("--workers", "tests/test_a.py", "tests/test_big.py", "--peaks", str(peaks))
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == ""
    assert "tests/test_big.py 2736 MB" in done.stderr


def test_a_module_with_no_measurement_counts_as_heavy(peaks: Path) -> None:
    done = shards("--workers", "tests/test_a.py", "tests/test_new.py", "--peaks", str(peaks))
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == ""
    assert "tests/test_new.py not measured" in done.stderr


@pytest.mark.parametrize("cap", [None, "3", "4"])
def test_a_runner_with_no_cap_below_three_is_left_alone(peaks: Path, cap: str | None) -> None:
    """A hosted runner sets no cap (``-n auto`` takes its cores); three would only lower it."""
    done = shards("--workers", "tests/test_a.py", "--peaks", str(peaks), cap=cap)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == ""


def test_the_refresh_keeps_each_modules_highest_figure_that_is_its_own(tmp_path: Path) -> None:
    """A worker's reset keeps what is resident, so a module run after a heavier one can read
    over 1500 MB on that one's leftovers. Such a figure, below its shard's highest, is not the
    module's own; a figure at or under 1500 MB always is, since leftovers only add."""
    one = tmp_path / "module-peaks-1.json"
    two = tmp_path / "module-peaks-12.json"
    one.write_text(json.dumps({"tests/test_merge.py": 1400, "tests/test_a.py": 700}), "utf-8")
    figures = {"tests/test_merge.py": 1785, "tests/test_big.py": 2390, "tests/test_a.py": 900}
    two.write_text(json.dumps(figures), encoding="utf-8")
    out = tmp_path / "peaks.json"
    done = shards("--refresh-peaks", str(one), str(two), "--peaks", str(out))
    assert done.returncode == 0, done.stderr
    table = json.loads(out.read_text(encoding="utf-8"))
    assert table == {"tests/test_a.py": 900, "tests/test_big.py": 2390, "tests/test_merge.py": 1400}


def test_a_module_whose_only_heavy_figures_are_below_a_heavier_one_is_not_recorded(
    tmp_path: Path,
) -> None:
    """With no figure of its own it is unmeasured, so it counts as heavy."""
    one = tmp_path / "module-peaks-14.json"
    one.write_text(json.dumps({"tests/test_big.py": 2595, "tests/test_next.py": 1504}), "utf-8")
    out = tmp_path / "peaks.json"
    done = shards("--refresh-peaks", str(one), "--peaks", str(out))
    assert done.returncode == 0, done.stderr
    assert json.loads(out.read_text(encoding="utf-8")) == {"tests/test_big.py": 2595}


def test_the_recorded_table_is_one_peak_in_mb_per_collected_test_file() -> None:
    table = json.loads((REPO / "scripts" / "ci_module_peaks.json").read_text(encoding="utf-8"))
    collected = set(ci_shards.collected_test_files())
    assert table, "no module has a recorded peak"
    assert all(isinstance(mb, int) and mb > 0 for mb in table.values())
    assert set(table) <= collected, sorted(set(table) - collected)


def test_the_heavy_line_is_the_one_the_module_peak_line_names_modules_by() -> None:
    assert getattr(ci_shards, "HEAVY_MB", None) == worker_peak.HEAVY_MB


def test_the_tests_step_exports_the_count_the_planner_gives() -> None:
    step = next(s for s in TESTS["steps"] if s.get("name") == "Tests")
    run = step["run"]
    assert 'python3 scripts/ci_shards.py --workers "${files[@]}"' in run
    assert 'export PYTEST_XDIST_AUTO_NUM_WORKERS="$workers"' in run
    assert run.index("--workers") < run.index("ci_run_pytest.py")
    assert step["env"].get("MODULE_PEAKS_OUT") == PEAKS_OUT


def test_each_shard_uploads_its_module_peaks() -> None:
    upload = [
        s for s in TESTS["steps"]
        if s.get("uses", "").startswith("actions/upload-artifact")
        and s["with"]["name"] == "module-peaks-${{ matrix.shard }}"
    ]  # fmt: skip
    assert upload, "no shard uploads the module peaks --refresh-peaks reads"
    assert upload[0]["if"] == "always()"
    assert upload[0]["with"]["path"] == PEAKS_OUT


#: Two modules on one worker, so the controller has two module peaks to write.
MODULE = "def test_one():\n    pass\n"


@pytest.mark.skipif(not Path("/proc/self/clear_refs").exists(), reason="Linux /proc only")
def test_a_run_writes_every_modules_peak_where_module_peaks_out_names(tmp_path: Path) -> None:
    (tmp_path / "conftest.py").write_text(
        "import worker_peak\n\n\ndef pytest_configure(config):\n"
        '    config.pluginmanager.register(worker_peak, "worker_peak")\n',
        encoding="utf-8",
    )
    (tmp_path / "test_one.py").write_text(MODULE, encoding="utf-8")
    (tmp_path / "test_two.py").write_text(MODULE, encoding="utf-8")
    out = tmp_path / "module-peaks.json"
    env = {k: v for k, v in os.environ.items() if k not in ("PYTEST_ADDOPTS", "WORKER_PEAK_DIR")}
    env["PYTHONPATH"] = str(REPO / "tests")
    env["MODULE_PEAKS_OUT"] = str(out)
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-o", "addopts=", "-p", "no:cacheprovider",
         "-p", "no:randomly", "--rootdir", str(tmp_path), "-n", "1",
         "test_one.py", "test_two.py"],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=120, check=False,
    )  # fmt: skip
    assert done.returncode == 0, done.stdout + done.stderr
    assert out.exists(), done.stdout
    table = json.loads(out.read_text(encoding="utf-8"))
    assert sorted(table) == ["test_one.py", "test_two.py"]
    assert all(isinstance(mb, int) and mb > 0 for mb in table.values())
