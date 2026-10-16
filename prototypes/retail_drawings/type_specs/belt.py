"""Belt (gen#422, a spec by gen#351): stub for the red commit."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import register
from type_registry import Row, TypeSpec, a, cw


def _stub(paint, fill, label, **params):
    return []


register({"belt_buckled": _stub})

SPEC = TypeSpec(
    key="belt",
    department="Clothing",
    product_type="Belt",
    owners=(("Wrenfield", "own"),),
    rows=(
        Row("BLTSTB", "Belt", "Wrenfield", "Clothing", ("Mens", "Accessories", "Belts"),
            "Belt", 12.0, "handbag", "A stub.",
            (cw("Black", "#2d2d33"),), (a("audience", "Audience", "Womens"),)),
    ),
)  # fmt: skip
