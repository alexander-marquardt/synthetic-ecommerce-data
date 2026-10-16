"""Glue Gun (gen#424): the ordinary type behind the toy-word decoys of "gun".

One authored product; the decoy rows of :mod:`decoy_product_words` hold the shopper's word.
Not derivable.
"""

from __future__ import annotations

from type_registry import TypeSpec, a
from word_decoy_types import HOME, plain

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
)
