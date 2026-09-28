"""Placing a figure on the sheet and painting it in the brand's house style.

THE SCALE IS ONE CONSTANT PER PRODUCT TYPE: sheet units per inch are the usable
sheet divided by the type's largest drawn extent (:data:`.figures.FIGURES`).
So every product of a type is drawn at its true size relative to every other --
an M20 flat head reads bigger than a #6 one of the same length, and a longer
sibling is drawn longer -- whatever the figure's own proportions.

The one exception is legibility. A product whose PRIMARY dimension (its
``size_in``: a screw's length, a washer's diameter) would be drawn shorter than
:data:`FLOOR` sheet units is enlarged so that it is drawn ``sqrt(FLOOR * d)``
long instead of ``d``. That map is strictly increasing in ``d``, so a larger
published primary dimension is never drawn shorter, within a product or across
a type; ``tests/test_sku_drawings.py`` asserts that order over the committed
catalog. Proportions within one drawing are always exactly the record's.
"""

from __future__ import annotations

import math

from . import svg
from .model import Disc, Dots, Figure, Lines, Poly
from .style import Hatch, HouseStyle, _mix

#: The inset of the drawing from the sheet edge, in sheet units.
MARGIN = 18.0
#: The shortest a product's primary dimension is drawn, in sheet units (the
#: sheet is 200 x 300) before the square-root lift stops applying.
FLOOR = 45.0

LW_PART = "1.6"
LW_LINE = "0.8"


def type_scale(extent: tuple[float, float]) -> float:
    """Sheet units per inch for a product type: its largest drawn extent fills the sheet."""
    width, height = extent
    aw, ah = svg.WIDTH - 2 * MARGIN, svg.HEIGHT - 2 * MARGIN
    return min(aw / width, ah / height)


def product_scale(extent: tuple[float, float], size_in: float) -> float:
    """The scale ONE product is drawn at: its type's, lifted monotonically when tiny.

    The primary dimension is drawn ``d = type_scale * size_in`` long; below
    :data:`FLOOR` it is drawn ``sqrt(FLOOR * d)`` long instead, which is
    increasing in ``d`` -- so order by ``size_in`` is order on the sheet.
    """
    scale = type_scale(extent)
    drawn = scale * size_in
    if 0 < drawn < FLOOR:
        return math.sqrt(FLOOR * drawn) / size_in
    return scale


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


def _frame(page: svg.Svg, house: HouseStyle) -> None:
    ink = house.ink
    if house.frame == "rule":
        page.rect(6, 6, svg.WIDTH - 12, svg.HEIGHT - 12, fill="none", stroke=ink, stroke_width="1")
    elif house.frame == "rounded":
        page.add(
            f'<rect x="6" y="6" width="{svg.WIDTH - 12}" height="{svg.HEIGHT - 12}" rx="14" '
            f'fill="none" stroke="{ink}" stroke-width="1.4"/>'
        )
    elif house.frame == "corners":
        w, h, a = svg.WIDTH, svg.HEIGHT, 18
        page.lines(
            [
                ((6, 6 + a), (6, 6)),
                ((6, 6), (6 + a, 6)),
                ((w - 6 - a, 6), (w - 6, 6)),
                ((w - 6, 6), (w - 6, 6 + a)),
                ((6, h - 6 - a), (6, h - 6)),
                ((6, h - 6), (6 + a, h - 6)),
                ((w - 6 - a, h - 6), (w - 6, h - 6)),
                ((w - 6, h - 6), (w - 6, h - 6 - a)),
            ],
            stroke=ink,
            stroke_width="2",
        )


def paint(
    figure: Figure,
    house: HouseStyle,
    fill: str,
    hatch: Hatch | None,
    extent: tuple[float, float],
) -> bytes:
    """The figure on a sheet, as SVG bytes. Contains no text of any kind."""
    page = svg.Svg(background=house.paper)
    _frame(page, house)

    x0, y0, x1, y1 = figure.bounds()
    bw, bh = max(x1 - x0, 1e-9), max(y1 - y0, 1e-9)
    scale = product_scale(extent, figure.size_in)
    ox = svg.WIDTH / 2 - (x0 + bw / 2) * scale
    oy = svg.HEIGHT / 2 - (y0 + bh / 2) * scale

    def at(p):
        return (ox + p[0] * scale, oy + p[1] * scale)

    hatch_id = _hatch_pattern(page, hatch, house.ink) if hatch is not None else None
    pale = _mix(fill, "#ffffff", 0.5)
    ink = house.ink

    for shape in figure.shapes:
        if isinstance(shape, Lines):
            page.lines(
                [(at(a), at(b)) for a, b in shape.segments],
                stroke=ink,
                stroke_width=LW_LINE,
                stroke_opacity=".8",
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
            colour, hatched = fill, True
        elif shape.role == "plain":
            colour, hatched = pale, False
        elif shape.role == "hole":
            colour, hatched = house.paper, False
        elif shape.role == "dark":
            colour, hatched = _mix(ink, "#ffffff", 0.55), False
        else:  # handle, grip
            colour, hatched = shape.fill or pale, False
        style = {"fill": colour, "stroke": ink, "stroke_width": LW_PART, "stroke_linejoin": "round"}
        if isinstance(shape, Poly):
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
    return page.to_bytes()
