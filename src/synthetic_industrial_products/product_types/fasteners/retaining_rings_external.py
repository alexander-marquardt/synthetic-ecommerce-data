"""External retaining rings (circlips for shafts): a table-driven type (#101,
:mod:`...catalog.tabletype`).

**Source.** The dimension chart at https://www.fasteners.eu/standards/DIN/471/
(retrieved 2026-10-07), which the page presents as DIN 471, "Retaining rings
for shafts". The standard itself was not read; every figure below is that
chart's. Twelve of its sizes are stated, for 6 mm to 50 mm shafts, with five
of its columns: ``d1`` (the shaft's nominal diameter), ``d3`` (the ring's
inside diameter before it is fitted), ``s`` (the ring's thickness), ``d2``
(the diameter of the groove the ring sits in) and ``m`` (that groove's
width).

``d3`` is published as ``Inside Diameter`` and ``s`` as ``Thickness``, the
census names. The census has no retaining ring, so ``For Shaft Diameter``,
``Groove Diameter`` and ``Groove Width`` are ``names.NAME_EXCEPTIONS``. The
chart's lug and beam columns are not published; the drawing's ring width and
lugs are nominal proportions.

Rings of this form are sold in carbon spring steel with a black finish and in
stainless steel. The price is a declared ladder, not measured (see
``tabletype``): about 1.60 USD for 10 of the 6 mm steel ring.
"""

from __future__ import annotations

from collections.abc import Mapping

from ...catalog.tabletype import TableType, Variant, spec
from ...drawing.model import Figure, arc

#: ``(d1, d3, s, d2, m)`` in millimetres, as the chart prints them.
ROWS = (
    (6.0, 5.6, 0.7, 5.7, 0.8),
    (8.0, 7.4, 0.8, 7.6, 0.9),
    (10.0, 9.3, 1.0, 9.6, 1.1),
    (12.0, 11.0, 1.0, 11.5, 1.1),
    (15.0, 13.8, 1.0, 14.3, 1.1),
    (16.0, 14.7, 1.0, 15.2, 1.1),
    (20.0, 18.5, 1.2, 19.0, 1.3),
    (25.0, 23.2, 1.2, 23.9, 1.3),
    (30.0, 27.9, 1.5, 28.6, 1.6),
    (35.0, 32.2, 1.5, 33.0, 1.6),
    (40.0, 36.5, 1.75, 37.5, 1.85),
    (50.0, 45.8, 2.0, 47.0, 2.15),
)
#: Nominal proportions of the shaft diameter, for what no published value
#: gives: the ring's radial width, its lugs and their holes, and the spacing
#: of the views.
BEAM = 0.11
LUG = 0.09
LUG_HOLE = 0.035
SPACE = 0.12
#: Half the opening between the ring's ends, in degrees.
OPENING = 12.0


def draw(values: Mapping[str, float]) -> Figure:
    """The ring face on, its edge beside it, and under them the shaft with
    the groove the ring snaps into."""
    shaft = values["For Shaft Diameter"]
    inner = values["Inside Diameter"] / 2
    thickness = values["Thickness"]
    groove = values["Groove Diameter"] / 2
    width = values["Groove Width"]
    outer = inner + BEAM * shaft
    start, end = 90.0 + OPENING, 450.0 - OPENING
    fig = Figure(size_in=shaft)
    fig.poly([*arc((0.0, 0.0), outer, start, end, 28), *arc((0.0, 0.0), inner, end, start, 28)])
    # The lugs stand outward from the inside edge, as a shaft ring's do.
    for point in arc((0.0, 0.0), inner + LUG * shaft, start, end, 1):
        fig.disc(point, LUG * shaft)
        fig.disc(point, LUG_HOLE * shaft, "hole")
    edge = outer + 2 * LUG * shaft + SPACE * shaft
    fig.rect(edge, -outer, edge + thickness, outer, "plain")
    # The shaft lies across the page, its groove under the ring's centre.
    axis = -(outer + SPACE * shaft + shaft / 2)
    half, r = outer, shaft / 2
    fig.poly(
        [
            (-half, axis - r), (half, axis - r), (half, axis + r), (width / 2, axis + r),
            (width / 2, axis + groove), (-width / 2, axis + groove), (-width / 2, axis + r),
            (-half, axis + r),
        ],
        "plain",
    )  # fmt: skip
    fig.lines([((-width / 2, axis - groove), (width / 2, axis - groove))])
    return fig


TABLE = TableType(
    "retaining_rings_external",
    category=("Fasteners", "Retaining Rings", "External Retaining Rings"),
    item="External Retaining Ring",
    standards_family="fastener",
    standard="DIN 471",
    columns=(
        "For Shaft Diameter",
        "Inside Diameter",
        "Thickness",
        "Groove Diameter",
        "Groove Width",
    ),
    rows=ROWS,
    variants=(
        Variant("Steel", "Black Oxide", 1.0),
        Variant("Stainless Steel", "Plain", 2.6),
    ),
    packs=(10, 50, 100),
    base_price=1.60,
    size_slope=1.2,
    pack_slope=0.85,
    draw=draw,
    extent=(3.0, 4.65),
    share=0.015,
    default_lines=39,
    default_skus=82,
    series="RR",
    use_lines=(
        "Snaps into a groove on a shaft to hold a bearing, gear or pulley against a shoulder.",
        "Fitted with retaining ring pliers through the two lug holes.",
    ),
)
SPEC = spec(TABLE)
