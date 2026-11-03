"""Shapes in the product's own units (inches), before they are placed on the sheet.

A kind's drawing function returns a :class:`Figure`: polygons, circles and
line work in inches, plus the product's characteristic size. :mod:`.sheet`
fits the figure into the sheet and writes it. Keeping the geometry in real
units until the last step is what makes "a longer length of cut is drawn
longer" true by construction rather than by tuning.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

Point = tuple[float, float]

#: How a shape is painted. ``part`` is the product's body: finish fill,
#: material hatch, brand outline. ``plain`` is a secondary surface (a shank, an
#: edge view): a paler fill, no hatch. ``hole`` is a bore or an arbor: the
#: paper shows through. ``dark`` is a recess (a socket, a drive). ``line`` is
#: line work only (flutes, thread crests). ``handle`` and ``grip`` take their
#: color from the shape itself. ``break`` is a drafting break's zigzag, line work
#: stroked at the outline's weight, solid; ``gap`` is the paper between a break's
#: two zigzags, unoutlined, so a shank's cut end follows its zigzag (#822).
ROLES = ("part", "plain", "hole", "dark", "line", "handle", "grip", "break", "gap")


@dataclass(frozen=True)
class Poly:
    points: tuple[Point, ...]
    role: str = "part"
    fill: str | None = None


@dataclass(frozen=True)
class Disc:
    centre: Point
    radius: float
    role: str = "part"
    fill: str | None = None


@dataclass(frozen=True)
class Lines:
    segments: tuple[tuple[Point, Point], ...]
    role: str = "line"


@dataclass(frozen=True)
class Dots:
    """Many small marks of one size, painted as ONE path: texture, cheaply."""

    centres: tuple[Point, ...]
    radius: float


@dataclass(frozen=True)
class Bars:
    """Many rectangles of one role, painted as ONE path: a part that repeats
    (a chain's link plates seen from above) costs a few bytes a copy rather
    than a styled element a copy. Each is ``(x0, y0, x1, y1)``."""

    rects: tuple[tuple[float, float, float, float], ...]
    role: str = "part"


@dataclass(frozen=True)
class Outlines:
    """Plain closed outlines painted as ONE path: the items behind a pack's top item (:func:`fan`)
    cost a few bytes each rather than a whole drawing each."""

    outlines: tuple[tuple[Point, ...], ...]


@dataclass
class Figure:
    """One product drawn in inches, and how big it is."""

    shapes: list[Poly | Disc | Lines | Dots | Bars | Outlines] = field(default_factory=list)
    #: The characteristic size, in inches, that the sheet's size cue reads.
    size_in: float = 1.0

    def poly(self, points, role: str = "part", fill: str | None = None) -> None:
        self.shapes.append(Poly(tuple(points), role, fill))

    def rect(self, x0: float, y0: float, x1: float, y1: float, role: str = "part", fill=None):
        self.poly(((x0, y0), (x1, y0), (x1, y1), (x0, y1)), role, fill)

    def disc(self, centre: Point, radius: float, role: str = "part", fill=None) -> None:
        self.shapes.append(Disc(centre, radius, role, fill))

    def lines(self, segments, role: str = "line") -> None:
        segments = tuple(segments)
        if segments:
            self.shapes.append(Lines(segments, role))

    def dots(self, centres, radius: float) -> None:
        centres = tuple(centres)
        if centres:
            self.shapes.append(Dots(centres, radius))

    def bars(self, rects, role: str = "part") -> None:
        rects = tuple(rects)
        if rects:
            self.shapes.append(Bars(rects, role))

    def bounds(self) -> tuple[float, float, float, float]:
        xs: list[float] = []
        ys: list[float] = []
        for shape in self.shapes:
            if isinstance(shape, Poly):
                xs.extend(p[0] for p in shape.points)
                ys.extend(p[1] for p in shape.points)
            elif isinstance(shape, Disc):
                xs.extend((shape.centre[0] - shape.radius, shape.centre[0] + shape.radius))
                ys.extend((shape.centre[1] - shape.radius, shape.centre[1] + shape.radius))
            elif isinstance(shape, Dots):
                xs.extend(c[0] for c in shape.centres)
                ys.extend(c[1] for c in shape.centres)
            elif isinstance(shape, Bars):
                for x0, y0, x1, y1 in shape.rects:
                    xs.extend((x0, x1))
                    ys.extend((y0, y1))
            elif isinstance(shape, Outlines):
                xs.extend(p[0] for outline in shape.outlines for p in outline)
                ys.extend(p[1] for outline in shape.outlines for p in outline)
            else:
                for a, b in shape.segments:
                    xs.extend((a[0], b[0]))
                    ys.extend((a[1], b[1]))
        if not xs:
            raise ValueError("an empty figure has no bounds")
        return min(xs), min(ys), max(xs), max(ys)


#: How far apart a pack's items stand, and the furthest one leans to either side.
FAN_STEP_DEG = 14.0
FAN_REACH_DEG = 55.0


def fan(figure: Figure, count: int) -> Figure:
    """``count`` of ``figure``, fanned about the foot of its long axis, as a pack is depicted.

    The figure itself stands on top, whole. The other ``count - 1`` lean out to alternate sides
    behind it, each as its bounding box: a drawing has a byte budget, and only the top item's
    detail can be seen anyway. Rotation carries a property here, the pack (gen#14 supersedes #5
    for this one use).
    """
    x0, y0, x1, y1 = figure.bounds()
    pivot = ((x0 + x1) / 2, y1) if y1 - y0 >= x1 - x0 else (x0, (y0 + y1) / 2)
    box = ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
    step = min(FAN_STEP_DEG, FAN_REACH_DEG / (count // 2))
    behind = []
    for k in range(1, count):
        angle = math.radians((k + 1) // 2 * step * (1 if k % 2 else -1))
        cos, sin = math.cos(angle), math.sin(angle)
        behind.append(
            tuple(
                (
                    pivot[0] + (x - pivot[0]) * cos - (y - pivot[1]) * sin,
                    pivot[1] + (x - pivot[0]) * sin + (y - pivot[1]) * cos,
                )
                for x, y in box
            )
        )
    return Figure([Outlines(tuple(behind)), *figure.shapes], figure.size_in)


def regular_polygon(centre: Point, radius: float, sides: int, phase_deg: float = 0.0):
    cx, cy = centre
    return [
        (
            cx + radius * math.cos(math.radians(phase_deg + 360.0 * k / sides)),
            cy + radius * math.sin(math.radians(phase_deg + 360.0 * k / sides)),
        )
        for k in range(sides)
    ]


def arc(centre: Point, radius: float, start_deg: float, end_deg: float, steps: int = 12):
    cx, cy = centre
    return [
        (
            cx + radius * math.cos(math.radians(start_deg + (end_deg - start_deg) * k / steps)),
            cy + radius * math.sin(math.radians(start_deg + (end_deg - start_deg) * k / steps)),
        )
        for k in range(steps + 1)
    ]
