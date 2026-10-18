"""Square End Mill Storage Case: a text-match decoy for the industrial seed queries (#462).

A case that stores 3/8 in square end mills. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "cutter_storage_cases",
    label="Square End Mill Storage Case",
    breadth=BreadthRow(
        key="cutter_storage_cases",
        category=("Material Handling & Storage", "Tool Storage", "Cutter Storage Cases"),
        family="cutting_tool",
        shape="block",
        item="Square End Mill Storage Case",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("3/8 in", "1/2 in"),
        attributes={"Material": ("Plastic",)},
        price_range=(8.0, 30.0),
        skus=2,
        featured_sizes=("3/8 in",),
        reason="decoy for the industrial seed queries (#462): a case that stores 3/8 in square end mills",
    ),
)
