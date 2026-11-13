"""Hex Nut Driver: a text-match decoy for the industrial seed queries (#462).

A driver for hex nuts, sold in the Hand Tools department. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "nut_drivers_hex",
    label="Hex Nut Driver",
    use_lines=(
        "Turns hex nuts faster than a wrench; the six-point socket grips the nut on its flats.",
        (
            "A hollow shaft clears long studs, so the driver runs a nut down threaded rod and "
            "seats the nut by hand."
        ),
    ),
    breadth=BreadthRow(
        key="nut_drivers_hex",
        category=("Hand Tools", "Screwdrivers & Nut Drivers", "Nut Drivers"),
        family="hand_tool",
        shape="cylinder",
        item="Hex Nut Driver",
        descriptor_attr=None,
        size_attr="Drive Size",
        size_values=("1/4 in", "5/16 in", "3/8 in", "1/2 in"),
        attributes={"Material": ("Alloy Steel",), "Type": ("Hollow Shaft",)},
        price_range=(6.0, 18.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a driver for hex nuts, sold in the "
            "Hand Tools department"
        ),
    ),
)
