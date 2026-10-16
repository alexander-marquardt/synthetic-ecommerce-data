"""Greeting Card (gen#424): the ordinary type behind the toy-word decoys of "card".

One authored product; the class-8 decoys (gen#326) hold the shopper's word.
Not derivable.
"""

from __future__ import annotations

from type_registry import TypeSpec, a
from word_decoy_types import GIFTS, plain, word_decoy

SPEC = TypeSpec(
    key="greeting_card",
    department="Gifts",
    product_type="Greeting Card",
    rows=(
        plain(
            "GCDPLN",
            "Birthday Wishes Card",
            GIFTS,
            "Gifts",
            ("Gifts", "Cards", "Greeting Cards"),
            "Greeting Card",
            "greeting_card",
            "A folded card printed with a birthday message, with a blank inside and an envelope.",
            3.0,
            (
                a("occasion", "Occasion", "Birthday"),
                a("material", "Material", "Card"),
            ),
        ),
    ),
    decoys=(
        word_decoy(
            3, "Birthday Greeting Card",
            "A folded card with a message inside, sent with a present.",
            "Cream", GIFTS, "Gifts", ("Gifts", "Cards", "Greeting Cards"),
            "Greeting Card", "greeting_card", 3.0, "card",
        ),
    ),
)
