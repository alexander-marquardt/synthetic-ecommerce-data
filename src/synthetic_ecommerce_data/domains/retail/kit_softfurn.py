"""Soft furnishing shapes for the retail drawing kit (gen#204).

Each type of :mod:`softfurn_rows` has its own flat drawing in the kit's house style: outlines in
the kit's ink, the record's fill (solid color or pattern) on the product's main surface.

==============  ==============================================  ==========================
shape           draws                                           params
==============  ==============================================  ==========================
curtains        a pair of panels with folds on a pole           heading (eyelet, pencil,
                                                                tab), lined (yes, no)
blind           a window frame with the blind fitted            kind (roller, roman,
                                                                venetian, vertical)
rug             a floor covering in perspective: a rug, a       form (rectangle, round,
                doormat or a kitchen mat, a kids' rug with      runner, doormat,
                its motif                                       kitchen_mat), pile (flat,
                                                                shag, short), motif (none,
                                                                road, hopscotch, stars)
draped_throw    a throw over a sofa arm                         edge (fringe, bound,
                                                                pompom)
bath_mat        a mat in perspective on the floor               texture (ribbed, tufted,
                                                                slatted)
shower_curtain  a curtain on a rail with ring clips             hem (plain, weighted)
==============  ==============================================  ==========================

A drawing never prints a size: a style's SKUs share one image per colorway. Every param is a
string with a default, so each shape also draws bare. Marked groups (``class="ring"``,
``"pleat"``, ``"tab"``, ``"slat"``, ``"louvre"``, ``"fringe"``, ``"pompom"``, ``"tuft"``,
``"weight"``, ``"clip"``) let ``tests/test_retail_softfurn_204.py`` count what a param draws.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _panel,
    _path,
    _shade,
    _tint,
    register,
)

POLE = "#8d949c"
WOOD = "#b98b55"
FRAME = "#e9e4d8"
LINING = "#f1ece0"
#: How many of each marked part a param draws (``tests/test_retail_softfurn_204.py`` reads them).
RINGS, CLIPS, SLATS, LOUVRES, WEIGHTS = 7, 9, 12, 9, 8


def _ell(cx: float, cy: float, rx: float, ry: float, fill: str, width: float = LW, cls: str = "") -> str:
    extra = f' class="{cls}"' if cls else ""
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{width}"{extra}/>'


def _rect(x: float, y: float, w: float, h: float, fill: str, r: float = 4, width: float = LW, cls: str = "") -> str:
    extra = f' class="{cls}"' if cls else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:g}" fill="{fill}" stroke="{INK}" stroke-width="{width}"{extra}/>'


def _label(out: list[str], label: str | None) -> list[str]:
    if label:
        out += _panel(264, 350, 100, 28, label, 16)
    return out


def _folds(x0: float, x1: float, y0: float, y1: float, n: int, dark: str) -> list[str]:
    """Vertical fold lines that sway, between two x edges."""
    out = []
    for i in range(1, n):
        x = x0 + (x1 - x0) * i / n
        out.append(_line(f"M{x:.1f},{y0:.1f} Q{x + 5:.1f},{(y0 + y1) / 2:.1f} {x:.1f},{y1:.1f}", 1.8, stroke=dark))
    return out


def curtains(paint: str, fill: Fill, label: str | None, heading: str = "eyelet", lined: str = "no") -> list[str]:
    """A pair of curtain panels on a pole. ``heading`` is ``eyelet`` (metal rings along the top),
    ``pencil`` (a pleated tape band with pleat marks) or ``tab`` (fabric loops over the pole);
    ``lined`` ``yes`` shows the lining on the leading edge of each panel."""
    dark = _shade(fill.base, 0.3)
    top = 84 if heading != "tab" else 92
    out = [_line("M44,64 L356,64", 9, stroke=INK), _line("M44,64 L356,64", 5, stroke=POLE),
           _ell(40, 64, 8, 8, POLE), _ell(360, 64, 8, 8, POLE)]
    panels = ((62, 192), (208, 338))
    for x0, x1 in panels:
        out.append(_path(f"M{x0},{top} L{x1},{top} L{x1},330 Q{(x0 + x1) / 2},342 {x0},330 Z", paint))
        out += _folds(x0, x1, top + 6, 330, 5, dark)
    if lined.lower() == "yes":
        out += [_path("M192,84 L178,84 L174,330 L188,334 Z", LINING), _path("M208,84 L222,84 L226,330 L212,334 Z", LINING)]
    head = heading.lower()
    if head == "pencil":
        for x0, x1 in panels:
            out.append(_rect(x0, 70, x1 - x0, 26, paint, 2, 2.4))
            for i in range(1, 7):
                x = x0 + (x1 - x0) * i / 7
                out.append(f'<g class="pleat">{_line(f"M{x - 4:.1f},72 Q{x:.1f},84 {x - 4:.1f},94 M{x + 4:.1f},72 Q{x + 8:.1f},84 {x + 4:.1f},94", 1.8, stroke=dark)}</g>')
    elif head == "tab":
        for x0, x1 in panels:
            for i in range(4):
                x = x0 + 8 + (x1 - x0 - 24) * i / 3
                out.append(f'<g class="tab">{_rect(x, 50, 16, 46, paint, 3, 2.6)}</g>')
    else:
        for x0, x1 in panels:
            for i in range(RINGS // 2 + 1 if x0 < 100 else RINGS // 2):
                x = x0 + 14 + (x1 - x0 - 28) * i / (RINGS // 2)
                out.append(_ell(x, 76, 7, 7, "none", 3.2, "ring"))
    out += [_highlight("M80,118 L80,300", 4, 0.35), _highlight("M226,118 L226,300", 4, 0.35)]
    return _label(out, label)


def blind(paint: str, fill: Fill, label: str | None, kind: str = "roller") -> list[str]:
    """A window frame with a blind fitted. ``kind`` is ``roller`` (a flat drop with a bottom bar
    and a pull chain), ``roman`` (soft horizontal folds), ``venetian`` (:data:`SLATS` slats on
    two cords) or ``vertical`` (:data:`LOUVRES` hanging louvres)."""
    dark = _shade(fill.base, 0.3)
    out = [_rect(40, 36, 320, 330, FRAME, 6, 3.4), _rect(58, 54, 284, 294, "#dbe9f0", 2, 2.4)]
    k = kind.lower()
    if k == "venetian":
        out.append(_rect(58, 54, 284, 12, POLE, 2, 2.4))
        for i in range(SLATS):
            y = 70 + i * 17
            out.append(f'<g class="slat">{_path(f"M60,{y} L340,{y} L340,{y + 12} L60,{y + 12} Z", paint, 2.2)}</g>')
        out += [_line("M96,66 L96,262", 2), _line("M304,66 L304,262", 2), _rect(58, 262, 284, 10, POLE, 2, 2.4)]
    elif k == "vertical":
        out.append(_rect(58, 54, 284, 12, POLE, 2, 2.4))
        w = 284 / LOUVRES
        for i in range(LOUVRES):
            x = 58 + i * w
            out.append(f'<g class="louvre">{_path(f"M{x + 2:.1f},68 L{x + w - 2:.1f},68 L{x + w - 6:.1f},330 L{x + 6:.1f},330 Z", paint, 2.2)}</g>')
    elif k == "roman":
        out.append(_rect(58, 54, 284, 12, POLE, 2, 2.4))
        out.append(_path("M60,66 L340,66 L340,296 Q200,310 60,296 Z", paint))
        for y in (112, 158, 204, 250):
            out.append(_line(f"M60,{y} Q200,{y + 16} 340,{y}", 2.4, stroke=dark))
            out.append(_highlight(f"M70,{y + 10} Q200,{y + 24} 330,{y + 10}", 3, 0.3))
    else:
        out += [_ell(200, 62, 142, 9, POLE, 2.6), _path("M60,62 L340,62 L340,250 L60,250 Z", paint), _rect(56, 250, 288, 14, _shade(fill.base, 0.35), 3, 2.6),
                _line("M326,264 L326,314", 2.2), _ell(326, 322, 7, 7, POLE, 2.4)]
    return _label(out, label)


def _ticks(points: list[tuple[float, float]], dx: float, dy: float, cls: str, color: str, width: float = 2.2) -> list[str]:
    return [f'<g class="{cls}">{_line(f"M{x:.1f},{y:.1f} L{x + dx:.1f},{y + dy:.1f}", width, stroke=color)}</g>' for x, y in points]


#: The rug's params and the values it draws; any other value is refused naming the param. The
#: doormat, the kitchen mat and the motifs of a kids' rug are gen#1022's slice 7.
RUG_PARAMS: dict[str, tuple[str, ...]] = {
    "form": ("rectangle", "round", "runner", "doormat", "kitchen_mat"),
    "pile": ("flat", "shag", "short"),
    "motif": ("none", "road", "hopscotch", "stars"),
}
#: Where a kids' rug's motif sits on each form: its center and half-extents on the sheet.
MOTIF_AREA = {
    "rectangle": (200, 232, 110, 52), "round": (200, 236, 100, 30), "runner": (200, 228, 64, 72),
    "doormat": (200, 246, 76, 28), "kitchen_mat": (200, 244, 120, 28),
}  # fmt: skip
#: A kids' rug's bright motif colors, and the grey of its play road.
KIDS = ("#f2c14e", "#5b8def", "#e4572e", "#5fae5a")
ROAD = "#6b6b6b"
#: A doormat's rubber rim.
RUBBER = "#3d3a36"


def _bristles(top: float, bottom: float, left: float, right: float, slant: float, dark: str) -> list[str]:
    """A doormat's coir: rows of short stiff strokes (``class="bristle"``) across its face, each row
    as wide as the mat is at that depth (``slant``: how far each side leans out per unit down)."""
    out = []
    for i in range(5):
        y = top + 10 + i * (bottom - top - 20) / 4
        x0, x1 = left - (y - top) * slant + 8, right + (y - top) * slant - 8
        out += _ticks([(x0 + (x1 - x0) * j / 11, y) for j in range(12)], 0, 6, "bristle", dark, 1.8)
    return out


def _star(cx: float, cy: float, r: float, color: str) -> str:
    pts = [(cx + (r if k % 2 == 0 else r * 0.45) * math.sin(k * math.pi / 5), cy - (r if k % 2 == 0 else r * 0.45) * math.cos(k * math.pi / 5) * 0.7) for k in range(10)]
    return _path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z", color, 1.6)


def _motif(motif: str, cx: float, cy: float, rx: float, ry: float) -> list[str]:
    """A kids' rug's motif in one ``class="motif"`` group: a play road, a hopscotch court or stars."""
    if motif == "road":
        ring = f'cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx * 0.78:.1f}" ry="{ry * 0.7:.1f}" fill="none"'
        parts = [f'<ellipse {ring} stroke="{ROAD}" stroke-width="{max(ry * 0.3, 8):.1f}"/>',
                 f'<ellipse {ring} stroke="#ffffff" stroke-width="1.6" stroke-dasharray="6 6"/>',
                 _rect(cx - rx * 0.78 - 9, cy - 6, 18, 12, KIDS[2], 3, 1.6), _rect(cx + rx * 0.78 - 9, cy - 6, 18, 12, KIDS[1], 3, 1.6)]
    elif motif == "hopscotch":
        parts, rows = [], (1, 2, 1, 2, 1)  # laid along the rug's longer side
        long, short = (rx, ry) if rx >= ry else (ry, rx)
        step, side = 1.6 * long / len(rows), 0.7 * short
        for r, n in enumerate(rows):
            a = -0.8 * long + r * step
            for k in range(n):
                b = -side / 2 if n == 1 else -side + k * side
                x, y, w, h = (cx + a, cy + b, step, side) if rx >= ry else (cx + b, cy + a, side, step)
                parts.append(_rect(x, y, w, h, KIDS[(r + k) % len(KIDS)], 0, 1.6))
    else:
        parts = [_star(cx + rx * dx, cy + ry * dy, max(ry * 0.45, 12), KIDS[i % len(KIDS)])
                 for i, (dx, dy) in enumerate(((-0.6, -0.3), (-0.2, 0.35), (0.15, -0.4), (0.55, 0.2), (0.0, 0.0)))]
    return [f'<g class="motif">{"".join(parts)}</g>']


def rug(paint: str, fill: Fill, label: str | None, form: str = "rectangle", pile: str = "short", motif: str = "none") -> list[str]:
    """A rug on a floor line, in perspective. ``form`` is ``rectangle``, ``round``, ``runner``,
    ``doormat`` (a coir face in a rubber rim) or ``kitchen_mat`` (a long cushioned mat, its
    beveled front edge ``class="bevel"``); ``pile`` is ``flat`` (a fringe at both ends), ``shag``
    (a shaggy edge all round) or ``short`` (a plain edge with an inner border); ``motif`` is a kids'
    rug's ``road``, ``hopscotch`` or ``stars``, and ``none`` draws no motif."""
    dark = _shade(fill.base, 0.3)
    s, p, m = form.lower(), pile.lower(), motif.lower()
    for key, value in (("form", s), ("pile", p), ("motif", m)):
        if value not in RUG_PARAMS[key]:
            raise ValueError(f"unknown rug {key} {value!r}; one of {RUG_PARAMS[key]}")
    out = [_line("M20,300 L380,300", 2, stroke=_tint(INK, 0.6))]
    if s == "round":
        out.append(_ell(200, 236, 150, 52, paint))
        inner = _ell(200, 236, 112, 36, "none", 2, "border")
        edge = [(200 + 150 * math.cos(a / 14 * 6.2832), 236 + 52 * math.sin(a / 14 * 6.2832)) for a in range(14)]
    elif s == "runner":
        out.append(_path("M120,120 L280,120 L336,330 L64,330 Z", paint))
        inner = _path("M134,140 L266,140 L314,310 L86,310 Z", "none", 2)
        edge = [(120 + 160 * i / 6, 120) for i in range(7)] + [(64 + 272 * i / 6, 330) for i in range(7)]
    elif s == "doormat":
        out += [_path("M104,190 L296,190 L336,302 L64,302 Z", RUBBER), _path("M118,202 L282,202 L314,290 L86,290 Z", paint)]
        out += _bristles(202, 290, 118, 282, 32 / 88, dark)
        inner = _path("M132,214 L268,214 L294,278 L106,278 Z", "none", 2)
        edge = [(118 + 164 * i / 6, 202) for i in range(7)] + [(86 + 228 * i / 6, 290) for i in range(7)]
    elif s == "kitchen_mat":
        out.append(_path("M70,200 L330,200 L362,288 L38,288 Z", paint))
        out.append(_path("M38,288 L362,288 L358,300 L42,300 Z", _shade(fill.base, 0.15), LW_DETAIL, ' class="bevel"'))
        out += [_line(f"M{70 - (y - 200) * 0.36:.1f},{y} L{330 + (y - 200) * 0.36:.1f},{y}", 1.4, ' stroke-opacity=".5"', dark) for y in (222, 244, 266)]
        inner = _path("M84,212 L316,212 L342,278 L58,278 Z", "none", 2)
        edge = [(70 + 260 * i / 8, 200) for i in range(9)] + [(38 + 324 * i / 8, 288) for i in range(9)]
    else:
        out.append(_path("M96,150 L304,150 L368,310 L32,310 Z", paint))
        inner = _path("M112,168 L288,168 L344,296 L56,296 Z", "none", 2)
        edge = [(96 + 208 * i / 8, 150) for i in range(9)] + [(32 + 336 * i / 8, 310) for i in range(9)]
    if p == "shag":
        out += _ticks(edge, 0, 10, "fringe", dark, 3.4) + _ticks([(x + 8, y) for x, y in edge], -3, 8, "fringe", dark, 3.4)
        out.append(_highlight("M130,200 L260,200", 5, 0.25))
    elif p == "flat":
        ends = [(x, y) for x, y in edge if (y > 250 if s != "round" else x < 100 or x > 300)]
        out += _ticks(ends, 0, 12, "fringe", INK, 2.2)
        out += [_line("M130,220 L280,220", 2.4, stroke=dark), _line("M120,250 L292,250", 2.4, stroke=dark)]
    else:
        out.append(inner)
    if m != "none":
        out += _motif(m, *MOTIF_AREA[s])
    return _label(out, label)


def draped_throw(paint: str, fill: Fill, label: str | None, edge: str = "fringe") -> list[str]:
    """A throw over the arm of a sofa. ``edge`` is ``fringe`` (tassels), ``bound`` (a binding
    stitched round the hem) or ``pompom`` (a row of pom-poms)."""
    dark = _shade(fill.base, 0.3)
    out = [_rect(170, 176, 200, 150, "#a9a49a", 18, 3), _rect(60, 130, 130, 210, "#bdb8ac", 24, 3),
           _path("M66,150 Q66,110 130,110 Q194,110 194,150 L212,330 L48,330 Z", paint)]
    out += [_line("M96,140 Q94,230 88,326", 1.8, stroke=dark), _line("M150,138 Q154,230 162,326", 1.8, stroke=dark), _highlight("M84,128 Q130,118 176,128", 4, 0.35)]
    e = edge.lower()
    xs = [54 + i * 20 for i in range(8)]
    if e == "fringe":
        out += _ticks([(x, 330) for x in xs], 0, 22, "fringe", INK, 2.6)
    elif e == "pompom":
        out += [_ell(x, 336, 7, 7, _tint(fill.base, 0.4), 2.2, "pompom") for x in xs]
    else:
        out += [_line("M50,322 L210,322", 7, stroke=_shade(fill.base, 0.45)), _line("M50,318 L210,318", 1.6, stroke=_tint(fill.base, 0.5))]
    return _label(out, label)


def bath_mat(paint: str, fill: Fill, label: str | None, texture: str = "ribbed") -> list[str]:
    """A bath mat laid on the floor in perspective. ``texture`` is ``ribbed`` (parallel ribs),
    ``tufted`` (a grid of tufts, one ``class="tuft"`` each) or ``slatted`` (bamboo slats on two
    cords)."""
    dark = _shade(fill.base, 0.3)
    t = texture.lower()
    out = [_path("M104,150 Q104,140 120,140 L280,140 Q296,140 296,150 L352,296 Q354,314 336,314 L64,314 Q46,314 48,296 Z", paint)]
    if t == "slatted":
        for i in range(8):
            y = 156 + i * 19
            out.append(_line(f"M{96 - i * 7},{y} L{304 + i * 7},{y}", 3.4, stroke=INK))
            out.append(_line(f"M{96 - i * 7},{y} L{304 + i * 7},{y}", 1.6, stroke=_tint(fill.base, 0.45)))
        out += [_line("M150,142 L110,312", 2, stroke=POLE), _line("M250,142 L290,312", 2, stroke=POLE)]
    elif t == "tufted":
        for r in range(4):
            for c in range(7):
                x, y = 100 + c * 33 - r * 10 + (r % 2) * 6, 164 + r * 34
                out.append(_ell(x + 12, y, 8, 6, _tint(fill.base, 0.25), 1.8, "tuft"))
    else:
        for i in range(1, 7):
            out.append(_line(f"M{80 + i * 5},{150 + i * 22} L{320 - i * 5},{150 + i * 22}", 2.2, stroke=dark))
    out.append(_highlight("M120,152 L260,152", 4, 0.35))
    return _label(out, label)


def shower_curtain(paint: str, fill: Fill, label: str | None, hem: str = "plain") -> list[str]:
    """A shower curtain hung from a rail by :data:`CLIPS` ring clips. ``hem`` is ``plain`` (a
    single hem line) or ``weighted`` (a row of :data:`WEIGHTS` marked weights in the hem)."""
    dark = _shade(fill.base, 0.3)
    out = [_line("M36,56 L364,56", 8, stroke=INK), _line("M36,56 L364,56", 4, stroke=POLE)]
    out.append(_path("M54,74 L346,74 L346,330 Q330,340 314,330 Q298,340 282,330 Q266,340 250,330 Q234,340 218,330 Q202,340 186,330 Q170,340 154,330 Q138,340 122,330 Q106,340 90,330 Q72,340 54,330 Z", paint))
    for i in range(CLIPS):
        x = 62 + i * 34.5
        out.append(f'<g class="clip">{_ell(x, 64, 6, 9, "none", 2.6)}</g>')
    out += _folds(54, 346, 82, 322, 8, dark)
    if hem.lower() == "weighted":
        out.append(_line("M54,300 L346,300", 2.4, stroke=INK))
        out += [_ell(60 + i * 40, 312, 7, 7, POLE, 2.2, "weight") for i in range(WEIGHTS)]
    else:
        out.append(_line("M54,310 L346,310", 2.4, stroke=dark))
    out.append(_highlight("M70,100 L70,300", 4, 0.3))
    return _label(out, label)


SHAPES = {
    "curtains": curtains, "blind": blind, "rug": rug, "draped_throw": draped_throw,
    "bath_mat": bath_mat, "shower_curtain": shower_curtain,
}  # fmt: skip
register(SHAPES)
