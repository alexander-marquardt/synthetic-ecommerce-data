"""Mugs (gen#425, a spec by gen#351): Gifts > Mugs & Drinkware.

The Gifts department held photo frames, keyrings, candles, wrapping paper and bags, and a search
for a mug found none. Four styles from four brands, drawn by :func:`kit_gifts.gift_mug`: a
slogan mug, a personalised initial mug, a pattern mug and a plain enamel one. The material, the
capacity (in millilitres, a measured entry) and whether it is dishwasher safe are structured
entries; the SKUs are the six main colors (gen#275). Not derivable: authored rows only. Every
name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

import kit_gifts  # noqa: F401 -- registers gift_mug
from gifts_rows import CALDERBY, DEPARTMENT, HEARTH, LANTERNBY, MUG_PATH, SIX_COLORS, THISTLE
from type_registry import Row, TypeSpec, a


def _ml(n: int) -> tuple[str, str, str, str, float]:
    """A capacity in millilitres: the same entry the tableware rows use."""
    return ("capacity", "Capacity", str(n), "MLT", float(n))


def _mug(code, title, brand, price, design, material, ml, dishwasher, description) -> Row:
    return Row(
        code, title, brand, DEPARTMENT, MUG_PATH, "Mug", price, "gift_mug", description,
        SIX_COLORS,
        (a("material", "Material", material.title()), _ml(ml), a("design", "Design", design.title()),
         a("dishwasher_safe", "Dishwasher safe", dishwasher)),
        params=(("design", design), ("material", material)),
    )  # fmt: skip


SPEC = TypeSpec(
    key="gift_mug",
    department=DEPARTMENT,
    product_type="Mug",
    rows=(
        _mug("GMGSLOG", "Slogan Ceramic Mug", LANTERNBY, 8.0, "slogan", "ceramic", 350, "Yes",
             "A 350 ml ceramic mug printed with a cheerful slogan, a gift for a colleague or a friend."),
        _mug("GMGINIT", "Personalised Initial Mug", HEARTH, 12.0, "initial", "stoneware", 400, "Yes",
             "A 400 ml stoneware mug with a large initial on the side, to give as a personalised gift."),
        _mug("GMGPATT", "Spotted Pattern Mug", THISTLE, 9.0, "pattern", "ceramic", 300, "Yes",
             "A 300 ml ceramic mug covered in small spots, with a comfortable handle."),
        _mug("GMGENAM", "Classic Enamel Mug", CALDERBY, 10.0, "plain", "enamel", 350, "No",
             "A 350 ml enamel mug with a rolled rim and a plain finish; wash it by hand."),
    ),
)  # fmt: skip
