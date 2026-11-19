"""Sponges, cloths, dishwasher tablets and laundry pods for the retail drawing kit (gen#962).

=================  ===========================================  ================================
shape              draws                                        params
=================  ===========================================  ================================
sponge_cloth       a sponge block or a folded cloth in the      kind (scrub sponge: a dark green
                   SKU's color                                  scourer on top, non-scratch
                                                                sponge: a pale blue one,
                                                                cellulose sponge: its pores,
                                                                microfiber cloth: a fine weave,
                                                                dish cloth: a waffle grid and a
                                                                hanging loop)
tablet_box         a box of dishwasher tablets with one         formula (the tablet's layers and
                   tablet stood before it                       its ball), scent (the band on the
                                                                box), tablet_count (the box's
                                                                width)
pod_tub            a tub of laundry pods with one pod before    formula (deep clean: three
                   it                                           chambers, sensitive skin: one,
                                                                oxi boost: three and bubbles),
                                                                scent (the pod's liquid and the
                                                                tub's lid), loads (the tub's
                                                                height)
=================  ===========================================  ================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a sponge's ``kind`` or a box's ``formula`` draws what it states (gen#512). A sponge
or a cloth is painted in the SKU's color. A box of tablets and a tub of pods are sold without a
color: their own colors are the scent's and the formula's.
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

#: Each sponge or cloth ``kind``: the color of a sponge's scourer layer, or None for no layer.
SPONGE_KINDS = {
    "scrub sponge": "#2f6b3a",
    "non-scratch sponge": "#9cc3e0",
    "cellulose sponge": None,
    "microfiber cloth": None,
    "dish cloth": None,
}
#: Each ``scent``'s color: the band on a box of tablets, a pod's liquid and a tub's lid.
SCENTS = {"spring rain": "#6fa8d6", "clean breeze": "#7fc9a4", "unscented": "#d9d9d9"}
#: Each tablet ``formula``: the colors of its layers, top to bottom, and whether it has a ball.
TABLET_LAYERS = {
    "classic": (("#f4f4f4",), False),
    "all in one": (("#3f74c4", "#f4f4f4"), True),
    "max clean": (("#3f74c4", "#f4f4f4", "#4caf6e"), True),
    "quick wash": (("#f4f4f4", "#f2b134"), False),
}
#: The red ball pressed into a tablet's top.
BALL = "#d6403a"
#: A box's width by ``tablet_count``: a box of more tablets is wider.
BOX_WIDTHS = {"30 count": 150, "50 count": 190, "80 count": 230}
#: Each pod ``formula``: how many chambers its pod has, and whether bubbles rise from it.
POD_FORMULAS = {"deep clean": (3, False), "sensitive skin": (1, False), "oxi boost": (3, True)}
#: A tub's height by ``loads``: a tub of more pods is taller.
TUB_HEIGHTS = {"24 loads": 130, "42 loads": 160, "64 loads": 190}
#: The second and third chambers of a pod: a white and a deep blue swirl.
POD_SWIRLS = ("#ffffff", "#2d4f9e")


def _sponge(paint: str, layer: str | None, cellulose: bool) -> list[str]:
    """A sponge block in its color, seen a little from above, its scourer layer on top."""
    x0, y0, w, h, d = 110, 190, 180, 70, 30
    top = layer if layer else _tint(paint, 0.2)
    out = [
        _path(f"M{x0},{y0} L{x0 + d},{y0 - d} L{x0 + w + d},{y0 - d} L{x0 + w},{y0} Z", top),
        _path(f"M{x0 + w},{y0} L{x0 + w + d},{y0 - d} L{x0 + w + d},{y0 + h - d} "
              f"L{x0 + w},{y0 + h} Z", _shade(paint, 0.2)),  # fmt: skip
        _rect(x0, y0, w, h, paint, 3),
    ]
    if layer:
        out.append(_rect(x0, y0, w, 18, layer, 2, LW_DETAIL))
        out += [_ell(x0 + 30 + 34 * i, y0 - d / 2, 3, 2, _shade(layer, 0.3), 0.6)
                for i in range(5)]  # fmt: skip
    if cellulose:
        out += [_ell(x0 + 22 + 30 * (i % 6), y0 + 18 + 22 * (i // 6), 6 + (i % 3) * 2, 4,
                     _shade(paint, 0.3), 0.6) for i in range(12)]  # fmt: skip
    out.append(_highlight(f"M{x0 + 10},{y0 + h - 12} L{x0 + w - 20},{y0 + h - 12}", 4, 0.35))
    return out


def _cloth(paint: str, waffle: bool) -> list[str]:
    """A cloth folded in four, in its color: a microfiber cloth's fine weave, or a dish
    cloth's waffle grid and the loop it hangs by."""
    x0, y0, s = 120, 120, 170
    out = [
        _path(f"M{x0},{y0} L{x0 + s},{y0} L{x0 + s},{y0 + s} L{x0},{y0 + s} Z", paint),
        _path(f"M{x0 + s},{y0} L{x0 + s - 40},{y0 + 40} L{x0 + s},{y0 + 40} Z",
              _shade(paint, 0.18), LW_DETAIL),  # fmt: skip
    ]
    if waffle:
        out += [_line(f"M{x0 + 6},{y0 + 20 * i} L{x0 + s - 6},{y0 + 20 * i}", 0.8)
                for i in range(2, 9)]  # fmt: skip
        out += [_line(f"M{x0 + 20 * i},{y0 + 46} L{x0 + 20 * i},{y0 + s - 6}", 0.8)
                for i in range(1, 9)]  # fmt: skip
        out.append(_path(f"M{x0 + 10},{y0} Q{x0 + 22},{y0 - 34} {x0 + 34},{y0}", "none",
                         LW_DETAIL))  # fmt: skip
    else:
        out += [_line(f"M{x0 + 8},{y0 + 54 + 9 * i} L{x0 + s - 8},{y0 + 54 + 9 * i}", 0.5,
                      ' stroke-opacity=".5"') for i in range(12)]  # fmt: skip
    out.append(_highlight(f"M{x0 + 12},{y0 + 14} L{x0 + s - 52},{y0 + 14}", 4, 0.35))
    return out


def sponge_cloth(paint: str, fill: Fill, label: str | None,
                 kind: str = "scrub sponge") -> list[str]:  # fmt: skip
    """A sponge or a cloth in its color, drawn as ``kind`` is made."""
    if kind.endswith("cloth"):
        out = _cloth(paint, kind == "dish cloth")
    else:
        out = _sponge(paint, SPONGE_KINDS[kind], kind == "cellulose sponge")
    return _label(out, label)


def _tablet(cx: float, top: float, formula: str) -> list[str]:
    """One tablet standing, its layers top to bottom, and its ball when it has one."""
    layers, ball = TABLET_LAYERS[formula]
    w, h = 74, 54
    step = h / len(layers)
    out = [_rect(cx - w / 2, top + step * i, w, step, color, 3, LW_DETAIL)
           for i, color in enumerate(layers)]  # fmt: skip
    if ball:
        out.append(_ell(cx, top + step / 2, 12, 9, BALL, LW_DETAIL))
    if formula == "classic":
        out += [_ell(cx - 22 + 14 * i, top + 16 + 8 * (i % 2), 3, 3, "#3f74c4", 0.6)
                for i in range(4)]  # fmt: skip
    return out


def tablet_box(paint: str, fill: Fill, label: str | None, formula: str = "classic",
               scent: str = "spring rain",
               tablet_count: str = "50 count") -> list[str]:  # fmt: skip
    """A box of dishwasher tablets: a band in the scent's color, one tablet stood before it."""
    w, h = BOX_WIDTHS[tablet_count], 150
    x0, y0 = 200 - w / 2 - 30, 100
    band = SCENTS[scent]
    out = [
        _path(f"M{x0},{y0} L{x0 + 24},{y0 - 24} L{x0 + w + 24},{y0 - 24} L{x0 + w},{y0} Z",
              _shade(paint, 0.08)),  # fmt: skip
        _path(f"M{x0 + w},{y0} L{x0 + w + 24},{y0 - 24} L{x0 + w + 24},{y0 + h - 24} "
              f"L{x0 + w},{y0 + h} Z", _shade(paint, 0.2)),  # fmt: skip
        _rect(x0, y0, w, h, paint, 3),
        _rect(x0, y0 + 26, w, 34, band, 0, LW_DETAIL),
    ]
    out += _tablet(x0 + w / 2 + 70, y0 + h - 20, formula)
    out.append(_highlight(f"M{x0 + 10},{y0 + 10} L{x0 + w - 10},{y0 + 10}", 4, 0.4))
    return _label(out, label)


def _pod(cx: float, cy: float, formula: str, liquid: str) -> list[str]:
    """One pod: a soft pillow of its scent's liquid, split into its chambers."""
    chambers, bubbles = POD_FORMULAS[formula]
    out = [_ell(cx, cy, 44, 34, liquid, LW_DETAIL)]
    if chambers == 3:
        out += [
            _path(f"M{cx},{cy - 2} Q{cx - 26},{cy + 6} {cx - 30},{cy + 26} Q{cx - 4},{cy + 34} "
                  f"{cx},{cy - 2} Z", POD_SWIRLS[0], LW_DETAIL),  # fmt: skip
            _path(f"M{cx},{cy - 2} Q{cx + 26},{cy + 6} {cx + 30},{cy + 26} Q{cx + 4},{cy + 34} "
                  f"{cx},{cy - 2} Z", POD_SWIRLS[1], LW_DETAIL),  # fmt: skip
        ]
    out.append(_highlight(f"M{cx - 26},{cy - 16} Q{cx - 10},{cy - 28} {cx + 12},{cy - 24}",
                          4, 0.6))  # fmt: skip
    if bubbles:
        out += [_ell(cx + dx, cy - 44 - dy, r, r, "#ffffff", 0.8)
                for dx, dy, r in ((-18, 0, 6), (4, 12, 8), (24, 2, 5))]  # fmt: skip
    return out


def pod_tub(paint: str, fill: Fill, label: str | None, formula: str = "deep clean",
            scent: str = "spring rain", loads: str = "42 loads") -> list[str]:  # fmt: skip
    """A tub of laundry pods, its lid in the scent's color, one pod before it."""
    h = TUB_HEIGHTS[loads]
    liquid = SCENTS[scent]
    x0, bottom = 100, 300
    top = bottom - h
    out = [
        _path(f"M{x0},{top} L{x0 + 160},{top} L{x0 + 150},{bottom} L{x0 + 10},{bottom} Z",
              paint),  # fmt: skip
        _rect(x0 - 8, top - 26, 176, 30, liquid, 6),
        _rect(x0 + 30, top + h * 0.35, 100, h * 0.3, _tint(liquid, 0.5), 4, LW_DETAIL),
    ]
    out += _pod(x0 + 210, bottom - 34, formula, liquid)
    out.append(_highlight(f"M{x0 + 18},{top + 12} L{x0 + 24},{bottom - 14}", 5, 0.4))
    return _label(out, label)


SHAPES = {
    "sponge_cloth": sponge_cloth,
    "tablet_box": tablet_box,
    "pod_tub": pod_tub,
}
register(SHAPES)
