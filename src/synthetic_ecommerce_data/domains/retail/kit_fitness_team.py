"""Fitness, team-sport and racket-sport shapes for the retail drawing kit (gen#959, slice 2).

Each product is drawn as what it is, so a weight plate never reads as a ball and a pickleball
paddle never as a table tennis bat. Outlines are the kit's ink, and the record's fill (color and
pattern) paints the main surface: a bike's frame, a plate's face, a bench's pad, a ball's cover, a
guard's shell, a stick's shaft, a paddle's face and a bat's rubber.

=================  =========================================  ===================================
shape              draws                                      params
=================  =========================================  ===================================
exercise_bike      a bike from the side on its floor bar      bike_style (upright, recumbent,
                                                              folding)
weight_plate       a plate face on, its hub and its grips     material (cast iron, rubber
                                                              coated, urethane)
weight_bench       a bench from the side on its legs          bench_type (flat, adjustable,
                                                              decline)
basketball         a ball with its eight channels             cover (rubber, composite,
                                                              full-grain leather)
volleyball         a ball of curved panel bands               play (indoor, beach)
shin_guard         a shield from the front                    guard_type (slip-in, ankle, sleeve)
hockey_stick       a stick on the slant with its blade        hockey_type (ice, street)
pickleball_paddle  a paddle face on with its grip             face (graphite, fiberglass, carbon
                                                              fiber, wood)
table_tennis_bat   a round bat face on with its handle        blade (wood, carbon)
=================  =========================================  ===================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a bench's ``bench_type`` or a ball's ``cover`` draws what it states (gen#512). A
drawing never prints a weight or a size: a style's SKUs share one image per colorway. Every param
is a string with a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

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
from synthetic_ecommerce_data.domains.retail.kit_sports import POLE, _ell, _label, _rect, _tilted

#: The dark rubber of a grip, a pad's cushion and a bike's floor bar.
GRIP = "#33363c"
#: The steel of a plate's hub and a bench's frame.
STEEL = "#b8bec6"
#: The plain wood of a bat's handle and a paddle's or a stick's grain.
WOOD = "#d9b27c"


def exercise_bike(paint: str, fill: Fill, label: str | None, bike_style: str = "upright") -> list[str]:
    """A bike from the side: an ``upright`` bike with a front flywheel and a high saddle, a
    ``recumbent`` one with a low seat and a backrest, or a ``folding`` one on an X frame."""
    kind = bike_style.lower()
    dark = _shade(fill.base, 0.35)
    out = [_rect(60, 318, 280, 14, GRIP, 6), _rect(80, 306, 40, 14, GRIP, 5), _rect(280, 306, 40, 14, GRIP, 5)]
    if kind == "recumbent":
        out += [
            _path("M110,310 L150,240 L290,240 L310,310 Z", paint),
            _rect(118, 200, 92, 30, GRIP, 10), _rect(104, 120, 26, 96, GRIP, 10),
            _ell(300, 236, 34, 34, dark), _line("M300,236 L326,222", 5, stroke=POLE),
            _line("M246,240 L270,150 L300,150", 6, stroke=POLE),
        ]
    elif kind == "folding":
        out += [
            _path("M110,310 L270,110 L290,120 L134,316 Z", paint),
            _path("M290,310 L150,140 L130,150 L268,316 Z", paint),
            _ell(200, 226, 30, 30, dark), _rect(126, 128, 56, 18, GRIP, 8),
            _line("M270,110 L300,90 L320,92", 6, stroke=POLE),
        ]
    else:
        out += [
            _path("M120,310 L170,150 L196,150 L160,310 Z", paint),
            _path("M160,300 L300,300 L280,250 L176,250 Z", paint),
            _ell(290, 250, 50, 50, dark), _ell(290, 250, 14, 14, POLE),
            _rect(140, 128, 64, 20, GRIP, 8), _line("M276,206 L250,120 L292,104", 6, stroke=POLE),
            _ell(212, 276, 16, 16, POLE, LW_DETAIL),
        ]
    out.append(_highlight("M130,300 L170,170", 4, 0.4))
    return _label(out, label)


def weight_plate(paint: str, fill: Fill, label: str | None, material: str = "cast iron") -> list[str]:
    """A plate face on: a ``cast iron`` plate shows its raised rim, a ``rubber coated`` one three
    grip holes, and a ``urethane`` one a deep face with a steel hub insert."""
    kind = material.lower()
    dark = _shade(fill.base, 0.35)
    out = [_ell(200, 190, 140, 140, paint)]
    if kind == "rubber coated":
        out += [_ell(200 + dx, 190 + dy, 22, 22, "#ffffff", LW_DETAIL) for dx, dy in ((0, -88), (76, 44), (-76, 44))]
    elif kind == "urethane":
        out += [_ell(200, 190, 112, 112, _tint(fill.base, 0.25), LW_DETAIL), _ell(200, 190, 50, 50, STEEL)]
    else:
        out += [_ell(200, 190, 124, 124, "none", 4), _ell(200, 190, 60, 60, dark, LW_DETAIL)]
    out += [_ell(200, 190, 24, 24, "#ffffff"), _highlight("M110,120 Q140,80 190,70", 5, 0.5)]
    return _label(out, label)


def weight_bench(paint: str, fill: Fill, label: str | None, bench_type: str = "flat") -> list[str]:
    """A bench from the side: a ``flat`` pad on two legs, an ``adjustable`` one whose back pad
    rises on a ladder, or a ``decline`` one that slopes down to a leg roller."""
    kind = bench_type.lower()
    out = [_rect(70, 310, 260, 12, STEEL, 5)]
    if kind == "adjustable":
        out += [
            _line("M120,310 L150,230 M290,310 L280,230", 8, stroke=STEEL),
            _rect(200, 210, 110, 26, paint, 10),
            _path("M90,150 L110,140 L210,214 L196,232 Z", paint),
            _line("M180,230 L170,280 L200,300", 6, stroke=POLE),
        ]
    elif kind == "decline":
        out += [
            _line("M110,310 L120,270 M300,310 L300,180", 8, stroke=STEEL),
            _path("M80,250 L90,236 L320,170 L314,190 Z", paint),
            _ell(300, 140, 18, 18, GRIP), _ell(334, 140, 18, 18, GRIP),
        ]
    else:
        out += [_line("M110,310 L120,232 M290,310 L280,232", 8, stroke=STEEL), _rect(70, 206, 260, 28, paint, 10)]
    out.append(_highlight("M90,214 L180,214", 4, 0.4))
    return _label(out, label)


def basketball(paint: str, fill: Fill, label: str | None, cover: str = "rubber") -> list[str]:
    """A ball with its channels: a ``rubber`` ball has deep wide channels and a pebbled face, a
    ``composite`` one medium channels, and a ``full-grain leather`` one thin channels."""
    kind = cover.lower()
    width = {"rubber": 7.0, "composite": 4.5}.get(kind, 2.6)
    out = [_ell(200, 190, 130, 130, paint)]
    for d in ("M70,190 L330,190", "M200,60 L200,320", "M108,98 Q200,190 108,282", "M292,98 Q200,190 292,282"):
        out.append(_line(d, width, stroke="#1d1d1f"))
    if kind == "rubber":
        out += [_ell(x, y, 3, 3, _shade(fill.base, 0.3), 0) for x, y in ((150, 140), (250, 140), (150, 240), (250, 240), (230, 110), (170, 270))]
    out.append(_highlight("M120,120 Q150,80 200,72", 5, 0.5))
    return _label(out, label)


def volleyball(paint: str, fill: Fill, label: str | None, play: str = "indoor") -> list[str]:
    """A ball of curved panel bands: an ``indoor`` ball has three bands of glued panels, a
    ``beach`` one is softer, with stitched seams."""
    kind = play.lower()
    dark = _shade(fill.base, 0.35)
    out = [_ell(200, 190, 130, 130, "#ffffff"), _path("M200,60 Q120,150 160,300 Q90,250 76,170 Q110,90 200,60 Z", paint),
           _path("M318,140 Q230,170 210,318 Q300,290 326,210 Z", paint)]
    seams = ("M200,60 Q260,140 318,140", "M160,300 Q190,260 210,318", "M76,170 Q170,190 240,240")
    extra = ' stroke-dasharray="6 6"' if kind == "beach" else ""
    out += [_line(d, 3 if kind == "beach" else 2.4, extra, dark) for d in seams]
    out.append(_highlight("M120,110 Q150,80 190,72", 5, 0.5))
    return _label(out, label)


def shin_guard(paint: str, fill: Fill, label: str | None, guard_type: str = "slip-in") -> list[str]:
    """A shield from the front: a ``slip-in`` guard alone, an ``ankle`` guard with its ankle cups
    and strap, or a ``sleeve`` guard held in a fabric sleeve."""
    kind = guard_type.lower()
    dark = _shade(fill.base, 0.35)
    out = []
    if kind == "sleeve":
        out.append(_rect(130, 50, 140, 260, _tint(fill.base, 0.5), 30, LW_DETAIL))
    out.append(_path("M150,60 Q200,40 250,60 L262,240 Q200,280 138,240 Z", paint))
    out += [_line("M170,90 Q200,80 230,90 M168,140 Q200,130 232,140 M166,190 Q200,180 234,190", LW_DETAIL, stroke=dark)]
    if kind == "ankle":
        out += [_ell(150, 290, 26, 22, paint), _ell(250, 290, 26, 22, paint), _rect(130, 316, 140, 16, GRIP, 6)]
    out.append(_highlight("M160,70 L162,220", 4, 0.4))
    return _label(out, label)


def hockey_stick(paint: str, fill: Fill, label: str | None, hockey_type: str = "ice") -> list[str]:
    """A stick on the slant: an ``ice`` stick ends in a low curved blade with tape, and a
    ``street`` stick in a wide moulded plastic blade."""
    kind = hockey_type.lower()
    parts = [_rect(40, 192, 60, 16, GRIP, 6), _path("M100,192 L300,192 L300,208 L100,208 Z", paint)]
    if kind == "street":
        parts.append(_path("M296,192 L310,192 Q330,230 380,236 L384,262 Q312,262 292,208 Z", _tint(fill.base, 0.3)))
        parts += [_line(f"M{316 + 14 * i},{222 + 8 * i} L{314 + 14 * i},{250}", LW_DETAIL, stroke=_shade(fill.base, 0.4)) for i in range(4)]
    else:
        parts.append(_path("M296,192 L310,192 Q322,226 372,232 L374,248 Q308,250 292,208 Z", paint))
        parts.append(_path("M318,214 Q330,232 362,236 L362,244 Q324,244 312,220 Z", "#ffffff", LW_DETAIL))
    return _label(_tilted(parts, 38), label)


def pickleball_paddle(paint: str, fill: Fill, label: str | None, face: str = "graphite") -> list[str]:
    """A paddle face on: a ``graphite`` or ``carbon fiber`` face shows its weave, ``fiberglass``
    a glossy sheen, and ``wood`` its grain; the grip is wrapped below."""
    kind = face.lower()
    dark = _shade(fill.base, 0.35)
    out = [_rect(186, 250, 28, 90, GRIP, 8), _rect(120, 60, 160, 200, paint, 50)]
    if kind in ("graphite", "carbon fiber"):
        step = 18 if kind == "graphite" else 12
        out += [_line(f"M{132 + step * i},76 L{132 + step * i},244", LW_DETAIL, ' stroke-opacity=".35"', dark) for i in range(int(136 / step) + 1)]
    elif kind == "wood":
        out += [_line(f"M{140 + 24 * i},70 Q{150 + 24 * i},160 {140 + 24 * i},250", LW_DETAIL, stroke=WOOD) for i in range(6)]
    else:
        out.append(_highlight("M140,90 Q200,70 260,90", 8, 0.6))
    out.append(_rect(116, 56, 168, 208, "none", 52, 3))
    return _label(out, label)


def table_tennis_bat(paint: str, fill: Fill, label: str | None, blade: str = "wood") -> list[str]:
    """A round bat face on: the rubber is the SKU's color, and the handle shows a ``wood``
    blade's grain or a ``carbon`` blade's dark weave layer at its edge."""
    kind = blade.lower()
    out = [_rect(182, 230, 36, 110, WOOD, 10), _ell(200, 150, 100, 110, paint)]
    if kind == "carbon":
        out += [_line("M184,250 L216,250 M184,270 L216,270 M184,290 L216,290", 3, stroke=GRIP), _ell(200, 150, 104, 114, "none", 3.5)]
    else:
        out += [_line(f"M{190 + 8 * i},240 L{190 + 8 * i},334", LW_DETAIL, ' stroke-opacity=".5"', _shade(WOOD, 0.4)) for i in range(3)]
    out.append(_highlight("M130,110 Q160,60 210,52", 5, 0.5))
    return _label(out, label)


SHAPES = {
    "exercise_bike": exercise_bike,
    "weight_plate": weight_plate,
    "weight_bench": weight_bench,
    "basketball": basketball,
    "volleyball": volleyball,
    "shin_guard": shin_guard,
    "hockey_stick": hockey_stick,
    "pickleball_paddle": pickleball_paddle,
    "table_tennis_bat": table_tennis_bat,
}
register(SHAPES)
