"""Bearing Fitting Tool Kit for 6203 Bearings: text-match decoy for the industrial seeds (#462).

A fitting kit whose sleeves seat a 6203 bearing. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "sleeve_installation_kits",
    label="Bearing Fitting Tool Kit for 6203 Bearings",
    breadth=BreadthRow(
        key="sleeve_installation_kits",
        category=("Hand Tools", "Installation Tools", "Sleeve Installation Kits"),
        family="hand_tool",
        shape="block",
        item="Bearing Fitting Tool Kit for 6203 Bearings",
        descriptor_attr=None,
        size_attr="Piece Count",
        size_values=("10", "36"),
        attributes={"Material": ("Aluminum",)},
        price_range=(25.0, 95.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a fitting kit whose sleeves seat a "
            "6203 bearing"
        ),
    ),
)
