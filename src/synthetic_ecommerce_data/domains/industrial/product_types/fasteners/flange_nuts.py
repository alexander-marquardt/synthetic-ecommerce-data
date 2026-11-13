"""Flange nuts, deepened from a breadth row into a modelled type (#829).

The breadth row offered five threads, two materials and two finishes. A
distributor's flange nut space is a hex flange nut's size table, inch and
metric, in a serrated or a plain flange, and each table here is one a reviewer
can open:

* ISO 4161 hexagon nuts with flange, coarse thread, M5 to M20: the pitch, the
  width across flats (``s``), the flange diameter (``d_c``) and the height
  (``m``) are FreeCAD_FastenersWB's ``FsData/iso4161def.csv``
  (``ISO4161def``) at commit ``fddd07af``, the commit
  ``core/standards_library/tables/fastener_standards.json``, the dowel pins,
  the roll pins, the lag screws and the carriage bolts pin. ``s`` and ``m``
  are the file's maxima, the nominal sizes; ``d_c`` is the only flange
  diameter it gives, the maximum.
* ASME B18.2.2 hex flange nuts, #6 to 3/4": the threads per inch, the width
  across flats (``F``), the flange diameter (``B``) and the height (``H``)
  are the same commit's ``FsData/asmeb18.2.2.12def.csv``
  (``ASMEB18.2.2.12def``), which writes each dimension as the midpoint of the
  standard's maximum and minimum.

The thread is read from the library's ASME B1.1 (UNC) and ISO 262 (metric
coarse) tables, as the threaded rod, the stud and the carriage bolt read it
(#73); each nut table's own pitch agrees with it on every row (the type's gate
file checks). Both tables cover the serrated and the plain flange with one set
of dimensions, so the flange is a line attribute (``Style``, a census name;
the gate refuses ``Nut Style``, the type's own noun) and moves no dimension.

Left out on purpose: the flange's edge thickness and the bearing face
diameter (the census has no name for either); the fine-thread and the
prevailing-torque kinds (no table was read). A line is one nut per SKU: the
census has no flange nuts, so no pack quantity is published (#14).
"""

from __future__ import annotations

import contextlib
import math
from collections.abc import Mapping
from typing import Any, NamedTuple

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.dimensions import (
    DimensionParseError,
    parse_length,
    parse_thread,
)
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing import primitives as P  # noqa: N812
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import MM_PER_INCH, table_provenance
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "flange_nuts"
ITEM = "Flange Nut"
THREAD = "Thread Size"
FLATS = "Width Across Flats"
FLANGE = "Flange Dia."
HEIGHT = "Height"
#: The nut dimensions each SKU publishes, in its table's order.
NUT_DIMS = (FLATS, FLANGE, HEIGHT)

ASME = "ASME B18.2.2"
ISO_4161 = "ISO 4161"
INCH_THREADS = "ASME B1.1"
METRIC_THREADS = "ISO 262"


class MetricRow(NamedTuple):
    """One ISO 4161 diameter: d and its pitch, and s, d_c and m, mm."""

    d: int
    p: float
    s: float
    dc: float
    m: float


#: FastenersWB ``iso4161def.csv`` (``ISO4161def``), mm: ``s_max``, ``d_c_max``
#: and ``m_max``. The file's bracketed (M14), a second-choice size, is left out.
ISO_4161_ROWS = (
    MetricRow(5, 0.8, 8.0, 11.8, 5.0),
    MetricRow(6, 1.0, 10.0, 14.2, 6.0),
    MetricRow(8, 1.25, 13.0, 17.9, 8.0),
    MetricRow(10, 1.5, 15.0, 21.8, 10.0),
    MetricRow(12, 1.75, 18.0, 26.0, 12.0),
    MetricRow(16, 2.0, 24.0, 34.5, 16.0),
    MetricRow(20, 2.5, 30.0, 42.8, 20.0),
)


class InchRow(NamedTuple):
    """One ASME B18.2.2 hex flange nut size: its nominal diameter, its threads
    per inch, and F, B and H, inches."""

    size: str
    tpi: int
    f: float
    b: float
    h: float


#: FastenersWB ``asmeb18.2.2.12def.csv`` (``ASMEB18.2.2.12def``). Its #12 row
#: is left out: the library's ASME B1.1 table, which the thread is read from,
#: has no #12.
ASME_ROWS = (
    InchRow("#6", 32, 0.307, 0.414, 0.1635),
    InchRow("#8", 32, 0.339, 0.4605, 0.195),
    InchRow("#10", 24, 0.37, 0.49, 0.211),
    InchRow("1/4", 20, 0.433, 0.584, 0.229),
    InchRow("5/16", 18, 0.4945, 0.67, 0.2755),
    InchRow("3/8", 16, 0.5565, 0.739, 0.3385),
    InchRow("7/16", 14, 0.6815, 0.9235, 0.385),
    InchRow("1/2", 13, 0.743, 1.0155, 0.4475),
    InchRow("9/16", 12, 0.868, 1.1715, 0.4945),
    InchRow("5/8", 11, 0.93, 1.2645, 0.557),
    InchRow("3/4", 10, 1.1065, 1.48, 0.651),
)

_UNIFIED = {row["size"]: row for row in library.table("asme_b1_1_unified_threads").rows}
_ISO = {row["size"]: row for row in library.table("iso_262_metric_threads").rows}


def inch_thread(row: InchRow) -> str:
    """The row's UNC designation, from ASME B1.1."""
    return f"{row.size}-{_UNIFIED[row.size]['unc_tpi']}"


def metric_thread(row: MetricRow) -> str:
    """The row's metric coarse designation, from ISO 262."""
    return f"M{row.d}x{_ISO[f'M{row.d}']['coarse_pitch_mm']:g}"


#: The flange a line is stocked with, in rotation within each table.
STYLES = ("Serrated Flange", "Plain Flange")

#: (Material, Finish, Grade or None): the combinations each table is stocked in.
Combo = tuple[str, str, "str | None"]
INCH_COMBOS: tuple[Combo, ...] = (
    ("Steel", "Zinc Plated", "Grade 5"),
    ("Steel", "Zinc Plated", "Grade 8"),
    ("Steel", "Plain", "Grade 5"),
    ("18-8 Stainless Steel", "Plain", None),
    ("316 Stainless Steel", "Plain", None),
)
METRIC_COMBOS: tuple[Combo, ...] = (
    ("Steel", "Zinc Plated", "Class 8"),
    ("Steel", "Zinc Plated", "Class 10"),
    ("Steel", "Plain", "Class 8"),
    ("18-8 Stainless Steel", "Plain", None),
    ("316 Stainless Steel", "Plain", None),
)

#: The table a line is drawn from, in rotation: two inch, one metric.
SERIES = (ASME, ISO_4161, ASME)


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Style", "line"),
    _spec("Material", "line"),
    _spec("Finish", "line", 0.85),
    _spec("Grade", "line", 0.9),
    _spec("Thread Type", "line", 0.8),
    _spec(THREAD, "sku"),
    _spec(FLATS, "sku", kind="length"),
    _spec(FLANGE, "sku", kind="length"),
    _spec(HEIGHT, "sku", 0.9, kind="length"),
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
    style = STYLES[gen._rotate(f"style:{type_key}:{standard}", len(STYLES))]
    combos = INCH_COMBOS if standard == ASME else METRIC_COMBOS
    material, finish, grade = combos[
        gen._rotate(f"combo:{type_key}:{standard}:{style}", len(combos))
    ]
    sizes: list[tuple[str, tuple[float, ...]]]
    if standard == ASME:
        sizes = [(inch_thread(row), (row.f, row.b, row.h)) for row in ASME_ROWS]
    else:
        sizes = [
            (metric_thread(row), tuple(mm / MM_PER_INCH for mm in (row.s, row.dc, row.m)))
            for row in ISO_4161_ROWS
        ]
    brand = brands.pick_brand(rng, type_key, gen._exhausted)

    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"FN{rng.randint(100, 999)}",
        category=category,
        provenance=provenance(standard),
        standard=standard,
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", ITEM)),  # keeps the stream stable for #497
        keyword_attribute("Style", style),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute("Thread Type", "UNC" if standard == ASME else "Metric Coarse"),
    ]
    if grade is not None:
        draft.line_attrs.append(keyword_attribute("Grade", grade))
    draft.descriptors = [("Material", material)]

    system = "in" if standard == ASME else "mm"
    run = gen._table_run(f"sizes:{type_key}:{standard}:{style}", sizes, gen._variant_count())
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

#: The flange's edge, as drawn, a share of the nut's height (no table read
#: here publishes it).
FLANGE_SHARE = 0.25
#: The drawing's extent (docs/adding-a-type.md "Figure and extent"), measured
#: over every row the tables admit, so any build fits it: the largest drawn is
#: 1.685 x 2.978 in, an M20 nut's 42.8 mm flange face over its edge.
EXTENT = (1.7, 3.0)


def _value(record: Mapping[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """A face view, the hexagon across its flats over the round flange and the
    threaded hole, and an edge view below it, the flange under the hex body."""
    thread = None
    with contextlib.suppress(KeyError, DimensionParseError):
        thread = parse_thread(record[THREAD])
    d = thread.major.inches if thread else 0.375
    flats = _value(record, FLATS)
    flange = _value(record, FLANGE)
    height = _value(record, HEIGHT)
    read = flats is not None and flange is not None and height is not None
    flats = flats if flats and flats > d else 1.5 * d
    flange = flange if flange and flange > flats else 1.4 * flats
    height = height or d
    fig = Figure(size_in=flange)
    fig.disc((0.0, 0.0), flange / 2)
    P.hex_face(fig, (0.0, 0.0), flats / math.sqrt(3))
    fig.disc((0.0, 0.0), d / 2, "hole")
    edge = flange / 2 + 0.3 * flange
    collar = edge + height * (1 - FLANGE_SHARE)
    P.hex_body(fig, flats, edge, collar, "plain")
    fig.rect(-flange / 2, collar, flange / 2, edge + height)
    source = "record" if thread and read else ("partial" if thread else "nominal")
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: GENERATED, NOT MEASURED: the price census has no flange nuts (neither
#: ``deep_types`` nor ``breadth_categories`` of P2_price_census.json). Hand-set
#: from the breadth row's level (0.20 to 2.00 USD): the anchor is a
#: standard-tier 3/8" steel flange nut, each.
PRICE = PriceModel(0.45, 0.375, 1.5, 0.2, 0.08, measured=False)


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """The line's nut table: ASME B18.2.2 or ISO 4161."""
    return (standard,)


SPEC = TypeSpec(
    KEY,
    category=("Fasteners", "Nuts", "Flange Nuts"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.012,
    price=PRICE,
    claims=claims,
    may_claim=frozenset({ASME, ISO_4161}),
    key_attributes=(THREAD,),
    unit_primary=THREAD,
    compat=False,
    use_lines=(
        "Its flange spreads the load like a built-in washer, so no loose washer is needed.",
        "A serrated flange bites the surface beneath it and resists loosening under vibration.",
    ),
)
