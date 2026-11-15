"""Baby gear for the retail drawing kit (gen#965): diapers, baby wipes and baby bottles.

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
=============  ==============================================  =================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a diaper's ``diaper_style`` or a bottle's ``material`` draws what it states
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


SHAPES = {"diaper_pack": diaper_pack, "wipes_pack": wipes_pack, "baby_bottle": baby_bottle}
register(SHAPES)
