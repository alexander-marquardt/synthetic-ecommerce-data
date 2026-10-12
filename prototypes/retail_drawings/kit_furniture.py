"""Own-kind shapes for the furniture range (gen#199): tables, chairs, storage and mirrors.

Each is a flat front or three-quarter drawing in the kit's house style, the record's fill
(its finish: a wood tone, a paint, a fabric) on the main surface. The variant axis that
changes how the piece looks is a param, so two styles that differ on it draw differently.

=================  ==============================================  ==========================
shape              draws                                           params
=================  ==============================================  ==========================
dining_table       a top in plan (its outline) over its legs,      outline, seats, extending
                   one chair back per seat around it
dining_chair       one chair, or a set fanned under a count band   style, count
coffee_table       a low table: top, legs, its storage             outline, storage, pieces
side_table         side, bedside, console or a nest of tables      kind, drawers
bookcase           a shelving unit, books on its shelves           shelves, style
wardrobe           a tall cabinet: its doors, mirrors, handles     doors, mirrored, door
chest_of_drawers   a chest with one front per drawer               drawers, form
mirror             a mirror glass in the record's frame            outline, kind
=================  ==============================================  ==========================

Every params value is a string, as a style row's ``params`` carry it. A top's or a glass's
outline is ``outline``, not ``shape``: :func:`variants.drawing` takes the shape name as ``shape``.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _path, _shade, _tint, register

GLASS = "#dfeaf0"
METAL = "#3b3f46"
BOOKS = ("#b5502f", "#2f5b8a", "#d4a32a", "#4f7a3a", "#7a4a8a", "#c46a4a")
SHAPES = ("round", "rectangular", "oval", "square")
CHAIR_STYLES = ("upholstered", "spindle", "cantilever", "bench")
SIDE_KINDS = ("side", "bedside", "console", "nest")
MIRROR_SHAPES = ("round", "arched", "rectangular", "sunburst")
MIRROR_KINDS = ("wall", "full_length", "floor", "bathroom", "vanity")


def _rect(x: float, y: float, w: float, h: float, fill: str, width: float = LW, rx: float = 0, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return f'<rect{c} x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:g}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _knob(cx: float, cy: float, r: float = 4.5) -> str:
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{METAL}" stroke="{INK}" stroke-width="1"/>'


def _grain(x: float, y: float, w: float, h: float, base: str) -> str:
    """Faint wood-grain strokes across a panel, in a shade of its own finish."""
    rows = " ".join(f"M{x + 6:.1f},{y + h * t:.1f} Q{x + w / 2:.1f},{y + h * t + 3:.1f} {x + w - 6:.1f},{y + h * t:.1f}" for t in (0.3, 0.55, 0.8))
    return _line(rows, 0.9, ' stroke-opacity=".25"', _shade(base, 0.35))


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


def dining_table(paint: str, fill: Fill, label: str | None, outline: str = "rectangular", seats: str = "4", extending: str = "no") -> list[str]:
    """A dining table and its ``seats`` chair backs: half behind the top, the rest at its ends.

    ``outline`` sets the top's outline (round and oval are ellipses, rectangular a slab); an
    ``extending`` table shows the seam of its extension leaf across the top."""
    if outline not in SHAPES:
        raise ValueError(f"unknown table outline {outline!r}; one of {SHAPES}")
    n = int(seats)
    if n not in (2, 4, 6, 8):
        raise ValueError(f"a dining table seats 2, 4, 6 or 8, not {n}")
    rx = {"round": 96, "square": 100, "oval": 150, "rectangular": 150}[outline] + (10 if n == 8 else 0)
    ry = 40 if outline != "round" else 46
    cx, cy = 200, 196
    # Every seat is drawn: chair backs in a row behind the top, and one at each end of a long
    # table of six or more, so the drawn backs (``class="seat"``) count the seats.
    ends = 2 if n >= 6 and outline in ("rectangular", "oval") else 0
    behind = n - ends
    span = rx * 0.78 if behind > 2 else rx * 0.45
    out: list[str] = []
    for x in [cx - span + 2 * span * k / (behind - 1) for k in range(behind)]:
        out += ['<g class="seat">', *_chair_back(x - 24, cy - ry - 70, 48, 66, _shade(paint, 0.08)), "</g>"]
    for side in (-1, 1)[:ends]:
        x = cx + side * (rx + 22)
        out += ['<g class="seat">', *_chair_back(x - 18, cy - 54, 36, 64, _shade(paint, 0.08)), "</g>"]
    legs = [cx] if outline == "round" else [cx - rx + 22, cx + rx - 22]
    if outline == "round":
        out += [_path(f"M{cx - 14},{cy + ry - 6} L{cx + 14},{cy + ry - 6} L{cx + 10},{cy + 140} L{cx - 10},{cy + 140} Z", paint), _path(f"M{cx - 60},{cy + 140} L{cx + 60},{cy + 140} L{cx + 50},{cy + 152} L{cx - 50},{cy + 152} Z", paint, LW_DETAIL)]
    else:
        out += _legs(legs, cy + ry - 4, cy + 150, paint, 14)
        if outline == "oval":
            out += _legs([cx - rx * 0.45, cx + rx * 0.45], cy + ry - 2, cy + 146, _shade(paint, 0.15), 12)
    top = _top_outline(outline, cx, cy, rx, ry)
    out += [_path(f"M{cx - rx:.1f},{cy + (0 if outline in ('round', 'oval') else ry):.1f} L{cx - rx:.1f},{cy + (0 if outline in ('round', 'oval') else ry) + 14:.1f} L{cx + rx:.1f},{cy + (0 if outline in ('round', 'oval') else ry) + 14:.1f} L{cx + rx:.1f},{cy + (0 if outline in ('round', 'oval') else ry):.1f} Z", _shade(paint, 0.2), LW_DETAIL) if outline not in ("round", "oval") else f'<ellipse cx="{cx}" cy="{cy + 10}" rx="{rx}" ry="{ry}" fill="{_shade(paint, 0.2)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>']
    out += [_path(top, paint), _grain(cx - rx, cy - ry, 2 * rx, 2 * ry, fill.base)]
    if extending == "yes":
        out.append(_line(f"M{cx - 22},{cy - ry + 2} L{cx - 26},{cy + ry - 2} M{cx + 22},{cy - ry + 2} L{cx + 26},{cy + ry - 2}", 1.6, ' stroke-dasharray="5 3"'))
    for side in (-1, 1)[:ends]:
        x = cx + side * (rx + 22)
        out += _legs([x - 12, x + 12], cy + 8, cy + 92, _shade(paint, 0.08), 6)
    return out


def _one_chair(style: str, paint: str, fill: Fill) -> list[str]:
    """One dining chair facing three-quarters front, its seat and back in the record's fill."""
    wood = _shade(paint, 0.25) if style == "upholstered" else paint
    if style == "upholstered":
        return [
            *_legs([136, 264], 250, 340, "#4a3a2e", 10), *_legs([152, 248], 250, 322, "#4a3a2e", 8),
            _path("M140,60 Q200,48 260,60 L262,214 L138,214 Z", paint),
            _line("M152,76 Q200,66 248,76", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
            _path("M120,206 L280,206 Q292,206 290,222 L286,256 L114,256 L110,222 Q108,206 120,206 Z", paint),
            _line("M116,236 L284,236", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
        ]
    if style == "spindle":
        bars = " ".join(f"M{x:.1f},84 L{x:.1f},206" for x in (166, 188, 212, 234))
        return [
            *_legs([132, 268], 236, 340, wood, 10), *_legs([150, 250], 236, 322, wood, 8),
            _line("M140,300 L260,300", 5, stroke=INK), _line("M140,300 L260,300", 3, stroke=wood),
            _line("M146,64 L146,214 M254,64 L254,214", 11, stroke=INK), _line("M146,64 L146,214 M254,64 L254,214", 7, stroke=wood),
            _line(bars, 7, stroke=INK), _line(bars, 4, stroke=wood),
            _path("M140,62 Q200,52 260,62 L260,84 Q200,76 140,84 Z", wood),
            _path("M118,210 L282,210 L286,240 L114,240 Z", paint),
        ]
    if style == "cantilever":
        return [
            _line("M150,214 L150,250 Q150,336 182,336 L292,336 M250,214 L250,250 Q250,320 280,320 L304,320", 9, stroke=INK),
            _line("M150,214 L150,250 Q150,336 182,336 L292,336 M250,214 L250,250 Q250,320 280,320 L304,320", 5, stroke="#c9ccd1"),
            _path("M142,62 Q200,50 258,62 L254,206 L146,206 Z", paint),
            _path("M124,200 L276,200 Q288,202 286,216 L282,236 L118,236 L114,216 Q112,202 124,200 Z", paint),
        ]
    if style == "bench":
        return [
            *_legs([86, 314], 230, 330, wood, 14), *_legs([110, 290], 230, 312, _shade(wood, 0.12), 10),
            _path("M66,196 L334,196 L346,228 L54,228 Z", paint),
            _path("M54,228 L346,228 L346,242 L54,242 Z", _shade(paint, 0.18), LW_DETAIL),
            _grain(66, 196, 268, 32, fill.base),
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
            p = _shade(paint, 0.1 * (2 - k))
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
        w, h = 90 * cols, 300
        x0 = 200 - w / 2
        out = [_rect(x0, 50, w, h, paint)]
        for i in range(n):
            r, c = divmod(i, cols)
            x, y = x0 + 8 + c * (w - 16) / cols, 58 + r * (h - 16) / rows
            out.append(_rect(x + 4, y + 4, (w - 16) / cols - 8, (h - 16) / rows - 8, _shade(paint, 0.3), LW_DETAIL, cls="shelf"))
            if i % 2 == 0:
                out.append(_rect(x + 12, y + (h - 16) / rows - 40, (w - 16) / cols - 24, 28, "#d8c9a8", 1.2))
        return out
    out = [_rect(110, 40, 180, 320, paint), _rect(122, 52, 156, 296, _shade(paint, 0.3), LW_DETAIL)]
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
