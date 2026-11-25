"""No CI shard holds modules that run at the same time and outgrow its container (#1230).

A shard's two xdist workers each run one module at a time, so the two modules with the highest
recorded peaks (``scripts/ci_module_peaks.json``) can meet. Their sum is bounded by the
container less a margin (``ci_shards.SHARD_PEAK_MB``): the deal keeps such modules apart, a
change-scoped run takes another shard when it must, and a plan that cannot fails in
``scripts/ci_shards.py`` with the modules named. ``tests/fixtures/shard_plans_1230.json`` holds
the two plans that were OOM-killed. It runs nothing heavy.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import ci_shards  # noqa: E402  (scripts/ is not a package)

PLANS = json.loads((REPO / "tests/fixtures/shard_plans_1230.json").read_text(encoding="utf-8"))
VOICE = "tests/test_catalog_brands_voice.py"
LEAVES = "tests/test_retail_facet_leaves.py"
MERGE = "tests/test_merge_pr.py"


def _weights(plan: dict) -> dict[str, float]:
    return {name: w for name, w in plan["files"].items() if w is not None}


def _together(shards: list[list[str]]) -> int:
    """How many shards hold both modules #1172's shard 4 was killed in."""
    return sum({VOICE, LEAVES} <= set(shard) for shard in shards)


def _matrix_count() -> int:
    ci = yaml.safe_load((REPO / ".github/workflows/ci.yaml").read_text(encoding="utf-8"))
    return len(ci["jobs"]["tests"]["strategy"]["matrix"]["shard"])


def test_the_replayed_1172_plan_is_dealt_so_no_shard_outgrows_its_container() -> None:
    """The control is the plan CI ran: its tenth of the selection that was killed holds both."""
    plan = PLANS["1172"]
    files, weights, peaks = list(plan["files"]), _weights(plan), plan["peaks"]
    spread = frozenset(plan["spread"])
    unbounded = ci_shards.deal(files, plan["count"], weights, peaks={}, spread=spread)
    assert {VOICE, LEAVES} <= set(unbounded[3]), "the control is not the plan that was killed"
    over = ci_shards.concurrent_peak(unbounded[3], peaks, spread)
    assert over[0] > ci_shards.SHARD_PEAK_MB

    count = ci_shards.shards_needed(files, plan["of"], weights, peaks, spread)
    shards = ci_shards.deal(files, count, weights, peaks=peaks, spread=spread)
    assert _together(shards) == 0, "the two modules still meet on one shard"
    for shard in shards:
        total, names = ci_shards.concurrent_peak(shard, peaks, spread)
        assert total <= ci_shards.SHARD_PEAK_MB, f"{names} reach {total} MB on one shard"
    assert sorted(name for shard in shards for name in shard) == sorted(files)


def test_the_replayed_839_plan_fails_in_the_planner_naming_the_spread_module() -> None:
    """Both killed workers of #839's shard 9 were in ``tests/test_merge_pr.py`` (split over every
    shard, spread over both workers), and the largest process was 2767 MB: 5534 MB at once."""
    plan = PLANS["839"]
    files, weights, spread = list(plan["files"]), _weights(plan), frozenset(plan["spread"])
    split = frozenset(plan["spread"])
    refusal = ""
    try:
        ci_shards.deal(files, plan["of"], weights, split, peaks=plan["peaks"], spread=spread)
    except ci_shards.PlanError as error:
        refusal = str(error)
    assert MERGE in refusal, "the planner dealt a shard two 2767 MB workers would share"
    assert "5534 MB" in refusal


def test_the_839_files_are_dealt_once_the_split_module_holds_its_own_peak() -> None:
    """#844 freed the Generators: without them the module stays near 1500 MB, and it is dealt."""
    plan = PLANS["839"]
    files, weights, spread = list(plan["files"]), _weights(plan), frozenset(plan["spread"])
    peaks = {**plan["peaks"], MERGE: 1461}
    shards = ci_shards.deal(files, plan["of"], weights, spread, peaks=peaks, spread=spread)
    assert all(MERGE in shard for shard in shards)


def test_a_scoped_run_takes_another_shard_rather_than_hold_two_modules_that_cannot_meet() -> None:
    peaks = {"tests/test_a.py": 2900, "tests/test_b.py": 2870}
    weights = {"tests/test_a.py": 10.0, "tests/test_b.py": 10.0}
    assert ci_shards.shards_needed(sorted(peaks), 16, weights, {}, frozenset()) == 1, "control"
    count = ci_shards.shards_needed(sorted(peaks), 16, weights, peaks, frozenset())
    assert count == 2


@pytest.mark.parametrize("args", [["--plan", "1"], ["--shard", "1"]])
def test_a_plan_that_cannot_fit_ends_red_with_its_modules_named(
    args: list[str], monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    every = ci_shards.collected_test_files()
    # One module more than the matrix has shards, each too heavy to meet another.
    heavy = [name for name in every if name not in ci_shards.SPLIT_FILES][: _matrix_count() + 1]
    monkeypatch.setattr(ci_shards, "load_peaks", lambda *_: dict.fromkeys(heavy, 2900))
    code = ci_shards.main([*args, "--of", str(_matrix_count())])
    err = capsys.readouterr().err
    assert code == 1
    assert sum(name in err for name in heavy) == 2, err
    assert "5800 MB" in err


def test_a_module_alone_over_the_container_fails_naming_it() -> None:
    with pytest.raises(ci_shards.PlanError, match=r"tests/test_a\.py 5000 MB"):
        ci_shards.deal(
            ["tests/test_a.py"], 2, {}, peaks={"tests/test_a.py": 5000}, spread=frozenset()
        )


def test_a_spread_file_counts_on_every_worker() -> None:
    files, peaks = ["tests/test_a.py", "tests/test_b.py"], {"tests/test_a.py": 1400}
    assert ci_shards.concurrent_peak(files, peaks, frozenset()) == (
        ci_shards.UNMEASURED_MB + 1400,
        ["tests/test_b.py", "tests/test_a.py"],
    )
    peaks["tests/test_b.py"] = 1000
    spread = frozenset({"tests/test_a.py"})
    assert ci_shards.concurrent_peak(files, peaks, spread) == (2800, ["tests/test_a.py"] * 2)


def test_three_light_workers_fit_the_bound_too() -> None:
    """``workers`` gives a shard three when no module is over ``HEAVY_MB``."""
    assert ci_shards.LIGHT_WORKERS * ci_shards.HEAVY_MB <= ci_shards.SHARD_PEAK_MB
    assert ci_shards.SHARD_PEAK_MB == ci_shards.CONTAINER_MB - ci_shards.MARGIN_MB


@pytest.mark.parametrize("every", [1, 2, 3, 5], ids=lambda n: f"every-{n}th-file")
def test_no_shard_of_the_committed_plans_outgrows_its_container(every: int) -> None:
    files = ci_shards.collected_test_files()[::every]
    peaks, weights = ci_shards.load_peaks(), ci_shards.load_weights()
    spread = ci_shards.spread_files(files)
    of = _matrix_count()
    count = of if every == 1 else ci_shards.shards_needed(files, of, weights, peaks, spread)
    for shard in ci_shards.deal(files, count, weights, peaks=peaks, spread=spread):
        total, names = ci_shards.concurrent_peak(shard, peaks, spread | ci_shards.SPLIT_FILES)
        assert total <= ci_shards.SHARD_PEAK_MB, f"{names} reach {total} MB on one shard"


def test_the_peak_table_names_the_modules_main_measures_over_the_heavy_line() -> None:
    """Refreshed from main's runs 45308069902 to 45331393444 (#1230): the two modules of #1172's
    shard 4 no longer read 2470 and 2209 MB, so the bound sees them."""
    peaks = ci_shards.load_peaks()
    assert peaks[VOICE] + peaks[LEAVES] > ci_shards.SHARD_PEAK_MB
