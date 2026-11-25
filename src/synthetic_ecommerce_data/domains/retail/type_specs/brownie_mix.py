"""Brownie Mix (gen#1119, slice 3): Food & Drink > Food Cupboard > Baking > Baking Mixes.

The half of ``How to Make Brownies`` a shopper eats. A title names the flavor, each SKU is a
carton's net weight, and the carton shows what tops the brownies
(:func:`kit_baking.brownie_mix`). Templates only: the set is sized to the collision, so the scaled
build draws no more of it.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail.baking_rows import MIXES, row
from synthetic_ecommerce_data.domains.retail.pantry_rows import (
    CROFTER,
    DEPARTMENT,
    FOREST,
    GOLDFIELD,
    HEARTH,
    NAVY,
    OWNERS,
    PANTRY_MILL,
    PLUM,
    RUST,
    SAND,
    SKY,
    TEAL,
    WHEATSHEAF,
    grams,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec, a

_EVERYDAY = grams((0.35, 2.2), (0.5, 2.9), (1.0, 5.2))
_SPECIALTY = grams((0.35, 3.2), (0.5, 4.2), (1.0, 7.5))


def _row(code: str, flavor: str, brand: str, desc: str, sizes: tuple[tuple[str, float], ...],
         color: tuple, topping: str) -> object:  # fmt: skip
    name = f"{flavor} Brownie Mix"
    return row(code, name, brand, MIXES, "Brownie Mix", "brownie_mix", desc,
               (a("flavor", "Flavor", flavor),), sizes, "net_weight_g", color,
               (("topping", topping), ("tray", "no")), name)  # fmt: skip


#: The kit: a mix with a tray in the box, whose title holds the plural the book title holds.
_KIT = replace(
    _row("BRMKIT", "Double Chocolate", PANTRY_MILL,
         "A dry mix and a foil baking tray in one box, so there is no tin to wash up.", _EVERYDAY, RUST, "none"),
    title="Bake Your Own Double Chocolate Brownies Kit with Foil Tray",
    label="Double Chocolate Brownies Kit",
    params=(("topping", "none"), ("tray", "yes")),
)  # fmt: skip


ROWS = (
    _row("BRMFUD", "Chocolate Fudge", PANTRY_MILL,
         "A dry mix for a dense, dark tray bake. Add eggs, oil and water.", _EVERYDAY, NAVY, "none"),
    _row("BRMTRI", "Triple Chocolate", CROFTER,
         "A dry mix with milk, dark and white chocolate pieces. Add eggs and melted butter.", _EVERYDAY, PLUM, "white"),
    _row("BRMCAR", "Salted Caramel", HEARTH,
         "A dry mix with a sachet of salted caramel sauce to swirl through before baking.", _SPECIALTY, RUST, "caramel"),
    _row("BRMWAL", "Walnut", GOLDFIELD,
         "A dry mix with chopped walnuts. Add eggs and melted butter.", _EVERYDAY, FOREST, "nuts"),
    _row("BRMRAS", "Raspberry", WHEATSHEAF,
         "A dry mix with freeze-dried raspberry pieces. Add eggs and oil.", _SPECIALTY, SKY, "berries"),
    _row("BRMTOF", "Toffee", WHEATSHEAF,
         "A dry mix with crunchy toffee pieces. Add eggs, oil and water.", _SPECIALTY, TEAL, "toffee"),
    _row("BRMPEC", "Pecan", GOLDFIELD,
         "A dry mix with chopped pecans. Add eggs and melted butter.", _SPECIALTY, SAND, "nuts"),
    _row("BRMPNB", "Peanut Butter", GOLDFIELD,
         "A dry mix with a sachet of peanut butter to swirl through before baking.", _SPECIALTY, SAND, "marble"),
    _row("BRMVAN", "Vanilla", CROFTER,
         "A dry mix for a chewy chocolate tray bake, finished with a sachet of vanilla sugar.", _EVERYDAY, NAVY, "sugar"),
    _row("BRMHAZ", "Hazelnut", HEARTH,
         "A dry mix with roasted hazelnut pieces. Add eggs and melted butter.", _SPECIALTY, PLUM, "hazelnuts"),
    _KIT,
)  # fmt: skip

SPEC = TypeSpec(
    key="brownie_mix",
    department=DEPARTMENT,
    product_type="Brownie Mix",
    owners=OWNERS,
    rows=ROWS,
)
