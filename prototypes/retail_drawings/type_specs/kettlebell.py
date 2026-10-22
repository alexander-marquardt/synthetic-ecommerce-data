"""Kettlebell (gen#265, moved to a spec by gen#351 and gen#455): Yoga & Fitness: a weight in kilograms is the SKU axis.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _H, _W, _WEIGHTS, BLACK, BLUE, GREEN, RED, WHITE, YELLOW, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="kettlebell",
    department="Sports & Outdoors",
    product_type="Kettlebell",
    rows=(
        _row("KTBCST", "Cast Iron Kettlebell", _H, (*_WEIGHTS, "Kettlebells"), "Kettlebell", 24.0,
             "kettlebell", "A solid cast kettlebell with a wide handle for swings, squats and "
             "presses.",
             (BLACK, BLUE),
             (_a("material", "Material", "Cast Iron"),),
             _axis((8, 24.0), (12, 34.0), (16, 44.0), (20, 54.0)), "weight_kg"),
        _row("KTBVIN", "Vinyl Coated Kettlebell", _W, (*_WEIGHTS, "Kettlebells"), "Kettlebell", 15.0,
             "kettlebell", "A kettlebell in a smooth vinyl coat that protects the floor, in light "
             "weights for beginners.",
             (RED, GREEN, YELLOW, WHITE),
             (_a("material", "Material", "Vinyl Coated Iron"),),
             _axis((4, 15.0), (6, 20.0), (8, 25.0)), "weight_kg"),
    ),
)  # fmt: skip
