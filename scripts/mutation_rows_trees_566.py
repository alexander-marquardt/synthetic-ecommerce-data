"""Mutation rows for the Garden > Trees category (gen#566), kept out of ``mutation_check.py``.

Each row puts one kind of tree back where it was before gen#566, or moves the gift olive tree
into the trees, and names the test that must go red. ``mutation_check.py`` turns them into
``Mutation`` rows named ``garden trees: ...`` (``--only "garden trees:"`` re-runs them).
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_trees_566.py"
_KIND = f"{_T} -k test_each_kind_of_tree_sits_in_garden_trees"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "the bay trees are back under Plants",
        "breadth_rows.py",
        '_TREES = ("Garden", "Trees", "Bay Trees")',
        '_TREES = ("Garden", "Plants", "Bay Trees")',
        _KIND,
        "a bay tree sits in Garden > Trees > Bay Trees",
    ),
    (
        "the olive tree is back under Plants",
        "breadth_rows.py",
        '_OLIVES = ("Garden", "Trees", "Olive Trees")',
        '_OLIVES = ("Garden", "Plants", "Olive Trees")',
        _KIND,
        "an olive tree sits in Garden > Trees > Olive Trees",
    ),
    (
        "the apple trees are back under Fruit Trees",
        "breadth_rows.py",
        '_APPLE = ("Garden", "Trees", "Apple Trees")',
        '_APPLE = ("Garden", "Fruit Trees", "Apple Trees")',
        _KIND,
        "an apple tree sits in Garden > Trees > Apple Trees",
    ),
    (
        "the Christmas trees are back under Real Christmas Trees",
        "breadth_rows.py",
        '_XMAS = ("Garden", "Trees", "Christmas Trees")',
        '_XMAS = ("Garden", "Christmas Trees", "Real Christmas Trees")',
        _KIND,
        "a Christmas tree sits in Garden > Trees > Christmas Trees",
    ),
    (
        "the Christmas trees get a Real Christmas Trees level under Trees",
        "breadth_rows.py",
        '_XMAS = ("Garden", "Trees", "Christmas Trees")',
        '_XMAS = ("Garden", "Trees", "Real Christmas Trees")',
        f"{_T} -k test_garden_trees_holds_exactly_the_four_kinds",
        "Garden > Trees holds Bay, Olive, Apple and Christmas Trees and no other child",
    ),
    (
        "the gift olive tree moves into the trees",
        "distractors.py",
        '("Garden", "Plants", "Gift Plants"), 30.0,\n        "A young olive tree',
        '("Garden", "Trees", "Olive Trees"), 30.0,\n        "A young olive tree',
        f"{_T} -k test_the_gift_olive_tree_stays_a_gift_plant",
        "the Olive Tree in Hessian Gift Bag stays in Garden > Plants > Gift Plants",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "garden trees"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
