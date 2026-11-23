"""Bangle (gen#1113): a rigid Womens bracelet, sold by metal and by size.

A bangle is a closed rigid round that slips over the hand, so it sits under ``Bracelets`` as
``Bangles``. Each SKU is a metal (the color is the metal, as for every jewelry row since gen#207)
times a size (Small, Medium, Large: the inner round that fits the hand). ``style`` is drawn by
:mod:`kit_jewellery` (plain, hammered, twisted, a stacked set of three), so a title that says
"hammered" or "twisted" is a drawing that shows it. The two decoys carry the word "bangle".
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.accessory_rows import ARow
from synthetic_ecommerce_data.domains.retail.audience import WOMENS
from synthetic_ecommerce_data.domains.retail.jewellery_rows import (
    ALL_METALS,
    CALDERBY,
    CLOTHING,
    GOLD,
    HARBOUR,
    LARKMOOR,
    METALS,
    OWNED,
    ROSE_GOLD,
    SILVER,
    SKERRY,
    STEEL,
    TIDEWELL,
    WRENFIELD,
    a,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

PATH, PTYPE = ("Womens", "Jewellery", "Bracelets", "Bangles"), "Bangle"
#: A bangle's sizes: the inner round, from a slim hand to a broad one, each a little dearer.
SIZES = ("Small", "Medium", "Large")


def _row(code, title, brand, price, desc, style, kind, colors=ALL_METALS, steel=False, pieces=0):
    table = STEEL if steel else METALS
    attrs = (
        a("bangle_style", "Bangle style", kind), *(a("metal", "Metal", table[c[0]]) for c in colors),
        *((a("piece_count", "Piece count", str(pieces)),) if pieces else ()),
        *((a("hypoallergenic", "Hypoallergenic", "Yes"),) if steel else ()),
        a("audience", "Audience", WOMENS),
    )  # fmt: skip
    sizes = tuple((s, price + i) for i, s in enumerate(SIZES))
    return ARow(code, title, brand, CLOTHING, PATH, PTYPE, price, "bangle", desc, colors, attrs, sizes,
                params=(("style", style),), metals=tuple(table[c[0]] for c in colors))  # fmt: skip


SPEC = TypeSpec(
    key="bangle",
    department="Clothing",
    product_type=PTYPE,
    owners=OWNED,
    apparel_exempt="jewellery: the color is the metal finish, not a printed or dyed color; it carries its own decoys (gen#1113)",
    rows=(
        _row("BNGPLN", "Polished Plain Bangle", WRENFIELD, 12.0,
             "A smooth rigid bangle with a polished finish that slips over the hand.", "plain", "Plain"),
        _row("BNGHAM", "Hammered Bangle", LARKMOOR, 15.0,
             "A rigid bangle with a hand hammered surface of small dimples that catch the light.", "hammered", "Hammered",
             colors=(GOLD, SILVER)),
        _row("BNGTWS", "Twisted Rope Bangle", HARBOUR, 16.0,
             "A rigid bangle in a twisted rope of metal that slips over the hand.", "twisted", "Twisted",
             colors=(GOLD, ROSE_GOLD)),
        _row("BNGSTK", "Set of Three Stacking Bangles", TIDEWELL, 19.0,
             "Three slim polished bangles to wear stacked together or one at a time.", "stacked", "Stacking",
             pieces=3),
        _row("BNGSTL", "Stainless Steel Bangle", SKERRY, 10.0,
             "A polished stainless steel bangle for sensitive skin, rigid and light to wear.", "plain", "Plain",
             colors=(GOLD, SILVER), steel=True),
        _row("BNGTW2", "Twisted Stainless Steel Bangle", CALDERBY, 13.0,
             "A rigid bangle in a twisted rope of stainless steel, for sensitive skin.", "twisted", "Twisted",
             colors=(GOLD, SILVER, ROSE_GOLD), steel=True),
    ),
    decoys=(
        Decoy(5, "gold bangle", "color",
              _row("BNGDGT", "Polished Bangle with a Tone Band", WRENFIELD, 11.0,
                   "A sterling silver bangle with one thin gold tone band: the bangle itself is silver.", "plain", "Plain",
                   colors=(SILVER,))),
        Decoy(6, "stacking bangles", "category",
              _row("BNGDSG", "Wide Single Bangle", HARBOUR, 14.0,
                   "One wide polished bangle with the look of a stacking set, sold on its own.", "plain", "Plain",
                   colors=(SILVER,))),
    ),
)  # fmt: skip
