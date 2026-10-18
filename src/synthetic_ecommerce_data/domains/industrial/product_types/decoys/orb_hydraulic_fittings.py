"""ORB Hydraulic Fitting with O-Ring: a text-match decoy for the industrial seed queries (#462).

An O-ring boss hydraulic fitting that seals with an O-ring. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "orb_hydraulic_fittings",
    label="ORB Hydraulic Fitting with O-Ring",
    breadth=BreadthRow(
        key="orb_hydraulic_fittings",
        category=("Hose, Tube, Fittings & Valves", "Hydraulic Fittings", "ORB Hydraulic Fittings"),
        family="motion",
        shape="cylinder",
        item="ORB Hydraulic Fitting with O-Ring",
        descriptor_attr=None,
        size_attr="Thread Size",
        size_values=("9/16-18", "3/4-16", "7/8-14"),
        attributes={"Material": ("Steel",), "Finish": ("Zinc Plated",)},
        price_range=(6.0, 26.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): an O-ring boss hydraulic fitting that "
            "seals with an O-ring"
        ),
    ),
)
