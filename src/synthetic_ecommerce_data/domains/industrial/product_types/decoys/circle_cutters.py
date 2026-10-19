"""Washer Cutter, Adjustable: a text-match decoy for the industrial seed queries (#462).

An adjustable cutter that cuts washers from gasket sheet. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "circle_cutters",
    label="Washer Cutter, Adjustable",
    breadth=BreadthRow(
        key="circle_cutters",
        category=("Hand Tools", "Cutters", "Circle Cutters"),
        family="hand_tool",
        shape="bracket",
        item="Washer Cutter, Adjustable",
        descriptor_attr=None,
        size_attr="Maximum Size",
        size_values=("1/2 in to 5 in",),
        attributes={"Material": ("High Speed Steel",)},
        price_range=(14.0, 48.0),
        skus=1,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): an adjustable cutter that cuts washers "
            "from gasket sheet"
        ),
    ),
)
