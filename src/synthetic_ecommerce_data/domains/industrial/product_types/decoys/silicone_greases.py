"""O-Ring Silicone Grease: a text-match decoy for the industrial seed queries (#462).

A silicone grease that lubricates O-rings. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "silicone_greases",
    label="O-Ring Silicone Grease",
    breadth=BreadthRow(
        key="silicone_greases",
        category=("Lubricants, Coolants & Fluids", "Greases", "Silicone Greases"),
        family="hand_tool",
        shape="tube",
        item="O-Ring Silicone Grease",
        descriptor_attr=None,
        size_attr="Container Size",
        size_values=("2 oz", "8 oz"),
        attributes={"Material": ("Silicone",)},
        price_range=(5.0, 20.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a silicone grease that lubricates O-rings",
    ),
)
