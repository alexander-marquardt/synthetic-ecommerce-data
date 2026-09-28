"""Placing a figure on the sheet and painting it in the brand's house style.

The scale. Every product of a type is drawn at ONE scale: the type's largest
product fills its sheet, and every other is drawn at its true size relative to
that one. So an M3 washer is drawn at about a quarter the diameter of an M16
washer, and a longer screw of a product is drawn longer than its shorter
sibling, whatever their proportions.

The one exception is legibility, and it is strictly monotonic: a product
drawn smaller than :data:`FLOOR` of the sheet is enlarged along a square-root
curve instead of being clamped, so two small siblings still differ in size --
the smaller is always drawn smaller -- and nothing collapses to one size.
Proportions are always exactly the record's.
"""

from __future__ import annotations

import math

from . import svg
from .model import Disc, Dots, Figure, Lines, Poly
from .style import Hatch, HouseStyle, _mix

#: The inset of the drawing from the sheet edge, in sheet units.
MARGIN = 18.0
#: Below this fraction of the sheet a product is enlarged for legibility, on
#: a square-root curve (monotonic: smaller stays smaller).
FLOOR = 0.2

LW_PART = "1.6"
LW_LINE = "0.8"


def product_scale(fit: float, size_in: float, size_range: tuple[float, float]) -> float:
    """Sheet units per inch: the type's one scale, with a monotonic legibility floor.

    ``fit`` is the scale at which THIS figure exactly fills the sheet. The
    type's largest product (``size_range[1]``) fills it, so this product fills
    ``size_in / top`` of it -- its true relative size.
    """
    _, top = size_range
    if size_in <= 0 or top <= 0:
        return fit
    fraction = min(1.0, size_in / top)
    if fraction < FLOOR:
        fraction = FLOOR * math.sqrt(fraction / FLOOR)
    return fit * fraction


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
    size_range: tuple[float, float],
) -> bytes:
    """The figure on a sheet, as SVG bytes. Contains no text of any kind."""
    page = svg.Svg(background=house.paper)
    _frame(page, house)

    x0, y0, x1, y1 = figure.bounds()
    bw, bh = max(x1 - x0, 1e-9), max(y1 - y0, 1e-9)
    aw, ah = svg.WIDTH - 2 * MARGIN, svg.HEIGHT - 2 * MARGIN
    scale = product_scale(min(aw / bw, ah / bh), figure.size_in, size_range)
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
