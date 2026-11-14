"""Coupling nuts, deepened from a breadth row into a modelled type (#829).

The breadth row offered five threads, two materials, two finishes and two
lengths. A distributor's coupling nut space is a long hex nut's size table,
inch and metric, and each table here is one a reviewer can open:

* DIN 6334 hexagon nuts, 3d long, coarse thread, M6 to M20: the pitch, the
  width across flats (``s``) and the length (``m``) are FreeCAD_FastenersWB's
  ``FsData/din6334def.csv`` (``DIN6334def``) at commit ``fddd07af``, the
  commit ``core/standards_library/tables/fastener_standards.json`` and the
  earlier #829 types (the dowel pins, roll pins, lag screws, carriage bolts
  and flange nuts) pin.
* ASME B18.2.2 hex coupling nuts, #6 to 1": the threads per inch, the width
  across flats (``F``) and the length (``H``) are the same commit's
  ``FsData/asmeb18.2.2.13def.csv`` (``ASMEB18.2.2.13def``, which FastenersWB
  titles "UNC Hex coupling nuts").

The thread is read from the library's ASME B1.1 (UNC) and ISO 262 (metric
coarse) tables, as the threaded rod, the stud, the carriage bolt and the
flange nut read it (#73); each nut table's own pitch agrees with it on every
row (the type's gate file checks). Each table gives one length per thread, so
the length is a table column, not a free axis: the survey's "2 lengths" is
not built.

Left out on purpose: the inch table's rows above 1" (the library's ASME B1.1
table, which the thread is read from, stops at 1"); DIN 6334's countersink
diameter ``d_a`` (the census has no name for it); the fine-thread, reducing
and round kinds (no table was read). A line is one nut per SKU: the census has
no coupling nuts, so no pack quantity is published (#14).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, NamedTuple

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn, hex_nut
from synthetic_ecommerce_data.domains.industrial.newtypes import MM_PER_INCH, table_provenance
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "coupling_nuts"
ITEM = "Coupling Nut"
THREAD = "Thread Size"
FLATS = "Width Across Flats"
LENGTH = "Length"
#: The nut dimensions each SKU publishes, in its table's order.
NUT_DIMS = (FLATS, LENGTH)

ASME = "ASME B18.2.2"
DIN_6334 = "DIN 6334"
INCH_THREADS = "ASME B1.1"
METRIC_THREADS = "ISO 262"


class MetricRow(NamedTuple):
    """One DIN 6334 diameter: d and its pitch, and s and m, mm."""

    d: int
    p: float
    s: float
    m: float


#: FastenersWB ``din6334def.csv`` (``DIN6334def``), mm: ``s`` and ``m``.
DIN_6334_ROWS = (
    MetricRow(6, 1.0, 10.0, 18.0),
    MetricRow(8, 1.25, 13.0, 24.0),
    MetricRow(10, 1.5, 17.0, 30.0),
    MetricRow(12, 1.75, 19.0, 36.0),
    MetricRow(16, 2.0, 24.0, 48.0),
    MetricRow(20, 2.5, 30.0, 54.0),
)


class InchRow(NamedTuple):
    """One ASME B18.2.2 hex coupling nut size: its nominal diameter, its
    threads per inch, and F and H, inches."""

    size: str
    tpi: int
    f: float
    h: float


#: FastenersWB ``asmeb18.2.2.13def.csv`` (``ASMEB18.2.2.13def``), #6 to 1".
ASME_ROWS = (
    InchRow("#6", 32, 0.3125, 0.5),
    InchRow("#8", 32, 0.3125, 0.625),
    InchRow("#10", 24, 0.3125, 0.75),
    InchRow("1/4", 20, 0.4375, 1.75),
    InchRow("5/16", 18, 0.5, 1.75),
    InchRow("3/8", 16, 0.5625, 1.75),
    InchRow("7/16", 14, 0.625, 1.75),
    InchRow("1/2", 13, 0.6875, 1.75),
    InchRow("9/16", 12, 0.8125, 2.125),
    InchRow("5/8", 11, 0.8125, 2.125),
    InchRow("3/4", 10, 1.0, 2.25),
    InchRow("7/8", 9, 1.25, 2.5),
    InchRow("1", 8, 1.375, 2.75),
)

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
    ("Steel", "Zinc Plated", "Grade 5"),
    ("18-8 Stainless Steel", "Plain", None),
    ("Steel", "Zinc Plated", "Grade 8"),
    ("Steel", "Plain", "Grade 5"),
    ("316 Stainless Steel", "Plain", None),
)
METRIC_COMBOS: tuple[Combo, ...] = (
    ("Steel", "Zinc Plated", "Class 8"),
    ("18-8 Stainless Steel", "Plain", None),
    ("Steel", "Zinc Plated", "Class 10"),
    ("Steel", "Plain", "Class 8"),
    ("316 Stainless Steel", "Plain", None),
)

#: The table a line is drawn from, in rotation: two inch, one metric.
SERIES = (ASME, DIN_6334, ASME)


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Material", "line"),
    _spec("Finish", "line", 0.85),
    _spec("Grade", "line", 0.9),
    _spec("Thread Type", "line", 0.8),
    _spec(THREAD, "sku"),
    _spec(FLATS, "sku", kind="length"),
    _spec(LENGTH, "sku", kind="length"),
)


def provenance(standard: str) -> str:
    """Where each dimension came from: the nut table and the thread table."""
    threads = INCH_THREADS if standard == ASME else METRIC_THREADS
    return table_provenance(*((name, standard) for name in NUT_DIMS), (THREAD, threads))


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    standard = SERIES[gen._rotate(f"series:{type_key}", len(SERIES))]
    combos = INCH_COMBOS if standard == ASME else METRIC_COMBOS
    material, finish, grade = combos[gen._rotate(f"combo:{type_key}:{standard}", len(combos))]
    sizes: list[tuple[str, tuple[float, ...]]]
    if standard == ASME:
        sizes = [(inch_thread(row), (row.f, row.h)) for row in ASME_ROWS]
    else:
        sizes = [
            (metric_thread(row), tuple(mm / MM_PER_INCH for mm in (row.s, row.m)))
            for row in DIN_6334_ROWS
        ]
    brand = brands.pick_brand(rng, type_key, gen._exhausted)

    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"CN{rng.randint(100, 999)}",
        category=category,
        provenance=provenance(standard),
        standard=standard,
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", ITEM)),  # keeps the stream stable for #497
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute("Thread Type", "UNC" if standard == ASME else "Metric Coarse"),
    ]
    if grade is not None:
        draft.line_attrs.append(keyword_attribute("Grade", grade))
    draft.descriptors = [("Material", material)]

    system = "in" if standard == ASME else "mm"
    run = gen._table_run(f"sizes:{type_key}:{standard}:{material}", sizes, gen._variant_count())
    for thread, dims in run:
        style_len = gen._style(system)
        child = ChildDraft(system=system)
        child.primary = keyword_attribute(THREAD, thread)
        child.attrs = [
            child.primary,
            *(gen._length(name, v, style_len) for name, v in zip(NUT_DIMS, dims, strict=True)),
        ]
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------


def figure(record: Mapping[str, str]) -> Drawn:
    """The hex nut's face over its side view (``hex_nut``), the side view as
    long as the coupling nut: hex_nut reads the length as its height."""
    view = dict(record)
    if LENGTH in record:
        view["Height"] = record[LENGTH]
    return hex_nut(view)


#: The drawing's extent (docs/adding-a-type.md "Figure and extent"), measured
#: over every row the tables admit, so any build fits it: the largest drawn is
#: 1.59 x 4.81 in, a 1" nut's corners over its face and its 2.75 in length.
EXTENT = (1.7, 4.95)


# --- price ------------------------------------------------------------------------

#: GENERATED, NOT MEASURED: the price census has no coupling nuts (neither
#: ``deep_types`` nor ``breadth_categories`` of P2_price_census.json). Hand-set
#: from the breadth row's level (0.50 to 4.00 USD): the anchor is a
#: standard-tier 3/8" steel coupling nut, each.
PRICE = PriceModel(0.85, 0.375, 1.5, 0.2, 0.08, measured=False)


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """The line's nut table: ASME B18.2.2 or DIN 6334."""
    return (standard,)


SPEC = TypeSpec(
    KEY,
    category=("Fasteners", "Nuts", "Coupling Nuts"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.012,
    price=PRICE,
    claims=claims,
    may_claim=frozenset({ASME, DIN_6334}),
    key_attributes=(THREAD,),
    unit_primary=THREAD,
    compat=False,
    use_lines=(
        "It joins two lengths of threaded rod end to end, or extends a stud that is too short.",
        "Its long hex body takes a wrench across the joint once both rods are turned in.",
    ),
)
