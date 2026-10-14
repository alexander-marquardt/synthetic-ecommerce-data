"""Pillow block bearings (set-screw insert-bearing units in a cast iron
housing): a table-driven type (#101, :mod:`...catalog.tabletype`).

**Sources.** Two published charts, both read 2026-10-07.

* Housing dimensions: the "Pillow Block Bearings UCP200 series" chart at
  http://www.queensbearing.com/products/51-Pillow-Block-Bearings-UCP200-series.html.
  It lists seventeen housing sizes, 202 to 218, in millimetres. Six are
  stated here (204, 205, 206, 208, 210, 212) with four of its columns: ``h``
  (base to shaft centre), ``a`` (overall length), ``e`` (bolt hole centres)
  and ``w`` (overall height). ``a``, ``e`` and ``w`` are converted to inches
  and rounded to two places, as inch listings of these units print them.
  ``h`` is stated as the sixteenth of an inch the chart's figure is within
  0.06 mm of (33.3 mm is 1-5/16 in), which is how inch listings print it.
* Which inch bores a housing takes: the inch-model table at
  https://www.fuli-bearings.com/products/bearing-cross-reference/ucp-200-series/
  for housings 204 to 208. That page says its sizes are per JIS B 1557
  (insert bearing units); the standard itself was not read.

The 2 in bore in the 210 housing and the 2-1/4 in bore in the 212 housing
are as distributor listings of these units state them (read 2026-10-07).

**Dropped.** Housings 207, 209 and 211: no chart read gives their inch
bores. The 211 housing also takes a 2 in bore, and a table's sizes are
distinct, so 2 in is the 210 unit only. Flange units (2-bolt and 4-bolt) are
a different outline with different dimensions and are not part of this type.
Load capacities are not published: they are forces, and a table's columns
are lengths. Only the cast iron housing is stated.

``a`` is published as ``Overall Length``, ``w`` as ``Overall Height`` and
``e`` as ``Bolt Hole Center-to-Center``, the census names. ``Bore`` is the
radial ball bearing's name for it. ``Base to Center Height`` is a
``names.NAME_EXCEPTIONS`` entry: the census has no name for it.

The price is a declared ladder, not measured (see ``tabletype``): about
48 USD for one 3/4 in unit at the standard tier, which puts the economy
tier near the 25 to 130 USD that economy listings of these sizes showed.
"""

from __future__ import annotations

from collections.abc import Mapping

from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.domains.industrial.tabletype import TableType, Variant, spec

#: ``(bore, h, a, e, w)`` in inches, with the housing size each row is.
ROWS = (
    (0.75, 1.3125, 5.00, 3.74, 2.56),  # 204
    (0.875, 1.4375, 5.51, 4.13, 2.80),  # 205
    (1.0, 1.4375, 5.51, 4.13, 2.80),  # 205
    (1.125, 1.6875, 6.50, 4.76, 3.27),  # 206
    (1.1875, 1.6875, 6.50, 4.76, 3.27),  # 206
    (1.25, 1.6875, 6.50, 4.76, 3.27),  # 206
    (1.5, 1.9375, 7.24, 5.39, 3.86),  # 208
    (2.0, 2.25, 8.11, 6.26, 4.49),  # 210
    (2.25, 2.75, 9.49, 7.24, 5.43),  # 212
)
#: Nominal proportions, for what no published column gives. Of the base to
#: centre height: the foot's thickness. Of the bolt centres: a slot's width.
#: Of the housing's radius: the neck's half width and the insert's radius.
FOOT = 0.3
SLOT = 0.1
NECK = 0.8
INSERT = 0.72


def draw(values: Mapping[str, float]) -> Figure:
    """The unit seen along the shaft: the foot on the ground with its two
    bolt slots cut through it, and the round housing above with the insert
    and the bore at ``Base to Center Height``."""
    bore = values["Bore Dia."]
    centre = values["Base to Center Height"]
    half = values["Overall Length"] / 2
    bolts = values["Bolt Hole Center-to-Center"] / 2
    radius = values["Overall Height"] - centre
    foot = FOOT * centre
    # The page's y runs down: the mounting face is y = 0 and the unit is above it.
    fig = Figure(size_in=bore)
    fig.rect(-half, -foot, half, 0.0)
    fig.rect(-NECK * radius, -centre, NECK * radius, -foot)
    fig.disc((0.0, -centre), radius)
    fig.disc((0.0, -centre), max(INSERT * radius, 0.6 * bore), "plain")
    fig.disc((0.0, -centre), bore / 2, "hole")
    slot = SLOT * bolts
    for x in (-bolts, bolts):
        fig.rect(x - slot, -foot, x + slot, 0.0, "hole")
    return fig


TABLE = TableType(
    "pillow_block_bearings",
    category=("Motion Control & Fluid Power", "Bearings", "Pillow Block Bearings"),
    item="Pillow Block Bearing",
    standards_family="motion",
    standard="JIS B 1557",
    columns=(
        "Bore Dia.",
        "Base to Center Height",
        "Overall Length",
        "Bolt Hole Center-to-Center",
        "Overall Height",
    ),
    rows=ROWS,
    variants=(Variant("Cast Iron", "Painted", 1.0),),
    packs=(1, 2, 4),
    base_price=48.0,
    size_slope=1.5,
    pack_slope=0.95,
    draw=draw,
    extent=(9.5, 5.45),
    share=0.02,
    series="PB",
    unit="in",
    use_lines=(
        "Bolts to a flat surface to carry a shaft parallel to it.",
        "Two set screws on the inner ring lock the insert bearing to the shaft.",
    ),
)
SPEC = spec(TABLE)
