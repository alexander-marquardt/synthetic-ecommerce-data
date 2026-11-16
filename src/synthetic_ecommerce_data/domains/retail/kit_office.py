"""Office and school supplies for the retail drawing kit (gen#969): pens, pencils, notebooks,
binders, folders and calculators.

===============  =============================================  ==================================
shape            draws                                          params
===============  =============================================  ==================================
pen              a pen at a slant: its barrel in the ink's      style (ballpoint, gel, rollerball,
                 color, its tip and, by ``mechanism``, a click  felt tip), mechanism (retractable,
                 button or a cap with its clip                  capped)
pencil           a sharpened wooden pencil at a slant, with an  eraser (yes, no)
                 eraser in its ferrule or a dipped end
spiral_notebook  a closed notebook: the cover, its coil along   binding (side bound, top bound),
                 the bound edge, and a cover panel showing the  ruling (lined, squared, plain,
                 ruling                                         dotted)
ring_binder      an open binder lying flat: both covers, the    ring_type (round ring, d-ring,
                 spine, a stack of punched sheets and the ring  slanted ring)
                 mechanism, whose rings are round, D-shaped or
                 slanted
document_folder  a closed folder: its back, its front with a    closure (elastic, press stud, zip)
                 flap and, by ``closure``, two elastic bands, a
                 press stud on the flap or a zip with its pull
calculator       a calculator face on: its case, the display    calculator_type (pocket, basic,
                 and a key grid; ``calculator_type`` sets the   desktop, scientific), power
                 case and the grid, ``power`` a solar strip or  (solar, dual power, battery)
                 none
===============  =============================================  ==================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a pen's ``style`` or a notebook's ``ruling`` draws what it states (gen#512).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    PAPER,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: The metal of a pen's or a pencil's tip, clip and button.
STEEL = "#c3c7cd"
#: The bare wood of a sharpened pencil and its graphite core.
WOOD = "#e8c690"
GRAPHITE = "#4a4a50"
#: A pencil's eraser.
ERASER = "#e9a3a0"
#: The ruling printed on a notebook's cover panel.
RULE = "#6d86a8"
#: A binder's rings, darker than the plate they are riveted to.
RING = "#7d838c"
#: A document folder's elastic bands.
INK_BAND = "#2a2a2e"
#: A calculator's display and its solar cell.
DISPLAY = "#c9d4b8"
SOLAR = "#3b3f58"
#: Every pen and pencil is drawn at this slant, about the center of the sheet.
SLANT = '<g transform="rotate(35 200 200)">'


def _slanted(parts: list[str]) -> list[str]:
    return [SLANT, *parts, "</g>"]


def pen(
    paint: str,
    fill: Fill,
    label: str | None,
    style: str = "ballpoint",
    mechanism: str = "retractable",
) -> list[str]:
    """A pen: the barrel, a tip by ``style`` and, by ``mechanism``, a click button or a cap."""
    half = 22 if style == "felt tip" else 16
    x0, x1 = 200 - half, 200 + half
    out = [_rect(x0, 70, 2 * half, 226, paint, 10)]
    if style == "gel":
        out.append(_rect(x0 + 2, 232, 2 * half - 4, 64, _tint(fill.base, 0.55), 6, LW_DETAIL))
        out += [_line(f"M{x0 + 4},{y} L{x1 - 4},{y}", LW_DETAIL) for y in range(244, 292, 10)]
    if style == "felt tip":
        out += [
            _path(f"M{x0},296 L{x1},296 L208,322 L192,322 Z", _shade(fill.base, 0.3)),
            _path("M193,322 L207,322 L205,348 Q200,356 195,348 Z", paint),
        ]
    elif style == "rollerball":
        out += [
            _path(f"M{x0},296 L{x1},296 L203,330 L197,330 Z", STEEL),
            _rect(197.5, 330, 5, 22, STEEL, 2, LW_DETAIL),
        ]
    else:
        out += [
            _path(f"M{x0},296 L{x1},296 L202,338 L198,338 Z", STEEL),
            _ell(200, 341, 3, 3, GRAPHITE, LW_DETAIL),
        ]
    if mechanism == "capped":
        out += [
            _rect(x0 - 4, 52, 2 * half + 8, 96, _shade(fill.base, 0.15), 12),
            _rect(x1 + 2, 62, 8, 78, STEEL, 3, LW_DETAIL),
            _ell(200, 52, half + 2, 6, _shade(fill.base, 0.35), LW_DETAIL),
        ]
    else:
        out += [
            _rect(192, 44, 16, 30, STEEL, 4),
            _rect(x1 - 2, 80, 8, 92, STEEL, 3, LW_DETAIL),
        ]
    out.append(_highlight(f"M{x0 + 8},{90} L{x0 + 8},{220}", 5, 0.5))
    return _label(_slanted(out), label)


def pencil(paint: str, fill: Fill, label: str | None, eraser: str = "yes") -> list[str]:
    """A sharpened wooden pencil: the barrel, its facets and point, and an eraser in its ferrule
    (``eraser`` yes) or an end dipped in the barrel's color (no)."""
    out = [
        _rect(182, 84, 36, 206, paint, 2),
        _line("M194,84 L194,290", LW_DETAIL, "", _shade(fill.base, 0.35)),
        _line("M206,84 L206,290", LW_DETAIL, "", _shade(fill.base, 0.35)),
        _path("M182,290 L218,290 L204,332 L196,332 Z", WOOD),
        _path("M196,332 L204,332 L200,346 Z", GRAPHITE),
    ]
    if eraser == "yes":
        out += [
            _rect(182, 58, 36, 28, STEEL, 2),
            _line("M182,66 L218,66", LW_DETAIL),
            _line("M182,78 L218,78", LW_DETAIL),
            _rect(184, 32, 32, 28, ERASER, 8),
        ]
    else:
        out.append(_rect(182, 70, 36, 20, _shade(fill.base, 0.25), 3))
    out.append(_highlight("M190,96 L190,280", 5, 0.45))
    return _label(_slanted(out), label)


def _ruling(ruling: str, x0: float, y0: float, x1: float, y1: float) -> list[str]:
    """The ruling of a page, printed in the box ``(x0, y0)`` to ``(x1, y1)``."""
    if ruling == "lined":
        return [_line(f"M{x0 + 8},{y} L{x1 - 8},{y}", LW_DETAIL, "", RULE)
                for y in range(int(y0) + 14, int(y1) - 4, 14)]  # fmt: skip
    if ruling == "squared":
        rows = [_line(f"M{x0 + 6},{y} L{x1 - 6},{y}", 1.0, "", RULE)
                for y in range(int(y0) + 10, int(y1) - 4, 10)]  # fmt: skip
        cols = [_line(f"M{x},{y0 + 6} L{x},{y1 - 6}", 1.0, "", RULE)
                for x in range(int(x0) + 10, int(x1) - 4, 10)]  # fmt: skip
        return rows + cols
    if ruling == "dotted":
        return [_ell(x, y, 1.6, 1.6, RULE, 0) for y in range(int(y0) + 12, int(y1) - 4, 12)
                for x in range(int(x0) + 12, int(x1) - 4, 12)]  # fmt: skip
    return []


def _coil(cx: float, cy: float, rx: float, ry: float) -> str:
    """One loop of a notebook's wire coil: an open steel ring through the bound edge."""
    return (
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
        f'fill="none" stroke="{STEEL}" stroke-width="3"/>'
    )


def spiral_notebook(
    paint: str, fill: Fill, label: str | None, binding: str = "side bound", ruling: str = "lined"
) -> list[str]:
    """A closed spiral notebook: the cover, the coil on its bound edge and a panel of its ruling."""
    top = binding == "top bound"
    x0, y0, x1, y1 = (90, 74, 320, 352) if top else (104, 48, 326, 350)
    out = [
        _rect(x0 + 6, y0 + 6, x1 - x0, y1 - y0, PAPER, 6),
        _rect(x0, y0, x1 - x0, y1 - y0, paint, 6),
    ]
    px0, py0 = (x0 + 50, y0 + 70) if top else (x0 + 46, y0 + 60)
    out.append(_rect(px0, py0, 130, 92, PAPER, 4, LW_DETAIL))
    out += _ruling(ruling, px0, py0, px0 + 130, py0 + 92)
    if top:
        out += [_coil(x, y0, 5, 13) for x in range(x0 + 14, x1 - 6, 16)]
    else:
        out += [_coil(x0, y, 13, 5) for y in range(y0 + 14, y1 - 6, 16)]
    out.append(_highlight(f"M{x1 - 16},{y0 + 20} L{x1 - 16},{y1 - 20}", 5, 0.4))
    return _label(out, label)


def _ring(kind: str, cx: float, cy: float) -> str:
    """One binder ring seen from above the open binder: round, D-shaped (flat on the back cover's
    side) or slanted."""
    if kind == "d-ring":
        d = (f"M{cx - 14},{cy - 24} L{cx - 14},{cy + 24} L{cx + 2},{cy + 24} "
             f"Q{cx + 28},{cy} {cx + 2},{cy - 24} Z")  # fmt: skip
        return _path(d, "none", 6, "", RING)
    if kind == "slanted ring":
        return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="12" ry="25" fill="none" stroke="{RING}" '
                f'stroke-width="6" transform="rotate(-28 {cx:.1f} {cy:.1f})"/>')  # fmt: skip
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="20" fill="none" stroke="{RING}" '
            f'stroke-width="6"/>')  # fmt: skip


def ring_binder(
    paint: str, fill: Fill, label: str | None, ring_type: str = "round ring"
) -> list[str]:
    """An open ring binder lying flat: both covers, the spine between them, a stack of punched
    sheets on the right and the mechanism's rings by ``ring_type`` (round, D-shaped, slanted)."""
    out = [
        _rect(40, 88, 160, 236, paint, 6),
        _rect(214, 88, 160, 236, paint, 6),
        _rect(196, 88, 22, 236, _shade(fill.base, 0.25), 2),
        _rect(70, 120, 100, 150, _tint(fill.base, 0.35), 4, LW_DETAIL),
        _rect(226, 98, 138, 216, PAPER, 2, LW_DETAIL),
        _rect(200, 132, 18, 152, STEEL, 4, LW_DETAIL),
    ]
    out += [_line(f"M{250},{y} L{352},{y}", LW_DETAIL, "", RULE) for y in range(128, 300, 18)]
    out += [_ring(ring_type, 222, y) for y in (166, 250)]
    out.append(_highlight("M56,108 L56,300", 5, 0.4))
    return _label(out, label)


def document_folder(
    paint: str, fill: Fill, label: str | None, closure: str = "elastic"
) -> list[str]:
    """A closed document folder: its back, its front panel with a flap folded over the top and,
    by ``closure``, two elastic bands over the corners, a press stud on the flap or a zip with
    its pull along the top."""
    zip_ = closure == "zip"
    out = [
        _rect(70, 70, 270, 290, _shade(fill.base, 0.2), 8),
        _rect(60, 84, 270, 280, paint, 8),
        _rect(84, 200, 120, 70, _tint(fill.base, 0.5), 4, LW_DETAIL),
    ]
    if zip_:
        out += [
            _rect(60, 84, 270, 22, _shade(fill.base, 0.35), 4, LW_DETAIL),
            *[_line(f"M{x},90 L{x},100", 2.0, "", STEEL) for x in range(72, 320, 8)],
            _rect(282, 98, 16, 34, STEEL, 4),
        ]
    else:
        out.append(_path("M60,84 L330,84 L330,150 Q195,176 60,150 Z", _shade(fill.base, 0.12)))
    if closure == "elastic":
        out += [
            _line("M92,84 L60,118", 7, "", INK_BAND),
            _line("M298,364 L330,330", 7, "", INK_BAND),
        ]
    elif closure == "press stud":
        out += [_ell(195, 160, 13, 13, STEEL), _ell(195, 160, 5, 5, _shade(STEEL, 0.3), LW_DETAIL)]
    out.append(_highlight("M84,200 L84,340", 5, 0.4))
    return _label(out, label)


def _keys(x0: float, y0: float, cols: int, rows: int, w: float, h: float, gap: float,
          paint: str) -> list[str]:  # fmt: skip
    """A grid of calculator keys, the right-hand column in the case's color (the operators)."""
    return [_rect(x0 + c * (w + gap), y0 + r * (h + gap), w, h, paint if c == cols - 1 else PAPER,
                  4, LW_DETAIL)
            for r in range(rows) for c in range(cols)]  # fmt: skip


def calculator(paint: str, fill: Fill, label: str | None, calculator_type: str = "pocket",
               power: str = "solar") -> list[str]:  # fmt: skip
    """A calculator face on: its case in the color, a display, a solar strip unless ``power`` is
    battery, and a key grid by ``calculator_type``: a slim case of 4 x 5 keys (pocket), a broader
    one of 4 x 6 keys (basic), a wide one of 5 x 5 big keys (desktop) or a tall one of 6 x 8 small
    keys (scientific)."""
    x0, y0, w, h, cols, rows = {
        "desktop": (64, 56, 272, 300, 5, 5),
        "scientific": (110, 30, 180, 340, 6, 8),
        "basic": (100, 40, 200, 320, 4, 6),
    }.get(calculator_type, (120, 50, 160, 300, 4, 5))
    out = [_rect(x0, y0, w, h, paint, 18), _rect(x0 + 14, y0 + 44, w - 28, 54, DISPLAY, 6)]
    out.append(_line(f"M{x0 + 28},{y0 + 84} L{x0 + w - 28},{y0 + 84}", LW_DETAIL, "", GRAPHITE))
    if power != "battery":
        out.append(_rect(x0 + w - 74, y0 + 14, 60, 20, SOLAR, 3, LW_DETAIL))
    gap = 8
    top = y0 + 112
    kw = (w - 28 - gap * (cols - 1)) / cols
    kh = (h - 128 - gap * (rows - 1)) / rows
    out += _keys(x0 + 14, top, cols, rows, kw, kh, gap, _shade(fill.base, 0.3))
    out.append(_highlight(f"M{x0 + 8},{y0 + 30} L{x0 + 8},{y0 + h - 30}", 4, 0.4))
    return _label(out, label)


SHAPES = {
    "pen": pen,
    "pencil": pencil,
    "spiral_notebook": spiral_notebook,
    "ring_binder": ring_binder,
    "document_folder": document_folder,
    "calculator": calculator,
}
register(SHAPES)
