"""Lock Nut Spanner Wrench: a text-match decoy for the industrial seed queries (#462).

A spanner that turns a bearing lock nut. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "spanner_wrenches",
    label="Lock Nut Spanner Wrench",
    breadth=BreadthRow(
        key="spanner_wrenches",
        category=("Hand Tools", "Wrenches", "Spanner Wrenches"),
        family="hand_tool",
        shape="bracket",
        item="Lock Nut Spanner Wrench",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("3/4 in to 2 in", "2 in to 4-1/2 in"),
        attributes={"Material": ("Alloy Steel",), "Finish": ("Chrome Plated",)},
        price_range=(9.0, 38.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a spanner that turns a bearing lock nut",
    ),
)
