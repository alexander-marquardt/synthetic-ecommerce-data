"""Flap Disc Angle Grinder Guard: a text-match decoy for the industrial seed queries (#462).

A guard that covers a flap disc on an angle grinder. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "grinder_guards",
    label="Flap Disc Angle Grinder Guard",
    breadth=BreadthRow(
        key="grinder_guards",
        category=("Abrasives", "Grinder Accessories", "Grinder Guards"),
        family="abrasive",
        shape="bracket",
        item="Flap Disc Angle Grinder Guard",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("4-1/2 in", "5 in"),
        attributes={"Material": ("Steel",)},
        price_range=(9.0, 32.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a guard that covers a flap disc on an "
            "angle grinder"
        ),
    ),
)
