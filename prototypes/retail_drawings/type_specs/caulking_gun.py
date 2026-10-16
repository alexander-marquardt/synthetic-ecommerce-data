"""Caulking Gun (gen#424): the ordinary type behind the toy-word decoys of "gun".

One authored product; the class-8 decoys (gen#326) hold the shopper's word.
Not derivable.
"""

from __future__ import annotations

from type_registry import TypeSpec, a
from word_decoy_types import HOME, plain, word_decoy

SPEC = TypeSpec(
    key="caulking_gun",
    department="Home",
    product_type="Caulking Gun",
    rows=(
        plain(
            "CGNPLN",
            "Frame Sealant Applicator",
            HOME,
            "Home",
            ("Home", "DIY & Car", "Caulking Guns"),
            "Caulking Gun",
            "caulking_gun",
            "A steel frame that squeezes sealant from a cartridge along a joint.",
            12.0,
            (
                a("material", "Material", "Steel"),
                a("cartridge", "Cartridge", "Standard"),
            ),
        ),
    ),
    decoys=(
        word_decoy(
            6, "Caulking Gun",
            "A frame gun that squeezes sealant from a cartridge along a joint.",
            "Grey", HOME, "Home", ("Home", "DIY & Car", "Caulking Guns"),
            "Caulking Gun", "caulking_gun", 12.0, "gun",
        ),
    ),
)
