"""Magnetic Screwdriver Bit Holder: a text-match decoy for the industrial seed queries (#462).

A magnetic holder that seats a bit in a screwdriver handle. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "magnetic_bit_holders",
    label="Magnetic Screwdriver Bit Holder",
    breadth=BreadthRow(
        key="magnetic_bit_holders",
        category=("Hand Tools", "Bits & Bit Holders", "Magnetic Bit Holders"),
        family="hand_tool",
        shape="cylinder",
        item="Magnetic Screwdriver Bit Holder",
        descriptor_attr=None,
        size_attr="Length",
        size_values=("2 in", "3 in"),
        attributes={"Material": ("Steel",)},
        price_range=(3.0, 12.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a magnetic holder that seats a bit in a screwdriver handle",
    ),
)
