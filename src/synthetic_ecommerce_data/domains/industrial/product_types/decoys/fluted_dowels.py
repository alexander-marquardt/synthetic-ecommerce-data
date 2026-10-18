"""Fluted Wooden Dowel Pins: a text-match decoy for the industrial seed queries (#462).

A wooden dowel pin for furniture joints, 8 mm. Its title holds the seed noun and its category path
does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "fluted_dowels",
    label="Fluted Wooden Dowel Pins",
    breadth=BreadthRow(
        key="fluted_dowels",
        category=("Raw Materials", "Wood Stock", "Fluted Dowels"),
        family="fastener",
        shape="cylinder",
        item="Fluted Wooden Dowel Pins",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("6 mm", "8 mm", "10 mm"),
        attributes={"Material": ("Birch",), "Units per Pack": ("100",)},
        price_range=(4.0, 14.0),
        skus=2,
        featured_sizes=("8 mm",),
        reason=(
            "decoy for the industrial seed queries (#462): a wooden dowel pin for furniture "
            "joints, 8 mm"
        ),
    ),
)
