"""Screwdriver Bit Set: a text-match decoy for the industrial seed queries (#462).

A bit set for a screwdriver handle or drill driver. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "driver_bit_sets",
    label="Screwdriver Bit Set",
    breadth=BreadthRow(
        key="driver_bit_sets",
        category=("Hand Tools", "Bits & Bit Holders", "Driver Bit Sets"),
        family="hand_tool",
        shape="cylinder",
        item="Screwdriver Bit Set",
        descriptor_attr=None,
        size_attr="Number of Pieces",
        size_values=("32", "100"),
        attributes={"Material": ("S2 Tool Steel",)},
        price_range=(8.0, 40.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a bit set for a screwdriver handle or "
            "drill driver"
        ),
    ),
)
