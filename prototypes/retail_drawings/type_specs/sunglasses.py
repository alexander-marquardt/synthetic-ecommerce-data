"""Sunglasses (gen#422, a spec by gen#351): stub for the red commit."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from type_registry import Row, TypeSpec, a, cw

SPEC = TypeSpec(
    key="sunglasses",
    department="Clothing",
    product_type="Sunglasses",
    owners=(("Wrenfield", "own"),),
    apparel_exempt="an accessory, not a garment",
    rows=(
        Row("SGLSTB", "Sunglasses", "Wrenfield", "Clothing", ("Womens", "Accessories", "Sunglasses"),
            "Sunglasses", 12.0, "handbag", "A pair of sunglasses.",
            (cw("Black", "#2d2d33"),), (a("audience", "Audience", "Womens"),)),
    ),
)  # fmt: skip
