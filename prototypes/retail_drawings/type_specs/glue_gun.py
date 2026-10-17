"""Glue Gun (gen#424): the ordinary type behind the toy-word decoys of "gun".

One authored product; the class-8 decoys (gen#326) hold the shopper's word.
Not derivable.
"""

from __future__ import annotations

from type_registry import TypeSpec, a
from word_decoy_types import HOME, plain, word_decoy

SPEC = TypeSpec(
    key="glue_gun",
    department="Home",
    product_type="Glue Gun",
    rows=(
        plain(
            "GGNPLN",
            "Hot Melt Craft Glue Tool",
            HOME,
            "Home",
            ("Home", "DIY & Car", "Glue Guns"),
            "Glue Gun",
            "glue_gun",
            "A trigger fed tool that melts glue sticks for crafts and quick repairs.",
            14.0,
            (
                a("power_source", "Power source", "Mains"),
                a("material", "Material", "Plastic"),
            ),
        ),
    ),
    decoys=(
        word_decoy(
            5, "Hot Glue Gun",
            "A trigger fed gun that melts glue sticks for crafts and repairs.",
            "Grey", HOME, "Home", ("Home", "DIY & Car", "Glue Guns"),
            "Glue Gun", "glue_gun", 14.0, "gun",
        ),
    ),
)
