"""Hex Nut Splitter: a text-match decoy for the industrial seed queries (#462).

A splitter that removes a seized hex nut. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "nut_splitters",
    label="Hex Nut Splitter",
    breadth=BreadthRow(
        key="nut_splitters",
        category=("Hand Tools", "Nut Breakers", "Nut Splitters"),
        family="hand_tool",
        shape="block",
        item="Hex Nut Splitter",
        descriptor_attr=None,
        size_attr="Capacity",
        size_values=("1/4 in", "1/2 in", "3/4 in"),
        attributes={"Material": ("Alloy Steel",), "Finish": ("Black Oxide",)},
        price_range=(12.0, 45.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a splitter that removes a seized hex nut",
    ),
)
