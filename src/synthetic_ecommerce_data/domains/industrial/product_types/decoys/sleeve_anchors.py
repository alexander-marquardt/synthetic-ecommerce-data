"""Stainless Steel Hex Bolt Sleeve Anchor: text-match decoy for the industrial seeds (#462).

A sleeve anchor with a stainless steel hex bolt. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "sleeve_anchors",
    label="Stainless Steel Hex Bolt Sleeve Anchor",
    breadth=BreadthRow(
        key="sleeve_anchors",
        category=("Fasteners", "Anchors", "Sleeve Anchors"),
        family="fastener",
        shape="cylinder",
        item="Stainless Steel Hex Bolt Sleeve Anchor",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("1/4 in", "5/16 in", "3/8 in", "1/2 in"),
        attributes={"Material": ("Stainless Steel",), "Head Type": ("Hex",)},
        price_range=(2.0, 9.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a sleeve anchor with a stainless steel "
            "hex bolt"
        ),
    ),
)
