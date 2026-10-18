"""Ball Bearing Puller Set: a text-match decoy for the industrial seed queries (#462).

A puller set that draws a ball bearing off a shaft. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "bearing_pullers",
    label="Ball Bearing Puller Set",
    breadth=BreadthRow(
        key="bearing_pullers",
        category=("Hand Tools", "Pullers & Extractors", "Bearing Pullers"),
        family="hand_tool",
        shape="bracket",
        item="Ball Bearing Puller Set",
        descriptor_attr=None,
        size_attr="Capacity",
        size_values=("3 in", "6 in"),
        attributes={"Material": ("Alloy Steel",), "Type": ("Three-Jaw",)},
        price_range=(28.0, 120.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a puller set that draws a ball bearing "
            "off a shaft"
        ),
    ),
)
