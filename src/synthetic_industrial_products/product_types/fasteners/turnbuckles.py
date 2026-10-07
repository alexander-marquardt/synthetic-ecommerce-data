"""Turnbuckles: a table-driven type (#101, :mod:`...catalog.tabletype`).

**Source.** A maker's catalog pages for drop forged turnbuckles,
http://www.chicagohardware.com/catalog/04_07_Fturnbuckles.pdf (retrieved
2026-10-07). The pages say the turnbuckles meet the performance requirements
of ASTM F1145; the standard itself was not read, and every figure below is
that chart's. It lists eight thread diameters, 1/4" to 1", in twenty-one
diameter and take-up combinations, each with a closed length per end
fitting, and a working load limit per diameter for each fitting (eye, jaw,
hook). All eight diameters are stated here, each at one take-up: 6" where
the chart has it, and the chart's only take-up for 1/4" (4") and 5/16"
(4-1/2"). The longer take-ups (9", 12", 18") and the 1/2" x 2" are left out.

Three of the chart's end-fitting pairs are built: eye and eye, jaw and jaw,
hook and eye. The closed length is the chart's for that pair. The working
load limit is the chart's for the fitting: an eye and a jaw carry the same
limit, a hook a lower one, so a hook and eye turnbuckle publishes the
hook's. It is published as ``Load Capacity``, in pounds-force, the census
name and the spelling the bearing's load ratings use.

Hot dip galvanized steel only. The chart's self-colored finish, its hook and
hook and jaw and eye pairs, and stub ends are left out; so are stainless and
the light cast turnbuckles, which the chart does not cover.

The price is a declared ladder, not measured (see ``tabletype``): about 15.50
USD for the 1/4" at the standard brand tier, rising with the thread diameter.
The ladder has one factor per material and this type has one material, so
the three end fittings cost the same at one size. A jaw end costs more than
an eye in practice; the mechanism has no place to say so.

The table mechanism builds the size columns every end fitting shares. The
end fitting, and the two columns that depend on it, are added to each line
it drafts (:func:`_make`), which is the one thing this module does beyond
declaring its table.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Mapping
from typing import Any

from ...catalog.model import keyword_attribute, numeric_attribute
from ...catalog.newtypes import table_provenance
from ...catalog.tabletype import TableType, Variant, lengths, spec
from ...catalog.vocab import AttrSpec
from ...dimensions import DimensionParseError, parse_length
from ...drawing.figures import Drawn
from ...drawing.model import Figure, arc

SIZE = "Thread Dia."
TAKE_UP = "Take Up"
CLOSED = "Closed Length"
LOAD = "Load Capacity"
END = "End Style"
STANDARD = "ASTM F1145"

EYE, JAW, HOOK = "Eye and Eye", "Jaw and Jaw", "Hook and Eye"

#: ``(thread diameter, take-up)`` in inches, as the chart prints them.
ROWS = (
    (0.25, 4.0),
    (0.3125, 4.5),
    (0.375, 6.0),
    (0.5, 6.0),
    (0.625, 6.0),
    (0.75, 6.0),
    (0.875, 6.0),
    (1.0, 6.0),
)
#: Each end-fitting pair's closed length in inches, one per row of ``ROWS``.
#: The 7/8" eye and eye is longer closed than the 1": that is the chart's.
CLOSED_IN = {
    EYE: (8.0, 9.0, 11.5, 13.0, 13.5, 14.75, 18.0, 17.0),
    JAW: (8.5, 9.25, 11.5, 13.5, 15.75, 16.5, 19.5, 20.1875),
    HOOK: (8.25, 9.25, 11.75, 13.625, 14.125, 15.75, 18.5, 19.5),
}
#: Each pair's working load limit in pounds, one per row of ``ROWS``: the
#: eye's (which is also the jaw's), and the hook's for the pair with a hook.
EYE_LIMIT_LB = (500, 800, 1200, 2200, 3500, 5200, 7200, 10000)
HOOK_LIMIT_LB = (400, 700, 1000, 1500, 2250, 3000, 3200, 5000)
LIMIT_LB = {EYE: EYE_LIMIT_LB, JAW: EYE_LIMIT_LB, HOOK: HOOK_LIMIT_LB}

# The chart gives none of the proportions below: they are nominal, in thread
# diameters, and chosen so every end fitting fits its row's closed length.
#: The body's height, which is also every end fitting's.
HEIGHT = 3.0
#: The solid end of the body the rod threads into. The open window between
#: the two is drawn the take-up long.
BOSS = 0.75
#: One side rail of the body.
RAIL = 0.5
#: An end fitting's length along the rod.
FITTING = 3.0


def _end(fig: Figure, kind: str, tip: float, d: float, sign: float) -> None:
    """One end fitting, its tip at ``tip`` and its rod side ``sign`` of it."""

    def x(along: float) -> float:
        return tip + sign * along * d

    half = HEIGHT * d / 2
    if kind == "eye":
        fig.disc((x(1.5), 0.0), half)
        fig.disc((x(1.5), 0.0), 0.9 * d, "hole")
    elif kind == "hook":
        # Open for sixty degrees beside the rod. Thirty steps of ten degrees
        # put the hook's highest, lowest and outermost points on the outline.
        start, stop = (60.0, 360.0) if sign > 0 else (120.0, -180.0)
        centre = (x(1.5), 0.0)
        fig.poly([*arc(centre, half, start, stop, 30), *arc(centre, 0.9 * d, stop, start, 30)])
    else:
        # The fork from the side: two tines off a base, and the cross pin
        # through both, standing proud of each.
        for low, high in ((0.6, 1.2), (-1.2, -0.6)):
            fig.rect(min(x(0.0), x(2.0)), low * d, max(x(0.0), x(2.0)), high * d)
        fig.rect(min(x(2.0), x(3.0)), -1.2 * d, max(x(2.0), x(3.0)), 1.2 * d)
        fig.rect(min(x(0.6), x(1.0)), -half, max(x(0.6), x(1.0)), half)


def draw(values: Mapping[str, float], end: str = EYE) -> Figure:
    """The turnbuckle from the side, closed: the open body, a threaded rod
    out of each end, and the end fitting ``end`` names on each rod. It is the
    ``Closed Length`` long and three thread diameters high."""
    d, take_up, closed = values[SIZE], values[TAKE_UP], values[CLOSED]
    half = HEIGHT * d / 2
    left, right = -closed / 2, closed / 2
    # A record whose closed length is too short for its take-up keeps both
    # end fittings and loses window.
    window = max(d, min(take_up, closed - 2 * (FITTING + BOSS) * d)) / 2
    body = window + BOSS * d
    fig = Figure(size_in=d)
    fig.rect(-body, -half, body, half)
    fig.rect(-window, -half + RAIL * d, window, half - RAIL * d, "hole")
    # Each rod runs from its fitting through the boss and shows in the window.
    reach = min(window, d)
    fig.rect(left + FITTING * d, -d / 2, -window + reach, d / 2)
    fig.rect(window - reach, -d / 2, right - FITTING * d, d / 2)
    first, second = {EYE: ("eye", "eye"), JAW: ("jaw", "jaw")}.get(end, ("hook", "eye"))
    _end(fig, first, left, d, 1.0)
    _end(fig, second, right, d, -1.0)
    return fig


TABLE = TableType(
    "turnbuckles",
    category=("Fasteners", "Rigging Hardware", "Forged Turnbuckles"),
    item="Turnbuckle",
    standards_family="fastener",
    standard=STANDARD,
    columns=(SIZE, TAKE_UP),
    rows=ROWS,
    variants=(Variant("Steel", "Hot Dip Galvanized", 1.0),),
    # Sold singly.
    packs=(1,),
    base_price=15.50,
    size_slope=1.3,
    pack_slope=0.8,
    draw=draw,
    extent=(20.3, 3.1),
    share=0.018,
    default_lines=42,
    default_skus=87,
    series="TB",
    unit="in",
    use_lines=(
        "Takes up slack and sets the tension in a cable, rod or guy line.",
        "Turning the body draws both end fittings in or lets them out together.",
    ),
)


def _index(dia: float) -> int:
    """The row whose thread diameter is nearest ``dia`` (inches)."""
    return min(range(len(ROWS)), key=lambda i: abs(ROWS[i][0] - dia))


def _figure(record: dict[str, str]) -> Drawn:
    values, source = lengths(TABLE, record)
    end = record.get(END, EYE)
    if end not in CLOSED_IN:
        end, source = EYE, "partial" if source == "record" else source
    try:
        closed = parse_length(record[CLOSED]).inches
    except (KeyError, DimensionParseError):
        # The nearest row's closed length, at that row's proportion.
        row = _index(values[SIZE])
        closed = CLOSED_IN[end][row] * values[SIZE] / ROWS[row][0]
        source = "partial" if source == "record" else source
    return Drawn(draw({**values, CLOSED: closed}, end), source)


def _make(base: Callable[..., Any]) -> Callable[..., Any]:
    def make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
        draft = base(gen, type_key, category)
        # Rotated, like the table's own rows, so every pair meets every size.
        ends = tuple(CLOSED_IN)
        end = ends[gen._rotate(f"end:{type_key}", len(ends))]
        draft.line_attrs.append(keyword_attribute(END, end))
        draft.descriptors = [(END, end)]
        draft.provenance = table_provenance(*((name, STANDARD) for name in (SIZE, TAKE_UP, CLOSED)))
        style = gen._style(TABLE.unit)
        for child in draft.children:
            row = _index(child.primary.value_num)
            limit = LIMIT_LB[end][row]
            child.attrs.append(gen._length(CLOSED, CLOSED_IN[end][row], style))
            child.attrs.append(numeric_attribute(LOAD, f"{limit:,} lbf", float(limit)))
        return draft

    return make


_BASE = spec(TABLE)
SPEC = dataclasses.replace(
    _BASE,
    vocab=(
        *_BASE.vocab,
        AttrSpec(name=END, scope="line", presence=1.0, kind="keyword"),
        AttrSpec(name=CLOSED, scope="sku", presence=1.0, kind="length"),
        AttrSpec(name=LOAD, scope="sku", presence=1.0, kind="count"),
    ),
    figure=_figure,
    make=_make(_BASE.make),
)
