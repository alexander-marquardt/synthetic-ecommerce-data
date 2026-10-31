"""School uniform shapes for the retail drawing kit (gen#205): eight shapes, each its own.

==============  ===========================================  ==========================
shape           draws                                        params
==============  ===========================================  ==========================
school_trousers straight legs with a front crease, two       fit (regular, slim, plus),
                pockets, a fly and a waistband button        length (regular, longer)
school_skirt    a waistband and a pleated, plain A-line or   style (pleated, a_line,
                kilt skirt (the kilt wraps, with a pin       kilt), length (knee, midi)
                and a fringe)
school_pinafore a blouse under a bib front with two straps   style (pinafore,
                and a pleated skirt, or a jumper dress with  jumper_dress)
                a scoop neck and no straps
school_shirt    a collared, buttoned shirt with long or      sleeve (long, short)
                short sleeves and a chest pocket
school_polo     a ribbed polo collar over a two-button       sleeve (short, long)
                placket, ribbed cuffs and a split hem
school_socks    a pair of ribbed socks, or a pair of tights  height (ankle, knee, tights)
school_blazer   a two-button jacket with lapels, flap        fit (regular, slim, plus),
                pockets and a chest pocket, which shows the  badge (outline, none)
                outline of a sewn-on badge when badge-ready
pe_shorts       a gathered elastic waist and short wide      leg (short, mid)
                legs with a stitched hem
==============  ===========================================  ==========================

What a drawing shows is what the record states, and a test reads it back from the marks: the leg
width is the group ``leg-<fit>``, the hem ``hem-<length>``, a pocket is a ``pocket`` group, a fold
a ``pleat`` group, a strap a ``strap`` group, a button a ``button`` group, a rib a ``rib`` group,
a sock's height ``height-<height>``, a blazer's badge a ``badge`` group and a pack item a
``pack-item`` group. A drawing never prints a size, an age or a pack count as text: a style's
sizes share one image per colorway. Every param is a string with a default, so each shape also
draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import LW, LW_DETAIL, Fill, _line, _path, register
from synthetic_ecommerce_data.domains.retail.kit_garments import _dark, _polo_collar
from synthetic_ecommerce_data.domains.retail.kit_lowerbody import _circle, _group
from synthetic_ecommerce_data.domains.retail.kit_more import _HEEL, _TOE

PAPER_WHITE = "#f4f1ea"
GOLD = "#d6b56a"

# --------------------------------------------------------------------------
# Trousers
# --------------------------------------------------------------------------

#: fit -> (hip half-width, leg width at the hem): a slim leg is narrow, a plus fit roomy.
TROUSER_FIT = {"regular": (62, 50), "slim": (56, 40), "plus": (74, 62)}
TROUSER_HEM = {"regular": 330, "longer": 362}
WAIST_TOP, WAIST_BOTTOM, CROTCH = 62, 84, 190
INSEAM_GAP = 8


def school_trousers(paint: str, fill: Fill, label: str | None, fit: str = "regular", length: str = "regular") -> list[str]:
    """Straight school trousers: a crease down each leg, two slant pockets, a fly and a button."""
    hip, leg = TROUSER_FIT[fit]
    hem = TROUSER_HEM[length]
    inner = INSEAM_GAP
    outer = inner + leg
    top = 200 - hip
    body = (f"M{top},{WAIST_BOTTOM} L{200 + hip},{WAIST_BOTTOM} L{200 + outer},{hem} L{200 + inner},{hem} "
            f"L200,{CROTCH} L{200 - inner},{hem} L{200 - outer},{hem} Z")  # fmt: skip
    out = [_group(f"leg-{fit}", [_path(body, paint)])]
    for sign in (1, -1):
        x0, x1 = 200 + sign * (hip + 2) / 2, 200 + sign * (outer + inner) / 2
        out.append(_group("crease", [_line(f"M{x0:.1f},{WAIST_BOTTOM + 20} L{x1:.1f},{hem - 8}", 1.4, ' stroke-opacity=".55"')]))
        edge = 200 + sign * hip
        pocket = f"M{edge - sign * 2},{WAIST_BOTTOM + 4} Q{edge - sign * 6},{WAIST_BOTTOM + 30} {edge - sign * 28},{WAIST_BOTTOM + 38}"
        out.append(_group("pocket", [_line(pocket, 1.8)]))
    out.append(_group(f"hem-{length}", [_line(f"M{200 - outer + 1},{hem - 10} L{200 - inner - 1},{hem - 10} M{200 + inner + 1},{hem - 10} L{200 + outer - 1},{hem - 10}", 1.2, ' stroke-opacity=".6"'),
                                       _dark(f"M{200 - outer},{hem - 10} L{200 - inner},{hem - 10} L{200 - inner},{hem} L{200 - outer},{hem} Z M{200 + inner},{hem - 10} L{200 + outer},{hem - 10} L{200 + outer},{hem} L{200 + inner},{hem} Z", 0.08)]))  # fmt: skip
    band = f"M{top},{WAIST_TOP} L{200 + hip},{WAIST_TOP} L{200 + hip},{WAIST_BOTTOM} L{top},{WAIST_BOTTOM} Z"
    out.append(_group("waistband", [_path(band, paint, LW), _dark(band, 0.12), _circle(207, 73, 3.4, GOLD, 1.2)]))
    out.append(_line(f"M200,{WAIST_BOTTOM} L200,{WAIST_BOTTOM + 52} Q206,{WAIST_BOTTOM + 62} 212,{WAIST_BOTTOM + 58}", 1.4, ' stroke-opacity=".6"'))
    return out


# --------------------------------------------------------------------------
# Skirts
# --------------------------------------------------------------------------

SKIRT_HEM = {"knee": 250, "midi": 312}
SKIRT_STYLES = ("pleated", "a_line", "kilt")
PLEATS = {"pleated": 13, "kilt": 9, "a_line": 0}  # n - 1 pleat lines are drawn
SKIRT_TOP, SKIRT_BAND = 60, 84


def school_skirt(paint: str, fill: Fill, label: str | None, style: str = "pleated", length: str = "knee") -> list[str]:
    """A school skirt: knife pleats, a plain A-line flare with darts, or a wrapped kilt with a pin
    and a fringed overlap."""
    hem = SKIRT_HEM[length]
    span = hem - SKIRT_BAND
    flare = {"pleated": 40 + span * 0.30, "a_line": 34 + span * 0.30, "kilt": 28 + span * 0.18}[style]
    half_hem = 52 + flare
    body = f"M148,{SKIRT_BAND} L252,{SKIRT_BAND} L{200 + half_hem:.1f},{hem} Q200,{hem + 10} {200 - half_hem:.1f},{hem} Z"
    out = [_group(f"hem-{length}", [_path(body, paint)])]
    n = PLEATS[style]
    for k in range(1, n):
        t = k / n
        x0, x1 = 148 + 104 * t, 200 - half_hem + 2 * half_hem * t
        out.append(_group("pleat", [_line(f"M{x0:.1f},{SKIRT_BAND + 2} L{x1:.1f},{hem - 3}", 1.2, ' stroke-opacity=".6"')]))
    if style == "a_line":
        out.append(_line(f"M176,{SKIRT_BAND} Q174,{SKIRT_BAND + 24} 180,{SKIRT_BAND + 40} M224,{SKIRT_BAND} Q226,{SKIRT_BAND + 24} 220,{SKIRT_BAND + 40}", 1.4, ' stroke-opacity=".6"'))
    if style == "kilt":
        edge = 172
        flap = f"M{edge},{SKIRT_BAND} L252,{SKIRT_BAND} L{200 + half_hem:.1f},{hem} L{edge - 14},{hem} Z"
        out += [_path(flap, paint, LW_DETAIL + 0.6), _dark(flap, 0.1)]
        fringe = " ".join(f"M{edge - 14 + 0.0:.1f},{y} L{edge - 20:.1f},{y + 2}" for y in range(SKIRT_BAND + 6, hem - 4, 12))
        out.append(_group("fringe", [_line(fringe, 1.4)]))
        out.append(_group("kilt-pin", [_line(f"M{edge + 6},{SKIRT_BAND + 40} L{edge + 34},{SKIRT_BAND + 52}", 2.6, stroke=GOLD), _circle(edge + 6, SKIRT_BAND + 40, 4.2, GOLD, 1.2)]))
    band = f"M148,{SKIRT_TOP} L252,{SKIRT_TOP} L252,{SKIRT_BAND} L148,{SKIRT_BAND} Z"
    out.append(_group("waistband", [_path(band, paint, LW), _dark(band, 0.12), _circle(236, 72, 3.4, GOLD, 1.2)]))
    return out


# --------------------------------------------------------------------------
# Pinafores and jumper dresses
# --------------------------------------------------------------------------

PINAFORE_STYLES = ("pinafore", "jumper_dress")


def _blouse() -> str:
    """The white blouse under the dress: short sleeves, a rounded collar and a row of buttons."""
    body = "M150,86 L250,86 L254,196 L146,196 Z"
    sleeves = "M150,86 L118,112 L128,140 L152,126 Z M250,86 L282,112 L272,140 L248,126 Z"
    collar = "M172,60 L200,84 L228,60 L236,72 L200,98 L164,72 Z"
    return _group("blouse", [_path(sleeves, PAPER_WHITE, LW_DETAIL + 0.6), _path(body, PAPER_WHITE, LW_DETAIL + 0.6), _path(collar, PAPER_WHITE, LW_DETAIL + 0.6)])


def school_pinafore(paint: str, fill: Fill, label: str | None, style: str = "pinafore") -> list[str]:
    """A blouse under a school dress: a pinafore has a squared bib and two straps, a jumper dress a
    scoop neck cut from the body itself; both end in a pleated skirt."""
    waist, hem = 176, 336
    out = [_blouse()]
    skirt = f"M146,{waist} L254,{waist} L{200 + 96},{hem} Q200,{hem + 10} {200 - 96},{hem} Z"
    out.append(_path(skirt, paint))
    for k in range(1, 11):
        t = k / 11
        out.append(_group("pleat", [_line(f"M{146 + 108 * t:.1f},{waist + 2} L{104 + 192 * t:.1f},{hem - 3}", 1.2, ' stroke-opacity=".6"')]))
    if style == "pinafore":
        bib = f"M162,100 L238,100 L246,{waist + 2} L154,{waist + 2} Z"
        out.append(_group("bib", [_path(bib, paint), _dark(bib, 0.06), _line("M178,128 L222,128 L222,150 L178,150 Z", 1.4, ' stroke-opacity=".55"')]))
        for sign, x in ((1, 168), (-1, 232)):
            out.append(_group("strap", [_path(f"M{x - 6},102 L{x + 6},102 L{x + sign * 10 + 4},60 L{x + sign * 10 - 8},60 Z", paint, LW_DETAIL + 0.8)]))
    else:
        body = f"M158,76 Q200,110 242,76 L252,96 L246,{waist + 2} L154,{waist + 2} L148,96 Z"
        out.append(_path(body, paint))
        out.append(_group("scoop", [_line("M158,76 Q200,112 242,76", 2.0)]))
        out.append(_line("M154,98 Q160,120 156,150 M246,98 Q240,120 244,150", 1.2, ' stroke-opacity=".5"'))
    out.append(_line(f"M146,{waist} L254,{waist}", LW_DETAIL + 0.6))
    return out


# --------------------------------------------------------------------------
# Shirts
# --------------------------------------------------------------------------

SLEEVE_END = {"long": 292, "short": 160}


def school_shirt(paint: str, fill: Fill, label: str | None, sleeve: str = "long") -> list[str]:
    """A school shirt: a pointed collar, a buttoned placket, a chest pocket and long or short
    sleeves."""
    end = SLEEVE_END[sleeve]
    sleeves = []
    for sign in (1, -1):
        x = lambda dx, sign=sign: 200 + sign * dx  # noqa: E731
        cuff = 12 if sleeve == "long" else 6
        sl = f"M{x(70)},84 L{x(112)},{100} L{x(124 if sleeve == 'long' else 112)},{end} L{x(124 - 36 if sleeve == 'long' else 112 - 28)},{end} L{x(62)},148 Z"
        sleeves.append(_path(sl, paint))
        sleeves.append(_line(f"M{x(124 if sleeve == 'long' else 112)},{end - cuff} L{x(124 - 36 if sleeve == 'long' else 112 - 28)},{end - cuff}", 1.4, ' stroke-opacity=".6"'))
    out = [_group(f"sleeve-{sleeve}", sleeves)]
    body = "M162,70 L238,70 L270,84 L266,330 Q200,340 134,330 L130,84 Z"
    out += [_path(body, paint), _line("M200,96 L200,328", 1.2, ' stroke-opacity=".5"')]
    for k in range(6):
        out.append(_group("button", [_circle(200, 112 + k * 38, 3.6, PAPER_WHITE, 1.2)]))
    out.append(_line("M222,146 L252,146 L252,176 L222,176 Z", 1.4, ' stroke-opacity=".6"'))
    collar = "M162,70 L200,100 L238,70 L246,58 L200,64 L154,58 Z"
    out.append(_group("collar", [_path(collar, paint, LW), _dark(collar, 0.1), _line("M200,64 L200,100", 1.2)]))
    return out


# --------------------------------------------------------------------------
# Polo shirts
# --------------------------------------------------------------------------

POLO_SLEEVE_END = {"short": 160, "long": 292}
RIB_OPACITY = ' stroke-opacity=".55"'


def school_polo(paint: str, fill: Fill, label: str | None, sleeve: str = "short") -> list[str]:
    """A school polo: a folded ribbed collar over a two-button placket, ribbed cuffs, long or short
    sleeves and a hem split at each side."""
    end = POLO_SLEEVE_END[sleeve]
    outer, inner = (124, 88) if sleeve == "long" else (112, 84)
    sleeves, cuffs = [], []
    for sign in (1, -1):
        out_x, in_x = 200 + sign * outer, 200 + sign * inner
        sleeves.append(_path(f"M{200 + sign * 70},84 L{200 + sign * 112},100 L{out_x},{end} L{in_x},{end} L{200 + sign * 62},148 Z", paint))
        ticks = " ".join(f"M{in_x + (out_x - in_x) * k / 6:.1f},{end - 12} L{in_x + (out_x - in_x) * k / 6:.1f},{end}" for k in range(1, 6))
        cuffs.append(_group("rib", [_line(f"M{out_x},{end - 12} L{in_x},{end - 12} {ticks}", 1.2, RIB_OPACITY)]))
    out = [_group(f"sleeve-{sleeve}", sleeves), _path("M162,70 L238,70 L270,84 L266,322 L232,334 L168,334 L134,322 L130,84 Z", paint)]
    out.append(_group("vent", [_line("M134,322 L142,296 M266,322 L258,296", 1.6)]))
    out += cuffs
    out.append(_group("placket", _polo_collar(paint)))
    collar_ticks = " ".join(f"M{x},{y} L{x + 10},{y - 8}" for x, y in ((162, 82), (170, 92), (178, 102)))
    mirrored = " ".join(f"M{400 - x},{y} L{390 - x},{y - 8}" for x, y in ((162, 82), (170, 92), (178, 102)))
    out.append(_group("rib", [_line(f"{collar_ticks} {mirrored}", 1.2, RIB_OPACITY)]))
    return out


# --------------------------------------------------------------------------
# Socks and tights
# --------------------------------------------------------------------------

#: height -> where the cuff starts in the sock's own frame (its heel is at y 150), and where that
#: frame sits on the sheet, so the pair is centered whatever the leg's length.
SOCK_TOP = {"ankle": (86, 30), "knee": (-30, 106)}
SOCK_HEIGHTS = (*SOCK_TOP, "tights")


def _school_sock(paint: str, top: int, transform: str) -> str:
    """One sock with a ribbed cuff, cut off at ``top``: the heel and toe are the sock kit's own."""
    cuff = f"M0,{top} L60,{top} L60,{top + 24} L0,{top + 24} Z"
    ribs = " ".join(f"M{x},{top + 4} L{x},{top + 22}" for x in range(8, 60, 8))
    parts = [
        _path(f"M0,{top} L60,{top} L60,128 Q62,146 80,152 L142,170 Q166,178 162,198 Q156,216 132,212 L30,190 Q0,182 0,150 Z", paint),
        _path(cuff, paint, LW_DETAIL),
        _dark(cuff, 0.14),
        _group("rib", [_line(ribs, 1.0, ' stroke-opacity=".5"')]),
        _dark(_HEEL, 0.2),
        _dark(_TOE, 0.2),
        _line("M0,146 Q34,164 46,193 M142,170 Q126,190 132,212", 1.2, ' stroke-opacity=".6"'),
    ]
    return f'<g class="sock" transform="{transform}">{"".join(parts)}</g>'


def _school_tights(paint: str, lone: str) -> list[str]:
    """A pair of tights laid flat: a ribbed waistband over two legs that end in feet. ``lone``
    folds the pair down its middle, so a pack fans one leg each rather than a tangle of two."""
    leg = "M200,84 L146,84 Q140,190 158,300 Q150,338 126,346 Q118,362 148,362 L176,358 Q186,330 186,300 Q192,230 200,188 Z"
    other = "M200,84 L254,84 Q260,190 242,300 Q250,338 274,346 Q282,362 252,362 L224,358 Q214,330 214,300 Q208,230 200,188 Z"
    foot = "M126,346 Q118,362 148,362 L176,358 Q180,348 182,338 Q150,338 126,346 Z"
    other_foot = "M274,346 Q282,362 252,362 L224,358 Q220,348 218,338 Q250,338 274,346 Z"
    right = 200 if lone else 254
    band = f"M146,60 L{right},60 L{right},84 L146,84 Z"
    ribs = " ".join(f"M{x},64 L{x},82" for x in range(154, right - 4, 8))
    legs = [_path(leg, paint)] if lone else [_path(leg, paint), _path(other, paint)]
    feet = [_dark(foot, 0.2)] if lone else [_dark(foot, 0.2), _dark(other_foot, 0.2)]
    return [*legs, _path(band, paint, LW_DETAIL), _dark(band, 0.14), _group("rib", [_line(ribs, 1.0, ' stroke-opacity=".5"')]), *feet]


def school_socks(paint: str, fill: Fill, label: str | None, height: str = "ankle", lone: str = "") -> list[str]:
    """School hosiery by ``height``: a pair of ankle or knee socks, or tights. A pack is
    :mod:`pack_copies`', which fans ``lone`` socks, one for a pair, as :func:`kit_more.socks` does."""
    if height == "tights":
        return [_group("height-tights", _school_tights(paint, lone))]
    top, y = SOCK_TOP[height]
    socks = [_school_sock(paint, top, f"translate(86 {y}) scale(1.2)")]
    if not lone:
        socks.insert(0, _school_sock(paint, top, f"translate(132 {y - 34}) scale(1.2)"))
    return [_group(f"height-{height}", socks)]


# --------------------------------------------------------------------------
# Blazers
# --------------------------------------------------------------------------

#: fit -> how far the body's hem reaches from the center line.
BLAZER_HEM = {"regular": 92, "slim": 80, "plus": 106}
BLAZER_BADGES = ("outline", "none")
_SHIELD = "M236,158 L264,158 L264,176 Q264,188 250,194 Q236,188 236,176 Z"


def school_blazer(paint: str, fill: Fill, label: str | None, fit: str = "regular", badge: str = "outline") -> list[str]:
    """A two-button school blazer: notched lapels over a shirt, two flap pockets and a chest pocket
    that shows the outline of a sewn-on badge when the style is badge-ready."""
    hem = BLAZER_HEM[fit]
    left, right = 200 - hem, 200 + hem
    sleeves = "M132,74 L92,108 L78,318 L114,324 L132,160 Z M268,74 L308,108 L322,318 L286,324 L268,160 Z"
    body = f"M160,56 L240,56 L272,74 L{right},344 L{left},344 L128,74 Z"
    out = [_path(sleeves, paint), _path(body, paint), _dark(sleeves, 0.06)]
    out.append(_group("shirt", [_path("M172,56 L228,56 L200,214 Z", PAPER_WHITE, LW_DETAIL + 0.6)]))
    out.append(_group("lapel", [_path("M170,54 L200,214 L156,146 L138,126 L156,108 Z", paint, LW_DETAIL + 0.8), _path("M230,54 L200,214 L244,146 L262,126 L244,108 Z", paint, LW_DETAIL + 0.8)]))
    out.append(_line("M200,214 L200,344", 1.4))
    for y in (232, 272):
        out.append(_group("button", [_circle(206, y, 4.6, GOLD, 1.2)]))
    for x in (132, 228):
        out.append(_group("pocket", [_path(f"M{x},268 L{x + 44},268 L{x + 44},284 L{x},284 Z", paint, LW_DETAIL + 0.4), _dark(f"M{x},268 L{x + 44},268 L{x + 44},284 L{x},284 Z", 0.08)]))
    chest = "M230,150 L270,150 L270,198 L230,198 Z"
    out.append(_group("chest-pocket", [_line(chest, 1.4)]))
    if badge == "outline":
        out.append(_group("badge", [_line(_SHIELD, 1.6, stroke=GOLD)]))
    return out


# --------------------------------------------------------------------------
# PE shorts
# --------------------------------------------------------------------------

PE_HEM = {"short": 276, "mid": 334}
PE_TOP, PE_BAND, PE_CROTCH = 90, 122, 196


def pe_shorts(paint: str, fill: Fill, label: str | None, leg: str = "short") -> list[str]:
    """PE shorts: wide legs ending ``short`` or ``mid`` over a stitched hem, under a gathered
    elastic waist."""
    hem = PE_HEM[leg]
    body = f"M122,{PE_BAND} L278,{PE_BAND} L320,{hem} L210,{hem} L200,{PE_CROTCH} L190,{hem} L80,{hem} Z"
    out = [_group(f"leg-{leg}", [_path(body, paint)])]
    out.append(_group("hem", [_line(f"M84,{hem - 10} L190,{hem - 10} M210,{hem - 10} L316,{hem - 10}", 1.2, ' stroke-dasharray="4 3"')]))
    band = f"M122,{PE_TOP} L278,{PE_TOP} L278,{PE_BAND} L122,{PE_BAND} Z"
    out.append(_group("waistband", [_path(band, paint, LW), _dark(band, 0.12)]))
    gathers = " ".join(f"M{x},{PE_TOP + 4} L{x},{PE_BAND - 4}" for x in range(130, 274, 8))
    out.append(_group("elastic", [_line(gathers, 1.4)]))
    return out


SHAPES = {
    "school_trousers": school_trousers, "school_skirt": school_skirt,
    "school_pinafore": school_pinafore, "school_shirt": school_shirt,
    "school_polo": school_polo, "school_socks": school_socks,
    "school_blazer": school_blazer, "pe_shorts": pe_shorts,
}  # fmt: skip
register(SHAPES)
