"""Car interior shapes for the retail drawing kit (gen#970, slice 3).

The Automotive department's interior products that no other shape draws: each is drawn as what it
is, so a seat cover never reads as a sofa cover and a floor mat never reads as a bath mat. Outlines
are the kit's ink, and the record's fill paints the main surface.

====================  =========================================  ================================
shape                 draws                                      params
====================  =========================================  ================================
seat_cover            a car seat in its cover: a bucket seat     style (bucket, bench)
                      with a headrest, or a rear bench of
                      three backs
floor_mat             a car floor mat seen from above: a         style (rubber, carpet)
                      rubber mat with deep channels, or a
                      carpet mat with a bound edge and heel pad
trunk_liner           a cargo liner seen from above: a tray      style (tray, fabric)
                      with raised walls, or a quilted fabric
                      liner with a bumper flap
steering_wheel_cover  a steering wheel in its cover: a stitched  style (stitched, grip)
                      rim, or a rim with finger grips
sun_shade             a windshield shade: an accordion of        style (accordion, twist,
                      folds, two twist-fold rounds, an           umbrella, side)
                      umbrella on its handle, or a side
                      window mesh
====================  =========================================  ================================

A drawing never prints a vehicle size or a set size: a style's SKUs share one image. Every param
is a string with a default, so each shape also draws bare.
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
from synthetic_ecommerce_data.domains.retail.kit_sports import _label, _rect

#: The reflective silver face of a sun shade.
SILVER = "#c9ced4"


def _ring(cx: float, cy: float, r: float, stroke: str, width: float) -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{stroke}" stroke-width="{width}"/>'


def seat_cover(paint: str, fill: Fill, label: str | None, style: str = "bucket") -> list[str]:
    """A seat in its cover: a ``bucket`` front seat with a headrest, or a rear ``bench``."""
    seam = _shade(fill.base, 0.3)
    if style.lower() == "bench":
        out = []
        for x in (70, 160, 250):
            out += [
                _rect(x, 120, 80, 150, paint, 18),
                _line(f"M{x + 14},{170} L{x + 66},{170} M{x + 14},{220} L{x + 66},{220}", LW_DETAIL, ' stroke-dasharray="5 4"', seam),
            ]
        out += [
            _path("M60,270 L340,270 L350,320 Q200,336 50,320 Z", paint),
            _line("M70,296 L330,296", LW_DETAIL, ' stroke-dasharray="5 4"', seam),
        ]
        return _label(out, label)
    return _label([
        _rect(158, 60, 84, 56, paint, 18),
        _line("M180,116 L180,132 M220,116 L220,132", LW + 2, stroke=INK),
        _path("M130,132 Q200,120 270,132 L282,280 L118,280 Z", paint),
        _line("M150,170 L250,170 M146,230 L254,230", LW_DETAIL, ' stroke-dasharray="5 4"', seam),
        _line("M200,140 L200,272", LW_DETAIL, ' stroke-dasharray="5 4"', seam),
        _path("M100,280 L300,280 L316,340 Q200,356 84,340 Z", paint),
        _highlight("M140,146 L132,262", 4, 0.35),
    ], label)


def floor_mat(paint: str, fill: Fill, label: str | None, style: str = "rubber") -> list[str]:
    """A floor mat from above: a ``rubber`` mat with channels, or a ``carpet`` mat with a heel pad."""
    outline = "M110,70 L290,70 Q310,70 312,92 L320,300 Q320,340 290,340 L110,340 Q80,340 80,300 L88,92 Q90,70 110,70 Z"
    if style.lower() == "carpet":
        return _label([
            _path(outline, _shade(fill.base, 0.35)),
            _path("M118,84 L282,84 Q298,84 299,100 L306,296 Q306,324 284,324 L116,324 Q94,324 94,296 L101,100 Q102,84 118,84 Z", paint, LW_DETAIL),
            _rect(150, 236, 100, 64, _shade(fill.base, 0.5), 8, LW_DETAIL),
            *[_line(f"M{162 + 12 * i},244 L{162 + 12 * i},292", 1.0, stroke=_tint(fill.base, 0.2)) for i in range(7)],
        ], label)
    channels = [_line(f"M{110 + 22 * i},110 L{108 + 22 * i},300", LW + 3, stroke=_shade(fill.base, 0.35)) for i in range(9)]
    return _label([
        _path(outline, paint),
        _path("M100,96 L300,96 L306,316 L94,316 Z", "none", LW_DETAIL),
        *channels,
        _highlight("M100,90 L296,90", 3, 0.4),
    ], label)


def trunk_liner(paint: str, fill: Fill, label: str | None, style: str = "tray") -> list[str]:
    """A cargo liner from above: a ``tray`` with raised walls, or a quilted ``fabric`` liner."""
    wall = _shade(fill.base, 0.3)
    if style.lower() == "fabric":
        quilt = [_line(f"M{80 + 40 * i},90 L{80 + 40 * i},270", LW_DETAIL, ' stroke-dasharray="6 4"', wall) for i in range(1, 7)]
        return _label([
            _path("M70,80 L330,80 L340,270 L60,270 Z", paint),
            *quilt,
            _line("M66,170 L334,170", LW_DETAIL, ' stroke-dasharray="6 4"', wall),
            _path("M60,270 L340,270 L330,330 L70,330 Z", _tint(fill.base, 0.15)),
            _line("M76,316 L324,316", LW_DETAIL, ' stroke-dasharray="6 4"', wall),
        ], label)
    return _label([
        _path("M60,70 L340,70 L350,320 L50,320 Z", wall),
        _path("M84,94 L316,94 L322,296 L78,296 Z", paint),
        *[_line(f"M100,{130 + 40 * i} L300,{130 + 40 * i}", LW + 2, stroke=wall) for i in range(4)],
        _highlight("M64,76 L336,76", 3, 0.35),
    ], label)


def steering_wheel_cover(paint: str, fill: Fill, label: str | None, style: str = "stitched") -> list[str]:
    """A steering wheel in its cover: a ``stitched`` rim, or a rim with finger ``grip`` ridges."""
    hub = "#3a3d42"
    out = [
        _ring(200, 200, 130, INK, 44),
        _ring(200, 200, 130, paint, 38),
        _path("M80,214 L160,200 Q200,236 240,200 L320,214 L316,232 L240,224 Q200,262 160,224 L84,232 Z", hub),
        f'<circle cx="200" cy="216" r="40" fill="{hub}" stroke="{INK}" stroke-width="{LW}"/>',
        _line("M200,256 L200,326", LW + 14, stroke=INK),
        _line("M200,256 L200,326", LW + 10, stroke=hub),
    ]
    if style.lower() == "grip":
        out += [_line(f"M{200 + 108 * c},{200 + 108 * s} L{200 + 152 * c},{200 + 152 * s}", LW + 1, stroke=_shade(fill.base, 0.35))
                for c, s in ((-0.94, -0.34), (-0.87, -0.5), (-0.77, -0.64), (0.94, -0.34), (0.87, -0.5), (0.77, -0.64))]
    else:
        out += [_ring(200, 200, 118, _tint(fill.base, 0.45), 1.4), _ring(200, 200, 142, _tint(fill.base, 0.45), 1.4)]
    return _label(out, label)


def sun_shade(paint: str, fill: Fill, label: str | None, style: str = "accordion") -> list[str]:
    """A windshield shade: an ``accordion``, a ``twist`` fold pair, an ``umbrella``, or a ``side`` mesh."""
    s = style.lower()
    edge = _shade(fill.base, 0.25)
    if s == "twist":
        out = []
        for cx in (130, 270):
            out += [
                f'<ellipse cx="{cx}" cy="200" rx="68" ry="112" fill="{SILVER}" stroke="{edge}" stroke-width="{LW + 4}"/>',
                _line(f"M{cx - 40},140 Q{cx},200 {cx - 40},260 M{cx + 40},140 Q{cx},200 {cx + 40},260", LW_DETAIL),
            ]
        return _label(out, label)
    if s == "umbrella":
        return _label([
            _path("M60,230 Q60,110 200,100 Q340,110 340,230 Q270,214 200,230 Q130,214 60,230 Z", SILVER),
            _line("M200,100 L130,224 M200,100 L270,224 M200,100 L200,230", LW_DETAIL),
            _path("M60,230 Q130,214 200,230 Q270,214 340,230 L336,244 Q270,228 200,244 Q130,228 64,244 Z", paint),
            _line("M200,244 L200,330", LW + 6, stroke=INK),
            _line("M200,244 L200,330", LW + 2, stroke=edge),
        ], label)
    if s == "side":
        mesh = [_line(f"M{110 + 20 * i},120 L{110 + 20 * i},290", 1.0, stroke=_tint(fill.base, 0.3)) for i in range(10)]
        return _label([
            _path("M100,110 L300,110 Q320,110 316,140 L300,300 L100,300 Q84,300 84,280 L90,130 Q92,110 100,110 Z", "#3b3f45", LW + 4),
            *mesh,
            _path("M100,110 L300,110 Q320,110 316,140 L300,300 L100,300 Q84,300 84,280 L90,130 Q92,110 100,110 Z", "none", LW + 2, stroke=paint),
        ], label)
    folds = [_path(f"M{60 + 28 * i},{120} L{88 + 28 * i},{120} L{88 + 28 * i},{290} L{60 + 28 * i},{290} Z",
                   SILVER if i % 2 == 0 else _shade(SILVER, 0.12), LW_DETAIL) for i in range(10)]
    return _label([
        *folds,
        _path("M60,120 L340,120 L340,290 L60,290 Z", "none", LW),
        _path("M186,190 L214,190 L214,226 L186,226 Z", paint, LW_DETAIL),
        _line("M60,120 L340,120 M60,290 L340,290", LW + 2, stroke=paint),
    ], label)


SHAPES = {
    "seat_cover": seat_cover,
    "floor_mat": floor_mat,
    "trunk_liner": trunk_liner,
    "steering_wheel_cover": steering_wheel_cover,
    "sun_shade": sun_shade,
}
register(SHAPES)
