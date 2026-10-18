"""Shackle Pin, Screw Pin Replacement: a text-match decoy for the industrial seed queries (#462).

A replacement screw pin for a shackle. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "replacement_pins",
    label="Shackle Pin, Screw Pin Replacement",
    breadth=BreadthRow(
        key="replacement_pins",
        category=("Material Handling & Storage", "Rigging Hardware", "Replacement Pins"),
        family="motion",
        shape="cylinder",
        item="Shackle Pin, Screw Pin Replacement",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("1/2 in", "5/8 in", "3/4 in"),
        attributes={"Material": ("Alloy Steel",), "Finish": ("Galvanized",)},
        price_range=(3.0, 14.0),
        skus=2,
        featured_sizes=("1/2 in",),
        reason="decoy for the industrial seed queries (#462): a replacement screw pin for a shackle",
    ),
)
