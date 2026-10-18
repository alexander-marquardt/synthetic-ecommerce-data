"""Pneumatic Cut-Off Tool for Cut-Off Wheels: a text-match decoy for the industrial seed queries (#462).

An air tool that spins 3 in cut-off wheels. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "pneumatic_cut_off_tools",
    label="Pneumatic Cut-Off Tool for Cut-Off Wheels",
    breadth=BreadthRow(
        key="pneumatic_cut_off_tools",
        category=("Power Tools", "Air Tools", "Pneumatic Cut-Off Tools"),
        family="abrasive",
        shape="block",
        item="Pneumatic Cut-Off Tool for Cut-Off Wheels",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("3 in", "4 in"),
        attributes={"Material": ("Aluminum",)},
        price_range=(35.0, 140.0),
        skus=2,
        featured_sizes=("3 in",),
        reason="decoy for the industrial seed queries (#462): an air tool that spins 3 in cut-off wheels",
    ),
)
