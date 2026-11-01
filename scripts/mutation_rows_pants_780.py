"""Mutation rows for the women's and men's pants and the plain swim bottoms (gen#780).

Each row plants one defect and names the test that must go red. ``mutation_row.discover`` finds
this file by glob and the harness names the rows ``pants 780: ...`` (``--only "pants 780:"``
re-runs them). A row is ``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501  (a row quotes the whole source line it changes)
from __future__ import annotations

from mutation_row import Row

_R = "src/synthetic_ecommerce_data/domains/retail"
_T = "tests/test_retail_pants_780.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a women's pants title says period again",
        "type_specs/pants.py",
        '_row("PPBKLT", "Cotton Bikini Pants",',
        '_row("PPBKLT", "Cotton Bikini Period Pants",',
        f"{_T} -k no_clothing_product_says_period",
        "no clothing product says period",
        _R,
    ),
    (
        "the men's pants are drawn as boxers",
        "type_specs/mens_pants.py",
        'price, "mens_pants", f"{desc} Machine washable."',
        'price, "boxers", f"{desc} Machine washable."',
        f"{_T} -k mens_pants_have_a_drawing_no_other_type_uses",
        "the men's pants have a drawing of their own",
        _R,
    ),
    (
        "the men's pants leave their leaf for Boxers",
        "type_specs/mens_pants.py",
        'PATH = ("Mens", "Underwear", "Pants")',
        'PATH = ("Mens", "Underwear", "Boxers")',
        f"{_T} -k mens_pants_are_a_leaf_of_their_own",
        "the men's pants are a leaf of their own",
        _R,
    ),
    (
        "the swim bottoms leave the Bikini Bottoms leaf",
        "swimwear_rows.py",
        'code, title, brand, BIKINI_BOTTOMS, "Swim Bottoms", "swim_bottoms"',
        'code, title, brand, TANKINI, "Swim Bottoms", "swim_bottoms"',
        f"{_T} -k swim_bottoms_are_plain_bikini_bottoms",
        "the swim bottoms are sold in the Bikini Bottoms leaf",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "pants 780"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
