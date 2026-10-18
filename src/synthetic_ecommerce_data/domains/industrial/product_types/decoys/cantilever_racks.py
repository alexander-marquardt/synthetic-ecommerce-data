"""Bar Stock Cantilever Rack: a text-match decoy for the industrial seed queries (#462).

A cantilever rack that stores bar stock. Its title holds the seed noun and its category path does
not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "cantilever_racks",
    label="Bar Stock Cantilever Rack",
    breadth=BreadthRow(
        key="cantilever_racks",
        category=("Material Handling & Storage", "Storage Racks", "Cantilever Racks"),
        family="hand_tool",
        shape="bracket",
        item="Bar Stock Cantilever Rack",
        descriptor_attr=None,
        size_attr="Rated Load",
        size_values=("2000 lb", "4000 lb"),
        attributes={"Material": ("Steel",), "Finish": ("Powder Coated",)},
        price_range=(240.0, 980.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a cantilever rack that stores bar stock"
        ),
    ),
)
