"""Women's bag shapes for the retail drawing kit (gen#1114): crossbody, shoulder and clutch bags.

Each shape reads the style's form from ``bag_shape`` and its surface from ``material``, the two
attributes of the same names, so a derived style that swaps its material draws the one it states.
The form is what the closure follows (a saddle bag closes with a flap), so it is never swapped
(``scale_text.TYPE_FROZEN_KEYS``).

=============  ==========================================  ================================
shape          ``bag_shape``                               ``material``
=============  ==========================================  ================================
crossbody_bag  saddle, camera, satchel (long strap)        leather, faux leather, canvas, nylon
shoulder_bag   hobo, baguette, crescent (short strap)      leather, faux leather, suede
clutch_bag     envelope, foldover, frame (no strap)        satin, velvet, faux leather
=============  ==========================================  ================================

Every param is a string with a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import details
from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    Fill,
    _highlight,
    _line,
    _panel,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_accessories import HARDWARE, _band, _circle, _rect


def _surface(material: str, fill: Fill, x0: float, y0: float, x1: float, y1: float) -> list[str]:
    """What the main panel is made of, drawn inside the box (x0, y0, x1, y1)."""
    ink = _shade(fill.base, 0.28)
    light = _tint(fill.base, 0.35)
    if material == "canvas":  # a plain weave
        rows = [_line(f"M{x0},{y} L{x1},{y}", 1.1, "", ink) for y in range(int(y0), int(y1), 14)]
        return rows + [_line(f"M{x},{y0} L{x},{y1}", 1.1, "", ink) for x in range(int(x0), int(x1), 14)]
    if material == "nylon":  # diagonal ripstop lines
        h = y1 - y0
        return [_line(f"M{x},{y1} L{x + h},{y0}", 1.6, "", light) for x in range(int(x0), int(x1 - h) + 1, 18)]
    if material == "suede":  # a nap of short strokes
        return [_line(f"M{x + (y % 4) * 4},{y} L{x + (y % 4) * 4},{y + 9}", 1.6, "", ink)
                for y in range(int(y0), int(y1) - 8, 19) for x in range(int(x0), int(x1) - 14, 22)]  # fmt: skip
    if material == "satin":  # broad soft sheen bands
        return [_line(f"M{x},{y1} Q{x + 26},{(y0 + y1) / 2} {x + 14},{y0}", 7, ' stroke-opacity=".55"', light)
                for x in range(int(x0) + 10, int(x1) - 30, 54)]  # fmt: skip
    if material == "velvet":  # a dense pile in dashed rows
        return [_line(f"M{x0},{y} L{x1},{y}", 2.4, ' stroke-dasharray="2 7"', light) for y in range(int(y0), int(y1), 11)]
    if material == "faux leather":  # an even embossed pebble
        return [_circle(x, y, 2.2, light, 0.8) for y in range(int(y0) + 8, int(y1), 24)
                for x in range(int(x0) + 8, int(x1), 24)]  # fmt: skip
    # Leather: a topstitched edge and one long highlight.
    return [_line(f"M{x0},{y0} L{x0},{y1} L{x1},{y1} L{x1},{y0}", 1.6, ' stroke-dasharray="6 4"', ink),
            _highlight(f"M{x0 + 12},{y0 + 10} L{x0 + 12},{y1 - 14}", 4, 0.35)]  # fmt: skip


def _label(out: list[str], label: str | None) -> list[str]:
    if label:
        out += _panel(150, 356, 100, 28, label, 16)
    return out


def crossbody_bag(paint: str, fill: Fill, label: str | None, bag_shape: str = "saddle", material: str = "leather") -> list[str]:  # fmt: skip
    """A small bag on a long strap: a ``saddle`` with a round flap, a zipped ``camera`` bag with a
    front pocket, or a ``satchel`` with two buckled straps."""
    dark = _shade(fill.base, 0.3)
    out = _band("M112,206 C40,-30 360,-30 288,206", dark, 9)
    if bag_shape == "camera":
        out += [_path("M96,212 Q96,190 118,190 L282,190 Q304,190 304,212 L304,322 Q304,342 284,342 L116,342 Q96,342 96,322 Z", paint),
                *_surface(material, fill, 112, 222, 288, 258),
                _line("M110,206 L290,206", 2.4, ' stroke-dasharray="7 3"'), _rect(262, 200, 26, 12, HARDWARE, 4, 1.6),
                _path("M122,268 L278,268 L278,328 L122,328 Z", _tint(fill.base, 0.18)),
                _line("M122,280 L278,280", 2.2, ' stroke-dasharray="7 3"')]  # fmt: skip
    elif bag_shape == "satchel":
        out += [_path("M78,186 L322,186 L322,338 L78,338 Z", paint), *_surface(material, fill, 90, 284, 310, 330),
                _path("M78,186 L322,186 L322,270 L78,270 Z", _shade(fill.base, 0.12)),
                *[p for x in (128, 250) for p in (_path(f"M{x},206 L{x + 22},206 L{x + 22},318 L{x},318 Z", dark),
                                                  _rect(x - 3, 274, 28, 20, HARDWARE, 3, 1.8))]]  # fmt: skip
    else:
        out += [_path("M98,194 L302,194 Q322,262 300,318 Q284,344 200,344 Q116,344 100,318 Q78,262 98,194 Z", paint),
                *_surface(material, fill, 126, 284, 274, 330),
                _path("M98,194 L302,194 Q314,236 290,262 Q250,292 200,292 Q150,292 110,262 Q86,236 98,194 Z", _tint(fill.base, 0.14)),
                _circle(200, 272, 9, HARDWARE, 1.6)]  # fmt: skip
    return _label(out, label)


def shoulder_bag(paint: str, fill: Fill, label: str | None, bag_shape: str = "hobo", material: str = "leather") -> list[str]:  # fmt: skip
    """A bag carried under the arm on one short strap: a slouched ``hobo``, a long low ``baguette``
    with a flap, or a moon-shaped ``crescent``."""
    dark = _shade(fill.base, 0.3)
    if bag_shape == "baguette":
        out = _band("M96,226 C110,92 290,92 304,226", dark, 12)
        out += [_path("M60,222 L340,222 Q348,222 348,232 L348,320 Q348,332 336,332 L64,332 Q52,332 52,320 L52,232 Q52,222 60,222 Z", paint),
                *_surface(material, fill, 72, 290, 328, 324),
                _path("M60,222 L340,222 Q348,222 348,232 L348,272 L52,272 L52,232 Q52,222 60,222 Z", _tint(fill.base, 0.14)),
                _rect(184, 260, 32, 22, HARDWARE, 5, 1.8)]  # fmt: skip
    elif bag_shape == "crescent":
        out = _band("M70,214 C92,50 308,50 330,214", dark, 13)
        out += [_path("M52,206 Q200,262 348,206 Q352,344 200,344 Q48,344 52,206 Z", paint),
                *_surface(material, fill, 130, 264, 270, 326),
                _line("M62,220 Q200,274 338,220", 2.4, ' stroke-dasharray="7 3"'),
                _rect(308, 224, 22, 12, HARDWARE, 4, 1.6)]  # fmt: skip
    else:
        out = [_path("M78,220 Q84,56 200,56 Q316,56 322,220 L290,220 Q280,92 200,92 Q120,92 110,220 Z", dark),
               _path("M78,214 Q140,252 200,236 Q260,252 322,214 Q366,320 300,342 L100,342 Q34,320 78,214 Z", paint),
               *_surface(material, fill, 104, 264, 296, 326),
               _circle(94, 214, 9, HARDWARE, 1.8), _circle(306, 214, 9, HARDWARE, 1.8)]  # fmt: skip
    return _label(out, label)


def clutch_bag(paint: str, fill: Fill, label: str | None, bag_shape: str = "envelope", material: str = "satin") -> list[str]:  # fmt: skip
    """A strapless evening bag: an ``envelope`` with a pointed flap, a ``foldover`` whose top folds
    down, or a ``frame`` clutch with a metal kiss clasp."""
    if bag_shape == "foldover":
        out = [_path("M64,140 L336,140 L336,312 L64,312 Z", paint), *_surface(material, fill, 78, 248, 322, 302),
               _path("M58,134 L342,134 L342,226 Q200,240 58,226 Z", _shade(fill.base, 0.12)),
               _line("M66,218 Q200,231 334,218", 1.8, ' stroke-dasharray="5 4"', _tint(fill.base, 0.4))]  # fmt: skip
    elif bag_shape == "frame":
        out = [_path("M72,158 Q50,240 74,304 Q200,330 326,304 Q350,240 328,158 Z", paint),
               *_surface(material, fill, 96, 190, 304, 296),
               _path("M66,142 L334,142 L334,166 L66,166 Z", HARDWARE),
               _circle(190, 132, 11, HARDWARE, 2), _circle(212, 132, 11, HARDWARE, 2)]  # fmt: skip
    else:
        out = [_path("M52,146 L348,146 L348,308 L52,308 Z", paint), *_surface(material, fill, 68, 262, 332, 300),
               _path("M52,146 L348,146 L200,252 Z", _tint(fill.base, 0.14)),
               _line("M66,152 L200,246 L334,152", 1.6, ' stroke-dasharray="5 4"', INK),
               _circle(200, 240, 8, HARDWARE, 1.6)]  # fmt: skip
    return _label(out, label)


SHAPES = {"crossbody_bag": crossbody_bag, "shoulder_bag": shoulder_bag, "clutch_bag": clutch_bag}
register(SHAPES)
#: The one long strap of every crossbody form, down to the bag's top edge: "with Red Strap" draws it.
details.register_parts("crossbody_bag", {"strap": details.free(("M107,186 C60,-23 340,-23 293,186", 9.0))})
