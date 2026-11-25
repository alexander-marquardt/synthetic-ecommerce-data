"""The tools of the sewing and knitting range for the retail drawing kit (gen#1118, cut 2).

================  ===========================================  =============================
shape             draws                                        params
================  ===========================================  =============================
sewing_machine    a machine's arm, pillar and bed in the        machine_type (mechanical,
                  SKU's color, its needle over the plate, a     computerized, heavy duty,
                  handwheel and a spool pin: dials for a        mini)
                  mechanical one, a screen and buttons for a
                  computerized one, a steel face plate for a
                  heavy duty one, and a small body for a mini
knitting_needles  a pair of straight needles crossed, two       needle_type (straight,
                  tips joined by a cable, or a set of four      circular, double pointed),
                  double pointed needles, a sheen for metal     material (aluminum, plastic)
crochet_hook      a hook with its notch at the tip and a flat   handle (inline, soft grip),
                  thumb rest, or a thick ribbed soft grip       material (aluminum, plastic)
                  handle, a sheen for metal
================  ===========================================  =============================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a machine's type or a needle's kind draws what it states (gen#512). A needle's or a
hook's size in millimeters is its SKU axis (``size_axes.AXES``): :mod:`size_ladder` scales the
drawing by it, so the kit draws one size.
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

#: The bare steel of a needle bar, a presser foot and a heavy duty machine's face plate.
STEEL = "#b8bec6"
#: The green glass of a computerized machine's screen.
SCREEN = "#9fd3c7"
#: The materials that shine: a metal needle or hook carries a highlight along its shaft.
METAL = ("aluminum", "steel")


def sewing_machine(
    paint: str, fill: Fill, label: str | None, machine_type: str = "mechanical"
) -> list[str]:
    """A sewing machine from the front: the bed, the pillar at the right and the arm across the
    top in the machine's color, the head at the left with its needle over the plate, a
    handwheel and a spool pin. ``machine_type`` shows on the pillar: two dials (mechanical), a
    screen and a row of buttons (computerized), a steel face plate and a large handwheel (heavy
    duty); a mini is the same machine at two thirds of the size with one dial."""
    k = 0.66 if machine_type == "mini" else 1.0
    ox, oy = (68, 104) if machine_type == "mini" else (0, 0)

    def x(v: float) -> float:
        return ox + v * k

    def y(v: float) -> float:
        return oy + v * k

    shade = _shade(fill.base, 0.2)
    wheel = 40 if machine_type == "heavy duty" else 32
    out = [
        _rect(x(296), y(48), 10 * k, 46 * k, STEEL, 2, LW_DETAIL),
        _rect(x(284), y(60), 34 * k, 26 * k, PAPER, 4, LW_DETAIL),
        _ell(x(352), y(170), 12 * k, wheel * k, shade),
        _rect(x(54), y(296), 300 * k, 44 * k, paint, 8),
        _rect(x(266), y(112), 80 * k, 196 * k, paint, 10),
        _rect(x(70), y(100), 276 * k, 70 * k, paint, 18),
        _rect(x(70), y(100), 66 * k, 150 * k, paint, 12),
        _rect(x(94), y(250), 12 * k, 34 * k, STEEL, 2, LW_DETAIL),
        _line(f"M{x(100):.1f},{y(284):.1f} L{x(100):.1f},{y(300):.1f}", 1.4),
        _rect(x(84), y(284), 36 * k, 8 * k, STEEL, 2, LW_DETAIL),
        _rect(x(150), y(304), 70 * k, 12 * k, STEEL, 2, LW_DETAIL),
    ]
    if machine_type == "computerized":
        out.append(_rect(x(278), y(132), 56 * k, 40 * k, SCREEN, 4, LW_DETAIL))
        out += [_rect(x(280 + 19 * i), y(188), 14 * k, 12 * k, PAPER, 3, LW_DETAIL)
                for i in range(3)]  # fmt: skip
    elif machine_type == "heavy duty":
        out.append(_rect(x(70), y(150), 276 * k, 16 * k, STEEL, 2, LW_DETAIL))
        out.append(_ell(x(306), y(220), 24 * k, 24 * k, PAPER, LW_DETAIL))
        out.append(_line(f"M{x(306):.1f},{y(220):.1f} L{x(318):.1f},{y(204):.1f}", 2.0))
    else:
        dials = ((306, 168, 22),) if machine_type == "mini" else ((306, 168, 22), (306, 238, 16))
        for cx, cy, r in dials:
            out.append(_ell(x(cx), y(cy), r * k, r * k, PAPER, LW_DETAIL))
            out.append(_line(f"M{x(cx):.1f},{y(cy):.1f} L{x(cx):.1f},{y(cy - r + 4):.1f}", 2.0))
    out.append(_highlight(f"M{x(90):.1f},{y(116):.1f} L{x(250):.1f},{y(116):.1f}", 5, 0.4))
    return _label(out, label)


def _needle(
    x0: float, y0: float, x1: float, y1: float, width: float, paint: str, both: bool = False
) -> str:
    """One needle from ``(x0, y0)`` to its point at ``(x1, y1)``, ``width`` thick; a double
    pointed one has a point at each end."""
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    nx, ny = -uy * width / 2, ux * width / 2
    tip = width * 2.4
    bx, by = x1 - ux * tip, y1 - uy * tip
    if both:
        ax, ay = x0 + ux * tip, y0 + uy * tip
        pts = [(x0, y0), (ax + nx, ay + ny), (bx + nx, by + ny), (x1, y1),
               (bx - nx, by - ny), (ax - nx, ay - ny)]  # fmt: skip
    else:
        pts = [(x0 + nx, y0 + ny), (bx + nx, by + ny), (x1, y1), (bx - nx, by - ny),
               (x0 - nx, y0 - ny)]  # fmt: skip
    return _path("M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts) + " Z", paint)


def _sheen(x0: float, y0: float, x1: float, y1: float, material: str) -> list[str]:
    """A highlight along a metal shaft; a plastic one is matte."""
    if material not in METAL:
        return []
    return [_highlight(f"M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}", 2.4, 0.6)]


def knitting_needles(
    paint: str,
    fill: Fill,
    label: str | None,
    needle_type: str = "straight",
    material: str = "aluminum",
) -> list[str]:
    """Knitting needles in the SKU's color by ``needle_type``: a pair of straight needles
    crossed, each with a knob at its end; two short tips joined by a looped cable (circular); a
    set of four short needles pointed at both ends (double pointed). A metal needle shines."""
    out: list[str] = []
    if needle_type == "circular":
        cable = _shade(fill.base, 0.35)
        out.append(_line("M150,236 C60,300 120,380 200,372 C280,380 340,300 250,236", 5.0,
                         stroke=cable))  # fmt: skip
        for x0, y0, x1, y1 in ((150, 236, 110, 70), (250, 236, 290, 70)):
            out.append(_rect(x0 - 9, y0 - 4, 18, 20, _shade(fill.base, 0.15), 4, LW_DETAIL))
            out.append(_needle(x0, y0, x1, y1, 14, paint))
            out += _sheen(x0, y0 - 20, x1 + (4 if x1 < x0 else -4), y1 + 30, material)
    elif needle_type == "double pointed":
        for i in range(4):
            dx = 46 * i
            out.append(_needle(70 + dx, 330, 170 + dx, 70, 11, paint, both=True))
            out += _sheen(84 + dx, 300, 156 + dx, 104, material)
    else:
        for x0, y0, x1, y1 in ((70, 340, 330, 60), (330, 340, 70, 60)):
            out.append(_needle(x0, y0, x1, y1, 14, paint))
            out.append(_ell(x0, y0, 16, 16, _shade(fill.base, 0.2)))
            out += _sheen(x0 + (14 if x1 > x0 else -14), y0 - 24, (x0 + x1) / 2, (y0 + y1) / 2,
                          material)  # fmt: skip
    return _label(out, label)


def crochet_hook(
    paint: str,
    fill: Fill,
    label: str | None,
    handle: str = "inline",
    material: str = "aluminum",
) -> list[str]:
    """A crochet hook lying across the frame in the SKU's color: the shaft with the hook's
    notch cut at its left tip and a flat thumb rest at its middle, and for a ``soft grip``
    handle a thick ribbed grip over its right half. A metal hook shines."""
    cy, half = 200, 9
    out = [
        _path(
            f"M46,{cy - half + 4} Q40,{cy} 50,{cy + half} L340,{cy + half} Q352,{cy} 340,"
            f"{cy - half} L72,{cy - half} L64,{cy - 2} L58,{cy - half + 1} Z",
            paint,
        ),  # fmt: skip
        _rect(160, cy - 16, 64, 32, _shade(fill.base, 0.1), 6, LW_DETAIL),
    ]
    out += _sheen(80, cy - 4, 330, cy - 4, material)
    if handle == "soft grip":
        grip = _shade(fill.base, 0.4)
        out.append(_rect(236, cy - 26, 124, 52, grip, 24))
        out += [_line(f"M{x},{cy - 22} L{x},{cy + 22}", 1.4, stroke=PAPER)
                for x in range(256, 350, 14)]  # fmt: skip
    return _label(out, label)


SHAPES = {
    "sewing_machine": sewing_machine,
    "knitting_needles": knitting_needles,
    "crochet_hook": crochet_hook,
}
register(SHAPES)
