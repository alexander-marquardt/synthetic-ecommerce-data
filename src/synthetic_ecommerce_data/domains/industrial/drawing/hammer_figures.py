"""The seven hammers, each drawn as its real kind, lit and large (#1215).

A hammer is seen from its head end: the head lies across the sheet, face to the left, and the
handle comes toward the viewer, so it is drawn short and stout. That is what lets a product that is
mostly a thin stick fill the figure area; the side view it replaced, true to its length, filled 2
to 21%.

The record says what the hammer looks like: its kind's head, ``Face Type`` (a milled face is
checkered), ``Handle Material`` (color, and the grain of a wood one) and ``Handle Grip Material``
(a ribbed grip). Its published ``Overall Length`` scales the whole drawing within :data:`SMALLEST`
to 1 of the kind's range, so a longer hammer is drawn larger than its shorter siblings; a record
without one is placed by its ``Handle Length``, else its ``Face Dia.``, and is ``partial``. A head
WEIGHT is not a shape, so it is not drawn.

Figures are laid out in a 164 by 200 box, in hundredths, y down, and written in the 1.64 by 2.0 box
of the figure area's own proportion.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing import product_look
from synthetic_ecommerce_data.core.drawing.model import Disc, Figure, Lines, Point, Poly, arc
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn, Record

#: The box every hammer's drawing at full size stays in, in inches: the type's extent.
EXTENT = (1.65, 2.01)
#: The scale of a kind's shortest hammer, of its longest one's: its siblings draw apart, and the
#: shortest keeps 90% of the area.
SMALLEST = 0.95
HANDLE_FILL = {"Hickory": "#c89a5b", "Ash": "#dcc08e", "Fiberglass": "#e2c64a", "Steel": "#9aa3aa"}
GRIP_FILL = {"Rubber": "#3d3d3d", "Vinyl": "#51638a"}
WOOD = ("Hickory", "Ash")
BOTTOM = 200.0

#: The lengths that say how large a hammer is, the one read first first: the shortest and longest of
#: each its kind is sold in, in inches.
Ranges = Mapping[str, tuple[float, float]]


def _clip(pts: list[Point], axis: int, at: float, keep_below: bool) -> list[Point]:
    """``pts`` cut at ``at`` on ``axis``: the part on one side of that line."""
    out: list[Point] = []
    side = -1.0 if keep_below else 1.0
    for a, b in zip(pts, [*pts[1:], pts[0]], strict=True):
        da, db = side * (a[axis] - at), side * (b[axis] - at)
        if da >= 0:
            out.append(a)
        if da * db < 0:
            t = da / (da - db)
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out


def _lit(fig: Figure, pts: list[Point], across: bool, role="part", fill=None) -> None:
    """A body: its outline, a highlight and a shadow in bands down it, or ``across`` it."""
    axis = 1 if across else 0
    low, high = min(p[axis] for p in pts), max(p[axis] for p in pts)
    fig.poly(pts, role, fill)
    for start, end, light in ((0.12, 0.28, "gloss"), (0.68, 1.0, "shade")):
        band = _clip(pts, axis, low + start * (high - low), keep_below=False)
        fig.poly(_clip(band, axis, low + end * (high - low), keep_below=True), light)


def _block(x0, y0, x1, y1, cut) -> list[Point]:
    """A block with its four corners cut."""
    return [
        (x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1 - cut),
        (x1 - cut, y1), (x0 + cut, y1), (x0, y1 - cut), (x0, y0 + cut),
    ]  # fmt: skip


def _checkered(fig: Figure, x0, y0, x1, y1) -> None:
    """The waffle of a milled face."""
    xs = [x0 + (x1 - x0) * k / 4 for k in range(5)]
    ys = [y0 + (y1 - y0) * k / 7 for k in range(8)]
    fig.lines([((x, y0), (x, y1)) for x in xs] + [((x0, y), (x1, y)) for y in ys])


# --- heads: each draws the head and says where its handle stands -------------------------------


def _claw(fig: Figure, record: Record) -> None:
    """A round face, a neck, the cheek and a curved claw split by its V."""
    _face(fig, record, 34)
    tail = [(88, 2), (122, 4), (146, 20), (160, 50), (164, 92), (154, 94), (142, 70), (124, 58),
            (88, 58)]  # fmt: skip
    _lit(fig, tail, across=True)
    fig.poly([(164, 92), (160, 93), (138, 52), (116, 34), (142, 46)], "dark")
    _lit(fig, _block(44, 0, 96, 76, 6), across=True)


def _framing(fig: Figure, record: Record) -> None:
    """A milled face, a neck, the cheek and a straight claw."""
    _face(fig, record, 36)
    tail = [(88, 2), (120, 8), (164, 34), (164, 50), (126, 66), (88, 70)]
    _lit(fig, tail, across=True)
    fig.poly([(164, 39), (164, 45), (116, 38)], "dark")
    _lit(fig, _block(44, 0, 98, 80, 5), across=True)


def _face(fig: Figure, record: Record, depth) -> None:
    """The striking end at the left: a neck behind a chamfered face, checkered when milled."""
    _lit(fig, [(24, 12), (50, 18), (50, 60), (24, 66)], across=True)
    _lit(fig, _block(0, 1, depth, 78, 7), across=True)
    if record.get("Face Type") == "Milled":
        _checkered(fig, 5, 10, depth - 5, 69)


def _ball_pein(fig: Figure, record: Record) -> None:
    """A round face at one end and a ball at the other."""
    _face(fig, record, 34)
    _lit(fig, [(90, 16), (124, 22), (124, 56), (90, 62)], across=True)
    centre, radius = (132.0, 39.0), 32.0
    fig.disc(centre, radius)
    for start, end, light in ((-30, 120, "shade"), (170, 280, "gloss")):
        rim = arc(centre, 0.92 * radius, start, end, 10)
        fig.poly([*rim, *arc(centre, 0.64 * radius, end, start, 10)], light)
    _lit(fig, _block(46, 0, 100, 78, 8), across=True)


def _club(fig: Figure, record: Record) -> None:
    """A short deep block with chamfered ends."""
    del record
    _lit(fig, _block(0, 0, 164, 94, 14), across=True)
    fig.lines(((x, 1), (x, 93)) for x in (18, 146))


def _sledge(fig: Figure, record: Record) -> None:
    """A long octagonal block: its flats run the length of the head."""
    del record
    _lit(fig, _block(0, 0, 164, 94, 20), across=True)
    fig.lines(((22, y), (142, y)) for y in (27, 64))
    fig.lines(((x, 1), (x, 93)) for x in (22, 142))


def _mallet(fig: Figure, record: Record) -> None:
    """A rubber barrel, fuller at its middle, a ring round each end."""
    del record
    top = [(82 + 82 * math.cos(math.radians(a)), 9 - 9 * math.sin(math.radians(a)))
           for a in range(0, 181, 15)]  # fmt: skip
    _lit(fig, [*top, *[(x, 100 - y) for x, y in reversed(top)]], across=True)
    for x in (18, 146):
        fig.lines([((x, 5), (x, 95))])


def _dead_blow(fig: Figure, record: Record) -> None:
    """A molded head: a waist between two rimmed ends, and its filler plug."""
    del record
    _lit(fig, [(20, 9), (144, 9), (144, 97), (20, 97)], across=True)
    for x0, x1 in ((0, 34), (130, 164)):
        _lit(fig, _block(x0, 0, x1, 106, 6), across=True)
    fig.disc((82, 53), 14, "dark")


@dataclass(frozen=True)
class Kind:
    """A kind's head, where its handle stands and how wide it is."""

    head: Callable[[Figure, Record], None]
    x: float
    top: float
    width: float


#: Every kind of hammer.
KINDS: dict[str, Kind] = {
    "hammer_ball_pein": Kind(_ball_pein, 73, 72, 56),
    "hammer_claw": Kind(_claw, 70, 70, 56),
    "hammer_framing": Kind(_framing, 71, 74, 58),
    "hammer_club": Kind(_club, 82, 86, 64),
    "hammer_sledge": Kind(_sledge, 82, 86, 66),
    "hammer_rubber_mallet": Kind(_mallet, 82, 92, 64),
    "hammer_dead_blow": Kind(_dead_blow, 82, 90, 66),
}


def _handle(fig: Figure, kind: Kind, record: Record) -> None:
    """The handle, toward the viewer: stout, and wider at its end; its grip or its grain."""
    x, half, top = kind.x, kind.width / 2, kind.top
    material = str(record.get("Handle Material", ""))
    grip = GRIP_FILL.get(str(record.get("Handle Grip Material", "")))
    end = half + 8
    sides = [(half - 4, top), (half, top + 40), (end - 2, 178), (end, 192), (end - 6, BOTTOM)]
    body = [(x - w, y) for w, y in sides] + [(x + w, y) for w, y in reversed(sides)]
    _lit(fig, body, across=False, role="handle", fill=HANDLE_FILL.get(material, "#c89a5b"))
    if grip:
        start = BOTTOM - 0.6 * (BOTTOM - top)
        sleeve = [(x - w, y) for w, y in _widths(sides, start)]
        sleeve += [(x + w, y) for w, y in reversed(_widths(sides, start))]
        _lit(fig, sleeve, across=False, role="grip", fill=grip)
        ribs = range(int(start) + 10, int(BOTTOM) - 8, 11)
        fig.lines(((x - half + 2, y), (x + half - 2, y)) for y in ribs)
    elif material in WOOD:
        grain = (-0.55, -0.15, 0.3, 0.65)
        fig.lines(((x + g * half, top + 22), (x + g * end, 186)) for g in grain)
    else:
        fig.lines([((x - end + 2, 178), (x + end - 2, 178))])
        fig.disc((x, 187), 5, "hole")


def _widths(sides: list[Point], start: float) -> list[Point]:
    """``sides`` (half width, y) from ``start`` down."""
    for (wa, ya), (wb, yb) in zip(sides, sides[1:], strict=False):
        if ya <= start <= yb:
            at = wa + (wb - wa) * (start - ya) / (yb - ya)
            return [(at, start), *[p for p in sides if p[1] > start]]
    raise ValueError(f"no handle at {start}")


def _scaled(fig: Figure, factor: float) -> Figure:
    """``fig`` in hundredths, written in inches at ``factor`` of its size."""
    k = factor / 100

    def at(p: Point) -> Point:
        return p[0] * k, p[1] * k

    out = Figure(size_in=2.0 * factor)
    for shape in fig.shapes:
        if isinstance(shape, Poly):
            out.poly([at(p) for p in shape.points], shape.role, shape.fill)
        elif isinstance(shape, Disc):
            out.disc(at(shape.centre), shape.radius * k, shape.role, shape.fill)
        elif isinstance(shape, Lines):
            out.lines(((at(a), at(b)) for a, b in shape.segments), shape.role)
        else:
            raise TypeError(f"{type(shape).__name__} is in no hammer")
    return out


def _share(ranges: Ranges, record: Record) -> tuple[float, str]:
    """How large the hammer is drawn, of its kind's longest, and whether the record says it: by the
    first of ``ranges``' lengths it publishes, ``partial`` when that is not the first."""
    for k, (name, (short, long)) in enumerate(ranges.items()):
        try:
            length = parse_length(record[name]).inches
        except (KeyError, DimensionParseError):
            continue
        place = min(1.0, max(0.0, (length - short) / (long - short)))
        return SMALLEST + (1.0 - SMALLEST) * place, "partial" if k else "record"
    return 1.0, "partial"


def hammer(key: str, ranges: Ranges, record: Record) -> Drawn:
    """``record`` drawn as the hammer ``key`` names, which is sold in ``ranges``."""
    kind = KINDS[key]
    factor, source = _share(ranges, record)
    fig = Figure()
    _handle(fig, kind, record)
    kind.head(fig, record)
    return Drawn(_scaled(fig, factor), source)


def _outline(key: str) -> tuple[Point, ...]:
    """The points the largest drawing of ``key`` reaches, about the centre of its box."""
    fig = hammer(key, {}, {}).figure
    x0, y0, x1, y1 = fig.bounds()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    points: list[Point] = []
    for shape in fig.shapes:
        if isinstance(shape, Poly):
            points += shape.points
        elif isinstance(shape, Disc):
            points += arc(shape.centre, shape.radius, 0, 360, 32)
    return tuple((x - cx, y - cy) for x, y in points)


product_look.OUTLINES.update({key: _outline(key) for key in KINDS})
