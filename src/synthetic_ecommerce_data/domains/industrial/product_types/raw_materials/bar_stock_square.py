"""Square bar stock: cold-drawn four-sided metal bar sold by width, alloy and cut length (#830).

A small generator rather than a breadth row, as the round bar (``bar_stock_round``) is:
a width, an alloy and a cut length are the whole part, so the spec space is their
product. It replaces the breadth row ``bar_stock_square`` (1 SKU) and draws from the
``material`` brand family (``core/brands.py``), not the fastener pool the row used.

Sources, and what is NOT claimed:

* The widths, alloys and lengths are the ones a metal distributor's cold-drawn square
  bar listings carry: fractional widths from 1/8" to 4" (sixteenths to 1", eighths to
  2", quarters to 3", then 3-1/2" and 4"), the free-machining and medium-carbon steels,
  4140 alloy steel, 303, 304 and 316 stainless, 6061 aluminum and C360 brass, in 12",
  36", 72" and 144" bars. They are conventional sizes.
* ASTM A108 (cold-finished carbon and alloy steel bar) and ASTM B211 (aluminum bar)
  are the specifications such bar is sold to. Neither was read, and neither prints a
  table of stocked sizes (a bar is drawn to order at any size), so no record publishes
  ``Standards``, a tolerance figure or a mechanical property; the provenance says no
  standard fixes the values.
* The size is the side of the square, published as ``Width``, the name square key stock
  (``key_stock``) publishes for the same dimension. A square bar has one width, so no
  ``Height`` is published.
* Square bar is drawn, not ground, so a record publishes no ``Finish``.
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

KEY = "bar_stock_square"
#: The breadth row's title noun, kept.
ITEM = "Square Bar Stock"
#: The side of the square, named as square key stock names it.
SIZE = "Width"

#: Stocked widths, inches: sixteenths from 1/8" to 1", eighths to 2", quarters to 3",
#: then 3-1/2" and 4".
SIZES: tuple[Fraction, ...] = (
    *(Fraction(n, 16) for n in range(2, 17)),
    *(Fraction(n, 8) for n in range(9, 17)),
    *(Fraction(n, 4) for n in range(9, 13)),
    Fraction(7, 2),
    Fraction(4),
)

#: (Material, Material Grade). ``Material`` is the catalog's name for the metal, so the
#: Material facet and the drawing's fill and hatch read it as every other type does; the
#: alloy is its ``Material Grade``, spelled as the round bar spells it.
ALLOYS: tuple[tuple[str, str], ...] = (
    ("Steel", "1018"),
    ("Steel", "1045"),
    ("Steel", "12L14"),
    ("Alloy Steel", "4140"),
    ("Stainless Steel", "303"),
    ("Stainless Steel", "304"),
    ("Stainless Steel", "316"),
    ("Aluminum", "6061-T6"),
    ("Brass", "C360"),
)
#: Bar lengths, inches.
LENGTHS = (12.0, 36.0, 72.0, 144.0)
#: A line is one alloy and length; its SKUs are widths.
COMBOS: tuple[tuple[str, str, float], ...] = tuple(
    (material, grade, length) for length in LENGTHS for material, grade in ALLOYS
)

#: How far apart one combination's successive lines start in SIZES, and how far apart
#: two neighbouring combinations' first lines start. Neither shares a factor with the 29
#: sizes, so every size is reached.
STRIDE = 7
OFFSET = 5

VOCAB = (
    AttrSpec("Material", "line"),
    AttrSpec("Material Grade", "line"),
    AttrSpec("Length", "line", kind="length"),
    AttrSpec(SIZE, "sku", kind="length"),
)

PROVENANCE = f"{SIZE} and Length are conventional stocked sizes; {NO_STANDARD}"


def line_sizes(start: int, count: int) -> list[Fraction]:
    """The widths a line offers: ``count`` of them from ``start`` on, round SIZES."""
    return [SIZES[(start + k) % len(SIZES)] for k in range(min(count, len(SIZES)))]


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    """One line: an alloy and a length, and a window of the widths."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    combo = gen._rotate("combo", len(COMBOS))
    material, grade, length = COMBOS[combo]
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"SB{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    style = gen._style("in")
    draft.line_attrs = [
        keyword_attribute("Material", material),
        keyword_attribute("Material Grade", grade),
        gen._length("Length", length, style),
    ]
    draft.descriptors = [("Material Grade", grade), ("Material", material)]
    start = OFFSET * combo + STRIDE * gen._rotate(f"sizes:{combo}", len(SIZES))
    for size in line_sizes(start, gen._variant_count()):
        child = ChildDraft(system="in")
        child.primary = gen._length(SIZE, float(size), style)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

#: A bar is drawn compressed, with a break, into KNEE + TAIL inches at most, as the round
#: bar is: a 144" bar at scale would leave its section a dot. The tail grows slowly
#: enough (SCALE inches) that a longer bar still draws longer.
KNEE = 2.4
TAIL = 0.6
SCALE = 40.0
#: The gap between the bar and its end view, as a share of the width.
GAP = 0.4
#: The drawing's extent, measured at the default and ``--lines 39000`` builds
#: (docs/adding-a-type.md "Figure and extent"): the 4" bar's side view, gap and end
#: view, and the 4" bar's end view, taller than a 144" bar compressed down the page
#: (9.90" x 4.00" at the large build, which reaches the 4" bar), plus 0.1".
EXTENT = (10.0, 4.1)


def _inches(record: Mapping[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The bar from the side, a face towards the eye and broken to fit, beside its square end."""
    width = _inches(record, SIZE)
    length = _inches(record, "Length")
    w = width or 0.5
    full = length or 12.0
    drawn = full if full <= KNEE else KNEE + TAIL * (1 - math.exp(-(full - KNEE) / SCALE))
    half = w / 2
    fig = Figure(size_in=max(drawn, w))
    fig.rect(-half, 0.0, half, drawn)
    if full > KNEE:
        cut = drawn * 0.45
        fig.lines([((-1.15 * half, cut + k), (1.15 * half, cut + k + 0.04)) for k in (0.0, 0.08)])
    left = half + GAP * w
    fig.rect(left, 0.0, left + w, w)
    # The end's diagonals mark it as a section, not a second bar seen from the side.
    fig.lines([((left, 0.0), (left + w, w)), ((left, w), (left + w, 0.0))])
    source = "record" if width and length else ("partial" if width else "nominal")
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: GENERATED, NOT MEASURED: the price census has no bar stock. The metal over plain
#: carbon steel, as the round bar sets it: alloy steel about half again, aluminum a
#: little over, brass and stainless about three times.
MATERIALS = {
    "Steel": 1.0,
    "Alloy Steel": 1.5,
    "Aluminum": 1.3,
    "Brass": 2.8,
    "Stainless Steel": 3.0,
}

#: GENERATED, NOT MEASURED. Anchored on a standard brand's 1/2" x 12" cold-drawn steel
#: square at about 9 USD, over the round bar's 7 and the hex's 8: a square holds about a
#: quarter more metal than a round of its width. The slope on the width (1.5) and the
#: length are the round bar's.
PRICE = PriceModel(
    9.0,
    0.5,
    1.5,
    0.2,
    0.08,
    measured=False,
    pack_attribute="Length",
    pack_slope=0.93,
    pack_ref=12.0,
    materials=MATERIALS,
)

SPEC = TypeSpec(
    KEY,
    category=("Raw Materials", "Bar & Rod Stock", "Square Bars"),
    standards_family="material",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=build,
    share=0.016,
    price=PRICE,
    may_claim=frozenset(),
    key_attributes=(SIZE,),
    unit_primary=SIZE,
    compat=False,
    use_lines=(
        "Cut and machined into keys, gibs, blocks, wear strips and fixture parts.",
        "Sold by the bar: order the length to cut from.",
    ),
)
