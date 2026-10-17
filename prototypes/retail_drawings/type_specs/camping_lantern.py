"""Camping Lantern (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _CAMP, _H, _NEUTRAL, _PRIMARY, _W, _a, _row, _words
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="camping_lantern",
    department="Sports & Outdoors",
    product_type="Camping Lantern",
    rows=(
        _row("LNTLED", "Rechargeable LED Camping Lantern", _H, (*_CAMP, "Lanterns"), "Camping Lantern", 18.0,
             "lantern", "A bright LED lantern with a hanging hook, charged over USB and dimmable for the tent or the table.",
             _NEUTRAL, (_a("power", "Power", "Rechargeable"), _a("material", "Material", "ABS Plastic")),
             _words(("200", 18.0), ("400", 24.0), ("800", 34.0)), "brightness_lm", (("style", "led"),)),
        _row("LNTCLP", "Collapsible Battery Camping Lantern", _W, (*_CAMP, "Lanterns"), "Camping Lantern", 11.0,
             "lantern", "A pleated lantern that pushes flat for the pack and pulls up to light a whole picnic table.",
             _PRIMARY, (_a("power", "Power", "Battery"), _a("material", "Material", "Silicone")),
             _words(("150", 11.0), ("300", 15.0)), "brightness_lm", (("style", "collapsible"),)),
    ),
)  # fmt: skip
