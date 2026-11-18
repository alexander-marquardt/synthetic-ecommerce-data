"""The Health department's own shapes: a capped supplement bottle (gen#1028) and first aid
and health monitors (gen#968, slice 2).

=================  ===============================================  ================================
shape              draws                                            params
=================  ===============================================  ================================
supplement_bottle  a capped bottle with a wrapped label: a band in   nutrient, form
                   the nutrient's color, its name, a tablet or a
                   capsule glyph
plaster_box        a carton of plasters with one plaster in front   plaster (fabric, waterproof,
                   of it, drawn by ``plaster``                      clear, blister, sensitive)
first_aid_kit      a first-aid kit in the box's color, with the     case (soft pouch, hard case)
                   white cross on it
thermometer        a digital thermometer with its display           kind (digital stick, ear,
                                                                    forehead)
bp_monitor         a blood-pressure monitor with its display and    fit (upper arm, wrist)
                   its cuff
=================  ===============================================  ================================

Vitamins and minerals drew the retail ``tub`` (a tall tapered open pot), which reads as a paper
cup. The bottle is the colorway's base (white, amber, sage), the screw cap its accent. The
label carries what tells two bottles of one brand apart on a shelf: the nutrient's name, a
band colored by the nutrient (:func:`band_color`), and a glyph by ``form`` (a scored tablet
for ``Tablets``, a two-tone capsule for ``Capsules``). Both are drawing params holding the
attribute values, so a derived style that swaps the nutrient or the form is redrawn.

Each param's values of the slice 2 shapes are the lower-cased attribute values of the spec rows
(``health_rows``), so a derived style that swaps a plaster's type or a thermometer's kind draws
what it states (gen#512). The cross of a first-aid kit is the white one of the first-aid sign,
never a red one.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import zlib

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    PAPER,
    Fill,
    _highlight,
    _line,
    _path,
    _rim,
    _shade,
    _tint,
    _word,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: The label band's colors: a nutrient or mineral picks one by a stable hash of its name, so
#: one nutrient has one color across brands and builds.
BANDS = (
    "#d9532b", "#e8a33a", "#e2c93f", "#7aa846", "#3f9a83", "#3e86c2",
    "#5b5fb8", "#9a58a8", "#c94f7c", "#8a6a4a", "#4a6f80", "#b33a3a",
)  # fmt: skip

#: The bottle's outline: a wide shoulder, a short neck under the cap, a round foot.
_BODY = "M124,186 Q124,152 160,142 L160,128 L240,128 L240,142 Q276,152 276,186 L276,346 A76,17 0 0 1 124,346 Z"
#: The wrapped label: its left and right edges, its top, its height and its band's height.
_LEFT, _RIGHT, _TOP, _HEIGHT, _BAND = 130, 270, 196, 128, 30


def band_color(nutrient: str) -> str:
    """The label band's color for ``nutrient``: one of :data:`BANDS`, by a stable hash."""
    return BANDS[zlib.crc32(nutrient.lower().encode()) % len(BANDS)]


def _wrapped(top: float, height: float) -> str:
    """A strip of the label from ``top`` down ``height``, its edges arcs of the bottle's rim."""
    rx, ry = _rim(76)
    return (
        f"M{_LEFT},{top:g} A{rx:g},{ry:g} 0 0 0 {_RIGHT},{top:g} "
        f"L{_RIGHT},{top + height:g} A{rx:g},{ry:g} 0 0 1 {_LEFT},{top + height:g} Z"
    )


def _glyph(form: str, cx: float, cy: float, color: str) -> str:
    """A scored tablet for ``Tablets``, a two-tone capsule for ``Capsules``, else nothing."""
    kind = form.strip().lower()
    if kind.startswith("tablet"):
        return (
            f'<g class="tablet">'
            f'<ellipse cx="{cx:g}" cy="{cy + 3:g}" rx="14" ry="9" fill="#e4e4e0" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
            f'<ellipse cx="{cx:g}" cy="{cy:g}" rx="14" ry="9" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
            f'<path d="M{cx - 8:g},{cy:g} L{cx + 8:g},{cy:g}" stroke="{INK}" stroke-width="1"/>'
            "</g>"
        )
    if kind.startswith("capsule"):
        left = f"M{cx:g},{cy - 8:g} L{cx - 10:g},{cy - 8:g} A8,8 0 0 0 {cx - 10:g},{cy + 8:g} L{cx:g},{cy + 8:g} Z"
        right = f"M{cx:g},{cy - 8:g} L{cx + 10:g},{cy - 8:g} A8,8 0 0 1 {cx + 10:g},{cy + 8:g} L{cx:g},{cy + 8:g} Z"
        return (
            f'<g class="capsule" transform="rotate(-30 {cx:g} {cy:g})">'
            f'<path d="{left}" fill="{color}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
            f'<path d="{right}" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
            "</g>"
        )
    return ""


def supplement_bottle(
    paint: str, fill: Fill, label: str | None, nutrient: str = "", form: str = ""
) -> list[str]:
    """A capped supplement bottle: the nutrient's band and name and the form's glyph on its label."""
    name = nutrient or label or ""
    color = band_color(name)
    _rx, ry = _rim(76)
    sag = ry * (1 - (1 - ((_RIGHT - _LEFT) / 2 / 76) ** 2) ** 0.5)
    word_y = _TOP + _BAND + sag + 26
    glyph_y = word_y + 36
    ridges = " ".join(f"M{x},86 L{x},124" for x in range(160, 248, 10))
    return [
        f'<path class="bottle" d="{_BODY}" fill="{paint}" stroke="{INK}" stroke-width="{LW}" stroke-linejoin="round"/>',
        _highlight("M134,190 Q136,164 158,152", 5, 0.5),
        f'<rect class="cap" x="148" y="80" width="104" height="50" rx="6" fill="{fill.accent}" stroke="{INK}" stroke-width="{LW}"/>',
        _line(ridges, 1.0, ' stroke-opacity=".5"'),
        f'<path class="label" d="{_wrapped(_TOP, _HEIGHT)}" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<path class="band" d="{_wrapped(_TOP, _BAND)}" fill="{color}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _word(name, 200, word_y, _RIGHT - _LEFT - 16, 26) if name else "",
        _glyph(form, 174, glyph_y, color),
        _word(form, 228, glyph_y, 64, 13, "#5a5f66") if form else "",
    ]


#: A display's glass and its digits.
SCREEN = "#cfe3d4"
DIGITS = "#24323a"
#: The steel tip of a stick thermometer and the grey of a cuff's tube.
STEEL = "#c3c7cd"
TUBE = "#7d838c"
#: A plaster's color by its type, and the pad in its middle.
PLASTER = {
    "fabric": "#d9a77c",
    "waterproof": "#e6c3a2",
    "clear": "#f1ece4",
    "blister": "#f0dcc4",
    "sensitive": "#f3d6c2",
}
PAD = "#f8f4ee"
#: The white cross of the first-aid sign.
CROSS = "#ffffff"


def _cross(cx: float, cy: float, arm: float) -> str:
    """The white cross of the first-aid sign, ``arm`` from its center to each tip."""
    w = arm * 0.6
    d = (
        f"M{cx - w / 2},{cy - arm} h{w} v{arm - w / 2} h{arm - w / 2} v{w} h{-(arm - w / 2)} "
        f"v{arm - w / 2} h{-w} v{-(arm - w / 2)} h{-(arm - w / 2)} v{-w} h{arm - w / 2} Z"
    )
    return _path(d, CROSS)


def _screen(x: float, y: float, w: float, h: float, digits: str) -> list[str]:
    """A small display with its reading."""
    return [
        _rect(x, y, w, h, SCREEN, 4, LW_DETAIL),
        f'<text x="{x + w / 2:.1f}" y="{y + h * 0.72:.1f}" font-size="{h * 0.62:.1f}" '
        f'font-family="Helvetica, Arial, sans-serif" text-anchor="middle" '
        f'fill="{DIGITS}">{digits}</text>',
    ]


def plaster_box(paint: str, fill: Fill, label: str | None, plaster: str = "fabric") -> list[str]:
    """A carton of plasters and, in front of it, one plaster of its ``plaster`` type."""
    out = [
        _path("M96,92 L270,92 L304,66 L130,66 Z", _tint(fill.base, 0.35)),
        _path("M270,92 L304,66 L304,262 L270,288 Z", _shade(fill.base, 0.2)),
        _rect(96, 92, 174, 196, paint, 4),
        _rect(110, 112, 146, 40, PAPER, 4, LW_DETAIL),
    ]
    color = PLASTER.get(plaster, PLASTER["fabric"])
    if plaster == "blister":  # an oval cushion, all pad
        out += [_ell(220, 300, 70, 42, color), _ell(220, 300, 46, 26, _tint(color, 0.4), LW_DETAIL)]
    else:
        strip = _rect(130, 270, 190, 54, color, 26)
        if plaster == "clear":
            strip = strip.replace("/>", ' fill-opacity="0.55"/>')
        out += [strip, _rect(196, 278, 58, 38, PAD, 6, LW_DETAIL)]
        if plaster == "fabric":  # the breathing holes of a fabric strip
            out += [_ell(x, y, 2, 2, _shade(color, 0.3), 0)
                    for x in (148, 164, 270, 286, 302) for y in (288, 306)]  # fmt: skip
        if plaster == "waterproof":  # a drop of water beading on it
            out.append(_path("M300,214 Q316,238 300,250 Q284,238 300,214 Z", "#7fb7e0"))
        if plaster == "sensitive":  # the soft scalloped edge of a gentle strip
            out += [_ell(x, 270, 6, 4, color, LW_DETAIL) for x in (150, 176, 274, 300)]
    out.append(_highlight("M104,104 L104,276", 5, 0.4))
    return _label(out, label)


def first_aid_kit(paint: str, fill: Fill, label: str | None, case: str = "soft pouch") -> list[str]:
    """A first-aid kit: a zipped soft pouch or a hard case with a handle, the white cross on it."""
    if case == "hard case":
        out = [
            _path("M160,96 L160,76 Q160,66 170,66 L230,66 Q240,66 240,76 L240,96", "none", 10),
            _rect(70, 96, 260, 220, paint, 14),
            _line("M70,140 L330,140", 3),
            _rect(84, 128, 18, 24, STEEL, 3, LW_DETAIL),
            _rect(298, 128, 18, 24, STEEL, 3, LW_DETAIL),
            _cross(200, 228, 56),
        ]
    else:
        out = [
            _path(
                "M78,128 Q78,98 108,98 L292,98 Q322,98 322,128 L330,292 Q330,320 300,320 "
                "L100,320 Q70,320 70,292 Z",
                paint,
            ),  # fmt: skip
            _line("M90,118 Q200,92 310,118", 4, ' stroke-dasharray="6 4"'),
            _rect(296, 104, 12, 30, STEEL, 4, LW_DETAIL),
            _cross(200, 214, 60),
        ]
    out.append(_highlight("M96,150 L96,290", 6, 0.35))
    return _label(out, label)


def thermometer(
    paint: str, fill: Fill, label: str | None, kind: str = "digital stick"
) -> list[str]:
    """A digital thermometer by ``kind``: a slim stick, an ear probe or a flat forehead head."""
    if kind == "digital stick":
        out = [
            _path("M176,60 Q176,40 200,40 Q224,40 224,60 L216,250 L184,250 Z", paint),
            _rect(186, 250, 28, 60, _tint(fill.base, 0.4), 6),
            _rect(194, 310, 12, 36, STEEL, 6),
            *_screen(184, 88, 32, 70, "36"),
            _ell(200, 190, 9, 9, _shade(fill.base, 0.25)),
        ]
    elif kind == "ear":
        out = [
            _path(
                "M150,330 L176,190 Q180,150 214,150 L250,150 Q270,150 270,176 L250,330 Z", paint
            ),  # fmt: skip
            _path(
                "M214,150 L222,92 Q226,78 240,78 Q254,78 254,92 L250,150 Z", _tint(fill.base, 0.4)
            ),  # fmt: skip
            _ell(238, 78, 10, 6, STEEL),
            *_screen(186, 196, 60, 40, "37.1"),
            _ell(214, 280, 14, 14, _shade(fill.base, 0.25)),
        ]
    else:  # a forehead thermometer: a wide flat head and a grip
        out = [
            _path("M170,340 L182,186 L238,186 L250,340 Z", paint),
            _rect(110, 92, 200, 104, paint, 26),
            _rect(96, 108, 22, 72, _tint(fill.base, 0.4), 8),
            *_screen(150, 116, 120, 56, "36.8"),
            _ell(210, 236, 14, 14, _shade(fill.base, 0.25)),
        ]
    out.append(_highlight("M200,60 L200,140", 4, 0.4) if kind == "digital stick"
               else _highlight("M190,220 L184,320", 5, 0.35))  # fmt: skip
    return _label(out, label)


def bp_monitor(paint: str, fill: Fill, label: str | None, fit: str = "upper arm") -> list[str]:
    """A blood-pressure monitor: a desk unit with its arm cuff on a tube, or a wrist unit on its
    cuff."""
    if fit == "wrist":
        out = [
            _rect(70, 170, 260, 90, _shade(fill.base, 0.35), 40),
            _line("M110,186 L110,244", LW_DETAIL),
            _line("M290,186 L290,244", LW_DETAIL),
            _rect(140, 130, 120, 170, paint, 18),
            *_screen(154, 146, 92, 70, "118"),
            _ell(200, 260, 16, 16, _shade(fill.base, 0.25)),
        ]
    else:
        out = [
            _path("M150,262 Q120,320 100,330", "none", 6, "", TUBE),
            _path("M40,300 L150,286 L170,350 L56,362 Z", _shade(fill.base, 0.35)),
            _line("M60,322 L156,310", LW_DETAIL),
            _rect(150, 90, 200, 190, paint, 20),
            *_screen(172, 110, 156, 92, "118/76"),
            _ell(212, 240, 16, 16, _shade(fill.base, 0.25)),
            _ell(290, 240, 16, 16, _shade(fill.base, 0.25)),
        ]
    out.append(_highlight("M166,104 L166,262", 5, 0.35) if fit != "wrist"
               else _highlight("M152,146 L152,286", 5, 0.35))  # fmt: skip
    return _label(out, label)


SHAPES = {
    "plaster_box": plaster_box,
    "first_aid_kit": first_aid_kit,
    "thermometer": thermometer,
    "bp_monitor": bp_monitor,
}
register(SHAPES)
register({"supplement_bottle": supplement_bottle})
