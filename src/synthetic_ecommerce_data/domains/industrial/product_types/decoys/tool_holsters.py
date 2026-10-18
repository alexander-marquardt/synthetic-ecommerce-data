"""Hammer Holster: a text-match decoy for the industrial seed queries (#462).

A belt holster that carries a hammer. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "tool_holsters",
    label="Hammer Holster",
    breadth=BreadthRow(
        key="tool_holsters",
        category=("Hand Tools", "Tool Holders & Holsters", "Tool Holsters"),
        family="hand_tool",
        shape="bracket",
        item="Hammer Holster",
        descriptor_attr=None,
        size_attr="Width",
        size_values=("2 in", "3 in"),
        attributes={"Material": ("Nylon",)},
        price_range=(6.0, 24.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a belt holster that carries a hammer",
    ),
)
