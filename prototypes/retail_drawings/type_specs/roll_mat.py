"""Roll Mat (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _CAMP, _L, _NEUTRAL, _PRIMARY, _W, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="roll_mat",
    department="Sports & Outdoors",
    product_type="Roll Mat",
    rows=(
        _row("RMTRLL", "Closed Cell Foam Roll Mat", _L, (*_CAMP, "Roll Mats"), "Roll Mat", 12.0, "roll_mat",
             "A light rolled foam mat that insulates from cold ground and straps to the outside of a rucksack.",
             _PRIMARY, (_a("material", "Material", "Closed Cell Foam"), _a("fold", "Fold", "Roll")),
             _axis((8, 12.0), (10, 15.0), (15, 20.0)), "thickness_mm", (("form", "rolled"),)),
        _row("RMTZFD", "Z-Fold Camping Mat", _W, (*_CAMP, "Roll Mats"), "Roll Mat", 16.0, "roll_mat",
             "A concertina mat that folds into a flat stack, with a ridged top that traps warmth.",
             _NEUTRAL, (_a("material", "Material", "EVA Foam"), _a("fold", "Fold", "Z-Fold")),
             _axis((14, 16.0), (20, 21.0)), "thickness_mm", (("form", "folded"),)),
    ),
)  # fmt: skip
