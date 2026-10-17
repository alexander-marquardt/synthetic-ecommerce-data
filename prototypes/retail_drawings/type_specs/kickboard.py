"""Kickboard (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _H, _NEUTRAL, _PRIMARY, _SWIM, _W, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="kickboard",
    department="Sports & Outdoors",
    product_type="Kickboard",
    rows=(
        _row("KBDPLN", "Foam Kickboard", _H, (*_SWIM, "Kickboards"), "Kickboard", 8.0, "kickboard",
             "A buoyant EVA foam float for kick sets, with a smooth finish and rounded edges.",
             _PRIMARY, (_a("material", "Material", "EVA Foam"), _a("grips", "Grips", "None")),
             _axis((38, 8.0), (42, 10.0)), "length_cm", (("grips", "none"),)),
        _row("KBDCUT", "Kickboard with Hand Cut-Outs", _W, (*_SWIM, "Kickboards"), "Kickboard", 11.0, "kickboard",
             "A kickboard with two cut-out hand holds for a secure grip through long sets.",
             _NEUTRAL, (_a("material", "Material", "EVA Foam"), _a("grips", "Grips", "Cut-Out Grips")),
             _axis((40, 11.0), (45, 13.0)), "length_cm", (("grips", "cutouts"),)),
    ),
)  # fmt: skip
