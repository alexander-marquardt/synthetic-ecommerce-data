"""Mutation rows for the thin leaves brought to fifteen products (gen#434, gap 3).

Each row plants one defect in ``thin_leaf_rows.py`` and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``thin leaves: ...``
(``--only "thin leaves:"`` re-runs them). A row is ``(name, file, old, new, test, prop, root)``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_thin_leaves_434.py"
_ROOT = "prototypes/retail_drawings"
_F = "thin_leaf_rows.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the chips go to another leaf",
        _F,
        '_FROZEN_NODE = ("Food & Drink", "Frozen Food", "Chips & Potatoes")',
        '_FROZEN_NODE = ("Food & Drink", "Frozen Food", "Frozen Chips")',
        f"{_T} -k 'at_least_fifteen_products and chips'",
        "the Chips & Potatoes leaf holds fifteen products",
        _ROOT,
    ),
    (
        "the beds go to another leaf",
        _F,
        '_BED_NODE = ("Home", "Furniture", "Beds")',
        '_BED_NODE = ("Home", "Furniture", "Bed Frames")',
        f"{_T} -k 'at_least_fifteen_products and beds'",
        "the Beds leaf holds fifteen products",
        _ROOT,
    ),
    (
        "the bombers go to another leaf",
        _F,
        '_BOMBER_NODE = ("Womens", "Coats & Jackets", "Bomber Jackets")',
        '_BOMBER_NODE = ("Womens", "Coats & Jackets", "Check Jackets")',
        f"{_T} -k 'at_least_fifteen_products and bombers'",
        "the Bomber Jackets leaf holds fifteen products",
        _ROOT,
    ),
    (
        "a check bomber is stated plain",
        _F,
        'facts=(("pattern", "check"), ("size_range", ["regular"])),',
        'facts=(("pattern", "plain"), ("size_range", ["regular"])),',
        f"{_T} -k 'womens_check_bomber_jackets'",
        "fifteen Womens bombers state pattern = check",
        _ROOT,
    ),
    (
        "a check bomber has a plain swatch",
        _F,
        'colors = (cw(f"{check} Check", base, "gingham", accent),)',
        'colors = (cw(f"{check} Check", base),)',
        f"{_T} -k 'check_in_its_swatch'",
        "a bomber stated as a check carries a check colorway",
        _ROOT,
    ),
    (
        "a bed is made in its smallest size only",
        _F,
        "bed_frame=sizes,",
        "bed_frame=sizes[:1],",
        f"{_T} -k 'made_in_each_named_size'",
        "at least six beds are made in each named size",
        _ROOT,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "thin leaves"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
