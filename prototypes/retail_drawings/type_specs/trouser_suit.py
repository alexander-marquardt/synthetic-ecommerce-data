"""Women's trouser suits (gen#215): a jacket and trousers cut from one cloth, sold as a set.

:mod:`kit_suit_sets` draws them: the jacket style (single breasted, double breasted or
collarless) and the trouser leg (slim, straight or wide) are shape params, so two styles that
differ on either draw differently. Each record states what its drawing shows (``jacket_style``,
``leg_fit``, ``piece_count``). The styles are templates only (``derivable`` False).
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import kit_suit_sets  # noqa: F401 -- registers trouser_suit
from type_registry import ApparelPlan, LRow, TypeSpec, a, count, cw, sizes

PRODUCT_TYPE = "Trouser Suit"
PATH = ("Womens", "Suits & Tailoring", "Trouser Suits")
UK = ("8", "10", "12", "14", "16", "18")
HEX = {
    "Navy": "#26365c", "Black": "#2f2f35", "Charcoal": "#4a4a50", "White": "#f4f4f4",
    "Stone": "#bdb5a6", "Blue": "#2f6fb5", "Red": "#c8312e", "Green": "#2f7a46",
    "Burgundy": "#6d1f2f", "Yellow": "#f2d14b", "Cream": "#efe4cf",
}  # fmt: skip
_JACKET = {"Single Breasted": "single", "Double Breasted": "double", "Collarless": "collarless"}
_LEG = {"Slim": "slim", "Straight": "straight", "Wide": "wide"}
_OCC = {
    "TRS01": "Workwear", "TRS02": "Smart Casual", "TRS03": "Evening", "TRS04": "Smart Casual",
    "TRS05": "Workwear", "TRS06": "Evening", "TRS07": "Smart Casual", "TRS08": "Wedding Guest",
}  # fmt: skip


def _row(code, brand, fabric, jacket, leg, price, colors, desc):
    title = f"Womens {fabric} {jacket} {leg} Leg Trouser Suit"
    return LRow(
        code, title, brand, "Clothing", PATH, PRODUCT_TYPE, price, "trouser_suit", desc,
        tuple(cw(c, HEX[c]) for c in colors),
        (a("jacket_style", "Jacket style", jacket), a("leg_fit", "Leg fit", leg),
         a("fabric", "Fabric", fabric), count("piece_count", "Piece count", 2),
         a("occasion", "Occasion", _OCC[code])),
        sizes(price, UK),
        params=(("jacket", _JACKET[jacket]), ("fit", _LEG[leg])),
        facts=(("size_range", ["regular"]), ("pattern", "plain")),
    )  # fmt: skip


_STYLES = (
    ("TRS01", "Calderby & Lune", "Wool", "Single Breasted", "Straight", 95.0,
     ("Navy", "Black", "Charcoal"), "a fitted jacket with notch lapels and straight leg trousers"),
    ("TRS02", "Bramblewood", "Linen", "Single Breasted", "Wide", 79.0,
     ("White", "Stone", "Blue"), "a relaxed linen jacket with wide leg trousers for summer"),
    ("TRS03", "Larkmoor", "Polyester", "Double Breasted", "Slim", 89.0,
     ("Black", "Red", "Green"), "a double breasted blazer with slim, cropped trousers"),
    ("TRS04", "Wrenfield", "Suiting", "Collarless", "Wide", 85.0,
     ("Yellow", "Blue", "Black"), "a collarless jacket that fastens to the neck with wide trousers"),
    ("TRS05", "Harbour & Pine", "Wool", "Double Breasted", "Straight", 110.0,
     ("Green", "Burgundy", "Charcoal"), "a heritage wool double breasted jacket and straight trousers"),
    ("TRS06", "Calderby & Lune", "Velvet", "Single Breasted", "Slim", 99.0,
     ("Burgundy", "Black", "Green"), "a velvet evening jacket with slim tapered trousers"),
    ("TRS07", "Bramblewood", "Cotton", "Collarless", "Straight", 72.0,
     ("Stone", "White", "Red"), "a collarless cotton jacket and straight trousers"),
    ("TRS08", "Larkmoor", "Polyester", "Double Breasted", "Wide", 92.0,
     ("Navy", "Red", "White"), "a double breasted jacket with wide leg trousers"),
)  # fmt: skip

SPEC = TypeSpec(
    key="trouser_suit",
    department="Clothing",
    product_type=PRODUCT_TYPE,
    apparel=ApparelPlan(
        compounds=(
            ("tuxedo", "Tuxedo Trouser Suit"),
            ("waistcoat", "Waistcoat Trouser Suit"),
            ("culotte", "Culotte Trouser Suit"),
        )
    ),
    rows=tuple(
        _row(c, b, f, j, lg, p, cols,
             f"{f} trouser suit: {d}. The jacket and the trousers are cut from one cloth.")
        for c, b, f, j, lg, p, cols, d in _STYLES
    ),
)  # fmt: skip
