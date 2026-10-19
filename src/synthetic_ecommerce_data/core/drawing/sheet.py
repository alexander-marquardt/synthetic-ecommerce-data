"""Placing a figure on the sheet and painting it in the brand's house style.

THE SCALE is one constant per product type: the usable sheet over the type's
largest drawn extent (:data:`.figures.FIGURES`). Every SKU of a type is drawn at
it, so any two parts of one type are in true proportion to each other, and
siblings draw a head, a thread or a bore they share identically.

THE MAGNIFIER (maintainer ruling on elastic/prism-industrial-products#103,
2026-09-28, from prototype v8). A part too small to read at its type's scale is
not enlarged in place. It is drawn at true scale near the bottom of the sheet,
horizontally centred, and a magnifying glass above it shows it enlarged:

* the glyph is the public-domain magnifier icon's SHAPE -- a ring, a thin shaft
  and a grip twice the shaft's width, with round caps -- at the icon's native
  angle (handle to the bottom-right), every stroke at :data:`RING_SHARE` of the
  icon's weight relative to its lens, in the brand's ink;
* the lens is white and holds the same figure, drawn :attr:`Magnifier.k` times
  larger so its bounding box's diagonal spans :data:`LENS_FILL` of the lens;
* the WHOLE glyph is horizontally centred and as large as the sheet allows;
  the space above it equals the space below the small part, and
  :data:`GLYPH_GAP` separates the grip's lowest point from the part;
* a part is TOO SMALL TO SEE when its drawn width is at most
  :data:`MAGNIFY_WIDTH_SHARE` (1/5) of the sheet's width AND its drawn height at
  most :data:`MAGNIFY_HEIGHT_SHARE` (1/6) of the sheet's height, and such a part
  ALWAYS gets a lens (the refined ruling of 2026-09-28: *"if they are too small
  to see, then they should have a lens .. if they can be seen, they should
  not"*; the 1/5 width share is the coordinator's call on the edge cases, so the
  socket screws drawn just over 1/6 wide are lensed too). Every other part is
  drawn plain, centred, at its type's scale;
* the handled glass is used when it enlarges the part at least
  :data:`MIN_ENLARGEMENT` times. Otherwise the lens is a larger HANDLE-LESS
  circle -- the same thin ring, white interior and enlarged part -- sized to the
  figure area, with the part below it, both centred and the margins
  balanced. Since the brand plate (#132) THAT LENS IS HEIGHT-BOUND for the
  tallest too-small parts: in the 236-unit figure area it enlarges the
  largest (40 x 50, a ~64-unit diagonal) only ~x2.05, where the 8-unit
  width bound alone would give ~x2.42. The floor the tests hold is the
  measured catalog minimum (``tests/test_sku_drawings.py``), not x2.5.

NO OUTLINE IS THINNER THAN :data:`MIN_STROKE` units, which is ~2 px on a
180 px-wide thumbnail, so a hairline part (a 1/16" drill at its type's scale is
under one unit wide) is visible with or without a lens. The interior detail
lines (flutes, threads, hatch) are texture, not the part's outline, and keep
their finer weight.

No part of the magnifier is text. ``tests/test_sku_drawings.py`` asserts the
rule, the enlargement, the balance, the ink and the allow-list.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from synthetic_ecommerce_data.core import brands
from synthetic_ecommerce_data.core.drawing import brand_mark, svg
from synthetic_ecommerce_data.core.drawing.model import Bars, Disc, Dots, Figure, Lines, Poly
from synthetic_ecommerce_data.core.drawing.style import Hatch, HouseStyle, _mix

#: The inset of the drawing from the sheet edge, in sheet units.
MARGIN = 18.0

#: The thinnest outline any drawing strokes, in sheet units: 2.3 units is
#: 2.07 px on a 180 px-wide thumbnail (the sheet is 200 units wide).
MIN_STROKE = brands.WEIGHTS[0]
LW_PART = svg.num(MIN_STROKE)
LW_LINE = "0.8"

#: The magnifier's rule and geometry (see the module docstring).
#: The too-small-to-see rule: a part drawn at most this share of the sheet's
#: WIDTH and at most that share of its HEIGHT gets a lens.
MAGNIFY_WIDTH_SHARE = 1 / 5
MAGNIFY_HEIGHT_SHARE = 1 / 6
MIN_ENLARGEMENT = 2.5
LENS_FILL = 0.92
GLYPH_GAP = 14.0
#: The glyph's inset from the sheet edge, sideways (the icon's frame-free zone).
GLYPH_MARGIN = 12.0
#: The handle-less lens's inset from the sheet edge: it is sized to the width.
#: 8 is the smallest that clears every brand frame: the frames are drawn at 6
#: units in with strokes at most 2 wide, so the ring stays at least 1 unit clear.
LENS_MARGIN = 8.0
#: Stroke weight as a share of the icon's (36 on a 135 lens interior).
RING_SHARE = 0.35
#: The icon's proportions, in its own units: lens interior radius, and how far
#: the shaft and the grip reach from the lens centre along the handle.
ICON_LENS, ICON_STROKE = 135.0, 36.0
ICON_SHAFT_END, ICON_GRIP_FROM, ICON_GRIP_TO = 394.0, 229.0, 420.0
HANDLE_ANGLE = 45.0  # degrees below the horizontal, toward the right


#: THE BRAND PLATE (#132): the brand's mark and wordmark, in a strip under the
#: figure. WHY THERE: an engineering drawing's maker sits in its title block,
#: below and outside the view, and a strip the figure never enters cannot
#: cover a dimension, a head or a thread of any family -- a corner stamp
#: would have to dodge every type's outline separately. The figure keeps the
#: sheet above :data:`FIGURE_HEIGHT`; its margins (:data:`MARGIN`,
#: :data:`GLYPH_MARGIN`, :data:`LENS_MARGIN`) apply inside that area, so
#: :func:`figure_boxes` never reaches the plate (``tests/test_brand_marks.py``).
#: The cost: a type whose largest part is height-bound is drawn 200/264 of
#: its former scale; a squat type (washers, discs) is width-bound and keeps it.
#: WHY 56 UNITS TALL: the full 32-unit mark (the distinguishability raster's
#: size), a 2-unit gap, and one line under it at the least legible size,
#: descenders included -- the layout a single word too wide to sit beside
#: the mark (Kessingmoor) needs: 32 + 2 + 0.926 x 23.3 = 55.6.
FIGURE_HEIGHT = 236.0
#: The plate's box (x0, y0, x1, y1): inside every frame (drawn 6 units in,
#: strokes at most 2 wide), clear of the rounded frame's corner arcs.
PLATE_BOX = (14.0, 236.0, 186.0, 292.0)
#: The mark's side and the gap before the name, in sheet units.
PLATE_MARK = 32.0
PLATE_GAP = 6.0
#: The Studio grid tile shows the sheet 180 px tall: 0.6 px a sheet unit. At
#: it the mark is 19 px across.
TILE_PX_PER_UNIT = 180 / svg.HEIGHT
#: THE LEGIBILITY RULING (#132): no brand name's CAPITALS render under 10 px
#: tall at the tile, so no name is set under 10 / (0.716 x 0.6) = 23.28
#: units, rounded up to the drawing's one decimal: 23.3. A name is set in the
#: first layout of :func:`...brand_mark.lockup` that reaches that size, and
#: one that none does raises: there is no shortened wordmark.
MIN_NAME_PX = 10.0
NAME_MAX = 26.0
NAME_MIN = math.ceil(MIN_NAME_PX / (brand_mark.CAP_HEIGHT * TILE_PX_PER_UNIT) * 10) / 10


def type_scale(extent: tuple[float, float]) -> float:
    """Sheet units per inch for a product type: its largest drawn extent fills the figure area."""
    width, height = extent
    aw, ah = svg.WIDTH - 2 * MARGIN, FIGURE_HEIGHT - 2 * MARGIN
    return min(aw / width, ah / height)


@dataclass(frozen=True)
class Magnifier:
    """Where a magnified part and its glyph go on the sheet, in sheet units."""

    k: float  # the lens's enlargement
    handle: bool  # the handled glass, or the larger handle-less lens
    lens: tuple[float, float]  # lens centre
    radius: float  # lens interior radius
    stroke: float  # ring and shaft width (the grip is twice it)
    part: tuple[float, float]  # the true-scale part's centre
    top: float  # the space above the glyph, equal to the space below the part


def _glyph_extent(radius: float, floor: bool = True) -> tuple[float, float, float, float]:
    """The glyph's (stroke, left, right, bottom) about its lens centre, in sheet units.

    ``floor=False`` leaves out the :data:`MIN_STROKE` floor, so the extents are
    linear in ``radius`` -- the form the largest-lens solve needs. At every
    radius a sheet actually draws, the icon's own stroke is above the floor.
    """
    f = radius / ICON_LENS
    w = ICON_STROKE * RING_SHARE * f
    if floor:
        w = max(w, MIN_STROKE)
    outer = radius + w
    reach = ICON_GRIP_TO * f
    a = math.radians(HANDLE_ANGLE)
    # The grip is a 2w-wide stroke with round caps: it reaches w past its end.
    return w, -outer, max(outer, reach * math.cos(a) + w), max(outer, reach * math.sin(a) + w)


def magnifier(width: float, height: float) -> Magnifier | None:
    """The layout for a part drawn ``width`` x ``height``, or ``None`` if it is drawn plain."""
    if width <= 0 or height <= 0:
        return None
    if width > svg.WIDTH * MAGNIFY_WIDTH_SHARE or height > svg.HEIGHT * MAGNIFY_HEIGHT_SHARE:
        return None
    diagonal = math.hypot(width, height)
    # The handled glass: every extent is linear in the lens radius, so the
    # largest lens that fits is the tighter of the width and the height budgets.
    _, left1, right1, bottom1 = _glyph_extent(1.0, floor=False)
    by_width = (svg.WIDTH - 2 * GLYPH_MARGIN) / (right1 - left1)
    by_height = (FIGURE_HEIGHT - 2 * GLYPH_MARGIN - GLYPH_GAP - height) / (-left1 + bottom1)
    radius = min(by_width, by_height)
    k = LENS_FILL * 2 * radius / diagonal
    if k >= MIN_ENLARGEMENT:
        w, left, right, bottom = _glyph_extent(radius)
        glyph_h = -left + bottom
        top = (FIGURE_HEIGHT - (glyph_h + GLYPH_GAP + height)) / 2
        lens = (svg.WIDTH / 2 - (left + right) / 2, top - left)
        part = (svg.WIDTH / 2, top + glyph_h + GLYPH_GAP + height / 2)
        return Magnifier(k=k, handle=True, lens=lens, radius=radius, stroke=w, part=part, top=top)
    # The handle-less lens: a circle as wide as the sheet allows.
    ring = ICON_STROKE * RING_SHARE / ICON_LENS  # the ring's width per unit of radius
    radius = min(
        (svg.WIDTH / 2 - LENS_MARGIN) / (1 + ring),
        (FIGURE_HEIGHT - 2 * LENS_MARGIN - GLYPH_GAP - height) / 2 / (1 + ring),
    )
    w = max(ring * radius, MIN_STROKE)
    outer = radius + w
    top = (FIGURE_HEIGHT - (2 * outer + GLYPH_GAP + height)) / 2
    lens = (svg.WIDTH / 2, top + outer)
    part = (svg.WIDTH / 2, top + 2 * outer + GLYPH_GAP + height / 2)
    k = LENS_FILL * 2 * radius / diagonal
    return Magnifier(k=k, handle=False, lens=lens, radius=radius, stroke=w, part=part, top=top)


def _hatch_pattern(page: svg.Svg, hatch: Hatch, ink: str) -> str:
    key = (
        "h"
        + "-".join(str(a) for a in hatch.angles)
        + f"s{hatch.spacing:g}"
        + ("d" if hatch.dots else "")
        + ink[1:]
    )
    s = svg.num(hatch.spacing)
    h = svg.num(hatch.spacing / 2)
    inner = []
    if not hatch.angles and hatch.dots:
        inner.append(f'<circle cx="{h}" cy="{h}" r=".7"/>')
    for angle in hatch.angles:
        inner.append(f'<path d="M0 0V{s}" stroke-width=".5" transform="rotate({angle} {h} {h})"/>')
    if hatch.angles and hatch.dots:
        inner.append(f'<circle cx="{svg.num(hatch.spacing / 2)}" cy="0" r=".6"/>')
    page.define(
        key,
        f'<pattern id="{key}" width="{s}" height="{s}" patternUnits="userSpaceOnUse">'
        f'<g stroke="{ink}" fill="{ink}" opacity=".45">{"".join(inner)}</g></pattern>',
    )
    return key


#: How far a chamfered frame cuts each corner. 7 keeps the plate's bottom corners
#: (14 units in, 8 above the edge) 2.1 units inside the cut at the default margin.
CHAMFER = 7.0
#: The texture's cell, in sheet units, and its strength. Faint, so the figure and
#: its hatch still read; drawn in the brand's ink over the figure area only, so the
#: wordmark's plate stays plain.
TEXTURE_CELL = 10.0
TEXTURE_OPACITY = {"grid": ".14", "dot": ".28"}


def chamfer_points(margin: float) -> list[tuple[float, float]]:
    """The chamfered frame's eight corners, clockwise from the top edge's left end."""
    w, h, m, c = svg.WIDTH, svg.HEIGHT, margin, CHAMFER
    return [
        (m + c, m),
        (w - m - c, m),
        (w - m, m + c),
        (w - m, h - m - c),
        (w - m - c, h - m),
        (m + c, h - m),
        (m, h - m - c),
        (m, m + c),
    ]


def _texture(page: svg.Svg, house: HouseStyle) -> None:
    """The background texture, behind everything, over the figure area."""
    if house.texture == "plain":
        return
    key = f"t{house.texture}{house.ink[1:]}"
    c = svg.num(TEXTURE_CELL)
    if house.texture == "grid":
        mark = f'<path d="M0 0H{c}M0 0V{c}" fill="none" stroke="{house.ink}" stroke-width=".5"/>'
    else:
        mid = svg.num(TEXTURE_CELL / 2)
        mark = f'<circle cx="{mid}" cy="{mid}" r=".9" fill="{house.ink}"/>'
    page.define(
        key,
        f'<pattern id="{key}" width="{c}" height="{c}" patternUnits="userSpaceOnUse">'
        f'<g opacity="{TEXTURE_OPACITY[house.texture]}">{mark}</g></pattern>',
    )
    page.rect(0, 0, svg.WIDTH, FIGURE_HEIGHT, fill=f"url(#{key})")


def _frame(page: svg.Svg, house: HouseStyle) -> None:
    ink, m = house.ink, house.margin
    w, h = svg.WIDTH, svg.HEIGHT
    if house.frame == "rule":
        page.rect(m, m, w - 2 * m, h - 2 * m, fill="none", stroke=ink, stroke_width="1")
    elif house.frame == "rounded":
        page.add(
            f'<rect x="{svg.num(m)}" y="{svg.num(m)}" width="{svg.num(w - 2 * m)}" '
            f'height="{svg.num(h - 2 * m)}" rx="14" fill="none" stroke="{ink}" stroke-width="1.4"/>'
        )
    elif house.frame == "chamfer":
        page.polygon(chamfer_points(m), fill="none", stroke=ink, stroke_width="1")
    elif house.frame == "corners":
        a = 18
        page.lines(
            [
                ((m, m + a), (m, m)),
                ((m, m), (m + a, m)),
                ((w - m - a, m), (w - m, m)),
                ((w - m, m), (w - m, m + a)),
                ((m, h - m - a), (m, h - m)),
                ((m, h - m), (m + a, h - m)),
                ((w - m - a, h - m), (w - m, h - m)),
                ((w - m, h - m), (w - m, h - m - a)),
            ],
            stroke=ink,
            stroke_width="2",
        )


def _figure_at(
    page: svg.Svg,
    figure: Figure,
    house: HouseStyle,
    fill: str,
    hatch_id: str | None,
    scale: float,
    centre: tuple[float, float],
) -> None:
    """Paint ``figure`` at ``scale`` with its bounding box centred on ``centre``."""
    x0, y0, x1, y1 = figure.bounds()
    bw, bh = max(x1 - x0, 1e-9), max(y1 - y0, 1e-9)
    ox = centre[0] - (x0 + bw / 2) * scale
    oy = centre[1] - (y0 + bh / 2) * scale

    def at(p):
        return (ox + p[0] * scale, oy + p[1] * scale)

    pale = _mix(fill, "#ffffff", 0.5)
    ink = house.ink
    for shape in figure.shapes:
        if isinstance(shape, Lines):
            dash = {"stroke_dasharray": house.dash} if house.dash else {}
            page.lines(
                [(at(a), at(b)) for a, b in shape.segments],
                stroke=ink,
                stroke_width=LW_LINE,
                stroke_opacity=".8",
                **dash,
            )
            continue
        if isinstance(shape, Dots):
            a = max(shape.radius * scale, 0.4)
            n, m = svg.num(a), svg.num(-a)
            d = "".join(
                f"M{svg.num(x - a)} {svg.num(y)}l{n} {m}l{n} {n}l{m} {n}z"
                for x, y in (at(c) for c in shape.centres)
            )
            page.path(d, fill=_mix(ink, "#ffffff", 0.55))
            continue
        if shape.role == "part":
            color, hatched = fill, True
        elif shape.role == "plain":
            color, hatched = pale, False
        elif shape.role == "hole":
            color, hatched = house.paper, False
        elif shape.role == "dark":
            color, hatched = _mix(ink, "#ffffff", 0.55), False
        else:  # handle, grip
            color, hatched = getattr(shape, "fill", None) or pale, False
        style = {
            "fill": color,
            "stroke": ink,
            "stroke_width": svg.num(house.stroke),
            "stroke_linejoin": "round",
        }
        if isinstance(shape, Bars):
            d = svg.bars_d([(*at((x0, y0)), *at((x1, y1))) for x0, y0, x1, y1 in shape.rects])
            page.path(d, **style)
            if hatched and hatch_id:
                page.path(d, fill=f"url(#{hatch_id})")
        elif isinstance(shape, Poly):
            points = [at(p) for p in shape.points]
            page.polygon(points, **style)
            if hatched and hatch_id:
                page.polygon(points, fill=f"url(#{hatch_id})")
        elif isinstance(shape, Disc):
            cx, cy = at(shape.centre)
            r = shape.radius * scale
            page.circle(cx, cy, r, **style)
            if hatched and hatch_id:
                page.circle(cx, cy, r, fill=f"url(#{hatch_id})")


def _glyph(page: svg.Svg, mag: Magnifier, ink: str) -> None:
    """The magnifier glyph: shaft, grip, then the ring over them, all in ``ink``."""
    f = mag.radius / ICON_LENS
    a = math.radians(HANDLE_ANGLE)
    cx, cy = mag.lens

    def along(d):
        return (cx + math.cos(a) * d, cy + math.sin(a) * d)

    ring = mag.radius + mag.stroke / 2
    handle = (
        (ring, ICON_SHAFT_END * f, mag.stroke),
        (ICON_GRIP_FROM * f, ICON_GRIP_TO * f, 2 * mag.stroke),
    )
    for start, end, width in handle if mag.handle else ():
        page.path(
            svg.path_d([along(start), along(end)], closed=False),
            fill="none",
            stroke=ink,
            stroke_width=svg.num(width),
            stroke_linecap="round",
        )
    page.circle(cx, cy, ring, fill="none", stroke=ink, stroke_width=svg.num(mag.stroke))


def paint(
    figure: Figure,
    house: HouseStyle,
    fill: str,
    hatch: Hatch | None,
    scale: float,
) -> bytes:
    """The figure on a sheet, as SVG bytes. Its only text is the brand's wordmark.

    Drawn plain and centred in the figure area, or -- when :func:`magnifier`
    says so -- at true scale near the bottom with a magnifying glass above it;
    then the brand plate (:func:`plate_lockup`) in the strip below.
    """
    page = svg.Svg(background=house.paper)
    _texture(page, house)
    _frame(page, house)
    hatch_id = _hatch_pattern(page, hatch, house.ink) if hatch is not None else None
    x0, y0, x1, y1 = figure.bounds()
    mag = magnifier((x1 - x0) * scale, (y1 - y0) * scale)
    if mag is None:
        _figure_at(page, figure, house, fill, hatch_id, scale, (svg.WIDTH / 2, FIGURE_HEIGHT / 2))
    else:
        _figure_at(page, figure, house, fill, hatch_id, scale, mag.part)
        page.circle(*mag.lens, mag.radius, fill="#ffffff")
        _figure_at(page, figure, house, fill, hatch_id, scale * mag.k, mag.lens)
        _glyph(page, mag, house.ink)
    brand_mark.plate(
        page,
        house.name,
        house.mark,
        PLATE_BOX,
        house.ink,
        house.paper,
        mark_size=PLATE_MARK,
        gap=PLATE_GAP,
        max_size=NAME_MAX,
        min_size=NAME_MIN,
    )
    return page.to_bytes()


def plate_lockup(name: str) -> brand_mark.Lockup:
    """Where :func:`paint` sets ``name``'s mark and wordmark, in sheet units."""
    return brand_mark.lockup(
        name, PLATE_BOX, mark_size=PLATE_MARK, gap=PLATE_GAP, max_size=NAME_MAX, min_size=NAME_MIN
    )


def wordmark_of(name: str) -> str:
    """The words :func:`paint` sets for brand ``name``: always the full name."""
    return " ".join(plate_lockup(name).lines)


def figure_boxes(
    figure: Figure, scale: float, stroke: float = MIN_STROKE
) -> list[tuple[float, float, float, float]]:
    """The boxes :func:`paint` draws the figure in, strokes included: the part,
    and -- when lensed -- the whole glyph. None of them reaches :data:`PLATE_BOX`."""
    x0, y0, x1, y1 = figure.bounds()
    w, h = (x1 - x0) * scale, (y1 - y0) * scale
    half = stroke / 2
    mag = magnifier(w, h)
    centre = (svg.WIDTH / 2, FIGURE_HEIGHT / 2) if mag is None else mag.part
    dx, dy = w / 2 + half, h / 2 + half
    boxes = [(centre[0] - dx, centre[1] - dy, centre[0] + dx, centre[1] + dy)]
    if mag is not None:
        if mag.handle:
            _, left, right, bottom = _glyph_extent(mag.radius)
        else:
            outer = mag.radius + mag.stroke
            left, right, bottom = -outer, outer, outer
        cx, cy = mag.lens
        boxes.append((cx + left, cy + left, cx + right, cy + bottom))
    return boxes
