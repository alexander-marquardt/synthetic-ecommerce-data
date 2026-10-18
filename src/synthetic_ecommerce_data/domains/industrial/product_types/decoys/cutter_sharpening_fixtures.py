"""Square End Mill Sharpening Fixture: a text-match decoy for the industrial seed queries (#462).

A fixture that holds a 3/8 in square end mill on a grinder. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "cutter_sharpening_fixtures",
    label="Square End Mill Sharpening Fixture",
    breadth=BreadthRow(
        key="cutter_sharpening_fixtures",
        category=("Machinery", "Tool Grinding", "Cutter Sharpening Fixtures"),
        family="cutting_tool",
        shape="block",
        item="Square End Mill Sharpening Fixture",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("3/8 in", "1/2 in"),
        attributes={"Material": ("Steel",)},
        price_range=(60.0, 240.0),
        skus=2,
        featured_sizes=("3/8 in",),
        reason="decoy for the industrial seed queries (#462): a fixture that holds a 3/8 in square end mill on a grinder",
    ),
)
