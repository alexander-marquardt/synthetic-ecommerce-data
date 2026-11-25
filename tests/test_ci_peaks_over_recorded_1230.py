"""A shard's log names a module measured well above the peak recorded for it (#1230, slice 2).

The deal (``scripts/ci_shards.py``) keeps apart modules whose recorded peaks together outgrow the
container, so a peak that has grown past its record is a pair it no longer separates. On the
evening #1172 was OOM-killed the table held 2470 and 2209 MB for modules CI measured at 2873 and
2912. ``tests/worker_peak.py`` prints the line; docs/ci-sharding.md says how to refresh the table.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import worker_peak

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import ci_shards  # noqa: E402  (scripts/ is not a package)

VOICE = "tests/test_catalog_brands_voice.py"
LEAVES = "tests/test_retail_facet_leaves.py"

#: The child run's conftest: the plugin, a table of its own, and a heavy line 100 MB is over.
CONFTEST = """\
from pathlib import Path

import worker_peak


def pytest_configure(config):
    worker_peak.HEAVY_MB = 100
    worker_peak.RECORDED_PEAKS = Path(__file__).parent / "recorded.json"
    config.pluginmanager.register(worker_peak, "worker_peak")
"""
#: A module that holds 200 MB on top of what the worker holds.
HOLDS_200_MB = "def test_holds():\n    held = b'x' * (200 << 20)\n    del held\n"


def child_run(tmp_path: Path, recorded: dict[str, int]) -> list[str]:
    (tmp_path / "conftest.py").write_text(CONFTEST, encoding="utf-8")
    (tmp_path / "test_grown.py").write_text(HOLDS_200_MB, encoding="utf-8")
    (tmp_path / "recorded.json").write_text(json.dumps(recorded), encoding="utf-8")
    drop = ("PYTEST_ADDOPTS", "CI_SHARD", "CI_SHARDS", "WORKER_PEAK_DIR", "MODULE_PEAKS_OUT")
    env = {k: v for k, v in os.environ.items() if k not in drop}
    env["PYTHONPATH"] = str(REPO / "tests")
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-o", "addopts=", "-p", "no:cacheprovider",
         "--rootdir", str(tmp_path), "-n", "1", "test_grown.py"],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=120, check=False,
    )  # fmt: skip
    assert done.returncode == 0, done.stdout + done.stderr
    return done.stdout.splitlines()


def over_lines(printed: list[str]) -> list[str]:
    return [line for line in printed if line.startswith("module over its recorded peak:")]


@pytest.mark.skipif(not Path("/proc/self/clear_refs").exists(), reason="Linux /proc only")
def test_a_shard_names_a_module_that_outgrew_its_recorded_peak(tmp_path: Path) -> None:
    lines = over_lines(child_run(tmp_path, {"test_grown.py": 150}))
    assert len(lines) == 1, lines
    assert "test_grown.py measured " in lines[0] and "recorded 150 MB" in lines[0]
    assert "--refresh-peaks" in lines[0] and "docs/ci-sharding.md" in lines[0]


@pytest.mark.skipif(not Path("/proc/self/clear_refs").exists(), reason="Linux /proc only")
def test_a_shard_whose_module_is_within_its_recorded_peak_names_none(tmp_path: Path) -> None:
    printed = child_run(tmp_path, {"test_grown.py": 5000})
    assert any(line.startswith("module peak memory: 1 of 1") for line in printed), printed
    assert over_lines(printed) == []


def test_the_two_modules_of_1172_are_each_named_against_the_table_that_dealt_them() -> None:
    """Each was its worker's highest; light modules beside them ran on other modules' leftovers."""
    workers = [{VOICE: 2873, "tests/test_light.py": 1400}, {LEAVES: 2912, "tests/test_b.py": 2300}]
    recorded = {VOICE: 2470, LEAVES: 2209, "tests/test_light.py": 500, "tests/test_b.py": 700}
    named = worker_peak.over_recorded(workers, recorded)
    assert list(named.items()) == [(LEAVES, (2912, 2209)), (VOICE, (2873, 2470))]


@pytest.mark.parametrize(("measured", "named"), [(2200, False), (2201, True)])
def test_the_share_is_ten_per_cent_above_the_record(measured: int, named: bool) -> None:
    found = worker_peak.over_recorded([{VOICE: measured}], {VOICE: 2000})
    assert bool(found) is named


@pytest.mark.parametrize(("measured", "named"), [(1651, False), (1652, True)])
def test_a_module_with_no_record_is_held_to_what_the_deal_counts(
    measured: int, named: bool
) -> None:
    assert worker_peak.UNMEASURED_MB == ci_shards.UNMEASURED_MB
    found = worker_peak.over_recorded([{"tests/test_new.py": measured}], {})
    assert bool(found) is named


def test_a_module_at_or_under_the_heavy_line_is_not_named() -> None:
    """Nearly every such figure over its record is an earlier module's leftovers."""
    light = "tests/test_light.py"
    assert worker_peak.over_recorded([{light: 1500}], {light: 1}) == {}


def test_the_line_reads_the_table_the_deal_reads() -> None:
    assert worker_peak.RECORDED_PEAKS == ci_shards.MODULE_PEAKS
    assert worker_peak.recorded_peaks() == ci_shards.load_peaks()


def test_a_run_with_no_table_names_no_module(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(worker_peak, "RECORDED_PEAKS", tmp_path / "none.json")
    assert worker_peak.recorded_peaks() == {}


def test_the_docs_say_what_the_line_means_and_how_to_refresh() -> None:
    text = (REPO / "docs" / "ci-sharding.md").read_text(encoding="utf-8")
    assert "module over its recorded peak:" in text
    assert f"{worker_peak.OVER_SHARE:.0%}" in text
