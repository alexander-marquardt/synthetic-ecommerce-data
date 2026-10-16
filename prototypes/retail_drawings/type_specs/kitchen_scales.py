"""Kitchen Scales (gen#424): the ordinary type behind the toy-word decoys of "kitchen".

One authored product; the class-8 decoys (gen#326) hold the shopper's word.
Not derivable.
"""

from __future__ import annotations

from type_registry import TypeSpec, a
from word_decoy_types import HOME, plain, word_decoy

SPEC = TypeSpec(
    key="kitchen_scales",
    department="Home",
    product_type="Kitchen Scales",
    rows=(
        plain(
            "KSCPLN",
            "Digital Baking Scales",
            HOME,
            "Home",
            ("Home", "Kitchen & Dining", "Kitchen Scales"),
            "Kitchen Scales",
            "kitchen_scales",
            "Flat electronic scales that weigh flour, sugar and butter to the gram.",
            16.0,
            (
                a("material", "Material", "Plastic"),
                a("display", "Display", "Digital"),
            ),
        ),
    ),
    decoys=(
        word_decoy(
            2, "Digital Kitchen Scales",
            "Flat scales that weigh ingredients in the kitchen to the gram.",
            "Grey", HOME, "Home", ("Home", "Kitchen & Dining", "Kitchen Scales"),
            "Kitchen Scales", "kitchen_scales", 16.0, "kitchen",
        ),
    ),
)
