"""Tap Wrench for Spiral Flute Taps: a text-match decoy for the industrial seed queries (#462).

A wrench that turns spiral flute taps. Its title holds the seed noun and its category path does
not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "tap_wrenches",
    label="Tap Wrench for Spiral Flute Taps",
    breadth=BreadthRow(
        key="tap_wrenches",
        category=("Threading", "Tap Accessories", "Tap Wrenches"),
        family="cutting_tool",
        shape="bracket",
        item="Tap Wrench for Spiral Flute Taps",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("M3 to M12",),
        attributes={"Material": ("Alloy Steel",), "Type": ("T-Handle",)},
        price_range=(10.0, 38.0),
        skus=1,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a wrench that turns spiral flute taps"
        ),
    ),
)
