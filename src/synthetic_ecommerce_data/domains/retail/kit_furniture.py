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
        # Curves, not arcs: the drawn-box measure reads an arc as a box of its radii around the chord's middle, wider than the top.
        lit = f"M{cx - front + 4:.1f},{cy:.1f} Q{cx - front * 0.6:.1f},{y0 + 4:.1f} {cx + front * 0.1:.1f},{y0 + 4:.1f} L{cx - front * 0.35:.1f},{y1 - ry * 0.12:.1f} Q{cx - front * 0.8:.1f},{y1 - 2:.1f} {cx - front + 4:.1f},{cy:.1f} Z"
        return [_path(under, edge, LW_DETAIL), _path(_top_outline("round", cx, cy, front, ry), paint, LW, c), _lit(lit)]
    under = _quad((cx - front, y1), (cx + front, y1), (cx + front, y1 + t), (cx - front, y1 + t))
    lit = _quad((cx - back + 4, y0 + 3), (cx + back * 0.15, y0 + 3), (cx - front * 0.3, y1 - 3), (cx - front + 5, y1 - 3))
    return [_path(under, edge, LW_DETAIL), _path(_quad((cx - back, y0), (cx + back, y0), (cx + front, y1), (cx - front, y1)), paint, LW, c), _lit(lit)]


def _front(x: float, y: float, w: float, h: float) -> list[str]:
    """The light down the left of an upright front and the shade down its right."""
    return [_lit(_quad((x + 2, y + 2), (x + w * 0.34, y + 2), (x + w * 0.2, y + h - 2), (x + 2, y + h - 2)), 0.3), _dim(_quad((x + w * 0.72, y + 2), (x + w - 2, y + 2), (x + w - 2, y + h - 2), (x + w * 0.6, y + h - 2)), 0.08)]


def _side(x: float, y: float, h: float, depth: float, paint: str) -> str:
    """The right side of a cabinet, receding ``depth`` from its front edge."""
    return _path(_quad((x, y), (x + depth, y - depth * 0.4), (x + depth, y + h - depth * 0.5), (x, y + h)), _shade(paint, 0.17), LW_DETAIL)


def _cabinet(x: float, y: float, w: float, h: float, depth: float, paint: str) -> list[str]:
    """A cabinet's body seen from in front, a little above and to the right: its side, its top, its front."""
    top = _quad((x, y), (x + depth, y - depth * 0.4), (x + w + depth, y - depth * 0.4), (x + w, y))
    return [_side(x + w, y, h, depth, paint), _path(top, _shade(paint, 0.05), LW_DETAIL), _lit(top, 0.3), _rect(x, y, w, h, paint)]


def _ellipse_slab(cx: float, cy: float, rx: float, ry: float, t: float, paint: str) -> list[str]:
    """A round top at its center: its edge, its surface, its light and its shade."""
    shade = f"M{cx + rx * 0.45:.1f},{cy + ry * 0.87:.1f} Q{cx + rx * 0.9:.1f},{cy + ry * 0.9:.1f} {cx + rx - 3:.1f},{cy:.1f} Q{cx + rx * 0.7:.1f},{cy + ry * 0.35:.1f} {cx + rx * 0.45:.1f},{cy + ry * 0.87:.1f} Z"
    return [*_slab(cx, cy - ry, cy + ry, rx, rx, t, paint, round_=True), _dim(shade, 0.12)]


def _flat_slab(cx: float, y0: float, y1: float, back: float, front: float, t: float, paint: str) -> list[str]:
    """A straight-edged top: :func:`_slab` with the shade down its right."""
    return [*_slab(cx, y0, y1, back, front, t, paint), _dim(_quad((cx + back * 0.7, y0 + 3), (cx + back - 3, y0 + 3), (cx + front - 4, y1 - 3), (cx + front * 0.5, y1 - 3)), 0.1)]


def _books(x: float, floor: float, w: float, h: float, k: int) -> list[str]:
    """Books of uneven height standing on a shelf at ``floor``, ``w`` wide, up to ``h`` tall, lit down each spine."""
    out, n = [], max(1, int(w // 17))
    bw = w / n
    for i in range(n):
        bh = h * (1 - 0.07 * ((i * 2 + k) % 4))
        out += [_rect(x + i * bw, floor - bh, bw - 1, bh, BOOKS[(i + k) % 6], 1), _lit(_quad((x + i * bw + 2, floor - bh + 2), (x + i * bw + bw * 0.4, floor - bh + 2), (x + i * bw + bw * 0.4, floor - 2), (x + i * bw + 2, floor - 2)), 0.3)]
    return out


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
    back, front = {"round": (150, 150), "square": (122, 142), "oval": (128, 128), "rectangular": (116, 132)}[outline]
    if outline == "square" and n > 2:
        back, front = back + 12, front + 14
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
            *[_bar(x, 264, x0, 358, 30, 20, _shade(paint, 0.08)) for x, x0 in ((98, 84), (302, 316))], _bar(92, 306, 308, 306, 17, 17, _shade(paint, 0.12)),
            *[_bar(x, 60, x0, 214, 24, 26, paint) for x, x0 in ((92, 102), (308, 298))], _dim(_quad((309, 64), (319, 64), (310, 210), (300, 210)), 0.14), _lit(_quad((82, 64), (90, 64), (99, 210), (91, 210)), 0.3),
            *[_bar(200 + 25.5 * k, 72, 200 + 22.5 * k, 212, 17, 17, _shade(paint, 0.04 if k % 2 else 0.09)) for k in range(-3, 4)],
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
        dx = (i - (n - 1) / 2) * (112 / max(n - 1, 1))
        out.append(f'<g class="chair" transform="translate({dx + 200 * 0.18:.1f} 12) scale(0.82)">{"".join(_one_chair(style, paint, fill))}</g>')
    return [*out, _rect(130, 324, 140, 34, "#ffffff", LW_DETAIL, rx=6), f'<text x="200" y="347" font-family="Helvetica, Arial, sans-serif" font-weight="700" font-size="20" text-anchor="middle" fill="{INK}">set of {n}</text>']


def coffee_table(paint: str, fill: Fill, label: str | None, outline: str = "rectangular", storage: str = "none", pieces: str = "1") -> list[str]:
    """A low coffee table: its top outline, legs, and its ``storage`` (a shelf, a drawer, a lift-top
    raised on its hinge); ``pieces`` > 1 is a nesting set, the smaller tables tucked beneath."""
    if outline not in SHAPES:
        raise ValueError(f"unknown table outline {outline!r}; one of {SHAPES}")
    dark = _shade(paint, 0.15)
    out: list[str] = [_ground(200, 354, 150)]
    if int(pieces) > 1:  # a nesting set: the tall table behind, each smaller one pulled out in front
        for k in range(int(pieces)):
            s = 1 - 0.16 * k
            x, y, rx, ry = 170 + 84 * k, 104 + 88 * k, 140 * s, 62 * s
            p = _shade(paint, 0.05 * k)
            body = [*[_bar(x + d * rx, y + 20, x + d * rx * 1.04, 336 + 14 * k + (0 if d else 8), 20, 14, _shade(p, 0.12)) for d in (-0.82, 0, 0.82)]]
            body += _ellipse_slab(x, y, rx, ry, 16, p) if outline in ("round", "oval") else _flat_slab(x, y - ry, y + ry, rx * 0.84, rx, 16, p)
            out += ['<g class="nest">', *body, "</g>"] if k else body
        return out
    if outline in ("round", "oval"):
        ry = 74 if outline == "round" else 62
        out += [_bar(x, 130, x, 320, 16, 14, dark) for x in (110, 290)]
        if storage == "shelf":
            out += _ellipse_slab(200, 282, 132, 46, 14, _shade(paint, 0.05))
        out += [_bar(x, 150, x0, 354, 24, 18, paint) for x, x0 in ((62, 56), (338, 344))]
        out += [*_ellipse_slab(200, 112, 162, ry, 18, paint), _grain(90, 70, 220, 84, fill.base)]
        return out
    y0, y1 = (174, 224) if storage == "lift_top" else (92, 198)
    out += [_bar(x, y1, x, 328, 18, 14, dark) for x in (74, 326)]
    if storage == "shelf":
        out += _flat_slab(200, 272, 320, 132, 152, 14, paint)
    out += [_bar(x, y1, x, 354, 26, 20, paint) for x in (50, 350)]
    if storage == "lift_top":  # the box stands open and its top is raised toward the sitter on its hinge
        out += [_path(_quad((62, y0), (338, y0), (366, y1), (34, y1)), _shade(paint, 0.1), LW_DETAIL), _dim(_quad((82, y0 + 8), (318, y0 + 8), (334, y1 - 6), (66, y1 - 6)), 0.18)]
        out += [_rect(36, y1, 328, 66, paint, LW_DETAIL), *_front(36, y1, 328, 66)]
        out += [_bar(x, 112, x + d, 206, 11, 11, METAL) for x, d in ((86, 14), (314, -14))]
        return [*out, *_flat_slab(200, 46, 124, 136, 164, 16, paint), _grain(70, 52, 260, 66, fill.base)]
    if storage == "drawer":
        out += [_rect(38, y1 + 14, 324, 62, paint, LW_DETAIL), *[_rect(x, y1 + 20, 154, 50, _shade(paint, 0.05), LW_DETAIL, rx=2) for x in (44, 202)], *_front(38, y1 + 14, 324, 62), _knob(121, y1 + 45), _knob(279, y1 + 45)]
    else:
        out.append(_rect(44, y1 + 14, 312, 26, dark, LW_DETAIL))
    return [*out, *_flat_slab(200, y0, y1, 138, 168, 16, paint), _grain(70, y0 + 4, 260, y1 - y0 - 8, fill.base)]


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
    dark = _shade(paint, 0.15)
    if kind == "side":
        return [
            _ground(200, 354, 140), _bar(200, 150, 200, 300, 16, 14, dark), *_ellipse_slab(200, 284, 122, 44, 14, _shade(paint, 0.05)),
            *[_bar(x, 130, x0, 356, 22, 15, paint) for x, x0 in ((76, 64), (324, 336))], *_ellipse_slab(200, 106, 160, 72, 18, paint), _grain(100, 70, 200, 76, fill.base),
        ]
    if kind == "bedside":
        out = [_ground(200, 356, 136), *_legs([92, 308], 326, 358, dark, 20), _rect(78, 98, 244, 234, paint)]
        if n:
            out += _drawer_fronts(82, 106, 236, 222 if n >= 3 else 150, n, paint)
        if n < 3:  # the open shelf under the drawers
            y = 260 if n else 114
            out += [_rect(88, y, 224, 324 - y, _shade(paint, 0.12), LW_DETAIL), _dim(_quad((88, y), (312, y), (312, y + 14), (88, y + 14)), 0.16), *_books(104, 322, 88, min(46, 300 - y), 1)]
        return [*out, *_front(78, 98, 244, 234), *_flat_slab(200, 36, 84, 108, 130, 16, paint), _grain(104, 40, 192, 40, fill.base)]
    if kind == "console":
        out = [_ground(200, 356, 160), *[_bar(x, 130, x, 338, 16, 14, dark) for x in (74, 326)], *_flat_slab(200, 268, 318, 136, 160, 14, _shade(paint, 0.05))]
        out += [*[_bar(x, 140, x, 358, 22, 18, paint) for x in (46, 354)], _rect(40, 138, 320, 64, paint, LW_DETAIL)]
        out += _drawer_fronts(52, 140, 296, 60, n, paint, cols=max(n, 1)) if n else []
        return [*out, *_front(40, 138, 320, 64), *_flat_slab(200, 64, 124, 146, 168, 15, paint), _grain(64, 68, 272, 52, fill.base)]
    if kind == "nest":
        out = [_ground(200, 356, 150)]
        for k, (y0, y1, half, floor) in enumerate(((42, 118, 160, 334), (148, 212, 124, 346), (238, 292, 90, 358))):
            p = _shade(paint, 0.06 * (2 - k))
            legs = [_bar(200 + d * (half - 14), y1 + 6, 200 + d * (half - 14), floor, 20, 16, p) for d in (-1, 1)]
            out += ['<g class="nest">', *legs, *_flat_slab(200, y0, y1, half * 0.84, half, 14, p), _grain(200 - half * 0.8, y0, half * 1.6, y1 - y0, p), "</g>"]
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
        out = [_ground(200, 358, 160)]
        rails = ((104, 52), (296, 348))
        out += [_bar(x, 40, x + (26 if x < 200 else -26), 350, 14, 14, _shade(paint, 0.18)) for x, _ in rails]  # the back posts
        gap = 270 / max(n - 1, 1)
        for i in range(n):
            y = 84 + gap * i - (6 if i == n - 1 else 0)
            x0, x1 = 102 - (y - 40) * 0.16, 298 + (y - 40) * 0.16
            d = 10 + 5 * i  # each shelf is deeper than the one above it
            h = min(gap - d - 18, 62) if i else 50
            out += [_path(_quad((x0 + 8, y - d), (x1 - 8, y - d), (x1, y), (x0, y)), paint, LW_DETAIL), _lit(_quad((x0 + 10, y - d + 2), (x0 + (x1 - x0) * 0.5, y - d + 2), (x0 + (x1 - x0) * 0.3, y - 2), (x0 + 4, y - 2)))]
            if i % 2:
                box = (x1 - x0) * 0.36
                out += [_rect(x0 + 14, y - 4 - h, box, h, "#d8c9a8", 1.4, rx=3), _dim(_quad((x0 + 14 + box * 0.6, y - 2 - h), (x0 + 12 + box, y - 2 - h), (x0 + 12 + box, y - 6), (x0 + 14 + box * 0.7, y - 6)), 0.12), _rect(x0 + 2 + box / 2, y + 8 - h, 24, 8, "#8a7a5a", 1.0, rx=4), *_books(x0 + 18 + box, y - 4, x1 - x0 - box - 32, h, i)]
            else:
                out += _books(x0 + 14, y - 4, x1 - x0 - 28, h, i)
            out.append(_path(_quad((x0, y), (x1, y), (x1, y + 14), (x0, y + 14)), _shade(paint, 0.12), LW_DETAIL).replace("<path", '<path class="shelf"'))
        out += [_bar(x, 32, x0, 358, 16, 18, paint) for x, x0 in rails]
        return [*out, _lit(_quad((99, 34), (104, 34), (52, 354), (46, 354)), 0.3), _dim(_quad((299, 34), (304, 34), (356, 354), (350, 354)), 0.16)]
    if style == "cube":
        cols = 2 if n <= 4 else 3
        rows = math.ceil(n / cols) if n > 4 else n // 2 if n % 2 == 0 else n
        cols = math.ceil(n / rows)
        side = min(140.0, 300 / max(rows, cols))
        w, h, depth = side * cols, side * rows, 30
        x0, y0 = 200 - (w + depth) / 2, 350 - h
        out = [_ground(x0 + w / 2 + 12, 354, w / 2 + 14), *_cabinet(x0, y0, w, h, depth, paint)]
        for i in range(n):
            r, c = divmod(i, cols)
            cw, ch = (w - 16) / cols, (h - 16) / rows
            x, y = x0 + 8 + c * cw, y0 + 8 + r * ch
            out += [
                _rect(x + 4, y + 4, cw - 8, ch - 8, _tint(paint, 0.6), LW_DETAIL, cls="shelf"),
                _rect(x + 12, y + 12, cw - 24, ch - 24, _tint(paint, 0.3), 1.0),
                _dim(_quad((x + 4, y + 4), (x + cw - 4, y + 4), (x + cw - 12, y + 14), (x + 12, y + 14)), 0.16),
            ]
            if (r + c) % 2 == 0:  # a fabric box fills most of the cell, a handle cut-out on its front
                out += [_rect(x + 10, y + 26, cw - 20, ch - 34, "#d8c9a8", 1.4, rx=3), _lit(_quad((x + 13, y + 29), (x + cw * 0.5, y + 29), (x + cw * 0.36, y + ch - 12), (x + 13, y + ch - 12)), 0.3), _dim(_quad((x + cw * 0.7, y + 28), (x + cw - 12, y + 28), (x + cw - 12, y + ch - 11), (x + cw * 0.6, y + ch - 11)), 0.12), _rect(x + cw / 2 - 16, y + 42, 32, 10, "#8a7a5a", 1.0, rx=5)]
            else:
                out += _books(x + 12, y + ch - 9, (cw - 24) * 0.8, ch * 0.6, i)
        return [*out, _dim(_quad((x0 + w - 6, y0 + 2), (x0 + w - 2, y0 + 2), (x0 + w - 2, y0 + h - 2), (x0 + w - 6, y0 + h - 2)), 0.14)]
    out = [_ground(204, 356, 120), *_cabinet(86, 42, 204, 314, 26, paint), _rect(98, 54, 180, 290, _shade(paint, 0.1), LW_DETAIL)]
    gap = 290 / n
    for i in range(n):
        y = 54 + gap * (i + 1)
        out += [_dim(_quad((98, y - gap + 4), (278, y - gap + 4), (278, y - gap + 12), (98, y - gap + 12)), 0.06), *_books(104, y - 2, 168 - 34 * (i % 3), gap * 0.7, i)]
        if i < n - 1:
            out.append(_path(f"M98,{y - 4:.1f} L278,{y - 4:.1f} L278,{y + 4:.1f} L98,{y + 4:.1f} Z", paint, LW_DETAIL).replace("<path", '<path class="shelf"'))
        else:
            out.append(_line(f"M98,{y:.1f} L278,{y:.1f}", 0.1).replace("<path", '<path class="shelf"'))
    out += [_lit(_quad((88, 44), (96, 44), (96, 354), (88, 354)), 0.35), _dim(_quad((280, 44), (288, 44), (288, 354), (280, 354)), 0.1)]
    if style == "glass_door":
        for x in (100, 189):
            out += [_rect(x, 56, 87, 286, GLASS, LW_DETAIL).replace('fill="', 'fill-opacity=".45" fill="'), _rect(x, 56, 87, 286, "none", 6), _rect(x, 56, 87, 286, "none", 3.5).replace(INK, paint), _lit(_quad((x + 8, 190), (x + 50, 62), (x + 72, 62), (x + 8, 260)), 0.35)]
        out += [_knob(180, 204, 5.5), _knob(196, 204, 5.5)]
    elif style != "standard":
        raise ValueError(f"unknown bookcase style {style!r}; standard, ladder, cube or glass_door")
    return out


def wardrobe(paint: str, fill: Fill, label: str | None, doors: str = "2", mirrored: str = "no", door: str = "hinged") -> list[str]:
    """A tall wardrobe with ``doors`` doors (``class="door"``): a mirrored wardrobe glazes its
    middle door (or every other sliding panel), a ``sliding`` one runs its doors on a top track."""
    n = int(doors)
    if n not in (2, 3, 4):
        raise ValueError(f"a wardrobe has 2, 3 or 4 doors, not {n}")
    w = {2: 206, 3: 244, 4: 280}[n]
    x0 = 200 - (w + 18) / 2
    out = [_ground(204, 356, w / 2 + 10), *_legs([x0 + 14, x0 + w - 14], 340, 358, _shade(paint, 0.3), 16), *_cabinet(x0, 42, w, 300, 18, paint)]
    out += [_rect(x0, 42, w, 14, _shade(paint, 0.06), LW_DETAIL), _rect(x0, 326, w, 16, _shade(paint, 0.12), LW_DETAIL)]
    dw = (w - 12) / n
    mirror_at = {n // 2} if n % 2 else ({1} if n == 2 else {1, 2})
    for i in range(n):
        x = x0 + 6 + i * dw
        glass = mirrored == "yes" and i in mirror_at
        out.append(_rect(x + 2, 60, dw - 4, 262, GLASS if glass else paint, LW_DETAIL, cls="door"))
        if glass:
            out += [_lit(_quad((x + 8, 190), (x + dw * 0.5, 64), (x + dw * 0.8, 64), (x + 8, 270)), 0.65), _dim(_quad((x + dw * 0.6, 318), (x + dw - 6, 200), (x + dw - 6, 318)), 0.08)]
        else:
            if door == "hinged":  # two raised panels
                out += [_rect(x + 12, 74, dw - 24, 136, _shade(paint, 0.05), 1.0), _rect(x + 12, 222, dw - 24, 86, _shade(paint, 0.05), 1.0)]
            out += _front(x + 2, 60, dw - 4, 262)
        if door == "hinged":
            hx = x + dw - 12 if i % 2 == 0 else x + 10
            out.append(_line(f"M{hx:.1f},178 L{hx:.1f},214", 5, stroke=METAL))
    if door == "sliding":
        out += [_line(f"M{x0 + 6},{62} L{x0 + w - 6},{62}", 3), _line(f"M{x0 + w / 2 - 8},176 L{x0 + w / 2 - 8},230 M{x0 + w / 2 + 8},176 L{x0 + w / 2 + 8},230", 4, stroke=METAL)]
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
    dark = _shade(paint, 0.17)
    out: list[str] = []
    cx, cy, w, h, m = 200.0, 195.0, 222.0, 282.0, 16.0
    if outline in ("round", "sunburst"):
        w = h = 320.0
    if kind == "bathroom":
        cy = 172.0
    elif kind == "vanity":
        w = h = 272.0
        cy = 164.0
        out += [_ground(200, 358, 110), _bar(200, 290, 200, 340, 34, 40, dark), f'<ellipse cx="200" cy="344" rx="104" ry="16" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>', _lit("M104,343 A100,13 0 0 1 220,331 L190,344 A100,13 0 0 1 104,343 Z", 0.4), _dim("M230,359 A100,14 0 0 0 301,345 Q270,348 230,359 Z", 0.2)]
    elif kind == "full_length":
        w, h, m = 114.0, 328.0, 9.0
    elif kind == "floor":  # a tall frame on a folding stand, its back leg opened out behind it
        cx, w, h, m = 182.0, 104.0, 322.0, 11.0
        out += [_ground(214, 358, 100), _path(_quad((cx + 20, 60), (cx + 48, 60), (cx + 112, 356), (cx + 84, 356)), dark, LW_DETAIL), _bar(cx + 48, 296, cx + 92, 296, 12, 12, dark)]
    bevel = 12.0 if kind in ("full_length", "floor") else 0.0  # the frame's own depth, seen at its right
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2

    def shape(i: float, dx: float = 0.0) -> str:
        """The mirror's outline, ``i`` inside its edge."""
        a, b, t, u = x0 + i + dx, x1 - i + dx, y0 + i, y1 - i
        if outline in ("round", "sunburst"):
            rx, ry = (b - a) / 2, (u - t) / 2
            return f"M{a:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 1 1 {b:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 1 1 {a:.1f},{cy:.1f} Z"
        if outline == "arched":
            r = (b - a) / 2
            return f"M{a:.1f},{u:.1f} L{a:.1f},{t + r:.1f} A{r:.1f},{r:.1f} 0 0 1 {b:.1f},{t + r:.1f} L{b:.1f},{u:.1f} Z"
        return _quad((a, t), (b, t), (b, u), (a, u))

    if outline == "sunburst":
        w = h = 208.0
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2

        def at(a: float, r: float) -> tuple[float, float]:
            return cx + r * math.cos(a), cy + r * math.sin(a)

        for k in range(24):  # a ray is two facets, the light on one and the shade on the other
            a, half = 2 * math.pi * k / 24, math.pi / 24
            tip, left, right = at(a, 167 if k % 2 else 162), at(a - half, 147), at(a + half, 147)
            foot = at(a, 90)
            out += [_path(_quad(foot, left, tip, right), paint, LW_DETAIL), _lit(_quad(foot, left, tip), 0.3), _dim(_quad(foot, tip, right), 0.14)]
        m = 14.0
    if bevel:
        out.append(_path(shape(0, bevel), dark, LW_DETAIL))
    out += [_path(shape(0), paint).replace("<path", '<path class="frame"'), _dim(shape(m * 0.55), 0.16), _path(shape(m), GLASS, LW_DETAIL)]
    # the room's light across the glass, and the far side's shade, each inside the glass's outline
    gx, gy = w / 2 - m - 4, h / 2 - m - 4
    if outline in ("round", "sunburst"):
        k, q = gx * 0.7071, gx
        lit = f"M{cx - k:.1f},{cy + k:.1f} A{q:.1f},{q:.1f} 0 0 1 {cx + k:.1f},{cy - k:.1f} L{cx + k * 0.5:.1f},{cy - k * 0.5 - 0.2 * q:.1f} L{cx - k * 0.5 - 0.2 * q:.1f},{cy + k * 0.5:.1f} Z"
        dim = f"M{cx - k * 0.2:.1f},{cy + q * 0.98:.1f} A{q:.1f},{q:.1f} 0 0 0 {cx + q * 0.98:.1f},{cy - k * 0.2:.1f} Q{cx + k * 0.75:.1f},{cy + k * 0.75:.1f} {cx - k * 0.2:.1f},{cy + q * 0.98:.1f} Z"
    else:
        top = -gy + (gx if outline == "arched" else 0)
        lit = _quad((cx - gx, cy + gy * 0.35), (cx - gx, cy + top), (cx - gx * 0.2, cy + top), (cx + gx, cy + top), (cx + gx, cy - gy * 0.3))
        dim = _quad((cx - gx, cy + gy), (cx - gx, cy + gy * 0.75), (cx + gx, cy + gy * 0.1), (cx + gx, cy + gy))
    out += [_lit(lit, 0.55), _dim(dim, 0.1), _lit(_quad((x0 + 2, cy - h * 0.2), (x0 + 5, cy - h * 0.2), (x0 + 5, cy + h * 0.2), (x0 + 2, cy + h * 0.2)), 0.5)]
    out += [_highlight(f"M{cx - gx * 0.62:.1f},{cy + gy * 0.02:.1f} L{cx - gx * 0.05:.1f},{cy - gy * 0.5:.1f}", 6, 0.85), _highlight(f"M{cx - gx * 0.5:.1f},{cy + gy * 0.2:.1f} L{cx + gx * 0.18:.1f},{cy - gy * 0.42:.1f}", 3, 0.7)]
    if kind == "bathroom":  # the glass shelf under it, on the frame's two brackets
        out += [_bar(x, y1 - 6, x, y1 + 34, 14, 14, dark) for x in (x0 + 20, x1 - 20)]
        out += [_path(_quad((x0 - 18, y1 + 14), (x1 + 18, y1 + 14), (x1 + 30, y1 + 36), (x0 - 30, y1 + 36)), GLASS, LW_DETAIL), _lit(_quad((x0 - 16, y1 + 16), (cx, y1 + 16), (cx - 30, y1 + 34), (x0 - 26, y1 + 34)), 0.6), _path(_quad((x0 - 30, y1 + 36), (x1 + 30, y1 + 36), (x1 + 30, y1 + 46), (x0 - 30, y1 + 46)), paint, LW_DETAIL)]
    return out


register(
    {"dining_table": dining_table, "dining_chair": dining_chair, "coffee_table": coffee_table,
     "side_table": side_table, "bookcase": bookcase, "wardrobe": wardrobe,
     "chest_of_drawers": chest_of_drawers, "mirror": mirror},
)  # fmt: skip
