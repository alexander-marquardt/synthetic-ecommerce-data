"""Jewellery Set (gen#1113): a matching necklace and earrings, or a set of three with a bracelet.

It sits under ``Jewellery`` as ``Jewellery Sets``. Each SKU is a metal (the color is the metal, as
for every jewelry row since gen#207). ``set_contents`` names the pieces and ``piece_count`` counts
them; :mod:`kit_jewellery` draws the same pieces (``pieces``), each showing the set's ``motif``: a
polished disc, a heart, a pearl, or a set ``stone`` the row states. The rows are derivable, and a
derived style keeps its template's pieces, motif and stone (``scale_text.JEWELLERY_KEYS``).
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
    SILVER,
    SKERRY,
    STEEL,
    TIDEWELL,
    WRENFIELD,
    a,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

PATH, PTYPE = ("Womens", "Jewellery", "Jewellery Sets"), "Jewellery Set"
CONTENTS = {"2": "Necklace and Earrings", "3": "Necklace, Earrings and Bracelet"}
MOTIFS = {"plain": "Polished Disc", "heart": "Heart", "pearl": "Pearl", "stone": "Stone"}


def _row(code, title, brand, price, desc, motif, pieces, colors=ALL_METALS, steel=False, stone=None):
    table = STEEL if steel else METALS
    attrs = (
        a("set_contents", "Set contents", CONTENTS[pieces]), ("piece_count", "Piece count", pieces, "C62"),
        a("set_style", "Set style", MOTIFS[motif]), *(a("metal", "Metal", table[c[0]]) for c in colors),
        *((a("stone", "Stone", stone),) if stone else ()),
        *((a("hypoallergenic", "Hypoallergenic", "Yes"),) if steel else ()),
        a("audience", "Audience", WOMENS),
    )  # fmt: skip
    params = (("pieces", pieces), ("motif", motif), *((("stone", stone.lower()),) if motif == "stone" else ()))
    return ARow(code, title, brand, CLOTHING, PATH, PTYPE, price, "jewellery_set", desc, colors, attrs,
                params=params, metals=tuple(table[c[0]] for c in colors))  # fmt: skip


#: A stone set: the stone, its pieces, its price and its brand.
STONE_SETS = (
    ("Cubic Zirconia", "2", 28.0, WRENFIELD), ("Sapphire", "2", 36.0, SKERRY),
    ("Emerald", "3", 45.0, CALDERBY), ("Ruby", "2", 36.0, HARBOUR), ("Amethyst", "3", 42.0, LARKMOOR),
)  # fmt: skip

SPEC = TypeSpec(
    key="jewellery_set",
    department="Clothing",
    product_type=PTYPE,
    derivable=True,
    owners=OWNED,
    apparel_exempt="jewellery: the color is the metal finish, not a printed or dyed color; it carries its own decoys (gen#1113)",
    rows=(
        _row("JSTDSC", "Polished Disc Necklace and Earrings Set", WRENFIELD, 24.0,
             "A matching set: a polished disc pendant on a fine chain and a pair of disc drop earrings, boxed as a gift.", "plain", "2"),
        _row("JSTDS3", "Polished Disc Jewellery Set of Three", HARBOUR, 32.0,
             "A matching necklace, a pair of drop earrings and a chain bracelet, each with a polished disc, boxed as a gift.", "plain", "3"),
        _row("JSTHRT", "Heart Necklace and Earrings Set", LARKMOOR, 26.0,
             "A heart pendant on a fine chain with a pair of matching heart drop earrings, boxed as a gift.", "heart", "2"),
        _row("JSTHR3", "Heart Jewellery Set of Three", TIDEWELL, 34.0,
             "A heart pendant necklace, a pair of heart drop earrings and a chain bracelet with a heart charm, boxed as a gift.", "heart", "3"),
        _row("JSTHST", "Stainless Steel Heart Necklace and Earrings Set", TIDEWELL, 19.0,
             "A stainless steel heart pendant and matching heart drop earrings for sensitive skin, a set that does not tarnish.", "heart", "2", steel=True),
        _row("JSTPRL", "Pearl Necklace and Earrings Set", CALDERBY, 29.0,
             "A freshwater pearl pendant on a fine chain and a pair of matching pearl drop earrings, boxed as a gift.", "pearl", "2", stone="Pearl"),
        _row("JSTPR3", "Pearl Bridal Jewellery Set of Three", SKERRY, 39.0,
             "A freshwater pearl necklace, a pair of pearl drop earrings and a chain bracelet with a pearl, for a wedding day.", "pearl", "3", stone="Pearl"),
        *(_row(f"JSTS{i:02d}", f"{stone} {'Necklace and Earrings Set' if pieces == '2' else 'Jewellery Set of Three'}", brand, price,
               f"A matching set with a faceted {stone.lower()} in a round setting on each piece: "
               + ("a pendant necklace and a pair of drop earrings." if pieces == "2" else "a pendant necklace, a pair of drop earrings and a chain bracelet."),
               "stone", pieces, stone=stone)
          for i, (stone, pieces, price, brand) in enumerate(STONE_SETS, 1)),
    ),
    decoys=(
        Decoy(5, "gold jewellery set", "color",
              _row("JSTDGT", "Necklace and Earrings Set with Gold Tone Hearts", LARKMOOR, 26.0,
                   "A sterling silver necklace and earrings set whose hearts carry a thin gold tone edge: the set itself is silver.", "heart", "2",
                   colors=(SILVER,))),
        Decoy(4, "bracelet", "category",
              _row("JSTDBR", "Necklace and Earrings Set to Match a Bracelet", HARBOUR, 24.0,
                   "A disc pendant necklace and a pair of disc earrings made to match a disc bracelet: the bracelet is not included.", "plain", "2",
                   colors=(GOLD,))),
    ),
)  # fmt: skip
