"""School uniform shapes for the retail drawing kit (gen#205): four shapes, each its own.

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
school_shirt    a collared, buttoned shirt with long or      sleeve (long, short),
                short sleeves, a chest pocket and, for a     pack (1, 2, 3)
                multipack, that many stacked pack items
==============  ===========================================  ==========================

What a drawing shows is what the record states, and a test reads it back from the marks: the leg
width is the group ``leg-<fit>``, the hem ``hem-<length>``, a pocket is a ``pocket`` group, a fold
a ``pleat`` group, a strap a ``strap`` group, a button a ``button`` group and a pack item a
``pack-item`` group. A drawing never prints a size, an age or a pack count as text: a style's
sizes share one image per colorway. Every param is a string with a default, so each shape also
draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import LW, LW_DETAIL, Fill, _line, _path, register
from kit_garments import _dark
from kit_lowerbody import _circle, _group

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


def school_shirt(paint: str, fill: Fill, label: str | None, sleeve: str = "long", pack: str = "1") -> list[str]:
    """A school shirt: a pointed collar, a buttoned placket, a chest pocket and long or short
    sleeves; a multipack stacks one small pack item per shirt in the pack under the hem."""
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
    count = int(pack)
    if count > 1:
        for i in range(count):
            x, y = 158 + i * 8, 356 - i * 5
            out.append(_group("pack-item", [_path(f"M{x},{y} L{x + 52},{y} L{x + 52},{y + 24} L{x},{y + 24} Z", paint, LW_DETAIL + 0.6)]))
    return out


SHAPES = {
    "school_trousers": school_trousers, "school_skirt": school_skirt,
    "school_pinafore": school_pinafore, "school_shirt": school_shirt,
}  # fmt: skip
register(SHAPES)
