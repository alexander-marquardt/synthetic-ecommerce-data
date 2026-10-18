"""Luggage Set (gen#209): two and three piece sets of nested hard shell cases.

**Womens > Accessories > Travel > Luggage Sets**: three styles from three invented brands, drawn
by :func:`kit_luggage.luggage_set` (``pieces``, so a two piece set draws two cases and a three
piece set draws three). The piece count, the sizes included, the shell and the wheels are
structured entries, so ``3 piece luggage set`` reads the count. A SKU is a color; the piece count
is a style, because the drawing shows it. Authored rows only. The decoys are real sets whose
title or description holds a word that fools a search (red zips, a weekend case in the set, a
lock that is not TSA).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from luggage_common import (
    BLACK,
    BLUE,
    EXEMPT,
    FENMOOR,
    GREEN,
    MARROWGATE,
    NAVY,
    OWNED,
    RED,
    SKERRY,
    TARNWICK,
    WHITE,
    YELLOW,
    a,
    count,
    luggage_row,
)  # fmt: skip
from type_registry import Decoy, TypeSpec

PT, LEAF = "Luggage Set", "Luggage Sets"
SIZES = {2: "Cabin, Medium", 3: "Cabin, Medium, Large"}


def _row(code, title, brand, price, desc, colors, pieces, wheels="4", **kw):
    attrs = (count("piece_count", "Piece count", pieces), a("sizes_included", "Sizes included", SIZES[pieces]),
             a("shell", "Shell", "Hard"), a("wheels", "Wheels", "4 Wheel Spinner" if wheels == "4" else "2 Wheel"))  # fmt: skip
    return luggage_row(code, title, brand, price, desc, colors, PT, LEAF, "luggage_set", attrs, (),
                       (("pieces", str(pieces)),), **kw)  # fmt: skip


_ROWS = (
    _row("LGSTHR", "3 Piece Hard Shell Luggage Set", TARNWICK, 139.0,
         "Three nesting hard shell suitcases, cabin, medium and large, each on four spinner wheels "
         "with a TSA lock. Stores as one.", (BLACK, BLUE, RED), 3),
    _row("LGSTTW", "2 Piece Hard Shell Luggage Set", MARROWGATE, 94.0,
         "A cabin case and a medium suitcase that nest together, in tough ABS with four spinner "
         "wheels and a combination lock.", (GREEN, NAVY), 2),
    _row("LGSTSP", "3 Piece Spinner Luggage Set", SKERRY, 149.0,
         "A lightweight set of three spinner suitcases in polycarbonate, with a lined interior "
         "and a telescopic handle on each.", (WHITE, YELLOW, BLACK), 3),
)  # fmt: skip


def _decoy(cls, query, policy, code, title, desc, color, pieces, brand):
    return Decoy(cls, query, policy, _row(code, title, brand, 90.0, desc, (color,), pieces))


SPEC = TypeSpec(
    key="luggage_set",
    department="Clothing",
    product_type=PT,
    rows=_ROWS,
    owners=OWNED,
    apparel_exempt=EXEMPT,
    decoys=(
        _decoy(1, "red luggage set", "color", "LGSDRD", "3 Piece Luggage Set, Red Zips",
               "A black hard shell luggage set with red zip pulls and red handle grips on each case.",
               BLACK, 3, TARNWICK),
        _decoy(6, "weekend bag", "category", "LGSDWK", "Weekend Luggage Set, 2 Piece",
               "A cabin case and a medium suitcase that fit a weekend away between them; both are "
               "hard shell trolley cases, not weekend bags.", NAVY, 2, FENMOOR),
        _decoy(4, "tsa lock luggage set", "generic", "LGSDLK", "Combination Lock Luggage Set",
               "A set of three suitcases with a standard combination lock on each; the locks are "
               "not TSA approved.", GREEN, 3, MARROWGATE),
    ),
)  # fmt: skip
