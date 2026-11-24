"""Cooking appliance shapes for the retail drawing kit (#1116): range cookers, built-in ovens, hobs and
cooker hoods.

Each shape is drawn in the kit's ink with the record's fill on the body, so a black range and a
red one are one drawing in two fills; a hob's glass is black whatever the finish.

=============  ============================================================  ==================
shape          draws                                                         params
=============  ============================================================  ==================
range_cooker   a freestanding range seen front on, its hob on top: gas       kind, width, ovens
               burners with pan supports and knobs (dual fuel) or flat black
               zones and a touch strip (induction); 90, 100 or 110 cm wide,
               two or three oven doors with glass, a drawer at its foot
built_in_oven  an oven in a wood housing: one door (single) or two stacked   kind
               (double), each with glass and a handle
hob            a hob seen from above on a worktop: outlined zones on black   kind, width, zones
               glass (induction), ringed zones (ceramic) or burners under
               a grid (gas); 60 to 90 cm wide, its zones as many as it has
cooker_hood    a cooker hood seen front on: a chimney and a flared canopy    kind, width
               (chimney) or a slim hood under a wall cabinet (integrated),
               filters and lamps below; 50 to 100 cm wide
=============  ============================================================  ==================

Every params value is a string and every param has a default, so each shape draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
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
from synthetic_ecommerce_data.domains.retail.kit_appliances import (
    BLACK,
    GLASS,
    STEEL,
    STEEL_DARK,
    WOOD,
    _circle,
    _int,
    _rect,
    _shadow,
)

_FLOOR = 352
_RING = "#c8463a"  # a ceramic zone's heating ring
_ZONE = "#8f989f"  # an induction zone's printed outline


def _ring(cx: float, cy: float, r: float, stroke: str, width: float) -> str:
    """A zone printed on black glass: a ring in its own color, the glass showing through."""
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{stroke}" stroke-width="{width:g}"/>'


def _burner(cx: float, cy: float, r: float) -> list[str]:
    """A gas burner: a cap in a crown, under a cross of pan supports."""
    out = [_circle(cx, cy, r, STEEL_DARK, LW_DETAIL), _circle(cx, cy, r * 0.5, BLACK, LW_DETAIL)]
    out += [_line(f"M{cx - r * 1.3},{cy} L{cx + r * 1.3},{cy}", 3), _line(f"M{cx},{cy - r * 1.3} L{cx},{cy + r * 1.3}", 3)]
    return out


def _glass_door(x: float, y: float, w: float, h: float, paint: str) -> list[str]:
    """An oven door: the finish around a glass window, a bar handle above it."""
    out = [_rect(x, y, w, h, paint, 4, LW_DETAIL), _rect(x + 10, y + 22, w - 20, h - 32, BLACK, 3, LW_DETAIL)]
    out += [_rect(x + 14, y + 26, w - 28, h - 40, _shade(GLASS, 0.55), 2, 1), _rect(x + 10, y + 7, w - 20, 7, STEEL, 3, LW_DETAIL)]
    out.append(_highlight(f"M{x + 18},{y + h - 20} L{x + w * 0.45},{y + 32}", 3, 0.35))
    return out


def range_cooker(paint: str, fill: Fill, label: str | None, kind: str = "dual_fuel", width: str = "90", ovens: str = "2") -> list[str]:
    """A range cooker; see the module table."""
    cm = _int(width, 90)
    w = {100: 280, 110: 310}.get(cm, 250)
    x, top, h = 200 - w / 2, 120, _FLOOR - 120
    n = max(1, min(3, _int(ovens, 2)))
    out = [_shadow(200, _FLOOR + 4, w * 0.6)]
    # the hob, seen a little from above, then the body front on
    if kind == "induction":
        out.append(_rect(x - 4, top - 34, w + 8, 34, BLACK, 4))
        out += [_ring(x + w * (0.2 + i * 0.2), top - 17, 11, _ZONE, 1.5) for i in range(4)]
    else:
        out.append(_rect(x - 4, top - 34, w + 8, 34, _shade(fill.base, 0.15), 4))
        for i in range(5 if cm >= 100 else 4):
            out += _burner(x + w * (0.14 + i * (0.72 / (4 if cm >= 100 else 3))), top - 17, 9)
    out += [_rect(x, top, w, h, paint, 6), _highlight(f"M{x + 8},{top + 14} L{x + 8},{_FLOOR - 14}", 4, 0.4)]
    # the control strip: knobs for gas, a touch strip for induction
    if kind == "induction":
        out.append(_rect(x + w * 0.2, top + 10, w * 0.6, 16, BLACK, 4, LW_DETAIL))
    else:
        for i in range(6):
            out.append(_circle(x + w * (0.12 + i * 0.152), top + 18, 8, STEEL, LW_DETAIL))
    # the oven doors side by side, the widest first, and the storage drawer at the foot
    dy, dh = top + 36, h - 100
    widths = (1.0,) if n == 1 else (0.58, 0.42) if n == 2 else (0.42, 0.29, 0.29)
    cx = x + 10
    for part in widths:
        dw = (w - 10 * (len(widths) + 1)) * part
        out += _glass_door(cx, dy, dw, dh, _tint(fill.base, 0.08))
        cx += dw + 10
    out += [_rect(x + 10, _FLOOR - 54, w - 20, 44, _tint(fill.base, 0.08), 4, LW_DETAIL), _rect(200 - 30, _FLOOR - 40, 60, 6, STEEL, 3, LW_DETAIL)]
    return out


def built_in_oven(paint: str, fill: Fill, label: str | None, kind: str = "single") -> list[str]:
    """A built-in oven in its wood housing: one door, or two stacked for a double."""
    out = [_rect(90, 50, 220, 302, WOOD, 3), _rect(102, 70 if kind == "double" else 120, 196, 262 if kind == "double" else 170, paint, 4)]
    if kind == "double":
        out += [_rect(110, 78, 180, 18, BLACK, 3, LW_DETAIL), _circle(270, 87, 5, STEEL, 1)]
        out += _glass_door(110, 102, 180, 92, _tint(fill.base, 0.06)) + _glass_door(110, 202, 180, 122, _tint(fill.base, 0.06))
    else:
        out += [_rect(110, 128, 180, 18, BLACK, 3, LW_DETAIL), _circle(130, 137, 5, STEEL, 1), _circle(270, 137, 5, STEEL, 1)]
        out += _glass_door(110, 152, 180, 130, _tint(fill.base, 0.06))
    out.append(_line("M90,352 L310,352", LW))
    return out


def _zones(n: int) -> list[tuple[float, float, float]]:
    """Where a hob's zones sit on a 0..1 plate, and each one's size: (x, y, r)."""
    if n <= 2:
        return [(0.3, 0.5, 0.3), (0.7, 0.5, 0.22)][:n]
    if n == 3:
        return [(0.25, 0.3, 0.2), (0.25, 0.72, 0.16), (0.7, 0.5, 0.28)]
    four = [(0.25, 0.28, 0.18), (0.25, 0.72, 0.2), (0.75, 0.28, 0.2), (0.75, 0.72, 0.16)]
    if n == 4:
        return four
    return [(0.16, 0.28, 0.14), (0.16, 0.72, 0.16), (0.5, 0.5, 0.22), (0.84, 0.28, 0.16), (0.84, 0.72, 0.14)]


def hob(paint: str, fill: Fill, label: str | None, kind: str = "induction", width: str = "60", zones: str = "4") -> list[str]:
    """A hob from above on a worktop: induction, ceramic or gas; see the module table."""
    cm = _int(width, 60)
    w = 200 + (max(60, min(90, cm)) - 60) * 3
    x, y, h = 200 - w / 2, 120, 170
    out = [_rect(30, 90, 340, 230, WOOD, 4)]
    gas = kind == "gas"
    out.append(_rect(x, y, w, h, paint if gas else BLACK, 6))
    s = min(w, h)
    for zx, zy, zr in _zones(max(2, min(5, _int(zones, 4)))):
        cx, cy, r = x + w * zx, y + h * zy, s * zr * (0.9 if gas else 1.0)
        if gas:
            out += _burner(cx, cy, r * 0.6)
        elif kind == "ceramic":
            out += [_ring(cx, cy, r, _RING, 2.5), _ring(cx, cy, r * 0.62, _RING, 1.5)]
        else:
            out.append(_ring(cx, cy, r, _ZONE, 1.5))
    if gas:
        out += [_line(f"M{x + 6},{y + h / 2} L{x + w - 6},{y + h / 2}", 4), _line(f"M{x + w / 2},{y + 6} L{x + w / 2},{y + h - 6}", 4)]
        out += [_circle(x + w * (0.2 + i * 0.2), y + h + 14, 7, STEEL, LW_DETAIL) for i in range(4)]
    else:
        out.append(f'<rect x="{x + w * 0.3:.1f}" y="{y + h - 22:.1f}" width="{w * 0.4:.1f}" height="12" rx="3" fill="none" stroke="{_ZONE}" stroke-width="1"/>')
    out.append(_highlight(f"M{x + 12},{y + 16} L{x + w * 0.35},{y + 16}", 3, 0.3))
    return out


def cooker_hood(paint: str, fill: Fill, label: str | None, kind: str = "chimney", width: str = "60") -> list[str]:
    """A cooker hood seen front on: a chimney over a flared canopy, or a slim hood in a wall cabinet."""
    cm = _int(width, 60)
    w = 220 + (max(50, min(100, cm)) - 50) * 2.4
    x, y = 200 - w / 2, 236
    out: list[str] = []
    if kind == "integrated":
        out += [_rect(x, 48, w, y - 48, WOOD, 3), _line(f"M200,56 L200,{y - 8}", LW_DETAIL)]
        out += [_circle(190, y - 40, 4, STEEL, 1), _circle(210, y - 40, 4, STEEL, 1)]
    else:
        out += [_rect(148, 40, 104, 132, paint, 2), _line("M148,132 L252,132"), _highlight("M160,52 L160,160", 4, 0.4)]
        out.append(_path(f"M148,172 L252,172 L{x + w},{y} L{x},{y} Z", _tint(fill.base, 0.06)))
    # the canopy's lip with its buttons, then the filters and lamps underneath it
    out += [_rect(x, y, w, 34, paint, 3), _highlight(f"M{x + 10},{y + 8} L{x + w * 0.5},{y + 8}", 3, 0.4)]
    out += [_circle(x + w * (0.4 + i * 0.05), y + 19, 4, STEEL_DARK, 1) for i in range(5)]
    out.append(_path(f"M{x + 8},{y + 34} L{x + w - 8},{y + 34} L{x + w - 26},{y + 78} L{x + 26},{y + 78} Z", STEEL))
    out += [_line(f"M{x + 30},{y + 44 + i * 9} L{x + w - 30},{y + 44 + i * 9}", 1.5) for i in range(4)]
    out += [_circle(x + w * 0.25, y + 72, 7, "#fff3c4", LW_DETAIL), _circle(x + w * 0.75, y + 72, 7, "#fff3c4", LW_DETAIL)]
    return out


register({"range_cooker": range_cooker, "built_in_oven": built_in_oven, "hob": hob, "cooker_hood": cooker_hood})

#: The shapes this module adds, in its table's order.
SHAPES = ("range_cooker", "built_in_oven", "hob", "cooker_hood")
