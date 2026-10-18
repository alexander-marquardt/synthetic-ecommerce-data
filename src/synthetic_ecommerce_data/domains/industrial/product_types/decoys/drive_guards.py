"""Sprocket and Chain Guard: a text-match decoy for the industrial seed queries (#462).

A guard that covers a sprocket and its chain. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "drive_guards",
    label="Sprocket and Chain Guard",
    breadth=BreadthRow(
        key="drive_guards",
        category=("Motion Control & Fluid Power", "Guards & Covers", "Drive Guards"),
        family="motion",
        shape="bracket",
        item="Sprocket and Chain Guard",
        descriptor_attr=None,
        size_attr="Width",
        size_values=("4 in", "6 in", "8 in"),
        attributes={"Material": ("Steel",), "Finish": ("Powder Coated",)},
        price_range=(30.0, 140.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a guard that covers a sprocket and its chain",
    ),
)
