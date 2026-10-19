"""Boys' suits (gen#215): a jacket and trousers, with a waistcoat for the three piece, in age sizes.

:mod:`kit_suit_sets` draws them: the number of pieces (two or three) and the fit (slim or
regular) are shape params, so a three piece draws its waistcoat and a slim fit is cut closer.
Each record states what its drawing shows (``piece_count``, ``fit``). The styles are templates
only (``derivable`` False).
"""

from __future__ import annotations

import kit_suit_sets  # noqa: F401 -- registers boys_suit
from type_registry import ApparelPlan, LRow, TypeSpec, a, count, cw

PRODUCT_TYPE = "Boys Suit"
PATH = ("Kids", "Boys", "Suits")
AGES = ("3-4 Yrs", "5-6 Yrs", "7-8 Yrs", "9-10 Yrs", "11-12 Yrs", "13-14 Yrs")
HEX = {
    "Navy": "#26365c", "Black": "#2f2f35", "Charcoal": "#4a4a50", "White": "#f4f4f4",
    "Stone": "#bdb5a6", "Blue": "#2f6fb5", "Red": "#c8312e", "Green": "#2f7a46",
    "Burgundy": "#6d1f2f", "Yellow": "#f2d14b", "Grey": "#9a9a9a",
}  # fmt: skip
_OCC = {
    "BYS01": "School Events", "BYS02": "Smart Casual", "BYS03": "Wedding",
    "BYS04": "Smart Casual", "BYS05": "Party", "BYS06": "School Events",
}  # fmt: skip


def _row(code, brand, fabric, pieces, fit, price, colors, desc):
    return LRow(
        code, f"Boys {pieces} Piece {fit} Fit {fabric} Suit", brand, "Clothing", PATH,
        PRODUCT_TYPE, price, "boys_suit", desc, tuple(cw(c, HEX[c]) for c in colors),
        (a("fit", "Fit", fit), a("fabric", "Fabric", fabric),
         count("piece_count", "Piece count", pieces), a("occasion", "Occasion", _OCC[code])),
        tuple((n, round(price + 3.0 * k, 2)) for k, n in enumerate(AGES)),
        params=(("pieces", str(pieces)), ("fit", fit.lower())),
        audience="kids",
        facts=(("size_range", ["regular"]), ("pattern", "plain")),
    )  # fmt: skip


_STYLES = (
    ("BYS01", "Little Fernby", "Polyester", 2, "Slim", 34.0,
     ("Navy", "Black", "Grey"), "a slim jacket and trousers for school events"),
    ("BYS02", "Harbour & Pine", "Wool", 3, "Regular", 52.0,
     ("Charcoal", "Navy", "Black"), "a jacket, trousers and waistcoat for the whole day"),
    ("BYS03", "Wrenfield", "Cotton", 3, "Slim", 46.0,
     ("White", "Blue", "Stone"), "a wedding suit with a jacket, trousers and waistcoat"),
    ("BYS04", "Little Fernby", "Linen", 2, "Regular", 38.0,
     ("Stone", "Blue", "Green"), "a light summer suit with a jacket and trousers"),
    ("BYS05", "Bramblewood", "Velvet", 3, "Slim", 58.0,
     ("Burgundy", "Red", "Green"), "a velvet party suit with a jacket, trousers and waistcoat"),
    ("BYS06", "Wrenfield", "Cotton", 2, "Slim", 36.0,
     ("Yellow", "Navy", "White"), "a cotton suit with a jacket and trousers"),
)  # fmt: skip

SPEC = TypeSpec(
    key="boys_suit",
    department="Clothing",
    product_type=PRODUCT_TYPE,
    apparel=ApparelPlan(
        compounds=(
            ("sailor", "Sailor Suit"),
            ("tuxedo", "Tuxedo Suit"),
            ("page", "Page Boy Suit"),
        )
    ),
    rows=tuple(
        _row(c, b, f, p, fit, pr, cols, f"{f} suit for boys: {d}, in age sizes.")
        for c, b, f, p, fit, pr, cols, d in _STYLES
    ),
)  # fmt: skip
