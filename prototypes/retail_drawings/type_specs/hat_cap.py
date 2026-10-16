"""Hats and caps (gen#422, a spec by gen#351): stub for the red commit."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import register
from type_registry import Row, TypeSpec, a, cw


def _stub(paint, fill, label, **params):
    return []


register({"hat": _stub})

SPEC = TypeSpec(
    key="hat_cap",
    department="Clothing",
    product_type="Hat",
    owners=(("Wrenfield", "own"),),
    apparel_exempt="an accessory, not a garment",
    rows=(
        Row("HATSTB", "Hats and caps", "Wrenfield", "Clothing", ("Womens", "Accessories", "Hats & Caps"),
            "Hat", 12.0, "handbag", "A stub.",
            (cw("Black", "#2d2d33"),), (a("audience", "Audience", "Womens"),)),
    ),
)  # fmt: skip
