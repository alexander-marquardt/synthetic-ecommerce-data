"""Mutation rows for the thin leaves brought to fifteen products (gen#434, gap 3).

Each row plants one defect in a thin leaf's type spec (``type_specs/chips.py``, ``bed.py``,
``bomber_jacket.py``, #645) and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``thin leaves: ...``
(``--only "thin leaves:"`` re-runs them). A row is ``(name, file, old, new, test, prop, root)``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_thin_leaves_434.py"
_ROOT = "src/synthetic_ecommerce_data/domains/retail"
_CHIPS = "type_specs/chips.py"
_BED = "type_specs/bed.py"
_BOMBER = "type_specs/bomber_jacket.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the chips go to another leaf",
        _CHIPS,
        '_PATH = ("Food & Drink", "Frozen Food", "Chips & Potatoes")',
        '_PATH = ("Food & Drink", "Frozen Food", "Frozen Chips")',
        f"{_T} -k 'at_least_fifteen_products and chips'",
        "the Chips & Potatoes leaf holds fifteen products",
        _ROOT,
    ),
    (
        "the beds go to another leaf",
        _BED,
        '_PATH = ("Home", "Furniture", "Beds")',
        '_PATH = ("Home", "Furniture", "Bed Frames")',
        f"{_T} -k 'at_least_fifteen_products and beds'",
        "the Beds leaf holds fifteen products",
        _ROOT,
    ),
    (
        "the bombers go to another leaf",
        _BOMBER,
        '_PATH = ("Womens", "Coats & Jackets", "Bomber Jackets")',
        '_PATH = ("Womens", "Coats & Jackets", "Check Jackets")',
        f"{_T} -k 'at_least_fifteen_products and bombers'",
        "the Bomber Jackets leaf holds fifteen products",
        _ROOT,
    ),
    (
        "a check bomber is stated plain",
        _BOMBER,
        'facts=(("pattern", "check"), ("size_range", ["regular"])),',
        'facts=(("pattern", "plain"), ("size_range", ["regular"])),',
        f"{_T} -k 'womens_check_bomber_jackets'",
        "fifteen Womens bombers state pattern = check",
        _ROOT,
    ),
    (
        "a check bomber has a plain swatch",
        _BOMBER,
        '(cw(f"{check} Check", base, "gingham", accent),),',
        '(cw(f"{check} Check", base),),',
        f"{_T} -k 'check_in_its_swatch'",
        "a bomber stated as a check carries a check colorway",
        _ROOT,
    ),
    (
        "a bed is made in its smallest size only",
        _BED,
        "for n, (s, _) in enumerate(self.sizes)",
        "for n, (s, _) in enumerate(self.sizes[:1])",
        f"{_T} -k 'made_in_each_named_size'",
        "at least six beds are made in each named size",
        _ROOT,
    ),
    (
        "a bed states the wrong mattress width",
        _BED,
        '"width_cm": BED_SIZE_DIMS[s][0]',
        '"width_cm": BED_SIZE_DIMS[s][1]',
        f"{_T} -k 'states_its_size_and_dimensions'",
        "every bed SKU carries the width and length of its size",
        _ROOT,
    ),
    (
        "a chips spec is derived into the seeded build",
        _CHIPS,
        '    key="chips",\n',
        '    key="chips",\n    derivable=True,\n',
        f"{_T} -k 'templates_only'",
        "the spec rows are templates only",
        _ROOT,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "thin leaves"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
