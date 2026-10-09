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
* :func:`plate` sets mark and wordmark in a box, in the first of four layouts
  that sets the name at the domain's least legible size or larger: one line
  beside the mark; two lines beside it; the first word beside it and the
  rest under it; the whole name under it (:func:`lockup`). No layout fitting
  is an error: a wordmark is always the full name;
* the mark itself comes from the domain, through the slot :func:`use_marks`
  fills and :func:`mark_for` reads, so core imports no domain.

Nothing here chooses a brand's look, and nothing reads a record: a mark is a
function of the brand alone, so every SKU of a brand carries the same one.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
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


#: THE MARK SLOT. Core draws marks but never imports a domain (``CORE_EDGES``
#: in ``tests/test_core_extraction_125.py`` may only shrink), so a domain
#: registers its brand -> mark function here: the industrial one does it in
#: ``domains/industrial/drawing/__init__.py``, which runs whenever
#: ``core.drawing`` loads, because that loads the domain's figures.
_MARK_OF: Callable[[str], Mark] | None = None


def use_marks(mark_of: Callable[[str], Mark]) -> None:
    """Make ``mark_of`` the function :func:`mark_for` asks for a brand's mark."""
    global _MARK_OF
    _MARK_OF = mark_of


def mark_for(brand: str) -> Mark:
    """``brand``'s mark, from the domain that registered with :func:`use_marks`.

    No registration is an error, never a blank plate.
    """
    if _MARK_OF is None:
        raise LookupError("no domain registered its brand marks (brand_mark.use_marks)")
    return _MARK_OF(brand)


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


def draw_mark(page: svg.Svg, mark: Mark, centre: Point, size: float, ink: str, paper: str) -> None:
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
    return tuple((cx + r * math.cos(a), cy + r * math.sin(a)) for a in angles)


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
#: Cap height and descender of the face, as shares of the font size. The cap
#: height is Arial Bold's (0.716); Helvetica-Bold's capitals are 0.718, so
#: either face draws them at least this tall. The legibility rule is stated
#: in cap height (:data:`...sheet.NAME_MIN`), so this is the number it rests on.
CAP_HEIGHT, DESCENDER = 0.716, 0.21
#: Two lines' baselines are this many font sizes apart.
LINE_GAP = 1.08
#: The gap between the mark's bottom and the capitals of a line set under it.
UNDER_GAP = 2.0


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
    """``text`` left-aligned at ``x``, its width pinned to :func:`text_width`.

    ``size`` is written at one decimal, and the width is that written size's,
    so a viewer reading both draws the glyphs at their own width.
    """
    size = float(svg.num(size))
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


Box = tuple[float, float, float, float]  # x0, y0, x1, y1


@dataclass(frozen=True)
class Line:
    """One line of a wordmark: its words, left edge and baseline."""

    text: str
    x: float
    baseline: float


@dataclass(frozen=True)
class Lockup:
    """Where :func:`plate` put a mark and its name, in sheet units."""

    mark: Box
    placed: tuple[Line, ...]
    size: float  # the name's font size, at one decimal as drawn
    #: Which of :data:`LAYOUTS` set it.
    layout: str

    @property
    def lines(self) -> tuple[str, ...]:
        return tuple(line.text for line in self.placed)

    def line_box(self, line: Line) -> Box:
        """``line``'s ink box: capitals up from the baseline, descenders below."""
        return (
            line.x,
            line.baseline - CAP_HEIGHT * self.size,
            line.x + text_width(line.text, self.size),
            line.baseline + DESCENDER * self.size,
        )

    @property
    def name(self) -> Box:
        """The whole name's ink box."""
        boxes = [self.line_box(line) for line in self.placed]
        return (
            min(b[0] for b in boxes),
            min(b[1] for b in boxes),
            max(b[2] for b in boxes),
            max(b[3] for b in boxes),
        )


#: The layouts :func:`lockup` tries, in order: the first that sets the name at
#: the least legible size or larger wins.
LAYOUTS: tuple[str, ...] = ("beside", "two_beside", "split_under", "under")


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

    The first of :data:`LAYOUTS` that sets the name at ``min_size`` or more:

    * ``beside``: one line beside the mark, centred on it;
    * ``two_beside``: two lines beside it, broken at the balancing space;
    * ``split_under``: the mark in the top-left corner, the words before a
      space beside it and the rest under it, across the full width;
    * ``under``: the mark in the top-left corner, the name under it.

    The wordmark is always the full name. A name no layout sets at
    ``min_size`` raises. Sizes are floored to one decimal, the precision the
    drawing writes, so the size drawn is the size checked.
    """
    x0, y0, x1, y1 = box
    left = x0 + mark_size + gap
    room, full = x1 - left, x1 - x0
    for layout in LAYOUTS:
        found = _layout(layout, name, box, mark_size, left, room, full, max_size)
        if found is not None and found.size >= min_size:
            return found
    raise ValueError(f"{name!r} fits {box} in no layout at {min_size} or more")


def _floor(size: float) -> float:
    return math.floor(size * 10 + 1e-9) / 10


def _layout(
    layout: str,
    name: str,
    box: Box,
    mark_size: float,
    left: float,
    room: float,
    full: float,
    max_size: float,
) -> Lockup | None:
    """``name`` set by ``layout`` in ``box`` as large as fits, or ``None`` if it cannot be."""
    x0, y0, x1, y1 = box
    height = y1 - y0
    if layout in ("beside", "two_beside"):
        lines = (name,) if layout == "beside" else split_name(name)
        if lines is None:
            return None
        tallest = height / (CAP_HEIGHT + (len(lines) - 1) * LINE_GAP + DESCENDER)
        size = _floor(min(tallest, *(fit_size(line, room, max_size) for line in lines)))
        cy = (y0 + y1) / 2
        block = CAP_HEIGHT * size + (len(lines) - 1) * LINE_GAP * size
        # The capitals are centred on the mark; a descender that would then
        # hang below the box (two lines at their tallest) lifts the name into it.
        first = min(cy + block / 2 + DESCENDER * size, y1) - DESCENDER * size - block
        first += CAP_HEIGHT * size
        placed = tuple(Line(t, left, first + k * LINE_GAP * size) for k, t in enumerate(lines))
        mark = (x0, cy - mark_size / 2, x0 + mark_size, cy + mark_size / 2)
        return Lockup(mark=mark, placed=placed, size=size, layout=layout)
    # The mark in the top-left corner; the last line under it.
    mark = (x0, y0, x0 + mark_size, y0 + mark_size)
    tallest = (height - mark_size - UNDER_GAP) / (CAP_HEIGHT + DESCENDER)
    under_baseline = y0 + mark_size + UNDER_GAP
    if layout == "under":
        size = _floor(min(tallest, fit_size(name, full, max_size)))
        line = Line(name, x0, under_baseline + CAP_HEIGHT * size)
        return Lockup(mark=mark, placed=(line,), size=size, layout=layout)
    # split_under: every split at a space, the largest size wins. The head's
    # capitals are centred on the mark, which keeps its descenders above the
    # tail's capitals at any size the box allows.
    best: Lockup | None = None
    for i, c in enumerate(name):
        if c != " ":
            continue
        head, tail = name[:i], name[i + 1 :]
        size = _floor(min(tallest, fit_size(head, room, max_size), fit_size(tail, full, max_size)))
        if best is None or size > best.size:
            placed = (
                Line(head, left, y0 + mark_size / 2 + CAP_HEIGHT * size / 2),
                Line(tail, x0, under_baseline + CAP_HEIGHT * size),
            )
            best = Lockup(mark=mark, placed=placed, size=size, layout=layout)
    return best


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
    for line in placed.placed:
        wordmark(page, line.text, line.x, line.baseline, placed.size, ink)
    page.add("</g>")
    return placed
