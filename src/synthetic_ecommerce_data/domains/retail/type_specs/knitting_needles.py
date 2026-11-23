"""Knitting Needles (gen#1118, cut 2): Office & School > Sewing & Knitting > Knitting Needles.

A breadth type: ``derivable`` True, so the scaled build draws more needles from these four by
the values their titles show (the material and the kind). A needle is sold by its size in
millimeters, the measured ``needle_mm`` SKU axis (``Option("needle_mm", "needle_size", ...)``,
``MMT``): 4, 5 and 6 mm for a straight pair, the sizes a DK to a chunky yarn takes, each a little
dearer than the last. :mod:`size_ladder` draws a thicker needle larger. Each style comes in three
of the six main colors, and the four styles between them carry all six (gen#275): a needle's
color is anodized or molded, and a pair in every color at every size would be 18 SKUs a style.
The drawing shows a crossed pair, two tips on a cable, or a set of four double pointed needles
(:func:`kit_sewing_tools.knitting_needles`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_sewing_tools,  # noqa: F401 -- registers knitting_needles
)
from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLACK,
    BLUE,
    GREEN,
    LANTERNBY,
    RED,
    WHITE,
    YELLOW,
    decoy,
)
from synthetic_ecommerce_data.domains.retail.sewing_rows import (
    DEPARTMENT,
    NEEDLES,
    OWNERS,
    PURLWICK,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec, a

#: A needle's sizes in millimeters and what each adds to the style's price.
SIZES = (("4", 0.0), ("5", 0.5), ("6", 1.0))


def _row(code: str, material: str, needle_type: str, brand: str, colors: tuple, description: str,
         price: float):  # fmt: skip
    attrs = (a("material", "Material", material), a("needle_type", "Needle type", needle_type))
    params = (("needle_type", needle_type.lower()), ("material", material.lower()))
    sizes = tuple((mm, round(price + extra, 2)) for mm, extra in SIZES)
    return row(code, f"{material} {needle_type} Knitting Needles", brand, NEEDLES, "Knitting Needles",
               "knitting_needles", description, attrs, sizes, params, size_key="needle_mm", colors=colors)  # fmt: skip


ROWS = (
    _row(
        "KNNALS",
        "Aluminum",
        "Straight",
        PURLWICK,
        (RED, BLUE, GREEN),
        "A pair of light, smooth 35 cm needles with a tapered point and an end knob, so the stitches slide but never slip off.",
        6.5,
    ),
    _row(
        "KNNPLC",
        "Plastic",
        "Circular",
        LANTERNBY,
        (YELLOW, BLACK, WHITE),
        "Two warm, flexible tips joined by an 80 cm cable that swivels, for knitting hats and sweaters in the round.",
        9.0,
    ),
    _row(
        "KNNADP",
        "Aluminum",
        "Double Pointed",
        PURLWICK,
        (BLUE, YELLOW, RED),
        "A set of four short 20 cm needles pointed at both ends, for socks, mittens and sleeves knitted in the round.",
        8.0,
    ),
    _row(
        "KNNPLS",
        "Plastic",
        "Straight",
        LANTERNBY,
        (GREEN, WHITE, BLACK),
        "A pair of warm, light 30 cm needles that grip the yarn gently, for beginners and slippery yarns.",
        5.0,
    ),
)

SPEC = TypeSpec(
    key="knitting_needles",
    department=DEPARTMENT,
    product_type="Knitting Needles",
    derivable=True,
    owners=OWNERS,
    options=(Option("needle_mm", "needle_size", "Needle size", "MMT"),),
    rows=ROWS,
    decoys=(
        Decoy(4, "green knitting needles", "vocabulary", decoy(ROWS[0], "KNNGEC", "Aluminum Straight Knitting Needles with Green End Caps",
              "A blue pair of needles whose end knobs are capped in a soft rubber.", BLUE)),
        Decoy(6, "white knitting needles", "generic", decoy(ROWS[3], "KNNWSW", "White Swan Plastic Straight Knitting Needles",
              "From the White Swan range: a pair of plastic needles in a bright red.", RED)),
    ),
)  # fmt: skip
