"""Underwear and nightwear templates for the scaled retail catalog (gen#208): data only.

The catalog had bras, pyjamas and pyjama shorts but no knickers, tights, vests, slips,
shapewear, dressing gowns or boxers, so a search for any of them found a bra or a pair of
pyjamas. Each type here is a leaf under the lingerie, hosiery, nightwear or underwear node
of its audience, with its own drawing (:mod:`kit_underwear`), its shopper attributes (cut,
denier, fabric, control level, hood, ...) as structured entries, and SKUs over color, size
and, where shoppers buy them, the pack: 1, 3 or 5 knickers, 2 or 3 tights.

A style's attribute and its drawing param are made from one value (:func:`_pair`), so the
image never states what the row does not. A drawing prints neither a size nor a pack count:
every size and pack of a colorway shares one image. These styles are templates only:
:func:`scale.derivable` leaves them out, as it does the shirts and the household styles,
so the seeded derivation is what it was.
"""

# ruff: noqa: E501 -- descriptions and row data read better whole than wrapped.

from __future__ import annotations

from dataclasses import dataclass

import kit_underwear  # noqa: F401 -- registers knickers, tights, vest, slip, ...
from breadth_rows import Row
from variants import cw

_LING = "Lingerie & Nightwear"
_DH, _HW, _TW, _QS, _WF, _LM, _HP, _HB = (
    "Dovecote Lane", "Hushwell", "Thistle & Wren", "Quillon Sleep", "Wrenfield", "Larkmoor",
    "Hollinwray Knits", "Harbour & Pine",
)  # fmt: skip

KNICKERS = ("Women", "Lingerie", "Knickers")
TIGHTS = ("Women", "Hosiery", "Tights")
VEST_W = ("Women", "Lingerie", "Vests")
VEST_M = ("Men", "Underwear", "Vests")
VEST_K = ("Kids", "Girls", "Vests")
SLIPS = ("Women", "Lingerie", "Slips")
SHAPE = ("Women", "Lingerie", "Shapewear")
GOWN_W = ("Women", "Nightwear", "Dressing Gowns")
GOWN_M = ("Men", "Nightwear", "Dressing Gowns")
GOWN_K = ("Kids", "Boys", "Dressing Gowns")
BOXERS = ("Men", "Underwear", "Boxers")

#: The product type -> its category path(s), for the tests and the README.
TYPES = {
    "Knickers": (KNICKERS,), "Tights": (TIGHTS,), "Vest": (VEST_W, VEST_M, VEST_K),
    "Slip": (SLIPS,), "Shapewear": (SHAPE,), "Dressing Gown": (GOWN_W, GOWN_M, GOWN_K),
    "Boxers": (BOXERS,),
}  # fmt: skip


@dataclass(frozen=True)
class URow(Row):
    """A row whose SKUs are color x size x pack: ``packs`` is ``(count, price factor)``, the
    factor on the size's price (a 3 pack costs less than three singles)."""

    packs: tuple[tuple[int, float], ...] = ()

    def skus(self) -> list[dict]:
        out = super().skus()
        if not self.packs:
            return out
        return [
            {**s, "pack_size": "Single" if n == 1 else f"{n} pack", "units_per_pack": n,
             "price": round(s["price"] * f, 2)}
            for s in out for n, f in self.packs
        ]  # fmt: skip


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _pair(key: str, name: str, value: str, param: str | None = None, shown: str | None = None):
    """The attribute and the drawing param that carry one value: ``(attr, param)``."""
    return (_a(key, name, value), (param or key, (shown or value).lower().replace("-", "_").replace(" ", "_")))


def _packs(*counts: int) -> tuple[tuple[int, float], ...]:
    """Pack counts with a multibuy price: the factor is the count less a growing saving."""
    return tuple((n, round(n * {1: 1.0, 2: 0.9, 3: 0.85, 5: 0.78, 7: 0.72}[n], 2)) for n in counts)


def _pack_attrs(packs: tuple[tuple[int, float], ...]) -> tuple:
    return tuple(_a("pack_size", "Pack size", "Single" if n == 1 else f"{n} pack") for n, _ in packs)


def _sizes(names: tuple[str, ...], base: float, step: float = 0.0, after: int = 99):
    """Each size's price: ``base``, plus ``step`` for every size past the ``after``-th."""
    return tuple((n, round(base + step * max(0, i - after + 1), 2)) for i, n in enumerate(names))


UK = ("8", "10", "12", "14", "16", "18")
UK_PLUS = ("8", "10", "12", "14", "16", "18", "20", "22")
BAND = ("S/M", "M/L", "L/XL")
LETTER = ("XS", "S", "M", "L", "XL")
LETTER_M = ("S", "M", "L", "XL", "XXL")
KIDS = ("3-4 Years", "5-6 Years", "7-8 Years", "9-10 Years")
WAISTS = ("30", "32", "34", "36", "38", "40")

BLACK = cw("Black", "#2f2f35", "solid", "#8f989f")
WHITE = cw("White", "#f4f1ea", "solid", "#b9b4a6")
NUDE = cw("Nude", "#e5c1a8", "solid", "#a9805f")
PINK = cw("Pink", "#e8b4c4", "solid", "#a8324a")
ROSE = cw("Rose", "#d98aa0", "solid", "#7a2a40")
NAVY = cw("Navy", "#2c3a5e", "solid", "#d8dce8")
GREY = cw("Grey", "#9a9ca0", "solid", "#55575c")
CHARCOAL = cw("Charcoal", "#4a4d52", "solid", "#c8cbd0")
RED = cw("Red", "#b3263a", "solid", "#f4d8dc")
BURGUNDY = cw("Burgundy", "#6a1f33", "solid", "#e8c8d0")
IVORY = cw("Ivory", "#f2ead8", "solid", "#b9ad8c")
BEIGE = cw("Beige", "#d9c3a0", "solid", "#8c7650")
LILAC = cw("Lilac", "#b9a6d0", "solid", "#5d4a80")
TEAL = cw("Teal", "#2f7f84", "solid", "#d0e6e8")
BLUE = cw("Blue", "#6b8fc4", "solid", "#e0e8f4")
GREEN = cw("Green", "#4c7a58", "solid", "#d8e6dc")
PINK_DOT = cw("Pink Polka Dot", "#f4f1ea", "polka", "#c9587a")
NAVY_DOT = cw("Navy Polka Dot", "#2c3a5e", "polka", "#f4f1ea")
NAVY_STRIPE = cw("Navy Stripe", "#f4f1ea", "stripe", "#2c3a5e")
GREY_STRIPE = cw("Grey Stripe", "#f4f1ea", "stripe", "#9a9ca0")
LEOPARD = cw("Brown Leopard", "#d6a76b", "leopard", "#5a3a22")

# --------------------------------------------------------------------------
# Knickers: the cut is drawn; fabric, pack and size vary.
# --------------------------------------------------------------------------

CUTS = {
    "Briefs": "brief", "Full Briefs": "brief", "High-Waisted": "high_waisted",
    "High-Leg": "high_leg", "Thong": "thong", "Shorts": "shorts", "Bikini": "bikini",
}  # fmt: skip


def _knickers(code, title, brand, cut, fabric, price, desc, colors, counts, sizes=UK):
    a_cut, p_cut = _pair("cut", "Cut", cut, shown=CUTS[cut])
    lace = fabric == "Lace"
    return URow(
        code, title, brand, _LING, KNICKERS, "Knickers", price, "knickers", desc, colors,
        (a_cut, _a("fabric", "Fabric", fabric), *_pack_attrs(_packs(*counts))),
        _sizes(sizes, price, 0.0), params=(p_cut, ("trim", "lace" if lace else "plain")),
        packs=_packs(*counts),
    )  # fmt: skip


KNICKER_ROWS = (
    _knickers("KNBRCT", "Cotton Full Briefs", _TW, "Full Briefs", "Cotton", 4.5,
              "Soft stretch cotton full briefs with a covered elastic waist and full back coverage. "
              "Machine washable.", (BLACK, WHITE, NUDE, PINK_DOT), (1, 3, 5, 7)),
    _knickers("KNHWMF", "Microfiber High-Waisted Knickers", _DH, "High-Waisted", "Microfiber", 7.0,
              "Smooth microfiber knickers that sit at the waist, with a bonded edge that stays flat "
              "under fitted clothes.", (BLACK, NUDE, ROSE), (1, 3), UK_PLUS),
    _knickers("KNHLLC", "Lace High-Leg Knickers", _HW, "High-Leg", "Lace", 8.0,
              "Stretch lace high-leg knickers with a scalloped waist and a cotton-lined gusset.",
              (BLACK, BURGUNDY, IVORY), (1, 3)),
    _knickers("KNTHSM", "Seamless Thong", _DH, "Thong", "Seamless", 5.0,
              "A seamless thong knitted in one piece, with no visible lines under leggings or "
              "trousers.", (BLACK, NUDE, BEIGE, LILAC), (1, 3, 5)),
    _knickers("KNSHCT", "Cotton Boy Shorts", _QS, "Shorts", "Cotton", 6.0,
              "Jersey cotton boy shorts with a short leg that does not ride up, and a flat waistband.",
              (NAVY, GREY, PINK_DOT, LEOPARD), (1, 3, 5)),
    _knickers("KNBKSM", "Seamless Bikini Knickers", _WF, "Bikini", "Seamless", 4.0,
              "Low-rise seamless bikini knickers with a bonded leg and waist, for a smooth line.",
              (BLACK, WHITE, NUDE, TEAL), (1, 3, 5, 7)),
    _knickers("KNBRMF", "Microfiber Briefs", _HP, "Briefs", "Microfiber", 5.5,
              "Lightweight microfiber briefs that dry fast, with a soft elastic waist.",
              (BLACK, GREY, BLUE), (3, 5)),
    _knickers("KNHLCT", "Cotton High-Leg Knickers", _TW, "High-Leg", "Cotton", 5.0,
              "Cotton high-leg knickers with a cut that sits high on the hip and a soft waist.",
              (WHITE, PINK, LILAC), (1, 3, 5)),
)  # fmt: skip

# --------------------------------------------------------------------------
# Tights: denier and finish are drawn (a low denier is faded); band and pack vary.
# --------------------------------------------------------------------------


def _tights(code, title, brand, denier, finish, price, desc, colors, counts, control="No", sizes=BAND):
    a_den, _ = _pair("denier", "Denier", str(denier))
    a_fin, _ = _pair("finish", "Finish", finish)
    fin = {"Sheer": "sheer", "Opaque": "opaque", "Fleece-Lined": "fleece", "Patterned": "patterned"}[finish]
    return URow(
        code, title, brand, _LING, TIGHTS, "Tights", price, "tights", desc, colors,
        (a_den, a_fin, _a("control_top", "Control top", control), *_pack_attrs(_packs(*counts))),
        _sizes(sizes, price), params=(("denier", str(denier)), ("finish", fin),
                                      ("control", "yes" if control == "Yes" else "no")),
        packs=_packs(*counts),
    )  # fmt: skip


TIGHT_ROWS = (
    _tights("TGSH10", "10 Denier Sheer Tights", _DH, 10, "Sheer", 3.5,
            "Ultra-sheer 10 denier tights with a reinforced toe and a flat seam, for bare legs "
            "with a smooth finish.", (NUDE, BLACK, BEIGE), (1, 2, 3)),
    _tights("TGSH15", "15 Denier Sheer Tights with Control Top", _HW, 15, "Sheer", 5.0,
            "Light 15 denier sheer tights with a control top panel that smooths the tummy.",
            (NUDE, BLACK, NAVY), (1, 2), "Yes"),
    _tights("TGSH20", "20 Denier Everyday Tights", _TW, 20, "Sheer", 3.0,
            "Everyday 20 denier tights in a soft, semi-sheer knit with a comfort waistband.",
            (BLACK, NAVY, GREY, NUDE), (1, 2, 3)),
    _tights("TGOP40", "40 Denier Opaque Tights", _QS, 40, "Opaque", 4.5,
            "Soft 40 denier opaque tights that keep their color wash after wash, with a gusset "
            "for comfort.", (BLACK, NAVY, BURGUNDY, TEAL), (1, 2, 3)),
    _tights("TGOP60", "60 Denier Opaque Tights with Control Top", _WF, 60, "Opaque", 6.0,
            "Thick 60 denier opaque tights with a control top for a smooth line under skirts and "
            "dresses.", (BLACK, CHARCOAL, NAVY), (1, 2), "Yes"),
    _tights("TGFL100", "100 Denier Fleece-Lined Tights", _HP, 100, "Fleece-Lined", 9.0,
            "Warm fleece-lined opaque tights, 100 denier, for the coldest days. A brushed lining "
            "and a deep waistband.", (BLACK, CHARCOAL, BURGUNDY), (1, 2)),
    _tights("TGPT20", "20 Denier Polka Dot Tights", _DH, 20, "Patterned", 6.0,
            "Fine 20 denier tights printed with polka dots on a plain ground.",
            (cw("Black Polka Dot", "#2f2f35", "polka", "#f4f1ea"), NAVY_DOT), (1, 2)),
)  # fmt: skip

# --------------------------------------------------------------------------
# Vests: the style is drawn (strap, sleeve, length); audience, fabric and pack vary.
# --------------------------------------------------------------------------

VEST_STYLES = {"Strappy": "strappy", "Thermal": "thermal", "Camisole": "camisole",
               "Crop": "crop", "Sleeveless": "sleeveless"}  # fmt: skip


def _vest(code, title, brand, path, style, fabric, price, desc, colors, counts, sizes, audience="adult"):
    a_style, p_style = _pair("style", "Style", style, shown=VEST_STYLES[style])
    return URow(
        code, title, brand, _LING, path, "Vest", price, "vest", desc, colors,
        (a_style, _a("fabric", "Fabric", fabric), *_pack_attrs(_packs(*counts))),
        _sizes(sizes, price), params=(p_style, ("trim", "lace" if style == "Camisole" else "plain")),
        packs=_packs(*counts), audience=audience,
    )  # fmt: skip


VEST_ROWS = (
    _vest("VSSTCT", "Cotton Strappy Vest Top", _TW, VEST_W, "Strappy", "Cotton", 4.0,
          "A soft cotton vest top on thin straps with a scoop neck. Wear under shirts or on its own.",
          (WHITE, BLACK, PINK, GREY), (1, 2, 3), UK),
    _vest("VSTHWL", "Thermal Short Sleeve Vest", _HP, VEST_W, "Thermal", "Cotton Blend", 7.0,
          "A warm thermal vest with short sleeves and a brushed inside. A first layer for cold days.",
          (WHITE, BLACK, PINK), (1, 2), UK),
    _vest("VSCMSA", "Lace Trim Camisole", _DH, VEST_W, "Camisole", "Satin", 12.0,
          "A satin camisole with a V neckline edged in lace and adjustable straps.",
          (BLACK, IVORY, BURGUNDY, ROSE), (1,), UK),
    _vest("VSCRCT", "Cotton Crop Vest Top", _HW, VEST_W, "Crop", "Cotton", 6.0,
          "A cropped vest top in stretch cotton, with a scoop neck and wide straps.",
          (WHITE, BLACK, LILAC), (1, 2), UK),
    _vest("VSSLCT", "Sleeveless Vest Top", _QS, VEST_W, "Sleeveless", "Cotton", 5.0,
          "A sleeveless cotton vest with wide shoulders and a round neck.",
          (WHITE, NAVY_STRIPE, GREY), (1, 3), UK),
    _vest("VSTHMN", "Men's Thermal Vest", _HB, VEST_M, "Thermal", "Cotton Blend", 8.0,
          "A men's thermal vest with short sleeves and a fleecy inside, for cold work days.",
          (WHITE, GREY, NAVY), (1, 2), LETTER_M),
    _vest("VSSLMN", "Men's Sleeveless Vest", _WF, VEST_M, "Sleeveless", "Cotton", 6.0,
          "A men's sleeveless cotton vest with a round neck, sold singly or in multipacks.",
          (WHITE, GREY, NAVY), (1, 3), LETTER_M),
    _vest("VSSTKD", "Girls' Strappy Vest Top", _LM, VEST_K, "Strappy", "Cotton", 3.0,
          "A soft cotton vest on thin straps for girls, sold singly or in packs.",
          (WHITE, PINK, LILAC), (1, 2, 3), KIDS, audience="kids"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Slips: the length and the lace hem are drawn; the fabric and the strap are attributes.
# --------------------------------------------------------------------------


def _slip(code, title, brand, length, fabric, strap, price, desc, colors):
    a_len, p_len = _pair("length", "Length", length)
    return URow(
        code, title, brand, _LING, SLIPS, "Slip", price, "slip", desc, colors,
        (a_len, _a("fabric", "Fabric", fabric), _a("strap", "Strap", strap)),
        _sizes(("S", "M", "L", "XL"), price), params=(p_len, ("trim", "lace" if "Lace" in fabric else "plain")),
    )  # fmt: skip


SLIP_ROWS = (
    _slip("SLMNSA", "Satin Mini Slip", _DH, "Mini", "Satin", "Thin", 16.0,
          "A short satin slip with thin adjustable straps, to wear under dresses or to bed.",
          (BLACK, IVORY, ROSE)),
    _slip("SLMDSA", "Satin Midi Slip", _HW, "Midi", "Satin", "Adjustable", 22.0,
          "A midi-length satin slip with adjustable straps and a smooth bias cut.",
          (BLACK, BURGUNDY, TEAL, IVORY)),
    _slip("SLFLLC", "Full Length Lace Trim Slip", _TW, "Full", "Lace Trim", "Thin", 18.0,
          "A full-length slip with a lace-trim hem, cut to sit under long skirts and dresses.",
          (BLACK, NUDE, WHITE)),
    _slip("SLMDLC", "Lace Trim Midi Slip", _QS, "Midi", "Lace Trim", "Adjustable", 20.0,
          "A midi slip in smooth jersey with a lace-trim hem and adjustable straps.",
          (NUDE, BLACK, NAVY)),
)  # fmt: skip

# --------------------------------------------------------------------------
# Shapewear: the type, the seams and the control level are drawn.
# --------------------------------------------------------------------------

TYPES_SHAPE = {"Bodysuit": "bodysuit", "Bra-Friendly Bodysuit": "bra_friendly",
               "Shorts": "shorts", "High-Waisted Brief": "high_waisted"}  # fmt: skip


def _shape(code, title, brand, kind, control, seamless, price, desc, colors):
    a_type, p_type = _pair("shapewear_type", "Type", kind, "type", TYPES_SHAPE[kind])
    return URow(
        code, title, brand, _LING, SHAPE, "Shapewear", price, "shapewear", desc, colors,
        (a_type, _a("control_level", "Control level", control), _a("seamless", "Seamless", seamless)),
        _sizes(("S", "M", "L", "XL", "XXL"), price, 1.0, 4),
        params=(p_type, ("seamless", seamless.lower()), ("control", control.lower())),
    )  # fmt: skip


SHAPE_ROWS = (
    _shape("SWBDFM", "Firm Control Bodysuit", _DH, "Bodysuit", "Firm", "No", 28.0,
           "A firm control bodysuit with side panels that smooth the waist and hips, and a popper gusset.",
           (NUDE, BLACK)),
    _shape("SWBFMD", "Medium Control Plunge Bodysuit", _HW, "Bra-Friendly Bodysuit", "Medium", "No", 26.0,
           "A medium control bodysuit with a plunge front and wide-set straps that sit clear of a bra.",
           (NUDE, BLACK, BEIGE)),
    _shape("SWSHLT", "Light Control Smoothing Shorts", _WF, "Shorts", "Light", "Yes", 16.0,
           "Seamless smoothing shorts with light control that stay put under dresses.",
           (NUDE, BLACK, WHITE)),
    _shape("SWHWFM", "Firm Control High-Waisted Brief", _QS, "High-Waisted Brief", "Firm", "Yes", 18.0,
           "A seamless high-waisted brief with firm tummy control and a smooth edge.",
           (NUDE, BLACK, BEIGE)),
    _shape("SWHWMD", "Medium Control High-Waisted Shorts", _TW, "Shorts", "Medium", "No", 20.0,
           "Medium control shorts with side panels, cut high at the waist for tummy control.",
           (NUDE, BLACK)),
)  # fmt: skip

# --------------------------------------------------------------------------
# Dressing gowns: the length, the hood and the belt are drawn; the fabric adds a texture.
# --------------------------------------------------------------------------

GOWN_FABRICS = {"Fleece": "fleece", "Towelling": "towelling", "Waffle": "waffle", "Satin": "satin"}


def _gown(code, title, brand, path, fabric, length, hood, belt, price, desc, colors, sizes, audience="adult"):
    a_len, p_len = _pair("length", "Length", length)
    return URow(
        code, title, brand, _LING, path, "Dressing Gown", price, "dressing_gown", desc, colors,
        (_a("fabric", "Fabric", fabric), a_len, _a("hood", "Hood", hood), _a("belt", "Belt", belt)),
        _sizes(sizes, price), params=(p_len, ("hood", hood.lower()), ("belt", belt.lower()),
                                      ("fabric", GOWN_FABRICS[fabric])),
        audience=audience,
    )  # fmt: skip


GOWN_ROWS = (
    _gown("DGFLHD", "Fleece Dressing Gown with Hood", _HW, GOWN_W, "Fleece", "Knee", "Yes", "Yes", 28.0,
          "A soft fleece dressing gown with a hood, a tie belt and two front pockets.",
          (GREY, PINK, NAVY), ("S/M", "M/L", "L/XL")),
    _gown("DGTWHD", "Hooded Towelling Dressing Gown", _QS, GOWN_W, "Towelling", "Knee", "Yes", "Yes", 34.0,
          "A cotton towelling dressing gown with a hood and a belt, for after the bath.",
          (WHITE, GREY, TEAL), ("S/M", "M/L", "L/XL")),
    _gown("DGWFFL", "Waffle Full Length Dressing Gown", _DH, GOWN_W, "Waffle", "Full", "No", "Yes", 30.0,
          "A lightweight waffle cotton gown that falls to the ankle, with a shawl collar and a belt.",
          (WHITE, IVORY, GREY), ("S/M", "M/L", "L/XL")),
    _gown("DGSTSH", "Satin Short Dressing Gown", _TW, GOWN_W, "Satin", "Short", "No", "Yes", 24.0,
          "A short satin wrap gown with a tie belt, light and smooth.",
          (BLACK, BURGUNDY, ROSE, IVORY), ("S/M", "M/L", "L/XL")),
    _gown("DGFLMN", "Men's Fleece Dressing Gown", _HB, GOWN_M, "Fleece", "Knee", "No", "Yes", 30.0,
          "A men's fleece dressing gown with a shawl collar, a belt and deep pockets.",
          (NAVY, GREY, BURGUNDY), LETTER_M),
    _gown("DGTWMN", "Men's Hooded Towelling Dressing Gown", _WF, GOWN_M, "Towelling", "Full", "Yes", "Yes", 38.0,
          "A men's full-length towelling dressing gown with a hood and a belt.",
          (GREY, NAVY, CHARCOAL), LETTER_M),
    _gown("DGFLKD", "Boys' Hooded Fleece Dressing Gown", _LM, GOWN_K, "Fleece", "Knee", "Yes", "Yes", 16.0,
          "A soft hooded fleece dressing gown for boys, with a tie belt.",
          (BLUE, GREY, GREEN), KIDS, audience="kids"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Boxers: the fit and its fly are drawn; fabric, pack and waist vary.
# --------------------------------------------------------------------------

FITS = {"Trunks": "trunks", "Boxer Shorts": "boxer", "Briefs": "brief"}


def _boxers(code, title, brand, fit, fabric, price, desc, colors, counts, sizes=WAISTS):
    a_fit, p_fit = _pair("fit", "Fit", fit, shown=FITS[fit])
    return URow(
        code, title, brand, _LING, BOXERS, "Boxers", price, "boxers", desc, colors,
        (a_fit, _a("fabric", "Fabric", fabric), *_pack_attrs(_packs(*counts))),
        _sizes(sizes, price), params=(p_fit,), packs=_packs(*counts), size_key="waist",
        audience="adult",
    )  # fmt: skip


BOXER_ROWS = (
    _boxers("BXTRCT", "Cotton Stretch Trunks", _HB, "Trunks", "Cotton", 4.0,
            "Cotton stretch trunks with a short leg and a soft covered waistband.",
            (BLACK, NAVY, GREY), (2, 3, 5)),
    _boxers("BXWVCT", "Woven Cotton Boxer Shorts", _WF, "Boxer Shorts", "Cotton", 4.5,
            "Woven cotton boxer shorts with a button fly and an elastic waist, for a loose fit.",
            (NAVY_STRIPE, GREY_STRIPE, BLUE), (2, 3)),
    _boxers("BXJRCT", "Jersey Boxer Shorts", _TW, "Boxer Shorts", "Cotton Jersey", 5.0,
            "Soft jersey boxer shorts with a button fly and a long leg.",
            (BLACK, GREY, NAVY), (2, 3, 5)),
    _boxers("BXBRCT", "Cotton Briefs", _QS, "Briefs", "Cotton", 3.5,
            "Y-front cotton briefs with a supportive pouch and a soft waistband.",
            (WHITE, BLACK, GREY), (3, 5)),
    _boxers("BXTRMF", "Microfiber Sports Trunks", _HP, "Trunks", "Microfiber", 7.0,
            "Quick-dry microfiber trunks with flat seams, for running and the gym.",
            (BLACK, CHARCOAL, TEAL), (2, 3)),
)  # fmt: skip

ROWS = (
    *KNICKER_ROWS, *TIGHT_ROWS, *VEST_ROWS, *SLIP_ROWS, *SHAPE_ROWS, *GOWN_ROWS, *BOXER_ROWS,
)


def docs() -> list[dict]:
    """Every underwear and nightwear style's catalog document."""
    return [r.doc() for r in ROWS]
