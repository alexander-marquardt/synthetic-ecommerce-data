"""Pendant (gen#1113): one pendant on a fine chain, sold by metal and by chain length.

It sits under ``Necklaces`` as ``Pendants``. Each SKU is a metal (the color is the metal, as for
every jewelry row since gen#207) times a chain length (``length_cm``: 40, 45 or 50). The charm is
drawn by :mod:`kit_jewellery`; a birthstone pendant states its ``stone`` and its ``birthstone``
month, and its drawing takes the stone. The rows are derivable, and a derived style keeps its
template's charm and stone (``scale_text.JEWELLERY_KEYS``).
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

PATH, PTYPE = ("Womens", "Jewellery", "Necklaces", "Pendants"), "Pendant"
#: The chain lengths, each a little dearer: 16, 18 and 20 inches.
LENGTHS = ("40", "45", "50")
#: A birthstone, its month, and what a customer pays over a plain pendant.
BIRTHSTONES = (
    ("Garnet", "January", 24.0, TIDEWELL), ("Amethyst", "February", 24.0, WRENFIELD),
    ("Aquamarine", "March", 26.0, LARKMOOR), ("Emerald", "May", 32.0, CALDERBY),
    ("Peridot", "August", 25.0, HARBOUR), ("Sapphire", "September", 32.0, SKERRY),
    ("Opal", "October", 27.0, TIDEWELL), ("Topaz", "November", 25.0, LARKMOOR),
    ("Turquoise", "December", 22.0, HARBOUR),
)  # fmt: skip


def _row(code, title, brand, price, desc, charm, kind, colors=ALL_METALS, steel=False, stone=None, month=None):
    table = STEEL if steel else METALS
    attrs = (
        a("pendant_style", "Pendant style", kind), *(a("metal", "Metal", table[c[0]]) for c in colors),
        *((a("stone", "Stone", stone),) if stone else ()),
        *((a("birthstone", "Birthstone", month),) if month else ()),
        *((a("hypoallergenic", "Hypoallergenic", "Yes"),) if steel else ()),
        a("audience", "Audience", WOMENS),
    )  # fmt: skip
    params = (("charm", charm), *((("stone", stone.lower()),) if charm == "stone" else ()))
    sizes = tuple((cm, price + 2 * i) for i, cm in enumerate(LENGTHS))
    return ARow(code, title, brand, CLOTHING, PATH, PTYPE, price, "pendant", desc, colors, attrs, sizes,
                size_key="length_cm", params=params, metals=tuple(table[c[0]] for c in colors))  # fmt: skip


SPEC = TypeSpec(
    key="pendant",
    department="Clothing",
    product_type=PTYPE,
    derivable=True,
    owners=OWNED,
    apparel_exempt="jewellery: the color is the metal finish, not a printed or dyed color; it carries its own decoys (gen#1113)",
    rows=(
        _row("PNDHRT", "Polished Heart Pendant", WRENFIELD, 16.0,
             "A smooth polished heart on a fine chain with a lobster clasp.", "heart", "Heart"),
        _row("PNDSTR", "Star Pendant", LARKMOOR, 15.0,
             "A five pointed star on a fine chain with a lobster clasp.", "star", "Star"),
        _row("PNDMON", "Crescent Moon Pendant", HARBOUR, 17.0,
             "A slim crescent moon on a fine chain with a lobster clasp.", "moon", "Moon"),
        _row("PNDCRS", "Plain Cross Pendant", CALDERBY, 18.0,
             "A plain cross with a polished finish on a fine chain, a gift for a christening.", "cross", "Cross"),
        _row("PNDDSC", "Round Disc Pendant", TIDEWELL, 14.0,
             "A flat round disc with a framed edge on a fine chain, plain on both sides for engraving.", "disc", "Disc"),
        _row("PNDPRL", "Freshwater Pearl Pendant", SKERRY, 21.0,
             "One round freshwater pearl under a small metal cap, on a fine chain.", "pearl", "Pearl", stone="Pearl"),
        _row("PNDCZR", "Cubic Zirconia Pendant", WRENFIELD, 20.0,
             "One faceted cubic zirconia in a round setting on a fine chain.", "stone", "Solitaire", stone="Cubic Zirconia"),
        _row("PNDHST", "Stainless Steel Heart Pendant", TIDEWELL, 12.0,
             "A polished stainless steel heart for sensitive skin, on a fine chain that does not tarnish.", "heart", "Heart", steel=True),
        _row("PNDCST", "Stainless Steel Cross Pendant", SKERRY, 13.0,
             "A polished stainless steel cross for sensitive skin, on a chain that does not tarnish.", "cross", "Cross", steel=True),
        *(_row(f"PNDB{i:02d}", f"{stone} Birthstone Pendant", brand, price,
               f"A faceted {stone.lower()} in a round setting on a fine chain. {stone} is the birthstone for {month}.",
               "stone", "Birthstone", stone=stone, month=month)
          for i, (stone, month, price, brand) in enumerate(BIRTHSTONES, 1)),
    ),
    decoys=(
        Decoy(5, "gold pendant", "color",
              _row("PNDDGT", "Heart Pendant with a Tone Edge", LARKMOOR, 13.0,
                   "A sterling silver heart with a thin gold tone edge: the pendant itself is silver.", "heart", "Heart",
                   colors=(SILVER,))),
        Decoy(6, "pearl pendant", "stone",
              _row("PNDDPB", "Bead Pendant", HARBOUR, 11.0,
                   "A glass bead in a pearl effect finish on a fine chain: a bead, not a real pearl.", "pearl", "Bead",
                   colors=(SILVER,), stone="Glass Bead")),
    ),
)  # fmt: skip
