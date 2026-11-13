"""Round bar stock: cold-finished metal rod sold by diameter, alloy and cut length (#830).

A small generator rather than a breadth row, as key stock is: a diameter, an alloy, a
finish and a cut length are the whole part, so the spec space is their product. It
replaces the breadth row ``bar_stock_round`` (2 SKUs) and draws from the ``material``
brand family (``core/brands.py``), not the fastener pool the row used.

Sources, and what is NOT claimed:

* The diameters, alloys, finishes and lengths are the ones a metal distributor's
  cold-finished round bar listings carry: fractional diameters from 1/8" to 3"
  (sixteenths to 1", eighths to 2", quarters to 3"), the free-machining and medium-carbon
  steels, 4140 and 4340 alloy steel, 303, 304 and 316 stainless, 2011, 6061 and 7075
  aluminum and C360 brass, in 12", 36", 72" and 144" bars. They are conventional sizes.
* ASTM A108 (cold-finished carbon and alloy steel bar) and ASTM B211 (aluminum bar)
  are the specifications such bar is sold to. Neither was read, and neither prints a
  table of stocked diameters (a bar is made to order at any size), so no record
  publishes ``Standards``, a tolerance figure or a mechanical property; the provenance
  says no standard fixes the values.
* ``Ground`` is the precision-ground (centerless ground) bar a distributor lists beside
  the cold-drawn one, for the steels and the stainless only; only its name is published.
* The price is GENERATED, not measured: the price census has no bar stock.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from fractions import Fraction
from typing import Any

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.model import keyword_attribute
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import NO_STANDARD
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "bar_stock_round"
#: The breadth row's title noun, kept.
ITEM = "Round Bar Stock"

#: Stocked diameters, inches: sixteenths to 1", eighths to 2", quarters to 3".
DIAMETERS: tuple[Fraction, ...] = (
    *(Fraction(n, 16) for n in range(2, 17)),
    *(Fraction(n, 8) for n in range(9, 17)),
    *(Fraction(n, 4) for n in range(9, 13)),
)

#: (Material, Material Grade, the finishes it is stocked in). ``Material`` is the
#: catalog's name for the metal, so the Material facet and the drawing's fill and hatch
#: read it as every other type does; the alloy is its ``Material Grade``.
ALLOYS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("Steel", "1018", ("Bright", "Ground")),
    ("Steel", "1045", ("Bright", "Ground")),
    ("Steel", "12L14", ("Bright", "Ground")),
    ("Steel", "1215", ("Bright",)),
    ("Alloy Steel", "4140", ("Bright", "Ground")),
    ("Alloy Steel", "4340", ("Bright",)),
    ("Stainless Steel", "303", ("Bright", "Ground")),
    ("Stainless Steel", "304", ("Bright", "Ground")),
    ("Stainless Steel", "316", ("Bright", "Ground")),
    ("Aluminum", "2011-T3", ("Bright",)),
    ("Aluminum", "6061-T6", ("Bright",)),
    ("Aluminum", "7075-T6", ("Bright",)),
    ("Brass", "C360", ("Bright",)),
)
#: Bar lengths, inches.
LENGTHS = (12.0, 36.0, 72.0, 144.0)
#: A line is one alloy, finish and length; its SKUs are diameters.
COMBOS: tuple[tuple[str, str, str, float], ...] = tuple(
    (material, grade, finish, length)
    for length in LENGTHS
    for material, grade, finishes in ALLOYS
    for finish in finishes
)

#: How far apart one combination's successive lines start in DIAMETERS, and how far
#: apart two neighbouring combinations' first lines start. Neither shares a factor with
#: the 27 diameters, so every diameter is reached.
STRIDE = 7
OFFSET = 5

VOCAB = (
    AttrSpec("Material", "line"),
    AttrSpec("Material Grade", "line"),
    AttrSpec("Finish", "line"),
    AttrSpec("Length", "line", kind="length"),
    AttrSpec("Diameter", "sku", kind="length"),
)

PROVENANCE = f"Diameter and Length are conventional stocked sizes; {NO_STANDARD}"


def line_diameters(start: int, count: int) -> list[Fraction]:
    """The diameters a line offers: ``count`` of them from ``start`` on, round DIAMETERS."""
    return [DIAMETERS[(start + k) % len(DIAMETERS)] for k in range(min(count, len(DIAMETERS)))]


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    """One line: an alloy, a finish and a length, and a window of the diameters."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    combo = gen._rotate("combo", len(COMBOS))
    material, grade, finish, length = COMBOS[combo]
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"RB{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    style = gen._style("in")
    draft.line_attrs = [
        keyword_attribute("Material", material),
        keyword_attribute("Material Grade", grade),
        keyword_attribute("Finish", finish),
        gen._length("Length", length, style),
    ]
    draft.descriptors = [("Material Grade", grade), ("Material", material)]
    start = OFFSET * combo + STRIDE * gen._rotate(f"diameters:{combo}", len(DIAMETERS))
    for diameter in line_diameters(start, gen._variant_count()):
        child = ChildDraft(system="in")
        child.primary = gen._length("Diameter", float(diameter), style)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

#: A bar is drawn compressed, with a break, into KNEE + TAIL inches at most, as key
#: stock is: a 144" bar at scale would leave its section a dot. The tail grows slowly
#: enough (SCALE inches) that a longer bar still draws longer.
KNEE = 2.4
TAIL = 0.6
SCALE = 40.0
#: The gap between the bar and its end view, as a share of the diameter.
GAP = 0.4
#: The drawing's extent, measured at the default and ``--lines 39000`` builds
#: (docs/adding-a-type.md "Figure and extent"): the 3" bar's side view, gap and end
#: view across, and a 144" bar compressed down the page.
EXTENT = (7.55, 3.1)


def _inches(record: Mapping[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The bar from the side, broken to fit, beside its round end."""
    diameter = _inches(record, "Diameter")
    length = _inches(record, "Length")
    d = diameter or 0.5
    full = length or 12.0
    drawn = full if full <= KNEE else KNEE + TAIL * (1 - math.exp(-(full - KNEE) / SCALE))
    half = d / 2
    fig = Figure(size_in=max(drawn, d))
    fig.rect(-half, 0.0, half, drawn)
    if full > KNEE:
        cut = drawn * 0.45
        fig.lines([((-1.15 * half, cut + k), (1.15 * half, cut + k + 0.04)) for k in (0.0, 0.08)])
    centre = half + GAP * d + half
    fig.disc((centre, half), half)
    fig.lines([((centre - 0.6 * half, half), (centre + 0.6 * half, half))])
    source = "record" if diameter and length else ("partial" if diameter else "nominal")
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: GENERATED, NOT MEASURED: the price census has no bar stock. The metal over plain
#: carbon steel, hand-set from distributor listings' spread at one diameter: alloy steel
#: about half again, aluminum a little over, brass and stainless about three times.
MATERIALS = {
    "Steel": 1.0,
    "Alloy Steel": 1.5,
    "Aluminum": 1.3,
    "Brass": 2.8,
    "Stainless Steel": 3.0,
}
#: A ground bar over the cold-drawn one.
GROUND_FACTOR = 1.6

#: GENERATED, NOT MEASURED. Anchored on a standard brand's 1/2" x 12" cold-drawn steel
#: bar at about 7 USD; the slope on the diameter (1.5) puts a 1" bar near three times a
#: 1/2" one, as the listings do. A 144" bar costs a little under twelve 12" bars.
PRICE = PriceModel(
    7.0,
    0.5,
    1.5,
    0.2,
    0.08,
    measured=False,
    pack_attribute="Length",
    pack_slope=0.93,
    pack_ref=12.0,
    materials=MATERIALS,
    option_attribute="Finish",
    option_factors={"Ground": GROUND_FACTOR},
)

SPEC = TypeSpec(
    KEY,
    category=("Raw Materials", "Bar & Rod Stock", "Round Bars"),
    standards_family="material",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=build,
    share=0.016,
    price=PRICE,
    may_claim=frozenset(),
    key_attributes=("Diameter",),
    unit_primary="Diameter",
    compat=False,
    use_lines=(
        "Cut and machined into shafts, pins, spacers and turned parts.",
        "Sold by the bar: order the length to cut from.",
    ),
)
