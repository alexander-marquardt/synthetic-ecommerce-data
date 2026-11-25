"""The light and the parts a breadth product is drawn with (#1216).

What :mod:`.breadth_products` and :mod:`.breadth_hardware` share: a body lit on its left and shaded
on its right, a thread, a hex, a drum, and the laying of a rod corner to corner. Figures are laid
out in a 1.64 by 2.0 box, the figure area's own proportion, y down.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence

from synthetic_ecommerce_data.core.drawing.model import Disc, Figure, Lines, Point, Poly, arc
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn

#: Colors a product is sold in, which no Material or Finish of the record says.
GRIP_RED = "#b5342b"
GRIP_BLUE = "#2f6fa8"
RUBBER = "#3a3d42"
PAPER_LABEL = "#f4efe2"
OIL = "#c99a2e"
SAFETY = "#e0a526"

BOX = (1.64, 2.0)
#: The turn, in degrees, at which a rod's smallest fill over its angles is largest.
LAID = 34


# --- light: every body is drawn with a highlight on its left and a shadow on its right ----------


def light(fig: Figure, box: tuple[float, float, float, float], across: bool = False) -> None:
    """A gloss strip and a shade strip over ``box``: down its sides, or ``across`` it."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if across:
        fig.rect(x0, y0 + 0.12 * h, x1, y0 + 0.27 * h, "gloss")
        fig.rect(x0, y0 + 0.7 * h, x1, y1, "shade")
        return
    fig.rect(x0 + 0.12 * w, y0, x0 + 0.27 * w, y1, "gloss")
    fig.rect(x0 + 0.7 * w, y0, x1, y1, "shade")


def col(fig: Figure, x0, y0, x1, y1, role="part", fill=None) -> None:
    """An upright round body from the side."""
    fig.rect(x0, y0, x1, y1, role, fill)
    light(fig, (x0, y0, x1, y1))


def bar(fig: Figure, x0, y0, x1, y1, role="part", fill=None) -> None:
    """A lying round body from the side."""
    fig.rect(x0, y0, x1, y1, role, fill)
    light(fig, (x0, y0, x1, y1), across=True)


def slab(fig: Figure, pts: Sequence[Point], role="part", fill=None, t=0.06) -> None:
    """A thick plate: its face, a highlight along its top-left edges and a shadow along its
    bottom-right ones, each ``t`` wide, so any outline is lit from the top left."""
    fig.poly(pts, role, fill)
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sign = 1 if area > 0 else -1
    for i in range(n):
        (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
        length = math.hypot(bx - ax, by - ay)
        if length < 3 * t:
            continue
        nx, ny = -(by - ay) / length * sign, (bx - ax) / length * sign  # inward
        lit = nx * 0.6 + ny * 0.8
        if abs(lit) < 0.25:
            continue
        inner = ((bx + nx * t, by + ny * t), (ax + nx * t, ay + ny * t))
        fig.poly(((ax, ay), (bx, by), *inner), "gloss" if lit > 0 else "shade")


def disc(
    fig: Figure, c: Point, r: float, role="part", fill=None, bore: float = 0.0, steps: int = 12
) -> None:
    """A round face: a highlight crescent up left, a shadow crescent down right, each drawn in
    ``steps`` (a small face needs few, and a drawing has a size cap)."""
    fig.disc(c, r, role, fill)
    for start, end, kind, outer in ((-30, 120, "shade", 1.0), (170, 280, "gloss", 0.92)):
        inner = max(outer - 0.22, (bore / r) if r else 0)
        rim = arc(c, r * outer, start, end, steps)
        fig.poly([*rim, *arc(c, r * inner, end, start, steps)], kind)


def ell(c: Point, rx: float, ry: float, start=0.0, end=360.0, steps=24) -> list[Point]:
    span = [math.radians(start + (end - start) * k / steps) for k in range(steps + 1)]
    return [(c[0] + rx * math.cos(a), c[1] + ry * math.sin(a)) for a in span]


def drum(fig: Figure, x0, y0, x1, y1, ry, role="part", fill=None, top="plain") -> None:
    """A round body seen from a little above: its side and its top face."""
    cx, rx = (x0 + x1) / 2, (x1 - x0) / 2
    side = [(x0, y0 + ry), (x1, y0 + ry), *ell((cx, y1 - ry), rx, ry, 0, 180, 14)]
    fig.poly(side, role, fill)
    for a, b, kind in ((0.12, 0.27, "gloss"), (0.7, 1.0, "shade")):
        xs = [x0 + (x1 - x0) * (a + (b - a) * k / 4) for k in range(5)]
        low = [(x, y1 - ry + ry * math.sqrt(max(0.0, 1 - ((x - cx) / rx) ** 2))) for x in xs]
        fig.poly([(xs[-1], y0 + ry), (xs[0], y0 + ry), *low], kind)
    fig.poly(ell((cx, y0 + ry), rx, ry), top)


def band(fig: Figure, x0, y0, x1, y1, ry, fill) -> None:
    """A label wrapped round a drum: it sags like the drum's own edge."""
    cx, rx = (x0 + x1) / 2, (x1 - x0) / 2
    fig.poly(
        [*ell((cx, y0), rx, ry, 180, 0, 12), *ell((cx, y1), rx, ry, 0, 180, 12)], "handle", fill
    )
    sides = [ell((cx, y), rx, ry, 0, 66, 6) for y in (y0, y1)]
    fig.poly([*sides[0], *sides[1][::-1]], "shade")


def thread(fig: Figure, x0, y0, x1, y1, pitch=0.1) -> None:
    """A threaded shank: its body, lit, and its crests."""
    col(fig, x0, y0, x1, y1)
    count = int((y1 - y0) / pitch)
    fig.lines(((x0, y0 + pitch * (k + 0.7)), (x1, y0 + pitch * (k + 0.2))) for k in range(count))


def hexes(fig: Figure, x0, y0, x1, y1, role="part") -> None:
    """A hex seen from the side: three faces, the middle one twice as wide."""
    w = x1 - x0
    fig.rect(x0, y0, x1, y1, role)
    fig.rect(x0, y0, x0 + w / 4, y1, "gloss")
    fig.rect(x1 - w / 4, y0, x1, y1, "shade")
    fig.lines(((x, y0), (x, y1)) for x in (x0 + w / 4, x1 - w / 4))


def hexagon(c: Point, r: float, start: float = 30.0) -> list[Point]:
    return [
        (c[0] + r * math.cos(math.radians(start + 60 * k)),
         c[1] + r * math.sin(math.radians(start + 60 * k)))
        for k in range(6)
    ]  # fmt: skip


def mirror(pts: Iterable[Point]) -> list[Point]:
    return [(BOX[0] - x, y) for x, y in pts][::-1]


def laid(fig: Figure, degrees: float) -> Figure:
    """``fig`` turned: a thin product laid corner to corner."""
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)

    def at(p):
        return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)

    out = Figure(size_in=fig.size_in)
    for shape in fig.shapes:
        if isinstance(shape, Poly):
            out.poly([at(p) for p in shape.points], shape.role, shape.fill)
        elif isinstance(shape, Disc):
            out.disc(at(shape.centre), shape.radius, shape.role, shape.fill)
        elif isinstance(shape, Lines):
            out.lines([(at(p), at(q)) for p, q in shape.segments], shape.role)
        else:
            raise TypeError(f"{type(shape).__name__} cannot be laid")
    return out


def done(fig: Figure) -> Drawn:
    return Drawn(fig, "nominal")


def new() -> Figure:
    return Figure(size_in=2.0)
