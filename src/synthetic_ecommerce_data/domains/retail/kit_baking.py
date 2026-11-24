"""Home baking for the retail drawing kit (gen#1119): a brownie mix and a brownie tin.

===========  =======================================================  =============================
shape        draws                                                    params
===========  =======================================================  =============================
brownie_mix  a carton with a stack of brownies on its front, what     topping (none, caramel, nuts,
             tops them by the flavor, and a foil tray beside the      hazelnuts, berries, white, toffee,
             carton of a kit that holds one                           marble, sugar), tray (no, yes)
brownie_tin  a baking tin seen from above its front edge: square or   outline (square, rectangular),
             rectangular, shallow or deep, with a loose base's ring,  base (fixed, loose), cells
             twelve cells, a speckled enamel or a lid behind it       (1, 12), depth (shallow, deep),
                                                                      finish (plain, speckled),
                                                                      lid (no, yes)
===========  =======================================================  =============================

Every params value is a string and every param has a default, so each shape draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
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
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: A baked brownie's crumb, its crust and a foil tray.
CRUMB = "#4a2a1a"
CRUST = "#6b4226"
FOIL = "#c9ced2"
#: What a flavor scatters on the brownies: topping -> its color.
TOPPINGS = {
    "caramel": "#d08a3c",
    "nuts": "#c9a26b",
    "hazelnuts": "#b07a45",
    "berries": "#b8325a",
    "white": "#f3e9d2",
    "toffee": "#d9a441",
    "marble": "#e0c08a",
    "sugar": "#ffffff",
}


def _brownie(x: float, y: float, w: float, topping: str) -> list[str]:
    """One brownie square seen from its front corner, ``w`` wide, with its topping."""
    out = [
        _path(f"M{x},{y} L{x + 14},{y - 14} L{x + w + 14},{y - 14} L{x + w},{y} Z", CRUST, 2),
        _path(f"M{x + w},{y} L{x + w + 14},{y - 14} L{x + w + 14},{y + 12} L{x + w},{y + 26} Z", _shade(CRUMB, 0.3), 2),
        _rect(x, y, w, 26, CRUMB, 2, 2),
    ]
    color = TOPPINGS.get(topping)
    if color is None:
        return out
    top = [(x + w * f + 6, y - 7 + (3 if i % 2 else -2)) for i, f in enumerate((0.1, 0.35, 0.6, 0.85))]
    if topping in ("caramel", "marble"):
        d = f"M{x + 4},{y - 5} " + " ".join(f"L{px:.1f},{py + (4 if i % 2 else -4):.1f}" for i, (px, py) in enumerate(top))
        out.append(_line(d, 5 if topping == "caramel" else 3, stroke=color))
        if topping == "caramel":
            out.append(_line(f"M{x + w * 0.3:.1f},{y} l0,10 M{x + w * 0.7:.1f},{y} l0,15", 4, stroke=color))
    elif topping == "sugar":
        out += [_ell(px + dx, py + 1, 1.6, 1.2, color, 0.4) for px, py in top for dx in (-5, 0, 5)]
    elif topping == "nuts":
        out += [_path(f"M{px - 6:.1f},{py + 3:.1f} l6,-8 l6,8 Z", color, 1.4) for px, py in top]
    elif topping == "white":
        out += [_rect(px - 5, py - 4, 10, 8, color, 1, 1.4) for px, py in top]
    elif topping == "toffee":
        out += [_path(f"M{px - 8:.1f},{py:.1f} q8,-9 16,0 q-8,9 -16,0 Z", color, 1.4) for px, py in top]
    else:  # berries and hazelnuts: round
        out += [_ell(px, py, 5, 4.4, color, 1.4) for px, py in top]
    return out


def brownie_mix(paint: str, fill: Fill, label: str | None, topping: str = "none", tray: str = "no") -> list[str]:
    """A carton of brownie mix: its name on a panel and a stack of brownies on the front."""
    out = [
        _path("M300,74 L328,56 L328,338 L300,356 Z", _shade(fill.base, 0.25)),
        _path("M74,74 L102,56 L328,56 L300,74 Z", _tint(fill.base, 0.25)),
        _path("M74,74 L300,74 L300,356 L74,356 Z", paint),
        *_panel(84, 92, 206, 92, label, 34),
        _ell(188, 332, 92, 13, "#ffffff", 2),
        *_brownie(116, 296, 64, topping),
        *_brownie(192, 296, 64, topping),
        *_brownie(154, 256, 64, topping),
    ]
    if tray == "yes":
        out += [
            _path("M220,306 L384,306 L368,360 L236,360 Z", FOIL),
            _path("M214,298 L390,298 L390,308 L214,308 Z", _tint(FOIL, 0.4), 2.4),
            *[_line(f"M{x},312 L{302 + (x - 302) * 0.83:.1f},356", 1.4) for x in range(242, 370, 20)],
        ]
    return out


def brownie_tin(
    paint: str,
    fill: Fill,
    label: str | None,
    outline: str = "square",
    base: str = "fixed",
    cells: str = "1",
    depth: str = "shallow",
    finish: str = "plain",
    lid: str = "no",
) -> list[str]:
    """A baking tin seen from above its front edge: the rim, the floor inside and the front wall."""
    wide = outline == "rectangular"
    half, back, front = (162, 142, 126) if wide else (124, 106, 144)
    wall = 62 if depth == "deep" else 34
    top, bottom = 194 - front / 2, 194 + front / 2  # the rim's back and front edges
    dark, floor = _shade(fill.base, 0.3), _shade(fill.base, 0.14)
    out: list[str] = []
    if lid == "yes":
        out += [
            _path(f"M{200 - back},{top - 10} L{200 - back + 8},{top - 92} L{200 + back - 8},{top - 92} L{200 + back},{top - 10} Z", _tint(fill.base, 0.35)),
            _rect(182, top - 70, 36, 14, _shade(fill.base, 0.2), 6, 2),
        ]
    out += [
        # the front wall below the rim, narrower at its foot
        _path(f"M{200 - half},{bottom} L{200 + half},{bottom} L{200 + half - 16},{bottom + wall} L{200 - half + 16},{bottom + wall} Z", dark),
        # the rim
        _path(f"M{200 - back},{top} L{200 + back},{top} L{200 + half},{bottom} L{200 - half},{bottom} Z", paint),
    ]
    # the walls inside, falling to the floor
    inset = 12
    ix0, ix1 = 200 - back + inset, 200 + back - inset
    jx0, jx1 = 200 - half + inset + 4, 200 + half - inset - 4
    iy0, iy1 = top + 8, bottom - 9
    out.append(_path(f"M{ix0},{iy0} L{ix1},{iy0} L{jx1},{iy1} L{jx0},{iy1} Z", dark, 2.4))
    drop = 24 if depth == "deep" else 14
    fx0, fx1 = ix0 + 8, ix1 - 8
    gx0, gx1 = jx0 + 12, jx1 - 12
    fy0, fy1 = iy0 + drop, iy1 - 5
    out.append(_path(f"M{fx0},{fy0} L{fx1},{fy0} L{gx1},{fy1} L{gx0},{fy1} Z", floor, 2))
    if base == "loose":
        out.append(_path(f"M{fx0 + 12},{fy0 + 8} L{fx1 - 12},{fy0 + 8} L{gx1 - 13},{fy1 - 8} L{gx0 + 13},{fy1 - 8} Z", _tint(floor, 0.25), 1.8))
        # the base's edge, lifted out below the tin
        y = bottom + wall + 22
        out.append(_path(f"M{200 - half + 18},{y} L{200 + half - 18},{y} L{200 + half - 26},{y + 12} L{200 - half + 26},{y + 12} Z", _tint(fill.base, 0.2), 2.4))
    if cells == "12":
        for i in range(1, 4):
            f = i / 4
            out.append(_line(f"M{fx0 + (fx1 - fx0) * f:.1f},{iy0} L{gx0 + (gx1 - gx0) * f:.1f},{iy1}", 4))
        for i in range(1, 3):
            f = i / 3
            y = fy0 + (fy1 - fy0) * f
            out.append(_line(f"M{fx0 + (gx0 - fx0) * f:.1f},{y:.1f} L{fx1 + (gx1 - fx1) * f:.1f},{y:.1f}", 4))
    if finish == "speckled":
        ink = _shade(fill.base, 0.55)
        out += [_ell(x, bottom + 8 + (x * 7) % (wall - 14), 2.2, 2.2, ink, 0.6)
                for x in range(int(200 - half + 24), int(200 + half - 20), 17)]  # fmt: skip
        out.append(_line(f"M{200 - half},{bottom} L{200 + half},{bottom}", LW_DETAIL + 3, stroke=_shade(fill.base, 0.7)))
    else:
        out.append(_highlight(f"M{200 - half + 30},{bottom + 12} L{200 - half + 120},{bottom + 12}", 5, 0.45))
    return _label(out, label)


SHAPES = {"brownie_mix": brownie_mix, "brownie_tin": brownie_tin}
register(SHAPES)
