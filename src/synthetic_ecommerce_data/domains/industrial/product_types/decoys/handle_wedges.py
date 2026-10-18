"""Hammer Handle Wedge: a text-match decoy for the industrial seed queries (#462).

A wedge that locks a hammer head on its handle. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "handle_wedges",
    label="Hammer Handle Wedge",
    breadth=BreadthRow(
        key="handle_wedges",
        category=("Hand Tools", "Replacement Parts", "Handle Wedges"),
        family="hand_tool",
        shape="block",
        item="Hammer Handle Wedge",
        descriptor_attr=None,
        size_attr="Width",
        size_values=("3/8 in", "1/2 in"),
        attributes={"Material": ("Steel",)},
        price_range=(2.0, 9.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a wedge that locks a hammer head on its handle",
    ),
)
