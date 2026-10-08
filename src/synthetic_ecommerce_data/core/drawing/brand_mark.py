"""A brand's mark: a shape and a wordmark, drawn the same way in every domain.

THE DOMAIN-NEUTRAL HALF of a brand mark (synthetic-ecommerce-data#132, on the
shared-core design of #125). A domain declares WHICH shape and enclosure each
of its brands wears (industrial: :mod:`...domains.industrial.drawing.brand_marks`
from the brand book's ``motif`` and ``enclosure`` columns); this module holds
what every domain needs and none owns. It is lifted from the retail prototype's
house-style kit (``prototypes/house_kit.py`` on the retail branches), whose
function names it keeps -- :func:`text_width`, :func:`fit_size`,
:func:`wordmark` -- so retail's move onto it is a rename, not a redesign:

* a mark is a tuple of :data:`Shape` -- :class:`Disc`, :class:`Ring`,
  :class:`Poly`, :class:`Stroke` -- in a unit box from -1 to 1. One geometry
  feeds both the SVG (:func:`draw_mark`) and the raster the distinguishability
  test measures (:func:`mark_bitmap`), so the test reads what is drawn;
* :func:`enclose` puts a motif in one of :data:`ENCLOSURES`: bare, inside a
  ring, or knocked out of a solid badge;
* a wordmark is SVG ``<text>`` set without a font engine: :func:`text_width`
  sums Helvetica-Bold advances (Arial Bold has the same metrics), and the
  ``textLength`` attribute pins the rendered width to that sum, so a viewer
  with another sans-serif squeezes the glyphs rather than overflowing the box;
* :func:`plate` sets mark and wordmark side by side in a box, the name on two
  lines when one line would fall below :data:`MIN_NAME_SIZE`.

Nothing here chooses a brand's look, and nothing reads a record: a mark is a
function of the brand alone, so every SKU of a brand carries the same one.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, replace

import numpy as np

from synthetic_ecommerce_data.core.drawing import svg

Point = tuple[float, float]


@dataclass(frozen=True)
class Disc:
    cx: float
    cy: float
    r: float
    #: Drawn in the paper colour: a hole knocked out of what is under it.
    cut: bool = False


@dataclass(frozen=True)
class Ring:
    cx: float
    cy: float
    r: float
    w: float
    cut: bool = False


@dataclass(frozen=True)
class Poly:
    points: tuple[Point, ...]
    cut: bool = False


@dataclass(frozen=True)
class Stroke:
    """A polyline of width ``w`` with round caps and joins."""

    points: tuple[Point, ...]
    w: float
    cut: bool = False


Shape = Disc | Ring | Poly | Stroke
Mark = tuple[Shape, ...]

#: How a motif sits in its mark. ``badge`` knocks the motif out of a solid
#: disc, so its pixels are nearly the inverse of the bare motif's.
ENCLOSURES: tuple[str, ...] = ("bare", "ring", "badge")

#: A motif's scale inside each enclosure (the ring's inner edge is at 0.78).
_INNER = {"bare": 1.0, "ring": 0.66, "badge": 0.7}
RING_RADIUS, RING_WIDTH = 0.91, 0.18


def _scaled(shape: Shape, k: float) -> Shape:
    if isinstance(shape, Disc):
        return replace(shape, cx=shape.cx * k, cy=shape.cy * k, r=shape.r * k)
    if isinstance(shape, Ring):
        return replace(shape, cx=shape.cx * k, cy=shape.cy * k, r=shape.r * k, w=shape.w * k)
    if isinstance(shape, Stroke):
        return replace(shape, points=tuple((x * k, y * k) for x, y in shape.points), w=shape.w * k)
    return replace(shape, points=tuple((x * k, y * k) for x, y in shape.points))


def enclose(motif: Mark, enclosure: str) -> Mark:
    """``motif`` in ``enclosure`` (one of :data:`ENCLOSURES`), still in the unit box."""
    if enclosure not in _INNER:
        raise ValueError(f"no enclosure {enclosure!r}; one of {ENCLOSURES}")
    inner = tuple(_scaled(shape, _INNER[enclosure]) for shape in motif)
    if enclosure == "bare":
        return inner
    if enclosure == "ring":
        return (Ring(0, 0, RING_RADIUS, RING_WIDTH), *inner)
    return (Disc(0, 0, 1.0), *(replace(shape, cut=not shape.cut) for shape in inner))


# --------------------------------------------------------------------------
# Drawing and measuring a mark
# --------------------------------------------------------------------------


def draw_mark(
    page: svg.Svg, mark: Mark, centre: Point, size: float, ink: str, paper: str
) -> None:
    """``mark`` on ``page``, its unit box ``size`` units across centred on ``centre``."""
    half = size / 2

    def at(p: Point) -> Point:
        return (centre[0] + p[0] * half, centre[1] + p[1] * half)

    for shape in mark:
        colour = paper if shape.cut else ink
        if isinstance(shape, Disc):
            page.circle(*at((shape.cx, shape.cy)), shape.r * half, fill=colour)
        elif isinstance(shape, Ring):
            page.circle(
                *at((shape.cx, shape.cy)),
                shape.r * half,
                fill="none",
                stroke=colour,
                stroke_width=svg.num(shape.w * half),
            )
        elif isinstance(shape, Poly):
            page.polygon([at(p) for p in shape.points], fill=colour)
        else:
            page.polyline(
                [at(p) for p in shape.points],
                stroke=colour,
                stroke_width=svg.num(shape.w * half),
                stroke_linecap="round",
                stroke_linejoin="round",
            )


def _inside_polygon(xs: np.ndarray, ys: np.ndarray, points: Sequence[Point]) -> np.ndarray:
    """Even-odd point-in-polygon for every ``(xs, ys)``."""
    inside = np.zeros(xs.shape, dtype=bool)
    n = len(points)
    for i in range(n):
        (x0, y0), (x1, y1) = points[i], points[(i + 1) % n]
        crosses = (y0 > ys) != (y1 > ys)
        with np.errstate(divide="ignore", invalid="ignore"):
            x_at = x0 + (ys - y0) * (x1 - x0) / (y1 - y0)
        inside ^= crosses & (xs < x_at)
    return inside


def _near_polyline(xs: np.ndarray, ys: np.ndarray, points: Sequence[Point], w: float) -> np.ndarray:
    near = np.zeros(xs.shape, dtype=bool)
    for (x0, y0), (x1, y1) in zip(points, points[1:], strict=False):
        dx, dy = x1 - x0, y1 - y0
        length2 = dx * dx + dy * dy or 1e-12
        t = np.clip(((xs - x0) * dx + (ys - y0) * dy) / length2, 0, 1)
        near |= np.hypot(xs - (x0 + t * dx), ys - (y0 + t * dy)) <= w / 2
    return near


def mark_bitmap(mark: Mark, px: int) -> np.ndarray:
    """The mark as a ``px`` x ``px`` boolean raster: True where a pixel's centre is ink.

    Painted in order, as :func:`draw_mark` paints: a ``cut`` shape clears
    what it covers. No antialiasing, so two marks compare pixel for pixel.
    """
    centres = (np.arange(px) + 0.5) / px * 2 - 1
    xs, ys = np.meshgrid(centres, centres)
    ink = np.zeros((px, px), dtype=bool)
    for shape in mark:
        if isinstance(shape, Disc):
            covered = np.hypot(xs - shape.cx, ys - shape.cy) <= shape.r
        elif isinstance(shape, Ring):
            covered = np.abs(np.hypot(xs - shape.cx, ys - shape.cy) - shape.r) <= shape.w / 2
        elif isinstance(shape, Poly):
            covered = _inside_polygon(xs, ys, shape.points)
        else:
            covered = _near_polyline(xs, ys, shape.points, shape.w)
        ink = ink & ~covered if shape.cut else ink | covered
    return ink


def differing_pixels(a: Mark, b: Mark, px: int) -> int:
    """How many pixels of the two ``px``-wide rasters only one of the marks inks.

    A count, not a share: what a shopper sees at a tile is a number of pixels
    that differ, whatever the marks' own ink areas are.
    """
    return int(np.count_nonzero(mark_bitmap(a, px) ^ mark_bitmap(b, px)))


# --------------------------------------------------------------------------
# Unit-space helpers motif tables are written with
# --------------------------------------------------------------------------


def regular(
    n: int, r: float, start: float = -90.0, cx: float = 0.0, cy: float = 0.0
) -> tuple[Point, ...]:
    """The ``n`` corners of a regular polygon of circumradius ``r``, the first at ``start``°."""
    angles = (math.radians(start + 360 * k / n) for k in range(n))
    return tuple(
        (cx + r * math.cos(a), cy + r * math.sin(a))
        for a in angles
    )


def star(n: int, outer: float, inner: float, start: float = -90.0) -> tuple[Point, ...]:
    """An ``n``-pointed star's outline, points at ``outer``, notches at ``inner``."""
    points = []
    for k in range(2 * n):
        a = math.radians(start + 180 * k / n)
        r = outer if k % 2 == 0 else inner
        points.append((r * math.cos(a), r * math.sin(a)))
    return tuple(points)


# --------------------------------------------------------------------------
# The wordmark
# --------------------------------------------------------------------------

#: The wordmark's face. Arial Bold is metric-compatible with Helvetica-Bold, and
#: ``textLength`` pins the width whatever the viewer substitutes.
FONT_FAMILY = "Arial, Helvetica, sans-serif"
FONT_WEIGHT = "700"
#: Helvetica-Bold advance widths, per 1000 units of the font size (its AFM).
_ADVANCE: dict[str, int] = {
    " ": 278, "&": 722, "'": 278, "-": 333, ".": 278,
    "A": 722, "B": 722, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722,
    "I": 278, "J": 556, "K": 722, "L": 611, "M": 833, "N": 722, "O": 778, "P": 667,
    "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944, "X": 667,
    "Y": 667, "Z": 611,
    "a": 556, "b": 611, "c": 556, "d": 611, "e": 556, "f": 333, "g": 611, "h": 611,
    "i": 278, "j": 278, "k": 556, "l": 278, "m": 889, "n": 611, "o": 611, "p": 611,
    "q": 611, "r": 389, "s": 556, "t": 333, "u": 611, "v": 556, "w": 778, "x": 556,
    "y": 556, "z": 500,
}  # fmt: skip
#: Cap height and descender of the face, as shares of the font size.
CAP_HEIGHT, DESCENDER = 0.72, 0.21
#: Two lines' baselines are this many font sizes apart.
LINE_GAP = 1.08


def text_width(text: str, size: float) -> float:
    """``text``'s set width at ``size``. A character outside the table raises:
    a guessed width could overflow the box the wordmark was fitted to."""
    try:
        return sum(_ADVANCE[c] for c in text) * size / 1000
    except KeyError as exc:
        raise ValueError(f"no advance width for {exc.args[0]!r} in {text!r}") from exc


def fit_size(text: str, room: float, start: float) -> float:
    """The largest size up to ``start`` at which ``text`` is at most ``room`` wide."""
    return min(start, room / (text_width(text, 1.0) or 1.0))


def wordmark(page: svg.Svg, text: str, x: float, baseline: float, size: float, ink: str) -> None:
    """``text`` left-aligned at ``x``, its width pinned to :func:`text_width`."""
    page.text(
        x,
        baseline,
        text,
        fill=ink,
        font_family=FONT_FAMILY,
        font_size=svg.num(size),
        font_weight=FONT_WEIGHT,
        textLength=svg.num(text_width(text, size)),
        lengthAdjust="spacingAndGlyphs",
    )


@dataclass(frozen=True)
class Lockup:
    """Where :func:`plate` put a mark and its name, in sheet units."""

    mark: tuple[float, float, float, float]  # x0, y0, x1, y1
    lines: tuple[str, ...]
    size: float  # the name's font size
    name: tuple[float, float, float, float]  # the name's ink box, descenders included


def split_name(name: str) -> tuple[str, str] | None:
    """``name`` broken at the space that best balances the two lines, or ``None``."""
    spaces = [i for i, c in enumerate(name) if c == " "]
    if not spaces:
        return None
    best = min(spaces, key=lambda i: max(text_width(name[:i], 1), text_width(name[i + 1 :], 1)))
    return name[:best], name[best + 1 :]


def lockup(
    name: str,
    box: tuple[float, float, float, float],
    *,
    mark_size: float,
    gap: float,
    max_size: float,
    min_size: float,
) -> Lockup:
    """Mark at the left of ``box``, then ``name`` as large as fits, up to ``max_size``.

    One line when it fits at ``min_size`` or more; else two lines, broken at a
    space, when that sets it larger. A name that fits neither way raises.
    """
    x0, y0, x1, y1 = box
    cy = (y0 + y1) / 2
    mark = (x0, cy - mark_size / 2, x0 + mark_size, cy + mark_size / 2)
    left = x0 + mark_size + gap
    room = x1 - left
    one = fit_size(name, room, max_size)
    halves = split_name(name)
    two = 0.0
    if halves is not None:
        tallest = (y1 - y0) / (CAP_HEIGHT + LINE_GAP + DESCENDER)
        two = min(fit_size(halves[0], room, max_size), fit_size(halves[1], room, max_size), tallest)
    lines: tuple[str, ...]
    if one >= min_size or two <= one:
        lines, size = (name,), one
    else:
        lines, size = halves, two  # type: ignore[assignment]
    if size < min_size:
        raise ValueError(f"{name!r} fits {box} only at {size:.1f}, under {min_size}")
    block = CAP_HEIGHT * size + (len(lines) - 1) * LINE_GAP * size
    top = cy - block / 2
    width = max(text_width(line, size) for line in lines)
    bottom = top + block + DESCENDER * size
    return Lockup(mark=mark, lines=lines, size=size, name=(left, top, left + width, bottom))


def plate(
    page: svg.Svg,
    name: str,
    mark: Mark,
    box: tuple[float, float, float, float],
    ink: str,
    paper: str,
    *,
    mark_size: float,
    gap: float,
    max_size: float,
    min_size: float,
) -> Lockup:
    """Draw ``mark`` and ``name`` in ``box`` (see :func:`lockup`) and say where they went.

    The plate is ONE top-level ``<g>``, so a reader of the figure's own
    elements (the drawing tests) skips it whole.
    """
    placed = lockup(name, box, mark_size=mark_size, gap=gap, max_size=max_size, min_size=min_size)
    mx0, my0, mx1, my1 = placed.mark
    page.add("<g>")
    draw_mark(page, mark, ((mx0 + mx1) / 2, (my0 + my1) / 2), mark_size, ink, paper)
    first = placed.name[1] + CAP_HEIGHT * placed.size
    for k, line in enumerate(placed.lines):
        wordmark(page, line, placed.name[0], first + k * LINE_GAP * placed.size, placed.size, ink)
    page.add("</g>")
    return placed
