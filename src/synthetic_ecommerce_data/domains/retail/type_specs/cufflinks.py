"""Cufflinks (gen#1113): the first Mens jewellery type, under ``Mens > Jewellery``.

Each style is a pair of cufflinks in one to three metals (the color is the metal, as for every
jewelry row since gen#207), on a swivel bar. ``face`` is drawn by :mod:`kit_jewellery` (a round or
square plate, a knot, a stone inlay), so a title that says "onyx" or "square" is a drawing that
shows it. A stone style states its ``stone``. The two decoys carry the word "cufflinks".
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.accessory_rows import ARow
from synthetic_ecommerce_data.domains.retail.audience import MENS
from synthetic_ecommerce_data.domains.retail.jewellery_rows import (
    ALL_METALS,
    CALDERBY,
    CLOTHING,
    GOLD,
    HARBOUR,
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

PATH, PTYPE = ("Mens", "Jewellery", "Cufflinks"), "Cufflinks"


def _row(code, title, brand, price, desc, face, kind, colors=(GOLD, SILVER), steel=False, stone=None):
    table = STEEL if steel else METALS
    attrs = (
        a("cufflink_style", "Cufflink style", kind), *(a("metal", "Metal", table[c[0]]) for c in colors),
        *((a("stone", "Stone", stone),) if stone else ()),
        a("fastening", "Fastening", "Swivel Bar"), a("audience", "Audience", MENS),
    )  # fmt: skip
    params = (("face", face), *((("stone", stone.lower()),) if stone else ()))
    return ARow(code, title, brand, CLOTHING, PATH, PTYPE, price, "cufflinks", desc, colors, attrs,
                params=params, metals=tuple(table[c[0]] for c in colors))  # fmt: skip


SPEC = TypeSpec(
    key="cufflinks",
    department="Clothing",
    product_type=PTYPE,
    owners=OWNED,
    apparel_exempt="jewellery: the color is the metal finish, not a printed or dyed color; it carries its own decoys (gen#1113)",
    rows=(
        _row("CUFRND", "Classic Round Cufflinks", CALDERBY, 22.0,
             "A pair of round polished cufflinks on a swivel bar, for a double cuff shirt.", "round", "Round",
             steel=True),
        _row("CUFSQR", "Square Plate Cufflinks", WRENFIELD, 24.0,
             "A pair of square cufflinks with a framed polished face, on a swivel bar.", "square", "Square",
             colors=ALL_METALS),
        _row("CUFKNT", "Knot Cufflinks", HARBOUR, 26.0,
             "A pair of cufflinks shaped as a round knot of polished metal, on a swivel bar.", "knot", "Knot"),
        _row("CUFONX", "Onyx Cufflinks", SKERRY, 32.0,
             "A pair of cufflinks with an onyx inlay in a polished frame, on a swivel bar.", "stone", "Stone Inlay",
             stone="Onyx"),
        _row("CUFLAP", "Lapis Lazuli Cufflinks", TIDEWELL, 36.0,
             "A pair of cufflinks with a lapis lazuli inlay in a polished frame, on a swivel bar.", "stone", "Stone Inlay",
             stone="Lapis Lazuli"),
        _row("CUFSTL", "Stainless Steel Square Cufflinks", TIDEWELL, 15.0,
             "A pair of square stainless steel cufflinks with a framed face, on a swivel bar.", "square", "Square",
             colors=ALL_METALS, steel=True),
    ),
    decoys=(
        Decoy(5, "silver cufflinks", "color",
              _row("CUFDGD", "Polished Round Cufflinks", WRENFIELD, 20.0,
                   "Gold plated round cufflinks on a silver tone swivel bar: the face itself is gold.", "round", "Round",
                   colors=(GOLD,))),
        Decoy(4, "onyx cufflinks", "category",
              _row("CUFDEN", "Enamel Inlay Cufflinks", HARBOUR, 18.0,
                   "Cufflinks with a painted enamel inlay in an onyx look: enamel, not a stone.", "stone", "Enamel Inlay",
                   colors=(SILVER,))),
    ),
)  # fmt: skip
