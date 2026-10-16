"""Garden machine and barbecue shapes for the retail drawing kit (gen#203).

Each type of :mod:`garden_rows` has its own flat drawing in the kit's house style: outlines in the
kit's ink, the record's fill (color and pattern) on the product's main surface.

==============  ==========================================  ==========================
shape           draws                                       params
==============  ==========================================  ==========================
lawn_mower      a deck on four wheels with a grass bag      power (cordless, petrol,
                and a push handle                           electric), drive (push,
                                                            self)
robot_mower     a low domed body on two wheels              boundary (wire, gps)
grass_trimmer   a long shaft with a cutting head at the     head (line, blade), power
                foot and a handle at the top                (cordless, petrol, electric)
bbq             a charcoal kettle, barrel, kamado egg or    kind (kettle, barrel,
                portable bowl, or a gas cabinet with a      kamado, portable, gas),
                knob per burner (one ``class="knob"``       burners
                each)
garden_hose     a coiled hose of three loops with a brass   style (coiled,
                connector, or an expandable one laid in     expandable)
                an S with a connector at each end
==============  ==========================================  ==========================

A decoy's title may name a part in a color the product lacks ("Red Wheels", "White Shelves"): its
row passes ``part`` (one of :data:`PARTS`) and ``part_color`` (a main color), and the shape draws
that part, and only that part, in the color, marking each element ``data-part="<part>"``
(:class:`_Part`). ``tests/test_retail_garden_203.py`` reads the rendered drawing for it.

A drawing never prints a width, an area or a diameter: a style's SKUs share one image per
colorway. Every param is a string with a default, so each shape also draws bare. The mower's power
source is drawn as what feeds it (a battery pack, a fuel cap and pull cord, or a cable), which
``tests/test_retail_garden_203.py`` counts against the record.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, Fill, _highlight, _line, _panel, _path, _shade, _tint, register
from kit_sports import POLE, _ell, _label, _rect

#: The knob classes a drawing marks: one group each, so a test counts them against the record.
KNOB_CLASS = "knob"
SHELF_CLASS = "shelf"
SIDE_BURNER_CLASS = "side-burner"
DRIVE_LEVER_CLASS = "drive-lever"
DRIVE_ARROW_CLASS = "drive-arrow"
BATTERY_CLASS = "battery"
FUEL_CLASS = "fuel-cap"
CABLE_CLASS = "cable"
GREASE = "#4a4f57"

#: The swatch of each main color: the rows' own (:mod:`garden_rows`) and a named part's.
ACCENT_HEX = {
    "red": "#c8312e",
    "blue": "#3f6fb5",
    "green": "#4f8a3a",
    "yellow": "#f2c230",
    "black": "#2d2d33",
    "white": "#f4f1ea",
}
#: shape -> the parts a decoy can name, the first being the one a short-title decoy draws in its color.
PARTS = {
    "lawn_mower": ("handle", "wheels", "grass-box"),
    "robot_mower": ("bumper", "wheels", "button"),
    "grass_trimmer": ("handle", "shaft", "engine"),
    "bbq": ("legs", "lid-handle", "shelves"),
    "garden_hose": ("connectors",),
}


class _Part:
    """The part a decoy names, drawn in the named color: ``fill`` gives the color to that part's
    element (or its own default), ``mark`` tags it ``data-part``. With no part, neither changes
    anything, so a bare drawing is the product's own."""

    def __init__(self, shape: str, part: str, color: str) -> None:
        self.part = part.lower()
        if self.part and self.part not in PARTS[shape]:
            raise ValueError(f"{shape!r} shows no part named {part!r}; it shows {PARTS[shape]}")
        self.hex = ACCENT_HEX[color.lower()] if self.part else ""

    def fill(self, name: str, default: str) -> str:
        return self.hex if self.part == name else default

    def mark(self, name: str, el: str) -> str:
        return el.replace("/>", f' data-part="{name}"/>', 1) if self.part == name else el


def _wheel(cx: float, cy: float, r: float, pt: _Part) -> str:
    return pt.mark("wheels", _ell(cx, cy, r, r, pt.fill("wheels", GREASE))) + _ell(cx, cy, r * 0.4, r * 0.4, POLE, 1.6)


def lawn_mower(paint: str, fill: Fill, label: str | None, power: str = "cordless", drive: str = "push",
               part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A lawn mower: a deck, a grass bag and a push handle. ``power`` adds a battery pack
    (cordless), a fuel cap with a pull cord (petrol) or a trailing cable (electric); ``self``
    drive adds a drive lever on the handle and a drive arrow on the deck."""
    power, drive = power.lower(), drive.lower()
    pt = _Part("lawn_mower", part, part_color)
    bag = pt.fill("grass-box", _tint(fill.base, 0.5))
    out = [
        _line("M20,334 L380,334", 4),
        pt.mark("grass-box", _path("M300,232 L384,232 L384,298 L300,298 Z", bag)),
        _line("M318,236 L318,296 M342,236 L342,296 M366,236 L366,296", 1.6, ' stroke-opacity=".4"'),
        _line("M296,230 L352,96 L384,106", 6),
        pt.mark("handle", _line("M296,230 L352,96 L384,106", 3, stroke=pt.fill("handle", POLE))),
        _path("M64,296 Q64,236 128,230 L282,230 Q338,236 338,296 Z", paint),
        _highlight("M92,254 Q104,240 140,238", 4, 0.5),
        _wheel(112, 306, 26, pt),
        _wheel(284, 302, 36 if drive == "self" else 28, pt),
    ]
    if drive == "self":
        out += [
            f'<g class="{DRIVE_LEVER_CLASS}">{_line("M340,106 L356,156", 5, stroke=POLE)}</g>',
            f'<g class="{DRIVE_ARROW_CLASS}">{_line("M92,276 L132,276 M122,266 L132,276 L122,286", 3)}</g>',
        ]
    if power == "cordless":
        out += [
            f'<g class="{BATTERY_CLASS}">{_rect(150, 190, 76, 44, _shade(fill.base, 0.35), 6)}'
            f'{_line("M164,204 L212,204", 2.4, stroke="#ffffff")}{_line("M164,218 L196,218", 2.4, stroke="#ffffff")}</g>'
        ]
    elif power == "petrol":
        out += [
            _rect(140, 196, 84, 36, _shade(fill.base, 0.35), 6),
            f'<g class="{FUEL_CLASS}">{_ell(184, 188, 14, 8, POLE, 2.4)}</g>',
            _line("M224,214 L252,214 Q262,214 262,224 L262,246", 3),
        ]
    else:
        out += [
            _rect(160, 206, 56, 24, _shade(fill.base, 0.3), 6),
            f'<g class="{CABLE_CLASS}">{_line("M384,106 Q398,200 372,318 Q330,350 250,350 Q150,350 120,342", 3.4, stroke="#e07a1f")}</g>',
        ]
    return _label(out, label)


def robot_mower(paint: str, fill: Fill, label: str | None, boundary: str = "wire",
                part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A robot mower: a low dome on two wheels with a stop button. ``wire`` shows the boundary
    wire pegged out in the grass in front of it; ``gps`` puts a satellite dome on its back."""
    pt = _Part("robot_mower", part, part_color)
    dark = _shade(fill.base, 0.35)
    out = [_line("M20,334 L380,334", 4)]
    if boundary.lower() == "gps":
        out += [_ell(200, 150, 26, 18, POLE, 2.4), _line("M200,132 L200,112 M186,136 L170,122 M214,136 L230,122", 2.4)]
    else:
        out += [_line("M20,352 L380,352", 3.2, ' stroke-dasharray="10 8"', stroke="#e07a1f")]
    out += [
        _path("M56,312 Q52,196 200,182 Q348,196 344,312 Z", paint),
        pt.mark("bumper", _path("M56,312 L344,312 L344,326 Q200,338 56,326 Z", pt.fill("bumper", dark), 2.4)),
        pt.mark("button", _rect(170, 214, 60, 22, pt.fill("button", dark), 8, 2.4)),
        _line("M176,248 L224,248", 3, ' stroke-opacity=".5"'),
        _wheel(96, 322, 22, pt),
        _wheel(304, 322, 22, pt),
        _highlight("M84,262 Q104,214 160,200", 4, 0.5),
    ]
    return _label(out, label)


def grass_trimmer(paint: str, fill: Fill, label: str | None, head: str = "line", power: str = "cordless",
                  part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A grass trimmer: a long shaft from a cutting head to a handle. ``head`` draws a nylon-line
    spool with two whiskers (line) or a toothed blade under a guard (blade); ``power`` puts a
    battery pack (cordless), an engine with a fuel cap (petrol) or a cable (electric) at the top."""
    head, power = head.lower(), power.lower()
    pt = _Part("grass_trimmer", part, part_color)
    dark = _shade(fill.base, 0.35)
    out = [_line("M96,330 L296,92", 9), pt.mark("shaft", _line("M96,330 L296,92", 5, stroke=pt.fill("shaft", POLE)))]
    if head == "blade":
        out += [
            _path("M40,332 L100,310 L156,324 L150,350 L60,356 Z", GREASE, 2.4),
            _path("M44,346 L68,338 L80,350 L104,338 L120,352 L146,344 L146,356 L44,358 Z", POLE, 2),
        ]
    else:
        out += [
            _ell(100, 336, 34, 16, paint),
            _ell(100, 336, 12, 6, dark, 2),
            _line("M66,336 L24,330 M134,336 L176,346", 2.2),
        ]
    out += [
        pt.mark("handle", _path("M262,132 Q320,112 340,70 Q348,52 330,50 L300,60 Q300,86 262,104 Z", pt.fill("handle", paint))),
        _line("M232,160 L270,184", 7),
        _line("M232,160 L270,184", 3.4, stroke=POLE),
    ]
    if power == "cordless":
        out += [f'<g class="{BATTERY_CLASS}">{_rect(264, 46, 70, 40, dark, 6)}{_line("M276,66 L322,66", 2.4, stroke="#ffffff")}</g>']
    elif power == "petrol":
        out += [
            pt.mark("engine", _rect(256, 52, 76, 36, pt.fill("engine", dark), 8)),
            f'<g class="{FUEL_CLASS}">{_ell(294, 46, 12, 7, POLE, 2.4)}</g>',
        ]
    else:
        out += [f'<g class="{CABLE_CLASS}">{_line("M340,70 Q380,120 360,230 Q340,330 280,350", 3.4, stroke="#e07a1f")}</g>']
    return _label(out, label)


def _legs(*xs: float, pt: _Part, top: float = 272, bottom: float = 340) -> str:
    d = " ".join(f"M{x:g},{top:g} L{x + (x - 200) * 0.12:g},{bottom:g}" for x in xs)
    return pt.mark("legs", _line(d, 6, stroke=pt.fill("legs", INK)))


def _knobs(count: int, y: float, x0: float, x1: float) -> list[str]:
    gap = (x1 - x0) / max(count - 1, 1)
    return [f'<g class="{KNOB_CLASS}">{_ell(x0 + i * gap, y, 9, 9, GREASE, 2.4)}</g>' for i in range(count)]


def bbq(paint: str, fill: Fill, label: str | None, kind: str = "kettle", burners: str = "3",
        side_burner: str = "no", part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A barbecue. ``kettle`` is a dome on a bowl and three legs, ``barrel`` a horizontal drum on a
    stand with a chimney, ``kamado`` an egg on a cradle, ``portable`` a low bowl on short legs with a
    carry handle, and ``gas`` a cabinet under a hood with side shelves and one knob per burner, and a
    hob on the right shelf when ``side_burner`` is ``yes``."""
    kind = kind.lower()
    side_burner = side_burner.lower() == "yes"
    pt = _Part("bbq", part, part_color)
    dark = _shade(fill.base, 0.35)
    out = [_line("M20,346 L380,346", 4)]
    if kind == "barrel":
        out += [
            pt.mark("legs", _line("M120,262 L96,346 M280,262 L304,346", 6, stroke=pt.fill("legs", INK))),
            _path("M70,150 L330,150 Q352,150 352,206 Q352,262 330,262 L70,262 Q48,262 48,206 Q48,150 70,150 Z", paint),
            _line("M70,150 L70,262 M330,150 L330,262", 2.4, ' stroke-opacity=".5"'),
            _path("M96,150 L96,110 L128,110 L128,150", dark, 2.4),
            _line("M140,164 L260,164", 6, stroke=POLE),
            _path("M352,196 L384,196 L384,246 L352,246", dark, 2.4),
            _ell(96, 346, 14, 14, GREASE, 2.4),
        ]
    elif kind == "kamado":
        out += [
            _path("M200,40 Q310,40 322,170 Q326,290 200,300 Q74,290 78,170 Q90,40 200,40 Z", paint),
            _line("M92,150 Q200,170 308,150", 7, stroke=POLE),
            _path("M176,40 L176,20 L224,20 L224,40", dark, 2.4),
            _path("M96,296 L96,340 L304,340 L304,296", dark, 2.4),
            _line("M322,170 L350,170 L350,190", 5, stroke=POLE),
            _highlight("M112,92 Q130,60 170,52", 4, 0.5),
        ]
    elif kind == "portable":
        out += [
            _path("M80,226 Q80,160 200,160 Q320,160 320,226 Z", paint),
            _path("M70,226 L330,226 Q320,276 200,282 Q80,276 70,226 Z", dark),
            pt.mark("legs", _line("M100,282 L72,346 M300,282 L328,346", 6, stroke=pt.fill("legs", INK))),
            _line("M120,176 Q200,126 280,176", 6, stroke=POLE),
            _line("M320,214 L368,214", 6, stroke=POLE),
        ]
    elif kind == "gas":
        try:
            count = max(1, min(int(burners), 6))
        except ValueError:
            count = 3
        out += [
            _legs(110, 290, pt=pt, top=276),
            _ell(110, 346, 12, 12, GREASE, 2.4),
            _ell(290, 346, 12, 12, GREASE, 2.4),
            _path("M96,150 Q96,98 200,98 Q304,98 304,150 L304,168 L96,168 Z", paint),
            _line("M170,120 L230,120", 6, stroke=POLE),
            _path("M92,168 L308,168 L308,276 L92,276 Z", dark),
            f'<g class="{SHELF_CLASS}">{pt.mark("shelves", _path("M30,184 L92,184 L92,198 L30,198 Z", pt.fill("shelves", paint), 2.4))}</g>',
            f'<g class="{SHELF_CLASS}">{pt.mark("shelves", _path("M308,184 L370,184 L370,198 L308,198 Z", pt.fill("shelves", paint), 2.4))}</g>',
            *_knobs(count, 188, 136, 264),
            *([f'<g class="{SIDE_BURNER_CLASS}">{_ell(339, 176, 22, 7, GREASE, 2.4)}</g>'] if side_burner else []),
            _line("M100,218 L300,218 M100,246 L300,246", 1.6, ' stroke-opacity=".4"'),
        ]
    else:
        out += [
            pt.mark("legs", _line("M150,240 L120,346 M250,240 L280,346 M200,250 L200,346", 6, stroke=pt.fill("legs", INK))),
            _path("M70,208 Q70,262 200,266 Q330,262 330,208 Z", dark),
            _path("M80,208 Q80,96 200,96 Q320,96 320,208 Z", paint),
            pt.mark("lid-handle", _ell(200, 84, 10, 10, pt.fill("lid-handle", POLE), 2.4)),
            _line("M150,150 L150,150 M200,140 L200,140 M250,150 L250,150", 7),
            _highlight("M100,170 Q104,124 150,106", 4, 0.5),
        ]
    return _label(out, label)


BRASS = "#c9a24a"
#: The three loops of a coiled hose, as (x radius, y radius); the widest is drawn first.
COIL_LOOPS = ((128, 92), (98, 68), (68, 44))


def _tube(d: str, paint: str, width: float) -> str:
    """One run of hose: an ink stroke, then the style's color narrower on top."""
    ink = _line(d, width + 5, stroke=INK)
    return ink + _line(d, width, stroke=paint)


def _fitting(x: float, y: float, w: float, h: float, pt: _Part) -> str:
    """A connector, brass unless a decoy names its color: a block with a ridge, centered on
    ``x, y``, marked ``data-part="connectors"`` when it is the named part."""
    block = (
        f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" '
        f'fill="{pt.fill("connectors", BRASS)}" stroke="{INK}" stroke-width="2.4"/>'
    )
    return (
        pt.mark("connectors", block)
        + _line(f"M{x:.1f},{y - h / 2:.1f} L{x:.1f},{y + h / 2:.1f}", 2, ' stroke-opacity=".6"')
    )


def _ellipse_d(cx: float, cy: float, rx: float, ry: float) -> str:
    return (
        f"M{cx - rx:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 1,1 {cx + rx:.1f},{cy:.1f} "
        f"A{rx:.1f},{ry:.1f} 0 1,1 {cx - rx:.1f},{cy:.1f} Z"
    )


def garden_hose(paint: str, fill: Fill, label: str | None, style: str = "coiled",
                part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A garden hose: ``coiled`` (three loops of a plain hose, one free end with a brass
    connector) or ``expandable`` (a thin ribbed hose laid in an S with a connector at each end).
    A decoy that names the connectors' color ("with Green Connectors") passes ``part``
    ``connectors`` and ``part_color``: every connector is drawn in it and the hose is not."""
    pt = _Part("garden_hose", part, part_color)
    if style.lower() == "expandable":
        run = "M70,310 C70,230 330,260 330,190 C330,130 120,150 120,100"
        out = [
            _tube(run, paint, 14),
            _line(run, 14, ' stroke-dasharray="2 9" stroke-opacity=".55"', _shade(fill.base, 0.4)),
            _fitting(70, 322, 30, 26, pt),
            _fitting(120, 88, 26, 24, pt),
            _highlight("M334,200 C340,150 250,150 200,146", 3, 0.5),
        ]
    else:
        out = []
        for rx, ry in COIL_LOOPS:
            out.append(_tube(_ellipse_d(190, 190, rx, ry), paint, 20))
        out += [
            _tube("M62,190 C40,250 70,320 150,330 L300,336", paint, 20),
            _fitting(318, 336, 28, 30, pt),
            _line("M334,326 L366,318 M334,346 L366,354", 3),
            _highlight("M80,160 C100,110 150,92 190,98", 4, 0.5),
            _line(_ellipse_d(190, 190, 28, 18), 2, ' stroke-opacity=".4"', _tint(fill.base, 0.2)),
        ]
    if label:
        out += _panel(264, 350, 100, 28, label, 16)
    return out


SHAPES = {"garden_hose": garden_hose, "lawn_mower": lawn_mower, "robot_mower": robot_mower, "grass_trimmer": grass_trimmer, "bbq": bbq}
register(SHAPES)
