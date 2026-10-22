"""Camping Chair (gen#265, moved to a spec by gen#351 and gen#455): Camping: a folding chair, with or without arms.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _CAMP, _H, _W, BLACK, BLUE, GREEN, RED, WHITE, YELLOW, _a, _kg, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="camping_chair",
    department="Sports & Outdoors",
    product_type="Camping Chair",
    rows=(
        _row("CHRFLD", "Folding Camping Chair", _W, (*_CAMP, "Camping Chairs"), "Camping Chair", 18.0,
             "camp_chair", "A light folding chair with a steel frame and a padded seat that packs into "
             "a carry bag.",
             (RED, BLUE, GREEN, YELLOW),
             (_a("frame_material", "Frame material", "Steel"), _kg("max_load_kg", "Maximum load", 100),
              _a("arms", "Arms", "No")),
             (), "size", (("arms", "no"),)),
        _row("CHRARM", "Folding Camping Armchair with Cup Holder", _H, (*_CAMP, "Camping Chairs"),
             "Camping Chair", 29.0, "camp_chair", "A folding armchair with a high back, padded arms and "
             "a cup holder, for long evenings round the fire.",
             (BLACK, WHITE, BLUE, GREEN),
             (_a("frame_material", "Frame material", "Steel"), _kg("max_load_kg", "Maximum load", 120),
              _a("arms", "Arms", "Yes")),
             (), "size", (("arms", "yes"),)),
    ),
)  # fmt: skip
