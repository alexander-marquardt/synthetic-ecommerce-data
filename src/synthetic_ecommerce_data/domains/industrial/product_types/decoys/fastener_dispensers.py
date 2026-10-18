"""Retaining Ring Applicator Dispenser: a text-match decoy for the industrial seed queries (#462).

An applicator that dispenses and seats retaining rings. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "fastener_dispensers",
    label="Retaining Ring Applicator Dispenser",
    breadth=BreadthRow(
        key="fastener_dispensers",
        category=("Hand Tools", "Assembly Tools", "Fastener Dispensers"),
        family="hand_tool",
        shape="tube",
        item="Retaining Ring Applicator Dispenser",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("10 mm", "25 mm"),
        attributes={"Material": ("Aluminum",)},
        price_range=(16.0, 55.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): an applicator that dispenses and seats "
            "retaining rings"
        ),
    ),
)
