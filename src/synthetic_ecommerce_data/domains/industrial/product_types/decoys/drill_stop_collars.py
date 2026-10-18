"""Drill Bit Stop Collar: a text-match decoy for the industrial seed queries (#462).

A stop collar that sets the depth of a 3/8 in drill bit. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "drill_stop_collars",
    label="Drill Bit Stop Collar",
    breadth=BreadthRow(
        key="drill_stop_collars",
        category=("Holemaking", "Drill Accessories", "Depth Stop Collars"),
        family="cutting_tool",
        shape="cylinder",
        item="Drill Bit Stop Collar",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("3/8 in", "1/2 in"),
        attributes={"Material": ("Steel",)},
        price_range=(2.0, 9.0),
        skus=2,
        featured_sizes=("3/8 in",),
        reason=(
            "decoy for the industrial seed queries (#462): a stop collar that sets the depth of a "
            "3/8 in drill bit"
        ),
    ),
)
