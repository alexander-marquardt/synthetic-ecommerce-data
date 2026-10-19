"""Fridge Magnets (gen#334): the ordinary type behind a class-8 decoy of "fridge".

One authored product, titled without the appliance word; the decoy (gen#326) is in
``feature_decoys/large_appliances.py``. Drawn by :func:`kit_large_appliances.fridge_magnet`.
Not derivable.
"""

from __future__ import annotations

import kit_large_appliances  # noqa: F401 -- registers the shape
from type_registry import TypeSpec, a
from word_decoy_types import HOME, plain

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
                a("pack_size", "Pack size", "8"),
            ),
        ),
    ),
)
