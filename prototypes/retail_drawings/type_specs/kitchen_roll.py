"""Kitchen Roll (gen#424): the ordinary type behind the toy-word decoys of "kitchen".

One authored product; the decoy rows of :mod:`decoy_product_words` hold the shopper's word.
Not derivable.
"""

from __future__ import annotations

from type_registry import TypeSpec, a
from word_decoy_types import HOME, plain

SPEC = TypeSpec(
    key="kitchen_roll",
    department="Home",
    product_type="Kitchen Roll",
    rows=(
        plain(
            "KRLPLN",
            "Absorbent Paper Towels, Pack of 4",
            HOME,
            "Home",
            ("Home", "Kitchen & Dining", "Kitchen Rolls"),
            "Kitchen Roll",
            "wrapping_paper",
            "Four rolls of soft, absorbent two ply paper towels.",
            5.0,
            (
                a("material", "Material", "Paper"),
                a("plies", "Plies", "2"),
            ),
        ),
    ),
)
