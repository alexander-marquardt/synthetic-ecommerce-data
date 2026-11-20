"""Hand tool, watering can and bird feeder shapes for the retail drawing kit (gen#961, slice 2).

Each type of the slice has its own flat drawing in the kit's house style (the outlines in the kit's
ink, the record's fill on the product's main surface), and each param is the lower-cased value of
the attribute it draws, so a derived style that swaps a value is drawn true (gen#512).

============  ==========================================  =====================================
shape         draws                                       params
============  ==========================================  =====================================
hand_tool     a painted handle with a grip, a ferrule     kind (trowel, hand fork, cultivator,
              and a metal head (or a pruner's two         transplanter, pruner), head (stainless
              handles and blades)                         steel, carbon steel, cast aluminum)
watering_can  a can with a handle, a spout and a rose     style (classic, long reach, indoor,
                                                          slimline), material (plastic,
                                                          galvanized steel, powder-coated steel)
bird_feeder   a feeder under a roof on a hanger, with     style (tube, window, suet cage,
              a perch                                     platform), material (metal, plastic,
                                                          wood)
============  ==========================================  =====================================

A decoy title that names a part's color ("with Red Grip") passes ``part`` and ``part_color``; the
parts each shape can name are :data:`PARTS`, added to :data:`kit_garden.PARTS`, which the Garden
decoys read. Every style draws every part, so a decoy may copy any style. A drawing never prints a
size: a style's capacities and packs share one image.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    PAPER,
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
    "hand_tool": ("grip", "ferrule", "hang-loop"),
    "watering_can": ("rose", "handle", "spout"),
    "bird_feeder": ("roof", "perch", "hanger"),
}
GARDEN_PARTS.update(PARTS)

#: head material -> the metal it is drawn in: none of the six main colors.
METAL = {"stainless steel": "#c9ced4", "carbon steel": "#5b6168", "cast aluminum": "#e2e5e8"}
HEAD_CLASS = "head"
MATERIAL_CLASS = "material"
CX = 200


def _head_marks(head: str, kind: str) -> str:
    """What tells one head metal from another, in a ``head`` group."""
    if head == "carbon steel":
        body = _line(f"M{CX - 6},150 L{CX + 6},120 M{CX - 4},176 L{CX + 6},160", 1.6, ' stroke-opacity=".6"', "#9aa0a6")
    elif head == "cast aluminum":
        dots = ((-14, 120), (10, 104), (-4, 150), (16, 140), (-18, 168))
        body = "".join(_ell(CX + dx, y, 2.5, 2.5, "#b9bec4", 1) for dx, y in dots)
    else:  # stainless steel: a polish that shines
        body = _highlight(f"M{CX - 18},{150 if kind != 'pruner' else 96} L{CX - 6},{80 if kind != 'pruner' else 60}", 6, 0.75)
    return f'<g class="{HEAD_CLASS}">{body}</g>'


def _head(kind: str, metal: str) -> list[str]:
    """The metal end of a digging or weeding tool, above the ferrule."""
    if kind == "hand fork":
        d = (f"M{CX - 8},192 L{CX - 8},150 L{CX - 40},140 L{CX - 40},50 L{CX - 28},50 L{CX - 28},128 "
             f"L{CX - 6},128 L{CX - 6},44 L{CX + 6},44 L{CX + 6},128 L{CX + 28},128 L{CX + 28},50 "
             f"L{CX + 40},50 L{CX + 40},140 L{CX + 8},150 L{CX + 8},192 Z")  # fmt: skip
    elif kind == "cultivator":
        d = (f"M{CX - 8},192 L{CX - 8},140 L{CX - 44},132 Q{CX - 70},96 {CX - 44},60 L{CX - 36},68 "
             f"Q{CX - 54},98 {CX - 34},120 L{CX - 6},120 L{CX - 6},56 Q{CX},40 {CX + 6},56 L{CX + 6},120 "
             f"L{CX + 34},120 Q{CX + 54},98 {CX + 36},68 L{CX + 44},60 Q{CX + 70},96 {CX + 44},132 "
             f"L{CX + 8},140 L{CX + 8},192 Z")  # fmt: skip
    elif kind == "transplanter":
        d = (f"M{CX - 8},192 L{CX - 8},172 Q{CX - 26},160 {CX - 26},120 L{CX - 20},40 Q{CX},24 {CX + 20},40 "
             f"L{CX + 26},120 Q{CX + 26},160 {CX + 8},172 L{CX + 8},192 Z")  # fmt: skip
        marks = "".join(f"M{CX - 14},{y} L{CX + 14},{y} " for y in (70, 96, 122, 148))
        return [_path(d, metal), _line(marks, 1.6)]
    else:  # trowel: a wide scoop
        d = (f"M{CX - 8},192 L{CX - 8},172 Q{CX - 52},150 {CX - 46},96 Q{CX - 30},50 {CX},34 "
             f"Q{CX + 30},50 {CX + 46},96 Q{CX + 52},150 {CX + 8},172 L{CX + 8},192 Z")  # fmt: skip
    return [_path(d, metal)]


def _pruner(paint: str, metal: str, pt: _Part, grip: str, ferrule: str, loop: str) -> list[str]:
    """A bypass pruner: two painted handles that meet at a pivot under a curved blade and a hook."""
    return [
        _path(f"M{CX - 4},140 Q{CX - 40},96 {CX - 14},40 Q{CX + 10},70 {CX + 10},132 Z", metal),
        _path(f"M{CX + 4},140 Q{CX + 30},110 {CX + 26},70 L{CX + 12},78 Q{CX + 14},112 {CX - 2},128 Z", _shade(metal, 0.2)),
        _path(f"M{CX - 10},150 L{CX - 18},140 L{CX - 70},318 L{CX - 46},324 Z", paint),
        _path(f"M{CX + 10},150 L{CX + 18},140 L{CX + 70},318 L{CX + 46},324 Z", paint),
        pt.mark("grip", _path(f"M{CX - 38},220 L{CX - 62},300 L{CX - 42},306 L{CX - 18},226 Z", grip)),
        pt.mark("grip", _path(f"M{CX + 38},220 L{CX + 62},300 L{CX + 42},306 L{CX + 18},226 Z", grip)),
        pt.mark("ferrule", _ell(CX, 144, 13, 13, ferrule)),
        pt.mark("hang-loop", _ell(CX - 62, 334, 12, 9, loop)),
        _ell(CX - 62, 334, 5, 3.5, PAPER, 1.6),
    ]


def hand_tool(paint: str, fill: Fill, label: str | None, kind: str = "trowel", head: str = "stainless steel",
              part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A garden hand tool standing on its handle: a ``trowel`` scoop, a three-tined ``hand fork``,
    a ``cultivator`` with three curved claws, a narrow ``transplanter`` with depth marks, or a
    bypass ``pruner`` on two handles; the ``head`` metal sets its color and its marks (a polish,
    forging lines, cast speckles)."""
    pt = _Part("hand_tool", part, part_color)
    kind, head = kind.lower(), head.lower()
    metal = METAL.get(head, METAL["stainless steel"])
    grip = pt.fill("grip", _tint(fill.base, 0.45))
    ferrule = pt.fill("ferrule", POLE)
    loop = pt.fill("hang-loop", GREASE)
    if kind == "pruner":
        out = _pruner(paint, metal, pt, grip, ferrule, loop)
    else:
        out = [
            *_head(kind, metal),
            pt.mark("hang-loop", _ell(CX, 330, 14, 10, loop)),
            _ell(CX, 330, 6, 4, PAPER, 1.6),
            _rect(CX - 20, 212, 40, 112, paint, 18),
            pt.mark("grip", _rect(CX - 24, 240, 48, 50, grip, 10)),
            pt.mark("ferrule", _rect(CX - 14, 190, 28, 26, ferrule, 4)),
        ]
    out.append(_head_marks(head, kind))
    return _label(out, label)


#: style -> (body x, body y, body width, body height, spout tip x, spout tip y, rose radius).
_CAN = {
    "classic": (110, 160, 170, 160, 360, 110, 22),
    "long reach": (90, 220, 170, 100, 384, 80, 16),
    "indoor": (140, 220, 110, 100, 350, 160, 8),
    "slimline": (150, 120, 100, 200, 350, 96, 18),
}


def _can_marks(material: str, x: float, y: float, w: float, h: float) -> str:
    """What tells one can material from another, in a ``material`` group."""
    if material == "galvanized steel":
        body = "".join(_line(f"M{x + 4},{y + h * f:.1f} L{x + w - 4},{y + h * f:.1f}", 2.4, stroke=POLE) for f in (0.2, 0.5, 0.8))
        body += "".join(_ell(x + 12, y + h * f, 3, 3, POLE, 1) for f in (0.12, 0.88))
    elif material == "powder-coated steel":
        body = _highlight(f"M{x + 16},{y + 18} L{x + 16},{y + h - 18}", 7, 0.5)
        body += _line(f"M{x - 4},{y} L{x + w + 4},{y}", 5)
    else:  # plastic: a molding seam down the side
        body = _line(f"M{x + w / 2:.1f},{y + 6} L{x + w / 2:.1f},{y + h - 6}", 1.4, ' stroke-opacity=".5"')
    return f'<g class="{MATERIAL_CLASS}">{body}</g>'


def watering_can(paint: str, fill: Fill, label: str | None, style: str = "classic", material: str = "plastic",
                 part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A watering can seen from the side: a ``classic`` round-shouldered can, a low ``long reach``
    can with a long spout, a small ``indoor`` can with a slim spout, or a tall ``slimline`` one;
    each has a top handle, a spout and a rose, and the ``material`` adds its marks (a seam, ribs
    and rivets, a sheen and a rolled rim)."""
    pt = _Part("watering_can", part, part_color)
    style, material = style.lower(), material.lower()
    x, y, w, h, tx, ty, rr = _CAN.get(style, _CAN["classic"])
    handle = pt.fill("handle", _shade(fill.base, 0.25))
    spout = pt.fill("spout", _shade(fill.base, 0.15))
    rose = pt.fill("rose", POLE)
    bx, by = x + w - 6, y + h - 24
    out = [
        _line("M20,338 L380,338", 4),
        pt.mark("spout", _path(f"M{bx},{by} L{tx - 6},{ty + 4} L{tx + 4},{ty + 14} L{bx},{by + 18} Z", spout)),
        pt.mark("handle", _path(f"M{x + 16},{y + 4} Q{x + w / 2:.1f},{y - 70} {x + w - 16},{y + 4} L{x + w - 30},{y + 4} Q{x + w / 2:.1f},{y - 46} {x + 30},{y + 4} Z", handle)),
        _rect(x, y, w, h, paint, 22),
        pt.mark("rose", _ell(tx + 2, ty + 8, rr * 0.5 + 4, rr + 2, rose)),
        _can_marks(material, x, y, w, h),
    ]
    return _label(out, label)


def _feeder_marks(material: str, x: float, y: float, w: float, h: float) -> str:
    """What tells one feeder material from another, in a ``material`` group."""
    if material == "wood":
        body = _line(f"M{x + 8},{y + h * 0.3:.1f} q{w / 4:.1f},6 {w / 2:.1f},0 t{w / 2 - 16:.1f},0 M{x + 8},{y + h * 0.7:.1f} q{w / 4:.1f},-6 {w / 2:.1f},0", 1.4, ' stroke-opacity=".5"')
    elif material == "metal":
        body = _highlight(f"M{x + 10},{y + 10} L{x + 10},{y + h - 10}", 5, 0.6)
    else:  # plastic: a clear window onto the seed
        body = _rect(x + w * 0.3, y + h * 0.2, w * 0.4, h * 0.5, _tint(PAPER, 0.2), 6, 1.6)
    return f'<g class="{MATERIAL_CLASS}">{body}</g>'


def bird_feeder(paint: str, fill: Fill, label: str | None, style: str = "tube", material: str = "metal",
                part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A bird feeder: a ``tube`` with feeding ports, a flat ``window`` feeder on suction cups, a
    wire ``suet cage``, or a ``platform`` tray on four cords; each has a roof, a perch and a hanger,
    and the ``material`` adds its marks (grain, a sheen, a clear window)."""
    pt = _Part("bird_feeder", part, part_color)
    style, material = style.lower(), material.lower()
    roof = pt.fill("roof", _shade(fill.base, 0.25))
    perch = pt.fill("perch", POLE)
    hanger = pt.fill("hanger", GREASE)
    if style == "window":
        x, y, w, h = 110.0, 130.0, 180.0, 170.0
        out = [
            pt.mark("hanger", _ell(x + 24, y + 24, 14, 14, hanger)),
            pt.mark("hanger", _ell(x + w - 24, y + 24, 14, 14, hanger)),
            _rect(x, y, w, h, paint, 10),
            pt.mark("roof", _path(f"M{x - 10},{y + 6} L{x + w + 10},{y + 6} L{x + w},{y - 22} L{x},{y - 22} Z", roof)),
            pt.mark("perch", _rect(x - 8, y + h - 16, w + 2 * 8, 12, perch, 6)),
        ]
    elif style == "suet cage":
        x, y, w, h = 130.0, 130.0, 140.0, 140.0
        grid = " ".join(f"M{x + i},{y} L{x + i},{y + h}" for i in range(20, int(w), 20))
        grid += " " + " ".join(f"M{x},{y + i} L{x + w},{y + i}" for i in range(20, int(h), 20))
        out = [
            pt.mark("hanger", _line(f"M{CX},{y - 30} L{CX},40", 5, stroke=hanger)),
            _rect(x, y, w, h, paint, 6),
            _line(grid, 2, stroke=_shade(fill.base, 0.4)),
            pt.mark("roof", _path(f"M{x - 16},{y + 2} L{CX},{y - 34} L{x + w + 2 * 8},{y + 2} Z", roof)),
            pt.mark("perch", _rect(x + 20, y + h + 6, w - 40, 12, perch, 6)),
        ]
    elif style == "platform":
        x, y, w, h = 90.0, 250.0, 220.0, 36.0
        out = [
            pt.mark("hanger", _line(f"M{CX},104 L{CX},40", 5, stroke=hanger)),
            _line(f"M{x + 10},{y} L{x + 30},138 M{x + w - 10},{y} L{x + w - 30},138", 2.4),
            pt.mark("roof", _path(f"M{x},{140} L{CX},{98} L{x + w},{140} Z", roof)),
            _rect(x, y, w, h, paint, 6),
            pt.mark("perch", _rect(x - 10, y - 12, w + 20, 12, perch, 6)),
        ]
    else:  # tube: a column with feeding ports
        x, y, w, h = 160.0, 100.0, 80.0, 200.0
        ports = "".join(_ell(CX, y + h * f, 10, 10, GREASE, 2) for f in (0.3, 0.7))
        out = [
            pt.mark("hanger", _line(f"M{CX},{y - 30} L{CX},40", 5, stroke=hanger)),
            _rect(x, y, w, h, paint, 10),
            ports,
            pt.mark("roof", _path(f"M{x - 14},{y + 4} Q{CX},{y - 50} {x + w + 14},{y + 4} Z", roof)),
            pt.mark("perch", _rect(x - 36, y + h * 0.3 + 12, w + 72, 8, perch, 4)),
            pt.mark("perch", _rect(x - 36, y + h * 0.7 + 12, w + 72, 8, perch, 4)),
        ]
    out.append(_feeder_marks(material, x, y, w, h))
    return _label(out, label)


SHAPES = {"hand_tool": hand_tool, "watering_can": watering_can, "bird_feeder": bird_feeder}
register(SHAPES)
