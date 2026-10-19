"""Carbide Drill Bit Index Case: a text-match decoy for the industrial seed queries (#462).

An empty index case for a carbide drill bit set. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "bit_index_cases",
    label="Carbide Drill Bit Index Case",
    breadth=BreadthRow(
        key="bit_index_cases",
        category=("Material Handling & Storage", "Tool Storage", "Bit Index Cases"),
        family="cutting_tool",
        shape="block",
        item="Carbide Drill Bit Index Case",
        descriptor_attr=None,
        size_attr="Capacity",
        size_values=("13 Slots", "29 Slots"),
        attributes={"Material": ("Plastic",)},
        price_range=(6.0, 24.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): an empty index case for a carbide "
            "drill bit set"
        ),
    ),
)
