"""Baby gear for the retail drawing kit (gen#965): diapers, wipes, bottles, strollers, car
seats and high chairs.

=============  ==============================================  =================================
shape          draws                                           params
=============  ==============================================  =================================
diaper_pack    a soft pack of diapers in the pack's color,     diaper_style (tape, pull-up)
               with a carry hole and a window showing one
               diaper: tabs on its sides, or a pull-up's
               elastic waist
wipes_pack     a pillow pack of wet wipes, crimped at both     lid (flip top, resealable)
               ends, and its lid: a hinged hard lid or an
               oval peel-back flap with a pull tab
baby_bottle    a baby bottle: the teat, the screw collar in    material (plastic, glass,
               the SKU's color and the body, tinted plastic,   silicone)
               clear glass, or a soft silicone bulge
stroller       a stroller in its fabric color: a deep seat     stroller_style (full-size,
               under a big hood on four wheels, a slim         compact, jogging)
               frame with a small hood and twin wheels, or a
               three-wheeler on large air tyres
car_seat       a child's car seat in its fabric color: a       seat_type (infant carrier,
               rear-facing carrier with a carry handle, a      convertible, high-back booster)
               harnessed seat on a base, or a booster with a
               high back, side wings and armrests
high_chair     a high chair with a tray, its seat pad in the   frame (wooden, folding,
               SKU's color: on four splayed wooden legs, a     pedestal)
               folding X-frame on wheels, or one pedestal on
               a round foot
=============  ==============================================  =================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a diaper's ``diaper_style``, a bottle's ``material``, a stroller's
``stroller_style``, a car seat's ``seat_type`` or a high chair's ``frame`` draws what it states
(gen#512).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    PAPER,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: A diaper's soft white body and its fastening tabs.
DIAPER = "#f7f5ef"
TAB = "#9fc3e6"
#: A bottle's silicone teat.
TEAT = "#f1dcb8"
#: Clear glass, drawn as a pale blue-grey.
GLASS = "#e6eff3"
#: The volume marks printed on a bottle.
MARK = "#6d86a8"
#: A stroller's or a high chair's metal frame, and a tyre.
FRAME = "#5b616b"
TYRE = "#34373d"
#: A wooden high chair's beech.
BEECH = "#d4a46a"
#: A car seat's shell and harness.
SHELL = "#4a4d55"
STRAP = "#2f3137"


def _diaper(style: str) -> list[str]:
    """One diaper in the pack's window: hourglass with side tabs, or pull-up pants."""
    if style == "pull-up":
        out = [
            _path(
                "M150,178 L250,178 L246,212 Q230,236 222,262 L178,262 Q170,236 154,212 Z", DIAPER
            ),
            _rect(148, 172, 104, 14, _tint(TAB, 0.3), 4, LW_DETAIL),
        ]
        out += [_line(f"M152,{y} L248,{y}", 1.0, "", MARK) for y in (176, 180)]
        return out
    return [
        _path("M160,178 L240,178 Q228,220 240,262 L160,262 Q172,220 160,178 Z", DIAPER),
        _rect(140, 184, 22, 16, TAB, 4, LW_DETAIL),
        _rect(238, 184, 22, 16, TAB, 4, LW_DETAIL),
        _line("M176,190 Q200,198 224,190", LW_DETAIL),
    ]


def diaper_pack(paint: str, fill: Fill, label: str | None, diaper_style: str = "tape") -> list[str]:
    """A soft pack of diapers: the bag, its carry hole, and a window showing one diaper."""
    out = [
        _rect(96, 56, 208, 296, paint, 22),
        _rect(96, 56, 208, 26, _shade(fill.base, 0.2), 12, LW_DETAIL),
        _ell(200, 100, 34, 11, PAPER, LW_DETAIL),
        _rect(128, 154, 144, 128, PAPER, 16, LW_DETAIL),
        *_diaper(diaper_style),
        _rect(128, 298, 144, 22, _tint(fill.base, 0.45), 8, LW_DETAIL),
        _highlight("M112,120 L112,330", 6, 0.45),
    ]
    return _label(out, label)


def wipes_pack(paint: str, fill: Fill, label: str | None, lid: str = "flip top") -> list[str]:
    """A pillow pack of wet wipes: the crimped pack and a flip-top lid or a peel-back flap."""
    crimp = _shade(fill.base, 0.3)
    out = [
        _rect(64, 132, 272, 176, paint, 30),
        *[_line(f"M{x},140 L{x},300", LW_DETAIL, "", crimp) for x in (78, 86, 314, 322)],
    ]
    if lid == "resealable":
        out += [
            _ell(200, 220, 70, 40, _tint(fill.base, 0.6), LW_DETAIL),
            _ell(200, 220, 44, 18, PAPER, LW_DETAIL),
            _rect(258, 210, 30, 20, _tint(fill.base, 0.3), 6, LW_DETAIL),
        ]
    else:
        out += [
            _rect(140, 186, 120, 70, PAPER, 14),
            _rect(150, 196, 100, 50, _tint(fill.base, 0.75), 10, LW_DETAIL),
            _line("M144,200 L256,200", LW_DETAIL),
            _path(
                "M184,216 Q200,198 216,216 Q208,226 200,220 Q192,226 184,216 Z", PAPER, LW_DETAIL
            ),
        ]
    out.append(_highlight("M96,160 L304,160", 6, 0.4))
    return _label(out, label)


def baby_bottle(paint: str, fill: Fill, label: str | None, material: str = "plastic") -> list[str]:
    """A baby bottle: the teat, the collar in the SKU's color, and a body by its material."""
    ridge = _shade(fill.base, 0.3)
    out = [_path("M176,118 Q178,70 200,62 Q222,70 224,118 Z", TEAT)]
    if material == "silicone":
        out.append(_path("M150,170 Q118,250 150,340 L250,340 Q282,250 250,170 Z", paint))
    elif material == "glass":
        out.append(_rect(152, 160, 96, 184, GLASS, 20))
        out.append(_highlight("M168,180 L168,320", 6, 0.8))
        out.append(_highlight("M232,190 L232,300", 3, 0.7))
    else:
        body = _tint(fill.base, 0.5) if paint == fill.base else paint
        out.append(_rect(152, 160, 96, 184, body, 20))
        out.append(_highlight("M168,180 L168,320", 6, 0.5))
    out += [_line(f"M156,{y} L176,{y}", LW_DETAIL, "", MARK) for y in range(196, 320, 24)]
    out += [
        _rect(144, 116, 112, 48, paint, 10),
        *[_line(f"M{x},122 L{x},158", LW_DETAIL, "", ridge) for x in range(156, 250, 12)],
    ]
    return _label(out, label)


def _wheel(cx: float, cy: float, r: float, spokes: bool = False) -> list[str]:
    """A wheel: the tyre, its hub and, on an air tyre, its spokes."""
    out = [_ell(cx, cy, r, r, TYRE), _ell(cx, cy, r * 0.62, r * 0.62, _tint(FRAME, 0.5), LW_DETAIL)]
    if spokes:
        out += [_line(f"M{cx - r * 0.6:.0f},{cy} L{cx + r * 0.6:.0f},{cy}", LW_DETAIL),
                _line(f"M{cx},{cy - r * 0.6:.0f} L{cx},{cy + r * 0.6:.0f}", LW_DETAIL)]  # fmt: skip
    out.append(_ell(cx, cy, r * 0.18, r * 0.18, FRAME, LW_DETAIL))
    return out


def stroller(
    paint: str, fill: Fill, label: str | None, stroller_style: str = "full-size"
) -> list[str]:
    """A stroller from the side: its frame, its seat and hood in the fabric color, its wheels."""
    hood = _shade(fill.base, 0.15)
    if stroller_style == "jogging":
        out = [
            _line("M86,92 L150,250 L312,318", 7, "", FRAME),
            _line("M150,250 L136,318", 7, "", FRAME),
            _rect(70, 82, 40, 14, TYRE, 7),
            _path("M150,170 L262,190 Q276,250 246,272 L166,268 Q146,232 150,170 Z", paint),
            _path("M146,182 Q150,104 236,114 L246,148 Q196,140 176,190 Z", hood),
            *_wheel(136, 318, 48, spokes=True),
            *_wheel(316, 326, 38, spokes=True),
        ]
    elif stroller_style == "compact":
        out = [
            _line("M108,84 L170,320", 4, "", FRAME),
            _line("M120,130 L270,326", 4, "", FRAME),
            _rect(96, 76, 28, 12, TYRE, 6),
            _path("M150,176 L236,236 L222,270 L160,262 Z", paint),
            _path("M138,168 Q160,118 214,140 L196,170 Z", hood),
            _rect(150, 290, 100, 18, _tint(fill.base, 0.4), 6, LW_DETAIL),
            *_wheel(164, 330, 16),
            *_wheel(184, 334, 14),
            *_wheel(264, 334, 16),
            *_wheel(284, 336, 14),
        ]
    else:
        out = [
            _line("M84,88 L150,300 L292,312", 6, "", FRAME),
            _line("M150,300 L120,332", 6, "", FRAME),
            _rect(66, 78, 46, 16, TYRE, 8),
            _path("M134,190 L290,190 Q300,262 262,292 L166,292 Q134,262 134,190 Z", paint),
            _path("M126,200 Q124,96 250,104 L262,142 Q178,136 166,200 Z", hood),
            *[_line(f"M{x},{y} Q{x + 30},{y - 34} {x + 70},{y - 26}", LW_DETAIL, "", _shade(hood))
              for x, y in ((140, 186), (154, 168))],
            _rect(160, 306, 112, 20, _tint(fill.base, 0.4), 6, LW_DETAIL),
            *_wheel(120, 332, 34),
            *_wheel(292, 334, 30),
        ]  # fmt: skip
    out.append(_highlight("M176,212 Q200,206 250,212", 6, 0.4))
    return _label(out, label)


def car_seat(
    paint: str, fill: Fill, label: str | None, seat_type: str = "infant carrier"
) -> list[str]:
    """A child's car seat, its fabric in the SKU's color: a carrier, a harnessed seat or a
    booster."""
    trim = _shade(fill.base, 0.25)
    if seat_type == "high-back booster":
        out = [
            _rect(136, 70, 128, 180, paint, 30),
            _path("M120,86 L156,80 L156,170 L120,160 Z", trim, LW_DETAIL),
            _path("M280,86 L244,80 L244,170 L280,160 Z", trim, LW_DETAIL),
            _rect(110, 248, 180, 64, paint, 18),
            _rect(96, 226, 36, 56, trim, 12),
            _rect(268, 226, 36, 56, trim, 12),
            _rect(156, 176, 26, 10, "#c8312e", 4, LW_DETAIL),
            _rect(118, 310, 164, 22, SHELL, 8),
        ]
    elif seat_type == "convertible":
        out = [
            _path("M130,320 L270,320 L290,348 L110,348 Z", SHELL),
            _rect(128, 64, 144, 214, paint, 34),
            _rect(118, 252, 164, 70, paint, 22),
            _path("M128,96 L110,110 L110,220 L128,228 Z", trim, LW_DETAIL),
            _path("M272,96 L290,110 L290,220 L272,228 Z", trim, LW_DETAIL),
            _line("M168,120 L192,262", 7, "", STRAP),
            _line("M232,120 L208,262", 7, "", STRAP),
            _rect(186, 254, 28, 22, FRAME, 5, LW_DETAIL),
            _rect(176, 180, 48, 14, FRAME, 5, LW_DETAIL),
        ]
    else:
        out = [
            _path("M96,214 Q90,124 160,146 L170,186 Q246,190 318,196 Q330,302 236,330 L150,330 "
                  "Q96,316 96,214 Z", SHELL),
            _path("M118,214 Q114,156 156,166 L168,206 Q240,210 296,214 Q300,290 230,306 L160,306 "
                  "Q118,296 118,214 Z", paint),
            _path("M82,238 Q200,40 330,214", "none", 12, "", FRAME),
            _path("M96,200 Q120,124 180,128 L172,170 Z", trim, LW_DETAIL),
            _line("M190,224 L214,290", 6, "", STRAP),
            _line("M236,224 L224,290", 6, "", STRAP),
        ]
    out.append(_highlight("M148,110 L148,220" if seat_type != "infant carrier" else
                          "M130,230 Q136,280 170,296", 5, 0.35))
    return _label(out, label)


def high_chair(paint: str, fill: Fill, label: str | None, frame: str = "wooden") -> list[str]:
    """A high chair with its tray and seat pad in the SKU's color, on its frame."""
    tray = _tint(fill.base, 0.7)
    if frame == "pedestal":
        out = [
            _ell(200, 344, 92, 18, FRAME),
            _rect(186, 214, 28, 132, _tint(FRAME, 0.3), 8),
            _path("M134,92 Q200,70 266,92 L270,220 Q200,240 130,220 Z", PAPER),
            _path("M148,106 Q200,90 252,106 L254,206 Q200,222 146,206 Z", paint),
        ]
    elif frame == "folding":
        out = [
            _line("M136,180 L270,334", 6, "", FRAME),
            _line("M264,180 L130,334", 6, "", FRAME),
            *_wheel(130, 340, 12),
            *_wheel(270, 340, 12),
            _rect(140, 70, 120, 170, paint, 26),
            _rect(150, 82, 100, 40, _shade(fill.base, 0.12), 18, LW_DETAIL),
            _line("M150,300 L250,300", 5, "", FRAME),
        ]
    else:
        out = [
            _line("M150,230 L112,346", 9, "", BEECH),
            _line("M250,230 L288,346", 9, "", BEECH),
            _line("M162,230 L150,346", 7, "", _shade(BEECH, 0.15)),
            _line("M238,230 L250,346", 7, "", _shade(BEECH, 0.15)),
            _line("M126,300 L274,300", 6, "", BEECH),
            _rect(146, 84, 108, 150, BEECH, 14),
            _rect(158, 98, 84, 124, paint, 14, LW_DETAIL),
        ]
    out += [
        _rect(96, 196, 208, 22, tray, 10),
        _rect(104, 190, 192, 10, PAPER, 5, LW_DETAIL),
    ]
    return _label(out, label)


SHAPES = {
    "diaper_pack": diaper_pack, "wipes_pack": wipes_pack, "baby_bottle": baby_bottle,
    "stroller": stroller, "car_seat": car_seat, "high_chair": high_chair,
}  # fmt: skip
register(SHAPES)
