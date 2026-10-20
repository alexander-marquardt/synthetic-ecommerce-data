"""The local run hands pytest the heaviest module first and the spread files last (#348).

``--dist loadgroup`` gives each worker the next module as it frees up, in the order pytest
collected them. The files were listed alphabetically, so the heavy modules that sort late
(``test_retail_scale.py`` and two other retail modules, starting at about 910-1020 s in the
13-worker replay) started when the other workers were nearly done and were the tail of the
run. Listing the modules longest-first (and the files whose tests xdist spreads, which are
many small units, last, as the filler that closes the gaps) is the classic longest-first schedule.

The guard times nothing: it replays xdist's rule (each unit goes to the worker that frees
first) over the committed weights of ``scripts/ci_shard_weights.json``, so it is red or
green by the order and not by the machine.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("ci_shards", REPO / "scripts" / "ci_shards.py")
assert _spec is not None and _spec.loader is not None
ci_shards = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("ci_shards", ci_shards)
_spec.loader.exec_module(ci_shards)


def makespan(order: list[str], workers: int, weights: dict[str, float], spread: frozenset[str]):
    """Seconds until the last worker ends: units go to the worker that frees first.

    A spread file is many small units (one ``DEFAULT_SECONDS`` each); any other file is one.
    """
    units: list[float] = []
    for name in order:
        seconds = weights.get(name, ci_shards.DEFAULT_SECONDS)
        if name in spread:
            count = max(1, int(seconds // ci_shards.DEFAULT_SECONDS))
            units += [seconds / count] * count
        else:
            units.append(seconds)
    free = [0.0] * workers
    for unit in units:
        free[free.index(min(free))] += unit
    return max(free)


def test_the_heaviest_module_is_first_and_a_tie_goes_to_the_name() -> None:
    weights = {"tests/test_a.py": 21.0, "tests/test_b.py": 300.0, "tests/test_c.py": 300.0}
    files = ["tests/test_a.py", "tests/test_c.py", "tests/test_b.py"]
    assert ci_shards.run_order(files, weights, frozenset()) == [
        "tests/test_b.py",
        "tests/test_c.py",
        "tests/test_a.py",
    ]


def test_a_new_file_weighs_the_default_in_the_order() -> None:
    weights = {"tests/test_a.py": 1.0, "tests/test_b.py": 1000.0}
    order = ci_shards.run_order(
        ["tests/test_a.py", "tests/test_b.py", "tests/test_new.py"], weights, frozenset()
    )
    assert order == ["tests/test_b.py", "tests/test_new.py", "tests/test_a.py"]


def test_a_spread_file_goes_last_however_heavy() -> None:
    weights = {"tests/test_big.py": 5000.0, "tests/test_a.py": 50.0, "tests/test_z.py": 40.0}
    order = ci_shards.run_order(
        ["tests/test_a.py", "tests/test_big.py", "tests/test_z.py"],
        weights,
        frozenset({"tests/test_big.py"}),
    )
    assert order == ["tests/test_a.py", "tests/test_z.py", "tests/test_big.py"]


def test_the_order_is_a_permutation_of_the_files_and_the_same_every_time() -> None:
    files = ci_shards.collected_test_files()
    weights = ci_shards.load_weights()
    spread = ci_shards.spread_files(files)
    order = ci_shards.run_order(files, weights, spread)
    assert sorted(order) == files
    assert order == ci_shards.run_order(list(reversed(files)), weights, spread)


def test_a_module_that_sets_xdist_spread_is_a_spread_file(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    spreads = tmp_path / "tests" / "test_spreads.py"
    spreads.write_text("XDIST_SPREAD = True\n\ndef test_x():\n    pass\n", encoding="utf-8")
    grouped = tmp_path / "tests" / "test_grouped.py"
    grouped.write_text("XDIST_SPREAD = False\n\ndef test_y():\n    pass\n", encoding="utf-8")
    mentions = tmp_path / "tests" / "test_mentions.py"
    mentions.write_text(
        '"""Say XDIST_SPREAD = True in a module to spread it."""\n', encoding="utf-8"
    )
    names = [p.relative_to(tmp_path).as_posix() for p in (spreads, grouped, mentions)]
    assert ci_shards.spread_files(names, tmp_path) == {"tests/test_spreads.py"}


def test_the_files_the_repo_spreads_are_found() -> None:
    spread = ci_shards.spread_files(ci_shards.collected_test_files())
    assert {
        "tests/test_merge_pr.py",
        "tests/test_merge_pr_github_ci_348.py",
        "tests/test_merge_pr_red_log_453.py",
    } <= spread
    assert spread >= ci_shards.SPLIT_FILES


def test_plan_all_lists_the_files_in_run_order() -> None:
    done = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "ci_shards.py"), "--plan", "all"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert done.returncode == 0, done.stderr
    first, *files = done.stdout.splitlines()
    assert first == "shards=1"
    every = ci_shards.collected_test_files()
    expected = ci_shards.run_order(every, ci_shards.load_weights(), ci_shards.spread_files(every))
    assert files == expected
    assert files != every, "the local run is not handed the files alphabetically"


def test_a_shard_plan_lists_its_files_in_run_order() -> None:
    done = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "ci_shards.py"), "--plan", "1", "--of", "3"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert done.returncode == 0, done.stderr
    first, *files = done.stdout.splitlines()
    every = ci_shards.collected_test_files()
    spread = ci_shards.spread_files(every)
    assert files == ci_shards.run_order(files, ci_shards.load_weights(), spread)
    assert files != sorted(files), "a shard of 60 files is not already alphabetical in run order"


@pytest.mark.parametrize("workers", [8, 12, 13, 24])
def test_run_order_ends_within_a_tenth_of_perfect_balance_and_beats_alphabetical(
    workers: int,
) -> None:
    files = ci_shards.collected_test_files()
    weights = ci_shards.load_weights()
    spread = ci_shards.spread_files(files)
    ordered = makespan(ci_shards.run_order(files, weights, spread), workers, weights, spread)
    alphabetical = makespan(files, workers, weights, spread)
    ideal = sum(weights.get(name, ci_shards.DEFAULT_SECONDS) for name in files) / workers
    assert ordered <= 1.10 * ideal, f"{ordered:.0f} s against {ideal:.0f} s of perfect balance"
    assert ordered < alphabetical, f"{ordered:.0f} s is not under alphabetical {alphabetical:.0f} s"
