"""Drawings of three ordinary products whose names hold a seed phrase (gen#461, class 8 of #326).

==================  ==========================================  ======
shape               what it draws                               params
==================  ==========================================  ======
makeup_brush        a long handle, a metal ferrule, flat bristles  none
makeup_sponge       a teardrop blending sponge with a rounded tip  none
bed_risers          four chunky square blocks with a dished top    none
==================  ==========================================  ======

A fixing kit reuses ``screw``, a gift box ``box_wide``, a baking mix ``box`` and a planter ``tub``.
No drawing prints a number.
"""

from __future__ import annotations

from kit import Fill, _highlight, _path, _shade, _tint, register
from kit_sports import _ell, _label, _rect

METAL = "#b9bdc4"


def makeup_brush(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A foundation brush: a slim handle, a metal ferrule and a flat-topped head of bristles."""
    out = [
        _path("M178,330 L222,330 L214,190 L186,190 Z", paint),
        _rect(182, 150, 36, 46, METAL, 6),
        _path("M170,150 L230,150 L240,84 L160,84 Z", _tint(fill.base, 0.55)),
        _path("M160,84 L240,84", "none", 5),
    ]
    out.append(_highlight("M192,300 L190,210", 5, 0.35))
    return _label(out, label)


def makeup_sponge(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A blending sponge: a soft teardrop, wide and round at the base and tapered to a tip."""
    out = [
        _path("M200,70 Q250,170 296,250 Q330,330 200,332 Q70,330 104,250 Q150,170 200,70 Z", paint),
        _ell(200, 292, 40, 14, _shade(fill.base, 0.12)),
    ]
    out.append(_highlight("M150,250 Q170,190 196,120", 6, 0.4))
    return _label(out, label)


def bed_risers(paint: str, fill: Fill, label: str | None) -> list[str]:
    """Bed risers: four chunky blocks in a row, each with a dished top that takes a bed leg."""
    out = []
    for x in (30, 112, 194, 276):
        out.append(_rect(x, 170, 78, 110, paint, 10))
        out.append(_ell(x + 39, 186, 26, 9, _shade(fill.base, 0.3)))
    out.append(_highlight("M40,200 L40,262", 5, 0.35))
    return _label(out, label)


SHAPES = {
    "makeup_brush": makeup_brush,
    "makeup_sponge": makeup_sponge,
    "bed_risers": bed_risers,
}
register(SHAPES)
