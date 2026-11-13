"""Office and school supplies for the retail drawing kit (gen#969): pens, pencils, notebooks.

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


SHAPES = {"pen": pen, "pencil": pencil, "spiral_notebook": spiral_notebook}
register(SHAPES)
