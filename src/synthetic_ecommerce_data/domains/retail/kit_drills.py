"""Drill, driver, bit set, tool kit and step ladder shapes for the retail drawing kit (gen#191).

Each type of the DIY drill family has its own drawing in the kit's house style: outlines in the
kit's ink, the record's fill (color and pattern) on the tool's body, its light and its shade laid
over it. Each covers half of the product area or more in every param (gen#1215,
``docs/retail-drills-191.md``); the bit set's is gen#191's own.

==============  ==========================================  ==========================
shape           draws                                       params
==============  ==========================================  ==========================
drill_driver    a pistol body, a torque collar, a keyless   pack (compact, standard,
                chuck and a battery pack under the grip     large)
combi_drill     a drill driver with a second ring behind    pack, and always a
                the chuck and a hammer mark on the body     mode ring
hammer_drill    a long body with a side handle and a        power (cordless, corded)
                depth rod; a battery, or a cable and plug
corded_drill    an in-line motor body with a keyed chuck,   handle (pistol, side)
                its cable tied in a hank; no battery
impact_driver   a short stubby body, a hammer case and a    batteries (0, 1, 2)
                hex collet; a battery per ``batteries``
sds_drill       a barrel over an upright motor, a D-handle  power (corded, cordless)
                at the back, an SDS chuck with two grooves
drill_bit_set   an open case holding a row of bits of       shank (round, hex, sds),
                the set's shank                             bits (3 to 23)
tool_kit        an open case, or a bag, holding a hammer,   case (case, bag)
                pliers, screwdrivers and a tape
step_ladder     an A-frame with one deep tread per step     steps (2 to 5), kind
                over its rear legs                          (stool, ladder)
volt_meter      a body with a display, a dial and sockets:  form (handheld, clamp)
                two probes on their leads, or a jaw on top
==============  ==========================================  ==========================

A drawing never prints a voltage, a wattage or a piece count: the title says it and a style's
SKUs share one image. Every param is a string with a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    Fill,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_furniture import _dim, _lit, _quad
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

METAL = "#aeb4bb"
GRIP = "#3a3f47"
WOOD = "#c99a5b"
#: Battery pack height by the ``pack`` param: a bigger voltage is a bigger pack.
PACK_H = {"compact": 44, "standard": 56, "large": 68}
#: Classes a test counts against the record.
BATTERY_CLASS = "battery"
TREAD_CLASS = "tread"
BIT_CLASS = "bit"
#: The most bits a case draws: with the case, a set of 24 pieces (``pack_copies.MOST_DRAWN``).
MOST_BITS = 23
CABLE_CLASS = "cable"


def _battery(x: float, y: float, w: float, h: float, fill: str) -> str:
    """A slide-on pack: its case, its light, its shade and the ribs of its release."""
    return (
        f'<g class="{BATTERY_CLASS}">'
        + _rect(x, y, w, h, fill, 10)
        + _lit(
            _quad(
                (x + 8, y + 4), (x + w - 8, y + 4), (x + w - 14, y + h * 0.4), (x + 8, y + h * 0.4)
            ),
            0.22,
        )
        + _dim(
            _quad(
                (x + 8, y + h * 0.74),
                (x + w - 6, y + h * 0.74),
                (x + w - 8, y + h - 3),
                (x + 10, y + h - 3),
            ),
            0.2,
        )
        + _line(
            f"M{x + w - 40:.1f},{y + h * 0.5:.1f} L{x + w - 14:.1f},{y + h * 0.5:.1f} M{x + w - 40:.1f},{y + h * 0.64:.1f} L{x + w - 14:.1f},{y + h * 0.64:.1f}",
            2,
        )
        + "</g>"
    )


def _cable(d: str) -> str:
    """A mains cable along ``d``: its sheath, lit along its length."""
    return (
        _line(d, 10) + _line(d, 6.6, "", GRIP) + _line(d, 1.6, ' stroke-opacity="0.4"', "#ffffff")
    )


def _hank(cx: float, cy: float, w: float, h: float) -> str:
    """A cable folded into a figure of eight and tied at its middle, as it is sold."""
    x0, x1, up, dn = cx - w / 2, cx + w / 2, cy - h * 0.62, cy + h * 0.62
    body = (
        f"M{cx:.1f},{cy - 13:.1f} C{cx + w * 0.16:.1f},{up:.1f} {x1:.1f},{up:.1f} {x1:.1f},{cy:.1f} "
        f"C{x1:.1f},{dn:.1f} {cx + w * 0.16:.1f},{dn:.1f} {cx:.1f},{cy + 13:.1f} "
        f"C{cx - w * 0.16:.1f},{dn:.1f} {x0:.1f},{dn:.1f} {x0:.1f},{cy:.1f} "
        f"C{x0:.1f},{up:.1f} {cx - w * 0.16:.1f},{up:.1f} {cx:.1f},{cy - 13:.1f} Z"
    )
    strands = " ".join(
        f"M{cx - w * 0.5 * k:.1f},{cy:.1f} C{cx - w * 0.5 * k:.1f},{cy - h * 0.6 * k:.1f} {cx - w * 0.16:.1f},{cy - h * 0.6 * k:.1f} {cx:.1f},{cy - 11 * k:.1f} "
        f"C{cx + w * 0.16:.1f},{cy + h * 0.6 * k:.1f} {cx + w * 0.5 * k:.1f},{cy + h * 0.6 * k:.1f} {cx + w * 0.5 * k:.1f},{cy:.1f} "
        f"C{cx + w * 0.5 * k:.1f},{cy - h * 0.6 * k:.1f} {cx + w * 0.16:.1f},{cy - h * 0.6 * k:.1f} {cx:.1f},{cy - 11 * k:.1f} "
        f"C{cx - w * 0.16:.1f},{cy + h * 0.6 * k:.1f} {cx - w * 0.5 * k:.1f},{cy + h * 0.6 * k:.1f} {cx - w * 0.5 * k:.1f},{cy:.1f}"
        for k in (0.82, 0.6, 0.36)
    )
    return (
        _path(body, GRIP)
        + _line(strands, 1.6, "", _tint(GRIP, 0.4))
        + _rect(cx - 9, cy - 19, 18, 38, METAL, 4, 1.6)
    )


def _plug(x: float, y: float) -> str:
    """A mains plug, its pins to the left."""
    return (
        _line(
            f"M{x:.1f},{y + 9:.1f} L{x - 13:.1f},{y + 9:.1f} M{x:.1f},{y + 23:.1f} L{x - 13:.1f},{y + 23:.1f}",
            4,
        )
        + _rect(x, y, 34, 32, GRIP, 6)
        + _lit(_quad((x + 4, y + 4), (x + 30, y + 4), (x + 28, y + 12), (x + 4, y + 12)), 0.25)
    )


def _chuck(x: float, y: float, keyed: bool = False, big: float = 1.0) -> list[str]:
    """A chuck from ``x`` along the axis ``y`` (70 long) with a twist bit in it; a keyed one is
    a steel barrel with its key standing in it, a keyless one a ribbed sleeve."""
    a, b = 46 * big, 30 * big
    sleeve = METAL if keyed else GRIP
    out = [
        _path(
            f"M{x + 60:.1f},{y - 8:.1f} L{x + 92:.1f},{y - 6:.1f} L{x + 102:.1f},{y:.1f} L{x + 92:.1f},{y + 6:.1f} L{x + 60:.1f},{y + 8:.1f} Z",
            METAL,
            1.6,
        ),
        _line(
            f"M{x + 74:.1f},{y - 7:.1f} L{x + 82:.1f},{y + 7:.1f} M{x + 84:.1f},{y - 6:.1f} L{x + 92:.1f},{y + 6:.1f}",
            1.6,
        ),
        _path(
            f"M{x:.1f},{y - a:.1f} L{x + 34:.1f},{y - a:.1f} L{x + 66:.1f},{y - b:.1f} L{x + 66:.1f},{y + b:.1f} L{x + 34:.1f},{y + a:.1f} L{x:.1f},{y + a:.1f} Z",
            sleeve,
        ),
        _lit(
            _quad(
                (x + 2, y - a * 0.78),
                (x + 34, y - a * 0.78),
                (x + 64, y - b * 0.78),
                (x + 64, y - b * 0.2),
                (x + 34, y - a * 0.2),
                (x + 2, y - a * 0.2),
            ),
            0.3,
        ),
        _dim(
            _quad(
                (x + 2, y + a * 0.5),
                (x + 34, y + a * 0.5),
                (x + 64, y + b * 0.5),
                (x + 64, y + b * 0.95),
                (x + 34, y + a * 0.95),
                (x + 2, y + a * 0.95),
            ),
            0.25,
        ),
    ]
    ribs = " ".join(
        f"M{x + 4:.1f},{y + a * t:.1f} L{x + 32:.1f},{y + a * t:.1f}"
        for t in (-0.6, -0.2, 0.2, 0.6)
    )
    out.append(_line(ribs, 1.6, "", _shade(sleeve, 0.45)))
    out.append(_line(f"M{x + 34:.1f},{y - a:.1f} L{x + 34:.1f},{y + a:.1f}", 1.8))
    if keyed:
        out += [
            _rect(x + 13, y + a - 6, 9, 34, METAL, 2, 1.6),
            _rect(x - 4, y + a + 24, 43, 10, METAL, 4, 1.6),
            _ell(x + 48, y, 5, 8, GRIP, 1.6),
        ]
    return out


def _collar(x: float, y: float, w: float, half: float, fill: str) -> list[str]:
    """A ribbed setting ring ``w`` wide round the axis ``y``."""
    ribs = " ".join(
        f"M{x + 4:.1f},{y + half * t:.1f} L{x + w - 4:.1f},{y + half * t:.1f}"
        for t in (-0.72, -0.48, -0.24, 0, 0.24, 0.48, 0.72)
    )
    return [
        _rect(x, y - half, w, 2 * half, fill, 6),
        _lit(
            _quad(
                (x + 3, y - half * 0.8),
                (x + w - 3, y - half * 0.8),
                (x + w - 3, y - half * 0.3),
                (x + 3, y - half * 0.3),
            ),
            0.28,
        ),
        _dim(
            _quad(
                (x + 3, y + half * 0.5),
                (x + w - 3, y + half * 0.5),
                (x + w - 3, y + half * 0.94),
                (x + 3, y + half * 0.94),
            ),
            0.2,
        ),
        _line(ribs, 1.6, "", _tint(fill, 0.45)),
    ]


def _grip(x: float, y: float, foot: float, w: float, fill: Fill) -> list[str]:
    """What a pistol grip carries from (``x``, ``y``) to its ``foot``: the trigger in front of it,
    the rubber down its face, the shade down its back."""
    mid = (y + foot) / 2
    return [
        _path(
            f"M{x + w - 4:.1f},{y:.1f} L{x + w + 26:.1f},{y:.1f} Q{x + w + 14:.1f},{y + 24:.1f} {x + w + 12:.1f},{y + 46:.1f} L{x + w - 8:.1f},{y + 46:.1f} Z",
            GRIP,
            1.8,
        ),
        _path(
            f"M{x + w * 0.42:.1f},{y + 6:.1f} L{x + w - 10:.1f},{y + 6:.1f} Q{x + w - 18:.1f},{mid:.1f} {x + w - 12:.1f},{foot - 6:.1f} L{x + w * 0.42:.1f},{foot - 6:.1f} Q{x + w * 0.28:.1f},{mid:.1f} {x + w * 0.42:.1f},{y + 6:.1f} Z",
            _shade(GRIP, 0.1),
            1.6,
        ),
        _lit(
            _quad(
                (x + w * 0.5, y + 10),
                (x + w * 0.66, y + 10),
                (x + w * 0.62, foot - 10),
                (x + w * 0.48, foot - 10),
            ),
            0.16,
        ),
        _dim(
            f"M{x + 3:.1f},{y:.1f} L{x + w * 0.2:.1f},{y:.1f} Q{x + w * 0.12:.1f},{mid:.1f} {x + w * 0.22:.1f},{foot:.1f} L{x + 8:.1f},{foot:.1f} Q{x + 2:.1f},{mid:.1f} {x + 3:.1f},{y:.1f} Z",
            0.18,
        ),
    ]


def _vents(x: float, y: float, h: float, n: int = 4) -> str:
    """The motor's cooling slots."""
    return _line(
        " ".join(f"M{x + 11 * i:.1f},{y:.1f} L{x + 11 * i - 5:.1f},{y + h:.1f}" for i in range(n)),
        4,
    )


def _housing(x0: float, x1: float, y0: float, y1: float) -> list[str]:
    """The light along the top of a motor housing and the shade under it."""
    h = y1 - y0
    return [
        _lit(
            f"M{x0 + 10:.1f},{y0 + h * 0.42:.1f} Q{x0 + 10:.1f},{y0 + 8:.1f} {x0 + 44:.1f},{y0 + 6:.1f} L{x1 - 6:.1f},{y0 + 6:.1f} L{x1 - 6:.1f},{y0 + h * 0.34:.1f} Q{(x0 + x1) / 2:.1f},{y0 + h * 0.3:.1f} {x0 + 10:.1f},{y0 + h * 0.42:.1f} Z",
            0.3,
        ),
        _dim(
            f"M{x0 + 8:.1f},{y1 - h * 0.3:.1f} Q{(x0 + x1) / 2:.1f},{y1 - h * 0.2:.1f} {x1 - 4:.1f},{y1 - h * 0.26:.1f} L{x1 - 4:.1f},{y1 - 4:.1f} L{x0 + 34:.1f},{y1 - 4:.1f} Q{x0 + 12:.1f},{y1 - 8:.1f} {x0 + 8:.1f},{y1 - h * 0.3:.1f} Z",
            0.18,
        ),
    ]


def _pistol(paint: str, fill: Fill, pack: str) -> list[str]:
    """A cordless pistol body from the rear cap to the chuck's collar, on its battery."""
    h = PACK_H.get(pack.lower(), 56)
    return [
        _battery(64, 288, 198, h, _shade(fill.base, 0.35)),
        _path(
            "M34,80 Q34,34 74,34 L232,34 Q246,34 246,50 L246,156 Q246,174 228,174 L212,176 Q200,226 212,264 L244,268 Q256,270 256,288 L72,288 Q72,270 84,266 L94,264 Q84,220 88,176 L74,174 Q34,174 34,132 Z",
            paint,
        ),
        *_housing(34, 246, 34, 174),
        _path("M34,80 Q34,34 74,34 L80,34 L80,174 L74,174 Q34,174 34,132 Z", GRIP),
        _lit("M42,84 Q42,46 70,42 L74,42 L74,82 L42,96 Z", 0.2),
        _vents(51, 92, 46, 3),
        *_grip(88, 178, 262, 118, fill),
    ]


def drill_driver(paint: str, fill: Fill, label: str | None, pack: str = "standard") -> list[str]:
    """A cordless drill driver: a pistol body and a battery pack whose height follows ``pack``."""
    out = [*_chuck(266, 104), *_pistol(paint, fill, pack), *_collar(240, 104, 30, 58, GRIP)]
    out.append(_line("M96,118 L226,118", 1.6, ' stroke-dasharray="6 4"'))
    return _label(out, label)


def combi_drill(paint: str, fill: Fill, label: str | None, pack: str = "standard") -> list[str]:
    """A combi drill: a drill driver with a mode ring behind the chuck and a hammer mark."""
    out = [
        *_chuck(266, 104),
        *_pistol(paint, fill, pack),
        *_collar(222, 104, 26, 66, _shade(fill.base, 0.5)),
        *_collar(246, 104, 26, 58, GRIP),
        _path(
            "M100,92 L156,92 L156,106 L135,106 L135,148 L121,148 L121,106 L100,106 Z",
            _tint(fill.base, 0.4),
            1.8,
        ),
    ]
    return _label(out, label)


def hammer_drill(paint: str, fill: Fill, label: str | None, power: str = "cordless") -> list[str]:
    """A hammer drill: a long body, a side handle and a depth rod; cordless it carries a battery,
    corded a cable and a plug."""
    corded = power.lower() == "corded"
    foot = 320 if corded else 284
    out = [
        _rect(200, 38, 164, 10, METAL, 3, 1.8),
        *_chuck(262, 112, big=0.9),
        _path(
            f"M34,94 Q34,54 72,54 L236,54 Q250,54 250,68 L250,160 Q250,174 234,174 L196,176 Q184,230 194,{foot - 20} L222,{foot - 18} Q232,{foot - 16} 232,{foot} L60,{foot} Q60,{foot - 18} 72,{foot - 20} L80,{foot - 22} Q68,230 74,176 L70,174 Q34,172 34,134 Z",
            paint,
        ),
        *_housing(34, 250, 54, 174),
        _vents(58, 88, 50, 4),
        _rect(150, 42, 66, 18, GRIP, 6, 1.8),
        *_grip(76, 180, foot - 22, 112, fill),
        *_collar(236, 112, 30, 56, METAL),
        _path(
            "M240,160 L276,160 L276,184 Q286,190 286,206 L290,302 Q290,320 268,320 L262,320 Q242,320 242,302 L238,206 Q238,190 244,184 L240,184 Z",
            GRIP,
        ),
        _lit("M248,200 L258,200 L262,308 L252,304 Z", 0.28),
        _dim("M276,200 L283,204 L286,304 L276,312 Z", 0.3),
        _line(
            "M241,222 L286,222 M242,242 L287,242 M242,262 L288,262 M243,282 L288,282",
            2,
            "",
            _tint(GRIP, 0.3),
        ),
    ]
    if corded:
        out.insert(
            0,
            f'<g class="{CABLE_CLASS}">'
            + _cable("M140,318 L140,338 Q140,350 160,350 L262,350 Q300,350 322,330")
            + _hank(332, 262, 70, 152)
            + _plug(50, 324)
            + "</g>",
        )
    else:
        out.insert(0, _battery(44, 284, 190, 70, _shade(fill.base, 0.35)))
    return _label(out, label)


def corded_drill(paint: str, fill: Fill, label: str | None, handle: str = "pistol") -> list[str]:
    """A corded drill: an in-line motor body with a keyed chuck, and its cable tied in a hank with
    the plug beside it; ``side`` adds a side handle."""
    out = [
        f'<g class="{CABLE_CLASS}">'
        + _cable("M140,330 L140,340 Q140,352 160,352 L226,352 Q250,352 262,338")
        + _hank(300, 284, 136, 112)
        + _plug(52, 324)
        + "</g>",
        *_chuck(262, 96, keyed=True),
        _path(
            "M34,74 Q34,34 70,34 L210,34 L256,52 Q264,56 264,66 L264,128 Q264,138 254,142 L214,162 L200,166 Q188,230 198,292 Q200,330 178,332 L100,332 Q78,332 78,296 Q68,230 78,166 L70,164 Q34,160 34,122 Z",
            paint,
        ),
        *_housing(34, 208, 34, 162),
        _path(
            "M208,34 L256,52 Q264,56 264,66 L264,128 Q264,138 254,142 L214,162 L208,160 Z", METAL
        ),
        _lit("M212,42 L254,58 Q258,60 258,68 L258,84 L212,80 Z", 0.4),
        _dim("M212,124 L258,112 L258,126 Q258,134 250,138 L214,154 Z", 0.2),
        _path("M34,74 Q34,34 70,34 L76,34 L76,164 L70,164 Q34,160 34,122 Z", GRIP),
        _vents(50, 72, 56, 3),
        *_grip(78, 172, 318, 116, fill),
        _rect(122, 326, 36, 18, GRIP, 5),
    ]
    if handle.lower() == "side":
        out += [
            _rect(222, 30, 22, 140, GRIP, 6),
            _path("M214,160 L252,160 L256,214 Q256,226 244,226 L224,226 Q210,226 210,214 Z", GRIP),
            _line("M212,180 L253,180 M212,196 L254,196 M212,210 L255,210", 2, "", _tint(GRIP, 0.3)),
            _lit("M219,164 L228,164 L228,220 L218,220 Z", 0.25),
        ]
    return _label(out, label)


def impact_driver(paint: str, fill: Fill, label: str | None, batteries: str = "1") -> list[str]:
    """An impact driver: a short stubby body on a hex collet; ``batteries`` 0 is a bare tool, 1 a pack
    on the grip, 2 adds a spare pack beside it."""
    n = max(0, min(2, int(batteries or 0)))
    foot = 318 if not n else 278
    out = [
        _path("M336,96 L356,96 L368,102 L368,114 L356,120 L336,120 Z", METAL, 1.8),
        _rect(306, 80, 40, 56, METAL, 6),
        _lit(_quad((309, 86), (343, 86), (343, 102), (309, 102)), 0.45),
        _line("M318,81 L318,135 M332,81 L332,135", 1.8),
        _path("M228,38 L262,44 L310,74 L310,142 L262,172 L228,178 Z", _shade(METAL, 0.3)),
        _lit("M232,46 L260,52 L304,80 L304,98 L232,86 Z", 0.35),
        _dim("M232,140 L304,122 L304,138 L260,164 L232,170 Z", 0.25),
        _path(
            f"M34,86 Q34,34 84,34 L226,34 Q240,34 240,50 L240,166 Q240,182 224,182 L206,184 Q194,230 206,{foot - 4} L236,{foot} Q248,{foot + 4} 248,{foot + 22} L60,{foot + 22} Q60,{foot + 4} 72,{foot} L86,{foot - 4} Q74,230 82,184 Q34,178 34,136 Z",
            paint,
        ),
        *_housing(34, 240, 34, 182),
        _path("M34,86 Q34,34 84,34 L88,34 L88,184 L82,184 Q34,178 34,136 Z", GRIP),
        _vents(54, 86, 52, 3),
        *_grip(82, 188, foot, 120, fill),
        _rect(62, foot + 10, 184, 18, GRIP, 5),
    ]
    if n:
        out.insert(0, _battery(54, foot + 22, 200, 56, _shade(fill.base, 0.35)))
    else:
        out.append(_rect(78, foot + 24, 150, 14, METAL, 4))
    if n > 1:
        out.append(_battery(268, 250, 98, 106, _shade(fill.base, 0.35)))
    return _label(out, label)


def sds_drill(paint: str, fill: Fill, label: str | None, power: str = "corded") -> list[str]:
    """An SDS hammer drill: a barrel over an upright motor, a D-handle at the back, an SDS chuck
    with two grooves; corded it ends in a cable, cordless it carries a battery."""
    cordless = power.lower() == "cordless"
    out = [
        _path("M326,88 L360,90 L369,97 L360,104 L326,106 Z", METAL, 1.8),
        _rect(284, 64, 48, 66, GRIP, 8),
        _lit(_quad((288, 70), (328, 70), (328, 88), (288, 88)), 0.28),
        _line("M300,65 L300,129 M316,65 L316,129", 3, "", METAL),
        _path(
            "M116,56 L78,56 Q34,58 34,102 L34,236 Q34,276 74,276 L140,276 L140,238 L88,238 Q72,238 72,222 L72,118 Q72,98 92,98 L116,98 Z",
            GRIP,
        ),
        _lit("M44,104 Q44,68 78,66 L110,66 L110,76 L84,76 Q56,78 56,108 L56,220 L44,220 Z", 0.22),
        _path("M72,128 L88,132 Q92,150 88,172 L72,176 Z", _shade(fill.base, 0.2), 1.8),
        _path(
            "M100,52 Q100,36 118,36 L232,36 L290,58 L290,138 L262,160 L256,172 L256,276 Q256,290 242,290 L140,290 Q126,290 126,276 L126,168 L116,164 Q100,162 100,144 Z",
            paint,
        ),
        *_housing(100, 288, 40, 160),
        _path("M232,36 L290,58 L290,138 L262,160 L232,160 Z", METAL),
        _lit("M237,46 L285,64 L285,86 L237,78 Z", 0.4),
        _dim("M237,128 L285,118 L285,134 L260,154 L237,154 Z", 0.2),
        _ell(182, 130, 26, 26, GRIP, 2),
        _path("M178,108 L186,108 L188,130 L176,130 Z", METAL, 1.6),
        _lit("M136,176 L156,176 L156,276 L136,276 Z", 0.28),
        _dim("M216,170 L250,170 L250,280 L216,280 Z", 0.2),
        _line("M172,196 L212,196 M172,212 L212,212 M172,228 L212,228 M172,244 L212,244", 4),
        _path(
            "M262,140 L292,140 L296,164 Q308,172 308,188 L312,284 Q312,300 296,300 L286,300 Q270,300 270,284 L266,188 Q266,172 264,164 Z",
            GRIP,
        ),
        _line(
            "M268,204 L308,204 M268,222 L309,222 M269,240 L310,240 M270,258 L311,258 M270,276 L312,276",
            2,
            "",
            _tint(GRIP, 0.3),
        ),
        _lit("M274,184 L284,184 L288,290 L278,288 Z", 0.28),
    ]
    if cordless:
        out.insert(0, _battery(104, 284, 176, 70, _shade(fill.base, 0.35)))
    else:
        out.insert(
            0,
            f'<g class="{CABLE_CLASS}">'
            + _cable("M60,272 L60,318 Q60,330 78,330 L110,330")
            + _hank(168, 326, 132, 56)
            + _plug(252, 316)
            + "</g>",
        )
    return _label(out, label)


def drill_bit_set(
    paint: str, fill: Fill, label: str | None, shank: str = "round", bits: str = "9"
) -> list[str]:
    """A drill bit set: an open case holding one bit per slot, up to :data:`MOST_BITS`; the shank
    is round, hex (a flat hex tip) or SDS (a grooved tip)."""
    n = max(3, min(MOST_BITS, int(bits or 9)))
    out = [
        _path("M40,120 L360,120 L360,330 L40,330 Z", paint),
        _path("M52,132 L348,132 L348,318 L52,318 Z", _shade(fill.base, 0.3), 1.6),
    ]
    gap = 280 / n
    for i in range(n):
        x = 60 + gap * (i + 0.5)
        top = 152 + (i % 3) * 8
        tip = 292 - (i % 4) * 10
        out.append(
            f'<g class="{BIT_CLASS}">'
            + _path(
                f"M{x - 3:.1f},{top:.1f} L{x + 3:.1f},{top:.1f} L{x + 3:.1f},{tip:.1f} L{x:.1f},{tip + 8:.1f} L{x - 3:.1f},{tip:.1f} Z",
                METAL,
                1.4,
            )
        )
        if shank.lower() == "hex":
            out.append(
                _line(
                    f"M{x - 5:.1f},{top:.1f} L{x - 3:.1f},{top - 6:.1f} L{x + 3:.1f},{top - 6:.1f} L{x + 5:.1f},{top:.1f}",
                    1.4,
                )
            )
        elif shank.lower() == "sds":
            out.append(
                _line(
                    f"M{x - 3:.1f},{top + 6:.1f} L{x + 3:.1f},{top + 6:.1f} M{x - 3:.1f},{top + 14:.1f} L{x + 3:.1f},{top + 14:.1f}",
                    1.6,
                )
            )
        out.append("</g>")
    out.append(_rect(176, 124, 48, 12, GRIP, 4))
    return _label(out, label)


def _hammer_tool(x: float, y: float, h: float) -> list[str]:
    """A claw hammer standing on its handle, its head at the top."""
    return [
        _rect(x - 9, y + 26, 18, h - 26, WOOD, 5),
        _lit(_quad((x - 6, y + 34), (x - 1, y + 34), (x - 1, y + h - 6), (x - 6, y + h - 6)), 0.35),
        _path(
            f"M{x - 40:.1f},{y + 10:.1f} Q{x - 26:.1f},{y - 2:.1f} {x - 8:.1f},{y:.1f} L{x + 22:.1f},{y:.1f} L{x + 24:.1f},{y - 3:.1f} L{x + 36:.1f},{y - 3:.1f} L{x + 36:.1f},{y + 29:.1f} L{x + 24:.1f},{y + 29:.1f} L{x + 22:.1f},{y + 26:.1f} L{x - 10:.1f},{y + 26:.1f} Q{x - 24:.1f},{y + 14:.1f} {x - 40:.1f},{y + 20:.1f} Z",
            METAL,
        ),
        _lit(_quad((x - 8, y + 4), (x + 34, y + 4), (x + 34, y + 11), (x - 10, y + 11)), 0.45),
    ]


def _driver_tool(x: float, y: float, h: float, handle: str) -> list[str]:
    """A screwdriver with its handle up and its blade down."""
    return [
        _rect(x - 4, y + h * 0.5, 8, h * 0.5, METAL, 2, 1.8),
        _path(
            f"M{x - 12:.1f},{y + 12:.1f} Q{x - 12:.1f},{y:.1f} {x:.1f},{y:.1f} Q{x + 12:.1f},{y:.1f} {x + 12:.1f},{y + 12:.1f} L{x + 12:.1f},{y + h * 0.44:.1f} L{x + 7:.1f},{y + h * 0.54:.1f} L{x - 7:.1f},{y + h * 0.54:.1f} L{x - 12:.1f},{y + h * 0.44:.1f} Z",
            handle,
        ),
        _lit(
            _quad((x - 8, y + 10), (x - 2, y + 10), (x - 2, y + h * 0.42), (x - 8, y + h * 0.42)),
            0.4,
        ),
    ]


def _pliers_tool(x: float, y: float, h: float, handle: str) -> list[str]:
    """Pliers with their handles up and their jaws down."""
    a, b = y + h * 0.56, y + h
    return [
        _path(
            f"M{x - 24:.1f},{y:.1f} L{x - 10:.1f},{y:.1f} Q{x - 12:.1f},{y + h * 0.3:.1f} {x + 2:.1f},{a:.1f} L{x - 14:.1f},{a:.1f} Q{x - 28:.1f},{y + h * 0.3:.1f} {x - 24:.1f},{y:.1f} Z",
            handle,
        ),
        _path(
            f"M{x + 24:.1f},{y:.1f} L{x + 10:.1f},{y:.1f} Q{x + 12:.1f},{y + h * 0.3:.1f} {x - 2:.1f},{a:.1f} L{x + 14:.1f},{a:.1f} Q{x + 28:.1f},{y + h * 0.3:.1f} {x + 24:.1f},{y:.1f} Z",
            handle,
        ),
        _path(
            f"M{x - 15:.1f},{a - 4:.1f} L{x + 15:.1f},{a - 4:.1f} L{x + 14:.1f},{a + 18:.1f} L{x + 6:.1f},{b:.1f} L{x - 6:.1f},{b:.1f} L{x - 14:.1f},{a + 18:.1f} Z",
            METAL,
        ),
        _ell(x, a + 8, 5, 5, GRIP, 1.4),
        _line(f"M{x:.1f},{a + 16:.1f} L{x:.1f},{b:.1f}", 1.8),
        _lit(_quad((x - 12, a), (x - 5, a), (x - 3, b - 4), (x - 8, a + 16)), 0.4),
    ]


def _tape_tool(x: float, y: float, r: float, fill: Fill) -> list[str]:
    """A tape measure lying on its side, its blade's hook out."""
    return [
        _rect(x + r - 8, y + r * 0.5, r * 0.6, r * 0.3, "#f2c230", 2, 1.6),
        _rect(x - r, y - r * 0.9, 2 * r, 1.8 * r, _shade(fill.base, 0.2), r * 0.45),
        _lit(
            _quad(
                (x - r + 8, y - r * 0.8),
                (x + r - 10, y - r * 0.8),
                (x + r - 18, y - r * 0.45),
                (x - r + 6, y - r * 0.4),
            ),
            0.35,
        ),
        _ell(x, y, r * 0.56, r * 0.56, METAL, 1.8),
        _ell(x, y, r * 0.2, r * 0.2, GRIP, 1.4),
    ]


def tool_kit(paint: str, fill: Fill, label: str | None, case: str = "case") -> list[str]:
    """A tool kit: a hard case standing open with its tools in the lid and the tray, or a soft bag
    with the tools standing in its mouth."""
    handle = _tint(fill.base, 0.35)
    if case.lower() == "bag":
        out = [
            _path(
                "M66,170 Q66,108 120,96 L280,96 Q334,108 334,170 L318,170 Q318,124 276,112 L124,112 Q82,124 82,170 Z",
                GRIP,
            ),
            _path("M56,150 L344,150 L338,196 L62,196 Z", _shade(fill.base, 0.55)),
            *_hammer_tool(112, 42, 170),
            *_driver_tool(172, 48, 160, handle),
            *_pliers_tool(222, 40, 168, handle),
            *_driver_tool(268, 62, 150, "#f2c230"),
            *_tape_tool(306, 152, 30, fill),
            _path(
                "M44,184 Q46,176 58,176 L342,176 Q354,176 356,184 L364,330 Q364,354 340,354 L60,354 Q36,354 36,330 Z",
                paint,
            ),
            _lit("M54,186 L180,186 Q120,240 110,344 L60,344 Q46,344 46,328 Z", 0.26),
            _dim("M300,186 L346,186 L354,328 Q354,346 338,346 L262,346 Q310,280 300,186 Z", 0.18),
            _path("M40,312 L360,312 L364,330 Q364,354 340,354 L60,354 Q36,354 36,330 Z", GRIP),
            _path("M128,232 L272,232 L278,312 L122,312 Z", _shade(fill.base, 0.2), 2),
            _lit(_quad((132, 236), (268, 236), (269, 250), (131, 250)), 0.22),
            _line("M44,206 L356,206", 2, ' stroke-dasharray="7 5"'),
            _rect(84, 176, 22, 136, GRIP, 3, 1.8),
            _rect(294, 176, 22, 136, GRIP, 3, 1.8),
        ]
        return _label(out, label)
    out = [
        _rect(44, 34, 312, 150, paint, 14),
        _rect(60, 48, 280, 130, GRIP, 8, 2),
        _dim("M62,50 L338,50 L338,66 L62,66 Z", 0.35),
        _lit("M64,70 L150,70 L96,174 L64,174 Z", 0.1),
        *_driver_tool(94, 58, 112, handle),
        *_driver_tool(130, 58, 112, "#f2c230"),
        *_pliers_tool(184, 58, 112, handle),
        *(
            p
            for i in range(4)
            for p in (
                _ell(242 + 26 * i, 84, 11, 11, METAL, 1.8),
                _ell(242 + 26 * i, 84, 5, 5, GRIP, 1.2),
            )
        ),
        _rect(228, 108, 106, 16, METAL, 5, 1.8),
        _lit(_quad((232, 110), (330, 110), (330, 115), (232, 115)), 0.5),
        _rect(228, 138, 106, 12, METAL, 4, 1.8),
        _rect(88, 174, 30, 20, METAL, 4, 2),
        _rect(282, 174, 30, 20, METAL, 4, 2),
        _path("M44,190 L356,190 L368,312 L32,312 Z", paint),
        _path("M58,200 L342,200 L350,300 L50,300 Z", _shade(GRIP, 0.15), 2),
        _dim("M58,200 L342,200 L343,214 L57,214 Z", 0.35),
        f'<g transform="rotate(90 136 236)">{"".join(_hammer_tool(136, 168, 148))}</g>',
        *_tape_tool(282, 244, 34, fill),
        *(_rect(70 + 24 * i, 272, 16, 22, METAL, 3, 1.6) for i in range(6)),
        _path("M32,312 L368,312 L366,342 Q364,354 350,354 L50,354 Q36,354 34,342 Z", paint),
        _lit("M36,316 L364,316 L364,326 L36,326 Z", 0.3),
        _dim("M38,342 L362,342 Q360,350 348,351 L52,351 Q40,350 38,342 Z", 0.22),
        _rect(84, 306, 34, 24, METAL, 4, 2),
        _rect(282, 306, 34, 24, METAL, 4, 2),
        _path(
            "M158,318 L242,318 Q248,318 248,326 L248,344 L232,344 L232,334 L168,334 L168,344 L152,344 L152,326 Q152,318 158,318 Z",
            GRIP,
            2,
        ),
    ]
    return _label(out, label)


def _rail(x0: float, y0: float, x1: float, y1: float, w: float, paint: str) -> list[str]:
    """A ladder's upright from (``x0``, ``y0``) to its rubber foot at (``x1``, ``y1``)."""
    a = (x1 - x0) / (y1 - y0)
    fy = y1 - 18
    fx = x1 - a * 18
    return [
        _path(_quad((x0 - w / 2, y0), (x0 + w / 2, y0), (x1 + w / 2, y1), (x1 - w / 2, y1)), paint),
        _lit(
            _quad(
                (x0 - w / 2 + 3, y0 + 2),
                (x0 - w * 0.08, y0 + 2),
                (x1 - w * 0.08, y1 - 2),
                (x1 - w / 2 + 3, y1 - 2),
            ),
            0.4,
        ),
        _dim(
            _quad(
                (x0 + w * 0.2, y0 + 2),
                (x0 + w / 2 - 2, y0 + 2),
                (x1 + w / 2 - 2, y1 - 2),
                (x1 + w * 0.2, y1 - 2),
            ),
            0.2,
        ),
        _path(
            _quad(
                (fx - w / 2 - 3, fy),
                (fx + w / 2 + 3, fy),
                (x1 + w / 2 + 4, y1),
                (x1 - w / 2 - 4, y1),
            ),
            GRIP,
        ),
    ]


def step_ladder(
    paint: str, fill: Fill, label: str | None, steps: str = "3", kind: str = "ladder"
) -> list[str]:
    """A step ladder seen from in front and a little above: an A-frame with one deep tread per step,
    over its rear legs. A ``stool`` is wider and ends in a hand grip, a ``ladder`` in a top cap."""
    n = max(2, min(5, int(steps or 3)))
    stool = kind.lower() == "stool"
    top, foot = (112.0 if stool else 64.0), 356.0
    half, splay = (116.0, 152.0) if stool else (94.0, 138.0)
    w = 30.0
    rear = _shade(fill.base, 0.4)

    def across(y: float) -> float:
        return half + (splay - half) * (y - top) / (foot - top)

    out = [
        *_rail(200 - half + 26, top, 200 - splay + 46, foot - 22, 20, rear),
        *_rail(200 + half - 26, top, 200 + splay - 46, foot - 22, 20, rear),
        _rect(200 - across(foot - 78) + 40, foot - 78, 2 * across(foot - 78) - 80, 14, rear, 3, 2),
    ]
    if stool:
        out.append(
            _path(
                f"M{200 - 84},{top + 8:.1f} L{200 - 84},66 Q{200 - 84},34 {200 - 52},34 L{200 + 52},34 Q{200 + 84},34 {200 + 84},66 L{200 + 84},{top + 8:.1f} "
                f"L{200 + 62},{top + 8:.1f} L{200 + 62},70 Q{200 + 62},56 {200 + 48},56 L{200 - 48},56 Q{200 - 62},56 {200 - 62},70 L{200 - 62},{top + 8:.1f} Z",
                GRIP,
            )
        )
    out += [
        *_rail(200 - half, top, 200 - splay, foot, w, paint),
        *_rail(200 + half, top, 200 + splay, foot, w, paint),
    ]
    first = top if stool else top + 34
    span = (foot - 34 - first) / n
    lip = 13.0 if n < 5 else 11.0
    deep = span * 0.72 - lip
    for i in range(n):
        y = first + span * i + (0 if stool else span * 0.1)
        b, f = across(y) - w * 0.1, across(y + deep) + w * 0.35
        surface = _quad((200 - b, y), (200 + b, y), (200 + f, y + deep), (200 - f, y + deep))
        out.append(
            f'<g class="{TREAD_CLASS}">'
            + _path(surface, _tint(fill.base, 0.2))
            + _lit(
                _quad(
                    (200 - b + 4, y + 2),
                    (200 + b * 0.1, y + 2),
                    (200 - f * 0.2, y + deep - 2),
                    (200 - f + 4, y + deep - 2),
                ),
                0.3,
            )
            + _line(
                " ".join(
                    f"M{200 - b + 12:.1f},{y + deep * t:.1f} L{200 + b - 12:.1f},{y + deep * t:.1f}"
                    for t in (0.3, 0.55, 0.8)
                ),
                1.6,
                ' stroke-opacity="0.5"',
            )
            + _rect(200 - f, y + deep, 2 * f, lip, _shade(fill.base, 0.25), 3)
            + _dim(
                _quad(
                    (200 - f + 3, y + deep + lip * 0.5),
                    (200 + f - 3, y + deep + lip * 0.5),
                    (200 + f - 3, y + deep + lip - 1),
                    (200 - f + 3, y + deep + lip - 1),
                ),
                0.25,
            )
            + "</g>"
        )
    if not stool:
        c = half + 18
        out += [
            _path(
                _quad((200 - c + 14, 34), (200 + c - 14, 34), (200 + c, 66), (200 - c, 66)),
                _tint(fill.base, 0.25),
            ),
            _lit(_quad((200 - c + 18, 37), (210, 37), (180, 63), (200 - c + 8, 63)), 0.32),
            _rect(200 - c, 66, 2 * c, 20, _shade(fill.base, 0.25), 4),
            _rect(176, 44, 48, 10, GRIP, 5, 1.8),
        ]
    return _label(out, label)


def _probe(x: float, y: float, h: float, fill: str) -> list[str]:
    """A test probe standing on its tip: its lead's sleeve, its handle and its guard."""
    return [
        _rect(x - 2.5, y + h - 30, 5, 28, METAL, 2, 1.4),
        _path(
            f"M{x - 8:.1f},{y + 8:.1f} Q{x:.1f},{y - 6:.1f} {x + 8:.1f},{y + 8:.1f} L{x + 14:.1f},{y + 36:.1f} L{x + 12:.1f},{y + h - 44:.1f} L{x + 6:.1f},{y + h - 24:.1f} L{x - 6:.1f},{y + h - 24:.1f} L{x - 12:.1f},{y + h - 44:.1f} L{x - 14:.1f},{y + 36:.1f} Z",
            fill,
        ),
        _lit(
            _quad((x - 9, y + 34), (x - 3, y + 34), (x - 3, y + h - 46), (x - 8, y + h - 46)), 0.35
        ),
        _rect(x - 17, y + h - 56, 34, 9, fill, 4, 1.8),
    ]


def volt_meter(paint: str, fill: Fill, label: str | None, form: str = "handheld") -> list[str]:
    """A volt meter: a body with a display and a dial; ``handheld`` has two probe leads, ``clamp`` a jaw on top."""
    clamp = form == "clamp"
    top, foot = (136.0, 356.0) if clamp else (34.0, 356.0)
    h = foot - top
    x0, x1 = (88.0, 312.0) if clamp else (92.0, 308.0)
    inset = 20.0
    dy, dh = top + inset + (0 if clamp else 12), 62.0 if clamp else 84.0
    cy, r = (top + 152, 48.0) if clamp else (top + 196, 62.0)
    out = [
        _rect(x0, top, x1 - x0, h, _shade(fill.base, 0.35), 30),
        _rect(x0 + 10, top + 8, x1 - x0 - 20, h - 16, paint, 24, 2),
        _lit(
            _quad(
                (x0 + 14, top + 34),
                (x0 + 60, top + 12),
                (x0 + 96, top + 12),
                (x0 + 40, foot - 40),
                (x0 + 14, foot - 40),
            ),
            0.28,
        ),
        _dim(
            _quad(
                (x1 - 30, top + 20),
                (x1 - 13, top + 34),
                (x1 - 13, foot - 34),
                (x1 - 50, foot - 13),
                (x0 + 60, foot - 13),
                (x1 - 46, foot - 40),
            ),
            0.18,
        ),
        _rect(x0 + 26, dy - 6, x1 - x0 - 52, dh + 12, GRIP, 8, 2),
        _rect(x0 + 36, dy, x1 - x0 - 72, dh, "#cfe3ee", 5, 1.6),
        _line(
            f"M{x0 + 52:.1f},{dy + dh * 0.36:.1f} L{x1 - 60:.1f},{dy + dh * 0.36:.1f} M{x0 + 52:.1f},{dy + dh * 0.7:.1f} L{x1 - 96:.1f},{dy + dh * 0.7:.1f}",
            6,
        ),
        _lit(
            _quad(
                (x0 + 40, dy + 4), (x0 + 90, dy + 4), (x0 + 62, dy + dh - 4), (x0 + 40, dy + dh - 4)
            ),
            0.45,
        ),
        _ell(200, cy, r, r, GRIP, 2),
        _ell(200, cy, r * 0.72, r * 0.72, _shade(GRIP, 0.2), 1.6),
        _line(
            " ".join(
                f"M{200 + r * 0.8 * a:.1f},{cy + r * 0.8 * b:.1f} L{200 + r * 0.93 * a:.1f},{cy + r * 0.93 * b:.1f}"
                for a, b in (
                    (-1, 0),
                    (-0.71, -0.71),
                    (0, -1),
                    (0.71, -0.71),
                    (1, 0),
                    (0.71, 0.71),
                    (-0.71, 0.71),
                )
            ),
            2.4,
            "",
            "#ffffff",
        ),
        _path(
            f"M{200 - r * 0.16:.1f},{cy + r * 0.6:.1f} L{200 - r * 0.16:.1f},{cy - r * 0.5:.1f} L200,{cy - r * 0.66:.1f} L{200 + r * 0.16:.1f},{cy - r * 0.5:.1f} L{200 + r * 0.16:.1f},{cy + r * 0.6:.1f} Z",
            _tint(GRIP, 0.25),
            1.6,
        ),
        _lit(
            _quad(
                (200 - r * 0.5, cy - r * 0.5),
                (200 - r * 0.2, cy - r * 0.64),
                (200 - r * 0.2, cy + r * 0.2),
                (200 - r * 0.5, cy + r * 0.3),
            ),
            0.2,
        ),
    ]
    if clamp:
        out[:0] = [
            _path("M128,140 Q92,30 196,32 L196,58 Q136,58 160,140 Z", _shade(fill.base, 0.2)),
            _path("M272,140 Q308,30 204,32 L204,58 Q264,58 240,140 Z", _shade(fill.base, 0.2)),
            _lit("M128,110 Q112,44 180,40 L180,48 Q128,54 140,112 Z", 0.35),
            _dim("M262,134 Q284,74 250,58 Q296,70 270,134 Z", 0.2),
        ]
        out += [
            _path("M84,170 L66,178 Q58,182 58,194 L58,236 L72,236 L72,200 L90,192 Z", GRIP),
        ]
    else:
        out += [
            _ell(156, 326, 10, 10, "#c8322b", 2),
            _ell(200, 326, 10, 10, GRIP, 2),
            _ell(244, 326, 10, 10, GRIP, 2),
            _line("M92,110 Q60,100 60,130", 5, "", "#c8322b"),
            _line("M308,110 Q340,100 340,130", 5),
            *_probe(60, 128, 220, "#c8322b"),
            *_probe(340, 128, 220, GRIP),
        ]
    return _label(out, label)


SHAPES = {
    "drill_driver": drill_driver, "combi_drill": combi_drill, "hammer_drill": hammer_drill,
    "corded_drill": corded_drill, "impact_driver": impact_driver, "sds_drill": sds_drill,
    "drill_bit_set": drill_bit_set, "tool_kit": tool_kit, "step_ladder": step_ladder,
    "volt_meter": volt_meter,
}  # fmt: skip
register(SHAPES)
