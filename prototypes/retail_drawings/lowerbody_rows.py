"""Lower-body templates for the scaled retail catalog (gen#206): data only.

The catalog held trousers and jeans but no leggings, joggers, shorts, cycling shorts,
tracksuits or skirts, so a search for any of them found trousers or a dress. Each type here
is a leaf with its own drawing (:mod:`kit_lowerbody`), its shopper attributes as structured
entries, and SKUs over the color, the size and, where the type varies on it, a third axis:
a leg or skirt length (``inside_leg``, ``fit_length``). The tracksuits moved to the spec
``type_specs/tracksuit.py`` (gen#351), which also draws with :mod:`kit_lowerbody`.

What a drawing shows is what the record states: ``pockets`` Yes draws two ``pocket`` groups,
``cargo_pockets`` Yes (or the Cargo shorts style) two ``cargo-pocket`` groups, a Belted
waist four ``belt-loop`` groups, ``piece_count`` that many ``piece`` groups, ``tiers`` that
many ``tier`` groups and Padded one ``pad``. The styles are templates only:
:func:`scale.derivable` leaves them out, as it does the shirts, so the seeded derivation is
what it was.
"""

from __future__ import annotations

from dataclasses import dataclass

import kit_lowerbody  # noqa: F401 -- registers leggings, joggers, shorts, ...
from breadth_rows import OWNERS, Row
from class_model import BRAND_OWNER, LEGS3, LENGTH_RANGE, SIZE_RANGES
from variants import cw

#: The brands these rows sell, owned as the rest of the clothing tree already states.
_BRANDS = ("Harbour & Pine", "Larkmoor", "Wrenfield", "Stridewell", "Hollinwray Knits",
           "Calderby & Lune", "Bramblewood", "Saltmarsh")  # fmt: skip
OWNERS.update({b: BRAND_OWNER[b] for b in _BRANDS})
HP, LK, WF, SW, HK, CL, BW, SM = _BRANDS

CL_ = "Clothing"
ADULT = ("XS", "S", "M", "L", "XL")


@dataclass(frozen=True)
class LRow(Row):
    """A row with a third SKU axis (``axis_key``: ``(value, price factor)`` pairs) and the
    top-level facts ``facts`` (a rise, a pattern, a size range) the export turns into entries."""

    axis_key: str = ""
    axis: tuple[tuple[str, float], ...] = ()
    facts: tuple[tuple[str, object], ...] = ()

    def skus(self) -> list[dict]:
        base = super().skus()
        if not self.axis:
            return base
        return [{**s, self.axis_key: v, "price": round(s["price"] * f, 2)}
                for s in base for v, f in self.axis]  # fmt: skip

    def doc(self) -> dict:
        out = super().doc()
        out.update(dict(self.facts))
        if self.axis_key in ("inside_leg", "fit_length"):
            served = {LENGTH_RANGE[v] for v, _ in self.axis}
            out["size_range"] = [r for r in SIZE_RANGES if r in served]
        return out


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


YES, NO = "Yes", "No"


def _sizes(price: float, names: tuple[str, ...] = ADULT) -> tuple[tuple[str, float], ...]:
    return tuple((n, price) for n in names)


def _pairs(names: tuple[str, ...], step: float = 0.0) -> tuple[tuple[str, float], ...]:
    """The values of a third axis, each costing ``step`` more than the one before."""
    return tuple((n, round(1 + step * i, 2)) for i, n in enumerate(names))


def _legs() -> tuple[tuple[str, float], ...]:
    return _pairs(LEGS3, 0.04)


def _facts(rise: str | None, pattern: str) -> tuple:
    return (*((("rise", rise),) if rise else ()), ("pattern", pattern))


def _waist(*kinds: str) -> tuple:
    return tuple(_a("waist_type", "Waist type", k) for k in kinds)


def _pockets(v: str) -> tuple:
    return (_a("pockets", "Pockets", v),)


def _count(key: str, name: str, n: int) -> tuple[str, str, str, str]:
    return (key, name, str(n), "C62")


BLACK = cw("Black", "#2f2f35")
WHITE = cw("White", "#f4f1ea", "solid", "#b9b4a6")
GREY = cw("Grey", "#9a9ca0")
CHARCOAL = cw("Charcoal", "#4b4e55")
NAVY = cw("Navy", "#26365c")
KHAKI = cw("Khaki", "#8a8456")
CREAM = cw("Cream", "#efe8d8", "solid", "#b9b4a6")
PINK = cw("Pink", "#e7a9b8")
TEAL = cw("Teal", "#1c7c7d")
RED = cw("Red", "#b8322b")
BLUE = cw("Blue", "#3f6fb5")
BROWN = cw("Brown", "#6b4a35")
GREEN = cw("Green", "#3f7a4a")
LILAC = cw("Lilac", "#b9a6d4")
BURGUNDY = cw("Burgundy", "#6e2433")
PURPLE = cw("Purple", "#6b4a8f")
BEIGE = cw("Beige", "#d8c9a8", "solid", "#b9b4a6")
GREY_MARL = cw("Grey Marl", "#a9abb0")
LIGHT_WASH = cw("Light Wash", "#8fb0cf", "solid", "#4a6a94")
MID_WASH = cw("Mid Wash", "#4a6a94", "solid", "#25345a")
BLACK_DENIM = cw("Black", "#3a3a40", "solid", "#8f989f")
NAVY_STRIPE = cw("Navy Stripe", "#f4f1ea", "stripe", "#26365c")
GREY_STRIPE = cw("Grey Stripe", "#f4f1ea", "stripe", "#7d8087")
NAVY_CHECK = cw("Navy Check", "#26365c", "gingham", "#a83a32")
GREEN_CHECK = cw("Green Check", "#3f7a4a", "gingham", "#efe8d8")

# --------------------------------------------------------------------------
# Leggings: length, rise, fit, fabric, lining and pockets are drawn or stated.
# --------------------------------------------------------------------------

_LG = ("Womens", "Leggings")


def _lg(
    fabric: str, fit: str, length: str, pockets: str, lining: str = "Unlined", maternity: str = NO
) -> tuple:
    return (_a("fabric", "Fabric", fabric), _a("leg_fit", "Leg fit", fit),
            _a("garment_length", "Length", length), *_pockets(pockets),
            _a("lining", "Lining", lining), _a("maternity", "Maternity", maternity))  # fmt: skip


def _lgp(length: str, rise: str, pocket: str) -> tuple[tuple[str, str], ...]:
    return (("length", length), ("rise", rise), ("pocket", pocket))


LEGGINGS = (
    LRow("LGGCOT", "Full Length Cotton Blend Leggings", "Harbour & Pine", CL_, _LG, "Leggings",
         14.0, "leggings", "Soft stretch cotton blend leggings that stay put through a day of "
         "wear, with a wide waistband.", (BLACK, GREY, NAVY),
         _lg("Cotton Blend", "Regular", "Full Length", NO), _sizes(14.0),
         params=_lgp("full", "high", "no"), facts=_facts("High", "plain")),
    LRow("LGGSPT", "High Waisted Sports Leggings with Pockets", SW, CL_, _LG, "Leggings", 28.0,
         "leggings", "Compression leggings in a sweat-wicking knit, with a high waistband and "
         "a side pocket on each leg that holds a phone.", (BLACK, NAVY, CHARCOAL),
         _lg("Knitted", "Compression", "Full Length", YES), _sizes(28.0),
         params=_lgp("full", "high", "yes"), facts=_facts("High", "plain")),
    LRow("LGGFLC", "Fleece Lined Thermal Leggings", HK, CL_, _LG, "Leggings", 18.0,
         "leggings", "Opaque leggings brushed with fleece on the inside, for cold walks and "
         "winter layering.", (BLACK, CHARCOAL),
         _lg("Cotton Blend", "Regular", "Full Length", NO, "Fleece"), _sizes(18.0),
         params=_lgp("full", "mid", "no"), facts=_facts("Mid", "plain")),
    LRow("LGGFXL", "Faux Leather Leggings", "Larkmoor", CL_, _LG, "Leggings", 26.0,
         "leggings", "Shiny coated leggings with a stretch backing and a high waist, for "
         "evenings out.", (BLACK, BROWN),
         _lg("Faux Leather", "Regular", "Full Length", NO), _sizes(26.0),
         params=_lgp("full", "high", "no"), facts=_facts("High", "plain")),
    LRow("LGG78S", "7/8 Length Compression Leggings with Pockets", SW, CL_, _LG, "Leggings",
         32.0, "leggings", "Shaping knit leggings that stop above the ankle, with a high waist and "
         "two side pockets.", (BLACK, TEAL, PURPLE),
         _lg("Knitted", "Compression", "7/8", YES), _sizes(32.0),
         params=_lgp("7_8", "high", "yes"), facts=_facts("High", "plain")),
    LRow("LGGCRP", "Striped Cropped Cotton Leggings", "Wrenfield", CL_, _LG, "Leggings", 12.0,
         "leggings", "Cropped leggings in a stretch cotton knit with a fine stripe, for summer.",
         (NAVY_STRIPE, GREY_STRIPE), _lg("Cotton Blend", "Regular", "Cropped", NO), _sizes(12.0),
         params=_lgp("cropped", "mid", "no"), facts=_facts("Mid", "stripe")),
    LRow("LGGMAT", "Maternity Over-the-Bump Leggings", "Harbour & Pine", CL_, _LG, "Leggings",
         20.0, "leggings", "Leggings with a stretch panel that sits over the bump and grows "
         "with it, in a soft cotton blend.", (BLACK, NAVY),
         _lg("Cotton Blend", "Regular", "Full Length", NO, maternity=YES), _sizes(20.0),
         params=_lgp("full", "high", "no"), facts=_facts("High", "plain")),
)  # fmt: skip

# --------------------------------------------------------------------------
# Joggers: fit, cuff, fabric, rise, pockets and cargo pockets; a leg length per SKU.
# --------------------------------------------------------------------------


def _jg(fit: str, cuff: str, fabric: str, pockets: str, cargo: str) -> tuple:
    return (_a("leg_fit", "Leg fit", fit), _a("cuff", "Cuff", cuff),
            _a("fabric", "Fabric", fabric), *_pockets(pockets),
            _a("cargo_pockets", "Cargo pockets", cargo),
            *_waist("Drawstring", "Elastic"))  # fmt: skip


def _jgp(fit: str, cuff: str, rise: str, pocket: str, cargo: str) -> tuple[tuple[str, str], ...]:
    return (("fit", fit), ("cuff", cuff), ("rise", rise.lower()), ("pocket", pocket),
            ("cargo", cargo))  # fmt: skip


def _jrow(code, title, brand, path, price, desc, colors, attrs, params, rise) -> LRow:
    return LRow(code, title, brand, CL_, path, "Joggers", price, "joggers", desc, colors, attrs,
                _sizes(price), params=params, axis_key="inside_leg", axis=_legs(),
                facts=_facts(rise, "plain"))  # fmt: skip


_MJ, _WJ = ("Mens", "Joggers"), ("Womens", "Joggers")
JOGGERS = (
    _jrow("JGGSLM", "Slim Fit Fleece Joggers with Cuffed Hems", SW, _MJ, 24.0,
          "Tapered fleece joggers with a ribbed cuff at the ankle and a drawstring waist.",
          (BLACK, GREY_MARL, NAVY), _jg("Slim", "Elasticated", "Fleece", YES, NO),
          _jgp("slim", "elastic", "Mid", "yes", "no"), "Mid"),
    _jrow("JGGREG", "Regular Fit Cotton Joggers with Open Hem", "Harbour & Pine", _MJ, 22.0,
          "Straight leg cotton joggers with an open hem and a drawstring waist.",
          (GREY_MARL, NAVY, BLACK), _jg("Regular", "Open Hem", "Cotton", NO, NO),
          _jgp("regular", "open", "Mid", "no", "no"), "Mid"),
    _jrow("JGGCRG", "Cargo Joggers with Cuffed Hems", "Larkmoor", _MJ, 30.0,
          "Twill joggers with a patch pocket on each thigh and a ribbed cuff.",
          (KHAKI, BLACK, NAVY), _jg("Regular", "Elasticated", "Twill", YES, YES),
          _jgp("regular", "elastic", "Mid", "yes", "yes"), "Mid"),
    _jrow("JGGRLX", "Relaxed Fit Fleece Joggers", HK, _WJ, 26.0,
          "Roomy brushed fleece joggers with a high rise and a cuffed hem.",
          (GREY_MARL, PINK, BLACK), _jg("Relaxed", "Elasticated", "Fleece", YES, NO),
          _jgp("relaxed", "elastic", "High", "yes", "no"), "High"),
    _jrow("JGGOVR", "Oversized Cotton Joggers", "Wrenfield", _WJ, 28.0,
          "A wide oversized cut in heavy cotton jersey, with an open hem that hangs over the shoe.",
          (CREAM, BLACK, LILAC), _jg("Oversized", "Open Hem", "Cotton", YES, NO),
          _jgp("oversized", "open", "High", "yes", "no"), "High"),
    _jrow("JGGWCR", "Cargo Joggers with Pockets", "Larkmoor", _WJ, 32.0,
          "Relaxed twill joggers with patch pockets on the thigh and a snug cuffed ankle.",
          (KHAKI, BLACK), _jg("Relaxed", "Elasticated", "Twill", YES, YES),
          _jgp("relaxed", "elastic", "Mid", "yes", "yes"), "Mid"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Shorts: the style is drawn; the waist type (Belted draws four belt loops) is stated.
# --------------------------------------------------------------------------


def _sh(style: str, length: str, fabric: str, waist: tuple, pockets: str = YES) -> tuple:
    return (_a("shorts_style", "Style", style), _a("garment_length", "Length", length),
            _a("fabric", "Fabric", fabric), *waist, *_pockets(pockets))  # fmt: skip


def _shp(length: str, style: str, pocket: str = "yes") -> tuple[tuple[str, str], ...]:
    return (("length", length), ("style", style), ("pocket", pocket))


_WS, _MS = ("Womens", "Shorts"), ("Mens", "Shorts")
SHORTS = (
    LRow("SHTDNW", "Denim Shorts", "Wrenfield", CL_, _WS, "Shorts", 22.0, "shorts",
         "Frayed-hem denim shorts with a zip fly and five pockets.", (LIGHT_WASH, MID_WASH),
         _sh("Denim", "Mid Length", "Denim", _waist("Zip")), _sizes(22.0),
         params=_shp("mid", "denim"), facts=_facts("High", "plain")),
    LRow("SHTDNM", "Mini Denim Shorts", "Larkmoor", CL_, _WS, "Shorts", 20.0, "shorts",
         "Short cut-off denim shorts with a high rise.", (LIGHT_WASH, BLACK_DENIM),
         _sh("Denim", "Mini", "Denim", _waist("Zip")), _sizes(20.0),
         params=_shp("mini", "denim"), facts=_facts("High", "plain")),
    LRow("SHTCHM", "Chino Shorts with Belt Loops", "Harbour & Pine", CL_, _MS, "Shorts", 26.0,
         "shorts", "Knee length cotton chino shorts with a flat front and belt loops.",
         (BEIGE, NAVY, GREEN), _sh("Chino", "Knee Length", "Cotton", _waist("Belted")),
         _sizes(26.0), params=_shp("knee", "chino"), facts=_facts("Mid", "plain")),
    LRow("SHTCRG", "Cargo Shorts", "Larkmoor", CL_, _MS, "Shorts", 28.0, "shorts",
         "Cotton ripstop shorts with a flapped pocket on each thigh and belt loops.",
         (KHAKI, BLACK, NAVY), _sh("Cargo", "Mid Length", "Cotton", _waist("Belted")),
         _sizes(28.0), params=_shp("mid", "cargo"), facts=_facts("Mid", "plain")),
    LRow("SHTTLR", "Tailored Pleated Shorts", CL, CL_, _WS, "Shorts", 34.0, "shorts",
         "Smart pleated shorts in a stretch suiting fabric, with a fly and belt loops.",
         (BLACK, BEIGE, NAVY_CHECK), _sh("Tailored", "Mid Length", "Polyester Blend",
                                          _waist("Belted")),
         _sizes(34.0), params=_shp("mid", "tailored"), facts=_facts("High", "plain")),
    LRow("SHTBRM", "Bermuda Shorts with Turned-Up Hem", "Wrenfield", CL_, _MS, "Shorts", 30.0,
         "shorts", "Knee length bermudas in a cotton twill, with a cuffed hem and belt loops.",
         (NAVY, KHAKI, GREEN_CHECK), _sh("Bermuda", "Knee Length", "Cotton", _waist("Belted")),
         _sizes(30.0), params=_shp("mini", "bermuda"), facts=_facts("Mid", "plain")),
    LRow("SHTSWW", "Sweat Shorts with Drawstring", HK, CL_, _WS, "Shorts", 16.0, "shorts",
         "Mini jersey shorts with an elastic waist and a drawstring.", (GREY_MARL, PINK, BLACK),
         _sh("Sweat", "Mini", "Cotton Jersey", _waist("Elastic", "Drawstring")), _sizes(16.0),
         params=_shp("mini", "sweat"), facts=_facts("High", "plain")),
    LRow("SHTSWM", "Sweat Shorts with Pockets", SW, CL_, _MS, "Shorts", 18.0, "shorts",
         "Mid length jersey shorts with an elastic waist, a drawstring and side pockets.",
         (GREY_MARL, NAVY, BLACK),
         _sh("Sweat", "Mid Length", "Cotton Jersey", _waist("Elastic", "Drawstring")),
         _sizes(18.0), params=_shp("mid", "sweat"), facts=_facts("Mid", "plain")),
)  # fmt: skip

# --------------------------------------------------------------------------
# Cycling shorts: padded or not (Padded draws the chamois pad), with or without pockets.
# --------------------------------------------------------------------------


def _cy(length: str, padding: str, pockets: str) -> tuple:
    """Cycling shorts are all close fitting: a compression fit (``leg_fit``), no fabric."""
    return (_a("leg_fit", "Leg fit", "Compression"), _a("garment_length", "Length", length),
            _a("padding", "Padding", padding), *_pockets(pockets))  # fmt: skip


def _cyp(length: str, rise: str, pad: str, pocket: str) -> tuple[tuple[str, str], ...]:
    return (("length", length), ("rise", rise), ("pad", pad), ("pocket", pocket))


_WC = ("Womens", "Sportswear", "Cycling Shorts")
_MC = ("Mens", "Sportswear", "Cycling Shorts")
CYCLING = (
    LRow("CYSWPD", "Padded Cycling Shorts", SW, CL_, _WC, "Cycling Shorts", 30.0,
         "cycling_shorts", "High rise cycling shorts with a padded chamois and flat seams, for "
         "long rides.", (BLACK, NAVY), _cy("Mid Length", "Padded", NO),
         _sizes(30.0), params=_cyp("mid", "mid", "yes", "no"), facts=_facts("High", "plain")),
    LRow("CYSWCP", "Compression Cycling Shorts", SW, CL_, _WC, "Cycling Shorts", 22.0,
         "cycling_shorts", "Close fitting compression shorts with a silicone gripper at each "
         "hem, for spin class and training.", (BLACK, PURPLE, TEAL),
         _cy("Mini", "Unpadded", NO), _sizes(22.0),
         params=_cyp("knee", "high", "no", "no"), facts=_facts("High", "plain")),
    LRow("CYSWPK", "Padded Cycling Shorts with Pockets", "Saltmarsh", CL_, _WC,
         "Cycling Shorts", 38.0, "cycling_shorts", "Knee length padded shorts with a mid rise "
         "and a pocket on each leg for a phone or keys.", (BLACK, GREY),
         _cy("Knee Length", "Padded", YES), _sizes(38.0),
         params=_cyp("knee", "mid", "yes", "yes"), facts=_facts("Mid", "plain")),
    LRow("CYMPAD", "Men's Padded Cycling Shorts", "Saltmarsh", CL_, _MC, "Cycling Shorts",
         34.0, "cycling_shorts", "Cycling shorts with a mid rise and a multi-density padded "
         "chamois.", (BLACK, NAVY, CHARCOAL), _cy("Mid Length", "Padded", NO),
         _sizes(34.0), params=_cyp("mid", "mid", "yes", "no"), facts=_facts("Mid", "plain")),
    LRow("CYMCMP", "Men's Compression Cycling Shorts", SW, CL_, _MC, "Cycling Shorts", 24.0,
         "cycling_shorts", "Short compression shorts that wick sweat and hold the muscle, "
         "with no pad.", (BLACK, BLUE),
         _cy("Mini", "Unpadded", NO), _sizes(24.0),
         params=_cyp("mini", "mid", "no", "no"), facts=_facts("Mid", "plain")),
    LRow("CYMKNE", "Men's Knee Length Padded Cycling Shorts with Pocket", "Bramblewood", CL_, _MC,
         "Cycling Shorts", 40.0, "cycling_shorts", "Longer padded cycling shorts with a high "
         "rise and a rear pocket.", (BLACK, GREEN),
         _cy("Knee Length", "Padded", YES), _sizes(40.0),
         params=_cyp("knee", "high", "yes", "yes"), facts=_facts("High", "plain")),
)  # fmt: skip

# --------------------------------------------------------------------------
# Skirts: the shape and the length are drawn; a tiered skirt states and draws three tiers.
# --------------------------------------------------------------------------


def _sk(
    shape: str, length: str, fabric: str, waist: str, lining: str = "Unlined", tiers: int = 0
) -> tuple:
    extra = (_count("tiers", "Tiers", tiers),) if tiers else ()
    return (_a("skirt_shape", "Shape", shape), _a("garment_length", "Length", length),
            _a("fabric", "Fabric", fabric), *_waist(waist),
            _a("lining", "Lining", lining), *extra)  # fmt: skip


_SKT = ("Womens", "Skirts")


# The drawing param is ``hem``: a SKU's own value of a drawing param key replaces the drawing's
# (export.drawing_spec). The SKU axis is ``fit_length`` (the Petite/Regular/Long fit), not
# ``length``: the Combined projection renames a bare ``length`` to ``garment_length``, which a
# skirt's style already states (gen#279).
def _skrow(code, title, brand, price, desc, colors, attrs, shape, length, pattern="plain"):
    return LRow(code, title, brand, CL_, _SKT, "Skirt", price, "skirt", desc, colors, attrs,
                _sizes(price), params=(("shape", shape), ("hem", length)),
                axis_key="fit_length", axis=_legs(), facts=_facts(None, pattern))  # fmt: skip


SKIRTS = (
    _skrow("SKTALN", "A-Line Cotton Midi Skirt", "Harbour & Pine", 24.0,
           "A flared cotton skirt that falls to mid calf, with a side zip.", (NAVY, CREAM, RED),
           _sk("A-Line", "Midi", "Cotton", "Zip", "Polyester"), "a_line", "midi"),
    _skrow("SKTPLT", "Pleated Satin Midi Skirt", "Wrenfield", 32.0,
           "Knife pleats in a fluid satin that catches the light, on an elastic waist.",
           (CHARCOAL, CREAM, GREEN), _sk("Pleated", "Midi", "Satin", "Elastic", "Polyester"),
           "pleated", "midi"),
    _skrow("SKTPNC", "Faux Leather Pencil Skirt", "Larkmoor", 30.0,
           "A straight faux leather skirt with a back slit, cut to the knee.", (BLACK, BROWN),
           _sk("Pencil", "Midi", "Faux Leather", "Zip", "Polyester"), "pencil", "midi"),
    _skrow("SKTWRP", "Cotton Wrap Maxi Skirt", CL, 36.0,
           "A floor-skimming wrap skirt with an overlap and a tie at the waist.",
           (BEIGE, NAVY, TEAL), _sk("Wrap", "Maxi", "Cotton", "Tie"), "wrap", "maxi"),
    _skrow("SKTTRD", "Tiered Cotton Maxi Skirt", CL, 34.0,
           "Three gathered tiers of light cotton on an elastic waist.", (GREY_STRIPE, CREAM),
           _sk("Tiered", "Maxi", "Cotton", "Elastic", tiers=3), "tiered", "maxi", "stripe"),
    _skrow("SKTTNS", "Tennis Skirt with Built-In Shorts", SW, 20.0,
           "A short skirt with built-in shorts, for the court and the gym.",
           (WHITE, BLACK, NAVY), _sk("Tennis", "Mini", "Tricot", "Elastic", "Polyester"),
           "tennis", "mini"),
    _skrow("SKTDNM", "Denim Mini Skirt", "Wrenfield", 22.0,
           "A flared denim skirt with a zip front, cut well above the knee.",
           (LIGHT_WASH, MID_WASH, BLACK_DENIM), _sk("A-Line", "Mini", "Denim", "Zip"),
           "a_line", "mini"),
    _skrow("SKTSAT", "Satin Pleated Maxi Skirt", "Larkmoor", 38.0,
           "Long pleated satin that moves with every step, lined in soft jersey.",
           (PURPLE, BLACK, BEIGE), _sk("Pleated", "Maxi", "Satin", "Elastic", "Jersey"),
           "pleated", "maxi"),
)  # fmt: skip

ROWS = (*LEGGINGS, *JOGGERS, *SHORTS, *CYCLING, *SKIRTS)


def docs() -> list[dict]:
    """Every lower-body row's catalog document, type by type."""
    return [r.doc() for r in ROWS]
