"""Foam Roller (gen#265, moved to a spec by gen#351 and gen#455): Yoga & Fitness: a roller's length is the SKU axis.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _FIT, _H, _L, BLACK, BLUE, GREEN, RED, WHITE, YELLOW, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="foam_roller",
    department="Sports & Outdoors",
    product_type="Foam Roller",
    rows=(
        _row("FMRSMT", "Smooth Foam Roller", _L, (*_FIT, "Foam Rollers"), "Foam Roller", 12.0,
             "foam_roller", "A firm foam roller with a smooth surface for stretching and easing tired "
             "muscles after a run.",
             (BLACK, BLUE, GREEN, RED),
             (_a("surface", "Surface", "Smooth"), _a("material", "Material", "EVA Foam")),
             _axis((33, 12.0), (45, 15.0), (60, 19.0)), "length_cm", (("texture", "smooth"),)),
        _row("FMRGRD", "Grid Foam Roller", _H, (*_FIT, "Foam Rollers"), "Foam Roller", 18.0,
             "foam_roller", "A foam roller with a grid of raised bumps for deeper massage along the "
             "back and legs.",
             (YELLOW, WHITE, BLUE, BLACK),
             (_a("surface", "Surface", "Grid"), _a("material", "Material", "EVA Foam")),
             _axis((33, 18.0), (45, 22.0)), "length_cm", (("texture", "grid"),)),
    ),
)  # fmt: skip
