"""Mutation rows for the one `scent` key and the collision-word depth of gen#273, in their own file.

Each row plants one defect in the code of gen#273 and names the test that must go red.
``mutation_row.discover`` finds this file by glob; ``--only "scent collision:"`` re-runs its rows.
A row is ``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501  (a row quotes the whole line it changes)
from __future__ import annotations

from mutation_row import Row

_R = "prototypes/retail_drawings"
_ONE = "tests/test_scent_one_key_273.py"
_DEPTH = "tests/test_collision_word_depth_273.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the lavender talc states its scent as fragrance again",
        "type_specs/talc.py",
        '(a("scent", "Scent", "Lavender"),)',
        '(a("fragrance", "Fragrance", "Lavender"),)',
        f"{_ONE}::test_no_style_or_sku_keys_a_scent_as_fragrance",
        "no style or SKU keys a scent as fragrance",
        _R,
    ),
    (
        "the rose talc names its scent attribute Fragrance",
        "type_specs/talc.py",
        '(a("scent", "Scent", "Rose"),)',
        '(a("scent", "Fragrance", "Rose"),)',
        f"{_ONE}::test_every_scent_attribute_is_named_scent",
        "every scent attribute carries the display name Scent",
        _R,
    ),
    (
        "the limes family falls back to its old weight",
        "grocery_rows.py",
        '_FRESH, 0.010, item_g=70, axis="variety", depth=True),',
        '_FRESH, 0.003, item_g=70, axis="variety", depth=True),',
        f'{_DEPTH} -k "food and lime"',
        "the food sense of lime holds the target styles",
        _R,
    ),
    (
        "both scent palettes lose mint, lime, vanilla and cherry blossom",
        "grocery_rows.py",
        '    F("Fresh Linen", "#cfe3ee"), F("Mint", "#3a8f6a"), F("Lime", "#9acd32"), F("Vanilla", "#f3e5ab"),\n    F("Cherry Blossom", "#f4b6c8"),\n)\n_HOME_BRANDS = ("Clearbrook Household", "Soapwell", "Pantry Mill", "Freshfold")\n_BODY_SCENTS = (\n    F("Honey", "#e0a030"), F("Lemon", "#f2d14b"), F("Coconut", "#efe8d8"), F("Almond", "#c9a96e"),\n    F("Lavender", "#9a7ab6"), F("Mint", "#3a8f6a"), F("Lime", "#9acd32"), F("Vanilla", "#f3e5ab"),\n    F("Cherry Blossom", "#f4b6c8"),\n)',
        '    F("Fresh Linen", "#cfe3ee"),\n)\n_HOME_BRANDS = ("Clearbrook Household", "Soapwell", "Pantry Mill", "Freshfold")\n_BODY_SCENTS = (\n    F("Honey", "#e0a030"), F("Lemon", "#f2d14b"), F("Coconut", "#efe8d8"), F("Almond", "#c9a96e"),\n    F("Lavender", "#9a7ab6"),\n)',
        f'{_DEPTH} -k "scent"',
        "the scent sense of a collision word holds the target styles",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "scent collision"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
