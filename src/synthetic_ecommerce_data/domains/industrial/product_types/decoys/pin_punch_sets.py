"""Dowel Pin Punch Set: a text-match decoy for the industrial seed queries (#462).

A punch set that drives out a dowel pin. Its title holds the seed noun and its category path does
not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "pin_punch_sets",
    label="Dowel Pin Punch Set",
    breadth=BreadthRow(
        key="pin_punch_sets",
        category=("Hand Tools", "Punches & Chisels", "Pin Punch Sets"),
        family="hand_tool",
        shape="cylinder",
        item="Dowel Pin Punch Set",
        descriptor_attr=None,
        size_attr="Number of Pieces",
        size_values=("5", "8"),
        attributes={"Material": ("Alloy Steel",), "Finish": ("Black Oxide",)},
        price_range=(12.0, 40.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a punch set that drives out a dowel pin"
        ),
    ),
)
