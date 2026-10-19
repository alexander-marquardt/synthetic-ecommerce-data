"""Hex Key for M6x1 Set Screws: a text-match decoy for the industrial seed queries (#462).

A 3 mm hex key that drives an M6x1 set screw. Its title holds the seed noun and its category path
does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "grub_screw_keys",
    label="Hex Key for M6x1 Set Screws",
    breadth=BreadthRow(
        key="grub_screw_keys",
        category=("Hand Tools", "Wrenches & Keys", "Grub Screw Keys"),
        family="hand_tool",
        shape="bracket",
        item="Hex Key for M6x1 Set Screws",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("3 mm", "4 mm"),
        attributes={"Material": ("Alloy Steel",), "Finish": ("Black Oxide",)},
        price_range=(3.0, 12.0),
        skus=2,
        featured_sizes=("3 mm",),
        reason=(
            "decoy for the industrial seed queries (#462): a 3 mm hex key that drives an M6x1 set "
            "screw"
        ),
    ),
)
