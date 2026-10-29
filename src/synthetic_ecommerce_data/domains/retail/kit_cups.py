"""Cup shapes for the retail drawing kit (gen#620).

Every cup kind of the catalogue has a drawing of its own: a shopper who searches ``cup`` sees a
tumbler, a paper cup, a measuring jug and a baby's sippy cup as the different things they are, not
the one mug shape the first cups shared. Outlines are the kit's ink, and the record's fill (color
and pattern) paints the main surface. A mug keeps ``mug`` in :mod:`kit_surfaces`.

===============  =============================================  ==========================
shape            draws                                          params
===============  =============================================  ==========================
tumbler          a tall insulated tumbler with a sliding lid    lid (slide, none)
tea_cup          a tea cup with a handle, on its saucer         (none)
travel_cup       a tapered cup with a domed sip lid and grip    grip (band, plain)
espresso_cup     two small espresso cups on saucers             (none)
party_cup        a tapered plastic cup with a rolled rim,       stack (single, stacked)
                 alone or with a second cup nested in it
paper_cup        a paper cup with a seam, a printed band and    band (printed, plain)
                 a curled lip
sippy_cup        a toddler's cup: two handles and a spout lid   handles (two, none)
measuring_cup    a measuring jug with a spout, a handle and     marks (metric, plain)
                 graduation marks
===============  =============================================  ==========================

A drawing never prints a size, a volume or a count: a style's SKUs share one image per colorway.
Every param is a string with a default, so each shape also draws bare. The lid, the saucer's
coffee and a sleeve's band are never the product's color; the fill paints the main surface only.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_decor import _ell, _label

LID = "#f4f1ea"
COFFEE = "#5a3b28"
SAUCER = "#f4f1ea"


def tumbler(paint: str, fill: Fill, label: str | None, lid: str = "slide") -> list[str]:
    """A tall insulated tumbler; ``slide`` shows a sliding lid with its slot, ``none`` an open top."""
    dark = _shade(fill.base, 0.3)
    out = [
        _path("M112,112 L288,112 L270,338 Q268,350 254,350 L146,350 Q132,350 130,338 Z", paint),
        _line("M120,214 L280,214", 2.4, ' stroke-opacity=".45"'),
        _highlight("M128,138 L140,326", 6, 0.4),
    ]
    if lid.lower() == "none":
        out.append(_ell(200, 112, 88, 14, _tint(fill.base, 0.25)))
    else:
        out += [
            _path("M106,112 L294,112 L294,88 Q294,76 282,76 L118,76 Q106,76 106,88 Z", LID),
            _path("M150,94 L250,94 L250,100 L150,100 Z", dark, 2.4),
            _line("M168,76 L168,64 Q168,58 176,58 L224,58 Q232,58 232,64 L232,76", 3.4),
        ]
    return _label(out, label)


def tea_cup(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A tea cup with a ring handle on a saucer."""
    out = [
        _ell(200, 312, 150, 24, SAUCER),
        _ell(200, 306, 96, 12, _tint(fill.base, 0.35), 2.4),
        _path("M290,176 Q352,172 350,222 Q348,266 284,262 L286,242 Q324,244 326,222 Q328,198 288,198 Z", _tint(fill.base, 0.1) if fill.base.startswith("#") else paint),
        _path("M96,168 L304,168 Q304,230 270,272 Q246,300 200,302 Q154,300 130,272 Q96,230 96,168 Z", paint),
        _ell(200, 168, 104, 18, LID),
        _ell(200, 170, 88, 12, COFFEE, 2.4),
        _highlight("M114,196 Q120,244 150,276", 5, 0.4),
    ]
    return _label(out, label)


def travel_cup(paint: str, fill: Fill, label: str | None, grip: str = "band") -> list[str]:
    """A tapered travel cup with a domed sip lid; ``band`` adds a grip sleeve around the middle."""
    dark = _shade(fill.base, 0.3)
    out = [
        _path("M114,148 L286,148 L262,340 Q260,350 248,350 L152,350 Q140,350 138,340 Z", paint),
    ]
    if grip.lower() != "plain":
        out.append(_path("M122,208 L278,208 L270,290 L130,290 Z", dark, 2.6))
    out += [
        _path("M104,148 L296,148 L296,130 Q296,114 280,112 Q262,92 200,92 Q138,92 120,112 Q104,114 104,130 Z", LID),
        _ell(236, 104, 24, 7, dark, 2.4),
        _line("M104,148 L296,148", 3.4),
        _highlight("M126,170 L138,330", 6, 0.4),
    ]
    return _label(out, label)


def _small_cup(cx: float, paint: str, base: str) -> list[str]:
    """One espresso cup on its saucer, centered on ``cx``."""
    return [
        _ell(cx, 318, 78, 14, SAUCER),
        _path(f"M{cx + 46},232 Q{cx + 84},228 {cx + 82},256 Q{cx + 80},282 {cx + 40},278 L{cx + 42},266 Q{cx + 62},268 {cx + 64},254 Q{cx + 64},242 {cx + 44},244 Z", _tint(base, 0.1) if base.startswith("#") else paint),
        _path(f"M{cx - 56},218 L{cx + 56},218 Q{cx + 54},290 {cx + 22},308 L{cx - 22},308 Q{cx - 54},290 {cx - 56},218 Z", paint),
        _ell(cx, 218, 56, 10, LID),
        _ell(cx, 219, 46, 6, COFFEE, 2.2),
    ]


def espresso_cup(paint: str, fill: Fill, label: str | None) -> list[str]:
    """Two small espresso cups on saucers, the second a little behind the first."""
    out = [*_small_cup(104, paint, fill.base), *_small_cup(272, paint, fill.base)]
    return _label(out, label)


def party_cup(paint: str, fill: Fill, label: str | None, stack: str = "single") -> list[str]:
    """A tapered plastic party cup with a rolled rim; ``stacked`` nests a second cup in it."""
    out: list[str] = []
    if stack.lower() == "stacked":
        out.append(_path("M110,64 L290,64 L262,250 L138,250 Z", _tint(fill.base, 0.2) if fill.base.startswith("#") else paint))
    out += [
        _path("M92,126 L308,126 L274,340 Q272,350 260,350 L140,350 Q128,350 126,340 Z", paint),
        _line("M100,184 L300,184 M108,238 L292,238 M116,292 L284,292", 2.2, ' stroke-opacity=".35"'),
        _path("M86,126 L314,126 L314,110 Q314,102 306,102 L94,102 Q86,102 86,110 Z", _tint(fill.base, 0.25) if fill.base.startswith("#") else paint),
        _highlight("M112,152 L134,330", 6, 0.4),
    ]
    return _label(out, label)


def paper_cup(paint: str, fill: Fill, label: str | None, band: str = "printed") -> list[str]:
    """A paper cup: a side seam, a curled lip and (``printed``) a band of the product's color."""
    body = "#fbfaf6"
    out = [
        _path("M100,120 L300,120 L268,340 Q266,350 254,350 L146,350 Q134,350 132,340 Z", body),
        _line("M296,140 L266,330", 2.4, ' stroke-opacity=".5"'),
    ]
    if band.lower() == "plain":
        out.append(_line("M108,190 L292,190", 2.4, ' stroke-opacity=".4"'))
    else:
        out.append(_path("M110,190 L290,190 L280,274 L120,274 Z", paint))
    out += [
        _path("M94,120 L306,120 Q306,102 296,100 L104,100 Q94,102 94,120 Z", _tint(fill.base, 0.3) if fill.base.startswith("#") else paint),
        _line("M94,120 L306,120", 3.4),
        _highlight("M118,142 L136,326", 5, 0.5),
    ]
    return _label(out, label)


def sippy_cup(paint: str, fill: Fill, label: str | None, handles: str = "two") -> list[str]:
    """A toddler's cup: a rounded body, a spout lid and (``two``) a handle on each side."""
    dark = _shade(fill.base, 0.3)
    out: list[str] = []
    if handles.lower() != "none":
        out += [
            _line("M118,200 Q58,198 62,252 Q66,296 122,290", 16),
            _line("M282,200 Q342,198 338,252 Q334,296 278,290", 16),
            _line("M118,200 Q58,198 62,252 Q66,296 122,290", 9, "", _tint(fill.base, 0.2) if fill.base.startswith("#") else paint),
            _line("M282,200 Q342,198 338,252 Q334,296 278,290", 9, "", _tint(fill.base, 0.2) if fill.base.startswith("#") else paint),
        ]
    out += [
        _path("M118,160 L282,160 Q298,250 280,330 Q276,350 254,350 L146,350 Q124,350 120,330 Q102,250 118,160 Z", paint),
        _path("M112,160 L288,160 L288,142 Q288,128 274,128 L126,128 Q112,128 112,142 Z", dark, 2.8),
        _path("M170,128 Q170,96 188,84 L212,84 Q230,96 230,128 Z", LID),
        _path("M188,84 Q188,60 200,58 Q212,60 212,84 Z", dark, 2.6),
        _highlight("M134,186 Q126,250 134,320", 5, 0.4),
    ]
    return _label(out, label)


def measuring_cup(paint: str, fill: Fill, label: str | None, marks: str = "metric") -> list[str]:
    """A measuring jug: a pouring spout, a handle and (``metric``) graduation marks down the side."""
    out = [
        _path("M284,132 Q352,128 350,196 Q348,262 282,262 L284,240 Q322,240 324,196 Q326,156 284,156 Z", _tint(fill.base, 0.1) if fill.base.startswith("#") else paint),
        _path("M80,100 L96,112 L96,124 L282,124 L270,334 Q268,346 254,346 L128,346 Q114,346 112,334 L100,150 Q96,126 80,100 Z", paint),
        _ell(189, 124, 93, 11, LID, 2.4),
    ]
    if marks.lower() != "plain":
        for i, y in enumerate((186, 232, 278, 324)):
            half = 30 if i % 2 == 0 else 18
            out.append(_line(f"M{140 + (4 - i) * 2},{y} L{140 + (4 - i) * 2 + half},{y}", 2.4, ' stroke-opacity=".7"'))
    out.append(_highlight("M122,160 L132,322", 5, 0.4))
    return _label(out, label)


SHAPES = {
    "tumbler": tumbler, "tea_cup": tea_cup, "travel_cup": travel_cup, "espresso_cup": espresso_cup,
    "party_cup": party_cup, "paper_cup": paper_cup, "sippy_cup": sippy_cup, "measuring_cup": measuring_cup,
}  # fmt: skip
register(SHAPES)
