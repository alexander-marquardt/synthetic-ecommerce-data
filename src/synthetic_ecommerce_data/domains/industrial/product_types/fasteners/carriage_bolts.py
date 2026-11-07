"""Carriage bolts, deepened from a breadth row into a modelled type (#829).

The breadth row offered four inch threads, two materials and three lengths. A
distributor's carriage bolt space is a round head square neck bolt's size
table, inch and metric, and each table here is one a reviewer can open:

* DIN 603 mushroom head square neck bolts, M5 to M20: the pitch, the head
  diameter (``dk``), the head height (``k``), the square neck's length along
  the bolt (``f``), the nominal lengths and each diameter's range of lengths
  are FreeCAD_FastenersWB's ``FsData/din603def.csv`` (``DIN603def``,
  ``DIN603length`` and ``DIN603range``) at commit ``fddd07af``, the commit
  ``core/standards_library/tables/fastener_standards.json``, the dowel pins,
  the roll pins and the lag screws pin. The file gives each dimension's
  maximum and minimum; a value here is their midpoint, the nominal.
* ASME B18.5 round head square neck bolts, #10 to 1": the threads per inch,
  the head diameter (``A``), the head height (``H``), the square neck's length
  (``P``) and each diameter's range of lengths are the same commit's
  ``FsData/asmeb18.5.2def.csv`` (``ASMEB18.5.2def`` and ``ASMEB18.5.2range``),
  which writes each dimension as the midpoint of the standard's maximum and
  minimum. The table lists no nominal lengths, so an inch bolt's length is a
  stocked length from :data:`INCH_LENGTHS` inside its row's range.

The thread is read from the library's ASME B1.1 (UNC) and ISO 262 (metric
coarse) tables, as the threaded rod and the stud read it (#73); each head
table's own pitch agrees with it on every row (the type's gate file checks).

Left out on purpose: the square neck's width (the census has no name for it);
the thread length (DIN 603 publishes one per length band and ASME B18.5 a
rule, neither read here); the fine-thread and the ribbed or short-neck kinds
(no table was read). A line is sold in a pack (:data:`PACK_COUNTS`), as 97% of
the census's carriage bolts are.
"""

from __future__ import annotations

import contextlib
import math
from collections.abc import Mapping
from fractions import Fraction
from typing import Any, NamedTuple

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.dimensions import (
    DimensionParseError,
    parse_length,
    parse_thread,
)
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.price import PACK_SLOPES, PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing import primitives as P  # noqa: N812
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import MM_PER_INCH, table_provenance
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "carriage_bolts"
ITEM = "Carriage Bolt"
THREAD = "Thread Size"
HEAD_DIA = "Head Diameter"
HEAD = "Head Height"
NECK = "Neck Length"
#: The head and neck dimensions each SKU publishes, in its table's order.
HEAD_DIMS = (HEAD_DIA, HEAD, NECK)

ASME = "ASME B18.5"
DIN_603 = "DIN 603"
INCH_THREADS = "ASME B1.1"
METRIC_THREADS = "ISO 262"


class MetricRow(NamedTuple):
    """One DIN 603 diameter: d and its pitch, dk, k and f, mm, and its shortest
    and longest l, mm."""

    d: int
    p: float
    dk: float
    k: float
    f: float
    min_l: int
    max_l: int


#: FastenersWB ``din603def.csv`` (``DIN603def`` and ``DIN603range``), mm: dk,
#: k and f the midpoints of the file's max and min.
DIN_603_ROWS = (
    MetricRow(5, 0.8, 13.0, 3.0, 3.5, 16, 80),
    MetricRow(6, 1.0, 16.0, 3.5, 4.0, 16, 150),
    MetricRow(8, 1.25, 20.0, 4.5, 5.0, 20, 150),
    MetricRow(10, 1.5, 24.0, 5.0, 6.0, 20, 200),
    MetricRow(12, 1.75, 30.0, 6.5, 8.0, 30, 200),
    MetricRow(16, 2.0, 38.0, 8.5, 12.0, 55, 200),
    MetricRow(20, 2.5, 46.0, 10.5, 15.0, 70, 200),
)
#: The ``DIN603length`` nominal lengths, mm.
DIN_603_LENGTHS = (
    16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 80, 90, 100, 110, 120, 130, 140,
    150, 160, 180, 200,
)  # fmt: skip


class InchRow(NamedTuple):
    """One ASME B18.5 round head square neck size: its nominal diameter, its
    threads per inch, A, H and P, inches, and its shortest and longest length."""

    size: str
    tpi: int
    a: float
    h: float
    p: float
    min_l: float
    max_l: float


def _row(size: str, tpi: int, a: float, h: float, p: float, min_l: str, max_l: str) -> InchRow:
    return InchRow(size, tpi, a, h, p, float(Fraction(min_l)), float(Fraction(max_l)))


#: FastenersWB ``asmeb18.5.2def.csv`` (``ASMEB18.5.2def`` and ``ASMEB18.5.2range``).
ASME_ROWS = (
    _row("#10", 24, 0.4525, 0.104, 0.1095, "3/16", "8"),
    _row("1/4", 20, 0.5785, 0.135, 0.1405, "3/8", "12"),
    _row("5/16", 18, 0.7035, 0.166, 0.1715, "1/2", "12"),
    _row("3/8", 16, 0.813, 0.198, 0.2035, "1/2", "12"),
    _row("7/16", 14, 0.938, 0.229, 0.2345, "3/4", "12"),
    _row("1/2", 13, 1.063, 0.26, 0.2655, "3/4", "12"),
    _row("5/8", 11, 1.2815, 0.3285, 0.3285, "3/4", "14"),
    _row("3/4", 10, 1.5315, 0.3905, 0.3905, "1", "14"),
    _row("7/8", 9, 1.7815, 0.4485, 0.4535, "3/2", "14"),
    _row("1", 8, 2.0315, 0.5155, 0.5155, "3/2", "14"),
)
#: The lengths an inch carriage bolt is stocked in: 1/2" to 2" by 1/4", to 6"
#: by 1/2", then 7" to 10" by 1", 12" and 14".
INCH_LENGTHS = tuple(
    Fraction(v)
    for v in (
        "1/2", "3/4", "1", "5/4", "3/2", "7/4", "2", "5/2", "3", "7/2", "4", "9/2", "5",
        "11/2", "6", "7", "8", "9", "10", "12", "14",
    )
)  # fmt: skip

_UNIFIED = {row["size"]: row for row in library.table("asme_b1_1_unified_threads").rows}
_ISO = {row["size"]: row for row in library.table("iso_262_metric_threads").rows}


def inch_thread(row: InchRow) -> str:
    """The row's UNC designation, from ASME B1.1."""
    return f"{row.size}-{_UNIFIED[row.size]['unc_tpi']}"


def metric_thread(row: MetricRow) -> str:
    """The row's metric coarse designation, from ISO 262."""
    return f"M{row.d}x{_ISO[f'M{row.d}']['coarse_pitch_mm']:g}"


#: (Material, Finish, Grade or None): the combinations each table is stocked in.
Combo = tuple[str, str, "str | None"]
INCH_COMBOS: tuple[Combo, ...] = (
    ("Steel", "Zinc Plated", "Grade 2"),
    ("Steel", "Hot Dip Galvanized", "Grade 2"),
    ("Steel", "Zinc Plated", "Grade 5"),
    ("18-8 Stainless Steel", "Plain", None),
    ("Steel", "Plain", "Grade 2"),
    ("316 Stainless Steel", "Plain", None),
)
METRIC_COMBOS: tuple[Combo, ...] = (
    ("Steel", "Zinc Plated", "Class 4.6"),
    ("Steel", "Hot Dip Galvanized", "Class 4.6"),
    ("Steel", "Zinc Plated", "Class 8.8"),
    ("18-8 Stainless Steel", "Plain", None),
    ("316 Stainless Steel", "Plain", None),
)

#: The table a line is drawn from, in rotation: two inch, one metric.
SERIES = (ASME, DIN_603, ASME)

#: Every diameter the type offers, inches: a line's pack is ranked among them,
#: so the pack falls as the bolt grows (:func:`.price.pack_quantity`).
DIAMETERS_IN = (
    *(parse_thread(inch_thread(row)).major.inches for row in ASME_ROWS),
    *(row.d / MM_PER_INCH for row in DIN_603_ROWS),
)


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Head Type", "line"),
    _spec("Material", "line"),
    _spec("Finish", "line", 0.85),
    _spec("Grade", "line", 0.9),
    _spec("Thread Type", "line", 0.8),
    # Unconditional: the census price is a pack's, so every record states the
    # pack it prices, as a hex bolt does (#65).
    _spec("Units per Pack", "line", kind="count"),
    _spec(THREAD, "sku"),
    _spec("Length", "sku", kind="length"),
    _spec(HEAD_DIA, "sku", kind="length"),
    _spec(HEAD, "sku", kind="length"),
    _spec(NECK, "sku", kind="length"),
)


def metric_lengths(row: MetricRow) -> tuple[int, ...]:
    """The nominal lengths ``row``'s range admits, mm."""
    return tuple(length for length in DIN_603_LENGTHS if row.min_l <= length <= row.max_l)


def inch_lengths(row: InchRow) -> tuple[Fraction, ...]:
    """The stocked lengths inside ``row``'s range."""
    return tuple(v for v in INCH_LENGTHS if row.min_l <= v <= row.max_l)


def provenance(standard: str) -> str:
    """Where each dimension came from: the head table, the thread table, and
    for an inch bolt a stocked length inside the head table's range."""
    if standard == ASME:
        table = table_provenance(
            (HEAD_DIA, ASME), (HEAD, ASME), (NECK, ASME), (THREAD, INCH_THREADS)
        )
        return f"{table}; Length is a stocked length inside the {ASME} table's range"
    return table_provenance(
        (HEAD_DIA, DIN_603), (HEAD, DIN_603), (NECK, DIN_603), ("Length", DIN_603),
        (THREAD, METRIC_THREADS),
    )  # fmt: skip


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    standard = SERIES[gen._rotate(f"series:{type_key}", len(SERIES))]
    if standard == ASME:
        row = ASME_ROWS[gen._rotate(f"size:{type_key}:{standard}", len(ASME_ROWS))]
        size_key, thread, combos = row.size, inch_thread(row), INCH_COMBOS
        head_in = (row.a, row.h, row.p)
        lengths_in = [float(v) for v in inch_lengths(row)]
    else:
        metric_row = DIN_603_ROWS[gen._rotate(f"size:{type_key}:{standard}", len(DIN_603_ROWS))]
        size_key, thread, combos = f"M{metric_row.d}", metric_thread(metric_row), METRIC_COMBOS
        head_in = tuple(mm / MM_PER_INCH for mm in (metric_row.dk, metric_row.k, metric_row.f))
        lengths_in = [mm / MM_PER_INCH for mm in metric_lengths(metric_row)]
    combo = f"combo:{type_key}:{standard}:{size_key}"
    material, finish, grade = combos[gen._rotate(combo, len(combos))]
    brand = brands.pick_brand(rng, type_key, gen._exhausted)

    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"CB{rng.randint(100, 999)}",
        category=category,
        provenance=provenance(standard),
        standard=standard,
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", ITEM)),  # keeps the stream stable for #497
        keyword_attribute("Head Type", "Round"),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute("Thread Type", "UNC" if standard == ASME else "Metric Coarse"),
        gen._pack(
            type_key,
            f"{standard}:{size_key}:{brand}:{draft.series}",
            parse_thread(thread).major.inches,
            DIAMETERS_IN,
        ),
    ]
    if grade is not None:
        draft.line_attrs.append(keyword_attribute("Grade", grade))
    draft.descriptors = [("Material", material)]

    count = min(gen._variant_count(), len(lengths_in))
    offered = gen._offered_run(f"lengths:{standard}:{size_key}", lengths_in, count)
    system = "in" if standard == ASME else "mm"
    for length_in in offered:
        style = gen._style(system)
        child = ChildDraft(system=system)
        child.primary = keyword_attribute(THREAD, thread)
        length_attr = gen._length("Length", length_in, style)
        child.attrs = [
            child.primary,
            length_attr,
            *(gen._length(name, v, style) for name, v in zip(HEAD_DIMS, head_in, strict=True)),
        ]
        child.secondary = {"other_length": length_attr}
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

#: A shank longer than KNEE inches is drawn compressed into at most KNEE + TAIL,
#: so a 14" bolt does not dwarf every short one.
KNEE = 3.0
TAIL = 0.6
#: The share of the shank the thread runs up from the end, as drawn (no thread
#: length is published).
THREAD_SHARE = 0.6
#: The drawing's extent (docs/adding-a-type.md "Figure and extent"), measured
#: over every row and length the tables admit, so any build fits it: the
#: largest drawn is 4.213 x 4.115 in, a 1" bolt's head and its end view beside
#: it, and a 14" bolt compressed down the page.
EXTENT = (4.25, 4.15)


def _value(record: Mapping[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """A side view, a domed head over a square neck, a plain shank and a thread
    to a chamfered end, and an end view of the head and its neck beside it."""
    thread = None
    with contextlib.suppress(KeyError, DimensionParseError):
        thread = parse_thread(record[THREAD])
    length = _value(record, "Length")
    d = thread.major.inches if thread else 0.375
    r = d / 2
    head_d = _value(record, HEAD_DIA) or 2.2 * d
    head = _value(record, HEAD) or 0.55 * d
    neck = _value(record, NECK) or 0.55 * d
    full = length or 8 * d
    shank = full if full <= KNEE else KNEE + TAIL * (1 - math.exp(-(full - KNEE)))
    fig = Figure(size_in=head + shank)
    P.head_button(fig, head_d, head)
    tip = head + shank
    neck_end = head + min(neck, shank / 3)
    fig.rect(-r, head, r, neck_end)
    thread_top = max(neck_end, head + shank * (1 - THREAD_SHARE))
    pitch = max(thread.pitch_in if thread else d / 8, (tip - thread_top) / 24)
    P.shank(fig, r, neck_end, thread_top)
    P.thread(fig, r, thread_top, tip, pitch, chamfer_length=min(pitch, r / 2))
    centre = (head_d + 0.15, head_d / 2)
    P.round_face(fig, centre, head_d / 2)
    cx, cy = centre
    fig.rect(cx - r, cy - r, cx + r, cy + r, "line")
    source = "record" if thread and length else ("partial" if thread else "nominal")
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: The census's carriage-bolt endings
#: (``breadth_categories.carriage_bolts.endings``).
ENDINGS = {
    "other": 0.4545,
    "other .x5": 0.2818,
    ".00": 0.0727,
    "other .x9": 0.0727,
    ".50": 0.0455,
    ".95": 0.0455,
    ".49": 0.0182,
    ".99": 0.0091,
}

#: Fitted by hand to the census's 110 carriage-bolt prices (p10 10.841, p50
#: 26.1, p90 67.205 USD; ``price.DEEPENED_CENSUS``): the anchor, the slope and
#: the noise, scored by the p50 and p90/p10 rows at both sizes (default
#: 22.67 USD and 6.84, --lines 39000 29.00 USD and 5.95). The census's own
#: slope on the thread (2.202) is from two cells and 55 SKUs, and at it the
#: p90/p10 row lands at 11.8 against a band of 4.6 to 8.2, so the slope is
#: fitted with the noise (1.0). The pack slope is the census's
#: (``pooled_loglog_slope_price_on_pack_qty``, ``price.PACK_SLOPES``). The
#: census measures no price on length for carriage bolts, so a bolt's length
#: does not move its price.
PRICE = PriceModel(
    # @fit-begin
    28.0, 0.375, 1.0, 0.4, 0.1,
    # @fit-end
    endings=ENDINGS,
    pack_attribute="Units per Pack",
    pack_slope=PACK_SLOPES[KEY],
    pack_ref=100.0,
)  # fmt: skip


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """The line's head table: ASME B18.5 or DIN 603."""
    return (standard,)


SPEC = TypeSpec(
    KEY,
    category=("Fasteners", "Bolts", "Carriage Bolts"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.012,
    price=PRICE,
    claims=claims,
    may_claim=frozenset({ASME, DIN_603}),
    key_attributes=(THREAD,),
    unit_primary=THREAD,
    compat=False,
    use_lines=(
        "Its square neck grips a round hole in timber, so the nut turns down alone.",
        "Fastens a post, beam or gate hinge through wood, its domed head outside.",
    ),
)
