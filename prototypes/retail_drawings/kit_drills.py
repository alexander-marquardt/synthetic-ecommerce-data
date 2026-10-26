"""Drill, driver, bit set, tool kit and step ladder shapes for the retail drawing kit (gen#191).

Each type of the DIY drill family has its own flat drawing in the kit's house style: outlines in
the kit's ink, the record's fill (color and pattern) on the tool's body.

==============  ==========================================  ==========================
shape           draws                                       params
==============  ==========================================  ==========================
drill_driver    a pistol body, a keyless chuck and a        pack (compact, standard,
                battery pack under the grip                 large)
combi_drill     a drill driver with a mode ring behind      pack, and always a
                the chuck and a hammer mark on the body     mode ring
hammer_drill    a long body with a side handle and a        power (cordless, corded)
                depth rod; a battery or a cable and plug
corded_drill    a pistol body with a keyed chuck and a      handle (pistol, side)
                cable and plug; no battery
impact_driver   a short stubby body with a hex collet       batteries (0, 1, 2)
                and a battery beside it per battery
sds_drill       a long barrel body with a D-handle and      power (corded, cordless)
                an SDS chuck with two grooves
drill_bit_set   an open case holding a row of bits of       shank (round, hex, sds),
                the set's shank                             bits (3 to 13)
tool_kit        a carry case or a bag with a hammer,        case (case, bag)
                pliers, a screwdriver and a tape on top
step_ladder     an A-frame with one tread per step          steps (2 to 5), kind
                                                            (stool, ladder)
==============  ==========================================  ==========================

A drawing never prints a voltage, a wattage or a piece count: the title says it and a style's
SKUs share one image. Every param is a string with a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import Fill, _highlight, _line, _path, _shade, _tint, register
from kit_sports import POLE, _ell, _label, _rect

METAL = "#aeb4bb"
GRIP = "#3a3f47"
#: Battery pack height by the ``pack`` param: a bigger voltage is a bigger pack.
PACK_H = {"compact": 30, "standard": 42, "large": 56}
#: Classes a test counts against the record.
BATTERY_CLASS = "battery"
TREAD_CLASS = "tread"
BIT_CLASS = "bit"
CABLE_CLASS = "cable"


def _battery(x: float, y: float, w: float, h: float, fill: str) -> str:
    return (
        f'<g class="{BATTERY_CLASS}">'
        + _rect(x, y, w, h, fill, 8)
        + _line(f"M{x + 8:.1f},{y + h / 2:.1f} L{x + w - 8:.1f},{y + h / 2:.1f}", 1.6)
        + "</g>"
    )


def _chuck(x: float, y: float, keyed: bool = False) -> list[str]:
    out = [
        _rect(x, y - 15, 36, 30, METAL, 5),
        _path(
            f"M{x + 36:.1f},{y - 4:.1f} L{x + 82:.1f},{y - 2:.1f} L{x + 82:.1f},{y + 2:.1f} L{x + 36:.1f},{y + 4:.1f} Z",
            METAL,
            1.6,
        ),
    ]
    out.append(
        _line(
            f"M{x + 12:.1f},{y - 15:.1f} L{x + 12:.1f},{y + 15:.1f} M{x + 24:.1f},{y - 15:.1f} L{x + 24:.1f},{y + 15:.1f}",
            1.4,
        )
    )
    if keyed:
        out.append(
            _path(
                f"M{x + 6:.1f},{y - 15:.1f} L{x + 10:.1f},{y - 30:.1f} L{x + 18:.1f},{y - 30:.1f} L{x + 22:.1f},{y - 15:.1f}",
                GRIP,
                1.6,
            )
        )
    return out


def _pistol(paint: str, pack_h: float, keyed: bool = False) -> list[str]:
    """The pistol body shared in outline by the drills: a barrel, a grip and a trigger."""
    return [
        *_chuck(268, 160, keyed),
        _path(
            "M80,134 Q80,120 100,120 L262,120 Q276,120 276,134 L276,186 Q276,200 262,200 L214,200 L228,290 L172,290 L152,200 L100,200 Q80,200 80,186 Z",
            paint,
        ),
        _path("M178,210 L190,210 L196,244 L184,244 Z", GRIP, 1.4),
        _highlight("M96,130 L248,130", 4, 0.45),
    ]


def drill_driver(paint: str, fill: Fill, label: str | None, pack: str = "standard") -> list[str]:
    """A cordless drill driver: a pistol body and a battery pack whose height follows ``pack``."""
    h = PACK_H.get(pack.lower(), 42)
    out = _pistol(paint, h)
    out.insert(0, _battery(150, 290, 96, h, _shade(fill.base, 0.35)))
    out.append(_line("M92,150 L236,150", 1.4, ' stroke-dasharray="6 4"'))
    return _label(out, label)


def combi_drill(paint: str, fill: Fill, label: str | None, pack: str = "standard") -> list[str]:
    """A combi drill: a drill driver with a mode ring behind the chuck and a hammer mark."""
    h = PACK_H.get(pack.lower(), 42)
    out = _pistol(paint, h)
    out.insert(0, _battery(150, 290, 96, h, _shade(fill.base, 0.35)))
    out += [
        _rect(246, 128, 24, 64, GRIP, 4),
        _line("M252,134 L252,186 M258,134 L258,186 M264,134 L264,186", 1.2, "", "#ffffff"),
        _path(
            "M104,150 L140,150 L140,158 L126,158 L126,182 L118,182 L118,158 L104,158 Z",
            _tint(fill.base, 0.4),
            1.6,
        ),
    ]
    return _label(out, label)


def hammer_drill(paint: str, fill: Fill, label: str | None, power: str = "cordless") -> list[str]:
    """A hammer drill: a long body, a side handle and a depth rod; cordless it carries a battery,
    corded a cable and a plug."""
    out = [
        *_chuck(286, 150),
        _path(
            "M60,130 Q60,114 80,114 L282,114 Q296,114 296,130 L296,176 Q296,190 282,190 L226,190 L240,282 L184,282 L164,190 L80,190 Q60,190 60,176 Z",
            paint,
        ),
        _path("M236,190 L254,190 L270,236 L256,242 Z", GRIP, 1.4),
        _path("M256,100 L274,100 L274,114 L256,114 Z", METAL, 1.6),
        _path("M300,118 L336,86 L346,96 L310,128 Z", GRIP, 1.6),
        _line("M330,150 L330,214 M330,214 L372,214", 4, "", POLE),
        _highlight("M76,124 L270,124", 4, 0.45),
    ]
    if power.lower() == "corded":
        out += [
            f'<g class="{CABLE_CLASS}">'
            + _line("M212,282 C212,330 120,320 110,350 C104,372 70,364 56,348", 4)
            + _rect(30, 336, 28, 26, GRIP, 4)
            + "</g>",
            _line("M34,344 L22,344 M34,354 L22,354", 3),
        ]
    else:
        out.insert(0, _battery(170, 282, 82, 50, _shade(fill.base, 0.35)))
    return _label(out, label)


def corded_drill(paint: str, fill: Fill, label: str | None, handle: str = "pistol") -> list[str]:
    """A corded drill: a pistol body with a keyed chuck and a cable ending in a plug; ``side``
    adds a side handle."""
    out = [
        *_pistol(paint, 0, keyed=True),
        f'<g class="{CABLE_CLASS}">'
        + _line("M200,290 C200,336 120,330 108,356 C102,372 76,370 62,356", 4)
        + _rect(36, 342, 28, 26, GRIP, 4)
        + "</g>",
        _line("M40,350 L26,350 M40,360 L26,360", 3),
    ]
    if handle.lower() == "side":
        out += [_path("M270,118 L296,84 L308,92 L286,128 Z", GRIP, 1.6)]
    return _label(out, label)


def impact_driver(paint: str, fill: Fill, label: str | None, batteries: str = "1") -> list[str]:
    """An impact driver: a short stubby body on a hex collet; ``batteries`` 0 is a bare tool, 1 a pack
    on the grip, 2 adds a spare pack beside it."""
    n = max(0, min(2, int(batteries or 0)))
    out = [
        _path(
            "M118,120 L118,98 L246,98 Q262,98 262,114 L262,196 Q262,210 246,210 L214,210 L224,288 L176,288 L164,210 L134,210 Q118,210 118,194 Z",
            paint,
        ),
        _rect(262, 132, 44, 34, METAL, 5),
        _path("M306,140 L346,140 L346,158 L306,158 Z", METAL, 1.6),
        _line("M346,142 L346,156 M334,142 L334,156 M322,142 L322,156", 1.4),
        _path("M186,214 L198,214 L202,244 L190,244 Z", GRIP, 1.4),
        _highlight("M132,108 L240,108", 4, 0.45),
    ]
    if n:
        out.append(_battery(168, 288, 64, 36, _shade(fill.base, 0.35)))
    for i in range(n - 1):
        out.append(_battery(40 + 70 * i, 300, 62, 56, _shade(fill.base, 0.35)))
    return _label(out, label)


def sds_drill(paint: str, fill: Fill, label: str | None, power: str = "corded") -> list[str]:
    """An SDS hammer drill: a long barrel body, a D-handle at the back, an SDS chuck with two
    grooves; corded it ends in a cable, cordless it carries a battery."""
    out = [
        _path(
            "M96,126 Q96,110 116,110 L268,110 Q284,110 284,126 L284,176 Q284,190 268,190 L116,190 Q96,190 96,176 Z",
            paint,
        ),
        _path(
            "M96,140 L40,140 Q24,140 24,156 L24,244 Q24,260 40,260 L72,260 L72,240 L48,240 L48,160 L96,160",
            paint,
        ),
        _path("M236,190 L252,190 L264,236 L250,240 Z", GRIP, 1.4),
        _rect(284, 132, 40, 44, METAL, 5),
        _path("M324,148 L372,150 L372,160 L324,162 Z", METAL, 1.6),
        _line("M300,132 L300,176 M312,132 L312,176", 2),
        _highlight("M112,120 L262,120", 4, 0.45),
    ]
    if power.lower() == "cordless":
        out.insert(0, _battery(130, 190, 90, 46, _shade(fill.base, 0.35)))
    else:
        out += [
            f'<g class="{CABLE_CLASS}">'
            + _line("M40,260 C40,310 120,300 130,340 C134,364 170,366 190,352", 4)
            + _rect(188, 338, 28, 26, GRIP, 4)
            + "</g>"
        ]
    return _label(out, label)


def drill_bit_set(
    paint: str, fill: Fill, label: str | None, shank: str = "round", bits: str = "9"
) -> list[str]:
    """A drill bit set: an open case holding one bit per slot; the shank is round, hex (a flat
    hex tip) or SDS (a grooved tip)."""
    n = max(3, min(13, int(bits or 9)))
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


def tool_kit(paint: str, fill: Fill, label: str | None, case: str = "case") -> list[str]:
    """A tool kit: a hard carry case (or a soft bag) with a hammer, pliers, a screwdriver and a
    tape measure laid on it."""
    if case.lower() == "bag":
        out = [
            _path(
                "M60,214 Q60,196 82,196 L318,196 Q340,196 340,214 L350,320 Q350,336 332,336 L68,336 Q50,336 50,320 Z",
                paint,
            ),
            _path("M130,196 Q130,150 200,150 Q270,150 270,196", "none", 5),
            _line("M60,252 L340,252", 1.6),
        ]
    else:
        out = [
            _rect(50, 190, 300, 150, paint, 10),
            _rect(180, 176, 40, 20, GRIP, 5),
            _line("M50,262 L350,262", 1.6),
            _rect(66, 270, 36, 14, METAL, 3),
            _rect(298, 270, 36, 14, METAL, 3),
        ]
    out += [
        _path("M92,150 L140,150 L140,170 L92,170 Z", METAL, 1.6),
        _line("M116,170 L116,214", 7),
        _path("M170,136 L170,186 L184,186 L184,136 Q184,124 177,124 Q170,124 170,136 Z", GRIP, 1.6),
        _line("M177,186 L177,196", 3),
        _path("M230,132 L270,132 L280,166 L220,166 Z", _tint(fill.base, 0.35), 1.6),
        _ell(310, 150, 26, 26, METAL, 1.8),
        _ell(310, 150, 10, 10, _tint(fill.base, 0.5), 1.4),
    ]
    return _label(out, label)


def step_ladder(
    paint: str, fill: Fill, label: str | None, steps: str = "3", kind: str = "ladder"
) -> list[str]:
    """A step ladder: an A-frame with one tread per step. A ``stool`` is wider and has a top
    step and a hand grip."""
    n = max(2, min(5, int(steps or 3)))
    stool = kind.lower() == "stool"
    top = 110 if not stool else 150
    foot = 350
    half = 86 if not stool else 112
    out = [
        _path(
            f"M{200 - half + 30:.1f},{top:.1f} L{200 - half - 30:.1f},{foot:.1f} L{200 - half - 10:.1f},{foot:.1f} L{200 - half + 46:.1f},{top:.1f} Z",
            paint,
        ),
        _path(
            f"M{200 + half - 46:.1f},{top:.1f} L{200 + half + 10:.1f},{foot:.1f} L{200 + half + 30:.1f},{foot:.1f} L{200 + half - 30:.1f},{top:.1f} Z",
            paint,
        ),
        _path(
            f"M{200 - half:.1f},{top - 14:.1f} L{200 + half:.1f},{top - 14:.1f} L{200 + half:.1f},{top:.1f} L{200 - half:.1f},{top:.1f} Z",
            _tint(fill.base, 0.25),
        ),
    ]
    span = (foot - top - 30) / n
    for i in range(n):
        y = top + 30 + span * i
        w = half + 8 + (y - top) * 0.32
        out.append(
            f'<g class="{TREAD_CLASS}">'
            + _path(
                f"M{200 - w:.1f},{y:.1f} L{200 + w:.1f},{y:.1f} L{200 + w:.1f},{y + 12:.1f} L{200 - w:.1f},{y + 12:.1f} Z",
                _tint(fill.base, 0.2),
            )
            + "</g>"
        )
    if stool:
        out.append(_line(f"M{200 - 40},{top - 14} Q200,{top - 48} {200 + 40},{top - 14}", 6))
    else:
        out.append(
            _line(
                f"M{200 + half + 6:.1f},{top + 10:.1f} L{200 + half + 6:.1f},{foot - 40:.1f}",
                2.4,
                ' stroke-dasharray="8 6"',
            )
        )
    return _label(out, label)


SHAPES = {
    "drill_driver": drill_driver, "combi_drill": combi_drill, "hammer_drill": hammer_drill,
    "corded_drill": corded_drill, "impact_driver": impact_driver, "sds_drill": sds_drill,
    "drill_bit_set": drill_bit_set, "tool_kit": tool_kit, "step_ladder": step_ladder,
}  # fmt: skip
register(SHAPES)
