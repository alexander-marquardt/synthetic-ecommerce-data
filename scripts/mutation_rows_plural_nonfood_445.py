"""Mutation rows for the non-food plural decoys of gen#445, in their own file.

Each row plants one defect in a non-food class 9 decoy row and names the test of
``tests/test_grocery_plural_nonfood_decoys_445.py`` that must go red. ``mutation_row.discover`` finds this file by glob and the harness names them as rows named ``plural nonfood: ...`` (``--only "plural
nonfood:"`` re-runs them). A row is ``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501  (a row quotes the whole line it changes)
from __future__ import annotations

from mutation_row import Row

_R = "prototypes/retail_drawings"
_F = "decoy_plural_nonfood_rows.py"
_T = "tests/test_grocery_plural_nonfood_decoys_445.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a lemons hand wash names the singular",
        _F,
        '"Sicilian Lemons Hand Wash, 250ml"',
        '"Sicilian Lemon Hand Wash, 250ml"',
        f'{_T} -k "has_a_non_food_decoy and lemons"',
        "every non-food decoy title carries the exact plural token it targets",
        _R,
    ),
    (
        "a Lucky Lemons pyjamas row loses its brand",
        _F,
        '"Navy", "lemons", 960, "Lucky Lemons", None)',
        '"Navy", "lemons", 960, None, None)',
        f'{_T} -k "brand_or_a_scent and lemons"',
        "a non-food decoy carries the plural as its brand or as its scent",
        _R,
    ),
    (
        "a limes shower gel loses the lime from its fragrance",
        _F,
        '"limes", 960, None, "Persian Lime")',
        '"limes", 960, None, "Persian Citrus")',
        f'{_T} -k "brand_or_a_scent and limes"',
        "a scented decoy names the fruit in its fragrance attribute",
        _R,
    ),
    (
        "an oranges washing-up liquid claims fresh oranges",
        _F,
        '"A washing-up liquid scented with sweet oranges, in a 500ml bottle."',
        '"A washing-up liquid scented with fresh sweet oranges, in a 500ml bottle."',
        f'{_T} -k "brand_or_a_scent and oranges"',
        "no decoy title or description claims the product is fresh",
        _R,
    ),
    (
        "the oranges candle moves into the food department",
        _F,
        '("XR01", "fruit_candle",',
        '("XR01", "juice",',
        f'{_T} -k "has_a_non_food_decoy and oranges"',
        "oranges keeps two decoys from a non-food department",
        _R,
    ),
    (
        "the limes air freshener stops competing in the raw search",
        _F,
        '"Green", "limes", 940, None, "Lime & Sea Salt")',
        '"Green", "limes", 1, None, "Lime & Sea Salt")',
        f'{_T} -k "first_twelve and limes"',
        "a raw search for limes shows two non-food decoys in its first twelve",
        _R,
    ),
    (
        "a decoy becomes the exemplar another decoy is cloned from",
        "decoy_apparel.py",
        '            and d["product_id"] not in PLURAL_NONFOOD_IDS  # a decoy is never a clone\'s source\n',
        "",
        "tests/test_retail_apparel_decoys_311.py",
        "the clothing decoy table does not move when the non-food plural rows are added",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "plural nonfood"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
