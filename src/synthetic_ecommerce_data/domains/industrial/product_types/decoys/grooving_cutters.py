"""Retaining Ring Groove Cutter: a text-match decoy for the industrial seed queries (#462).

A cutter that machines the groove a retaining ring sits in. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "grooving_cutters",
    label="Retaining Ring Groove Cutter",
    breadth=BreadthRow(
        key="grooving_cutters",
        category=("Milling", "Slotting Cutters", "Grooving Cutters"),
        family="cutting_tool",
        shape="disc",
        item="Retaining Ring Groove Cutter",
        descriptor_attr=None,
        size_attr="Width",
        size_values=("1.3 mm", "1.6 mm", "2.15 mm"),
        attributes={"Material": ("Carbide",)},
        price_range=(28.0, 90.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a cutter that machines the groove a "
            "retaining ring sits in"
        ),
    ),
)
