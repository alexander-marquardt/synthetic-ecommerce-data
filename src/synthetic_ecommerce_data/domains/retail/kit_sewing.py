"""Sewing and knitting for the retail drawing kit (gen#1118): thread, yarn and fabric.

=============  ==============================================  ===============================
shape          draws                                           params
=============  ==============================================  ===============================
sewing_thread  a spool between two flanges, or a cone from      spool_length (meters), style
               1000 m up: the thread wound on it in the         (all purpose, quilting,
               thread's color, its windings spaced by the       topstitch, embroidery),
               style, a sheen by the material and a loose end   material (polyester, cotton,
                                                                rayon)
yarn           a ball of yarn wound across itself under a       yarn_weight (4 ply, dk, aran,
               paper ball band: the strand's thickness by the   chunky), material (merino wool,
               weight, a fuzzy halo for a wool and a sheen for  cotton, acrylic, alpaca)
               an acrylic
fabric         three folded layers of a fabric, stacked, the    style (poplin, canvas, jersey,
               weave on each face by the style and a slub or a  crepe), material (cotton, linen,
               sheen by the material                            polyester, viscose)
=============  ==============================================  ===============================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a thread's style or a yarn's weight draws what it states (gen#512). A spool's
length has a unit, so the scaled build never changes it, and the figure it draws stays true.
"""

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    PAPER,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: The pale plastic of a spool's flanges and a cone's base.
FLANGE = "#efe9dc"
#: The gap between two windings of a thread, by its style: a topstitch thread is the thickest.
THREAD_GAP = {"all purpose": 8, "quilting": 10, "topstitch": 14, "embroidery": 6}
#: The sheen a thread's fiber gives its windings: a rayon shines, a cotton is matte.
SHEEN = {"rayon": 0.7, "polyester": 0.45, "cotton": 0.0, "acrylic": 0.45, "viscose": 0.5}
#: A yarn's strand width and the gap between its wraps, by its weight.
STRAND = {"4 ply": (1.4, 9), "dk": (2.4, 13), "aran": (3.4, 17), "chunky": (5.2, 24)}
#: The length of the fuzz a wool shows round its ball; a cotton and an acrylic show none.
FUZZ = {"merino wool": 6, "alpaca": 11}


def _spool_height(meters: int) -> float:
    """The wound height of a spool: a 100 m spool is short, a 500 m one tall."""
    return 120 + 100 * min(meters, 500) / 500


def sewing_thread(
    paint: str,
    fill: Fill,
    label: str | None,
    spool_length: str = "500",
    style: str = "all purpose",
    material: str = "polyester",
) -> list[str]:
    """A spool of sewing thread between its flanges (a cone from 1000 m): the thread wound in its
    color, the windings spaced by ``style``, a sheen by ``material`` and a loose end."""
    meters = int(float(spool_length))
    gap = THREAD_GAP.get(style, 8)
    wind = _shade(fill.base, 0.28)
    out: list[str] = []
    if meters >= 1000:
        top, bottom = 76, 330
        out += [
            _path(f"M126,{bottom} L274,{bottom} L234,{top} L166,{top} Z", paint),
            _rect(112, bottom - 4, 176, 30, FLANGE, 6),
            _rect(180, top - 22, 40, 26, FLANGE, 4),
        ]
        for y in range(top + gap, bottom - 4, gap):
            half = 34 + 40 * (y - top) / (bottom - top)
            out.append(_line(f"M{200 - half:.1f},{y} L{200 + half:.1f},{y}", 1.0, stroke=wind))
        shine_x0, shine_y = 160, (top + 20, bottom - 20)
        end = f"M262,{bottom - 60} C300,{bottom - 40} 296,{bottom + 10} 330,{bottom + 18}"
    else:
        height = _spool_height(meters)
        top, bottom = 212 - height / 2, 212 + height / 2
        out += [
            _rect(122, top, 156, height, paint, 3),
            _rect(100, top - 20, 200, 22, FLANGE, 8),
            _rect(100, bottom - 2, 200, 22, FLANGE, 8),
            _ell(200, top - 9, 16, 5, "#5a5a60", LW_DETAIL),
        ]
        for y in range(int(top + gap), int(bottom - 2), gap):
            out.append(_line(f"M124,{y} L276,{y}", 1.0, stroke=wind))
        shine_x0, shine_y = 140, (top + 12, bottom - 12)
        end = f"M276,{bottom - 30:.1f} C310,{bottom - 10:.1f} 300,{bottom + 30:.1f} 336,{bottom + 36:.1f}"  # noqa: E501
    out.append(_line(end, 2.4, stroke=fill.base))
    sheen = SHEEN.get(material, 0.0)
    if sheen:
        out.append(
            _highlight(f"M{shine_x0},{shine_y[0]:.1f} L{shine_x0},{shine_y[1]:.1f}", 8, sheen)
        )
    return _label(out, label)


def _chord(r: float, d: float, angle: float, cx: float, cy: float, bow: float) -> str:
    """One wrap of a ball's yarn: the chord ``d`` from the center at ``angle``, bowed outward."""
    ux, uy = math.cos(angle), math.sin(angle)
    nx, ny = -uy, ux
    half = math.sqrt(max(r * r - d * d, 0.0))
    x0, y0 = cx + nx * d - ux * half, cy + ny * d - uy * half
    x1, y1 = cx + nx * d + ux * half, cy + ny * d + uy * half
    qx, qy = cx + nx * d * bow, cy + ny * d * bow
    return f"M{x0:.1f},{y0:.1f} Q{qx:.1f},{qy:.1f} {x1:.1f},{y1:.1f}"


def yarn(
    paint: str,
    fill: Fill,
    label: str | None,
    yarn_weight: str = "dk",
    material: str = "merino wool",
) -> list[str]:
    """A ball of yarn: the ball in the yarn's color, wound across itself in two directions with a
    strand as thick as ``yarn_weight``, a paper ball band round its middle, a fuzzy halo for a
    wool, a sheen for an acrylic and a loose end trailing off."""
    cx, cy, r = 200, 200, 128
    width, gap = STRAND.get(yarn_weight, STRAND["dk"])
    wrap = _shade(fill.base, 0.3)
    out: list[str] = []
    fuzz = FUZZ.get(material, 0)
    for i in range(48 if fuzz else 0):
        a = 2 * math.pi * i / 48
        x0, y0 = cx + r * math.cos(a), cy + r * math.sin(a)
        x1, y1 = cx + (r + fuzz) * math.cos(a + 0.05), cy + (r + fuzz) * math.sin(a + 0.05)
        out.append(_line(f"M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}", 1.2, stroke=wrap))
    out.append(_ell(cx, cy, r, r, paint))
    d = -r + gap
    while d < r - 4:
        out.append(_line(_chord(r - 3, d, -0.5, cx, cy, 1.12), width, stroke=wrap))
        d += gap
    d = -r * 0.55
    while d < r * 0.2:
        out.append(_line(_chord(r - 3, d, 0.9, cx, cy, 1.1), width, stroke=wrap))
        d += gap
    out.append(_rect(cx - 52, cy - r + 18, 104, 2 * r - 36, PAPER, 10, LW_DETAIL))
    out.append(_rect(cx - 36, cy - 30, 72, 60, _shade(fill.base, 0.05), 6, LW_DETAIL))
    out.append(_line(f"M{cx + 90},{cy + 92} C{cx + 130},{cy + 120} {cx + 120},{cy + 160} {cx + 160},{cy + 168}",  # noqa: E501
                     width + 0.6, stroke=fill.base))  # fmt: skip
    if material == "acrylic":
        out.append(
            _highlight(f"M{cx - 96},{cy - 40} Q{cx - 90},{cy - 96} {cx - 40},{cy - 108}", 9, 0.5)
        )
    return _label(out, label)


def _weave(style: str, x0: float, y0: float, x1: float, y1: float, ink: str) -> list[str]:
    """The weave of one folded layer's face, in the box ``(x0, y0)`` to ``(x1, y1)``."""
    out: list[str] = []
    if style == "canvas":
        out += [
            _line(f"M{x},{y0} L{x},{y1}", 0.9, stroke=ink) for x in range(int(x0) + 8, int(x1), 9)
        ]
        out += [
            _line(f"M{x0},{y} L{x1},{y}", 0.9, stroke=ink) for y in range(int(y0) + 8, int(y1), 9)
        ]
    elif style == "jersey":
        for y in range(int(y0) + 10, int(y1) - 4, 12):
            for x in range(int(x0) + 8, int(x1) - 8, 14):
                out.append(_line(f"M{x},{y} L{x + 7},{y + 7} L{x + 14},{y}", 0.9, stroke=ink))
    elif style == "crepe":
        for y in range(int(y0) + 10, int(y1) - 4, 11):
            d = f"M{x0 + 6},{y}" + "".join(
                " q5,-4 10,0 q5,4 10,0" for _ in range(int((x1 - x0 - 12) // 20))
            )
            out.append(_line(d, 0.9, stroke=ink))
    return out


def fabric(
    paint: str, fill: Fill, label: str | None, style: str = "poplin", material: str = "cotton"
) -> list[str]:
    """Three folded layers of a fabric, stacked: each layer's face in the fabric's color, the
    fold rounded at the right, the weave of ``style`` on each face (a poplin plain, a canvas a
    grid, a jersey a knit, a crepe a crinkle), slubs for a linen and a sheen for a polyester."""
    ink = _shade(fill.base, 0.24)
    out: list[str] = []
    for i, y in enumerate((250, 172, 94)):
        x0, x1 = 64 + 6 * i, 316 + 6 * i
        out += [
            _path(
                f"M{x1},{y} C{x1 + 26},{y + 4} {x1 + 26},{y + 74} {x1},{y + 78}",
                _shade(fill.base, 0.16),
            ),
            _rect(x0, y, x1 - x0, 78, paint, 4),
        ]
        out += _weave(style, x0, y, x1, y + 78, ink)
        if material == "linen":
            out += [_line(f"M{x},{y + 16 + (x * 7) % 50} l14,0", 1.6, stroke=ink)
                    for x in range(int(x0) + 14, int(x1) - 20, 34)]  # fmt: skip
        if material in ("polyester", "viscose"):
            out.append(_highlight(f"M{x0 + 16},{y + 14} L{x0 + 120},{y + 14}", 6, 0.45))
    return _label(out, label)


SHAPES = {"sewing_thread": sewing_thread, "yarn": yarn, "fabric": fabric}
register(SHAPES)
