"""Fridge Magnets (gen#334): the ordinary type behind a class-8 decoy of "fridge".

One authored product, titled without the appliance word; the class-8 decoy (gen#326) is the
spec's own `decoys`. Drawn by :func:`kit_large_appliances.fridge_magnet`.
Not derivable.
"""

from __future__ import annotations

import kit_large_appliances  # noqa: F401 -- registers the shape
from type_registry import TypeSpec, a
from word_decoy_types import HOME, plain, word_decoy

SPEC = TypeSpec(
    key="fridge_magnets",
    department="Home",
    product_type="Fridge Magnets",
    rows=(
        plain(
            "FMGPLN",
            "Photo and Note Magnets, Set of 8",
            HOME,
            "Home",
            ("Home", "Kitchen & Dining", "Fridge Magnets"),
            "Fridge Magnets",
            "fridge_magnet",
            "Round magnets on a card that hold lists, photos and school letters to a steel door.",
            5.0,
            (
                a("material", "Material", "Ceramic"),
                a("pack_size", "Pack size", "8 pack"),
            ),
        ),
    ),
    decoys=(
        word_decoy(
            32, "Fridge Magnets, Set of 6",
            "Six small magnets that hold notes and photos on a door.",
            "Red", HOME, "Home", ("Home", "Kitchen & Dining", "Fridge Magnets"),
            "Fridge Magnets", "fridge_magnet", 6.0, "fridge", "category",
        ),
    ),
)
