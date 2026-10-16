"""Swim Goggles (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _H, _L, _NEUTRAL, _PRIMARY, _SWIM, _a, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="swim_goggles",
    department="Sports & Outdoors",
    product_type="Swim Goggles",
    rows=(
        _row("SGGCLR", "Anti-Fog Swimming Goggles", _L, (*_SWIM, "Swimming Goggles"), "Swim Goggles", 9.0,
             "swim_goggles", "Comfortable training goggles with clear lenses, an anti-fog coating and a soft silicone seal.",
             _PRIMARY, (_a("lens", "Lens", "Clear"), _a("anti_fog", "Anti-fog", "Yes"), _a("strap_material", "Strap material", "Silicone")),
             (), "size", (("lens", "clear"),)),
        _row("SGGMIR", "Mirrored Racing Swimming Goggles", _H, (*_SWIM, "Swimming Goggles"), "Swim Goggles", 16.0,
             "swim_goggles", "Low-profile racing goggles with mirrored lenses that cut glare in an outdoor pool.",
             _NEUTRAL, (_a("lens", "Lens", "Mirrored"), _a("anti_fog", "Anti-fog", "Yes"), _a("strap_material", "Strap material", "Silicone")),
             (), "size", (("lens", "mirrored"),)),
    ),
)  # fmt: skip
