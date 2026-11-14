"""Gadgets for the retail drawing kit (gen#956, slice 3a): power banks, webcams and smartwatches.

==========  ============================================  ======================================
shape       draws                                         params
==========  ============================================  ======================================
power_bank  a battery brick with four charge lights;      power_bank_form (slim, rugged,
            ``rugged`` adds corner bumpers, ``magnetic``  magnetic), power_bank_charging (usb-c,
            a metal ring; a port and cable for usb-c,     wireless)
            charge waves on the face for wireless
webcam      a camera on a monitor clip; ``streaming`` is  webcam_use (streaming, conference),
            a round body, ``conference`` a wide bar with  webcam_feature (ring light, privacy
            speaker grilles; a lit ring around the lens   shutter)
            or a slide shutter above it
smartwatch  a strap, a case with a crown and a dark       smartwatch_face (round, square),
            screen; a map pin on screen for gps, a red    smartwatch_network (gps, cellular)
            crown for cellular
==========  ============================================  ======================================

Each param's values are the lower-cased attribute values of the spec rows. A derived style that
changes any of these params draws what it states (gen#512).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: A lens's and a screen's dark glass, a clip's and a case's metal.
MESH = "#3a3b40"
STEEL = "#c3c7cd"
#: A charge light's green, a screen's cyan, a ring light's warm white and a cellular crown's red.
LIGHT = "#2fbf71"
GLOW = "#5fd3e8"
WARM = "#fff1c2"
CROWN = "#c8312e"


def power_bank(paint: str, fill: Fill, label: str | None, power_bank_form: str = "slim",
               power_bank_charging: str = "usb-c") -> list[str]:  # fmt: skip
    """A power bank by ``power_bank_form``: a port and cable for usb-c, waves for wireless."""
    if power_bank_form == "rugged":
        x, y, w, h, r = 112.0, 64.0, 176.0, 272.0, 26.0
    elif power_bank_form == "magnetic":
        x, y, w, h, r = 122.0, 90.0, 156.0, 220.0, 34.0
    else:
        x, y, w, h, r = 136.0, 70.0, 128.0, 260.0, 18.0
    out = [_rect(x, y, w, h, paint, r)]
    if power_bank_form == "rugged":
        out += [_rect(cx, cy, 34, 34, _shade(fill.base, 0.45), 10, LW_DETAIL)
                for cx in (x - 6, x + w - 28) for cy in (y - 6, y + h - 28)]  # fmt: skip
    if power_bank_form == "magnetic":
        out.append(_ell(200, 180, 48, 48, "none", 6.0))
        out.append(_ell(200, 180, 48, 48, "none", 3.0, ' stroke-opacity="0.6"'))
    out += [_rect(168 + 18 * i, y + h - 34, 12, 8, LIGHT, 2, 1.0) for i in range(4)]
    if power_bank_charging == "wireless":
        out += [_line(f"M{200 - s},{150 - s / 2} C{200 - s / 2},{150 - s} {200 + s / 2},{150 - s} "
                      f"{200 + s},{150 - s / 2}", 3.0) for s in (14, 26, 38)]  # fmt: skip
    else:
        out += [_rect(186, y - 8, 28, 10, MESH, 3, LW_DETAIL),
                _line(f"M200,{y - 8} C200,{y - 40} 250,{y - 44} 290,{y - 52}", 5.0)]  # fmt: skip
    out.append(
        _highlight(
            f"M{x + 14},{y + 40} C{x + 16},{y + 26} {x + 24},{y + 16} {x + 40},{y + 14}", 4, 0.5
        )
    )
    return _label(out, label)


def webcam(paint: str, fill: Fill, label: str | None, webcam_use: str = "streaming",
           webcam_feature: str = "privacy shutter") -> list[str]:  # fmt: skip
    """A webcam on a monitor clip by ``webcam_use``, with a ring light or a privacy shutter."""
    out = [
        _rect(120, 280, 160, 24, MESH, 4, LW_DETAIL),
        _path("M176,230 L224,230 L232,282 L168,282 Z", _shade(fill.base, 0.35)),
    ]
    if webcam_use == "conference":
        out += [_rect(64, 140, 272, 96, paint, 40)]
        out += [_rect(gx, 166, 40, 44, _shade(fill.base, 0.4), 10, LW_DETAIL) for gx in (88, 272)]
        lens = 30.0
    else:
        out.append(_ell(200, 188, 86, 76, paint))
        lens = 38.0
    if webcam_feature == "ring light":
        out.append(_ell(200, 188, lens + 14, lens + 14, WARM, LW_DETAIL))
    out += [
        _ell(200, 188, lens, lens, MESH, LW_DETAIL),
        _ell(200, 188, lens * 0.45, lens * 0.45, GLOW, 1.0),
    ]
    if webcam_feature == "privacy shutter":
        out.append(_rect(176, 188 - lens - 18, 48, 12, _shade(fill.base, 0.5), 4, LW_DETAIL))
    gloss = (f"M{200 - lens * 0.6},{188 - lens * 0.2} C{200 - lens * 0.5},{188 - lens * 0.6} "
             f"{200 - lens * 0.2},{188 - lens * 0.7} {200},{188 - lens * 0.7}")  # fmt: skip
    out.append(_highlight(gloss, 3, 0.6))
    return _label(out, label)


def smartwatch(paint: str, fill: Fill, label: str | None, smartwatch_face: str = "round",
               smartwatch_network: str = "gps") -> list[str]:  # fmt: skip
    """A smartwatch by ``smartwatch_face``: a map pin on screen for gps, a red crown for cellular
    (``smartwatch_network``)."""
    out = [_rect(162, 30, 76, 340, paint, 26)]
    out += [_ell(200, hy, 4, 4, _shade(fill.base, 0.45), 1.0) for hy in (300, 320, 340)]
    crown = CROWN if smartwatch_network == "cellular" else STEEL
    if smartwatch_face == "square":
        out += [
            _rect(134, 128, 132, 144, STEEL, 30),
            _rect(146, 140, 108, 120, MESH, 22, LW_DETAIL),
        ]
        out.append(_rect(264, 178, 14, 34, crown, 4, LW_DETAIL))
    else:
        out += [_ell(200, 200, 72, 72, STEEL), _ell(200, 200, 58, 58, MESH, LW_DETAIL)]
        out.append(_rect(270, 184, 14, 32, crown, 4, LW_DETAIL))
    out += [
        _line("M200,200 L200,166", 3.0, stroke=GLOW),
        _line("M200,200 L224,212", 3.0, stroke=GLOW),
    ]
    if smartwatch_network == "gps":
        pin = "M200,246 C190,234 186,228 186,222 A14,14 0 1 1 214,222 C214,228 210,234 200,246 Z"
        out.append(_path(pin, LIGHT, LW_DETAIL))
    out.append(_highlight("M150,180 C154,160 166,148 184,144", 4, 0.5))
    return _label(out, label)


SHAPES = {"power_bank": power_bank, "webcam": webcam, "smartwatch": smartwatch}
register(SHAPES)
