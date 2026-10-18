"""Tapping Fluid for Spiral Flute Taps: a text-match decoy for the industrial seed queries (#462).

A cutting fluid for tapping with spiral flute taps. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "tapping_fluids",
    label="Tapping Fluid for Spiral Flute Taps",
    breadth=BreadthRow(
        key="tapping_fluids",
        category=("Lubricants, Coolants & Fluids", "Cutting Fluids", "Tapping Fluids"),
        family="cutting_tool",
        shape="tube",
        item="Tapping Fluid for Spiral Flute Taps",
        descriptor_attr=None,
        size_attr="Container Size",
        size_values=("4 oz", "16 oz"),
        attributes={"Material": ("Sulfurized Oil",)},
        price_range=(6.0, 24.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a cutting fluid for tapping with "
            "spiral flute taps"
        ),
    ),
)
