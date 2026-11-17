"""Acorn cap nuts, deepened from a breadth row into a modelled type (#829).

The breadth row offered four threads, two materials and two finishes. A
distributor's acorn nut space is a cap nut's size table, inch and metric, and
each table here is one a reviewer can open:

* DIN 1587 hexagon domed cap nuts, M4 to M24: the pitch, the width across
  flats (``s``), the head diameter (``dk``, the dome) and the overall height
  (``h``) are FreeCAD_FastenersWB's ``FsData/din1587def.csv``
  (``DIN1587def``) at commit ``fddd07af``, the commit
  ``core/standards_library/tables/fastener_standards.json`` and the earlier
  #829 types pin. The file's bracketed second-choice sizes (M14, M18, M22)
  are left out.
* SAE J483 acorn nuts, #6 to 1", in the standard's two tables: the low crown
  (``FsData/saej483a1def.csv``, ``SAEJ483a1def``) and the high crown
  (``FsData/saej483a2def.csv``, ``SAEJ483a2def``) of the same commit. Their
  ``F`` is the width across flats, ``A`` the crown (head) diameter and ``H``
  the overall height, as FastenersWB's ``FsFunctions/FSmakeCupNut.py`` reads
  them. The #12 row and the rows above 1" are left out: the library's ASME
  B1.1 table, which the thread is read from, has no #12 and stops at 1".

The thread is read from the library's ASME B1.1 (UNC) and ISO 262 (metric
coarse) tables, as the flange nut reads it (#73); each nut table's own pitch
agrees with it on every row (the type's gate file checks). The crown is the
survey's "1.5 crowns" axis: an inch line is a low or a high crown (``Style``,
a census name; the gate refuses ``Nut Style``, the type's own noun), each its
own table; DIN 1587 has one crown and publishes no Style. ``Head Dia.`` is a
census name, and DIN 1587's own symbol for the dome, ``dk``, is a head
diameter's.

Left out on purpose: the hex height (``m``, ``Q``) and the thread depth
(``t``, ``U``), for which the census has no name a nut may publish (``Nut
Height`` carries the type's own noun); the self-locking and the two-piece
kinds (no table was read). A line is one nut per SKU: the census has no acorn
nuts, so no pack quantity is published (#14).
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

KEY = "cap_nuts_acorn"
ITEM = "Acorn Cap Nut"
THREAD = "Thread Size"
FLATS = "Width Across Flats"
HEAD = "Head Dia."
HEIGHT = "Overall Height"
#: The nut dimensions each SKU publishes, in its table's order.
NUT_DIMS = (FLATS, HEAD, HEIGHT)

SAE = "SAE J483"
DIN_1587 = "DIN 1587"
INCH_THREADS = "ASME B1.1"
METRIC_THREADS = "ISO 262"


class MetricRow(NamedTuple):
    """One DIN 1587 diameter: d and its pitch, and s, dk and h, mm."""

    d: int
    p: float
    s: float
    dk: float
    h: float


#: FastenersWB ``din1587def.csv`` (``DIN1587def``), mm: ``s``, ``dk`` and ``h``.
DIN_1587_ROWS = (
    MetricRow(4, 0.7, 7.0, 6.5, 8.0),
    MetricRow(5, 0.8, 8.0, 7.5, 10.0),
    MetricRow(6, 1.0, 10.0, 9.5, 12.0),
    MetricRow(8, 1.25, 13.0, 12.5, 15.0),
    MetricRow(10, 1.5, 16.0, 15.0, 18.0),
    MetricRow(12, 1.75, 18.0, 17.0, 22.0),
    MetricRow(16, 2.0, 24.0, 23.0, 28.0),
    MetricRow(20, 2.5, 30.0, 28.0, 34.0),
    MetricRow(24, 3.0, 36.0, 34.0, 42.0),
)


class InchRow(NamedTuple):
    """One SAE J483 acorn nut size: its nominal diameter, its threads per
    inch, and F, A and H, inches."""

    size: str
    tpi: int
    f: float
    a: float
    h: float


LOW = "Low Crown"
HIGH = "High Crown"

#: FastenersWB ``saej483a1def.csv`` (``SAEJ483a1def``, low crown) and
#: ``saej483a2def.csv`` (``SAEJ483a2def``, high crown). The two tables share
#: F and A; only H differs.
SAE_ROWS: dict[str, tuple[InchRow, ...]] = {
    LOW: (
        InchRow("#6", 32, 0.3125, 0.3, 0.34),
        InchRow("#8", 32, 0.3125, 0.3, 0.34),
        InchRow("#10", 24, 0.375, 0.36, 0.41),
        InchRow("1/4", 20, 0.4375, 0.41, 0.47),
        InchRow("5/16", 18, 0.5, 0.47, 0.53),
        InchRow("3/8", 16, 0.5625, 0.53, 0.62),
        InchRow("7/16", 14, 0.625, 0.59, 0.69),
        InchRow("1/2", 13, 0.75, 0.72, 0.81),
        InchRow("9/16", 12, 0.875, 0.84, 0.94),
        InchRow("5/8", 11, 0.9375, 0.91, 1.0),
        InchRow("3/4", 10, 1.0625, 1.03, 1.16),
        InchRow("7/8", 9, 1.25, 1.22, 1.36),
        InchRow("1", 8, 1.4375, 1.41, 1.55),
    ),
    HIGH: (
        InchRow("#6", 32, 0.3125, 0.3, 0.42),
        InchRow("#8", 32, 0.3125, 0.3, 0.42),
        InchRow("#10", 24, 0.375, 0.36, 0.52),
        InchRow("1/4", 20, 0.4375, 0.41, 0.59),
        InchRow("5/16", 18, 0.5, 0.47, 0.69),
        InchRow("3/8", 16, 0.5625, 0.53, 0.78),
        InchRow("7/16", 14, 0.625, 0.59, 0.88),
        InchRow("1/2", 13, 0.75, 0.72, 1.03),
        InchRow("9/16", 12, 0.875, 0.84, 1.19),
        InchRow("5/8", 11, 0.9375, 0.91, 1.28),
        InchRow("3/4", 10, 1.0625, 1.03, 1.45),
        InchRow("7/8", 9, 1.25, 1.22, 1.72),
        InchRow("1", 8, 1.4375, 1.41, 1.97),
    ),
}

_UNIFIED = {row["size"]: row for row in library.table("asme_b1_1_unified_threads").rows}
_ISO = {row["size"]: row for row in library.table("iso_262_metric_threads").rows}


def inch_thread(row: InchRow) -> str:
    """The row's UNC designation, from ASME B1.1."""
    return f"{row.size}-{_UNIFIED[row.size]['unc_tpi']}"


def metric_thread(row: MetricRow) -> str:
    """The row's metric coarse designation, from ISO 262."""
    return f"M{row.d}x{_ISO[f'M{row.d}']['coarse_pitch_mm']:g}"


#: (Material, Finish): the combinations an acorn nut is stocked in, either
#: table. The census has no grade for a cap nut, and no line claims one.
COMBOS: tuple[tuple[str, str], ...] = (
    ("Steel", "Chrome Plated"),
    ("Steel", "Zinc Plated"),
    ("18-8 Stainless Steel", "Plain"),
    ("316 Stainless Steel", "Plain"),
    ("Brass", "Plain"),
)

#: The table a line is drawn from, in rotation: two inch, one metric.
SERIES = (SAE, DIN_1587, SAE)
#: The inch crowns, in rotation within SAE J483.
CROWNS = (LOW, HIGH)


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Style", "line"),
    _spec("Material", "line"),
    _spec("Finish", "line", 0.85),
    _spec("Thread Type", "line", 0.8),
    _spec(THREAD, "sku"),
    _spec(FLATS, "sku", kind="length"),
    _spec(HEAD, "sku", 0.9, kind="length"),
    _spec(HEIGHT, "sku", kind="length"),
)


def provenance(standard: str) -> str:
    """Where each dimension came from: the nut table and the thread table."""
    threads = INCH_THREADS if standard == SAE else METRIC_THREADS
    return table_provenance(*((name, standard) for name in NUT_DIMS), (THREAD, threads))


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    standard = SERIES[gen._rotate(f"series:{type_key}", len(SERIES))]
    crown = CROWNS[gen._rotate(f"crown:{type_key}", len(CROWNS))] if standard == SAE else None
    material, finish = COMBOS[gen._rotate(f"combo:{type_key}:{standard}:{crown}", len(COMBOS))]
    sizes: list[tuple[str, tuple[float, ...]]]
    if crown is not None:
        sizes = [(inch_thread(row), (row.f, row.a, row.h)) for row in SAE_ROWS[crown]]
    else:
        sizes = [
            (metric_thread(row), tuple(mm / MM_PER_INCH for mm in (row.s, row.dk, row.h)))
            for row in DIN_1587_ROWS
        ]
    brand = brands.pick_brand(rng, type_key, gen._exhausted)

    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"AN{rng.randint(100, 999)}",
        category=category,
        provenance=provenance(standard),
        standard=standard,
    )
    draft.line_attrs = [retired(keyword_attribute("Item", ITEM))]  # keeps the stream stable
    if crown is not None:
        draft.line_attrs.append(keyword_attribute("Style", crown))
    draft.line_attrs += [
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute("Thread Type", "UNC" if standard == SAE else "Metric Coarse"),
    ]
    draft.descriptors = [("Material", material)]

    system = "in" if standard == SAE else "mm"
    run = gen._table_run(f"sizes:{type_key}:{standard}:{crown}", sizes, gen._variant_count())
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

#: The hex body's height, as drawn, a share of the overall height (the tables
#: read here publish it, but no SKU does).
HEX_SHARE = 0.45
#: The drawing's extent (docs/adding-a-type.md "Figure and extent"), measured
#: over every row the tables admit, so any build fits it: the largest drawn is
#: 1.660 x 4.061 in, a 1" high crown nut's hex face over its side view.
EXTENT = (1.7, 4.1)


def _value(record: Mapping[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """A top view, the hexagon across its flats around the round dome, and a
    side view below it, the dome over the hex body."""
    thread = None
    with contextlib.suppress(KeyError, DimensionParseError):
        thread = parse_thread(record[THREAD])
    d = thread.major.inches if thread else 0.375
    flats = _value(record, FLATS)
    head = _value(record, HEAD)
    height = _value(record, HEIGHT)
    read = flats is not None and head is not None and height is not None
    flats = flats if flats and flats > d else 1.5 * d
    head = head if head and head <= flats else 0.95 * flats
    height = height or 1.2 * flats
    corner = flats / math.sqrt(3)
    fig = Figure(size_in=2 * corner)
    P.hex_face(fig, (0.0, 0.0), corner)
    fig.disc((0.0, 0.0), head / 2, "hole")
    top = corner + 0.3 * flats
    dome = height * (1 - HEX_SHARE)
    P.head_button(fig, head, dome, top)
    P.hex_body(fig, flats, top + dome, top + height)
    source = "record" if thread and read else ("partial" if thread else "nominal")
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: GENERATED, NOT MEASURED: the price census has no acorn nuts (neither
#: ``deep_types`` nor ``breadth_categories`` of P2_price_census.json). Hand-set
#: from the breadth row's level (0.30 to 3.00 USD): the anchor is a
#: standard-tier 3/8" steel acorn nut, each.
PRICE = PriceModel(0.6, 0.375, 1.5, 0.2, 0.08, measured=False)


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """The line's nut table: SAE J483 or DIN 1587."""
    return (standard,)


SPEC = TypeSpec(
    KEY,
    category=("Fasteners", "Nuts", "Acorn Cap Nuts"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.012,
    price=PRICE,
    claims=claims,
    may_claim=frozenset({SAE, DIN_1587}),
    key_attributes=(THREAD,),
    unit_primary=THREAD,
    compat=False,
    use_lines=(
        "Its closed dome covers a bolt's exposed thread end and gives the joint a finished look.",
        "The domed crown keeps a cut thread from snagging clothing, hands or cables.",
    ),
)
