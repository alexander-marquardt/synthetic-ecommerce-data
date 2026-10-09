"""The retail catalog has ONE food tree: ``Food & Drink`` (departments.py), never a second root.

The build once emitted a legacy ``Food/...`` root beside ``Food & Drink/...`` (27 products
from the failure-class rows, the planted distractors and the round 1 samples), so the
"query names a category" policy for *lemons* resolved to a one-product node instead of the
real ``Food & Drink > Fruit & Vegetables > Fresh Fruit > Citrus Fruit > Lemons``.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
sys.path.insert(0, str(RETAIL))

import build_preview4  # noqa: E402
import class_rows  # noqa: E402
import samples  # noqa: E402
import scale  # noqa: E402
from departments import DEPARTMENTS  # noqa: E402

#: The roots that are not a department name: a department is where a word's meaning flips,
#: while these roots name an audience (Women, Men, Kids, Baby) or an aisle that the
#: department list files under another name (Cleaning, Electricals). A new root is added
#: here on purpose or the test fails.
NON_DEPARTMENT_ROOTS = frozenset({"Women", "Men", "Kids", "Baby", "Cleaning", "Electricals"})

LEMONS_NODE = ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Citrus Fruit", "Lemons")


@pytest.fixture(scope="module")
def records() -> list[dict]:
    return scale.build(10**6).records


def test_no_record_sits_under_a_food_root(records: list[dict]) -> None:
    food = [r["product_id"] for r in records if r["category_path"][0] == "Food"]
    assert food == []


def test_every_root_is_a_department_or_a_declared_non_department_root(
    records: list[dict],
) -> None:
    roots = {r["category_path"][0] for r in records}
    assert sorted(roots - set(DEPARTMENTS) - NON_DEPARTMENT_ROOTS) == []
    # The declared list stays exact: a root the build no longer emits is removed from it.
    assert sorted(NON_DEPARTMENT_ROOTS - roots) == []


def test_the_food_roots_of_the_other_sources_are_gone() -> None:
    """The failure-class rows, the planted distractors and the round 1 samples."""
    sources = {
        "class rows": [s.path for s in (*class_rows.BEERS, *class_rows.ORANGES, class_rows.HONEY)]
        + [s.path for s, _ in (*class_rows.NOT_BEER, *class_rows.NOT_ORANGES)],
        "planted": [d["category_path"] for s in build_preview4.samples().values() for d in s],
        "round 1 samples": [d["category_path"] for d in samples.FOOD],
    }
    for name, paths in sources.items():
        assert paths, name
        assert [p for p in paths if p[0] == "Food"] == [], name


def test_lemons_is_one_node_holding_the_planted_lemons_and_the_grocery_lemons(
    records: list[dict],
) -> None:
    lemons = [r for r in records if r["category_leaf"] == "Lemons"]
    assert {tuple(r["category_path"]) for r in lemons} == {LEMONS_NODE}
    kinds = Counter(r["product_id"].split("-")[0] for r in lemons)
    assert kinds["PLT"] == 1 and kinds["GRC"] >= 1
