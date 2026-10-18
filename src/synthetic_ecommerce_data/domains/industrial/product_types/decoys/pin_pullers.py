"""Dowel Pin Puller: a text-match decoy for the industrial seed queries (#462).

A puller that draws a dowel pin from a blind hole. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "pin_pullers",
    label="Dowel Pin Puller",
    breadth=BreadthRow(
        key="pin_pullers",
        category=("Hand Tools", "Pullers & Extractors", "Pin Pullers"),
        family="hand_tool",
        shape="bracket",
        item="Dowel Pin Puller",
        descriptor_attr=None,
        size_attr="Capacity",
        size_values=("1/4 in", "1/2 in"),
        attributes={"Material": ("Alloy Steel",)},
        price_range=(15.0, 60.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a puller that draws a dowel pin from a blind hole",
    ),
)
