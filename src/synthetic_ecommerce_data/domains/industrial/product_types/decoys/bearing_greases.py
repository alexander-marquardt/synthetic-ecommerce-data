"""Ball Bearing Grease: a text-match decoy for the industrial seed queries (#462).

A lithium complex grease sold for ball bearings. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "bearing_greases",
    label="Ball Bearing Grease",
    breadth=BreadthRow(
        key="bearing_greases",
        category=("Lubricants, Coolants & Fluids", "Greases", "Bearing Greases"),
        family="hand_tool",
        shape="tube",
        item="Ball Bearing Grease",
        descriptor_attr=None,
        size_attr="Container Size",
        size_values=("400 g", "1 kg"),
        attributes={"Material": ("Lithium Complex",)},
        price_range=(8.0, 30.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a lithium complex grease sold for ball bearings",
    ),
)
