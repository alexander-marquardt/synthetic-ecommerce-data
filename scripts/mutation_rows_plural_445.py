"""Mutation rows for the grocery plural decoys of gen#445, in their own file.

Each row plants one defect in a class 9 decoy row and names the test of
``tests/test_grocery_plural_decoys_445.py`` that must go red. ``mutation_row.discover`` finds this file by glob and the harness names them as rows named ``plural decoys: ...`` (``--only "plural
decoys:"`` re-runs them). A row is ``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501  (a removal row quotes the whole decoy row it takes out)
from __future__ import annotations

from mutation_row import Row

_R = "prototypes/retail_drawings"
_F = "decoy_plural_rows.py"
_T = "tests/test_grocery_plural_decoys_445.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a lime decoy names the singular",
        _F,
        '"Sparkling Mineral Water with Limes"',
        '"Sparkling Mineral Water with Lime"',
        f'{_T} -k "three_decoys_from_two_categories and limes"',
        "every decoy title carries the exact plural token it targets",
        _R,
    ),
    (
        "a lime decoy no longer matches the raw search",
        _F,
        '"Lemons and Limes Boiled Sweets"',
        '"Fruit Boiled Sweets"',
        f'{_T} -k "first_twelve and limes"',
        "a raw search for limes shows three decoys in its first twelve",
        _R,
    ),
    (
        "limes keep two decoys",
        _F,
        '    ("XQ11", "marinade", "Marinade with Limes and Coriander", "A bottled marinade of limes, coriander and chilli for chicken and fish.", "Green", "limes", 880, ("lime juice (20%)", "coriander", "rapeseed oil", "chilli")),\n',
        "",
        f'{_T} -k "three_decoys_from_two_categories and limes"',
        "each plural has at least three decoys",
        _R,
    ),
    (
        "an apple decoy claims to be fresh",
        _F,
        '"Stewed Apples in Syrup"',
        '"Fresh Apples in Syrup"',
        f'{_T} -k "never_claims_to_be_fresh and apples"',
        "no decoy title claims the product is fresh",
        _R,
    ),
    (
        "a lemon decoy has no lemon in its ingredients",
        _F,
        '"Yellow", "lemons", 920, ("lemons", "salt", "water")',
        '"Yellow", "lemons", 920, ("brine", "salt", "water")',
        f'{_T} -k "never_claims_to_be_fresh and lemons"',
        "a decoy is made of the fruit its title names",
        _R,
    ),
    (
        "an orange decoy title runs to seven words",
        _F,
        '"Juice from Oranges, 1L"',
        '"Juice Pressed from Spanish Valencia Oranges, 1L"',
        f'{_T} -k "three_decoys_from_two_categories and oranges"',
        "a decoy title is six words or fewer",
        _R,
    ),
    (
        "the orange family loses its grade",
        "grocery_rows.py",
        'Family("ORA", _FRUIT + ("Citrus Fruit", "Oranges"), "{line} {flavor}, Class 1"',
        'Family("ORA", _FRUIT + ("Citrus Fruit", "Oranges"), "{line} {flavor}"',
        f'{_T} -k "first_twelve and oranges"',
        "the fresh titles are longer than the decoy titles in the exact-token match",
        _R,
    ),
    (
        "the tomato family loses its grade",
        "grocery_rows.py",
        'Family("TOM", _p("Fruit & Vegetables", "Fresh Vegetables", "Tomatoes"), "{line} {flavor}, Class 1"',
        'Family("TOM", _p("Fruit & Vegetables", "Fresh Vegetables", "Tomatoes"), "{line} {flavor}"',
        f'{_T} -k "first_twelve and tomatoes"',
        "the fresh titles are longer than the decoy titles in the exact-token match",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "plural decoys"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
