"""Screwdriver Rack: a text-match decoy for the industrial seed queries (#462).

A bench rack that stores screwdrivers. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "bench_tool_racks",
    label="Screwdriver Rack",
    breadth=BreadthRow(
        key="bench_tool_racks",
        category=("Material Handling & Storage", "Tool Storage", "Bench Tool Racks"),
        family="hand_tool",
        shape="bracket",
        item="Screwdriver Rack",
        descriptor_attr=None,
        size_attr="Capacity",
        size_values=("12 Slots", "24 Slots"),
        attributes={"Material": ("Steel",)},
        price_range=(9.0, 36.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a bench rack that stores screwdrivers",
    ),
)
