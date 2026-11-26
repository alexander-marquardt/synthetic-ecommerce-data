"""A full run's deal gathers the heavy modules, so more shards run three workers (#1035).

A shard with one module over ``HEAVY_MB`` (or with no recorded peak) runs two workers, not
three (``scripts/ci_shards.py`` ``workers``). The deal by seconds alone spread main's heavy
modules one or two to a shard: on push run 45800458450, 11 of the 12 shards ran two workers,
and the run took 15.5 minutes against the 15 of #790. The deal now keeps the heavy modules on
as few shards as the memory bound and the budget allow, and weighs a shard by its seconds
over its workers:

* on main's tables, more than one shard of the 12 gets three workers, and the slowest shard
  ends sooner than in the deal that spreads the heavy modules over every shard;
* two heavy modules that fit together share a shard, and two that do not stay apart;
* a run with no heavy module is dealt by seconds alone, as before;
* no shard is dealt past the budget while another can take the file.

It times nothing, which would be red or green by the machine it ran on.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("ci_shards", REPO / "scripts" / "ci_shards.py")
assert _spec is not None and _spec.loader is not None
ci_shards = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("ci_shards", ci_shards)
_spec.loader.exec_module(ci_shards)

#: A self-hosted container's cap on ``-n auto``: the two ``workers`` raises to three.
RUNNER_CAP = "2"


def _shard_count() -> int:
    workflow = yaml.safe_load((REPO / ".github/workflows/ci.yaml").read_text(encoding="utf-8"))
    return len(workflow["jobs"]["tests"]["strategy"]["matrix"]["shard"])


def _walls(
    shards: list[list[str]], weights: dict[str, float], peaks: dict[str, int], count: int
) -> list[float]:
    """Each shard's seconds over the workers ``workers`` gives it on a self-hosted runner."""
    walls = []
    for shard in shards:
        seconds = sum(
            weights.get(name, ci_shards.DEFAULT_SECONDS)
            / (count if name in ci_shards.SPLIT_FILES else 1)
            for name in shard
        )
        workers = ci_shards.workers(shard, peaks, RUNNER_CAP)[0] or int(RUNNER_CAP)
        walls.append(seconds / workers)
    return walls


def test_main_s_full_run_gives_more_shards_three_workers_and_ends_sooner() -> None:
    count = _shard_count()
    files = ci_shards.collected_test_files()
    weights, peaks = ci_shards.load_weights(), ci_shards.load_peaks()
    spread = ci_shards.spread_files(files)
    dealt = ci_shards.deal(files, count, weights, peaks=peaks, spread=spread)
    heavy = frozenset(
        f for f in files if peaks.get(f, ci_shards.UNMEASURED_MB) > ci_shards.HEAVY_MB
    )
    split = sorted(ci_shards.SPLIT_FILES & set(files))
    seconds = {f: weights.get(f, ci_shards.DEFAULT_SECONDS) for f in files}
    whole = [f for f in files if f not in ci_shards.SPLIT_FILES]
    # The deal with the heavy modules free to go to any shard: main's before this change.
    spread_out = ci_shards._deal_into(
        whole, split, count, count, seconds, heavy, peaks, spread | ci_shards.SPLIT_FILES
    )[0]
    light = [shard for shard in dealt if ci_shards.workers(shard, peaks, RUNNER_CAP)[0] == 3]
    assert len(light) > 1, f"{len(light)} of {count} shards run three workers"
    now, before = _walls(dealt, weights, peaks, count), _walls(spread_out, weights, peaks, count)
    assert max(now) < max(before), (
        f"the slowest shard ends at {max(now):.0f} s, "
        f"not before the spread deal's {max(before):.0f} s"
    )


def test_two_heavy_modules_that_fit_together_share_a_shard() -> None:
    weights = {f"tests/test_light_{i:02}.py": 50.0 for i in range(12)}
    weights |= {"tests/test_heavy_a.py": 20.0, "tests/test_heavy_b.py": 10.0}
    peaks = {name: 500 for name in weights} | {
        "tests/test_heavy_a.py": 2000,
        "tests/test_heavy_b.py": 1800,
    }
    shards = ci_shards.deal(
        sorted(weights), 3, weights, split=frozenset(), peaks=peaks, spread=frozenset()
    )
    holding = [
        shard for shard in shards if {"tests/test_heavy_a.py", "tests/test_heavy_b.py"} & set(shard)
    ]
    assert len(holding) == 1, f"the heavy modules are spread: {shards}"
    assert sum(1 for shard in shards if ci_shards.workers(shard, peaks, RUNNER_CAP)[0] == 3) == 2


def test_two_heavy_modules_that_cannot_meet_stay_apart() -> None:
    weights = {f"tests/test_light_{i}.py": 100.0 for i in range(6)}
    weights |= {"tests/test_heavy_a.py": 50.0, "tests/test_heavy_b.py": 40.0}
    peaks = {name: 500 for name in weights} | {
        "tests/test_heavy_a.py": 2900,
        "tests/test_heavy_b.py": 2800,
    }
    shards = ci_shards.deal(
        sorted(weights), 3, weights, split=frozenset(), peaks=peaks, spread=frozenset()
    )
    for shard in shards:
        assert ci_shards.concurrent_peak(shard, peaks, frozenset())[0] <= ci_shards.SHARD_PEAK_MB, (
            shards
        )
    assert sorted(
        len({"tests/test_heavy_a.py", "tests/test_heavy_b.py"} & set(s)) for s in shards
    ) == [0, 1, 1]


def test_a_run_with_no_heavy_module_is_dealt_by_seconds_alone() -> None:
    weights = {
        f"tests/test_{c}.py": float(s)
        for c, s in zip("abcdef", [90, 80, 70, 40, 30, 10], strict=True)
    }
    peaks = {name: 500 for name in weights}
    shards = ci_shards.deal(
        sorted(weights), 2, weights, split=frozenset(), peaks=peaks, spread=frozenset()
    )
    assert shards == [
        ["tests/test_a.py", "tests/test_d.py", "tests/test_e.py"],
        ["tests/test_b.py", "tests/test_c.py", "tests/test_f.py"],
    ]


def test_a_three_worker_shard_is_not_dealt_past_the_budget() -> None:
    budget = ci_shards.SHARD_BUDGET_SECONDS
    weights = {f"tests/test_light_{i}.py": 0.3 * budget for i in range(8)}
    weights |= {"tests/test_heavy_a.py": 10.0}
    peaks = {name: 500 for name in weights} | {"tests/test_heavy_a.py": 2000}
    shards = ci_shards.deal(
        sorted(weights), 3, weights, split=frozenset(), peaks=peaks, spread=frozenset()
    )
    loads = [sum(weights[name] for name in shard) for shard in shards]
    assert max(loads) <= budget, f"a shard holds {max(loads):.0f} s, past the {budget:.0f} s budget"
