"""Money boxes (gen#425, a spec by gen#351): Gifts > Kids' Gifts > Money Boxes.

Six styles from three brands, drawn by :func:`kit_gifts.money_box` (the form, a pig, a rocket or
a house, and its material change the drawing, which carries one coin slot). The material and the
shape are structured entries. The SKUs are the six main colors (gen#275). Not derivable:
authored rows only. Every name here is invented.
"""

from __future__ import annotations

import kit_gifts  # noqa: F401 -- registers money_box
from gifts_rows import DEPARTMENT, FERNBY, HEARTH, MONEY_BOX_PATH, PIPWICK, SIX_COLORS
from type_registry import Row, TypeSpec, a


def _box(code, title, brand, price, form, material, description) -> Row:
    return Row(
        code, title, brand, DEPARTMENT, MONEY_BOX_PATH, "Money Box", price, "money_box",
        description, SIX_COLORS,
        (a("material", "Material", material.title()), a("shape", "Shape", form.title())),
        audience="kids", params=(("form", form), ("material", material)),
    )  # fmt: skip


SPEC = TypeSpec(
    key="money_box",
    department=DEPARTMENT,
    product_type="Money Box",
    rows=(
        _box("GMBPIGC", "Ceramic Pig Money Box", FERNBY, 9.0, "pig", "ceramic",
             "A ceramic pig money box with a coin slot on its back and a rubber stopper underneath."),
        _box("GMBPIGT", "Tin Pig Money Box", HEARTH, 7.0, "pig", "tin",
             "A tin pig money box with a coin slot, which opens with a key."),
        _box("GMBROKT", "Tin Rocket Money Box", PIPWICK, 8.0, "rocket", "tin",
             "A tin rocket money box with a coin slot below its nose cone, for a young space fan."),
        _box("GMBROKW", "Wooden Rocket Money Box", FERNBY, 11.0, "rocket", "wood",
             "A wooden rocket money box with a coin slot and a stopper in its base."),
        _box("GMBHOUW", "Wooden House Money Box", HEARTH, 12.0, "house", "wood",
             "A wooden house money box with a roof slot and a small door that stays shut."),
        _box("GMBHOUC", "Ceramic House Money Box", PIPWICK, 10.0, "house", "ceramic",
             "A ceramic house money box with a coin slot in its roof and a stopper in its base."),
    ),
)  # fmt: skip
