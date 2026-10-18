"""Bolt Cutter: a text-match decoy for the industrial seed queries (#462).

A compound action cutter that shears a bolt. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "compound_cutters",
    label="Bolt Cutter",
    breadth=BreadthRow(
        key="compound_cutters",
        category=("Hand Tools", "Cutters", "Compound Cutters"),
        family="hand_tool",
        shape="bracket",
        item="Bolt Cutter",
        descriptor_attr=None,
        size_attr="Overall Length",
        size_values=("18 in", "24 in", "36 in"),
        attributes={"Material": ("Alloy Steel",), "Handle Material": ("Steel",)},
        price_range=(22.0, 85.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a compound action cutter that shears a bolt",
    ),
)
