"""Own-kind shapes for the furniture range (gen#199): tables, chairs, storage and mirrors.

Each is a flat front or three-quarter drawing in the kit's house style, the record's fill
(its finish: a wood tone, a paint, a fabric) on the main surface. The variant axis that
changes how the piece looks is a param, so two styles that differ on it draw differently.

=================  ==============================================  ==========================
shape              draws                                           params
=================  ==============================================  ==========================
dining_table       a top in plan (its outline) over its legs,      outline, seats, extending,
                   one chair back per seat around it               top (its material)
dining_chair       one chair, or a set fanned under a count band   style, count
coffee_table       a low table: top, legs, its storage             outline, storage, pieces
side_table         side, bedside, console or a nest of tables      kind, drawers
bookcase           a shelving unit, books on its shelves           shelves, style
wardrobe           a tall cabinet: its doors, mirrors, handles     doors, mirrored, door
chest_of_drawers   a chest with one front per drawer               drawers, form
mirror             a mirror glass in the record's frame            outline, kind
=================  ==============================================  ==========================

A colorway's color drives the fill: a White piece reads white (no body is shaded far toward black),
and a dining table's ``top`` follows ``top_material`` (a timber draws grain, a glass top is
translucent over the record-colored legs, a marble-effect top carries veins), gen#226.

Every params value is a string, as a style row's ``params`` carry it. A top's or a glass's
outline is ``outline``, not ``shape``: :func:`variants.drawing` takes the shape name as ``shape``.
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
    _path,
    _shade,
    _tint,
    register,
)

GLASS = "#dfeaf0"
METAL = "#3b3f46"
BOOKS = ("#b5502f", "#2f5b8a", "#d4a32a", "#4f7a3a", "#7a4a8a", "#c46a4a")
SHAPES = ("round", "rectangular", "oval", "square")
TIMBERS = ("oak", "walnut", "pine", "ash", "beech", "teak")
TOPS = (*TIMBERS, "glass", "marble_effect")
CHAIR_STYLES = ("upholstered", "spindle", "cantilever", "bench")
SIDE_KINDS = ("side", "bedside", "console", "nest")
MIRROR_SHAPES = ("round", "arched", "rectangular", "sunburst")
MIRROR_KINDS = ("wall", "full_length", "floor", "bathroom", "vanity")
#: The dining bench's padded seat, three-quarters front: ``kit_home_variants.bench`` sits on it too.
BENCH_SEAT = "M66,190 Q200,176 334,190 Q352,192 350,214 L346,244 L54,244 L50,214 Q48,192 66,190 Z"


def _rect(x: float, y: float, w: float, h: float, fill: str, width: float = LW, rx: float = 0, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return f'<rect{c} x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:g}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _knob(cx: float, cy: float, r: float = 4.5) -> str:
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{METAL}" stroke="{INK}" stroke-width="1"/>'


def _grain(x: float, y: float, w: float, h: float, base: str) -> str:
    """Faint wood-grain strokes across a panel, in a shade of its own finish."""
    rows = " ".join(f"M{x + 6:.1f},{y + h * t:.1f} Q{x + w / 2:.1f},{y + h * t + 3:.1f} {x + w - 6:.1f},{y + h * t:.1f}" for t in (0.3, 0.55, 0.8))
    return _line(rows, 0.9, ' class="grain" stroke-opacity=".25"', _shade(base, 0.35))


def _veins(cx: float, cy: float, rx: float, ry: float, base: str) -> list[str]:
    """A few marble veins across a top, in a shade that shows on its own color."""
    r, g, b = (int(base[i : i + 2], 16) for i in (1, 3, 5))
    vein = _tint(base, 0.55) if 0.2126 * r + 0.7152 * g + 0.0722 * b < 110 else _shade(base, 0.4)
    curves = (
        (f"M{cx - 0.6 * rx:.1f},{cy + 0.55 * ry:.1f} C{cx - 0.3 * rx:.1f},{cy - 0.3 * ry:.1f} {cx + 0.1 * rx:.1f},{cy + 0.6 * ry:.1f} {cx + 0.6 * rx:.1f},{cy - 0.5 * ry:.1f}", 2.0),
        (f"M{cx - 0.2 * rx:.1f},{cy + 0.7 * ry:.1f} C{cx - 0.1 * rx:.1f},{cy + 0.2 * ry:.1f} {cx + 0.2 * rx:.1f},{cy + 0.1 * ry:.1f} {cx + 0.3 * rx:.1f},{cy + 0.6 * ry:.1f}", 1.0),
        (f"M{cx - 0.5 * rx:.1f},{cy - 0.2 * ry:.1f} C{cx - 0.3 * rx:.1f},{cy - 0.6 * ry:.1f} {cx - 0.1 * rx:.1f},{cy - 0.1 * ry:.1f} {cx + 0.05 * rx:.1f},{cy - 0.55 * ry:.1f}", 1.0),
        (f"M{cx + 0.15 * rx:.1f},{cy + 0.1 * ry:.1f} C{cx + 0.3 * rx:.1f},{cy - 0.2 * ry:.1f} {cx + 0.45 * rx:.1f},{cy + 0.3 * ry:.1f} {cx + 0.65 * rx:.1f},{cy + 0.15 * ry:.1f}", 0.9),
    )
    return [_line(d, w, ' class="vein" stroke-opacity=".85"', vein) for d, w in curves]


def _legs(xs: list[float], top: float, bottom: float, paint: str, w: float = 10) -> list[str]:
    return [_path(f"M{x - w / 2:.1f},{top:.1f} L{x + w / 2:.1f},{top:.1f} L{x + w / 2 - 2:.1f},{bottom:.1f} L{x - w / 2 + 2:.1f},{bottom:.1f} Z", paint, LW_DETAIL) for x in xs]


def _top_outline(shape: str, cx: float, cy: float, rx: float, ry: float) -> str:
    """A table top in a three-quarter view: an ellipse for round and oval, a slanted slab else."""
    if shape in ("round", "oval"):
        return f"M{cx - rx:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 1 0 {cx + rx:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 1 0 {cx - rx:.1f},{cy:.1f} Z"
    k = rx * 0.18
    return f"M{cx - rx + k:.1f},{cy - ry:.1f} L{cx + rx - k:.1f},{cy - ry:.1f} L{cx + rx:.1f},{cy + ry:.1f} L{cx - rx:.1f},{cy + ry:.1f} Z"


def _chair_back(x: float, y: float, w: float, h: float, paint: str) -> list[str]:
    return [_rect(x, y, w, h, paint, LW_DETAIL, rx=6), _line(f"M{x + 6:.1f},{y + h * 0.5:.1f} L{x + w - 6:.1f},{y + h * 0.5:.1f}", 1.0, ' stroke-opacity=".5"')]


def _area(d: str, color: str, opacity: float) -> str:
    """A translucent tone over ``d`` with no outline: the light or the shade a surface carries."""
    return f'<path d="{d}" fill="{color}" fill-opacity="{opacity:g}" stroke="none"/>'


def _lit(d: str, opacity: float = 0.28) -> str:
    return _area(d, "#ffffff", opacity)


def _dim(d: str, opacity: float = 0.1) -> str:
    return _area(d, "#000000", opacity)


def _quad(*pts: tuple[float, float]) -> str:
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"


def _ground(cx: float, y: float, rx: float, ry: float = 8.0) -> str:
    """The shadow the piece throws on the floor (``class="ground"``: not a part of the figure)."""
    return f'<ellipse class="ground" cx="{cx:g}" cy="{y:g}" rx="{rx:g}" ry="{ry:g}" fill="#000000" fill-opacity=".14"/>'


def _bar(x0: float, y0: float, x1: float, y1: float, w0: float, w1: float, paint: str) -> str:
    """A leg, post or rail from one point to the other, ``w0`` wide at its start and ``w1`` at its end."""
    n = math.hypot(x1 - x0, y1 - y0)
    ux, uy = -(y1 - y0) / n / 2, (x1 - x0) / n / 2
    return _path(_quad((x0 + ux * w0, y0 + uy * w0), (x0 - ux * w0, y0 - uy * w0), (x1 - ux * w1, y1 - uy * w1), (x1 + ux * w1, y1 + uy * w1)), paint, LW_DETAIL)


def _slab(cx: float, y0: float, y1: float, back: float, front: float, t: float, paint: str, round_: bool = False, cls: str = "") -> list[str]:
    """A table top seen from above its front edge: its surface from ``y0`` (its back edge, ``back``
    to each side of ``cx``) to ``y1`` (its front, ``front``), over its edge ``t`` thick, lit from the
    left and shaded to the right. A round one is an ellipse ``front`` wide to each side."""
    edge, c = _shade(paint, 0.18), f' class="{cls}"' if cls else ""
    if round_:
        cy, ry = (y0 + y1) / 2, (y1 - y0) / 2
        under = f"M{cx - front:.1f},{cy:.1f} L{cx - front:.1f},{cy + t:.1f} A{front:.1f},{ry:.1f} 0 0 0 {cx + front:.1f},{cy + t:.1f} L{cx + front:.1f},{cy:.1f} Z"
        lit = f"M{cx - front + 4:.1f},{cy:.1f} A{front - 4:.1f},{ry - 4:.1f} 0 0 1 {cx + front * 0.1:.1f},{y0 + 4:.1f} L{cx - front * 0.35:.1f},{y1 - ry * 0.12:.1f} A{front - 4:.1f},{ry - 4:.1f} 0 0 1 {cx - front + 4:.1f},{cy:.1f} Z"
        return [_path(under, edge, LW_DETAIL), _path(_top_outline("round", cx, cy, front, ry), paint, LW, c), _lit(lit)]
    under = _quad((cx - front, y1), (cx + front, y1), (cx + front, y1 + t), (cx - front, y1 + t))
    lit = _quad((cx - back + 4, y0 + 3), (cx + back * 0.15, y0 + 3), (cx - front * 0.3, y1 - 3), (cx - front + 5, y1 - 3))
    return [_path(under, edge, LW_DETAIL), _path(_quad((cx - back, y0), (cx + back, y0), (cx + front, y1), (cx - front, y1)), paint, LW, c), _lit(lit)]


def _front(x: float, y: float, w: float, h: float) -> list[str]:
    """The light down the left of an upright front and the shade down its right."""
    return [_lit(_quad((x + 2, y + 2), (x + w * 0.34, y + 2), (x + w * 0.2, y + h - 2), (x + 2, y + h - 2)), 0.3), _dim(_quad((x + w * 0.72, y + 2), (x + w - 2, y + 2), (x + w - 2, y + h - 2), (x + w * 0.6, y + h - 2)), 0.08)]


def _side(x: float, y: float, h: float, depth: float, paint: str) -> str:
    """The right side of a cabinet, receding ``depth`` from its front edge."""
    return _path(_quad((x, y), (x + depth, y - depth * 0.4), (x + depth, y + h - depth * 0.5), (x, y + h)), _shade(paint, 0.2), LW_DETAIL)


def _table_chair(x: float, y: float, w: float, h: float, paint: str, legs: float = 0.0) -> list[str]:
    """One chair at a table (``class="seat"``): its back, ``w`` by ``h``, and, for one drawn in
    front of the table, its legs down to ``legs``."""
    out = [_bar(x + dx, y + h - 4, x + dx, legs, 13, 10, _shade(paint, 0.15)) for dx in (10, w - 10)] if legs else []
    out += [_rect(x, y, w, h, paint, LW_DETAIL, rx=9), _lit(_quad((x + 7, y + 6), (x + w * 0.45, y + 6), (x + w * 0.3, y + h - 6), (x + 7, y + h - 6)), 0.25), _dim(_quad((x + w * 0.74, y + 6), (x + w - 5, y + 6), (x + w - 5, y + h - 6), (x + w * 0.62, y + h - 6)), 0.12), _line(f"M{x + 9:.1f},{y + h * 0.72:.1f} L{x + w - 9:.1f},{y + h * 0.72:.1f}", 1.0, ' stroke-opacity=".5"')]
    return ['<g class="seat">', *out, "</g>"]


def _end_chair(side: int, inner: float, outer: float, y: float, floor: float, paint: str) -> list[str]:
    """One chair at a table's end, its back outward (``class="seat"``)."""
    cx = 200.0
    a, b = cx + side * inner, cx + side * outer
    dark = _shade(paint, 0.15)
    back = _quad((b - side * 30, y), (b, y + 8), (b, y + 128), (b - side * 30, y + 118))
    seat = _quad((b - side * 30, y + 92), (a, y + 92), (a, y + 132), (b, y + 132))
    return ['<g class="seat">', _bar(b - side * 8, y + 124, b - side * 4, floor, 15, 11, dark), _bar(a - side * -8, y + 126, a + side * 8, floor - 14, 13, 10, dark),
            _path(seat, _shade(paint, 0.05), LW_DETAIL), _path(back, paint, LW_DETAIL), _lit(_quad((b - side * 26, y + 8), (b - side * 14, y + 10), (b - side * 14, y + 112), (b - side * 26, y + 110)), 0.3), "</g>"]


def dining_table(paint: str, fill: Fill, label: str | None, outline: str = "rectangular", seats: str = "4", extending: str = "no", top: str = "oak") -> list[str]:
    """A dining table and its ``seats`` chair backs: half behind the top, the rest at its ends.

    ``outline`` sets the top's outline (round and oval are ellipses, rectangular a slab); an
    ``extending`` table shows the seam of its extension leaf across the top. ``top`` is the top's
    material (the ``top_material`` attribute): a timber draws grain in the record's color, a
    ``glass`` top is translucent glass over the record-colored legs, a ``marble_effect`` top
    carries veins (``class="vein"``) in the record's color."""
    if outline not in SHAPES:
        raise ValueError(f"unknown table outline {outline!r}; one of {SHAPES}")
    if top not in TOPS:
        raise ValueError(f"unknown table top {top!r}; one of {TOPS}")
    n = int(seats)
    if n not in (2, 4, 6, 8):
        raise ValueError(f"a dining table seats 2, 4, 6 or 8, not {n}")
    cx = 200
    # Every seat is drawn (``class="seat"``): one chair at each end of a table for two, and of a long
    # table of six or more, and the rest half behind the top and half in front of it.
    long = outline in ("rectangular", "oval")
    ends = 2 if n == 2 or (n >= 6 and long) else 0
    each = (n - ends) // 2
    oval = outline in ("round", "oval")
    y0, y1, t = {"round": (84, 240), "square": (84, 232), "oval": (98, 224), "rectangular": (98, 224)}[outline] + (16,)
    back, front = {"round": (150, 150), "square": (112, 130), "oval": (128, 128), "rectangular": (116, 132)}[outline]
    if outline == "square" and n > 2:
        back, front = back + 22, front + 26
    cy, rx, ry = (y0 + y1) / 2, front, (y1 - y0) / 2
    seat = _shade(paint, 0.08)
    wide = min(84.0, 2 * front * 0.86 / max(each, 1) - 8)
    xs = [cx + (k - (each - 1) / 2) * (wide + 14) for k in range(each)]
    out: list[str] = [_ground(cx, 352, 150)]
    for x in xs:
        out += _table_chair(x - wide / 2, 34, wide, 86, seat)
    for side in (-1, 1)[:ends]:
        out += _end_chair(side, front - 12, 170, 112, 340, seat)
    if outline == "round":
        out += [_path(f"M{cx - 20},{cy + 40} L{cx + 20},{cy + 40} L{cx + 16},{cy + 150} L{cx - 16},{cy + 150} Z", paint), _path(f"M{cx - 78},346 Q{cx},296 {cx + 78},346 L{cx + 78},356 L{cx - 78},356 Z", paint, LW_DETAIL), _dim(f"M{cx + 4},{cy + 90} L{cx + 16},{cy + 90} L{cx + 12},{cy + 146} L{cx + 4},{cy + 146} Z", 0.16)]
    else:
        inset = 34 if oval else 14
        out += [_bar(cx + s * (back - inset - 6), y1 - 10, cx + s * (back - inset - 10), 326, 18, 13, _shade(paint, 0.2)) for s in (-1, 1)]
        out += [_bar(cx + s * (front - inset), y1 - 6, cx + s * (front - inset - 2), 350, 24, 16, paint) for s in (-1, 1)]
        if not oval and top != "glass":
            out.append(_path(_quad((cx - front + 10, y1 + t - 4), (cx + front - 10, y1 + t - 4), (cx + front - 10, y1 + t + 26), (cx - front + 10, y1 + t + 26)), _shade(paint, 0.1), LW_DETAIL))
    outline_d = _top_outline(outline, cx, cy, rx, ry) if oval else _quad((cx - back, y0), (cx + back, y0), (cx + front, y1), (cx - front, y1))
    out.append(_slab(cx, y0, y1, back, front, t, GLASS if top == "glass" else paint, oval)[0])
    lit = _slab(cx, y0, y1, back, front, t, paint, oval)[2]
    if top == "glass":
        out += [_path(outline_d, GLASS, LW, ' class="top" fill-opacity=".55"'), _highlight(f"M{cx - rx * 0.55:.1f},{cy + ry * 0.45:.1f} L{cx - rx * 0.3:.1f},{cy - ry * 0.45:.1f}", 4, 0.7)]
    elif top == "marble_effect":
        out += [_path(outline_d, paint, LW, ' class="top"'), *_veins(cx, cy, rx, ry, fill.base)]
    else:
        out += [_path(outline_d, paint, LW, ' class="top"'), _grain(cx - back, y0, 2 * back, 2 * ry, fill.base)]
    out += [lit, _dim(_quad((cx + back * 0.7, y0 + 3), (cx + back - 3, y0 + 3), (cx + front - 4, y1 - 3), (cx + front * 0.5, y1 - 3)), 0.1)] if not oval else [lit, _dim(f"M{cx + rx * 0.45:.1f},{cy + ry * 0.87:.1f} A{rx},{ry:g} 0 0 0 {cx + rx - 3:.1f},{cy:.1f} Q{cx + rx * 0.7:.1f},{cy + ry * 0.35:.1f} {cx + rx * 0.45:.1f},{cy + ry * 0.87:.1f} Z", 0.12)]
    if extending == "yes":
        out.append(_line(f"M{cx - 22},{y0 + 2} L{cx - 26},{y1 - 2} M{cx + 22},{y0 + 2} L{cx + 26},{y1 - 2}", 1.6, ' stroke-dasharray="5 3"'))
    for x in xs:  # the chairs in front, tucked in: their backs over the top's near edge
        out += _table_chair(x - wide / 2, y1 - 10, wide, 82, seat, 356)
    return out


def _one_chair(style: str, paint: str, fill: Fill) -> list[str]:
    """One dining chair from in front and a little above, its seat and back in the record's fill."""
    if style == "upholstered":
        wood, dark = "#5a4433", "#4a3a2e"
        return [
            _ground(200, 358, 128),
            *[_bar(x, 270, x, 336, 19, 13, dark) for x in (118, 282)],
            *[_bar(x, 274, x, 358, 27, 18, wood) for x in (94, 306)],
            _path("M94,44 Q200,20 306,44 Q318,48 316,64 L302,216 L98,216 L84,64 Q82,48 94,44 Z", paint),
            _lit("M98,52 Q140,38 182,36 L150,206 L106,206 L92,66 Q92,56 98,52 Z", 0.22), _dim("M256,40 Q290,44 304,52 L308,64 L294,208 L252,208 Z", 0.12),
            _line("M112,64 Q200,44 288,64 L278,206 M112,64 L122,206", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
            _path("M82,196 Q200,184 318,196 Q332,200 332,216 L332,262 Q330,284 312,284 L88,284 Q70,284 68,262 L68,216 Q68,200 82,196 Z", paint),
            _lit("M84,202 Q200,190 316,202 Q326,206 326,218 Q200,208 74,218 Q74,206 84,202 Z", 0.3), _dim("M68,246 L332,246 L332,264 Q330,284 312,284 L88,284 Q70,284 68,264 Z", 0.14),
            _line("M70,246 L330,246", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
        ]
    if style == "spindle":
        dark = _shade(paint, 0.16)
        return [
            _ground(200, 358, 128),
            *[_bar(x, 262, x0, 336, 22, 16, dark) for x, x0 in ((122, 114), (278, 286))], _bar(116, 316, 284, 316, 15, 15, dark),
            *[_bar(x, 264, x0, 358, 30, 20, paint) for x, x0 in ((98, 84), (302, 316))], _bar(92, 306, 308, 306, 17, 17, paint),
            *[_bar(x, 60, x0, 214, 24, 26, paint) for x, x0 in ((92, 102), (308, 298))],
            *[_bar(200 + 25.5 * k, 72, 200 + 22.5 * k, 212, 17, 17, paint if k % 2 else _shade(paint, 0.06)) for k in range(-3, 4)],
            _path("M80,40 Q200,18 320,40 L318,86 Q200,66 82,86 Z", paint), _lit("M88,44 Q160,30 220,30 L210,48 Q150,48 88,60 Z", 0.35), _dim("M84,74 Q200,54 316,74 L318,86 Q200,66 82,86 Z", 0.16),
            _path("M90,202 Q200,190 310,202 L336,254 Q336,274 318,276 L82,276 Q64,274 64,254 Z", paint),
            _lit("M96,206 Q160,198 212,198 L180,250 L74,250 Z", 0.28), _dim("M64,254 L336,254 Q336,274 318,276 L82,276 Q64,274 64,256 Z", 0.16),
        ]
    if style == "cantilever":
        chrome, far = "#c9ccd1", "#a9adb4"
        return [
            _ground(200, 358, 134),
            _bar(104, 322, 296, 322, 14, 14, far), *[_bar(x, 320, x0, 350, 15, 15, chrome) for x, x0 in ((104, 78), (296, 322))],
            *[_bar(x, 262, x, 354, 17, 17, chrome) for x in (78, 322)], *[_bar(x, 180, x, 226, 16, 16, chrome) for x in (110, 290)],
            _path("M92,42 Q200,22 308,42 Q318,46 316,60 L302,202 L98,202 L84,60 Q82,46 92,42 Z", paint),
            _lit("M96,50 Q140,38 184,36 L152,194 L106,194 L92,64 Z", 0.24), _dim("M256,38 Q292,44 306,50 L308,62 L294,194 L250,194 Z", 0.14),
            _path("M86,202 Q200,192 314,202 Q330,206 332,222 L334,262 Q334,284 314,286 L86,286 Q66,284 66,262 L68,222 Q70,206 86,202 Z", paint),
            _lit("M88,208 Q200,198 312,208 Q324,212 326,226 Q200,214 74,226 Q76,212 88,208 Z", 0.3), _dim("M66,252 L334,252 L334,264 Q334,284 314,286 L86,286 Q66,284 66,264 Z", 0.16),
            _highlight("M76,290 L76,346", 3, 0.8),
        ]
    if style == "bench":
        wood, dark = "#8a6a48", "#6b5138"
        return [
            _ground(200, 342, 172),
            *[_bar(x, 246, x, 316, 22, 16, dark) for x in (74, 326)], _bar(70, 300, 330, 300, 16, 16, dark),
            *[_bar(x, 254, x, 342, 32, 22, wood) for x in (52, 348)],
            _rect(44, 246, 312, 30, wood, LW_DETAIL), _dim("M44,246 L356,246 L356,258 L44,258 Z", 0.18),
            _path("M64,96 Q200,84 336,96 Q352,98 356,116 L370,206 Q372,254 350,256 L50,256 Q28,254 30,206 L44,116 Q48,98 64,96 Z", paint),
            _lit("M70,102 Q130,96 196,96 L160,206 L40,206 L52,118 Q56,104 70,102 Z", 0.26), _dim("M30,210 L370,210 Q372,254 350,256 L50,256 Q28,254 30,210 Z", 0.14),
            _line("M34,210 L366,210", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
            _line("M54,120 Q200,108 346,120", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
        ]
    raise ValueError(f"unknown chair style {style!r}; one of {CHAIR_STYLES}")


def dining_chair(paint: str, fill: Fill, label: str | None, style: str = "upholstered", count: str = "1") -> list[str]:
    """A dining chair of ``style``; a set of ``count`` overlaps that many under a band naming it."""
    n = int(count)
    if n < 1:
        raise ValueError(f"a set holds at least one chair, not {n}")
    if n == 1 or style == "bench":
        return [f'<g class="chair">{"".join(_one_chair(style, paint, fill))}</g>']
    out = []
    for i in range(n):
        dx = (i - (n - 1) / 2) * (150 / max(n - 1, 1))
        out.append(f'<g class="chair" transform="translate({dx + 200 * 0.3:.1f} {40 - abs(dx) * 0.1:.1f}) scale(0.7)">{"".join(_one_chair(style, paint, fill))}</g>')
    return [*out, _rect(130, 352, 140, 34, "#ffffff", LW_DETAIL, rx=6), f'<text x="200" y="375" font-family="Helvetica, Arial, sans-serif" font-weight="700" font-size="20" text-anchor="middle" fill="{INK}">set of {n}</text>']


def coffee_table(paint: str, fill: Fill, label: str | None, outline: str = "rectangular", storage: str = "none", pieces: str = "1") -> list[str]:
    """A low coffee table: its top outline, legs, and its ``storage`` (a shelf, a drawer, a lift-top
    raised on its hinge); ``pieces`` > 1 is a nesting set, the smaller tables tucked beneath."""
    if outline not in SHAPES:
        raise ValueError(f"unknown table outline {outline!r}; one of {SHAPES}")
    cx, cy, rx, ry = 200, 178, (110 if outline == "round" else 156), (44 if outline == "round" else 38)
    out: list[str] = []
    for k in range(1, int(pieces)):
        s = 1 - 0.18 * k
        out += [f'<g class="nest" transform="translate({200 - 200 * s + 30 * k:.1f} {120 * k * 0.5:.1f}) scale({s:.2f})">', _path(_top_outline(outline, 200, 250, rx * 0.9, ry), _shade(paint, 0.1)), *_legs([200 - rx * 0.7, 200 + rx * 0.7], 250 + ry - 4, 330, _shade(paint, 0.1), 10), "</g>"]
    legs = [cx - rx + 20, cx + rx - 20] if outline != "round" else [cx - 60, cx + 60]
    out += _legs(legs, cy + ry, cy + 140, paint, 14)
    out += _legs([cx - rx * 0.55, cx + rx * 0.55] if outline != "round" else [cx], cy + ry - 8, cy + 128, _shade(paint, 0.18), 10)
    if storage == "shelf":
        out.append(_path(f"M{cx - rx + 16},{cy + 96} L{cx + rx - 16},{cy + 96} L{cx + rx - 16},{cy + 108} L{cx - rx + 16},{cy + 108} Z", paint, LW_DETAIL))
        out += [_rect(cx - 40 + 18 * i, cy + 78, 14, 18, BOOKS[i], 1) for i in range(3)]
    if storage == "drawer":
        out += [_rect(cx - rx + 4, cy + ry - 2, 2 * rx - 8, 40, _shade(paint, 0.06), LW_DETAIL), _knob(cx, cy + ry + 18)]
        out.append(_line(f"M{cx},{cy + ry - 2} L{cx},{cy + ry + 38}", 1.2))
    if storage == "lift_top":
        out += [
            _rect(cx - rx + 4, cy + ry - 2, 2 * rx - 8, 46, _shade(paint, 0.12), LW_DETAIL),
            _path(f"M{cx - rx + 30},{cy - 6} L{cx + rx - 30},{cy - 6} L{cx + rx - 50},{cy - 70} L{cx - rx + 50},{cy - 70} Z", paint),
            _line(f"M{cx - rx + 60},{cy - 4} L{cx - rx + 74},{cy - 56} M{cx + rx - 60},{cy - 4} L{cx + rx - 74},{cy - 56}", 3, stroke=METAL),
        ]
    out += [_path(_top_outline(outline, cx, cy, rx, ry), paint), _grain(cx - rx, cy - ry, 2 * rx, 2 * ry, fill.base)]
    if storage == "lift_top":
        out.append(_path(f"M{cx - rx + 30},{cy - 70} L{cx + rx - 30},{cy - 70} L{cx + rx - 10},{cy - 14} L{cx - rx + 10},{cy - 14} Z", paint))
    return out


def _drawer_fronts(x: float, y: float, w: float, h: float, n: int, paint: str, cols: int = 1) -> list[str]:
    """``n`` drawer fronts filling the box, ``cols`` across, one handle each (``class="drawer"``)."""
    rows = math.ceil(n / cols)
    out = []
    for i in range(n):
        r, c = divmod(i, cols)
        # a last row of fewer drawers spans the width
        cw_ = w / (n % cols) if r == rows - 1 and n % cols and cols > 1 else w / cols
        dx = x + c * cw_
        dy = y + r * h / rows
        out += [_rect(dx + 3, dy + 3, cw_ - 6, h / rows - 6, paint, LW_DETAIL, rx=2, cls="drawer"), _line(f"M{dx + cw_ / 2 - 14:.1f},{dy + h / rows / 2:.1f} L{dx + cw_ / 2 + 14:.1f},{dy + h / rows / 2:.1f}", 4, stroke=METAL)]
    return out


def side_table(paint: str, fill: Fill, label: str | None, kind: str = "side", drawers: str = "0") -> list[str]:
    """A small table: ``side`` (round top, three legs), ``bedside`` (a cabinet of ``drawers``),
    ``console`` (long and narrow, against a wall) or ``nest`` (three tables tucked in each other)."""
    n = int(drawers)
    if kind == "side":
        return [*_legs([150, 250, 200], 160, 330, paint, 10), f'<ellipse cx="200" cy="158" rx="90" ry="30" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>', _path("M140,272 L260,272 L254,282 L146,282 Z", _shade(paint, 0.15), LW_DETAIL)]
    if kind == "bedside":
        out = [*_legs([126, 274], 300, 336, paint, 10), _rect(112, 120, 176, 186, paint), _path("M104,106 L296,106 L296,124 L104,124 Z", paint, LW_DETAIL)]
        out += _drawer_fronts(116, 126, 168, 120 if n < 3 else 176, n, paint) if n else []
        if n and n < 3:
            out.append(_rect(118, 252, 164, 48, _shade(paint, 0.25), LW_DETAIL))
        out.append(_path("M196,60 L230,60 L240,104 L186,104 Z", "#f1ede4", LW_DETAIL))  # a lamp shade on top
        return out
    if kind == "console":
        out = [*_legs([48, 352], 186, 330, paint, 12), _path("M40,170 L360,170 L360,188 L40,188 Z", paint), _path("M56,300 L344,300 L344,310 L56,310 Z", _shade(paint, 0.1), LW_DETAIL)]
        out += _drawer_fronts(60, 188, 280, 34, n, paint, cols=max(n, 1)) if n else []
        return out
    if kind == "nest":
        out = []
        for k, (w, h, x0) in enumerate(((240, 210, 80), (190, 170, 105), (140, 130, 130))):
            p = _shade(paint, 0.06 * (2 - k))
            out += ['<g class="nest">', _path(f"M{x0},{340 - h} L{x0 + w},{340 - h} L{x0 + w},{340 - h + 14} L{x0},{340 - h + 14} Z", p), *_legs([x0 + 8, x0 + w - 8], 340 - h + 14, 340, p, 9), "</g>"]
        return out
    raise ValueError(f"unknown side table kind {kind!r}; one of {SIDE_KINDS}")


def bookcase(paint: str, fill: Fill, label: str | None, shelves: str = "4", style: str = "standard") -> list[str]:
    """A bookcase with ``shelves`` shelves (``class="shelf"``), each holding books: ``standard``,
    ``ladder`` (leaning, shelves deepening downward), ``cube`` (a grid of open cubes) or
    ``glass_door`` (two glazed doors)."""
    n = int(shelves)
    if not 2 <= n <= 8:
        raise ValueError(f"a bookcase has 2 to 8 shelves, not {n}")
    if style == "ladder":
        out = [_line("M150,40 L110,350 M250,40 L290,350", 12, stroke=INK), _line("M150,40 L110,350 M250,40 L290,350", 8, stroke=paint)]
        for i in range(n):
            y = 70 + (260 / max(n - 1, 1)) * i
            x0, x1 = 150 - (y - 40) * 0.13, 250 + (y - 40) * 0.13
            out += [_rect(x0 + 10 + 16 * k, y - 26, 12, 26, BOOKS[(i + k) % 6], 1) for k in range(int((x1 - x0 - 30) / 16))]
            out.append(_path(f"M{x0:.1f},{y:.1f} L{x1:.1f},{y:.1f} L{x1:.1f},{y + 8:.1f} L{x0:.1f},{y + 8:.1f} Z", paint, LW_DETAIL).replace("<path", '<path class="shelf"'))
        return out
    if style == "cube":
        cols = 2 if n <= 4 else 3
        rows = math.ceil(n / cols) if n > 4 else n // 2 if n % 2 == 0 else n
        cols = math.ceil(n / rows)
        w, h = 90 * cols, 90 * rows
        x0, y0 = 200 - w / 2, 200 - h / 2
        out = [_rect(x0, y0, w, h, paint)]
        for i in range(n):
            r, c = divmod(i, cols)
            cw, ch = (w - 16) / cols, (h - 16) / rows
            x, y = x0 + 8 + c * cw, y0 + 8 + r * ch
            out += [
                _rect(x + 4, y + 4, cw - 8, ch - 8, _tint(paint, 0.6), LW_DETAIL, cls="shelf"),
                _rect(x + 10, y + 10, cw - 20, ch - 20, _tint(paint, 0.3), 1.0),
            ]
            if i % 2 == 0:  # a fabric box fills most of the cell, a handle cut-out on its front
                out += [_rect(x + 9, y + 24, cw - 18, ch - 32, "#d8c9a8", 1.4, rx=3), _rect(x + cw / 2 - 12, y + 36, 24, 8, "#8a7a5a", 1.0, rx=4)]
        return out
    out = [_rect(110, 40, 180, 320, paint), _rect(122, 52, 156, 296, _shade(paint, 0.1), LW_DETAIL)]
    gap = 296 / n
    for i in range(n):
        y = 52 + gap * (i + 1)
        out += [_rect(128 + 15 * k, y - gap * 0.62, 12, gap * 0.62 - 2, BOOKS[(i + k) % 6], 1) for k in range(int(9 - i % 3))]
        if i < n - 1:
            out.append(_path(f"M122,{y - 2:.1f} L278,{y - 2:.1f} L278,{y + 4:.1f} L122,{y + 4:.1f} Z", paint, LW_DETAIL).replace("<path", '<path class="shelf"'))
        else:
            out.append(_line(f"M122,{y:.1f} L278,{y:.1f}", 0.1).replace("<path", '<path class="shelf"'))
    if style == "glass_door":
        out += [_rect(124, 54, 75, 292, GLASS, LW_DETAIL).replace('fill="', 'fill-opacity=".45" fill="'), _rect(201, 54, 75, 292, GLASS, LW_DETAIL).replace('fill="', 'fill-opacity=".45" fill="'), _knob(192, 200), _knob(208, 200)]
        out += [_highlight("M136,80 L170,40", 4, 0.7), _highlight("M214,90 L250,48", 4, 0.7)]
    elif style != "standard":
        raise ValueError(f"unknown bookcase style {style!r}; standard, ladder, cube or glass_door")
    return out


def wardrobe(paint: str, fill: Fill, label: str | None, doors: str = "2", mirrored: str = "no", door: str = "hinged") -> list[str]:
    """A tall wardrobe with ``doors`` doors (``class="door"``): a mirrored wardrobe glazes its
    middle door (or every other sliding panel), a ``sliding`` one runs its doors on a top track."""
    n = int(doors)
    if n not in (2, 3, 4):
        raise ValueError(f"a wardrobe has 2, 3 or 4 doors, not {n}")
    w = 70 * n + 40
    x0 = 200 - w / 2
    out = [_path(f"M{x0 - 6},{40} L{x0 + w + 6},{40} L{x0 + w + 6},{54} L{x0 - 6},{54} Z", paint, LW_DETAIL), _rect(x0, 54, w, 286, paint), *_legs([x0 + 14, x0 + w - 14], 340, 356, _shade(paint, 0.3), 12)]
    dw = (w - 12) / n
    mirror_at = {n // 2} if n % 2 else ({1} if n == 2 else {1, 2})
    for i in range(n):
        x = x0 + 6 + i * dw
        glass = mirrored == "yes" and i in mirror_at
        out.append(_rect(x + 2, 60, dw - 4, 274, GLASS if glass else paint, LW_DETAIL, cls="door"))
        if glass:
            out += [_highlight(f"M{x + 14:.1f},{120} L{x + dw - 18:.1f},{80}", 5, 0.8), _highlight(f"M{x + 14:.1f},{170} L{x + dw - 30:.1f},{140}", 3, 0.6)]
        elif door == "hinged":
            out.append(_rect(x + 10, 74, dw - 20, 110, _shade(paint, 0.05), 1.0))
        if door == "hinged":
            hx = x + dw - 12 if i % 2 == 0 else x + 10
            out.append(_line(f"M{hx:.1f},178 L{hx:.1f},214", 5, stroke=METAL))
    if door == "sliding":
        out += [_line(f"M{x0 + 6},{62} L{x0 + w - 6},{62}", 3), _line(f"M{x0 + w / 2 - 6},180 L{x0 + w / 2 - 6},230 M{x0 + w / 2 + 6},180 L{x0 + w / 2 + 6},230", 3, stroke=METAL)]
    elif door != "hinged":
        raise ValueError(f"unknown wardrobe door {door!r}; hinged or sliding")
    return out


def chest_of_drawers(paint: str, fill: Fill, label: str | None, drawers: str = "4", form: str = "tall") -> list[str]:
    """A chest with exactly ``drawers`` drawer fronts (``class="drawer"``): a ``tall`` chest stacks
    them in one column, a ``wide`` one sets two small drawers over full-width ones."""
    n = int(drawers)
    if not 2 <= n <= 8:
        raise ValueError(f"a chest has 2 to 8 drawers, not {n}")
    if form == "tall":
        x, w, top, h = 120, 160, 60, 270
        out = [_rect(x, top, w, h, paint), _path(f"M{x - 8},{top - 14} L{x + w + 8},{top - 14} L{x + w + 8},{top} L{x - 8},{top} Z", paint, LW_DETAIL)]
        out += _drawer_fronts(x + 4, top + 4, w - 8, h - 8, n, paint)
    elif form == "wide":
        x, w, top, h = 60, 280, 120, 210
        out = [_rect(x, top, w, h, paint), _path(f"M{x - 8},{top - 14} L{x + w + 8},{top - 14} L{x + w + 8},{top} L{x - 8},{top} Z", paint, LW_DETAIL)]
        small = 2 if n >= 4 and n % 2 == 0 else 0 if n % 2 == 0 else 1
        rows_full = n - (2 if small == 2 else 0)
        if small == 2:
            band = h / (rows_full + 1)
            out += _drawer_fronts(x + 4, top + 4, w - 8, band, 2, paint, cols=2)
            out += _drawer_fronts(x + 4, top + 4 + band, w - 8, h - 8 - band, rows_full, paint)
        else:
            out += _drawer_fronts(x + 4, top + 4, w - 8, h - 8, n, paint)
    else:
        raise ValueError(f"unknown chest form {form!r}; tall or wide")
    return [*out, *_legs([x + 16, x + w - 16], top + h, top + h + 22, _shade(paint, 0.25), 12)]


def mirror(paint: str, fill: Fill, label: str | None, outline: str = "rectangular", kind: str = "wall") -> list[str]:
    """A mirror glass in a frame of the record's finish: ``outline`` sets the outline, ``kind`` the
    proportion (a ``full_length`` or ``floor`` mirror is drawn tall and narrow, a floor one on a
    stand; a ``vanity`` one on a small foot; a ``bathroom`` one with a shelf under it)."""
    if outline not in MIRROR_SHAPES:
        raise ValueError(f"unknown mirror outline {outline!r}; one of {MIRROR_SHAPES}")
    if kind not in MIRROR_KINDS:
        raise ValueError(f"unknown mirror kind {kind!r}; one of {MIRROR_KINDS}")
    tall = kind in ("full_length", "floor")
    w, h = (130, 320) if tall else (220, 220 if outline in ("round", "sunburst") else 260)
    if kind == "vanity":
        w, h = 170, 170
    cx, cy = 200, 40 + h / 2 + (10 if tall else 0)
    out: list[str] = []
    if kind == "floor":
        out.append(_line(f"M{cx + 20},{cy} L{cx + 60},{cy + h / 2 + 20}", 8, stroke=_shade(paint, 0.2)))
    if kind == "vanity":
        out += [_line(f"M{cx},{cy + h / 2} L{cx},{cy + h / 2 + 70}", 10, stroke=paint), f'<ellipse cx="{cx}" cy="{cy + h / 2 + 74}" rx="56" ry="12" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>']
    if outline == "sunburst":
        rays = []
        for k in range(24):
            a = 2 * math.pi * k / 24
            r1, r2 = w / 2 - 6, w / 2 + (44 if k % 2 else 26)
            rays.append(f"M{cx + r1 * math.cos(a):.1f},{cy + r1 * math.sin(a):.1f} L{cx + r2 * math.cos(a):.1f},{cy + r2 * math.sin(a):.1f}")
        out += [_line(" ".join(rays), 8, stroke=INK), _line(" ".join(rays), 5, stroke=paint)]
        frame, glass = (f'<circle class="frame" cx="{cx}" cy="{cy}" r="{w / 2 - 4:.1f}" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>', f'<circle cx="{cx}" cy="{cy}" r="{w / 2 - 24:.1f}" fill="{GLASS}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
    elif outline == "round":
        rx, ry = (w / 2, h / 2) if tall else (w / 2, w / 2)
        frame = f'<ellipse class="frame" cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>'
        glass = f'<ellipse cx="{cx}" cy="{cy}" rx="{rx - 16:.1f}" ry="{ry - 16:.1f}" fill="{GLASS}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
    elif outline == "arched":
        def arch(m: float) -> str:
            x0, x1, y0, y1 = cx - w / 2 + m, cx + w / 2 - m, cy - h / 2 + m, cy + h / 2 - m
            r = (x1 - x0) / 2
            return f"M{x0:.1f},{y1:.1f} L{x0:.1f},{y0 + r:.1f} A{r:.1f},{r:.1f} 0 0 1 {x1:.1f},{y0 + r:.1f} L{x1:.1f},{y1:.1f} Z"

        frame, glass = _path(arch(0), paint).replace("<path", '<path class="frame"'), _path(arch(16), GLASS, LW_DETAIL)
    else:
        frame = _rect(cx - w / 2, cy - h / 2, w, h, paint, cls="frame")
        glass = _rect(cx - w / 2 + 16, cy - h / 2 + 16, w - 32, h - 32, GLASS, LW_DETAIL)
    out += [frame, glass, _highlight(f"M{cx - w * 0.22:.1f},{cy - h * 0.12:.1f} L{cx - w * 0.04:.1f},{cy - h * 0.3:.1f}", 6, 0.85), _highlight(f"M{cx - w * 0.18:.1f},{cy + h * 0.04:.1f} L{cx + w * 0.06:.1f},{cy - h * 0.22:.1f}", 3, 0.7)]
    if kind == "bathroom":
        out.append(_path(f"M{cx - w / 2 - 6},{cy + h / 2 + 10} L{cx + w / 2 + 6},{cy + h / 2 + 10} L{cx + w / 2 + 6},{cy + h / 2 + 22} L{cx - w / 2 - 6},{cy + h / 2 + 22} Z", _tint(paint, 0.3), LW_DETAIL))
    return out


register(
    {"dining_table": dining_table, "dining_chair": dining_chair, "coffee_table": coffee_table,
     "side_table": side_table, "bookcase": bookcase, "wardrobe": wardrobe,
     "chest_of_drawers": chest_of_drawers, "mirror": mirror},
)  # fmt: skip
