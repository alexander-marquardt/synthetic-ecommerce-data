"""Hex Key Holder: a text-match decoy for the industrial seed queries (#462).

A holder that keeps a set of hex keys in order. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "wrench_organizers",
    label="Hex Key Holder",
    breadth=BreadthRow(
        key="wrench_organizers",
        category=("Material Handling & Storage", "Tool Storage", "Wrench Organizers"),
        family="hand_tool",
        shape="block",
        item="Hex Key Holder",
        descriptor_attr=None,
        size_attr="Capacity",
        size_values=("8 Slots", "13 Slots"),
        attributes={"Material": ("Plastic",)},
        price_range=(4.0, 16.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a holder that keeps a set of hex keys in order",
    ),
)
