"""Side-Lock End Mill Holder: a text-match decoy for the industrial seed queries (#462).

A side-lock holder that clamps a 25 mm end mill. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "side_lock_holders",
    label="Side-Lock End Mill Holder",
    breadth=BreadthRow(
        key="side_lock_holders",
        category=("Tool Holding", "Holders", "Side-Lock Tool Holders"),
        family="cutting_tool",
        shape="cylinder",
        item="Side-Lock End Mill Holder",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("25 mm", "20 mm"),
        attributes={"Material": ("Alloy Steel",), "Type": ("CAT40",)},
        price_range=(55.0, 190.0),
        skus=2,
        featured_sizes=("25 mm",),
        reason=(
            "decoy for the industrial seed queries (#462): a side-lock holder that clamps a 25 mm "
            "end mill"
        ),
    ),
)
