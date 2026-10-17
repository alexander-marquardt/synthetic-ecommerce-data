"""Gift Card (gen#424): the ordinary type behind the toy-word decoys of "card".

One authored product; the class-8 decoys (gen#326) hold the shopper's word.
Not derivable.
"""

from __future__ import annotations

from type_registry import TypeSpec, a
from word_decoy_types import GIFTS, plain, word_decoy

SPEC = TypeSpec(
    key="gift_card",
    department="Gifts",
    product_type="Gift Card",
    rows=(
        plain(
            "GFCPLN",
            "Shop Voucher Wallet",
            GIFTS,
            "Gifts",
            ("Gifts", "Cards", "Gift Cards"),
            "Gift Card",
            "gift_card",
            "A voucher that holds a balance to spend in the shop, in a presentation wallet.",
            25.0,
            (
                a("material", "Material", "Plastic"),
                a("kind", "Kind", "Voucher"),
            ),
        ),
    ),
    decoys=(
        word_decoy(
            4, "Plastic Gift Card",
            "A card that holds a balance to spend in the shop, in a sleeve.",
            "Gold", GIFTS, "Gifts", ("Gifts", "Cards", "Gift Cards"),
            "Gift Card", "gift_card", 25.0, "card",
        ),
        word_decoy(
            7, "Christmas Gift Card",
            "A festive card that holds a balance to spend in the shop.",
            "Red", GIFTS, "Gifts", ("Gifts", "Cards", "Gift Cards"),
            "Gift Card", "gift_card", 25.0, "card",
        ),
    ),
)
