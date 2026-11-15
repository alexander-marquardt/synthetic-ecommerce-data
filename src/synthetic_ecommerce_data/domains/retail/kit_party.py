"""Party supplies for the retail drawing kit (gen#966): balloons and bunting.

=======  ===============================================  =======================================
shape    draws                                            params
=======  ===============================================  =======================================
balloon  a balloon on its ribbon: by ``style`` a latex    style (latex, foil, confetti), finish
         oval with its tied knot, a round foil one with   (matte, pearl, metallic, clear)
         a crimped seal, or a clear one holding confetti
         in the color; ``finish`` sets its sheen
bunting  a length of bunting hung in two swags: by        flag (pennant, square, scalloped),
         ``flag`` pointed, square or round-bottomed       material (paper, fabric, felt)
         flags in the color, every second one a tint;
         ``material`` draws stitching or a felt edge
=======  ===============================================  =======================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a balloon's ``style`` or a bunting's ``flag`` draws what it states (gen#512).
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

#: A balloon's ribbon and a bunting's cord.
CORD = "#8a8f98"
#: A foil balloon's crimped seal and a clear balloon's skin.
SILVER = "#d9dde3"
CLEAR = "#eef3f8"
#: How strong a finish's gloss stroke is: a matte balloon has none.
SHEEN = {"matte": 0.0, "pearl": 0.35, "metallic": 0.75, "clear": 0.55}
#: The confetti dots inside a clear balloon: (x, y, radius).
CONFETTI = ((176, 120, 7), (214, 104, 6), (232, 150, 8), (190, 170, 6), (160, 160, 5),
            (220, 196, 7), (184, 212, 6), (244, 118, 5), (204, 140, 5), (168, 196, 6))  # fmt: skip


def _ribbon(top: float) -> str:
    d = f"M200,{top} Q186,{top + 40} 204,{top + 80} Q220,{top + 118} 196,370"
    return _line(d, 3, stroke=CORD)


def balloon(paint: str, fill: Fill, label: str | None, style: str = "latex",
            finish: str = "matte") -> list[str]:  # fmt: skip
    """A balloon on its ribbon: latex with a knot, round foil with a seal, or clear confetti."""
    sheen = SHEEN.get(finish, 0.0)
    if style == "foil":
        out = [_ribbon(270), _rect(190, 254, 20, 18, SILVER, 3, LW_DETAIL),
               _ell(200, 150, 108, 106, paint),
               _ell(200, 150, 92, 90, "none", LW_DETAIL, ' stroke-opacity=".5"')]  # fmt: skip
        out.append(_highlight("M134,110 Q160,70 210,62", 9, max(sheen, 0.45)))
        return _label(out, label)
    skin = CLEAR if style == "confetti" else paint
    out = [_ribbon(272), _path("M190,272 L210,272 L204,258 L196,258 Z", _shade(fill.base, 0.3)),
           _path("M200,258 C120,250 104,150 126,104 C150,52 250,52 274,104 "
                 "C296,150 280,250 200,258 Z", skin)]  # fmt: skip
    if style == "confetti":
        out += [_ell(x, y, r, r, paint, LW_DETAIL) for x, y, r in CONFETTI]
        out.append(_ell(200, 156, 70, 92, "none", LW_DETAIL, ' stroke-opacity=".25"'))
    if sheen:
        out.append(_highlight("M150,120 Q160,86 192,74", 10, sheen))
    if finish == "pearl":
        out.append(_highlight("M246,206 Q262,176 262,146", 6, 0.25))
    return _label(out, label)


def _flag(x: float, y: float, flag: str, color: str) -> str:
    """One flag hung from its top edge at (x, y), 44 wide."""
    if flag == "square":
        return _path(f"M{x},{y} L{x + 44},{y} L{x + 44},{y + 50} L{x},{y + 50} Z", color)
    if flag == "scalloped":
        d = f"M{x},{y} L{x + 44},{y} L{x + 44},{y + 34} Q{x + 22},{y + 64} {x},{y + 34} Z"
        return _path(d, color)
    return _path(f"M{x},{y} L{x + 44},{y} L{x + 22},{y + 62} Z", color)


def bunting(paint: str, fill: Fill, label: str | None, flag: str = "pennant",
            material: str = "paper") -> list[str]:  # fmt: skip
    """Bunting in two swags of flags, every second flag a tint of the color."""
    out: list[str] = []
    tint = _tint(fill.base, 0.45)
    for row, top in enumerate((96, 216)):
        out.append(_line(f"M40,{top} Q200,{top + 34} 360,{top}", 3, stroke=CORD))
        for i, x in enumerate(range(52, 340, 50)):
            sag = 34 * (1 - ((x + 22 - 200) / 160) ** 2) * 0.5
            color = paint if (i + row) % 2 == 0 else tint
            out.append(_flag(x, top + sag, flag, color))
            if material == "fabric":
                out.append(_line(f"M{x + 4},{top + sag + 5} L{x + 40},{top + sag + 5}", LW_DETAIL,
                                 ' stroke-dasharray="3 3"'))  # fmt: skip
            elif material == "felt":
                out.append(_line(f"M{x},{top + sag} L{x + 44},{top + sag}", 5,
                                 ' stroke-opacity=".5"', _shade(fill.base, 0.35)))  # fmt: skip
    return _label(out, label)


SHAPES = {"balloon": balloon, "bunting": bunting}
register(SHAPES)
