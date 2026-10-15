"""School uniform for Kids, first increment (gen#205): trousers, skirts, pinafores and shirts.

The catalog had school shoes and school socks and no garment to wear above them, so "school
trousers longer length", "girls pleated school skirt" or "2 pack school shirts" found adult trousers
or nothing. Each type here is a leaf under ``Kids > School Uniform`` with its own drawing
(:mod:`kit_school`), its shopper attributes as structured entries, and SKUs over its colors and the
school ages ("3-4 Yrs" to "15-16 Yrs") the garment is sold in.

========================  =====================================================================
type                      what a shopper filters on (a structured attribute each)
========================  =====================================================================
School Trousers           fit (Regular, Slim, Longer Length, Plus Fit), adjustable waist, pack
School Skirt              style (Pleated, A-Line, Kilt), length, adjustable waist
School Pinafore           style (Pinafore, Jumper Dress), fabric
School Shirt              sleeve length, fit, easy care, pack (1, 2 or 3)
========================  =====================================================================

A pack is what a style is sold as (a "2 Pack" is its own product with its own price), so the pack
count is a product attribute and the drawing of a multipack stacks that many pack items. The
styles are templates only: :func:`scale.derivable` leaves them out (``scale.SCHOOL_IDS``), so the
seeded derivation is what it was. The types carry text-match decoys from :mod:`decoy_apparel`
like every other clothing type, and the six main colors come from :mod:`main_colors`. Not yet
here: polo shirts, socks (one pack style exists in ``class_rows``), blazers, PE shorts and
jumpers or cardigans, which the issue lists next. Every brand is invented.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_school  # noqa: F401 -- registers school_trousers, school_skirt, ...
from breadth_rows import OWNERS, Row
from class_model import BRAND_OWNER
from variants import cw

_BRANDS = ("Little Fernby", "Calderby & Lune", "Bramblewood", "Larkmoor")
OWNERS.update({b: BRAND_OWNER[b] for b in _BRANDS})
LF, CL, BW, LK = _BRANDS

DEPARTMENT = "Clothing"
_BASE = ("Kids", "School Uniform")
_TROUSERS, _SKIRTS = (*_BASE, "School Trousers"), (*_BASE, "School Skirts")
_PINAFORES, _SHIRTS = (*_BASE, "School Pinafores"), (*_BASE, "School Shirts")

#: The school ages, two years a size, from reception to year 11 (the issue's 3-4 to 15-16).
AGES = ("3-4 Yrs", "5-6 Yrs", "7-8 Yrs", "9-10 Yrs", "11-12 Yrs", "13-14 Yrs", "15-16 Yrs")

BLACK = cw("Black", "#2a2a2e")
GREY = cw("Grey", "#9a9ca0")
NAVY = cw("Navy", "#26365c")
CHARCOAL = cw("Charcoal", "#4a4a50")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
BLUE = cw("Blue", "#8fb4dc")
GREEN = cw("Green", "#3f6b4a")
RED = cw("Red", "#9d2a2f")


def _pack(n: int) -> str:
    """A pack as the underwear and socks spell it: Single, 2 pack, 3 pack."""
    return "Single" if n == 1 else f"{n} pack"


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _sizes(price: float, step: float = 0.5) -> tuple[tuple[str, float], ...]:
    """Each age's price: a bigger age costs ``step`` more than the one before."""
    return tuple((a, round(price + step * i, 2)) for i, a in enumerate(AGES))


def _row(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
         shape: str, description: str, colors: tuple, attrs: tuple, params: tuple) -> Row:  # fmt: skip
    return Row(code, title, brand, DEPARTMENT, path, ptype, price, shape, description, colors,
               attrs, _sizes(price), audience="kids", params=params)  # fmt: skip


# --------------------------------------------------------------------------
# Trousers: the leg width (fit) and the hem (length) are drawn; pack and age are not.
# --------------------------------------------------------------------------

_FIT_PARAMS = {
    "Regular": (("fit", "regular"), ("length", "regular")),
    "Slim": (("fit", "slim"), ("length", "regular")),
    "Longer Length": (("fit", "regular"), ("length", "longer")),
    "Plus Fit": (("fit", "plus"), ("length", "regular")),
}


def _trousers(code, title, brand, fit, fabric, adjustable, pack, price, desc, colors) -> Row:
    return _row(code, title, brand, _TROUSERS, "School Trousers", price, "school_trousers", desc,
                colors, (_a("fit", "Fit", fit), _a("fabric", "Fabric", fabric),
                         _a("adjustable_waist", "Adjustable waist", adjustable),
                         _a("pack_size", "Pack size", _pack(pack))), _FIT_PARAMS[fit])  # fmt: skip


TROUSERS = (
    _trousers(
        "SCHSLM",
        "Slim Fit School Trousers",
        LF,
        "Slim",
        "Polyester",
        "Yes",
        1,
        8.0,
        "Slim leg school trousers with a front crease, two pockets and an adjustable waist "
        "that grows with the wearer.",
        (BLACK, GREY, NAVY),
    ),
    _trousers(
        "SCHRGL",
        "Regular Fit School Trousers, 2 Pack",
        CL,
        "Regular",
        "Polyester",
        "No",
        2,
        14.0,
        "Two pairs of straight leg school trousers with a front crease and two pockets, a "
        "pair to wear and a pair in the wash.",
        (BLACK, GREY, CHARCOAL),
    ),
    _trousers(
        "SCHLNG",
        "Longer Length School Trousers",
        BW,
        "Longer Length",
        "Polyester",
        "Yes",
        1,
        10.0,
        "School trousers cut longer in the leg for tall children, with a crease, two "
        "pockets and an adjustable waist.",
        (BLACK, GREY, NAVY),
    ),
    _trousers(
        "SCHPLS",
        "Plus Fit School Trousers",
        LF,
        "Plus Fit",
        "Polyester",
        "Yes",
        1,
        10.0,
        "Roomier school trousers with extra width through the waist and leg, an adjustable "
        "waist and a front crease.",
        (BLACK, GREY, CHARCOAL),
    ),
    _trousers(
        "SCHCTN",
        "Cotton Twill School Trousers, 2 Pack",
        BW,
        "Regular",
        "Cotton",
        "No",
        2,
        16.0,
        "Hard wearing cotton twill school trousers sold as a pair, with a crease and two pockets.",
        (GREY, NAVY, CHARCOAL),
    ),
)

# --------------------------------------------------------------------------
# Skirts: the style is drawn (pleats, A-line, kilt) and so is the length.
# --------------------------------------------------------------------------


def _skirt(code, title, brand, style, fabric, adjustable, length, price, desc, colors) -> Row:
    return _row(code, title, brand, _SKIRTS, "School Skirt", price, "school_skirt", desc, colors,
                (_a("skirt_style", "Skirt style", style), _a("fabric", "Fabric", fabric),
                 _a("adjustable_waist", "Adjustable waist", adjustable),
                 _a("skirt_length", "Skirt length", length)),
                (("style", style.lower().replace("-", "_")), ("length", length.lower())))  # fmt: skip


SKIRTS = (
    _skirt(
        "SCHPLT",
        "Pleated School Skirt",
        LF,
        "Pleated",
        "Polyester",
        "Yes",
        "Knee",
        9.0,
        "A knee length school skirt with knife pleats from the waist and an adjustable waistband.",
        (BLACK, GREY, NAVY),
    ),
    _skirt(
        "SCHALN",
        "Plain A-Line School Skirt",
        CL,
        "A-Line",
        "Polyester",
        "No",
        "Knee",
        8.0,
        "A plain A-line school skirt with a smooth flare and a zip at the side.",
        (BLACK, NAVY, CHARCOAL),
    ),
    _skirt(
        "SCHKLT",
        "Wrap School Kilt",
        BW,
        "Kilt",
        "Polyester",
        "No",
        "Knee",
        12.0,
        "A wrapped school kilt with a pin at the front, a fringed overlap and pleats at the back.",
        (NAVY, GREY, BLACK),
    ),
    _skirt(
        "SCHLPL",
        "Longline Pleated School Skirt",
        LK,
        "Pleated",
        "Polyester",
        "Yes",
        "Midi",
        11.0,
        "A midi length pleated school skirt with an adjustable waistband, for a longer fit.",
        (BLACK, NAVY, GREY),
    ),
)

# --------------------------------------------------------------------------
# Pinafores and jumper dresses: the bib and straps, or the scoop neck, are drawn.
# --------------------------------------------------------------------------


def _pinafore(code, title, brand, style, fabric, price, desc, colors) -> Row:
    return _row(code, title, brand, _PINAFORES, "School Pinafore", price, "school_pinafore", desc,
                colors, (_a("pinafore_style", "Pinafore style", style), _a("fabric", "Fabric", fabric)),
                (("style", style.lower().replace(" ", "_")),))  # fmt: skip


PINAFORES = (
    _pinafore(
        "SCHPNF",
        "Pleated School Pinafore",
        LF,
        "Pinafore",
        "Polyester",
        12.0,
        "A school pinafore with a squared bib, two straps and a pleated skirt, to wear over a "
        "blouse.",
        (GREY, NAVY, BLACK),
    ),
    _pinafore(
        "SCHPCT",
        "Cotton Blend School Pinafore",
        CL,
        "Pinafore",
        "Cotton",
        14.0,
        "A soft school pinafore dress with a bib front and a skirt that holds its pleats.",
        (NAVY, GREY, CHARCOAL),
    ),
    _pinafore(
        "SCHJMP",
        "Scoop Neck School Jumper Dress",
        BW,
        "Jumper Dress",
        "Polyester",
        13.0,
        "A sleeveless school jumper dress with a scoop neck and a pleated skirt, for layering "
        "over a shirt.",
        (GREY, NAVY, BLACK),
    ),
    _pinafore(
        "SCHJLG",
        "Longline School Jumper Dress",
        LK,
        "Jumper Dress",
        "Polyester",
        15.0,
        "A school jumper dress cut longer through the body, with a scoop neck and pleats "
        "below the waist.",
        (NAVY, CHARCOAL, GREY),
    ),
)

# --------------------------------------------------------------------------
# Shirts: the sleeve and the pack are drawn; fit and easy care are attributes.
# --------------------------------------------------------------------------


def _shirt(code, title, brand, sleeve, fit, care, fabric, pack, price, desc, colors) -> Row:
    return _row(code, title, brand, _SHIRTS, "School Shirt", price, "school_shirt", desc, colors,
                (_a("sleeve_length", "Sleeve length", sleeve), _a("fit", "Fit", fit),
                 _a("easy_care", "Easy care", care), _a("fabric", "Fabric", fabric),
                 _a("pack_size", "Pack size", _pack(pack))),
                (("sleeve", sleeve.lower()), ("pack", str(pack))))  # fmt: skip


SHIRTS = (
    _shirt(
        "SCHLSL",
        "Long Sleeve School Shirt, 2 Pack",
        LF,
        "Long",
        "Regular",
        "Easy Iron",
        "Cotton",
        2,
        9.0,
        "Two long sleeve school shirts with a pointed collar and a button front, easy to iron.",
        (WHITE, BLUE),
    ),
    _shirt(
        "SCHSSL",
        "Short Sleeve School Shirt, 3 Pack",
        CL,
        "Short",
        "Regular",
        "Easy Iron",
        "Cotton",
        3,
        12.0,
        "Three short sleeve school shirts with a pointed collar and a chest pocket.",
        (WHITE, BLUE),
    ),
    _shirt(
        "SCHSLM2",
        "Slim Fit School Shirt",
        BW,
        "Long",
        "Slim",
        "Non-Iron",
        "Polyester",
        1,
        6.0,
        "A slim fit long sleeve school shirt that comes out of the wash ready to wear.",
        (WHITE, BLUE),
    ),
    _shirt(
        "SCHPLS2",
        "Plus Fit Short Sleeve School Shirt",
        LF,
        "Short",
        "Plus Fit",
        "Easy Iron",
        "Cotton",
        1,
        6.5,
        "A roomier short sleeve school shirt with extra width through the chest and body.",
        (WHITE, BLUE),
    ),
    _shirt(
        "SCHNIR",
        "Non-Iron School Shirt, 3 Pack",
        LK,
        "Long",
        "Regular",
        "Non-Iron",
        "Polyester",
        3,
        13.0,
        "Three long sleeve non-iron school shirts with a pointed collar and a button front.",
        (WHITE, BLUE),
    ),
)

ROWS = (*TROUSERS, *SKIRTS, *PINAFORES, *SHIRTS)


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]
