"""Retaining Ring Pliers: a text-match decoy for the industrial seed queries (#462).

Pliers that fit and remove retaining rings. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "snap_ring_pliers",
    label="Retaining Ring Pliers",
    breadth=BreadthRow(
        key="snap_ring_pliers",
        category=("Hand Tools", "Pliers", "Snap Ring Pliers"),
        family="hand_tool",
        shape="bracket",
        item="Retaining Ring Pliers",
        descriptor_attr=None,
        size_attr="Overall Length",
        size_values=("5 in", "7 in"),
        attributes={"Material": ("Alloy Steel",), "Type": ("Internal/External Convertible",)},
        price_range=(12.0, 42.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): pliers that fit and remove retaining rings",
    ),
)
