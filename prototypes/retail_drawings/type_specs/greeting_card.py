"""Greeting cards (gen#425, a spec by gen#351): Gifts > Cards > Greeting Cards.

Eight styles from three brands, drawn by :func:`kit_gifts.greeting_card` (the occasion picks the
motif on the front): a birthday card for a mum, a dad and a friend, an anniversary, a thank you,
a wedding, a new baby and a Christmas card. The occasion and the recipient are structured entries,
and every card is blank inside. The SKUs are the six main colors (gen#275). Not derivable:
authored rows only. Every name here is invented.
"""

from __future__ import annotations

import kit_gifts  # noqa: F401 -- registers greeting_card
from gifts_rows import CALDERBY, CARD_PATH, DEPARTMENT, LANTERNBY, SIX_COLORS, THISTLE
from type_registry import Row, TypeSpec, a


def _card(code, title, brand, occasion, recipient, shape_occasion, description) -> Row:
    return Row(
        code, title, brand, DEPARTMENT, CARD_PATH, "Greeting Card", 3.0, "greeting_card",
        description, SIX_COLORS,
        (a("occasion", "Occasion", occasion), a("recipient", "Recipient", recipient),
         a("blank_inside", "Blank Inside", "Yes")),
        params=(("occasion", shape_occasion),),
    )  # fmt: skip


SPEC = TypeSpec(
    key="greeting_card",
    department=DEPARTMENT,
    product_type="Greeting Card",
    rows=(
        _card("GCDMUM", "Birthday Card for Mum", THISTLE, "Birthday", "Mum", "birthday",
              "A birthday card for mum with a warm message on the front, blank inside to write your own."),
        _card("GCDDAD", "Birthday Card for Dad", CALDERBY, "Birthday", "Dad", "birthday",
              "A birthday card for dad with a dry joke on the front, blank inside to write your own."),
        _card("GCDFRI", "Birthday Card for a Friend", LANTERNBY, "Birthday", "Friend", "birthday",
              "A birthday card for a friend with a funny line on the front, blank inside."),
        _card("GCANNI", "Anniversary Card", THISTLE, "Anniversary", "Any", "anniversary",
              "An anniversary card for a husband, wife or partner, blank inside for your own words."),
        _card("GCTHNK", "Thank You Card", LANTERNBY, "Thank You", "Any", "thank_you",
              "A thank you card to say thanks to a teacher, a neighbour or a host, blank inside."),
        _card("GCWEDD", "Wedding Card", CALDERBY, "Wedding", "Any", "wedding",
              "A wedding card to congratulate the happy couple, blank inside for your good wishes."),
        _card("GCBABY", "New Baby Card", THISTLE, "New Baby", "Any", "new_baby",
              "A new baby card to welcome the little one, blank inside for your message."),
        _card("GCXMAS", "Christmas Card", LANTERNBY, "Christmas", "Any", "christmas",
              "A Christmas card with a festive motif on the front, blank inside for a seasonal greeting."),
    ),
)  # fmt: skip
