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
==============  ==========================================  ==========================

A drawing never prints a width, an area or a diameter: a style's SKUs share one image per
colorway. Every param is a string with a default, so each shape also draws bare. The mower's power
source is drawn as what feeds it (a battery pack, a fuel cap and pull cord, or a cable), which
``tests/test_retail_garden_203.py`` counts against the record.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import Fill, _highlight, _line, _path, _shade, _tint, register
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


def _wheel(cx: float, cy: float, r: float) -> str:
    return _ell(cx, cy, r, r, GREASE) + _ell(cx, cy, r * 0.4, r * 0.4, POLE, 1.6)


def lawn_mower(paint: str, fill: Fill, label: str | None, power: str = "cordless", drive: str = "push") -> list[str]:
    """A lawn mower: a deck, a grass bag and a push handle. ``power`` adds a battery pack
    (cordless), a fuel cap with a pull cord (petrol) or a trailing cable (electric); ``self``
    drive adds a drive lever on the handle and a drive arrow on the deck."""
    power, drive = power.lower(), drive.lower()
    bag = _tint(fill.base, 0.5)
    out = [
        _line("M20,334 L380,334", 4),
        _path("M300,232 L384,232 L384,298 L300,298 Z", bag),
        _line("M318,236 L318,296 M342,236 L342,296 M366,236 L366,296", 1.6, ' stroke-opacity=".4"'),
        _line("M296,230 L352,96 L384,106", 6),
        _line("M296,230 L352,96 L384,106", 3, stroke=POLE),
        _path("M64,296 Q64,236 128,230 L282,230 Q338,236 338,296 Z", paint),
        _highlight("M92,254 Q104,240 140,238", 4, 0.5),
        _wheel(112, 306, 26),
        _wheel(284, 302, 36 if drive == "self" else 28),
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


def robot_mower(paint: str, fill: Fill, label: str | None, boundary: str = "wire") -> list[str]:
    """A robot mower: a low dome on two wheels with a stop button. ``wire`` shows the boundary
    wire pegged out in the grass in front of it; ``gps`` puts a satellite dome on its back."""
    dark = _shade(fill.base, 0.35)
    out = [_line("M20,334 L380,334", 4)]
    if boundary.lower() == "gps":
        out += [_ell(200, 150, 26, 18, POLE, 2.4), _line("M200,132 L200,112 M186,136 L170,122 M214,136 L230,122", 2.4)]
    else:
        out += [_line("M20,352 L380,352", 3.2, ' stroke-dasharray="10 8"', stroke="#e07a1f")]
    out += [
        _path("M56,312 Q52,196 200,182 Q348,196 344,312 Z", paint),
        _path("M56,312 L344,312 L344,326 Q200,338 56,326 Z", dark, 2.4),
        _rect(170, 214, 60, 22, dark, 8, 2.4),
        _line("M176,248 L224,248", 3, ' stroke-opacity=".5"'),
        _wheel(96, 322, 22),
        _wheel(304, 322, 22),
        _highlight("M84,262 Q104,214 160,200", 4, 0.5),
    ]
    return _label(out, label)


def grass_trimmer(paint: str, fill: Fill, label: str | None, head: str = "line", power: str = "cordless") -> list[str]:
    """A grass trimmer: a long shaft from a cutting head to a handle. ``head`` draws a nylon-line
    spool with two whiskers (line) or a toothed blade under a guard (blade); ``power`` puts a
    battery pack (cordless), an engine with a fuel cap (petrol) or a cable (electric) at the top."""
    head, power = head.lower(), power.lower()
    dark = _shade(fill.base, 0.35)
    out = [_line("M96,330 L296,92", 9), _line("M96,330 L296,92", 5, stroke=POLE)]
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
        _path("M262,132 Q320,112 340,70 Q348,52 330,50 L300,60 Q300,86 262,104 Z", paint),
        _line("M232,160 L270,184", 7),
        _line("M232,160 L270,184", 3.4, stroke=POLE),
    ]
    if power == "cordless":
        out += [f'<g class="{BATTERY_CLASS}">{_rect(264, 46, 70, 40, dark, 6)}{_line("M276,66 L322,66", 2.4, stroke="#ffffff")}</g>']
    elif power == "petrol":
        out += [
            _rect(256, 52, 76, 36, dark, 8),
            f'<g class="{FUEL_CLASS}">{_ell(294, 46, 12, 7, POLE, 2.4)}</g>',
        ]
    else:
        out += [f'<g class="{CABLE_CLASS}">{_line("M340,70 Q380,120 360,230 Q340,330 280,350", 3.4, stroke="#e07a1f")}</g>']
    return _label(out, label)


def _legs(*xs: float, top: float = 272, bottom: float = 340) -> str:
    return _line(" ".join(f"M{x:g},{top:g} L{x + (x - 200) * 0.12:g},{bottom:g}" for x in xs), 6)


def _knobs(count: int, y: float, x0: float, x1: float) -> list[str]:
    gap = (x1 - x0) / max(count - 1, 1)
    return [f'<g class="{KNOB_CLASS}">{_ell(x0 + i * gap, y, 9, 9, GREASE, 2.4)}</g>' for i in range(count)]


def bbq(paint: str, fill: Fill, label: str | None, kind: str = "kettle", burners: str = "3",
        side_burner: str = "no") -> list[str]:  # fmt: skip
    """A barbecue. ``kettle`` is a dome on a bowl and three legs, ``barrel`` a horizontal drum on a
    stand with a chimney, ``kamado`` an egg on a cradle, ``portable`` a low bowl on short legs with a
    carry handle, and ``gas`` a cabinet under a hood with side shelves and one knob per burner, and a
    hob on the right shelf when ``side_burner`` is ``yes``."""
    kind = kind.lower()
    side_burner = side_burner.lower() == "yes"
    dark = _shade(fill.base, 0.35)
    out = [_line("M20,346 L380,346", 4)]
    if kind == "barrel":
        out += [
            _line("M120,262 L96,346 M280,262 L304,346", 6),
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
            _line("M100,282 L72,346 M300,282 L328,346", 6),
            _line("M120,176 Q200,126 280,176", 6, stroke=POLE),
            _line("M320,214 L368,214", 6, stroke=POLE),
        ]
    elif kind == "gas":
        try:
            count = max(1, min(int(burners), 6))
        except ValueError:
            count = 3
        out += [
            _legs(110, 290, top=276),
            _ell(110, 346, 12, 12, GREASE, 2.4),
            _ell(290, 346, 12, 12, GREASE, 2.4),
            _path("M96,150 Q96,98 200,98 Q304,98 304,150 L304,168 L96,168 Z", paint),
            _line("M170,120 L230,120", 6, stroke=POLE),
            _path("M92,168 L308,168 L308,276 L92,276 Z", dark),
            f'<g class="{SHELF_CLASS}">{_path("M30,184 L92,184 L92,198 L30,198 Z", paint, 2.4)}</g>',
            f'<g class="{SHELF_CLASS}">{_path("M308,184 L370,184 L370,198 L308,198 Z", paint, 2.4)}</g>',
            *_knobs(count, 188, 136, 264),
            *([f'<g class="{SIDE_BURNER_CLASS}">{_ell(339, 176, 22, 7, GREASE, 2.4)}</g>'] if side_burner else []),
            _line("M100,218 L300,218 M100,246 L300,246", 1.6, ' stroke-opacity=".4"'),
        ]
    else:
        out += [
            _line("M150,240 L120,346 M250,240 L280,346 M200,250 L200,346", 6),
            _path("M70,208 Q70,262 200,266 Q330,262 330,208 Z", dark),
            _path("M80,208 Q80,96 200,96 Q320,96 320,208 Z", paint),
            _ell(200, 84, 10, 10, POLE, 2.4),
            _line("M150,150 L150,150 M200,140 L200,140 M250,150 L250,150", 7),
            _highlight("M100,170 Q104,124 150,106", 4, 0.5),
        ]
    return _label(out, label)


SHAPES = {"lawn_mower": lawn_mower, "robot_mower": robot_mower, "grass_trimmer": grass_trimmer, "bbq": bbq}
register(SHAPES)
