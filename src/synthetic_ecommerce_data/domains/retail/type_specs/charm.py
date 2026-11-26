"""Charm (gen#1113): one charm for a charm bracelet, sold by metal.

It sits under ``Jewellery`` as ``Charms``. Each SKU is a metal (the color is the metal, as for
every jewelry row since gen#207). ``motif`` is drawn by :mod:`kit_jewellery`: an outline on a
lobster clasp (heart, star, moon, cross, a lucky four leaf, a paw print), a stone in a round
setting, or a bead threaded on the bracelet's strand, so ``fastening`` follows the motif. A
birthstone charm states its ``stone`` and its ``birthstone`` month, and its drawing takes the
stone. The rows are derivable, and a derived style keeps its template's motif and stone
(``scale_text.JEWELLERY_KEYS``).
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

PATH, PTYPE = ("Womens", "Jewellery", "Charms"), "Charm"
#: A birthstone, its month, its price and its brand.
BIRTHSTONES = (
    ("Garnet", "January", 14.0, TIDEWELL), ("Amethyst", "February", 14.0, WRENFIELD),
    ("Aquamarine", "March", 15.0, LARKMOOR), ("Emerald", "May", 18.0, CALDERBY),
    ("Ruby", "July", 18.0, HARBOUR), ("Sapphire", "September", 18.0, SKERRY),
)  # fmt: skip


def _row(code, title, brand, price, desc, motif, kind, colors=ALL_METALS, steel=False, stone=None, month=None):
    table = STEEL if steel else METALS
    attrs = (
        a("charm_style", "Charm style", kind), *(a("metal", "Metal", table[c[0]]) for c in colors),
        *((a("stone", "Stone", stone),) if stone else ()),
        *((a("birthstone", "Birthstone", month),) if month else ()),
        a("fastening", "Fastening", "Threaded" if motif == "bead" else "Lobster Clasp"),
        *((a("hypoallergenic", "Hypoallergenic", "Yes"),) if steel else ()),
        a("audience", "Audience", WOMENS),
    )  # fmt: skip
    params = (("motif", motif), *((("stone", stone.lower()),) if motif == "stone" else ()))
    return ARow(code, title, brand, CLOTHING, PATH, PTYPE, price, "charm", desc, colors, attrs,
                params=params, metals=tuple(table[c[0]] for c in colors))  # fmt: skip


SPEC = TypeSpec(
    key="charm",
    department="Clothing",
    product_type=PTYPE,
    derivable=True,
    owners=OWNED,
    apparel_exempt="jewellery: the color is the metal finish, not a printed or dyed color; it carries its own decoys (gen#1113)",
    rows=(
        _row("CHMHRT", "Heart Charm", WRENFIELD, 9.0,
             "A polished heart charm on a lobster clasp that clips onto a charm bracelet.", "heart", "Heart"),
        _row("CHMSTR", "Star Charm", LARKMOOR, 9.0,
             "A five pointed star charm on a lobster clasp that clips onto a charm bracelet.", "star", "Star"),
        _row("CHMMON", "Crescent Moon Charm", HARBOUR, 9.0,
             "A slim crescent moon charm on a lobster clasp that clips onto a charm bracelet.", "moon", "Moon"),
        _row("CHMCRS", "Cross Charm", CALDERBY, 9.0,
             "A plain cross charm with a polished finish on a lobster clasp, a gift for a christening.", "cross", "Cross"),
        _row("CHMCLV", "Lucky Four Leaf Charm", TIDEWELL, 10.0,
             "A four leaf charm for luck, on a lobster clasp that clips onto a charm bracelet.", "clover", "Four Leaf"),
        _row("CHMPAW", "Paw Print Charm", SKERRY, 10.0,
             "A paw print charm for a pet lover, on a lobster clasp that clips onto a charm bracelet.", "paw", "Paw Print"),
        _row("CHMBED", "Barrel Bead Charm", WRENFIELD, 8.0,
             "A polished barrel bead charm with two grooves that threads onto a bead charm bracelet.", "bead", "Bead"),
        _row("CHMHST", "Stainless Steel Heart Charm", TIDEWELL, 7.0,
             "A polished stainless steel heart charm for sensitive skin, on a lobster clasp that does not tarnish.", "heart", "Heart", steel=True),
        *(_row(f"CHMB{i:02d}", f"{stone} Birthstone Charm", brand, price,
               f"A faceted {stone.lower()} in a round setting on a lobster clasp. {stone} is the birthstone for {month}.",
               "stone", "Birthstone", stone=stone, month=month)
          for i, (stone, month, price, brand) in enumerate(BIRTHSTONES, 1)),
    ),
    decoys=(
        Decoy(5, "gold charm", "color",
              _row("CHMDGT", "Heart Charm with a Gold Tone Edge", LARKMOOR, 9.0,
                   "A sterling silver heart charm with a thin gold tone edge: the charm itself is silver.", "heart", "Heart",
                   colors=(SILVER,))),
        Decoy(4, "charm bracelet", "category",
              _row("CHMDBR", "Star Charm for a Charm Bracelet", HARBOUR, 9.0,
                   "One star charm on a lobster clasp to add to a charm bracelet: the bracelet is not included.", "star", "Star",
                   colors=(GOLD,))),
    ),
)  # fmt: skip
