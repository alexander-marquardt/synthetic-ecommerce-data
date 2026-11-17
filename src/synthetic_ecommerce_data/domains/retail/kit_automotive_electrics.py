"""Car electrics shapes for the retail drawing kit (gen#970, slice 2).

The Automotive department's electrics that no other shape draws: each is drawn as what it is, so a
jump starter never reads as a power bank and a phone mount never reads as a phone case. Outlines
are the kit's ink, and the record's fill paints the main surface. Motor oil and coolant use slice
1's ``fluid_jug``; a car charger uses the electronics kit's ``charger`` with ``kind="car"``.

=============  ==============================================  ==================================
shape          draws                                           params
=============  ==============================================  ==================================
jump_starter   a pack with a screen and two clamps on their    style (compact, jump_box)
               cables: a slim lithium pack, or a box with a
               carry handle
tire_inflator  an inflator with a gauge and a coiled hose:     style (box, handheld)
               a box on the floor, or a handheld grip
phone_mount    a phone held by a mount: a vent clip, a         style (vent, suction, cup_holder,
               suction cup on an arm, a cup holder base on a   magnetic)
               neck, or a round magnetic pad
=============  ==============================================  ==================================

A drawing never prints a peak current, a pressure or a pack size: a style's SKUs share one image.
Every param is a string with a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import POLE, _label, _rect

#: A dark screen or a phone's glass.
GLASS = "#1f2a36"
#: The positive clamp's red and the negative clamp's black.
CLAMP_RED, CLAMP_BLACK = "#c8322b", "#2a2a2e"


def _circle(cx: float, cy: float, r: float, fill: str, width: float = LW) -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _clamps() -> list[str]:
    """Two cables from the pack's foot, each to its clamp: red on the left, black on the right."""
    out = []
    for cable, jaw, color in (
        ("M180,318 Q150,350 104,346", "M64,330 L112,330 L118,346 L112,362 L64,362 Z", CLAMP_RED),
        ("M220,318 Q250,350 296,346", "M288,330 L336,330 L336,362 L288,362 L282,346 Z", CLAMP_BLACK),
    ):
        out += [
            _line(cable, LW + 5, stroke=INK),
            _line(cable, LW + 1, stroke=color),
            _path(jaw, color),
        ]
    return out


def jump_starter(paint: str, fill: Fill, label: str | None, style: str = "compact") -> list[str]:
    """A jump starter: a slim ``compact`` lithium pack, or a ``jump_box`` with a carry handle."""
    dark = _shade(fill.base, 0.35)
    if style.lower() == "jump_box":
        out = [
            _line("M150,130 L150,96 Q150,76 170,76 L230,76 Q250,76 250,96 L250,130", LW + 9, stroke=INK),
            _line("M150,130 L150,96 Q150,76 170,76 L230,76 Q250,76 250,96 L250,130", LW + 4, stroke=dark),
            _rect(96, 124, 208, 196, paint, 16),
            _rect(122, 150, 156, 56, dark, 8),
            _circle(150, 262, 18, CLAMP_RED, LW_DETAIL),
            _circle(250, 262, 18, CLAMP_BLACK, LW_DETAIL),
            _rect(176, 246, 48, 30, GLASS, 4, LW_DETAIL),
        ]
    else:
        out = [
            _rect(132, 96, 136, 222, paint, 26),
            _rect(152, 124, 96, 46, GLASS, 6, LW_DETAIL),
            *[_circle(162 + 25 * i, 196, 6, "#2fbf71" if i < 3 else _tint(fill.base, 0.5), 1.4) for i in range(4)],
            _rect(176, 226, 48, 36, dark, 8, LW_DETAIL),
            _highlight("M146,120 L146,290", 4, 0.4),
        ]
    return _label(out + _clamps(), label)


def tire_inflator(paint: str, fill: Fill, label: str | None, style: str = "box") -> list[str]:
    """A tire inflator with a gauge and a coiled hose: a ``box`` on the floor or a ``handheld`` grip."""
    dark = _shade(fill.base, 0.3)
    hose = "M262,214 Q300,214 310,250 Q318,280 296,292 Q276,300 290,318 Q306,336 286,350 L262,356"
    if style.lower() == "handheld":
        out = [
            _path("M150,200 L190,200 L206,350 Q190,362 166,358 Z", dark),
            _rect(110, 110, 160, 104, paint, 22),
            _rect(134, 128, 72, 44, GLASS, 6, LW_DETAIL),
            _line("M222,138 L250,138 M222,156 L250,156", LW_DETAIL),
            _line("M270,160 L262,214", LW + 1),
        ]
    else:
        out = [
            _rect(96, 150, 166, 170, paint, 20),
            _circle(160, 230, 42, _tint(fill.base, 0.65), LW),
            _line("M160,230 L182,206", LW, stroke=CLAMP_RED),
            _line("M130,230 L136,230 M160,200 L160,206 M190,230 L184,230", LW_DETAIL),
            _rect(212, 196, 34, 64, dark, 6, LW_DETAIL),
            _rect(140, 320, 80, 16, POLE, 4, LW_DETAIL),
        ]
    out += [
        _line(hose, LW + 4, stroke=INK),
        _line(hose, LW, stroke=CLAMP_BLACK),
        _rect(232, 348, 32, 18, POLE, 4, LW_DETAIL),
    ]
    return _label(out, label)


def phone_mount(paint: str, fill: Fill, label: str | None, style: str = "vent") -> list[str]:
    """A phone held by its mount: a ``vent`` clip, a ``suction`` cup, a ``cup_holder`` base or a ``magnetic`` pad."""
    s = style.lower()
    dark = _shade(fill.base, 0.35)
    phone = [_rect(150, 60, 100, 180, GLASS, 14), _highlight("M162,80 L162,220", 3, 0.35)]
    arms = [_rect(138, 120, 16, 64, paint, 6), _rect(246, 120, 16, 64, paint, 6)]
    if s == "magnetic":
        out = [_circle(200, 290, 44, paint), _circle(200, 290, 26, _tint(fill.base, 0.35), LW_DETAIL), _line("M200,246 L200,240", LW + 2), *phone]
    elif s == "suction":
        out = [
            f'<ellipse cx="200" cy="356" rx="70" ry="18" fill="{dark}" stroke="{INK}" stroke-width="{LW}"/>',
            _line("M200,340 Q200,300 230,280 L210,240", LW + 7, stroke=INK),
            _line("M200,340 Q200,300 230,280 L210,240", LW + 3, stroke=paint),
            _rect(176, 226, 48, 22, paint, 6),
            *phone, *arms,
        ]
    elif s == "cup_holder":
        out = [
            _path("M150,360 L160,290 L240,290 L250,360 Q200,372 150,360 Z", paint),
            _line("M160,316 L240,316", LW_DETAIL),
            _line("M200,290 Q180,262 200,244", LW + 6, stroke=INK),
            _line("M200,290 Q180,262 200,244", LW + 2, stroke=dark),
            _rect(176, 226, 48, 22, paint, 6),
            *phone, *arms,
        ]
    else:
        out = [
            _rect(176, 240, 48, 30, paint, 6),
            _line("M186,270 L186,322 M200,270 L200,326 M214,270 L214,322", LW + 2, stroke=INK),
            _line("M120,300 L280,300 M120,318 L280,318", LW_DETAIL, ' stroke-dasharray="6 6"'),
            *phone, *arms,
        ]
    return _label(out, label)


SHAPES = {
    "jump_starter": jump_starter,
    "tire_inflator": tire_inflator,
    "phone_mount": phone_mount,
}
register(SHAPES)
