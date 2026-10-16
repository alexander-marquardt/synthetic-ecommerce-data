"""Greeting Card (gen#424): the ordinary type behind the toy-word decoys of "card".

One authored product; the decoy rows of :mod:`decoy_product_words` hold the shopper's word.
Not derivable.
"""

from __future__ import annotations

from type_registry import TypeSpec, a
from word_decoy_types import GIFTS, plain

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
)
