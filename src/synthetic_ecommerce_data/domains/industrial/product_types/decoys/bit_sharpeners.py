"""Drill Bit Sharpener: a text-match decoy for the industrial seed queries (#462).

A sharpener for drill bits up to 3/8 in. Its title holds the seed noun and its category path does
not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "bit_sharpeners",
    label="Drill Bit Sharpener",
    breadth=BreadthRow(
        key="bit_sharpeners",
        category=("Holemaking", "Drill Accessories", "Bit Sharpeners"),
        family="cutting_tool",
        shape="block",
        item="Drill Bit Sharpener",
        descriptor_attr=None,
        size_attr="Capacity",
        size_values=("3/8 in", "1/2 in"),
        attributes={"Material": ("Diamond",)},
        price_range=(20.0, 90.0),
        skus=2,
        featured_sizes=("3/8 in",),
        reason=(
            "decoy for the industrial seed queries (#462): a sharpener for drill bits up to 3/8 in"
        ),
    ),
)
