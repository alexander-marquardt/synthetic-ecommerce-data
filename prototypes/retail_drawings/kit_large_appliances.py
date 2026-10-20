"""Large appliance shapes for the retail drawing kit (gen#334): fridges, freezers, dishwashers,
washing machines and tumble dryers, and the three small things their names are borrowed by.

Each shape is drawn front on, in the kit's ink, with the record's fill on the body; the finish is
the SKU's color, so a stainless fridge and a white one are one drawing in two fills.

==================  =====================================================  ==================
shape               draws                                                  params
==================  =====================================================  ==================
fridge              a tall two-door fridge freezer (the freezer below, 70/30 or 50/50), a
                    side-by-side pair of tall doors, a short under-counter fridge, a tall
                    larder fridge, a chest freezer (lid, seen a little from above), a tall
                    freezer of drawers or an integrated fridge (a fascia panel, hinge marks)
                    kind
dishwasher          a front-loading door with a handle and a control strip, in a full-size,
                    slimline (narrow), integrated (a panel and no handle) or table-top
                    (small, on a counter) body                               kind
washing_machine     a front loader with a round porthole door, a dial and a drawer
tumble_dryer        a front loader with a porthole door; a condenser shows its water tank, a
                    vented one its hose, a heat pump its plinth              kind
washer_dryer        a front loader with a large porthole and two dials
fridge_magnet       three small magnets on a card (a decoy's true type)
fridge_thermometer  a dial thermometer on a hook (a decoy's true type)
anti_vibration_mat  four rubber pads (a decoy's true type)
==================  =====================================================  ==================

Every params value is a string and every param has a default, so each shape draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _shade, _tint, register
from kit_appliances import BLACK, GLASS, STEEL, STEEL_DARK, WATER, _circle, _rect, _shadow

_FLOOR = 352


def _body(x: float, y: float, w: float, h: float, paint: str, fill: Fill) -> list[str]:
    return [_shadow(x + w / 2, y + h + 4, w * 0.62), _rect(x, y, w, h, paint, 6),
            _highlight(f"M{x + 8},{y + 14} L{x + 8},{y + h - 14}", 4, 0.4)]  # fmt: skip


def _bar(x: float, y: float, h: float) -> str:
    return _rect(x, y, 6, h, STEEL, 3, LW_DETAIL)


def fridge(paint: str, fill: Fill, label: str | None, kind: str = "fridge_freezer_7030") -> list[str]:
    """One of eight fridges and freezers; see the module table."""
    if kind == "chest":
        out = [_shadow(200, _FLOOR + 4, 190), _rect(60, 230, 280, 122, paint, 6), _rect(52, 200, 296, 40, _tint(fill.base, 0.12), 6)]
        out += [_rect(168, 213, 64, 12, STEEL, 5, LW_DETAIL), _rect(70, 340, 20, 12, BLACK, 2, 1), _rect(310, 340, 20, 12, BLACK, 2, 1)]
        return out
    if kind == "side_by_side":
        x, y, w, h = 70, 40, 260, 312
        out = _body(x, y, w, h, paint, fill)
        out.append(_line(f"M{x + w / 2},{y} L{x + w / 2},{y + h}", LW))
        out += [_bar(x + w / 2 - 14, y + 90, 90), _bar(x + w / 2 + 8, y + 90, 90), _rect(x + 40, y + 60, 50, 70, _tint(fill.base, 0.2), 4, LW_DETAIL)]
        return out
    if kind == "under_counter":
        x, y, w, h = 110, 200, 180, 152
        out = _body(x, y, w, h, paint, fill)
        out += [_bar(x + w - 18, y + 20, 50), _rect(x - 20, y - 12, w + 40, 12, WOOD_TOP, 2, LW_DETAIL)]
        return out
    if kind in {"upright_freezer", "larder"}:
        x, y, w, h = 105, 50, 190, 302
        out = _body(x, y, w, h, paint, fill)
        if kind == "upright_freezer":
            for i in range(4):
                out += [_line(f"M{x},{y + 70 + i * 58} L{x + w},{y + 70 + i * 58}", LW), _rect(x + 55, y + 82 + i * 58, 80, 8, STEEL, 4, LW_DETAIL)]
        else:
            out += [_bar(x + w - 18, y + 80, 100), _rect(x + 24, y + 22, 60, 22, _tint(fill.base, 0.2), 4, LW_DETAIL)]
        return out
    if kind == "integrated":
        x, y, w, h = 105, 50, 190, 302
        out = _body(x, y, w, h, paint, fill)
        out += [_rect(x + 6, y + 6, w - 12, 36, _tint(fill.base, 0.18), 3, LW_DETAIL)]
        out += [_circle(x + 18, y + 120, 4, STEEL_DARK, 1), _circle(x + 18, y + 230, 4, STEEL_DARK, 1), _bar(x + w - 18, y + 80, 90)]
        return out
    split = 0.5 if kind.endswith("5050") else 0.7
    x, y, w, h = 95, 40, 210, 312
    out = _body(x, y, w, h, paint, fill)
    cut = y + h * split
    out += [_line(f"M{x},{cut} L{x + w},{cut}", LW), _bar(x + w - 20, cut - 70, 60), _bar(x + w - 20, cut + 14, 36)]
    return out


WOOD_TOP = "#b8875a"


def _door(cx: float, cy: float, r: float, glass: str = GLASS) -> list[str]:
    return [_circle(cx, cy, r, STEEL, LW), _circle(cx, cy, r * 0.78, glass, LW_DETAIL), _highlight(f"M{cx - r * 0.5},{cy - r * 0.3} Q{cx - r * 0.3},{cy - r * 0.6} {cx},{cy - r * 0.6}", 3, 0.5)]


def dishwasher(paint: str, fill: Fill, label: str | None, kind: str = "full") -> list[str]:
    """A dishwasher front: full-size, slimline, integrated or table-top."""
    w = {"slim": 140, "tabletop": 190}.get(kind, 220)
    h = 150 if kind == "tabletop" else 280
    x, y = 200 - w / 2, _FLOOR - h
    out = _body(x, y, w, h, paint, fill)
    out.append(_rect(x + 8, y + 8, w - 16, 26, _tint(fill.base, 0.16), 3, LW_DETAIL))
    for i in range(3):
        out.append(_circle(x + 22 + i * 18, y + 21, 4, STEEL_DARK, 1))
    if kind == "integrated":
        out.append(_rect(x + 8, y + 40, w - 16, h - 48, _tint(fill.base, 0.1), 3, LW_DETAIL))
    else:
        out += [_rect(x + 24, y + 46, w - 48, 12, STEEL, 6, LW_DETAIL), _line(f"M{x + 8},{y + 66} L{x + w - 8},{y + 66}", LW_DETAIL)]
    if kind == "tabletop":
        out.append(_rect(x - 24, y + h, w + 48, 14, WOOD_TOP, 2, LW_DETAIL))
    return out


def washing_machine(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A front loader: the drawer, a dial and a porthole door."""
    x, y, w, h = 105, 70, 190, 282
    out = _body(x, y, w, h, paint, fill)
    out += [_rect(x + 14, y + 12, 56, 24, _tint(fill.base, 0.2), 3, LW_DETAIL), _circle(x + w - 40, y + 24, 14, STEEL, LW_DETAIL)]
    out += _door(200, y + 160, 66)
    return out


def tumble_dryer(paint: str, fill: Fill, label: str | None, kind: str = "condenser") -> list[str]:
    """A tumble dryer front; a condenser shows its water tank, a vented one a rear hose, a heat pump a plinth."""
    x, y, w, h = 105, 70, 190, 282
    out = _body(x, y, w, h, paint, fill)
    if kind == "vented":
        out.append(f'<path d="M{x + w},{y + 60} q50,0 50,40 t-30,60" fill="none" stroke="{INK}" stroke-width="{LW}"/>')
    out += [_rect(x + 14, y + 12, w - 28, 24, _tint(fill.base, 0.2), 3, LW_DETAIL), _circle(x + w - 36, y + 24, 9, STEEL, LW_DETAIL)]
    out += _door(200, y + 158, 62, _tint(fill.base, 0.35))
    if kind == "condenser":
        out.append(_rect(x + 40, y + h - 30, w - 80, 16, WATER, 3, LW_DETAIL))
    if kind == "heat_pump":
        out.append(_rect(x, y + h - 22, w, 22, _shade(fill.base, 0.2), 3, LW_DETAIL))
    return out


def washer_dryer(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A front loader with a wide porthole and a wash dial beside a dry dial."""
    x, y, w, h = 105, 70, 190, 282
    out = _body(x, y, w, h, paint, fill)
    out += [_rect(x + 14, y + 12, 50, 22, _tint(fill.base, 0.2), 3, LW_DETAIL), _circle(x + w - 62, y + 24, 12, STEEL, LW_DETAIL), _circle(x + w - 30, y + 24, 12, STEEL_DARK, LW_DETAIL)]
    out += _door(200, y + 165, 78)
    return out


def fridge_magnet(paint: str, fill: Fill, label: str | None) -> list[str]:
    """Three small fridge magnets on a card."""
    out = [_rect(70, 130, 260, 150, "#fbfaf6", 6)]
    for i, tint in enumerate((fill.base, _tint(fill.base, 0.3), _shade(fill.base, 0.25))):
        out.append(_circle(130 + i * 70, 205, 26, tint, LW))
    return out


def fridge_thermometer(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A dial thermometer on a hook."""
    return [_line("M200,90 L200,130", LW), _circle(200, 200, 70, paint, LW), _circle(200, 200, 54, "#fbfaf6", LW_DETAIL), _line("M200,200 L232,170", 4)]


def anti_vibration_mat(paint: str, fill: Fill, label: str | None) -> list[str]:
    """Four rubber pads in a square."""
    return [_rect(x, y, 90, 90, paint, 10) for x in (100, 210) for y in (130, 240)]


register({
    "fridge": fridge, "dishwasher": dishwasher, "washing_machine": washing_machine,
    "tumble_dryer": tumble_dryer, "washer_dryer": washer_dryer, "fridge_magnet": fridge_magnet,
    "fridge_thermometer": fridge_thermometer, "anti_vibration_mat": anti_vibration_mat,
})  # fmt: skip

#: The shapes this module adds, in its table's order.
SHAPES = ("fridge", "dishwasher", "washing_machine", "tumble_dryer", "washer_dryer", "fridge_magnet",
          "fridge_thermometer", "anti_vibration_mat")  # fmt: skip
