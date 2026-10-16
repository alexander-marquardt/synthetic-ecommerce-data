"""The six ordinary types behind the toy-word decoys of gen#424.

They are kitchen roll, kitchen scales, greeting card, gift card, glue gun and caulking gun. A
decoy of :mod:`decoy_product_words` is a real product of its own type, and a type is registered
through a spec file (gen#351). Each type here has one spec with one ordinary product, titled
without the shopper's toy word, so the decoy rows are the ones that hold it.
"""

from __future__ import annotations

import kit_toy_word_decoys  # noqa: F401 -- registers the shapes
from type_registry import Row
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
