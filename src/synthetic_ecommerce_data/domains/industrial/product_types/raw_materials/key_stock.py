"""Key stock: the square or rectangular bar a machine key is cut from (#108).

A small generator rather than a breadth row: a section, a fit, a material and
a length are the whole part, so the spec space is their product.

Sources, and what is NOT claimed:

* The sections, fits, materials and lengths are the ones distributor listings
  of key stock carry (surveyed 2026-10-07): eleven square sizes from 1/8" to
  1", three rectangular sizes, oversized and undersized bars, low-carbon
  steel plain or zinc plated, 18-8 stainless steel, and 12" and 36" bars. No
  standard's table was read for them, so they are conventional sizes and the
  provenance says so.
* ASME B17.1 covers keys and keyseats, and the two fits are its plus- and
  minus-toleranced bars. No chart of its tolerances was found that a reviewer
  can open, so a record states the fit's NAME only: no tolerance figure, no
  ``Standards`` claim, no hardness and no grade (C1018, C1045) is published.
* The price is GENERATED, not measured: the price census has no key stock.
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

KEY = "key_stock"
ITEM = "Key Stock"

#: The square sizes in common stock, inches: width and height are equal.
SQUARE = ("1/8", "3/16", "1/4", "5/16", "3/8", "7/16", "1/2", "5/8", "3/4", "7/8", "1")
#: The rectangular sizes the listings name, inches: (width, height).
RECTANGULAR = (("1/4", "3/16"), ("3/8", "1/4"), ("1/2", "3/8"))
#: Every section, (width, height), smallest width first and a square before
#: the rectangle of its width.
SECTIONS: tuple[tuple[Fraction, Fraction], ...] = tuple(
    sorted(
        [(Fraction(s), Fraction(s)) for s in SQUARE]
        + [(Fraction(w), Fraction(h)) for w, h in RECTANGULAR],
        key=lambda section: (section[0], -section[1]),
    )
)

#: An oversized bar is toleranced on the plus side and an undersized one on
#: the minus side. Only the name is published (see the module docstring).
FITS = ("Oversized", "Undersized")
#: (Material, Finish). The low-carbon steel is published as ``Steel``, the
#: catalog's one name for plain carbon steel: a second name for it would split
#: the Material facet and need a hatch and a fill of its own.
MATERIALS = (
    ("Steel", "Plain"),
    ("Steel", "Zinc Plated"),
    ("18-8 Stainless Steel", "Plain"),
)
#: Bar lengths, inches.
LENGTHS = (12.0, 36.0)
#: A line is one fit, material, finish and length; its SKUs are sections.
COMBOS = tuple(
    (fit, material, finish, length)
    for length in LENGTHS
    for material, finish in MATERIALS
    for fit in FITS
)

#: How far apart one combination's successive lines start in SECTIONS.
STRIDE = 5
#: How far apart two neighbouring combinations' first lines start.
OFFSET = 3

VOCAB = (
    AttrSpec("Item", "line"),
    AttrSpec("Fit", "line"),
    AttrSpec("Material", "line"),
    AttrSpec("Finish", "line"),
    AttrSpec("Length", "line", kind="length"),
    AttrSpec("Width", "sku", kind="length"),
    AttrSpec("Height", "sku", kind="length"),
)

PROVENANCE = f"Width, Height and Length are conventional stocked sizes; {NO_STANDARD}"


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    """One line: a fit, a material and a length, and a window of the sections."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    combo = gen._rotate("combo", len(COMBOS))
    fit, material, finish, length = COMBOS[combo]
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"KS{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    style = gen._style("in")
    draft.line_attrs = [
        keyword_attribute("Item", ITEM),
        keyword_attribute("Fit", fit),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        gen._length("Length", length, style),
    ]
    draft.descriptors = [("Fit", fit), ("Material", material)]
    # A combination's lines start STRIDE sections apart, and each combination
    # OFFSET after the one before, so the few lines a small build gives one
    # combination spread over the sizes. Every section is reached: STRIDE
    # shares no factor with the section count.
    start = OFFSET * combo + STRIDE * gen._rotate(f"sections:{combo}", len(SECTIONS))
    count = min(gen._variant_count(), len(SECTIONS))
    for width, height in (SECTIONS[(start + k) % len(SECTIONS)] for k in range(count)):
        child = ChildDraft(system="in")
        child.primary = gen._length("Width", float(width), style)
        height_attr = gen._length("Height", float(height), style)
        child.attrs = [child.primary, height_attr]
        # A rectangular bar's title names its height: a line can hold the
        # square bar of the same width, and the width alone reads as that one.
        if height != width:
            child.also = height_attr
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

#: A bar is drawn compressed, with a break, into KNEE + TAIL inches at most: a
#: 36" bar at scale would leave its section a dot. The tail grows slowly
#: enough (SCALE inches) that a 36" bar still draws longer than a 12" one.
KNEE = 2.4
TAIL = 0.45
SCALE = 20.0
#: The gap between the bar and its section, as a share of the width.
GAP = 0.4
#: The drawing's extent, measured at the default and ``--lines 39000`` builds
#: (docs/adding-a-type.md "Figure and extent"): the largest drawn is 2.47 x
#: 2.77 in, the 1" bar's break marks, bar, gap and section across and a 36"
#: bar compressed down the page.
EXTENT = (2.6, 2.9)


def _inches(record: Mapping[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The bar seen on its width face, broken to fit, beside its section."""
    width = _inches(record, "Width")
    height = _inches(record, "Height")
    length = _inches(record, "Length")
    w = width or 0.25
    h = height or w
    full = length or 12.0
    drawn = full if full <= KNEE else KNEE + TAIL * (1 - math.exp(-(full - KNEE) / SCALE))
    half = w / 2
    fig = Figure(size_in=drawn)
    fig.rect(-half, 0.0, half, drawn)
    if full > KNEE:
        cut = drawn * 0.45
        fig.lines([((-1.15 * half, cut + k), (1.15 * half, cut + k + 0.04)) for k in (0.0, 0.08)])
    left = half + GAP * w
    fig.rect(left, 0.0, left + w, h)
    source = "record" if width and height and length else ("partial" if width else "nominal")
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: What 18-8 stainless key stock costs over the shared material table's 1.6
#: for 18-8 (``price.MATERIAL_FACTORS``): together 5.6 times steel.
#: GENERATED: the listings show one stainless 1/4" bar at about nine times the
#: plain steel one and two smaller pieces at four to five times.
STAINLESS_FACTOR = 3.5

#: GENERATED, NOT MEASURED: the price census has no key stock. Hand-set so an
#: economy brand's 12" plain bar lands near the listings' economy prices
#: (0.83 at 3/16", 1.19 at 1/4", 3.76 at 1/2", 7.50 at 3/4": a log-log slope
#: of 1.6 on the width). The anchor is the standard tier's 1/4" x 12" bar, the
#: economy price over the economy tier's 0.52. A 36" bar costs a little under
#: three 12" bars. Two details are dropped: a zinc-plated bar's premium over a
#: plain one (about a quarter in the listings), and a rectangular bar's lower
#: price than the square bar of its width.
PRICE = PriceModel(
    2.3,
    0.25,
    1.6,
    0.2,
    0.08,
    measured=False,
    pack_attribute="Length",
    pack_slope=0.93,
    pack_ref=12.0,
    option_attribute="Material",
    option_factors={"18-8 Stainless Steel": STAINLESS_FACTOR},
)

SPEC = TypeSpec(
    KEY,
    category=("Raw Materials", "Bar & Rod Stock", "Key Stock Bars"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=build,
    share=0.016,
    price=PRICE,
    may_claim=frozenset(),
    key_attributes=("Width",),
    unit_primary="Width",
    use_lines=(
        "Cut to length to make a machine key for a shaft and hub keyway.",
        "An oversized bar is fitted to the keyway; an undersized bar slips in.",
    ),
)
