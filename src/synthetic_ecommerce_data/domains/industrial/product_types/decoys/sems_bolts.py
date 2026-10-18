"""Sems Bolt with Captive Washer: a text-match decoy for the industrial seed queries (#462).

A bolt that carries its own captive washer, M10. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "sems_bolts",
    label="Sems Bolt with Captive Washer",
    breadth=BreadthRow(
        key="sems_bolts",
        category=("Fasteners", "Bolts", "Sems Bolts"),
        family="fastener",
        shape="cylinder",
        item="Sems Bolt with Captive Washer",
        descriptor_attr=None,
        size_attr="Thread Size",
        size_values=("M6", "M8", "M10", "M12"),
        attributes={"Material": ("Steel",), "Finish": ("Zinc Plated",), "Head Type": ("Hex",)},
        price_range=(5.0, 16.0),
        skus=2,
        featured_sizes=("M10",),
        reason=(
            "decoy for the industrial seed queries (#462): a bolt that carries its own captive "
            "washer, M10"
        ),
    ),
)
