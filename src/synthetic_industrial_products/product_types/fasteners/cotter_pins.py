"""Cotter pins (split pins): a table-driven type (#101, :mod:`...catalog.tabletype`).

**Source.** The dimension chart at https://www.fasteners.eu/standards/ISO/1234/
(retrieved 2026-10-07), which the page presents as ISO 1234, "Split pins". The
standard itself was not read; every figure below is that chart's. Its rows
are ``d`` (the nominal size, which is the hole the pin fits), ``a max.`` (how
far one prong extends past the other), ``b`` (the length of the eye) and
``c`` (the width of the eye; the chart heads it "c mam."). Twelve of its
sixteen sizes (0.6 mm to 20 mm) are stated, 1 mm to 13 mm.

``d`` is published as ``Diameter``, ``c`` as ``Head Diameter`` and ``b`` as
``Head Height``, the census names for those measurements. ``a`` is not
published: the census has no name for it. The chart gives no lengths, so a
record publishes none and the drawing's shank is a nominal proportion.

Steel (zinc plated), brass and 18-8 stainless split pins are all sold. The
price is a declared ladder, not measured (see ``tabletype``): about 1.40 USD
for 25 of the 1 mm steel pin.
"""

from __future__ import annotations

from collections.abc import Mapping

from ...catalog.tabletype import TableType, Variant, spec
from ...drawing.model import Figure, arc

#: ``(d, c, b)`` in millimetres, as the chart prints them.
ROWS = (
    (1.0, 1.8, 3.0),
    (1.2, 2.0, 3.0),
    (1.6, 2.8, 3.2),
    (2.0, 3.6, 4.0),
    (2.5, 4.6, 5.0),
    (3.2, 5.8, 6.4),
    (4.0, 7.4, 8.0),
    (5.0, 9.2, 10.0),
    (6.3, 11.8, 12.6),
    (8.0, 15.0, 16.0),
    (10.0, 19.0, 20.0),
    (13.0, 24.8, 26.0),
)
#: The drawn shank, in diameters: the chart gives no length to draw.
SHANK = 6.0
#: How far the short prong stops above the long one, in diameters.
STEP = 0.6


def draw(values: Mapping[str, float]) -> Figure:
    """The pin standing on its prongs: two half-round wires, and the eye
    ``Head Diameter`` wide and ``Head Height`` long above them."""
    d, c, b = values["Diameter"], values["Head Diameter"], values["Head Height"]
    shank = SHANK * d
    radius = c / 2
    centre = (0.0, shank + b - radius)
    fig = Figure(size_in=d)
    fig.rect(-d / 2, STEP * d, 0.0, shank)
    fig.rect(0.0, 0.0, d / 2, shank)
    # Thirty steps of ten degrees, so the eye's widest and highest points
    # are on the outline and it measures exactly c by b.
    fig.poly([(d / 2, shank), *arc(centre, radius, -60.0, 240.0, 30), (-d / 2, shank)])
    # Half-round wire: each leg is half the diameter thick.
    if radius > d / 2:
        fig.disc(centre, radius - d / 2, "hole")
    return fig


TABLE = TableType(
    "cotter_pins",
    category=("Fasteners", "Pins", "Cotter Pins"),
    item="Cotter Pin",
    standards_family="fastener",
    standard="ISO 1234",
    columns=("Diameter", "Head Diameter", "Head Height"),
    rows=ROWS,
    variants=(
        Variant("Steel", "Zinc Plated", 1.0),
        Variant("Brass", "Plain", 1.8),
        Variant("18-8 Stainless Steel", "Plain", 2.2),
    ),
    packs=(25, 100, 500),
    base_price=1.40,
    size_slope=1.1,
    pack_slope=0.8,
    draw=draw,
    extent=(1.1, 4.2),
    share=0.015,
    default_lines=39,
    default_skus=67,
    series="CP",
    use_lines=(
        "Passed through a cross-drilled hole and spread to hold a castle nut or clevis pin.",
        "Locks a slotted nut on a drilled bolt or stud so it cannot back off.",
    ),
)
SPEC = spec(TABLE)
