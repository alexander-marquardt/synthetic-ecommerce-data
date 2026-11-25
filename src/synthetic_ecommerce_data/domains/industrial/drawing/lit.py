"""Bodies with light on them, and the shapes they are cut from (#1215).

A body is an outline with a highlight band and a shadow band (the ``gloss`` and ``shade`` roles of
the drawing model). Figures are laid out in hundredths of an inch, y down, and written in inches by
:func:`inches`.
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.core.drawing.model import (
    Bars,
    Disc,
    Discs,
    Figure,
    Lines,
    Point,
    Poly,
    arc,
)


def clip(points: list[Point], axis: int, at: float, keep_below: bool) -> list[Point]:
    """``points`` cut at ``at`` on ``axis`` (0 is x, 1 is y): the part on one side of it."""
    out: list[Point] = []
    side = -1.0 if keep_below else 1.0
    for a, b in zip(points, [*points[1:], points[0]], strict=True):
        da, db = side * (a[axis] - at), side * (b[axis] - at)
        if da >= 0:
            out.append(a)
        if da * db < 0:
            t = da / (da - db)
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out


def lit(fig: Figure, points: list[Point], fill: str, across: bool = False) -> None:
    """A body in ``fill``, a highlight and a shadow in bands down it, or ``across`` it."""
    axis = 1 if across else 0
    low, high = min(p[axis] for p in points), max(p[axis] for p in points)
    fig.poly(points, "handle", fill)
    for start, end, light in ((0.08, 0.3, "gloss"), (0.68, 1.0, "shade")):
        band = clip(points, axis, low + start * (high - low), keep_below=False)
        fig.poly(clip(band, axis, low + end * (high - low), keep_below=True), light)


def block(x0: float, y0: float, x1: float, y1: float, cut: float) -> list[Point]:
    """A box with rounded corners."""
    out: list[Point] = []
    for cx, cy, start in (
        (x1 - cut, y0 + cut, -90), (x1 - cut, y1 - cut, 0),
        (x0 + cut, y1 - cut, 90), (x0 + cut, y0 + cut, 180),
    ):  # fmt: skip
        out += arc((cx, cy), cut, start, start + 90, 2)
    return out


def box(x0: float, y0: float, x1: float, y1: float) -> list[Point]:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def inches(fig: Figure, scale: float = 1.0) -> Figure:
    """``fig``, laid out in hundredths, in inches and times ``scale``; its size is its width."""

    def at(*values: float) -> tuple[float, ...]:
        return tuple(v * scale / 100 for v in values)

    shapes = []
    for s in fig.shapes:
        if isinstance(s, Poly):
            s = replace(s, points=tuple(at(*p) for p in s.points))
        elif isinstance(s, Disc):
            s = replace(s, centre=at(*s.centre), radius=at(s.radius)[0])
        elif isinstance(s, Discs):
            s = replace(s, centres=tuple(at(*c) for c in s.centres), radius=at(s.radius)[0])
        elif isinstance(s, Lines):
            s = replace(s, segments=tuple((at(*a), at(*b)) for a, b in s.segments))
        elif isinstance(s, Bars):
            s = replace(s, rects=tuple(at(*r) for r in s.rects))
        else:
            raise TypeError(f"{type(s).__name__} is not laid out in hundredths")
        shapes.append(s)
    out = Figure(shapes)
    x0, _, x1, _ = out.bounds()
    out.size_in = x1 - x0
    return out
