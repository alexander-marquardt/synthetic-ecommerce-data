"""Shared pieces of the bag types (gen#1114): colors, brands, the row and decoy builders.

Each type is a leaf of its own under **Womens > Accessories > Bags** or **Mens > Accessories >
Bags** and its own drawing in :mod:`kit_bags` or :mod:`kit_bags_carry`. The form (``bag_shape``) and the surface (``material``) are drawing params of the
same key with the lower-cased value. The five Handbag styles of gen#207 whose ``bag_style`` is
Crossbody, Shoulder or Clutch stay Handbags, as the purses keep their card holders (gen#422).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_bags,  # noqa: F401 -- registers the shapes
    kit_bags_carry,  # noqa: F401 -- registers the shapes
)
from synthetic_ecommerce_data.domains.retail.accessory_rows import (
    BLACK,
    BLUE,
    BURGUNDY,
    CREAM,
    GREEN,
    GREY,
    KHAKI,
    NAVY,
    PINK,
    RED,
    TAN,
    ARow,
    _a,
    _sizes,
    _who,
)
from synthetic_ecommerce_data.domains.retail.audience import MENS, WOMENS
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy
from synthetic_ecommerce_data.domains.retail.variants import cw

PATHS = {WOMENS: ("Womens", "Accessories", "Bags"), MENS: ("Mens", "Accessories", "Bags")}
DEPARTMENT = "Clothing"
CALDERBY, THISTLE, HARBOUR, WRENFIELD = "Calderby & Lune", "Thistle & Wren", "Harbour & Pine", "Wrenfield"
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
YELLOW = cw("Yellow", "#f2c230")
APPAREL_EXEMPT = "an accessory, not a garment: its text words are those of its own decoys"

#: The colorways of a style: the six main colors are carried across each type.
BRIGHT = (RED, BLUE, GREEN, YELLOW)
CLASSIC = (BLACK, TAN, BURGUNDY, NAVY)
SOFT = (BLACK, WHITE, PINK, GREY)
EARTH = (KHAKI, TAN, NAVY, CREAM)


def small_medium(small: float, medium: float) -> tuple[tuple[str, float], ...]:
    return _sizes(("Small", small), ("Medium", medium))


def bag_row(code, title, brand, price, desc, colors, ptype, shape, form, material, closure, strap=None, sizes=(), who=WOMENS, size_key="size") -> ARow:  # fmt: skip
    """One bag style: its colors times its sizes; a clutch and a belt bag have one size."""
    attrs = (_a("bag_shape", "Bag shape", form), _a("material", "Material", material),
             _a("closure", "Closure", closure), *((_a("strap", "Strap", strap),) if strap else ()))  # fmt: skip
    return ARow(code, title, brand, DEPARTMENT, (*PATHS[who], f"{ptype}s"), ptype, price, shape, desc, colors,
                _who(attrs, who), sizes, params=(("bag_shape", form.lower()), ("material", material.lower())),
                size_key=size_key)  # fmt: skip


def decoy(cls: int, query: str, policy: str, row: ARow) -> Decoy:
    return Decoy(cls, query, policy, row)
