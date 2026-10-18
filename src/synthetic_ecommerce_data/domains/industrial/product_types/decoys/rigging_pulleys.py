"""Shackle-Mount Pulley Block: a text-match decoy for the industrial seed queries (#462).

A pulley block that hangs from a shackle. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "rigging_pulleys",
    label="Shackle-Mount Pulley Block",
    breadth=BreadthRow(
        key="rigging_pulleys",
        category=("Material Handling & Storage", "Rigging Hardware", "Rigging Pulleys"),
        family="motion",
        shape="disc",
        item="Shackle-Mount Pulley Block",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("2 in", "3 in", "4 in"),
        attributes={"Material": ("Steel",), "Finish": ("Zinc Plated",)},
        price_range=(12.0, 60.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a pulley block that hangs from a shackle",
    ),
)
