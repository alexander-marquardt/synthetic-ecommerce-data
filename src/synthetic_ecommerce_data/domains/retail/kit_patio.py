"""Planter, outdoor light and garden chair shapes for the retail drawing kit (gen#961, slice 1).

Each type of the slice has its own flat drawing in the kit's house style (the outlines in the kit's
ink, the record's fill on the product's main surface), and each param is the lower-cased value of
the attribute it draws, so a derived style that swaps a value is drawn true (gen#512).

=============  ============================================  ==================================
shape          draws                                         params
=============  ============================================  ==================================
planter        a pot on two feet with a rim and a band       form (round, square, tall,
                                                             trough), material (ceramic,
                                                             plastic, fiberglass, concrete,
                                                             galvanized steel)
outdoor_light  a lit head on a ground stake or a wall plate  style (lantern, bollard, globe,
                                                             bulkhead, cube), power_source
                                                             (solar, plug-in, hardwired,
                                                             battery),
                                                             mounting (ground stake, wall)
garden_chair   a seat, a back, armrests and legs             style (folding, stacking,
                                                             reclining, adirondack), material
                                                             (acacia, steel, aluminum, rattan,
                                                             plastic)
=============  ============================================  ==================================

A decoy title that names a part's color ("with Red Rim") passes ``part`` and ``part_color``; the
parts each shape can name are :data:`PARTS`, added to :data:`kit_garden.PARTS`, which the Garden
decoys read. A drawing never prints a size: a style's sizes and packs share one image.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_garden import GREASE, _Part
from synthetic_ecommerce_data.domains.retail.kit_garden import PARTS as GARDEN_PARTS
from synthetic_ecommerce_data.domains.retail.kit_sports import POLE, _ell, _label, _rect

#: shape -> the parts a decoy can name, the first being the one a short-title decoy draws in its color.
PARTS = {
    "planter": ("rim", "feet", "band"),
    "outdoor_light": ("cap", "frame", "base"),
    "garden_chair": ("legs", "armrests", "seat-pad"),
}
GARDEN_PARTS.update(PARTS)

#: The glow of a lit lamp: a pale cream that is none of the six main colors.
GLOW = "#fdf0c2"
#: A solar panel's cells.
CELL = "#33405a"
MATERIAL_CLASS = "material"
SOLAR_CLASS = "solar-panel"
CABLE_CLASS = "cable"
BATTERY_CLASS = "battery"

#: form -> (top left x, top right x, top y, bottom left x, bottom right x, bottom y) of the body.
_POT = {
    "round": (110, 290, 150, 140, 260, 318),
    "square": (118, 282, 140, 126, 274, 318),
    "tall": (142, 258, 84, 150, 250, 318),
    "trough": (48, 352, 206, 62, 338, 318),
}


def _at(top: float, bottom: float, y0: float, y1: float, y: float) -> float:
    return top + (bottom - top) * (y - y0) / (y1 - y0)


def _material_marks(material: str, box: tuple, fill: Fill) -> str:
    """What tells one planter material from another, in a ``material`` group."""
    tlx, trx, ty, blx, brx, by = box
    mid = (tlx + trx) / 2
    if material == "plastic":
        body = _line(f"M{tlx + 8},{ty + 14} L{trx - 8},{ty + 14}", 2.4)
    elif material == "fiberglass":
        body = _highlight(f"M{mid + 30},{ty + 20} L{mid + 22},{by - 20}", 8, 0.45)
    elif material == "concrete":
        dots = [(0.3, 0.3), (0.6, 0.25), (0.45, 0.55), (0.7, 0.7), (0.25, 0.75), (0.55, 0.85)]
        body = "".join(
            _ell(tlx + (trx - tlx) * fx, ty + (by - ty) * fy, 3, 3, _shade(fill.base, 0.35), 1)
            for fx, fy in dots
        )
    elif material == "galvanized steel":
        ys = [ty + (by - ty) * f for f in (0.2, 0.72, 0.88)]
        body = "".join(
            _line(f"M{_at(tlx, blx, ty, by, y):.1f},{y:.1f} L{_at(trx, brx, ty, by, y):.1f},{y:.1f}", 2.4)
            for y in ys
        )
        body += _line(f"M{tlx - 4},{ty + 24} q-22,6 -4,24 M{trx + 4},{ty + 24} q22,6 4,24", 4, stroke=POLE)
    else:  # ceramic: a glaze that shines
        body = _highlight(f"M{tlx + 22},{ty + 26} Q{tlx + 14},{(ty + by) / 2} {blx + 18},{by - 24}", 6, 0.6)
    return f'<g class="{MATERIAL_CLASS}">{body}</g>'


def planter(paint: str, fill: Fill, label: str | None, form: str = "round", material: str = "ceramic",
            part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A planter: a ``round`` tapered pot, a ``square`` box, a ``tall`` square pot or a long
    low ``trough``, with a rim, a band and two feet; the ``material`` adds its own marks (a glaze,
    a rolled lip, a gloss stripe, speckles, ribs and handles)."""
    pt = _Part("planter", part, part_color)
    box = _POT.get(form.lower(), _POT["round"])
    tlx, trx, ty, blx, brx, by = box
    y0, y1 = ty + (by - ty) * 0.42, ty + (by - ty) * 0.54
    band = (
        f"M{_at(tlx, blx, ty, by, y0):.1f},{y0:.1f} L{_at(trx, brx, ty, by, y0):.1f},{y0:.1f} "
        f"L{_at(trx, brx, ty, by, y1):.1f},{y1:.1f} L{_at(tlx, blx, ty, by, y1):.1f},{y1:.1f} Z"
    )
    feet = pt.fill("feet", GREASE)
    out = [
        _line("M20,338 L380,338", 4),
        pt.mark("feet", _rect(blx + 10, by - 2, 28, 18, feet, 3)),
        pt.mark("feet", _rect(brx - 38, by - 2, 28, 18, feet, 3)),
        _path(f"M{tlx},{ty} L{trx},{ty} L{brx},{by} L{blx},{by} Z", paint),
        pt.mark("band", _path(band, pt.fill("band", _tint(fill.base, 0.35)), 2)),
        pt.mark("rim", _rect(tlx - 10, ty - 20, trx - tlx + 20, 22, pt.fill("rim", _shade(fill.base, 0.2)), 4)),
        _material_marks(material.lower(), box, fill),
    ]
    return _label(out, label)


def _power(power: str, x: float, top: float, base: float) -> str:
    """The light's power source: a solar panel on its cap, a cable to a plug, or a battery box."""
    if power == "solar":
        cells = _line(f"M{x - 22},{top - 12} L{x + 22},{top - 12} M{x},{top - 20} L{x},{top - 4}", 1.2, stroke="#9fb0c8")
        return f'<g class="{SOLAR_CLASS}">{_rect(x - 30, top - 22, 60, 20, CELL, 2)}{cells}</g>'
    if power == "hardwired":
        return f'<g class="{CABLE_CLASS}">{_line(f"M{x - 40},{base - 40} Q{x - 90},{base - 10} 86,{base + 10}", 3, stroke=INK)}</g>'
    if power == "plug-in":
        return (
            f'<g class="{CABLE_CLASS}">{_line(f"M{x},{base} Q{x + 60},{base + 30} {x + 120},{base + 4}", 3, stroke=INK)}'
            f"{_rect(x + 116, base - 8, 26, 18, POLE, 3)}</g>"
        )
    return f'<g class="{BATTERY_CLASS}">{_rect(x + 34, base - 70, 26, 40, GREASE, 4)}{_line(f"M{x + 41},{base - 62} L{x + 53},{base - 62}", 2, stroke="#ffffff")}</g>'


def _head(style: str, x: float, top: float, paint: str, fill: Fill, pt: _Part) -> tuple[list[str], float]:
    """The lamp head from ``top`` down: its body, its glow, its frame and its cap; returns the
    elements and the y of its foot."""
    frame = pt.fill("frame", _shade(fill.base, 0.3))
    cap = pt.fill("cap", _shade(fill.base, 0.25))
    if style == "bollard":
        foot = top + 200
        return [
            _rect(x - 34, top, 68, 200, paint, 8),
            _rect(x - 28, top + 18, 56, 42, GLOW, 4),
            pt.mark("frame", _line(f"M{x - 12},{top + 18} L{x - 12},{top + 60} M{x + 12},{top + 18} L{x + 12},{top + 60}", 4, stroke=frame)),
            pt.mark("cap", _rect(x - 40, top - 10, 80, 16, cap, 4)),
        ], foot
    if style == "globe":
        foot = top + 120
        return [
            _rect(x - 10, top + 80, 20, 40, paint, 3),
            _ell(x, top + 44, 44, 44, GLOW),
            pt.mark("frame", _path(f"M{x - 30},{top + 76} L{x + 30},{top + 76} L{x + 22},{top + 90} L{x - 22},{top + 90} Z", frame, 2)),
            pt.mark("cap", _ell(x, top + 2, 16, 8, cap)),
        ], foot
    if style == "bulkhead":
        foot = top + 110
        return [
            _ell(x, top + 55, 70, 50, paint),
            _ell(x, top + 55, 50, 32, GLOW, 2),
            pt.mark("frame", _line(f"M{x - 46},{top + 45} L{x + 46},{top + 45} M{x - 48},{top + 65} L{x + 48},{top + 65}", 4, stroke=frame)),
            pt.mark("cap", _rect(x - 40, top - 2, 80, 12, cap, 4)),
        ], foot
    if style == "cube":
        foot = top + 110
        return [
            _rect(x - 50, top, 100, 110, paint, 4),
            _rect(x - 8, top - 30, 16, 30, GLOW, 2),
            _rect(x - 8, top + 110, 16, 30, GLOW, 2),
            pt.mark("frame", _rect(x - 38, top + 12, 76, 86, frame, 3)),
            pt.mark("cap", _rect(x - 56, top - 6, 112, 12, cap, 3)),
        ], foot
    foot = top + 130  # lantern: a glazed cage under a pitched roof
    return [
        _rect(x - 40, top + 20, 80, 100, paint, 4),
        _rect(x - 28, top + 32, 56, 76, GLOW, 3),
        pt.mark("frame", _line(f"M{x},{top + 32} L{x},{top + 108} M{x - 28},{top + 70} L{x + 28},{top + 70}", 4, stroke=frame)),
        _rect(x - 30, top + 120, 60, 10, paint, 3),
        pt.mark("cap", _path(f"M{x - 50},{top + 22} L{x},{top - 14} L{x + 50},{top + 22} Z", cap)),
    ], foot


def outdoor_light(paint: str, fill: Fill, label: str | None, style: str = "lantern",
                  power_source: str = "solar", mounting: str = "ground stake",
                  part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """An outdoor light: a ``lantern``, ``bollard``, ``globe``, ``bulkhead`` or ``cube`` head on a
    ground stake or a wall plate (``mounting``), fed by its ``power_source``: a solar panel on
    the cap, a cable to a plug, a cable into the wall, or a battery box."""
    pt = _Part("outdoor_light", part, part_color)
    style, power = style.lower(), power_source.lower()
    base = pt.fill("base", POLE)
    x = 210.0
    wall = mounting.lower() == "wall"
    top = 90.0 if wall else 110.0
    if style == "bollard":
        top = 120.0
    head, foot = _head(style, x, top, paint, fill, pt)
    if wall:
        out = [
            pt.mark("base", _rect(52, 60, 34, 250, base, 4)),
            _line(f"M86,{top + 50} L{x - 40},{top + 50}", 8, stroke=POLE),
            *head,
        ]
        anchor = foot
    else:
        out = [
            _line("M20,338 L380,338", 4),
            pt.mark("base", _path(f"M{x - 8},{foot} L{x + 8},{foot} L{x},{338} Z", base, 2)),
            *head,
        ]
        anchor = 330.0
    out.append(_power(power, x, top - 14 if style not in ("globe", "cube") else top - 40, anchor))
    return _label(out, label)


def _material_chair(material: str, seat: tuple[float, float, float, float], back: str) -> str:
    """What tells one chair material from another, in a ``material`` group."""
    x, y, w, h = seat
    if material == "steel":
        body = _line(f"M{x + 6},{y + h / 2} L{x + w - 6},{y + h / 2}", 2.4, stroke=POLE)
    elif material == "aluminum":
        body = _highlight(f"M{x + 10},{y + 4} L{x + w - 10},{y + 4}", 4, 0.7)
    elif material == "rattan":
        weave = " ".join(f"M{x + i},{y} l12,{h}" for i in range(6, int(w) - 6, 14))
        body = _line(weave, 1.4, ' stroke-opacity=".5"') + _line(back, 1.4, ' stroke-opacity=".5"')
    elif material == "plastic":
        body = _highlight(f"M{x + 14},{y + h - 4} Q{x + w / 2},{y + h + 6} {x + w - 14},{y + h - 4}", 4, 0.6)
    else:  # acacia: wood grain on the seat
        body = _line(f"M{x + 8},{y + 5} q{w / 4},4 {w / 2},0 t{w / 2 - 16},0", 1.4, ' stroke-opacity=".5"')
    return f'<g class="{MATERIAL_CLASS}">{body}</g>'


def garden_chair(paint: str, fill: Fill, label: str | None, style: str = "folding", material: str = "acacia",
                 part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A garden chair seen from the side and a little in front: a ``folding`` chair on crossed
    legs, a ``stacking`` one on four straight legs, a ``reclining`` one with a raked back and a
    footrest, or an ``adirondack`` with a fan of back slats; each has armrests and a seat pad, and
    the ``material`` adds its marks (grain, a tube, a sheen, a weave, a moulded lip)."""
    pt = _Part("garden_chair", part, part_color)
    style = style.lower()
    legs = pt.fill("legs", GREASE)
    arm = pt.fill("armrests", _shade(fill.base, 0.25))
    pad = pt.fill("seat-pad", _tint(fill.base, 0.55))
    seat = (120.0, 214.0, 170.0, 20.0)
    if style == "reclining":
        back = "M120,214 L72,96 L104,88 L148,214 Z"
        leg_d = "M130,234 L118,334 M280,234 L300,334 M290,224 L360,250"
    elif style == "adirondack":
        seat = (110.0, 236.0, 190.0, 20.0)
        back = "M114,236 L90,96 L126,80 L170,76 L206,86 L218,236 Z"
        leg_d = "M124,256 L124,334 M286,256 L296,334"
    elif style == "stacking":
        back = "M128,214 L122,90 L272,90 L262,214 Z"
        leg_d = "M130,234 L124,334 M160,234 L156,334 M250,234 L254,334 M280,234 L286,334"
    else:  # folding: crossed legs
        back = "M130,214 L126,96 L270,96 L262,214 Z"
        leg_d = "M130,234 L280,334 M280,234 L130,334"
    x, y, w, h = seat
    out = [
        _line("M20,338 L380,338", 4),
        pt.mark("legs", _line(leg_d, 8, stroke=legs)),
        _path(back, paint),
        _rect(x, y, w, h, paint, 5),
        pt.mark("seat-pad", _rect(x + 8, y - 12, w - 16, 12, pad, 5)),
        pt.mark("armrests", _rect(x - 6, y - 64, w + 12, 12, arm, 5)),
        _line(f"M{x + 8},{y - 52} L{x + 8},{y} M{x + w - 8},{y - 52} L{x + w - 8},{y}", 5, stroke=POLE),
        _material_chair(material.lower(), seat, back),
    ]
    if style == "adirondack":
        out.append(_line("M138,90 L152,234 M170,78 L172,234 M196,84 L192,234", 1.6, ' stroke-opacity=".5"'))
    return _label(out, label)


SHAPES = {"planter": planter, "outdoor_light": outdoor_light, "garden_chair": garden_chair}
register(SHAPES)
