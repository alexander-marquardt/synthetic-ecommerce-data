"""Induction Bearing Heater for 6203 Bearings: text-match decoy for the industrial seeds (#462).

An induction heater that expands a 6203 bearing for fitting. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "induction_heaters",
    label="Induction Bearing Heater for 6203 Bearings",
    breadth=BreadthRow(
        key="induction_heaters",
        category=("Power Tools", "Heating Tools", "Induction Heaters"),
        family="hand_tool",
        shape="block",
        item="Induction Bearing Heater for 6203 Bearings",
        descriptor_attr=None,
        size_attr="Maximum Workpiece Weight",
        size_values=("20 lb", "44 lb"),
        attributes={"Material": ("Steel",)},
        price_range=(180.0, 520.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): an induction heater that expands a "
            "6203 bearing for fitting"
        ),
    ),
)
