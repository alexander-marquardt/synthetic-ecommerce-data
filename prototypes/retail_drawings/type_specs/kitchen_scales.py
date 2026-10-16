"""Kitchen Scales (gen#424): the ordinary type behind the toy-word decoys of "kitchen".

One authored product; the decoy rows of :mod:`decoy_product_words` hold the shopper's word.
Not derivable.
"""

from __future__ import annotations

from type_registry import TypeSpec, a
from word_decoy_types import HOME, plain

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
)
