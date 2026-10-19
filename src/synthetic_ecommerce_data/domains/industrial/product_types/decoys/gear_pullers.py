"""Sprocket Puller: a text-match decoy for the industrial seed queries (#462).

A puller that draws a sprocket off its shaft. Its title holds the seed noun and its category path
does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "gear_pullers",
    label="Sprocket Puller",
    breadth=BreadthRow(
        key="gear_pullers",
        category=("Hand Tools", "Pullers & Extractors", "Gear Pullers"),
        family="hand_tool",
        shape="bracket",
        item="Sprocket Puller",
        descriptor_attr=None,
        size_attr="Maximum Size",
        size_values=("4 in", "6 in", "8 in"),
        attributes={"Material": ("Alloy Steel",), "Type": ("Two-Jaw",)},
        price_range=(20.0, 85.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a puller that draws a sprocket off its "
            "shaft"
        ),
    ),
)
