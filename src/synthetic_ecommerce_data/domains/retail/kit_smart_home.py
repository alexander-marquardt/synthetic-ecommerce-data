"""Smart home for the retail drawing kit (gen#956): smart plugs, smart bulbs, doorbell cameras.

===============  ===========================================  ===================================
shape            draws                                        params
===============  ===========================================  ===================================
smart_plug       a plug body with its socket, a button and a  plug_form (mini, dual outlet,
                 status light: small and square, wide with    outdoor)
                 two sockets, or tall with a hinged cover
                 and a cable
smart_bulb       a bulb: a round globe on a threaded screw    bulb_fitting (e27, e14, b22,
                 base (narrow for e14), on a smooth bayonet   gu10)
                 base with two
                 side pins, or a spot cone on two pins
doorbell_camera  a tall doorbell with its camera lens and a   doorbell_power (battery, wired)
                 lit button, and a battery gauge or two wires
                 out of its foot
===============  ===========================================  ===================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a plug's ``plug_form`` or a bulb's ``bulb_fitting`` draws what it states (gen#512).
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

#: A socket's holes and a lens's dark glass.
MESH = "#3a3b40"
#: A bulb base's metal, a status light's green and a ring light's blue.
STEEL = "#c3c7cd"
LIGHT = "#2fbf71"
RING = "#5fb6e8"


def _socket(cx: float, cy: float, fill: Fill) -> list[str]:
    """One round socket face with its two holes."""
    return [
        _ell(cx, cy, 40, 40, _shade(fill.base, 0.15), LW_DETAIL),
        _ell(cx - 14, cy, 5, 7, MESH, 1.2),
        _ell(cx + 14, cy, 5, 7, MESH, 1.2),
    ]


def smart_plug(paint: str, fill: Fill, label: str | None, plug_form: str = "mini") -> list[str]:
    """A smart plug by ``plug_form``: one socket, two sockets, or a covered socket and a cable."""
    if plug_form == "dual outlet":
        out = [_rect(70, 110, 260, 180, paint, 30)]
        out += [*_socket(145, 195, fill), *_socket(255, 195, fill)]
        out += [_rect(185, 122, 30, 12, _shade(fill.base, 0.3), 5, LW_DETAIL)]
        out += [_ell(200, 268, 5, 5, LIGHT, 1.2), _highlight("M84,140 L84,260", 4, 0.5)]
        return _label(out, label)
    if plug_form == "outdoor":
        out = [
            _rect(120, 70, 160, 250, paint, 24),
            *_socket(200, 200, fill),
            _rect(136, 128, 128, 40, _shade(fill.base, 0.25), 12, LW_DETAIL),
            _line("M200,320 C200,352 236,360 270,364", 5.0),
            _ell(200, 292, 5, 5, LIGHT, 1.2),
            _highlight("M132,100 L132,290", 4, 0.5),
        ]
        return _label(out, label)
    out = [
        _rect(130, 110, 140, 180, paint, 30),
        *_socket(200, 195, fill),
        _rect(185, 122, 30, 12, _shade(fill.base, 0.3), 5, LW_DETAIL),
        _ell(200, 266, 5, 5, LIGHT, 1.2),
        _highlight("M144,140 L144,260", 4, 0.5),
    ]
    return _label(out, label)


def smart_bulb(paint: str, fill: Fill, label: str | None, bulb_fitting: str = "e27") -> list[str]:
    """A smart bulb by ``bulb_fitting``: a globe on a screw or bayonet base, or a spot on pins."""
    if bulb_fitting == "gu10":
        out = [
            _path("M110,100 L290,100 L240,250 L160,250 Z", paint),
            _ell(200, 100, 90, 20, _tint(fill.base, 0.5), LW_DETAIL),
            _rect(176, 250, 12, 44, STEEL, 3, LW_DETAIL),
            _rect(212, 250, 12, 44, STEEL, 3, LW_DETAIL),
            _ell(182, 296, 9, 6, STEEL, LW_DETAIL),
            _ell(218, 296, 9, 6, STEEL, LW_DETAIL),
            _highlight("M136,112 L172,234", 4, 0.5),
        ]
        return _label(out, label)
    out = [
        _path(
            "M168,226 C120,196 104,160 104,130 C104,74 148,40 200,40 C252,40 296,74 296,130 "
            "C296,160 280,196 232,226 Z",
            paint,
        ),  # fmt: skip
        _rect(166, 222, 68, 22, _shade(fill.base, 0.15), 6, LW_DETAIL),
    ]
    if bulb_fitting == "b22":
        out += [
            _rect(170, 244, 60, 50, STEEL, 8, LW_DETAIL),
            _rect(158, 262, 12, 10, STEEL, 2, LW_DETAIL),
            _rect(230, 262, 12, 10, STEEL, 2, LW_DETAIL),
            _ell(186, 300, 7, 5, MESH, LW_DETAIL),
            _ell(214, 300, 7, 5, MESH, LW_DETAIL),
        ]
    else:
        half = 18 if bulb_fitting == "e14" else 30
        out += [_rect(200 - half, 244, 2 * half, 56, STEEL, 8, LW_DETAIL)]
        out += [_line(f"M{202 - half},{y} L{198 + half},{y + 6}", 1.6, "", _shade(STEEL, 0.4))
                for y in (252, 266, 280)]  # fmt: skip
        out += [_ell(200, 306, half / 2, 8, MESH, LW_DETAIL)]
    out.append(_highlight("M132,140 C132,104 152,80 180,70", 5, 0.5))
    return _label(out, label)


def doorbell_camera(paint: str, fill: Fill, label: str | None,
                    doorbell_power: str = "battery") -> list[str]:  # fmt: skip
    """A video doorbell: lens, lit button and, by ``doorbell_power``, a battery gauge or wires."""
    out = [
        _rect(140, 40, 120, 300, paint, 44),
        _ell(200, 100, 32, 32, MESH, LW_DETAIL),
        _ell(200, 100, 13, 13, _tint(MESH, 0.3), LW_DETAIL),
        _ell(200, 262, 40, 40, RING, LW_DETAIL),
        _ell(200, 262, 30, 30, _shade(fill.base, 0.2), LW_DETAIL),
    ]
    if doorbell_power == "wired":
        out += [
            _line("M186,340 C186,366 166,374 150,380", 3.0, "", "#b03a2e"),
            _line("M214,340 C214,366 234,374 250,380", 3.0),
        ]
    else:
        out += [_rect(170, 168, 60, 24, _tint(fill.base, 0.6), 5, LW_DETAIL)]
        out += [_rect(176 + i * 16, 173, 12, 14, LIGHT, 2, 1.0) for i in range(3)]
    out.append(_highlight("M152,80 L152,300", 4, 0.5))
    return _label(out, label)


SHAPES = {"smart_plug": smart_plug, "smart_bulb": smart_bulb, "doorbell_camera": doorbell_camera}
register(SHAPES)
