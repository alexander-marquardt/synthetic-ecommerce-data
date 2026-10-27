"""No CI shard is planned past the budget that fits its job's timeout (#704).

A pull request that touches the shared price code selects nearly every test file. The
scoped plan (``scripts/ci_shards.py``) dealt that selection to as few shards as kept each
under ``SCOPED_SHARD_SECONDS`` (1800 s of the weights), where a full run's shard holds
about 1121 s. Measured on the hosted runners (the 16 ``tests`` jobs of the push run 40436122954),
a shard takes 0.47 to 0.99 s of wall clock per second of weight, so a 1767 s shard ran 25
minutes and was cancelled at the job's ``timeout-minutes: 25`` (tests (5) of #696 and #697).

* the scoped shard budget is no heavier than a full run's shard, and the budget fits the timeout;
* a selection is dealt so that no shard's real load is past the budget (the longest-first deal
  can overshoot the average by a file, so the shard count is checked against the deal itself);
* the Tests step prints the slowest tests, so a slow test is named in the log the first time it
  appears.

It times nothing, which would be red or green by the machine it ran on.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "ci.yaml"

_spec = importlib.util.spec_from_file_location("ci_shards", REPO / "scripts" / "ci_shards.py")
assert _spec is not None and _spec.loader is not None
ci_shards = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("ci_shards", ci_shards)
_spec.loader.exec_module(ci_shards)

#: The worst wall-clock seconds per second of weight measured on a hosted shard (#704).
WORST_WALL_PER_WEIGHT = 1.0


def _tests_job() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["tests"]


def _loads(files: list[str], count: int, weights: dict[str, float]) -> list[float]:
    """Each shard's seconds of work as the deal makes it, a split file's share included."""
    return [
        sum(
            weights.get(name, ci_shards.DEFAULT_SECONDS)
            / (count if name in ci_shards.SPLIT_FILES and count > 1 else 1)
            for name in shard
        )
        for shard in ci_shards.deal(files, count, weights)
    ]


def test_a_scoped_shard_is_no_heavier_than_a_shard_of_a_full_run() -> None:
    count = len(_tests_job()["strategy"]["matrix"]["shard"])
    full = max(ci_shards.shard_loads(count))
    assert ci_shards.SCOPED_SHARD_SECONDS <= ci_shards.SHARD_BUDGET_SECONDS
    assert full <= ci_shards.SHARD_BUDGET_SECONDS, (
        f"a full run's heaviest shard is {full:.0f} s of the weights: refresh "
        "scripts/ci_shard_weights.json or add a shard (docs/ci-sharding.md)"
    )


def test_the_budget_leaves_the_job_timeout_a_fifth_to_spare() -> None:
    timeout_seconds = _tests_job()["timeout-minutes"] * 60
    assert 0.8 * timeout_seconds >= ci_shards.SHARD_BUDGET_SECONDS * WORST_WALL_PER_WEIGHT, (
        "the shard budget no longer fits the job's timeout; cut the budget "
        "(add shards), do not raise the timeout (#704)"
    )


@pytest.mark.parametrize("every", [1, 2, 3, 5], ids=lambda n: f"every-{n}th-file")
def test_no_selection_is_dealt_a_shard_past_the_budget(every: int) -> None:
    """The real weights and files: the whole suite, and a half, a third, a fifth of it."""
    weights = ci_shards.load_weights()
    files = ci_shards.collected_test_files()[::every]
    count = ci_shards.shards_needed(files, 16, weights)
    loads = _loads(files, count, weights)
    assert max(loads) <= ci_shards.SHARD_BUDGET_SECONDS, (
        f"{len(files)} files go to {count} shards of {[round(x) for x in loads]} s of work, "
        f"past the {ci_shards.SHARD_BUDGET_SECONDS:.0f} s budget"
    )


def test_a_deal_that_overshoots_the_budget_gets_one_more_shard() -> None:
    """Four files whose total needs 3 shards by the average, but whose longest-first deal
    puts two 0.6-budget files on one shard: that is 1.2 budgets, so it needs a fourth."""
    budget = ci_shards.SCOPED_SHARD_SECONDS
    weights = {
        "tests/test_a.py": 0.75 * budget,
        "tests/test_b.py": 0.6 * budget,
        "tests/test_c.py": 0.6 * budget,
        "tests/test_d.py": 0.6 * budget,
    }
    files = sorted(weights)
    count = ci_shards.shards_needed(files, 16, weights)
    assert max(_loads(files, count, weights)) <= budget, f"{count} shards is too few"


def test_the_tests_step_prints_the_ten_slowest_tests() -> None:
    (step,) = [s for s in _tests_job()["steps"] if s.get("name") == "Tests"]
    assert "--durations=10" in str(step["env"]["PYTEST_ADDOPTS"]).split()
