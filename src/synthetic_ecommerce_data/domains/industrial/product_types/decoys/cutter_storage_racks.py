"""End Mill Storage Rack: a text-match decoy for the industrial seed queries (#462).

A rack that stores end mills from 2.5 mm to 25 mm. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "cutter_storage_racks",
    label="End Mill Storage Rack",
    breadth=BreadthRow(
        key="cutter_storage_racks",
        category=("Material Handling & Storage", "Tool Storage", "Cutter Storage Racks"),
        family="cutting_tool",
        shape="block",
        item="End Mill Storage Rack",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("2.5 mm to 25 mm",),
        attributes={"Material": ("Steel",)},
        price_range=(18.0, 70.0),
        skus=1,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a rack that stores end mills from 2.5 mm to 25 mm",
    ),
)
