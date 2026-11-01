"""Plain goods for the retail drawing kit (gen#34): small products of the breadth tier.

==============  ==========================================  ==============================
shape           draws                                       params
==============  ==========================================  ==============================
picture_hook    a hook plate with its hardened pin or pins  pins (1, 2)
plant_pot       a tapered pot on its saucer, the rim        finish (plain, glazed)
                proud of the body
battery         a cell standing on its base, the band and   cell (AA, AAA)
                the positive tip showing
==============  ==========================================  ==============================
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

#: A cell's width and height in sheet units, in the proportion of its real size (IEC 60086).
CELLS = {"AA": (84, 290), "AAA": (60, 256)}


def picture_hook(paint: str, fill: Fill, label: str | None, pins: str = "1") -> list[str]:
    """A picture hook: a plate that curls out into a hook, and ``pins`` slanted pins through it."""
    n = int(pins)
    out = [
        _path(
            "M150,70 C150,50 250,50 250,70 L250,190 C250,270 240,320 200,330 "
            "C160,340 130,310 136,270 L164,274 C160,296 176,306 196,300 "
            "C216,294 222,250 222,190 L178,190 L150,190 Z",
            paint,
        ),
        _highlight("M238,84 L238,180", 4, 0.5),
    ]
    for i in range(n):
        y = 110 + (0 if n == 1 else i * 44)
        out += [
            _ell(200, y, 11, 11, _shade(fill.base, 0.3)),
            _line(f"M204,{y - 4} L288,{y - 46}", 6),
        ]
    return _label(out, label)


def plant_pot(paint: str, fill: Fill, label: str | None, finish: str = "plain") -> list[str]:
    """A plant pot: the rim, the tapered body and the saucer; ``glazed`` adds a shine and a band."""
    dark = _shade(fill.base, 0.3)
    out = [
        _ell(200, 334, 124, 24, dark),
        _path("M104,128 L136,328 C160,346 240,346 264,328 L296,128 Z", paint),
        _rect(88, 84, 224, 48, paint, 8),
        _ell(200, 86, 112, 16, _shade(fill.base, 0.55), LW_DETAIL),
    ]
    if finish == "glazed":
        out += [
            _line("M121,236 C160,252 240,252 279,236", 3),
            _highlight("M132,146 L150,300", 8, 0.55),
            _highlight("M108,98 L150,98", 6, 0.55),
        ]
    return _label(out, label)


def battery(paint: str, fill: Fill, label: str | None, cell: str = "AA") -> list[str]:
    """A cell: the body, its band, the flat base and the raised positive tip."""
    w, h = CELLS[cell]
    x, top = 200 - w / 2, 364 - h
    out = [
        _rect(x, top, w, h, paint, 8),
        _rect(x, top, w, h * 0.34, _tint(fill.base, 0.65), 8, LW_DETAIL),
        _rect(200 - w * 0.2, top - 16, w * 0.4, 20, "#b9bcc2", 4, LW_DETAIL),
        _highlight(f"M{x + w * 0.2:.1f},{top + 16:.1f} L{x + w * 0.2:.1f},{364 - 16}", 5, 0.5),
    ]
    return _label(out, label)


SHAPES = {"picture_hook": picture_hook, "plant_pot": plant_pot, "battery": battery}
register(SHAPES)
