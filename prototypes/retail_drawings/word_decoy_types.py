"""The six ordinary types behind the toy-word decoys of gen#424.

They are kitchen roll, kitchen scales, greeting card, gift card, glue gun and caulking gun: each
is a real product type of another department whose name holds a toy word ("kitchen", "card",
"gun"). A type is registered through a spec file (gen#351), so each has one spec with one ordinary
product, titled without the toy word, and the class-8 decoys of gen#326 that hold it as the
spec's ``decoys=`` (:func:`word_decoy`).
"""

from __future__ import annotations

import kit_toy_word_decoys  # noqa: F401 -- registers the shapes
from decoy_rows import COLORS
from type_registry import Decoy, Row
from variants import cw

WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
HOME, GIFTS = "Brackenmere Home", "Lanternby"


def plain(
    code: str,
    title: str,
    brand: str,
    dept: str,
    path: tuple[str, ...],
    ptype: str,
    shape: str,
    desc: str,
    price: float,
    attrs: tuple[tuple[str, str, str], ...],
) -> Row:
    """The one ordinary product of a type, drawn by its own shape and sold without a color."""
    return Row(
        code, title, brand, dept, path, ptype, price, shape, desc, (WHITE,), attrs, colorless=True
    )


def word_decoy(
    n: int,
    title: str,
    desc: str,
    color: str,
    brand: str,
    dept: str,
    path: tuple[str, ...],
    ptype: str,
    shape: str,
    price: float,
    noun: str,
) -> Decoy:
    """A class-8 decoy (gen#326): a product of its own type whose title holds the toy word ``noun``.

    It sits in a leaf of a department other than Toys, so the department policy drops it. Coded
    ``DT<n>``; its drawing takes its own color, as the type is sold without one.
    """
    row = Row(
        f"DT{n:02d}", title, brand, dept, path, ptype, price, shape, desc,
        (cw(color, COLORS[color]),), (), colorless=True,
    )  # fmt: skip
    return Decoy(8, noun, "department", row)
