"""Roller Chain Lubricant: a text-match decoy for the industrial seed queries (#462).

An aerosol lubricant for roller chain. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "chain_lubricants",
    label="Roller Chain Lubricant",
    breadth=BreadthRow(
        key="chain_lubricants",
        category=("Lubricants, Coolants & Fluids", "Oils & Lubricants", "Chain Lubricants"),
        family="motion",
        shape="tube",
        item="Roller Chain Lubricant",
        descriptor_attr=None,
        size_attr="Container Size",
        size_values=("11 oz", "16 oz"),
        attributes={"Material": ("PTFE",), "Type": ("Aerosol",)},
        price_range=(6.0, 22.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): an aerosol lubricant for roller chain",
    ),
)
