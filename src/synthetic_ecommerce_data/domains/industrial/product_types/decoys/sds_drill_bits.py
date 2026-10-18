"""Hammer Drill Bit, SDS-Plus: a text-match decoy for the industrial seed queries (#462).

A masonry bit for a hammer drill. Its title holds the seed noun and its category path does not, so
it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "sds_drill_bits",
    label="Hammer Drill Bit, SDS-Plus",
    breadth=BreadthRow(
        key="sds_drill_bits",
        category=("Holemaking", "Masonry Drilling", "SDS Masonry Drill Bits"),
        family="cutting_tool",
        shape="cylinder",
        item="Hammer Drill Bit, SDS-Plus",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("6 mm", "8 mm", "10 mm"),
        attributes={"Material": ("Carbide",)},
        price_range=(3.0, 14.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a masonry bit for a hammer drill",
    ),
)
