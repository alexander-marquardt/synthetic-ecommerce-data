"""Sprocket Alignment Laser Tool: a text-match decoy for the industrial seed queries (#462).

A laser that lines up two sprockets. Its title holds the seed noun and its category path does not,
so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "shaft_alignment_lasers",
    label="Sprocket Alignment Laser Tool",
    breadth=BreadthRow(
        key="shaft_alignment_lasers",
        category=("Measuring & Inspecting", "Alignment Tools", "Shaft Alignment Lasers"),
        family="motion",
        shape="cylinder",
        item="Sprocket Alignment Laser Tool",
        descriptor_attr=None,
        size_attr="Overall Length",
        size_values=("4 in", "6 in"),
        attributes={"Material": ("Aluminum",)},
        price_range=(35.0, 140.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a laser that lines up two sprockets",
    ),
)
