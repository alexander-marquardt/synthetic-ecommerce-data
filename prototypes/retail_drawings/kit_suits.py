"""Tailoring shapes for the retail drawing kit (gen#215): five shapes, each its own.

==================  =====================================================  =================
shape               draws                                                  params
==================  =====================================================  =================
suit_jacket         a single-breasted jacket, cut closer to the body        fit, lapel
                    as the fit narrows, with a notch, peak or shawl lapel
suit_trousers       tailored trousers with a pleat crease and belt loops,   fit, leg
                    the hem set by the leg length
waistcoat           a V-neck waistcoat with a buttoned front               fit, buttons
dinner_suit         a dinner jacket (satin-faced peak or shawl lapel)       fit, lapel
                    over trousers with a satin side stripe, and a bow tie
formal_accessory    a tie, bow tie, braces, cummerbund or pocket square     item
==================  =====================================================  =================

The fit is stamped on the body (``class="fit-slim"``), the lapel on the lapel group
(``class="lapel-peak"``), the leg length on the hem (``class="leg-long"``), each button as a
``class="button"`` mark and the accessory on its group (``class="item-bow_tie"``), so
``tests/test_retail_suits_215.py`` reads the record's choice back from the drawing. A shape is
painted in the record's fill and prints no size.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _line, _mirror, _path, _shade, register

FITS = ("slim", "tailored", "regular")
LAPELS = ("notch", "peak", "shawl")
LEGS = ("short", "regular", "long")
ITEMS = ("tie", "bow_tie", "braces", "cummerbund", "pocket_square")
BUTTON_COUNTS = ("4", "5", "6")

#: fit -> (waist x, hem x) of the jacket's LEFT side; the right side is the mirror image.
_JACKET = {"slim": (142, 136), "tailored": (134, 126), "regular": (122, 116)}
#: fit -> the half-width of one trouser leg at the hem.
_LEG_W = {"slim": 17, "tailored": 22, "regular": 28}
#: leg -> hem y.
_HEM = {"short": 316, "regular": 340, "long": 366}
SATIN = "#23262b"


def _m(x: float) -> float:
    return 400 - x


def _g(cls: str, parts: list[str]) -> str:
    return f'<g class="{cls}">' + "".join(parts) + "</g>"


def _both(left: str, right: str, fill: str, width: float = LW) -> list[str]:
    return [_path(left, fill, width), _path(right, fill, width)]


def _button(x: float, y: float, r: float = 4.5, fill: str = "#d9d4c4") -> str:
    return f'<circle class="button" cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>'


def _lapel_paths(lapel: str, y0: float = 52.0) -> tuple[str, str]:
    """The left and right lapel of a jacket whose neck is at ``y0``, opening down to y0 + 120."""
    if lapel == "notch":
        left = f"M176,{y0} L200,{y0 + 124} L184,{y0 + 126} L168,{y0 + 78} L146,{y0 + 70} L154,{y0 + 32} Z"
    elif lapel == "peak":
        left = f"M176,{y0} L200,{y0 + 124} L182,{y0 + 124} L150,{y0 + 62} L162,{y0 + 52} L142,{y0 + 30} L156,{y0 + 20} Z"
    else:  # shawl: one rolled curve with no notch
        left = f"M176,{y0} Q146,{y0 + 60} 200,{y0 + 124} L186,{y0 + 122} Q150,{y0 + 66} 154,{y0 + 30} Z"
    return left, _mirror(left)


def _jacket_body(
    paint: str, fill: Fill, fit: str, lapel: str, top: float = 52.0, dinner: bool = False
) -> list[str]:
    wx, hx = _JACKET[fit]
    cx = 128 if fit != "slim" else 134
    bottom = 330
    body = f"M176,{top} L142,{top + 12} L{cx},{top + 56} L{wx},{top + 158} L{hx},{bottom} L{_m(hx)},{bottom} L{_m(wx)},{top + 158} L{_m(cx)},{top + 56} L258,{top + 12} L224,{top} Z"
    sleeve_x = 96 if fit == "regular" else 104
    sleeve = f"M142,{top + 12} L{sleeve_x},{top + 36} L{sleeve_x - 6},{bottom - 30} L{sleeve_x + 26},{bottom - 24} L{cx},{top + 56} Z"
    sleeve_r = f"M258,{top + 12} L{_m(sleeve_x)},{top + 36} L{_m(sleeve_x - 6)},{bottom - 30} L{_m(sleeve_x + 26)},{bottom - 24} L{_m(cx)},{top + 56} Z"
    ll, lr = _lapel_paths(lapel, top)
    facing = _shade(SATIN, 0.0) if dinner else _shade(fill.base, 0.14)
    out = [*_both(sleeve, sleeve_r, paint), _g(f"fit-{fit}", [_path(body, paint)])]
    out.append(_g(f"lapel-{lapel}", [_path(ll, facing, LW_DETAIL), _path(lr, facing, LW_DETAIL)]))
    out.append(_line(f"M200,{top + 124} L200,{bottom}"))
    out += (
        [_button(206, top + 150), _button(206, top + 198)]
        if not dinner
        else [_button(206, top + 150, 4, "#14161a")]
    )
    out += [
        _path(
            f"M{wx + 16},{top + 188} L{wx + 52},{top + 188} L{wx + 52},{top + 204} L{wx + 16},{top + 204} Z",
            paint,
            LW_DETAIL,
        )
    ]
    out += [
        _path(
            f"M{_m(wx + 16)},{top + 188} L{_m(wx + 52)},{top + 188} L{_m(wx + 52)},{top + 204} L{_m(wx + 16)},{top + 204} Z",
            paint,
            LW_DETAIL,
        )
    ]
    return out


def suit_jacket(
    paint: str, fill: Fill, label: str | None, fit: str = "regular", lapel: str = "notch"
) -> list[str]:
    return _jacket_body(
        paint, fill, fit if fit in _JACKET else "regular", lapel if lapel in LAPELS else "notch"
    )


def _trouser_legs(paint: str, fit: str, hem: float, top: float, belt: bool = True) -> list[str]:
    half = _LEG_W[fit]
    hip = 74 if fit == "slim" else 80
    left = f"M{200 - hip},{top} L200,{top} L200,{top + 96} L{200 - 4},{hem} L{200 - 4 - 2 * half},{hem} L{200 - hip + 6},{top + 80} Z"
    right = f"M200,{top} L{200 + hip},{top} L{200 + hip - 6},{top + 80} L{200 + 4 + 2 * half},{hem} L{200 + 4},{hem} L200,{top + 96} Z"
    crease_l = f"M{200 - 40},{top + 24} L{200 - 4 - half},{hem}"
    crease_r = f"M{200 + 40},{top + 24} L{200 + 4 + half},{hem}"
    out = [*_both(left, right, paint)]
    out += [
        _line(crease_l, 1.2, ' stroke-opacity=".5"'),
        _line(crease_r, 1.2, ' stroke-opacity=".5"'),
    ]
    return out


def suit_trousers(
    paint: str, fill: Fill, label: str | None, fit: str = "regular", leg: str = "regular"
) -> list[str]:
    fit = fit if fit in _LEG_W else "regular"
    hem = _HEM.get(leg, 340)
    top = 70.0
    out = [_g(f"fit-{fit}", _trouser_legs(paint, fit, hem, top))]
    band = f"M{200 - 82},{top - 4} L{200 + 82},{top - 4} L{200 + 82},{top + 18} L{200 - 82},{top + 18} Z"
    out.append(_path(band, _shade(fill.base, 0.12), LW_DETAIL))
    out += [_line(f"M{x},{top - 18} L{x},{top + 2}", 3.2) for x in (140, 170, 230, 260)]
    out.append(
        f'<circle cx="206" cy="{top + 7}" r="4" fill="#d9d4c4" stroke="{INK}" stroke-width="1.2"/>'
    )
    out.append(_line(f"M200,{top + 18} L200,{top + 96}", 1.4))
    out += [
        _line(f"M{200 - 70},{top + 26} Q{200 - 56},{top + 44} {200 - 60},{top + 70}", 1.6),
        _line(f"M{200 + 70},{top + 26} Q{200 + 56},{top + 44} {200 + 60},{top + 70}", 1.6),
    ]
    out.append(
        _g(
            f"leg-{leg}",
            [
                _line(
                    f"M{200 - 4 - 2 * _LEG_W[fit]},{hem} L{200 - 4},{hem} M{200 + 4},{hem} L{200 + 4 + 2 * _LEG_W[fit]},{hem}",
                    4,
                )
            ],
        )
    )
    return out


def waistcoat(
    paint: str, fill: Fill, label: str | None, fit: str = "regular", buttons: str = "5"
) -> list[str]:
    fit = fit if fit in _JACKET else "regular"
    n = int(buttons) if buttons in BUTTON_COUNTS else 5
    wx = {"slim": 150, "tailored": 142, "regular": 132}[fit]
    left = f"M168,46 L150,60 L146,118 L{wx},206 L{wx + 4},310 L200,346 L200,150 Z"
    right = f"M232,46 L250,60 L254,118 L{_m(wx)},206 L{_m(wx + 4)},310 L200,346 L200,150 Z"
    out = [_g(f"fit-{fit}", [*_both(left, right, paint)])]
    out.append(_g(f"buttons-{n}", [_button(194, 160 + k * (150 / (n - 1)), 4) for k in range(n)]))
    out += [_line("M168,46 L200,150 L232,46", 3)]
    out += [
        _path(f"M{wx + 14},228 L{wx + 48},224 L{wx + 48},234 L{wx + 14},238 Z", paint, LW_DETAIL),
        _path(
            f"M{_m(wx + 14)},228 L{_m(wx + 48)},224 L{_m(wx + 48)},234 L{_m(wx + 14)},238 Z",
            paint,
            LW_DETAIL,
        ),
    ]
    out.append(_line(f"M{wx + 2},250 L{wx + 2},300", 1.2, ' stroke-opacity=".5"'))
    return out


def dinner_suit(
    paint: str, fill: Fill, label: str | None, fit: str = "regular", lapel: str = "shawl"
) -> list[str]:
    fit = fit if fit in _JACKET else "regular"
    lapel = lapel if lapel in ("peak", "shawl") else "shawl"
    top = 24.0
    hem = 368.0
    legs = _trouser_legs(paint, "slim" if fit == "slim" else "tailored", hem, 214.0)
    stripe = [
        _line(f"M{200 - 38},238 L{200 - 24},{hem}", 5, stroke=SATIN),
        _line(f"M{200 + 38},238 L{200 + 24},{hem}", 5, stroke=SATIN),
    ]
    out = [*legs, _g("side-stripe", stripe)]
    out += _jacket_body(paint, fill, fit, lapel, top, dinner=True)
    bow = f'<g class="bow"><path d="M200,{top + 60} L178,{top + 48} L178,{top + 72} Z M200,{top + 60} L222,{top + 48} L222,{top + 72} Z" fill="{SATIN}" stroke="{INK}" stroke-width="1.4"/></g>'
    return [*out, bow]


def _tie(paint: str, fill: Fill) -> list[str]:
    knot = "M178,60 L222,60 L216,100 L184,100 Z"
    blade = "M184,100 L216,100 L236,330 L200,358 L164,330 Z"
    return [
        _path(blade, paint),
        _path(knot, _shade(fill.base, 0.14)),
        _line("M184,100 L216,100", 1.6),
        _line("M200,120 L200,330", 1.2, ' stroke-opacity=".4"'),
    ]


def _bow_tie(paint: str, fill: Fill) -> list[str]:
    left = "M200,190 L112,146 Q96,200 112,254 Z"
    right = "M200,190 L288,146 Q304,200 288,254 Z"
    return [
        *_both(left, right, paint),
        _path("M184,170 L216,170 L216,210 L184,210 Z", _shade(fill.base, 0.16)),
        _line(
            "M130,170 L184,190 M130,230 L184,196 M270,170 L216,190 M270,230 L216,196",
            1.0,
            ' stroke-opacity=".5"',
        ),
    ]


def _clip(x: float, y: float) -> str:
    return f'<rect x="{x}" y="{y}" width="26" height="22" rx="3" fill="#cfcab8" stroke="{INK}" stroke-width="1.6"/>'


def _braces(paint: str, fill: Fill) -> list[str]:
    strap_l = "M150,30 L170,30 L196,230 L176,232 Z"
    strap_r = "M250,30 L230,30 L204,230 L224,232 Z"
    out = [
        *_both(strap_l, strap_r, paint),
        _path("M176,232 L224,232 L222,262 L178,262 Z", _shade(fill.base, 0.12), LW_DETAIL),
    ]
    out += [_clip(142, 24), _clip(232, 24), _clip(150, 258), _clip(224, 258)]
    return out


def _cummerbund(paint: str, fill: Fill) -> list[str]:
    band = "M70,150 Q200,120 330,150 L330,250 Q200,282 70,250 Z"
    pleats = "".join(
        _line(
            f"M{70 + k * 33},{150 + 4 - abs(k - 3.9) * 0.4} Q{70 + k * 33},{200} {70 + k * 33},{252 - 4 + abs(k - 3.9) * 0.3}",
            1.2,
            ' stroke-opacity=".5"',
        )
        for k in range(1, 8)
    )
    return [
        _path(band, paint),
        pleats,
        _path("M312,150 L336,148 L336,252 L312,254 Z", _shade(fill.base, 0.2), LW_DETAIL),
    ]


def _pocket_square(paint: str, fill: Fill) -> list[str]:
    sq = "M120,250 L200,110 L280,250 L252,300 L148,300 Z"
    fold = "M148,300 L200,200 L252,300"
    return [
        _path(sq, paint),
        _line(fold, 1.6),
        _path("M150,262 L200,176 L250,262 Z", _shade(fill.base, 0.1), LW_DETAIL),
    ]


def formal_accessory(paint: str, fill: Fill, label: str | None, item: str = "tie") -> list[str]:
    item = item if item in ITEMS else "tie"
    draw = {
        "tie": _tie,
        "bow_tie": _bow_tie,
        "braces": _braces,
        "cummerbund": _cummerbund,
        "pocket_square": _pocket_square,
    }[item]
    return [_g(f"item-{item}", draw(paint, fill))]


SHAPES = {"suit_jacket": suit_jacket, "suit_trousers": suit_trousers, "waistcoat": waistcoat,
          "dinner_suit": dinner_suit, "formal_accessory": formal_accessory}  # fmt: skip
register(SHAPES)
