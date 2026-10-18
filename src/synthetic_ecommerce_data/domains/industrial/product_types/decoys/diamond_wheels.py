"""Carbide Drill Bit Sharpening Wheel: a text-match decoy for the industrial seed queries (#462).

A diamond wheel that sharpens a carbide drill bit. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "diamond_wheels",
    label="Carbide Drill Bit Sharpening Wheel",
    breadth=BreadthRow(
        key="diamond_wheels",
        category=("Abrasives", "Grinding & Cut-Off", "Diamond Wheels"),
        family="abrasive",
        shape="disc",
        item="Carbide Drill Bit Sharpening Wheel",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("4 in", "6 in"),
        attributes={"Material": ("Diamond",)},
        price_range=(18.0, 80.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a diamond wheel that sharpens a "
            "carbide drill bit"
        ),
    ),
)
