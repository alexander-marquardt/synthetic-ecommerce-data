"""Lag screws, deepened from a breadth row into a modelled type (#829).

The breadth row offered four inch diameters, one material and three lengths.
A distributor's lag screw space is a hex head wood screw's size table, inch
and metric, and each table here is one a reviewer can open:

* DIN 571 hex head wood screws: the diameters, the width across flats, the
  head height, the nominal lengths and each diameter's range of lengths are
  FreeCAD_FastenersWB's ``FsData/din571def.csv`` (``DIN571def``,
  ``DIN571length`` and ``DIN571range``) at commit ``fddd07af``, the commit
  ``core/standards_library/tables/fastener_standards.json``, the dowel pins
  and the roll pins pin.
* ASME B18.2.1 hex lag screws, 1/4" to 1": the diameter, threads per inch,
  basic width across flats and basic head height of the standard's hex lag
  screw table (1996 edition), as AFT Fasteners' "Lag Screws: Dimensions and
  Specifications" publishes it for 1/4" to 7/8" and Portland Bolt's "Hex Lag
  Dimensions" for 1/2" to 1" (the two agree where they overlap). The table
  publishes no range of lengths per diameter, so an inch screw's length is a
  stocked length from :data:`INCH_LENGTHS`, between :data:`MIN_OVER_DIAMETER`
  and :data:`MAX_OVER_DIAMETER` diameters, and no length claims the table.

Left out on purpose: the #10 lag screw (a light-duty size few distributors
stock); a lag's thread length (neither table above publishes one per row);
DIN 571's thread pitch (the census has no thread-pitch name a screw shares
with a chain's pitch, #497); the hex washer head lag (no table was read). No
pack quantity is published (#14): a line is one screw per SKU.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from fractions import Fraction
from typing import Any, NamedTuple

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing import primitives as P  # noqa: N812
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import MM_PER_INCH, table_provenance
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "lag_screws"
ITEM = "Lag Screw"
DIA = "Diameter"
FLATS = "Width Across Flats"
HEAD = "Head Height"
TPI = "Threads per Inch"

ASME = "ASME B18.2.1"
DIN_571 = "DIN 571"


class MetricRow(NamedTuple):
    """One DIN 571 diameter: d, s and k, mm, and its shortest and longest l, mm."""

    d: float
    s: float
    k: float
    min_l: int
    max_l: int


#: FastenersWB ``din571def.csv`` (``DIN571def`` and ``DIN571range``), mm.
DIN_571_ROWS = (
    MetricRow(4, 7, 2.8, 16, 40), MetricRow(5, 8, 3.5, 16, 40), MetricRow(6, 10, 4, 20, 60),
    MetricRow(8, 13, 5.5, 25, 100), MetricRow(10, 17, 7, 30, 100), MetricRow(12, 19, 8, 35, 120),
    MetricRow(16, 24, 10, 50, 160), MetricRow(20, 30, 13, 60, 200),
)  # fmt: skip
#: The ``DIN571length`` nominal lengths, mm.
DIN_571_LENGTHS = (
    16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100, 110, 120, 130, 140,
    150, 160, 170, 180, 190, 200,
)  # fmt: skip


class InchRow(NamedTuple):
    """One ASME B18.2.1 hex lag size: its nominal diameter, its threads per
    inch as the table writes them, and its basic flats and head height, inches."""

    size: str
    tpi: str
    flats: Fraction
    head: Fraction


def _row(size: str, tpi: str, flats: str, head: str) -> InchRow:
    return InchRow(size, tpi, Fraction(flats), Fraction(head))


#: The ASME B18.2.1 hex lag screw table, 1/4" to 1".
ASME_ROWS = (
    _row("1/4", "10", "7/16", "11/64"),
    _row("5/16", "9", "1/2", "7/32"),
    _row("3/8", "7", "9/16", "1/4"),
    _row("7/16", "7", "5/8", "19/64"),
    _row("1/2", "6", "3/4", "11/32"),
    _row("5/8", "5", "15/16", "27/64"),
    _row("3/4", "4.5", "9/8", "1/2"),
    _row("7/8", "4", "21/16", "37/64"),
    _row("1", "3.5", "3/2", "43/64"),
)
#: The lengths an inch lag screw is stocked in: 1" to 2" by 1/4" but 1-3/4",
#: to 6" by 1/2", then 7" to 10" by 1" and 12".
INCH_LENGTHS = tuple(
    Fraction(v)
    for v in (
        "1", "5/4", "3/2", "2", "5/2", "3", "7/2", "4", "9/2", "5", "11/2", "6",
        "7", "8", "9", "10", "12",
    )
)  # fmt: skip
#: An inch screw is stocked from four to twenty-four diameters long.
MIN_OVER_DIAMETER = 4
MAX_OVER_DIAMETER = 24

#: (Material, Finish): the combinations a lag screw is stocked in. A
#: stainless screw is plain; a steel one plain, zinc plated or hot dip
#: galvanized for outdoor timber.
COMBOS = (
    ("Steel", "Zinc Plated"),
    ("Steel", "Hot Dip Galvanized"),
    ("18-8 Stainless Steel", "Plain"),
    ("Steel", "Plain"),
    ("316 Stainless Steel", "Plain"),
)

#: The table a line is drawn from, in rotation: two inch, one metric.
SERIES = (ASME, DIN_571, ASME)


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Head Type", "line"),
    _spec("Drive Type", "line", 0.85),
    _spec("Material", "line"),
    _spec("Finish", "line", 0.85),
    _spec(DIA, "sku", kind="length"),
    _spec("Length", "sku", kind="length"),
    _spec(FLATS, "sku", kind="length"),
    _spec(HEAD, "sku", kind="length"),
    _spec(TPI, "sku"),
)


def metric_lengths(row: MetricRow) -> tuple[int, ...]:
    """The nominal lengths ``row``'s range admits, mm."""
    return tuple(length for length in DIN_571_LENGTHS if row.min_l <= length <= row.max_l)


def inch_lengths(row: InchRow) -> tuple[Fraction, ...]:
    """The stocked lengths of :data:`MIN_OVER_DIAMETER` to :data:`MAX_OVER_DIAMETER` diameters."""
    d = Fraction(row.size)
    return tuple(v for v in INCH_LENGTHS if MIN_OVER_DIAMETER * d <= v <= MAX_OVER_DIAMETER * d)


def provenance(standard: str) -> str:
    """A metric line's dimensions and length are DIN 571's; an inch line's length is stocked."""
    if standard == ASME:
        table = table_provenance((DIA, ASME), (TPI, ASME), (FLATS, ASME), (HEAD, ASME))
        return f"{table}; Length is a stocked length"
    return table_provenance((DIA, DIN_571), (FLATS, DIN_571), (HEAD, DIN_571), ("Length", DIN_571))


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import Attribute, keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    standard = SERIES[gen._rotate(f"series:{type_key}", len(SERIES))]
    tpi = None
    if standard == ASME:
        row = ASME_ROWS[gen._rotate(f"size:{type_key}:{standard}", len(ASME_ROWS))]
        size_key = row.size
        diameter_in = float(Fraction(row.size))
        flats_in, head_in, tpi = float(row.flats), float(row.head), row.tpi
        lengths_in = [float(v) for v in inch_lengths(row)]
    else:
        metric_row = DIN_571_ROWS[gen._rotate(f"size:{type_key}:{standard}", len(DIN_571_ROWS))]
        size_key = f"{metric_row.d:g}"
        diameter_in = metric_row.d / MM_PER_INCH
        flats_in, head_in = metric_row.s / MM_PER_INCH, metric_row.k / MM_PER_INCH
        lengths_in = [mm / MM_PER_INCH for mm in metric_lengths(metric_row)]
    material, finish = COMBOS[gen._rotate(f"combo:{type_key}:{standard}:{size_key}", len(COMBOS))]
    brand = brands.pick_brand(rng, type_key, gen._exhausted)

    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"LS{rng.randint(100, 999)}",
        category=category,
        provenance=provenance(standard),
        standard=standard,
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", ITEM)),  # keeps the stream stable for #497
        keyword_attribute("Head Type", "Hex"),
        keyword_attribute("Drive Type", "External Hex"),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
    ]
    draft.descriptors = [("Material", material)]

    count = min(gen._variant_count(), len(lengths_in))
    offered = gen._offered_run(f"lengths:{standard}:{size_key}", lengths_in, count)
    system = "in" if standard == ASME else "mm"
    for length_in in offered:
        style = gen._style(system)
        child = ChildDraft(system=system)
        child.primary = gen._length(DIA, diameter_in, style)
        length_attr = gen._length("Length", length_in, style)
        child.attrs = [
            child.primary,
            length_attr,
            gen._length(FLATS, flats_in, style),
            gen._length(HEAD, head_in, style),
            *([Attribute(TPI, tpi, bare_unit="TPI")] if tpi else []),
        ]
        child.secondary = {"other_length": length_attr}
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

#: A shank longer than KNEE inches is drawn compressed into at most KNEE + TAIL,
#: so a 200 mm screw does not dwarf every short one.
KNEE = 3.0
TAIL = 0.6
#: The share of the shank the thread runs up from the point.
THREAD_SHARE = 0.6
#: The drawing's extent (docs/adding-a-type.md "Figure and extent"), measured
#: over every row and length the tables admit, so any build fits it: the
#: largest drawn is 4.132 x 4.272 in, a 1" screw's head across its corners
#: and its end view beside it, and a 200 mm screw compressed down the page.
EXTENT = (4.15, 4.3)


def _value(record: Mapping[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """A side view, hex head on a plain shank and a coarse wood thread to a
    gimlet point, and an end view of the hex head beside it."""
    diameter = _value(record, DIA)
    length = _value(record, "Length")
    d = diameter or 0.375
    r = d / 2
    flats = _value(record, FLATS) or 1.5 * d
    head = _value(record, HEAD) or 0.7 * d
    full = length or 8 * d
    shank = full if full <= KNEE else KNEE + TAIL * (1 - math.exp(-(full - KNEE)))
    fig = Figure(size_in=head + shank)
    P.head_hex(fig, flats, head)
    point = min(1.2 * d, shank / 3)
    thread_top = head + shank * (1 - THREAD_SHARE)
    tip = head + shank
    fig.poly([
        (-r, head), (r, head), (r, tip - point), (0.0, tip), (-r, tip - point),
    ])  # fmt: skip
    pitch = max(d / 2.5, (tip - thread_top) / 24)
    fig.lines(P.thread_crests(r, thread_top, tip - point, pitch))
    corner = flats / math.sqrt(3)
    P.hex_face(fig, (flats + corner + 0.15, corner), corner)
    source = "record" if diameter and length else ("partial" if diameter else "nominal")
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: GENERATED, NOT MEASURED: the price census has no lag screws (neither
#: ``deep_types`` nor ``breadth_categories`` of P2_price_census.json). Hand-set
#: from the breadth row's level (0.30 to 3.00 USD for 1/4" to 1/2"): the anchor
#: is a standard-tier 3/8" steel lag screw 3" long, each. Its price scales with
#: its length below one for one (the pack slope), as the stud's does.
PRICE = PriceModel(
    0.6,
    0.375,
    1.6,
    0.2,
    0.08,
    measured=False,
    pack_attribute="Length",
    pack_slope=0.6,
    pack_ref=3.0,
)


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """The line's table: ASME B18.2.1 or DIN 571."""
    return (standard,)


SPEC = TypeSpec(
    KEY,
    category=("Fasteners", "Screws", "Lag Screws"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.012,
    price=PRICE,
    claims=claims,
    may_claim=frozenset({ASME, DIN_571}),
    key_attributes=(DIA,),
    unit_primary=DIA,
    compat=False,
    use_lines=(
        "Driven by its hex head with a wrench into a pilot hole in timber.",
        "Fastens a ledger, post bracket or heavy hardware to wood framing.",
    ),
)
