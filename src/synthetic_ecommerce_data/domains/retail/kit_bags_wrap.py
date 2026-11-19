"""Household bags and wraps for the retail drawing kit (gen#962): trash bags, food bags, food wrap.

=================  ===========================================  ================================
shape              draws                                        params
=================  ===========================================  ================================
trash_bag          a full trash bag in the bag's color,         closure (drawstring, tie handle,
                   closed at its neck                           flap tie), use (bathroom,
                                                                kitchen, outdoor: the bag's size)
zip_bag            a clear food bag lying flat, its seal        closure (zip seal, slider, fold
                   along the top and what it holds inside       top), kind (freezer draws a
                                                                write-on panel and a snowflake,
                                                                sandwich a slice of bread, snack
                                                                crackers), bag_size (small,
                                                                medium, large)
wrap_box           a long box of food wrap with a sheet         material (aluminum foil, plastic
                   pulled out over its cutting edge             wrap, parchment paper, wax
                                                                paper), roll (regular, large,
                                                                jumbo: the box's length), grade
                                                                (extra wide draws a deeper box)
=================  ===========================================  ================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a bag's ``closure`` or a box's ``material`` draws what it states (gen#512). A trash
bag is painted in the SKU's color. A food bag is clear film over the paint, and a wrap box is
painted with a band and a sheet in the material's own color: both are sold without a color.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: A trash bag's half width and height by ``use``: a bathroom bin's bag is the smallest.
TRASH_SIZES = {"bathroom": (64, 150), "kitchen": (86, 196), "outdoor": (108, 236)}
#: A food bag's width and height by ``bag_size``.
BAG_SIZES = {"small": (150, 130), "medium": (200, 170), "large": (250, 210)}
#: A wrap box's length by ``roll``: a longer roll comes in a longer box.
ROLL_LENGTHS = {"regular": 220, "large": 262, "jumbo": 304}
#: Each wrap's own color: the sheet and the band on its box.
MATERIALS = {
    "aluminum foil": "#c4cad1",
    "plastic wrap": "#d9edf4",
    "parchment paper": "#e2c99a",
    "wax paper": "#f0e6c2",
}
#: The clear film of a food bag, and the bread and crackers seen through it.
FILM = "#eaf4f8"
BREAD = "#e2b877"
CRACKER = "#d9a55c"
#: The blue of a freezer bag's snowflake.
FROST = "#4f86b8"


def _trash_closure(cx: float, neck: float, paint: str, closure: str) -> list[str]:
    """The neck of a trash bag, closed as ``closure`` closes it."""
    if closure == "drawstring":
        cord = _tint(paint, 0.55)
        return [
            _rect(cx - 20, neck - 10, 40, 16, _shade(paint, 0.15), 5, LW_DETAIL),
            _path(
                f"M{cx - 8},{neck - 8} Q{cx - 46},{neck - 58} {cx - 6},{neck - 50} "
                f"Q{cx + 2},{neck - 30} {cx - 2},{neck - 8} Z",
                cord,
                LW_DETAIL,
            ),  # fmt: skip
            _path(
                f"M{cx + 8},{neck - 8} Q{cx + 46},{neck - 58} {cx + 6},{neck - 50} "
                f"Q{cx - 2},{neck - 30} {cx + 2},{neck - 8} Z",
                cord,
                LW_DETAIL,
            ),  # fmt: skip
        ]
    if closure == "tie handle":
        return [
            _path(
                f"M{cx - 10},{neck} L{cx - 52},{neck - 52} L{cx - 30},{neck - 60} "
                f"L{cx + 2},{neck - 14} Z",
                paint,
                LW_DETAIL,
            ),  # fmt: skip
            _path(
                f"M{cx + 10},{neck} L{cx + 52},{neck - 52} L{cx + 30},{neck - 60} "
                f"L{cx - 2},{neck - 14} Z",
                paint,
                LW_DETAIL,
            ),  # fmt: skip
            _ell(cx, neck - 12, 14, 10, _shade(paint, 0.2), LW_DETAIL),
        ]
    # flap tie: four narrow flaps knotted in pairs
    out = []
    for dx, tip in ((-34, -44), (-12, -56), (12, -56), (34, -44)):
        out.append(_path(f"M{cx + dx * 0.3 - 5},{neck} L{cx + dx},{neck + tip} "
                         f"L{cx + dx * 0.3 + 5},{neck - 4} Z", paint, LW_DETAIL))  # fmt: skip
    out.append(_ell(cx, neck - 6, 12, 8, _shade(paint, 0.2), LW_DETAIL))
    return out


def trash_bag(paint: str, fill: Fill, label: str | None, closure: str = "drawstring",
              use: str = "kitchen") -> list[str]:  # fmt: skip
    """A full trash bag in its color, standing, its neck closed by ``closure``."""
    half, height = TRASH_SIZES[use]
    cx, bottom = 200, 200 + height // 2 + 28
    neck = bottom - height
    out = [
        _path(
            f"M{cx - 18},{neck} C{cx - half - 24},{neck + height * 0.35} {cx - half},"
            f"{bottom - 12} {cx - half * 0.6},{bottom} Q{cx},{bottom + 12} {cx + half * 0.6},"
            f"{bottom} C{cx + half},{bottom - 12} {cx + half + 24},{neck + height * 0.35} "
            f"{cx + 18},{neck} Z",
            paint,
        ),  # fmt: skip
        _line(
            f"M{cx - 10},{neck + 14} Q{cx - half * 0.5},{neck + height * 0.5} "
            f"{cx - half * 0.4},{bottom - 16}",
            1.0,
        ),  # fmt: skip
        _line(
            f"M{cx + 8},{neck + 18} Q{cx + half * 0.3},{neck + height * 0.55} "
            f"{cx + half * 0.5},{bottom - 20}",
            1.0,
        ),  # fmt: skip
    ]
    out += _trash_closure(cx, neck, paint, closure)
    out.append(_highlight(f"M{cx - half * 0.7},{neck + height * 0.4} "
                          f"Q{cx - half * 0.8},{bottom - 40} {cx - half * 0.5},{bottom - 18}",
                          5, 0.45))  # fmt: skip
    return _label(out, label)


def _bag_kind(x0: float, y0: float, w: float, h: float, kind: str) -> list[str]:
    """What a food bag's ``kind`` shows: a freezer bag's write-on panel and snowflake, the slice
    of bread in a sandwich bag, the crackers in a snack bag."""
    cx, cy = x0 + w / 2, y0 + h / 2 + 12
    if kind == "freezer":
        out = [_rect(x0 + 14, y0 + 40, w * 0.45, h * 0.32, "#ffffff", 3, LW_DETAIL)]
        out += [_line(f"M{x0 + 22},{y0 + 54 + 12 * i} L{x0 + w * 0.45 + 6},{y0 + 54 + 12 * i}",
                      0.8) for i in range(int(h * 0.32 // 12) - 1)]  # fmt: skip
        sx, sy = x0 + w - 40, y0 + 64
        out += [_line(f"M{sx - 14},{sy} L{sx + 14},{sy} M{sx - 7},{sy - 12} L{sx + 7},{sy + 12} "
                      f"M{sx - 7},{sy + 12} L{sx + 7},{sy - 12}", 2.2, stroke=FROST)]  # fmt: skip
        return out
    if kind == "sandwich":
        r = min(w, h) * 0.3
        return [_path(f"M{cx - r},{cy + r} L{cx - r},{cy - r * 0.3} Q{cx - r},{cy - r * 1.1} "
                      f"{cx},{cy - r} Q{cx + r},{cy - r * 1.1} {cx + r},{cy - r * 0.3} "
                      f"L{cx + r},{cy + r} Z", BREAD, LW_DETAIL)]  # fmt: skip
    # snack: a few crackers
    return [_ell(cx + dx, cy + dy, 16, 16, CRACKER, LW_DETAIL)
            for dx, dy in ((-30, 10), (0, -8), (28, 12), (6, 26))]  # fmt: skip


def zip_bag(paint: str, fill: Fill, label: str | None, closure: str = "zip seal",
            kind: str = "sandwich", bag_size: str = "medium") -> list[str]:  # fmt: skip
    """A clear food bag lying flat: its seal along the top and what it holds inside."""
    w, h = BAG_SIZES[bag_size]
    x0, y0 = 200 - w / 2, 200 - h / 2 + 10
    out = [
        _rect(x0, y0, w, h, paint, 8),
        _rect(x0, y0, w, h, FILM, 8, 0),
    ]
    out += _bag_kind(x0, y0, w, h, kind)
    if closure == "fold top":
        out += [
            _path(
                f"M{x0},{y0} L{x0 + w},{y0} L{x0 + w},{y0 + 26} L{x0},{y0 + 26} Z",
                _shade(FILM, 0.08),
                LW_DETAIL,
            ),
            _line(f"M{x0},{y0 + 26} L{x0 + w},{y0 + 26}", 1.0, ' stroke-dasharray="6 3"'),
        ]
    else:
        out += [
            _line(f"M{x0 + 4},{y0 + 14} L{x0 + w - 4},{y0 + 14}", 1.6),
            _line(f"M{x0 + 4},{y0 + 20} L{x0 + w - 4},{y0 + 20}", 1.6),
        ]
        if closure == "slider":
            out.append(_rect(x0 + w - 34, y0 + 6, 22, 22, _shade(paint, 0.35), 3, LW_DETAIL))
    out.append(_highlight(f"M{x0 + 14},{y0 + 36} L{x0 + 14},{y0 + h - 14}", 5, 0.5))
    return _label(out, label)


def wrap_box(paint: str, fill: Fill, label: str | None, material: str = "aluminum foil",
             roll: str = "regular", grade: str = "everyday") -> list[str]:  # fmt: skip
    """A long box of food wrap seen from the front, a sheet of the wrap pulled over its edge."""
    length = ROLL_LENGTHS[roll]
    height = 76 if grade == "extra wide" else 56
    depth = 30
    sheet = MATERIALS[material]
    x0, y0 = 200 - length / 2 - depth / 2, 200 - height / 2 + depth / 2
    x1, y1 = x0 + length, y0 + height
    teeth = " ".join(f"L{x0 + 6 + 8 * i + 4},{y1 + (6 if i % 2 == 0 else 0)}"
                     for i in range(int((length - 12) // 8)))  # fmt: skip
    out = [
        _path(
            f"M{x0},{y0} L{x0 + depth},{y0 - depth} L{x1 + depth},{y0 - depth} L{x1},{y0} Z",
            _shade(fill.base, 0.12) if fill.pattern == "solid" else paint,
        ),
        _path(
            f"M{x1},{y0} L{x1 + depth},{y0 - depth} L{x1 + depth},{y1 - depth} L{x1},{y1} Z",
            _shade(fill.base, 0.28) if fill.pattern == "solid" else paint,
        ),
        _rect(x0, y0, length, height, paint, 2),
        _rect(x0 + 12, y0 + height * 0.3, length - 24, height * 0.4, sheet, 2, LW_DETAIL),
        _path(
            f"M{x0 + 6},{y1} L{x1 - 6},{y1} L{x1 - 22},{y1 + 70} L{x0 + 22},{y1 + 70} Z",
            sheet,
            LW_DETAIL,
        ),
        _line(f"M{x0 + 6},{y1} {teeth}", 1.0),
    ]
    if material == "aluminum foil":
        shine = ' stroke-opacity=".6"'
        out += [_line(f"M{x0 + 40 + 60 * i},{y1 + 12} L{x0 + 24 + 60 * i},{y1 + 60}", 2.0, shine,
                      "#ffffff") for i in range(int(length // 70))]  # fmt: skip
    elif material == "wax paper":
        out += [_line(f"M{x0 + 30},{y1 + 30 + 14 * i} L{x1 - 30},{y1 + 30 + 14 * i}", 0.8,
                      ' stroke-opacity=".4"') for i in range(3)]  # fmt: skip
    out.append(_highlight(f"M{x0 + 10},{y0 + 8} L{x1 - 10},{y0 + 8}", 4, 0.45))
    return _label(out, label)


SHAPES = {
    "trash_bag": trash_bag,
    "zip_bag": zip_bag,
    "wrap_box": wrap_box,
}
register(SHAPES)
