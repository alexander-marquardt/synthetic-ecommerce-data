"""Roller Chain Breaker Tool: a text-match decoy for the industrial seed queries (#462).

A breaker that presses a pin out of roller chain. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "chain_breakers",
    label="Roller Chain Breaker Tool",
    breadth=BreadthRow(
        key="chain_breakers",
        category=("Hand Tools", "Chain Tools", "Chain Breakers"),
        family="motion",
        shape="bracket",
        item="Roller Chain Breaker Tool",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("#40", "#50", "#60"),
        attributes={"Material": ("Alloy Steel",)},
        price_range=(22.0, 80.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a breaker that presses a pin out of roller chain",
    ),
)
