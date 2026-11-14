"""Office and school supplies for the retail drawing kit (gen#969): pens, pencils, notebooks,
school backpacks, colored pencils and desk organizers.

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
school_backpack  a backpack from the front: its handle, a       backpack_style (classic, laptop,
                 zipped front pocket and the style's parts      rolling, mini)
colored_pencils  a tin, its lid open, the pencils standing in   pencil_type (classic, watercolor,
                 it and the set's count on its front            soft core, erasable), count
desk_organizer   compartments stepped front to back behind a    compartments (a number), material
                 front panel showing the material               (mesh, plastic, felt, metal)
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
#: A mini backpack's reflective strip.
REFLECT = "#dfe3e8"
#: The leads of a tin of colored pencils, left to right.
RAINBOW = ("#d93a3a", "#f08a24", "#f4d03f", "#4caf50", "#1e88e5", "#5e35b1", "#8d6e63", "#2a2a2e")
#: The most pencils a tin shows; a bigger set shows its count on the tin.
MOST_SHOWN = 12
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


def school_backpack(
    paint: str, fill: Fill, label: str | None, backpack_style: str = "classic"
) -> list[str]:
    """A school backpack from the front: the bag, its top handle, a zipped front pocket and, by
    ``backpack_style``, a padded laptop panel (laptop), a telescopic handle and wheels (rolling)
    or a smaller bag with a reflective strip (mini)."""
    mini = backpack_style == "mini"
    rolling = backpack_style == "rolling"
    x0, y0, w, h = (128, 120, 144, 196) if mini else (108, 96 if rolling else 76, 184, 246)
    x1, y1 = x0 + w, y0 + h
    out: list[str] = []
    if rolling:
        out += [
            _rect(150, 28, 10, y0 - 20, STEEL, 3, LW_DETAIL),
            _rect(240, 28, 10, y0 - 20, STEEL, 3, LW_DETAIL),
            _rect(144, 20, 112, 16, GRAPHITE, 6),
        ]
    out += [
        _path(f"M{x0 + 50},{y0 + 6} Q200,{y0 - 34} {x1 - 50},{y0 + 6}", "none", 8, "",
              _shade(fill.base, 0.35)),
        _rect(x0, y0, w, h, paint, 40),
        _line(f"M{x0 + 22},{y0 + 34} Q200,{y0 + 6} {x1 - 22},{y0 + 34}", LW_DETAIL),
    ]
    if backpack_style == "laptop":
        out += [
            _rect(x0 + 16, y0 + 46, w - 32, 50, _shade(fill.base, 0.12), 10, LW_DETAIL),
            _line(f"M{x0 + 24},{y0 + 71} L{x1 - 24},{y0 + 71}", 1.0, ' stroke-dasharray="4 4"'),
        ]
    py = y1 - (96 if mini else 118)
    out += [
        _rect(x0 + 24, py, w - 48, (76 if mini else 96), _shade(fill.base, 0.18), 18),
        _line(f"M{x0 + 36},{py + 16} L{x1 - 36},{py + 16}", LW_DETAIL),
        _rect(x1 - 52, py + 10, 10, 14, STEEL, 2, LW_DETAIL),
    ]
    if mini:
        out.append(_rect(x0 + 10, py - 26, w - 20, 12, REFLECT, 4, LW_DETAIL))
    if rolling:
        out += [_ell(x0 + 24, y1 + 4, 14, 14, GRAPHITE), _ell(x1 - 24, y1 + 4, 14, 14, GRAPHITE)]
    out.append(_highlight(f"M{x0 + 22},{y0 + 60} L{x0 + 22},{y1 - 40}", 6, 0.4))
    return _label(out, label)


def colored_pencils(
    paint: str, fill: Fill, label: str | None, pencil_type: str = "classic", count: str = "12"
) -> list[str]:
    """A tin of colored pencils: the open lid behind, the pencils standing in the tin in a
    rainbow of colors (thicker for ``soft core``), the tin's front in its color with the set's
    count, and a brush before a ``watercolor`` set or an eraser before an ``erasable`` one."""
    n = min(int(count), MOST_SHOWN)
    half = 9 if pencil_type == "soft core" else 7
    out = [_rect(72, 70, 256, 120, _shade(fill.base, 0.2), 10)]
    step = 224 / n
    for i in range(n):
        cx = 88 + step * (i + 0.5)
        top = 150 + (i % 2) * 14
        lead = RAINBOW[i % len(RAINBOW)]
        out += [
            _rect(cx - half, top, 2 * half, 120, lead, 2, LW_DETAIL),
            _path(f"M{cx - half},{top} L{cx + half},{top} L{cx},{top - 22} Z", WOOD, LW_DETAIL),
            _path(f"M{cx - 3},{top - 15} L{cx + 3},{top - 15} L{cx},{top - 22} Z", lead, 1.0),
        ]
    out += [
        _rect(64, 214, 272, 130, paint, 10),
        _rect(150, 250, 100, 52, PAPER, 6, LW_DETAIL),
        f'<text x="200" y="286" font-size="30" text-anchor="middle" fill="#2a2a2e">{count}</text>',
    ]
    if pencil_type == "watercolor":
        out += [
            _rect(90, 352, 170, 8, WOOD, 3, LW_DETAIL),
            _path("M260,350 L282,352 L292,356 L282,360 L260,362 Z", GRAPHITE, LW_DETAIL),
        ]
    elif pencil_type == "erasable":
        out.append(_rect(272, 346, 44, 22, ERASER, 5, LW_DETAIL))
    out.append(_highlight("M80,232 L80,326", 6, 0.4))
    return _label(out, label)


def desk_organizer(
    paint: str, fill: Fill, label: str | None, compartments: str = "4", material: str = "plastic"
) -> list[str]:
    """A desk organizer: its compartments stepped from front to back, each a section of its own,
    with a front panel in the organizer's color whose ``material`` shows as a mesh, a stitched
    felt edge, a metal sheen or plain plastic."""
    n = int(compartments)
    width = 252 / n
    out: list[str] = []
    for i in range(n):
        x = 74 + width * i
        top = 96 + ((i + 1) % 3) * 30
        out.append(_rect(x, top, width, 330 - top, _shade(fill.base, 0.12 + 0.06 * (i % 2)), 4))
    out.append(_rect(66, 236, 268, 110, paint, 6))
    if material == "mesh":
        out += [_line(f"M{x},{240} L{x},{342}", 1.0) for x in range(78, 330, 12)]
        out += [_line(f"M70,{y} L330,{y}", 1.0) for y in range(248, 344, 12)]
    elif material == "felt":
        edge = _rect(76, 246, 248, 90, "none", 4, 1.2)
        out.append(edge.replace("/>", ' stroke-dasharray="6 5"/>'))
    elif material == "metal":
        out.append(_highlight("M84,256 L316,256", 8, 0.55))
    out.append(_highlight("M76,252 L76,330", 5, 0.4))
    return _label(out, label)


SHAPES = {
    "pen": pen,
    "pencil": pencil,
    "spiral_notebook": spiral_notebook,
    "school_backpack": school_backpack,
    "colored_pencils": colored_pencils,
    "desk_organizer": desk_organizer,
}
register(SHAPES)
