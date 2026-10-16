"""Hoop Earrings (gen#423): a new Womens jewellery type beside the legacy ``Earrings``.

Each style is a pair of hoops in one to three metals (the color is the metal, as for every
jewelry row since gen#207). ``size`` and ``band`` are drawn by :mod:`kit_jewellery`, so a title
that says "twisted" or "large" is a drawing that shows it. The two decoys carry the word "hoop"
in their text and are not hoop earrings by their fields.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from jewellery_rows import (
    ALL_METALS,
    GOLD,
    HARBOUR,
    LARKMOOR,
    OWNED,
    ROSE_GOLD,
    SILVER,
    TIDEWELL,
    WRENFIELD,
    a,
    earrings_row,
)
from type_registry import Decoy, TypeSpec

LEAF, PTYPE = "Hoop Earrings", "Hoop Earrings"
STYLE = a("earring_style", "Earring style", "Hoop")


def _row(code, title, brand, price, desc, size, band, **kw):
    return earrings_row(code, title, brand, price, desc, "hoop_earrings", LEAF, PTYPE, STYLE, (("size", size), ("band", band)), **kw)


SPEC = TypeSpec(
    key="hoop_earrings",
    department="Clothing",
    product_type=PTYPE,
    owners=OWNED,
    apparel_exempt="jewellery: the color is the metal finish, not a printed or dyed color; it carries its own decoys (gen#423)",
    rows=(
        _row("HPEMED", "Classic Hoop Earrings", WRENFIELD, 14.0,
             "Smooth medium hoop earrings with a hinged post closure, light enough for all day.", "medium", "plain"),
        _row("HPESML", "Small Huggie Hoop Earrings", LARKMOOR, 11.0,
             "Small hoops that sit close to the lobe, with a hinged snap closure.", "small", "plain"),
        _row("HPELRG", "Large Statement Hoop Earrings", TIDEWELL, 19.0,
             "Large hoop earrings with a bold, polished wire and a post and butterfly fastening.", "large", "plain",
             colors=(GOLD, SILVER)),
        _row("HPETWT", "Twisted Rope Hoop Earrings", HARBOUR, 17.0,
             "Medium hoop earrings in a twisted rope wire that catches the light.", "medium", "twisted",
             colors=(GOLD, ROSE_GOLD)),
        _row("HPEBED", "Beaded Hoop Earrings", LARKMOOR, 21.0,
             "Fine hoop earrings strung with small round beads, in stainless steel for sensitive ears.", "medium", "beaded",
             steel=True, colors=ALL_METALS),
    ),
    decoys=(
        Decoy(5, "gold hoop earrings", "color",
              _row("HPEDHG", "Sleeper Earrings", WRENFIELD, 10.0,
                   "Tiny sleeper earrings that hug the lobe like a hoop, with a gold tone hinge on a silver wire.", "small", "plain",
                   colors=(SILVER,))),
        Decoy(6, "hoop earrings", "category",
              _row("HPEDWR", "Twisted Wire Earrings", HARBOUR, 9.0,
                   "Open twisted wire earrings with a hoop look that fasten with a fish hook instead of a hinge.", "small", "twisted",
                   colors=(SILVER,))),
    ),
)  # fmt: skip
