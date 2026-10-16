"""Yoga Strap (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _H, _NEUTRAL, _PRIMARY, _W, _YOGA, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="yoga_strap",
    department="Sports & Outdoors",
    product_type="Yoga Strap",
    rows=(
        _row("YGSRNG", "Cotton Yoga Strap with D-Rings", _W, (*_YOGA, "Yoga Straps"), "Yoga Strap", 6.0,
             "yoga_strap", "A woven cotton strap with two D-rings that hold a loop at any length, for binds and long holds.",
             _PRIMARY, (_a("material", "Material", "Cotton"), _a("closure", "Closure", "D-Ring")),
             _axis((183, 6.0), (244, 8.0)), "length_cm", (("buckle", "ring"),)),
        _row("YGSCLP", "Nylon Yoga Strap with Quick Clip", _H, (*_YOGA, "Yoga Straps"), "Yoga Strap", 9.0,
             "yoga_strap", "A soft nylon strap with a quick-release clip that closes in one move and holds under tension.",
             _NEUTRAL, (_a("material", "Material", "Nylon"), _a("closure", "Closure", "Clip")),
             _axis((183, 9.0), (244, 11.0)), "length_cm", (("buckle", "clip"),)),
    ),
)  # fmt: skip
