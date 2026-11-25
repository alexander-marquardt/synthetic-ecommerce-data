"""Stud Earrings (gen#1113): a Womens jewellery type beside the hoop and drop earrings.

Each style is a pair of studs in one to three metals (the color is the metal, as for every jewelry
row since gen#207). ``stud`` is drawn by :mod:`kit_jewellery`: a ball, a gem, a pearl or a knot, so
a title that says "pearl" or "sapphire" is a drawing that shows it. A stone style states its
``stone``, which a shopper filters on. The two decoys carry the word "stud" and a query word their
fields contradict.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.jewellery_rows import (
    ALL_METALS,
    CALDERBY,
    GOLD,
    HARBOUR,
    LARKMOOR,
    OWNED,
    ROSE_GOLD,
    SILVER,
    SKERRY,
    TIDEWELL,
    WRENFIELD,
    a,
    earrings_row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

LEAF, PTYPE = ("Earrings", "Stud Earrings"), "Stud Earrings"
STYLE = a("earring_style", "Earring style", "Stud")


def _row(code, title, brand, price, desc, stud, stone=None, **kw):
    params = (("stud", stud), *((("stone", stone.lower()),) if stone and stud == "gem" else ()))
    return earrings_row(code, title, brand, price, desc, "stud_earrings", LEAF, PTYPE, STYLE, params, stone=stone, **kw)


SPEC = TypeSpec(
    key="stud_earrings",
    department="Clothing",
    product_type=PTYPE,
    derivable=True,
    owners=OWNED,
    apparel_exempt="jewellery: the color is the metal finish, not a printed or dyed color; it carries its own decoys (gen#1113)",
    rows=(
        _row("STDBAL", "Polished Ball Stud Earrings", WRENFIELD, 9.0,
             "Small polished ball studs on a fine post with a butterfly back, made to wear every day.", "ball"),
        _row("STDCZR", "Cubic Zirconia Stud Earrings", LARKMOOR, 12.0,
             "Round cubic zirconia studs in a metal bezel, on a post with a butterfly back.", "gem", "Cubic Zirconia"),
        _row("STDPRL", "Freshwater Pearl Stud Earrings", HARBOUR, 18.0,
             "A freshwater pearl on each stud, set in a small metal cup on a post with a butterfly back.", "pearl", "Pearl",
             colors=(GOLD, SILVER)),
        _row("STDKNT", "Love Knot Stud Earrings", TIDEWELL, 11.0,
             "Studs shaped as a small love knot of polished wire, on a post with a butterfly back.", "knot"),
        _row("STDSPH", "Sapphire Stud Earrings", SKERRY, 24.0,
             "A faceted sapphire on each stud in a round bezel. Sapphire is the birthstone for September.", "gem", "Sapphire",
             colors=(GOLD, SILVER)),
        _row("STDAME", "Amethyst Stud Earrings", CALDERBY, 22.0,
             "A faceted amethyst on each stud in a round bezel. Amethyst is the birthstone for February.", "gem", "Amethyst",
             colors=(SILVER, ROSE_GOLD)),
        _row("STDEMD", "Emerald Stud Earrings", WRENFIELD, 26.0,
             "A faceted emerald on each stud in a round bezel. Emerald is the birthstone for May.", "gem", "Emerald",
             colors=(GOLD, SILVER)),
        _row("STDSTL", "Stainless Steel Ball Stud Earrings", HARBOUR, 7.0,
             "Polished ball studs in stainless steel for sensitive ears, on a post with a butterfly back.", "ball",
             steel=True, colors=ALL_METALS),
    ),
    decoys=(
        Decoy(5, "gold stud earrings", "color",
              _row("STDDGT", "Two Tone Ball Stud Earrings", WRENFIELD, 8.0,
                   "Sterling silver ball studs on a gold tone butterfly back: the stud itself is silver.", "ball",
                   colors=(SILVER,))),
        Decoy(6, "pearl stud earrings", "category",
              _row("STDDPB", "Pearl Effect Bead Stud Earrings", LARKMOOR, 6.0,
                   "Studs with a glass bead in a pearl effect finish on a fine post: a bead, not a real pearl.", "pearl", "Glass Bead",
                   colors=(SILVER,))),
    ),
)  # fmt: skip
