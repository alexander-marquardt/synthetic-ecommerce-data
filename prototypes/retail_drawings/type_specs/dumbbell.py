"""Dumbbell (gen#265, moved to a spec by gen#351 and gen#455): Yoga & Fitness: a weight in kilograms is the SKU axis.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _L, _W, _WEIGHTS, BLACK, BLUE, GREEN, RED, WHITE, YELLOW, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="dumbbell",
    department="Sports & Outdoors",
    product_type="Dumbbell",
    rows=(
        _row("DMBHEX", "Hex Rubber Dumbbell", _W, (*_WEIGHTS, "Dumbbells"), "Dumbbell", 14.0,
             "dumbbell", "A cast iron dumbbell in a rubber coat with hex heads that do not roll, "
             "sold singly in a range of weights.",
             (BLACK, BLUE),
             (_a("material", "Material", "Rubber Coated Iron"), _a("head_shape", "Head shape", "Hex"),
              _a("sold_as", "Sold as", "Single")),
             _axis((2, 14.0), (4, 24.0), (6, 34.0), (8, 44.0)), "weight_kg", (("style", "hex"),)),
        _row("DMBNEO", "Neoprene Dumbbell", _L, (*_WEIGHTS, "Dumbbells"), "Dumbbell", 6.0, "dumbbell",
             "A soft-coated dumbbell with a comfortable grip for home workouts, sold singly in a "
             "range of weights.",
             (RED, GREEN, YELLOW, WHITE),
             (_a("material", "Material", "Neoprene Coated Iron"), _a("head_shape", "Head shape", "Round"),
              _a("sold_as", "Sold as", "Single")),
             _axis((1, 6.0), (2, 9.0), (3, 12.0)), "weight_kg", (("style", "round"),)),
    ),
)  # fmt: skip
