"""Screw Extractor Set for 1/4-20 Screws: a text-match decoy for the industrial seed queries (#462).

An extractor set that backs out a damaged 1/4-20 screw. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "fastener_extractors",
    label="Screw Extractor Set for 1/4-20 Screws",
    breadth=BreadthRow(
        key="fastener_extractors",
        category=("Hand Tools", "Extractors", "Fastener Extractors"),
        family="hand_tool",
        shape="cylinder",
        item="Screw Extractor Set for 1/4-20 Screws",
        descriptor_attr=None,
        size_attr="Piece Count",
        size_values=("5", "6"),
        attributes={"Material": ("Alloy Steel",)},
        price_range=(9.0, 32.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): an extractor set that backs out a "
            "damaged 1/4-20 screw"
        ),
    ),
)
