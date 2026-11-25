"""Anklet (gen#1113): a fine chain for the ankle, sold by metal and by length.

Each SKU is a metal (the color is the metal, as for every jewelry row since gen#207) times a
length (``length_cm``: 23 or 25, each with an extender). ``style`` is drawn by
:mod:`kit_jewellery` (plain chain, beaded, charm discs, double chain). The rows are derivable, and
a derived style keeps its template's style (``scale_text.JEWELLERY_KEYS``).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.accessory_rows import ARow
from synthetic_ecommerce_data.domains.retail.audience import WOMENS
from synthetic_ecommerce_data.domains.retail.jewellery_rows import (
    ALL_METALS,
    CALDERBY,
    CLOTHING,
    HARBOUR,
    LARKMOOR,
    METALS,
    OWNED,
    SILVER,
    SKERRY,
    STEEL,
    TIDEWELL,
    WRENFIELD,
    a,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

PATH, PTYPE = ("Womens", "Jewellery", "Anklets"), "Anklet"
#: The lengths, the longer a little dearer.
LENGTHS = ("23", "25")


def _row(code, title, brand, price, desc, style, kind, colors=ALL_METALS, steel=False):
    table = STEEL if steel else METALS
    attrs = (
        a("anklet_style", "Anklet style", kind), *(a("metal", "Metal", table[c[0]]) for c in colors),
        *((a("hypoallergenic", "Hypoallergenic", "Yes"),) if steel else ()),
        a("audience", "Audience", WOMENS),
    )  # fmt: skip
    sizes = tuple((cm, price + i) for i, cm in enumerate(LENGTHS))
    return ARow(code, title, brand, CLOTHING, PATH, PTYPE, price, "anklet", desc, colors, attrs, sizes,
                size_key="length_cm", params=(("style", style),), metals=tuple(table[c[0]] for c in colors))  # fmt: skip


SPEC = TypeSpec(
    key="anklet",
    department="Clothing",
    product_type=PTYPE,
    derivable=True,
    owners=OWNED,
    apparel_exempt="jewellery: the color is the metal finish, not a printed or dyed color; it carries its own decoys (gen#1113)",
    rows=(
        _row("ANKCHN", "Fine Chain Anklet", WRENFIELD, 11.0,
             "A fine chain for the ankle with a lobster clasp and an extender.", "chain", "Chain"),
        _row("ANKBED", "Beaded Anklet", LARKMOOR, 12.0,
             "Small polished beads strung round the ankle, with a lobster clasp and an extender.", "beaded", "Beaded"),
        _row("ANKCHM", "Disc Charm Anklet", HARBOUR, 14.0,
             "Small round discs hung round the ankle, with a lobster clasp and an extender.", "charm", "Charm"),
        _row("ANKDBL", "Double Chain Anklet", TIDEWELL, 16.0,
             "Two fine chains worn one above the other, joined at one clasp with an extender.", "double", "Double"),
        _row("ANKSTC", "Stainless Steel Chain Anklet", SKERRY, 10.0,
             "A stainless steel chain for sensitive skin that can be worn in the sea, with an extender.", "chain", "Chain", steel=True),
        _row("ANKSTB", "Beaded Stainless Steel Anklet", CALDERBY, 13.0,
             "Polished stainless steel beads for sensitive skin, with a lobster clasp and an extender.", "beaded", "Beaded", steel=True),
    ),
    decoys=(
        Decoy(5, "gold anklet", "color",
              _row("ANKDGT", "Chain Anklet with a Tone Clasp", LARKMOOR, 10.0,
                   "A sterling silver chain for the ankle on a gold tone clasp: the chain itself is silver.", "chain", "Chain",
                   colors=(SILVER,))),
        Decoy(6, "charm anklet", "category",
              _row("ANKDPL", "Plain Link Anklet", HARBOUR, 9.0,
                   "A plain chain for the ankle with a ring to hang a charm from; no charm is included.", "chain", "Chain",
                   colors=(SILVER,))),
    ),
)  # fmt: skip
