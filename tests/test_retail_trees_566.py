"""One Garden > Trees category holds the bay, olive, apple and Christmas trees (gen#566).

The maintainer searched for "tree" and found the trees spread over four places in Garden: bay and
olive trees under Plants, apple trees under Fruit Trees, Christmas trees under Christmas Trees.
These checks hold what the issue asked for: Garden has a Trees category, the four kinds sit
inside it as Bay Trees, Olive Trees, Apple Trees and Christmas Trees, nothing tree-shaped is left
under Plants or in the two single-child levels (Fruit Trees, Real Christmas Trees), and the olive
tree sold as a gift stays a gift plant.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402

#: Product-code prefix -> the kind of tree, which names its category under Garden > Trees.
KINDS = {
    "BAY": "Bay Trees",
    "OLV": "Olive Trees",
    "APL": "Apple Trees",
    "XMS": "Christmas Trees",
}
#: The olive tree sold as a gift (``distractors.py``): a gift item, not a tree for the garden.
GIFT_OLIVE_ID = "PLT-GTOLIV"


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def _garden_paths(templates: list[dict]) -> set[tuple[str, ...]]:
    return {tuple(d["category_path"]) for d in templates if d["category_path"][0] == "Garden"}


@pytest.mark.parametrize("prefix", sorted(KINDS))
def test_each_kind_of_tree_sits_in_garden_trees(prefix: str, templates: list[dict]) -> None:
    docs = [d for d in templates if d["product_id"].startswith(f"BRD-{prefix}")]
    assert docs, prefix
    wrong = {d["product_id"]: d["category_path"] for d in docs}
    assert all(p == ["Garden", "Trees", KINDS[prefix]] for p in wrong.values()), wrong


def test_garden_trees_holds_exactly_the_four_kinds(templates: list[dict]) -> None:
    kinds = {p[2] for p in _garden_paths(templates) if p[:2] == ("Garden", "Trees")}
    assert kinds == set(KINDS.values()), kinds


@pytest.mark.parametrize("old", ["Bay Trees", "Olive Trees"], ids=["bay", "olive"])
def test_plants_holds_no_bay_or_olive_tree_category(old: str, templates: list[dict]) -> None:
    under_plants = {p for p in _garden_paths(templates) if p[:2] == ("Garden", "Plants")}
    assert ("Garden", "Plants", old) not in under_plants, sorted(under_plants)


@pytest.mark.parametrize("old", ["Fruit Trees", "Christmas Trees"], ids=["fruit", "christmas"])
def test_the_single_child_levels_are_gone(old: str, templates: list[dict]) -> None:
    """Apple is the only fruit tree and every Christmas tree is real: no level for either."""
    second = {p[1] for p in _garden_paths(templates) if len(p) > 1}
    assert old not in second, sorted(second)
    assert ("Garden", "Trees", "Real Christmas Trees") not in _garden_paths(templates)


def test_the_gift_olive_tree_stays_a_gift_plant(templates: list[dict]) -> None:
    gift = [d for d in templates if d["product_id"] == GIFT_OLIVE_ID]
    assert gift, "the Olive Tree in Hessian Gift Bag distractor is missing"
    assert gift[0]["category_path"] == ["Garden", "Plants", "Gift Plants"]
