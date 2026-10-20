"""Swimwear templates for the scaled retail catalog (gen#212): data only.

The catalog had no swimsuit, bikini, swim short or swimwear shape, so a search for any of them
found nothing relevant. Each type here is a leaf under the Swimwear node of its audience
(``Womens/Swimwear``, ``Mens/Swimwear``, ``Kids/Girls|Boys|Baby/Swimwear``), with its own
drawing (:mod:`kit_swimwear`), its shopper attributes (cut, rise, length, UPF, absorbency,
lining, ...) as structured entries, and SKUs over color and size (and, for a swimsuit, the cup).

A style's attribute and its drawing param are made from one value (:func:`_f`), so the image
never states what the row does not. A drawing prints no size. These styles are templates only:
:func:`scale.derivable` leaves them out, as it does the underwear, so the seeded derivation is
what it was.
"""

# ruff: noqa: E501 -- descriptions and row data read better whole than wrapped.

from __future__ import annotations

import kit_swimwear  # noqa: F401 -- registers swimsuit, bikini_top, tankini, ...
from breadth_rows import OWNERS
from class_model import BRAND_OWNER
from lowerbody_rows import LRow
from variants import cw

_CLOTH = "Clothing"
_HW, _TW, _LM, _WF, _LK, _DL, _HP, _QS, _HK = (
    "Hushwell", "Thistle & Wren", "Little Fernby", "Wrenfield", "Larkmoor", "Dovecote Lane",
    "Harbour & Pine", "Quillon Sleep", "Hollinwray Knits",
)  # fmt: skip

#: The brands these rows sell, owned as the rest of the clothing tree states.
OWNED = tuple((b, OWNERS.get(b) or BRAND_OWNER[b]) for b in (_HW, _TW, _LM, _WF, _LK, _DL, _HP, _QS, _HK))

SWIMSUIT = ("Womens", "Swimwear", "Swimsuits")
BIKINI_TOP = ("Womens", "Swimwear", "Bikini Tops")
BIKINI_BOTTOMS = ("Womens", "Swimwear", "Bikini Bottoms")
TANKINI = ("Womens", "Swimwear", "Tankinis")
PERIOD = ("Womens", "Swimwear", "Period Swimwear")
COVER_UP = ("Womens", "Swimwear", "Cover-Ups & Kaftans")
ROBE_W = ("Womens", "Swimwear", "Changing Robes")
ROBE_M = ("Mens", "Swimwear", "Changing Robes")
SHORTS = ("Mens", "Swimwear", "Swim Shorts")
KIDS_G = ("Kids", "Girls", "Swimwear")
KIDS_B = ("Kids", "Boys", "Swimwear")
KIDS_BABY = ("Kids", "Baby", "Swimwear")

def _f(key: str, name: str, value: str, param: str | None = None, shown: str | None = None):
    """The attribute and the drawing param that carry one value: ``(attr, param or None)``."""
    attr = (key, name, value)
    if param is None:
        return attr, None
    return attr, (param, (shown or value).lower().replace("-", "_").replace(" ", "_"))


def _sizes(names: tuple[str, ...], base: float, step: float = 1.0):
    """Each size's price: ``base``, plus ``step`` for every size from the fourth."""
    return tuple((n, round(base + step * max(0, i - 2), 2)) for i, n in enumerate(names))


def _row(code, title, brand, path, ptype, shape, price, desc, colors, facts, sizes, audience="adult", axis=None):
    pairs = [_f(*f) for f in facts]
    return LRow(
        code, title, brand, _CLOTH, path, ptype, price, shape, desc, colors,
        tuple(a for a, _ in pairs), _sizes(sizes, price),
        params=tuple(p for _, p in pairs if p), audience=audience,
        axis_key=axis[0] if axis else "", axis=tuple((v, 1.0) for v in axis[1]) if axis else (),
    )  # fmt: skip


UK = ("8", "10", "12", "14", "16", "18")
LETTER_M = ("S", "M", "L", "XL", "XXL")
LETTER = ("XS", "S", "M", "L", "XL")
KIDS = ("3-4 Yrs", "5-6 Yrs", "7-8 Yrs", "9-10 Yrs")
BABY = ("0-1 Yrs", "1-2 Yrs", "2-3 Yrs")
CUPS = ("B", "C", "D", "DD")

BLACK = cw("Black", "#2f2f35", "solid", "#d8dce8")
WHITE = cw("White", "#f4f1ea", "solid", "#7a7f88")
NAVY = cw("Navy", "#2c3a5e", "solid", "#d8dce8")
RED = cw("Red", "#c32f3a", "solid", "#f4d8dc")
BLUE = cw("Blue", "#2f6db5", "solid", "#e4eefa")
GREEN = cw("Green", "#3c8d4f", "solid", "#e0f1e4")
YELLOW = cw("Yellow", "#f2c230", "solid", "#6a5412")
PINK = cw("Pink", "#e8789a", "solid", "#fbe4ec")
TEAL = cw("Teal", "#2a8a8c", "solid", "#d9f0f0")
CORAL = cw("Coral", "#f07a68", "solid", "#fde6e1")
GREY = cw("Grey", "#9a9ca0", "solid", "#55575c")

# -- Swimsuit: cut, tummy control, padded cups, coverage, leg cut --------------------------------


def _swimsuit(code, title, brand, cut, tummy, padded, leg, coverage, price, desc, colors):
    return _row(
        code, title, brand, SWIMSUIT, "Swimsuit", "swimsuit", price, desc, colors,
        (("cut", "Cut", cut, "cut"), ("tummy_control", "Tummy control", tummy, "tummy"),
         ("padded", "Padded cups", padded, "padded"),
         ("leg_cut", "Leg cut", leg, "leg", "high" if leg == "High Leg" else "regular"),
         ("coverage", "Coverage", coverage)),
        UK, axis=("cup_size", CUPS),
    )  # fmt: skip


SWIMSUIT_ROWS = (
    _swimsuit("SWSCTC", "Scoop Neck Swimsuit with Tummy Control", _HW, "Scoop", "Yes", "No", "Regular", "Full", 28.0,
              "A scoop neck swimsuit with a ruched front panel that smooths the tummy and a lined bust.", (BLACK, NAVY, RED, BLUE, GREEN, WHITE)),
    _swimsuit("SWPLPD", "Plunge Padded Swimsuit", _TW, "Plunge", "No", "Yes", "High Leg", "Moderate", 32.0,
              "A plunge swimsuit with soft padded cups and a high leg cut.", (BLACK, RED, YELLOW, WHITE)),
    _swimsuit("SWHLTC", "Halter Neck Swimsuit with Tummy Control", _WF, "Halter", "Yes", "Yes", "Regular", "Full", 36.0,
              "A halter neck swimsuit with padded cups and a ruched tummy control front.", (BLACK, BLUE, GREEN, WHITE)),
    _swimsuit("SWOSHL", "One Shoulder Swimsuit", _LK, "One Shoulder", "No", "No", "High Leg", "Moderate", 30.0,
              "An asymmetric one shoulder swimsuit with a high leg.", (BLUE, RED, BLACK, YELLOW)),
    _swimsuit("SWSCPL", "Plain Scoop Back Swimsuit", _DL, "Scoop", "No", "No", "Regular", "Full", 22.0,
              "A plain scoop neck swimsuit with a scoop back and a full seat.", (NAVY, BLACK, GREEN, RED, WHITE)),
    _swimsuit("SWHLPL", "Halter Swimsuit in Bright Colors", _HP, "Halter", "No", "No", "Regular", "Moderate", 26.0,
              "A halter swimsuit that ties at the neck, in bright colors.", (YELLOW, CORAL, BLUE, BLACK)),
    # Titles that name their cups in the plural (gen#508): `padded` Yes, drawn with cups.
    _swimsuit("SWCPPL", "Plunge Swimsuit with Padded Cups", _TW, "Plunge", "No", "Yes", "High Leg", "Moderate", 30.0,
              "A plunge swimsuit with padded cups and a high leg cut.", (BLACK, NAVY, RED, WHITE)),
    _swimsuit("SWCPHL", "Halter Swimsuit with Padded Cups", _WF, "Halter", "No", "Yes", "Regular", "Full", 34.0,
              "A halter swimsuit with padded cups that ties at the neck.", (BLACK, BLUE, GREEN, YELLOW)),
    _swimsuit("SWCPSC", "Scoop Neck Swimsuit with Padded Cups", _HW, "Scoop", "Yes", "Yes", "Regular", "Full", 32.0,
              "A scoop neck swimsuit with padded cups and a ruched front panel that smooths the tummy.", (BLACK, NAVY, RED, GREEN)),
    _swimsuit("SWCPOS", "One Shoulder Swimsuit with Padded Cups", _LK, "One Shoulder", "No", "Yes", "High Leg", "Moderate", 33.0,
              "An asymmetric one shoulder swimsuit with padded cups and a high leg.", (RED, BLUE, BLACK, WHITE)),
)

# -- Bikini tops and bottoms (sold as separates) --------------------------------------------------


def _top(code, title, brand, shape, padded, price, desc, colors):
    return _row(
        code, title, brand, BIKINI_TOP, "Bikini Top", "bikini_top", price, desc, colors,
        (("top_shape", "Top shape", shape, "top_shape"), ("padded", "Padded cups", padded)), UK,
    )  # fmt: skip


TOP_ROWS = (
    _top("BKTTRI", "Triangle Bikini Top", _HW, "Triangle", "No", 10.0, "A triangle bikini top with sliding cups and neck and back ties.", (BLACK, RED, BLUE, GREEN, YELLOW, WHITE)),
    _top("BKTBAN", "Bandeau Bikini Top", _TW, "Bandeau", "No", 11.0, "A strapless bandeau bikini top with a removable tie.", (BLACK, WHITE, RED, BLUE)),
    _top("BKTBAL", "Balcony Bikini Top", _WF, "Balcony", "Yes", 13.0, "A balcony bikini top with padded cups and adjustable straps.", (BLACK, NAVY, GREEN, YELLOW)),
    _top("BKTWIR", "Underwired Bikini Top", _LK, "Underwired", "Yes", 16.0, "An underwired bikini top with molded cups for support.", (BLACK, RED, BLUE, WHITE)),
    # Titles that name their cups in the plural (gen#508): `padded` Yes, drawn with cups.
    _top("BKCPTR", "Triangle Bikini Top with Padded Cups", _TW, "Triangle", "Yes", 12.0, "A triangle bikini top with padded cups and neck and back ties.", (BLACK, RED, BLUE, WHITE)),
    _top("BKCPSL", "Sliding Triangle Bikini Top with Padded Cups", _LK, "Triangle", "Yes", 13.0, "A sliding triangle bikini top with padded cups and neck and back ties.", (CORAL, TEAL, BLACK, WHITE)),
    _top("BKCPBL", "Balcony Bikini Top with Padded Cups", _HW, "Balcony", "Yes", 14.0, "A balcony bikini top with padded cups and a clip fastening at the back.", (BLACK, NAVY, GREEN, YELLOW)),
    _top("BKCPWR", "Underwired Bikini Top with Padded Cups", _DL, "Underwired", "Yes", 17.0, "An underwired bikini top with padded cups for support.", (BLACK, RED, BLUE, WHITE)),
)


def _bottoms(code, title, brand, rise, tie, price, desc, colors):
    return _row(
        code, title, brand, BIKINI_BOTTOMS, "Bikini Bottoms", "bikini_bottoms", price, desc, colors,
        (("rise", "Rise", rise, "rise", rise.split("-")[0]), ("tie_side", "Tie side", tie, "tie_side")), UK,
    )  # fmt: skip


BOTTOM_ROWS = (
    _bottoms("BKBHIG", "High-Waisted Bikini Bottoms", _HW, "High", "No", 10.0, "High-waisted bikini bottoms that sit above the navel.", (BLACK, RED, BLUE, GREEN, YELLOW, WHITE)),
    _bottoms("BKBMID", "Mid-Rise Bikini Bottoms", _TW, "Mid", "No", 9.0, "Mid-rise bikini bottoms with a classic brief leg.", (BLACK, NAVY, RED, WHITE)),
    _bottoms("BKBLOW", "Low-Rise Bikini Bottoms", _WF, "Low", "No", 9.0, "Low-rise bikini bottoms that sit below the hip.", (BLACK, BLUE, GREEN, YELLOW)),
    _bottoms("BKBTIE", "Tie Side Bikini Bottoms", _LK, "Mid", "Yes", 11.0, "Mid-rise bikini bottoms with a tie at each hip.", (BLACK, RED, BLUE, WHITE)),
    _bottoms("BKBHTI", "High-Waisted Tie Side Bikini Bottoms", _DL, "High", "Yes", 12.0, "High-waisted bikini bottoms with a tie at each hip.", (BLACK, GREEN, YELLOW, WHITE)),
)

# -- Tankini ---------------------------------------------------------------------------------------


def _tankini(code, title, brand, length, support, match, price, desc, colors):
    return _row(
        code, title, brand, TANKINI, "Tankini", "tankini", price, desc, colors,
        (("length", "Length", length, "length"), ("support", "Support", support, "support"),
         ("matching_bottoms", "Matching bottoms", match)), UK,
    )  # fmt: skip


TANKINI_ROWS = (
    _tankini("TNKCRP", "Crop Tankini Top", _HW, "Crop", "Light", "Yes", 18.0, "A cropped tankini top that stops at the ribs; sold with matching bottoms.", (BLACK, RED, BLUE, GREEN, WHITE)),
    _tankini("TNKHIP", "Hip Length Tankini Top", _TW, "Hip", "Medium", "Yes", 22.0, "A hip length tankini top with a built-in shelf band for support.", (BLACK, NAVY, YELLOW, WHITE)),
    _tankini("TNKLNG", "Longline Underwired Tankini Top", _WF, "Long", "Underwired", "No", 28.0, "A longline tankini top with underwired cups.", (BLACK, BLUE, RED, GREEN)),
    _tankini("TNKHPL", "Hip Length Tankini Top with Light Support", _LK, "Hip", "Light", "No", 20.0, "A relaxed hip length tankini top with a light lining.", (CORAL, TEAL, BLACK, WHITE)),
)

# -- Swim shorts -----------------------------------------------------------------------------------


def _shorts(code, title, brand, length, waist, quick, price, desc, colors):
    return _row(
        code, title, brand, SHORTS, "Swim Shorts", "swim_shorts", price, desc, colors,
        (("length", "Length", length, "length"), ("waist_type", "Waist type", waist, "waist"),
         ("quick_dry", "Quick dry", quick)), LETTER_M,
    )  # fmt: skip


SHORTS_ROWS = (
    _shorts("SHTSHD", "Short Length Swim Shorts", _HP, "Short", "Drawstring", "Yes", 14.0, "Short swim shorts with a drawstring waist and a mesh liner.", (BLUE, NAVY, RED, GREEN, BLACK, YELLOW, WHITE)),
    _shorts("SHTMEL", "Mid Length Swim Shorts", _QS, "Mid", "Elasticated", "Yes", 16.0, "Mid length swim shorts with an elasticated waist and two pockets.", (NAVY, BLACK, GREEN, RED, BLUE)),
    _shorts("SHTLND", "Long Board Shorts", _TW, "Long", "Drawstring", "Yes", 20.0, "Long board shorts that fall below the knee, with a drawstring waist.", (BLACK, BLUE, GREEN, YELLOW, WHITE)),
    _shorts("SHTSEL", "Short Elasticated Swim Shorts", _HK, "Short", "Elasticated", "No", 12.0, "Short swim shorts with a soft elasticated waist.", (BLUE, RED, BLACK, WHITE)),
    _shorts("SHTMDS", "Mid Length Drawstring Swim Shorts", _LK, "Mid", "Drawstring", "No", 15.0, "Mid length swim shorts with a drawstring waist.", (NAVY, GREEN, YELLOW, BLACK)),
)

# -- Kids' and baby swimsuits ---------------------------------------------------------------------


def _kids(code, title, brand, path, sleeve, upf, nappy, price, desc, colors, sizes, age):
    return _row(
        code, title, brand, path, "Kids Swimsuit", "kids_swimsuit", price, desc, colors,
        (("sleeve", "Sleeve", sleeve, "sleeve", {"Sleeveless": "none"}.get(sleeve, sleeve)),
         ("uv_protection", "UV protection", "UPF 50+" if upf == "yes" else "None", "upf", upf),
         ("nappy_friendly", "Nappy friendly", "Yes" if nappy == "yes" else "No", "nappy", nappy)),
        sizes, audience=age,
    )  # fmt: skip


KIDS_ROWS = (
    _kids("KSWGPL", "Girls' Swimsuit", _LM, KIDS_G, "Sleeveless", "no", "no", 10.0, "A sleeveless swimsuit for girls with a lined front.", (PINK, BLUE, RED, GREEN, YELLOW), KIDS, "kids"),
    _kids("KSWGUV", "Girls' Long Sleeve UPF Swimsuit", _LM, KIDS_G, "Long", "yes", "no", 16.0, "A long sleeve UPF 50+ swimsuit that keeps the sun off.", (BLUE, PINK, GREEN, WHITE), KIDS, "kids"),
    _kids("KSWBUV", "Boys' Short Sleeve UPF Swimsuit", _HP, KIDS_B, "Short", "yes", "no", 14.0, "A short sleeve UPF 50+ sun suit for boys.", (BLUE, RED, GREEN, YELLOW, BLACK), KIDS, "kids"),
    _kids("KSWBPL", "Boys' Sleeveless Swimsuit", _QS, KIDS_B, "Sleeveless", "no", "no", 9.0, "A sleeveless swimsuit for boys that dries fast.", (NAVY, RED, GREEN, WHITE), KIDS, "kids"),
    _kids("KSWBBY", "Baby Nappy Friendly Swimsuit", _TW, KIDS_BABY, "Sleeveless", "no", "yes", 9.0, "A baby swimsuit with a double leg band that holds a swim nappy.", (BLUE, PINK, YELLOW, GREEN, WHITE), BABY, "baby"),
    _kids("KSWBBU", "Baby Long Sleeve UPF Swimsuit", _LM, KIDS_BABY, "Long", "yes", "yes", 13.0, "A baby long sleeve UPF 50+ swimsuit with a nappy friendly leg band.", (BLUE, RED, GREEN, WHITE, YELLOW), BABY, "baby"),
)

# -- Period swimwear -------------------------------------------------------------------------------


def _period(code, title, brand, absorbency, cut, price, desc, colors):
    return _row(
        code, title, brand, PERIOD, "Period Swimwear", "period_swimwear", price, desc, colors,
        (("absorbency", "Absorbency", absorbency, "absorbency"), ("cut", "Cut", cut, "cut")), UK,
    )  # fmt: skip


PERIOD_ROWS = (
    _period("PRDLGT", "Light Absorbency Period Swim Bottoms", _HW, "Light", "Bikini", 22.0, "Period swim bottoms with a light absorbency gusset for the lighter days of a period.", (BLACK, NAVY, RED, BLUE, GREEN, WHITE)),
    _period("PRDMOD", "Moderate Absorbency Period Swim Bottoms", _TW, "Moderate", "High-Waisted", 28.0, "High-waisted period swim bottoms with a two layer gusset for a moderate flow.", (BLACK, RED, BLUE, YELLOW)),
    _period("PRDHWL", "High-Waisted Light Period Swim Bottoms", _WF, "Light", "High-Waisted", 24.0, "High-waisted period swim bottoms with a light absorbency lining.", (BLACK, GREEN, WHITE, NAVY)),
    _period("PRDBMO", "Bikini Period Swim Bottoms, Moderate", _LK, "Moderate", "Bikini", 26.0, "Bikini cut period swim bottoms with a moderate absorbency gusset.", (BLACK, BLUE, RED, YELLOW)),
)

# -- Cover-ups and kaftans -------------------------------------------------------------------------


def _cover(code, title, brand, length, fabric, price, desc, colors):
    return _row(
        code, title, brand, COVER_UP, "Cover-Up", "cover_up", price, desc, colors,
        (("length", "Length", length, "length"), ("fabric", "Fabric", fabric)), LETTER,
    )  # fmt: skip


COVER_ROWS = (
    _cover("CVRMNI", "Mini Beach Cover-Up", _HW, "Mini", "Cotton", 20.0, "A mini cotton beach cover-up with wide sleeves and a V neck.", (WHITE, BLACK, RED, BLUE, GREEN, YELLOW)),
    _cover("CVRMDI", "Midi Kaftan", _TW, "Midi", "Voile", 28.0, "A flowing voile kaftan that falls to the calf.", (BLUE, GREEN, WHITE, BLACK, YELLOW)),
    _cover("CVRMXI", "Maxi Kaftan", _WF, "Maxi", "Voile", 34.0, "A full length voile kaftan with wide sleeves.", (BLACK, RED, YELLOW, WHITE)),
    _cover("CVRCTM", "Cotton Midi Beach Kaftan", _DL, "Midi", "Cotton", 26.0, "A cotton beach kaftan to the calf, light enough to fold into a bag.", (WHITE, BLUE, GREEN, RED)),
)

# -- Changing robes --------------------------------------------------------------------------------


def _robe(code, title, brand, path, lining, shell, length, price, desc, colors):
    return _row(
        code, title, brand, path, "Changing Robe", "changing_robe", price, desc, colors,
        (("lining", "Lining", lining, "lining"), ("waterproof_shell", "Waterproof shell", shell, "waterproof"),
         ("length", "Length", length, "length")), LETTER_M,
    )  # fmt: skip


ROBE_ROWS = (
    _robe("CHRFLW", "Waterproof Fleece Lined Changing Robe", _HP, ROBE_W, "Fleece", "Yes", "Knee", 60.0, "A hooded changing robe with a waterproof shell and a warm fleece lining.", (BLACK, BLUE, GREEN, RED, YELLOW, WHITE)),
    _robe("CHRTWW", "Towelling Lined Changing Robe", _QS, ROBE_W, "Towelling", "No", "Full", 40.0, "A full length hooded changing robe lined with soft towelling.", (NAVY, WHITE, GREEN, BLACK)),
    _robe("CHRFLM", "Mens Waterproof Fleece Lined Changing Robe", _LK, ROBE_M, "Fleece", "Yes", "Full", 65.0, "A full length hooded changing robe for men, with a waterproof shell and a fleece lining.", (BLACK, NAVY, GREEN, RED)),
    _robe("CHRTWM", "Mens Towelling Changing Robe", _HK, ROBE_M, "Towelling", "No", "Hip", 32.0, "A hip length hooded changing robe for men, lined with towelling.", (NAVY, BLUE, BLACK, WHITE)),
)
