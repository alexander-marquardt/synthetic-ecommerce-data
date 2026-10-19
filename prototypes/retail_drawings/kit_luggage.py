"""Luggage and travel shapes for the retail drawing kit (gen#209).

Each luggage type has its own flat drawing in the kit's house style: outlines in the kit's ink,
the record's fill (color and pattern) on the product's main surface, so a shopper tells a hard
suitcase from a soft one, a holdall from a weekend bag, and a packing cube from a passport
holder at thumbnail size. A drawing never prints a size beyond what it shows: a style's sizes
share one image per colorway, and the ``size`` param only sets the height of the case.

==================  ===============================================  =====================
shape               draws                                            params
==================  ===============================================  =====================
suitcase            a tall upright case, telescopic handle; hard     size, shell, wheels
                    with vertical ribs (one ``class="rib"`` each) or
                    soft with a front pocket; four feet or two wheels
cabin_case          a small case; ``carry-on`` with a front flap and  kind, wheels, shell
                    wheels, ``under-seat`` a squat case with feet
holdall             a soft rectangular bag, two handles, a shoulder   wheels, strap
                    strap, an optional wheel pair
weekend_bag         a rounded duffel with two top handles and a zip;  compartments, sleeve
                    one ``class="pocket"`` end pocket per compartment
luggage_set         two or three nested cases side by side, one       pieces
                    ``class="piece"`` group each
travel_organizer    a stack of packing cubes (``class="cube"`` each), kind
                    a passport holder with a window, a toiletry roll
                    or an adapter case with plug pins
neck_pillow         a U shaped pillow, with or without a hood         hood
==================  ===============================================  =====================

Every param is a string with a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _panel, _path, _shade, _tint, register
from kit_accessories import HARDWARE, _circle, _ell, _group, _n, _rect

#: A case's height by size: top and bottom of the body on the sheet.
CASE_HEIGHT = {"cabin": (150, 322), "medium": (118, 322), "large": (92, 322)}


def _wheels(cx_left: float, cx_right: float, y: float, kind: str) -> list[str]:
    """Four small feet in pairs (``4``) or two larger wheels (``2``) under a case."""
    if kind == "2":
        return [_circle(cx_left, y + 8, 12, "#3a3a40", LW_DETAIL), _circle(cx_right, y + 8, 12, "#3a3a40", LW_DETAIL)]
    return [_circle(x, y + 7, 7, "#3a3a40", LW_DETAIL) for x in (cx_left - 9, cx_left + 9, cx_right - 9, cx_right + 9)]


def _case(paint: str, fill: Fill, x0: float, x1: float, top: float, bottom: float, hard: bool) -> list[str]:
    """A rounded case body between the x and y bounds, ribbed when hard, pocketed when soft."""
    mid = (x0 + x1) / 2
    out = [_path(f"M{x0 + 14},{top} L{x1 - 14},{top} Q{x1},{top} {x1},{top + 14} L{x1},{bottom - 14} Q{x1},{bottom} {x1 - 14},{bottom} L{x0 + 14},{bottom} Q{x0},{bottom} {x0},{bottom - 14} L{x0},{top + 14} Q{x0},{top} {x0 + 14},{top} Z", paint)]
    if hard:
        step = (x1 - x0) / 5
        out += [_group("rib", [_line(f"M{x0 + step * i},{top + 12} L{x0 + step * i},{bottom - 12}", 3, ' stroke-opacity=".55"', _shade(fill.base, 0.35))]) for i in range(1, 5)]
        out.append(_highlight(f"M{x0 + 8},{top + 24} L{x0 + 8},{bottom - 40}", 4, 0.35))
    else:
        py = top + (bottom - top) * 0.45
        out += [_path(f"M{x0 + 10},{py} L{x1 - 10},{py} L{x1 - 10},{bottom - 12} Q{x1 - 10},{bottom - 6} {x1 - 18},{bottom - 6} L{x0 + 18},{bottom - 6} Q{x0 + 10},{bottom - 6} {x0 + 10},{bottom - 12} Z", _tint(fill.base, 0.08), LW_DETAIL),
                _line(f"M{x0 + 16},{py + 12} L{x1 - 16},{py + 12}", 1.8, ' stroke-dasharray="6 3"'),
                _rect(mid - 7, py + 6, 14, 12, HARDWARE, 3, 1.2)]  # fmt: skip
    return out


def suitcase(paint: str, fill: Fill, label: str | None, size: str = "medium", shell: str = "hard", wheels: str = "4") -> list[str]:
    """An upright suitcase: ``size`` (cabin, medium, large) sets its height, ``shell`` is hard
    (vertical ribs) or soft (a front pocket), ``wheels`` is ``4`` (spinner feet) or ``2``."""
    top, bottom = CASE_HEIGHT.get(size.lower(), CASE_HEIGHT["medium"])
    x0, x1 = (140, 260) if size.lower() == "cabin" else (124, 276)
    mid = (x0 + x1) / 2
    out = [_line(f"M{mid - 30},{top} L{mid - 30},{top - 34} M{mid + 30},{top} L{mid + 30},{top - 34}", 6, stroke=INK),
           _line(f"M{mid - 30},{top} L{mid - 30},{top - 34} M{mid + 30},{top} L{mid + 30},{top - 34}", 3, stroke="#b8bcc2"),
           _rect(mid - 40, top - 46, 80, 14, "#3a3a40", 6, LW_DETAIL)]  # fmt: skip
    out += _wheels(x0 + 20, x1 - 20, bottom - 2, wheels)
    out += _case(paint, fill, x0, x1, top, bottom, shell.lower() != "soft")
    out += [_rect(mid - 22, top - 8, 44, 12, "#3a3a40", 5, LW_DETAIL)]
    if label:
        out += _panel(mid - 40, bottom + 26, 80, 24, label, 14)
    return out


def cabin_case(paint: str, fill: Fill, label: str | None, kind: str = "carry-on", wheels: str = "yes", shell: str = "soft") -> list[str]:
    """A cabin case: ``carry-on`` (front flap, handle) or ``under-seat`` (squat, a grab handle);
    ``wheels`` is ``yes`` (spinner wheels) or ``no`` (feet); ``shell`` is ``hard`` (ribs) or ``soft``."""
    under = kind.lower() == "under-seat"
    top, bottom = (190, 322) if under else (140, 322)
    x0, x1 = (110, 290) if under else (132, 268)
    mid = (x0 + x1) / 2
    out = []
    if not under:
        out += [_line(f"M{mid - 24},{top} L{mid - 24},{top - 30} M{mid + 24},{top} L{mid + 24},{top - 30}", 6, stroke=INK),
                _rect(mid - 34, top - 42, 68, 14, "#3a3a40", 6, LW_DETAIL)]  # fmt: skip
    else:
        out += [_line(f"M{mid - 26},{top} Q{mid},{top - 34} {mid + 26},{top}", 8, stroke=INK), _line(f"M{mid - 26},{top} Q{mid},{top - 34} {mid + 26},{top}", 4, stroke="#3a3a40")]
    out += _wheels(x0 + 20, x1 - 20, bottom - 2, "4") if wheels.lower() == "yes" else [_rect(x0 + 14, bottom - 2, 22, 9, "#3a3a40", 3, LW_DETAIL), _rect(x1 - 36, bottom - 2, 22, 9, "#3a3a40", 3, LW_DETAIL)]
    out += _case(paint, fill, x0, x1, top, bottom, shell.lower() == "hard")
    fy = top + (bottom - top) * 0.22
    out += [_path(f"M{x0 + 6},{top + 12} Q{x0 + 6},{top + 4} {x0 + 16},{top + 4} L{x1 - 16},{top + 4} Q{x1 - 6},{top + 4} {x1 - 6},{top + 12} L{x1 - 6},{fy} L{x0 + 6},{fy} Z", _tint(fill.base, 0.14), LW_DETAIL, ""),
            _rect(mid - 9, fy - 8, 18, 14, HARDWARE, 3, 1.2)]  # fmt: skip
    if label:
        out += _panel(mid - 40, bottom + 26, 80, 24, label, 14)
    return out


def holdall(paint: str, fill: Fill, label: str | None, wheels: str = "no", strap: str = "yes") -> list[str]:
    """A soft rectangular holdall with two handles; ``strap`` draws the shoulder strap and
    ``wheels`` ``yes`` a wheel pair at one end."""
    dark = _shade(fill.base, 0.3)
    out = []
    if strap.lower() == "yes":
        out += [_line("M96,196 Q200,110 304,196", 9, stroke=INK), _line("M96,196 Q200,110 304,196", 5, stroke=dark)]
    out += [_line("M150,168 Q150,120 190,120 L210,120 Q250,120 250,168", 9, stroke=INK), _line("M150,168 Q150,120 190,120 L210,120 Q250,120 250,168", 5, stroke=dark)]
    if wheels.lower() == "yes":
        out += [_circle(120, 320, 13, "#3a3a40", LW_DETAIL), _circle(280, 320, 13, "#3a3a40", LW_DETAIL)]
    out += [_path("M86,176 L314,176 Q330,176 330,192 L330,300 Q330,316 314,316 L86,316 Q70,316 70,300 L70,192 Q70,176 86,176 Z", paint),
            _line("M84,206 L316,206", 2.2, ' stroke-dasharray="7 4"'), _rect(188, 196, 24, 14, HARDWARE, 3, 1.4),
            _path("M96,236 L196,236 L196,298 Q196,304 190,304 L102,304 Q96,304 96,298 Z", _tint(fill.base, 0.1), LW_DETAIL),
            _highlight("M80,214 L80,290", 4, 0.3)]  # fmt: skip
    if label:
        out += _panel(150, 332, 100, 26, label, 15)
    return out


def weekend_bag(paint: str, fill: Fill, label: str | None, compartments: str = "1", sleeve: str = "no") -> list[str]:
    """A rounded duffel: two top handles, a zip, one end pocket per compartment beyond the first
    (``compartments``, at most 3) and a trolley sleeve strap across the back when ``sleeve`` is
    ``yes``."""
    n = min(max(_n(compartments, 1), 1), 3)
    dark = _shade(fill.base, 0.3)
    out = [_line("M148,160 Q152,100 200,100 Q248,100 252,160", 9, stroke=INK), _line("M148,160 Q152,100 200,100 Q248,100 252,160", 5, stroke=dark),
           _path("M80,190 Q80,150 130,150 L270,150 Q320,150 320,190 L320,290 Q320,326 284,326 L116,326 Q80,326 80,290 Z", paint),
           _line("M100,176 Q200,150 300,176", 2.4, ' stroke-dasharray="7 4"'), _rect(188, 156, 24, 14, HARDWARE, 3, 1.4),
           _highlight("M92,200 L92,290", 4, 0.3)]  # fmt: skip
    if sleeve.lower() == "yes":
        out += [_line("M116,238 L284,238", 14, stroke=INK), _line("M116,238 L284,238", 9, stroke=_tint(fill.base, 0.2))]
    for i in range(n - 1):
        x = 108 + i * 28
        out.append(_group("pocket", [_path(f"M{x},254 L{x + 22},254 L{x + 22},312 L{x},312 Z", _tint(fill.base, 0.12), LW_DETAIL), _rect(x + 6, 262, 10, 8, HARDWARE, 2, 1.0)]))
    out.append(_group("pocket", [_path("M248,254 L292,254 L292,312 L248,312 Z", _tint(fill.base, 0.12), LW_DETAIL), _rect(264, 262, 12, 9, HARDWARE, 2, 1.0)]))
    if label:
        out += _panel(150, 338, 100, 26, label, 15)
    return out


def luggage_set(paint: str, fill: Fill, label: str | None, pieces: str = "3") -> list[str]:
    """Two or three nested cases of falling height side by side, one ``class="piece"`` group each."""
    n = 2 if _n(pieces, 3) <= 2 else 3
    spans = {2: ((60, 190, 100), (220, 330, 170)), 3: ((40, 140, 170), (150, 250, 120), (264, 350, 190))}[n]
    plan = [(a, b, 322 - h) for (a, b, h) in sorted(spans, key=lambda s: -s[2])] if n == 3 else [(a, b, 322 - h) for (a, b, h) in spans]
    shades = (0.0, 0.1, 0.2)
    out = []
    for i, (x0, x1, top) in enumerate(sorted(plan, key=lambda p: p[0])):
        tone = _tint(fill.base, shades[i]) if paint == fill.base else paint
        mid = (x0 + x1) / 2
        out.append(_group("piece", [
            _line(f"M{mid - 12},{top} L{mid - 12},{top - 18} M{mid + 12},{top} L{mid + 12},{top - 18}", 4, stroke=INK),
            *_case(tone, fill, x0, x1, top, 322, True),
            _circle(x0 + 14, 330, 6, "#3a3a40", LW_DETAIL), _circle(x1 - 14, 330, 6, "#3a3a40", LW_DETAIL),
        ]))  # fmt: skip
    if label:
        out += _panel(150, 350, 100, 26, label, 15)
    return out


def travel_organizer(paint: str, fill: Fill, label: str | None, kind: str = "packing cubes") -> list[str]:
    """A travel organizer: ``packing cubes`` (a stack of three, ``class="cube"`` each),
    ``passport holder`` (a window and a crest), ``toiletry roll`` (a rolled bag with a strap) or
    ``adapter case`` (a small zip case with plug pins)."""
    k = kind.lower()
    out: list[str] = []
    if k == "passport holder":
        out += [_path("M112,92 L288,92 Q304,92 304,108 L304,320 Q304,336 288,336 L112,336 Q96,336 96,320 L96,108 Q96,92 112,92 Z", paint),
                _rect(136, 128, 128, 84, "#eef3f6", 8, LW_DETAIL), _ell(200, 252, 22, 22, "none", 1.6), _line("M200,232 L200,272 M180,252 L220,252", 1.4),
                _line("M104,300 L296,300", 1.8, ' stroke-dasharray="6 3"'), _highlight("M108,112 L108,300", 4, 0.3)]  # fmt: skip
    elif k == "toiletry roll":
        out += [_path("M60,170 L340,170 L340,270 L60,270 Z", paint),
                _ell(60, 220, 18, 50, _shade(fill.base, 0.15), LW), _ell(340, 220, 18, 50, _tint(fill.base, 0.1), LW),
                _line("M170,170 L170,270 M230,170 L230,270", 9, stroke=INK), _line("M170,170 L170,270 M230,170 L230,270", 5, stroke="#d9d2c0"),
                _rect(190, 150, 20, 14, HARDWARE, 3, 1.2), _highlight("M80,184 L320,184", 4, 0.3)]  # fmt: skip
    elif k == "adapter case":
        out += [_path("M96,150 L304,150 Q320,150 320,166 L320,274 Q320,290 304,290 L96,290 Q80,290 80,274 L80,166 Q80,150 96,150 Z", paint),
                _line("M96,176 L304,176", 2, ' stroke-dasharray="6 3"'), _rect(188, 164, 24, 12, HARDWARE, 3, 1.2),
                _rect(150, 200, 10, 34, "#b8bcc2", 2, LW_DETAIL), _rect(190, 200, 10, 34, "#b8bcc2", 2, LW_DETAIL), _rect(230, 200, 10, 34, "#b8bcc2", 2, LW_DETAIL),
                _highlight("M92,190 L92,270", 4, 0.3)]  # fmt: skip
    else:
        for i, (w, y) in enumerate(((190, 232), (170, 160), (150, 92))):
            x0 = 200 - w / 2
            out.append(_group("cube", [_path(f"M{x0 + 10},{y} L{x0 + w - 10},{y} Q{x0 + w},{y} {x0 + w},{y + 10} L{x0 + w},{y + 66} Q{x0 + w},{y + 76} {x0 + w - 10},{y + 76} L{x0 + 10},{y + 76} Q{x0},{y + 76} {x0},{y + 66} L{x0},{y + 10} Q{x0},{y} {x0 + 10},{y} Z", _tint(fill.base, 0.06 * i) if paint == fill.base else paint),
                                       _line(f"M{x0 + 8},{y + 14} L{x0 + w - 8},{y + 14}", 1.8, ' stroke-dasharray="6 3"'), _rect(200 - 8, y + 8, 16, 12, HARDWARE, 3, 1.2)]))  # fmt: skip
    if label:
        out += _panel(150, 350, 100, 26, label, 15)
    return out


def neck_pillow(paint: str, fill: Fill, label: str | None, hood: str = "no") -> list[str]:
    """A U shaped travel pillow open at the front; ``hood`` ``yes`` adds a hood behind the head."""
    out = []
    if hood.lower() == "yes":
        out += [_path("M112,196 Q108,70 200,66 Q292,70 288,196 Q250,160 200,160 Q150,160 112,196 Z", _tint(fill.base, 0.12), LW)]
    out += [_path("M96,150 Q96,92 200,92 Q304,92 304,150 L304,242 Q304,286 262,286 Q232,286 232,254 L232,186 Q232,170 200,170 Q168,170 168,186 L168,254 Q168,286 138,286 Q96,286 96,242 Z", paint),
            _line("M110,150 Q120,112 200,108 Q280,112 290,150", 2, ' stroke-dasharray="6 4"'),
            _highlight("M112,170 L112,244", 4, 0.35)]  # fmt: skip
    if label:
        out += _panel(150, 312, 100, 26, label, 15)
    return out


SHAPES = {
    "suitcase": suitcase, "cabin_case": cabin_case, "holdall": holdall, "weekend_bag": weekend_bag,
    "luggage_set": luggage_set, "travel_organizer": travel_organizer, "neck_pillow": neck_pillow,
}  # fmt: skip
register(SHAPES)
