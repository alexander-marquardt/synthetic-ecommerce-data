"""Pipe nipples, deepened from a breadth row into a modelled type (#832).

The breadth row offered five sizes, three materials and three lengths on two
SKUs. A pipe nipple is a short length of pipe threaded male NPT (ASME B1.20.1)
at both ends. The type builds the two families the issue names:

**Close and barrel nipples (ASTM A733).** Cut from Schedule 40 or 80 pipe. A
close nipple is threaded end to end, at the length A733 sets for its size; a
barrel nipple is any longer stocked length. Every size, close length, outside
diameter and stocked length is a row of the library's ``astm_a733_pipe_nipples``
table, read from two maker's sheets that state conformance to ASTM A733 and
ASME B1.20.1 (the table's ``_library`` block cites both). The Schedule 40 sheet
is a stainless one: a steel Schedule 40 line is stocked on its lengths, as the
dimensions A733 sets do not depend on the material. The Schedule 80 sheet is
black steel, the one material built in Schedule 80. A733's own tables were not
read (the standard is sold), so no line claims it.

**Hex nipples (no standard).** Machined from bar with a wrench hex between its
two male ends: equal, reducing and long. Every row is the Swagelok "Pipe
Fittings" catalogue MS-01-147 R10, pages 4 and 5 (2010,
https://acomee.com.mx/catalogos/catalogoss1/SWAGELOK%20PIPE%20FITTINGS.pdf,
read 2026-11-04): length, hex across flats and the pressure rating, which the
chart gives once for 316 stainless and carbon steel and once for brass. The
1/16 in rows and the heavy-wall and ISO thread variants are not built.

**Names.** ``Pipe Size`` is the census's key dimension for the type and a
reference spec-table name; ``Length``, ``Outside Dia.``, ``Hex Size``,
``Thread Type``, ``Material``, ``Finish`` and ``Type`` are census names, and
``Pressure Rating (psi)`` a reference spec-table name. ``Schedule`` is neither:
``names.NAME_EXCEPTIONS`` cites A733 and the sheets for it.

**Price.** The census measured 81 nipples (``price.DEEPENED_CENSUS``): the
model's level is hand-set against it, and its slope on the pipe size is cut
below the census's (``PRICE`` says why). The material
factors and the length slope are GENERATED, not measured: the census keys the
price on the pipe size alone.
"""

from __future__ import annotations

import contextlib
from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING, Any

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.model import keyword_attribute, numeric_attribute
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import (
    NO_STANDARD,
    _weighted,
    _window,
    feed_style,
    table_provenance,
)
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

if TYPE_CHECKING:
    from synthetic_ecommerce_data.domains.industrial.generate import LineDraft

KEY = "hex_pipe_nipples"

PIPE_SIZE = "Pipe Size"
LENGTH = "Length"
OD = "Outside Dia."
HEX = "Hex Size"
PRESSURE = "Pressure Rating (psi)"
SCHEDULE = "Schedule"
MATERIAL = "Material"
FINISH = "Finish"

A733 = "ASTM A733"
#: The hex chart, as a record's provenance names it.
HEX_CHART = "maker's hex nipple chart"
A733_TABLE = library.table("astm_a733_pipe_nipples")
_A733_ROWS: dict[str, dict[str, Any]] = {row["size"]: row for row in A733_TABLE.rows}
SIZES = tuple(_A733_ROWS)

HEX_KINDS = ("Hex", "Hex Reducing", "Hex Long")
CLOSE, BARREL = "Close", "Barrel"
KINDS = (*HEX_KINDS, CLOSE, BARREL)


def nps(size: str) -> float:
    """A nominal pipe size as a number: ``1-1/4`` is 1.25."""
    return float(sum(Fraction(part) for part in size.split("-")))


@dataclass(frozen=True)
class HexRow:
    """One row of the hex chart."""

    kind: str
    #: The size of each end, the larger first.
    ends: tuple[str, str]
    length: float
    #: Width across the hex's flats.
    hex: float
    #: The rating for 316 stainless and carbon steel, and for brass, in psig.
    psi: int
    brass_psi: int

    @property
    def size(self) -> str:
        big, small = self.ends
        return f"{big} in" if big == small else f"{big} x {small} in"


def _hex(size: str, length: float, flats: str, psi: int, brass: int) -> HexRow:
    return HexRow("Hex", (size, size), length, nps(flats), psi, brass)


def _reducing(big: str, small: str, length: float, flats: str, psi: int, brass: int) -> HexRow:
    return HexRow("Hex Reducing", (big, small), length, nps(flats), psi, brass)


#: Hex Nipples, Male NPT (page 4): size, A, F, the two ratings.
_HEX = (
    _hex("1/8", 1.01, "7/16", 10000, 5000),
    _hex("1/4", 1.40, "9/16", 8000, 4000),
    _hex("3/8", 1.43, "11/16", 7800, 3900),
    _hex("1/2", 1.84, "7/8", 7700, 3800),
    _hex("3/4", 1.84, "1-1/16", 7300, 3600),
    _hex("1", 2.32, "1-3/8", 5300, 2600),
)
#: Hex Reducing Nipples, Male NPT (page 5).
_REDUCING = (
    _reducing("1/4", "1/8", 1.22, "9/16", 10000, 5000),
    _reducing("3/8", "1/8", 1.25, "11/16", 10000, 5000),
    _reducing("3/8", "1/4", 1.43, "11/16", 8000, 4000),
    _reducing("1/2", "1/8", 1.47, "7/8", 7700, 3800),
    _reducing("1/2", "1/4", 1.65, "7/8", 8000, 4000),
    _reducing("1/2", "3/8", 1.65, "7/8", 7800, 3900),
    _reducing("3/4", "1/4", 1.65, "1-1/16", 8000, 4000),
    _reducing("3/4", "1/2", 1.84, "1-1/16", 7700, 3800),
    _reducing("1", "1/4", 1.94, "1-3/8", 5300, 2600),
    _reducing("1", "1/2", 2.13, "1-3/8", 7700, 3800),
    _reducing("1", "3/4", 2.13, "1-3/8", 7300, 3600),
)
#: Hex Long Nipples, Male NPT (page 5): the lengths each size is offered in;
#: the hex and the ratings are the equal hex nipple's.
_LONG_LENGTHS = {
    "1/8": (1.5, 2.0, 2.5, 3.0),
    "1/4": (1.5, 2.0, 2.5, 3.0, 4.0),
    "3/8": (1.5, 2.0, 2.5, 3.0, 4.0),
    "1/2": (2.0, 3.0, 4.0, 6.0),
    "3/4": (2.0, 3.0, 4.0),
    "1": (3.0, 4.0),
}
_LONG = tuple(
    HexRow("Hex Long", row.ends, length, row.hex, row.psi, row.brass_psi)
    for row in _HEX
    for length in _LONG_LENGTHS[row.ends[0]]
)
HEX_POOLS: dict[str, tuple[HexRow, ...]] = {
    "Hex": _HEX,
    "Hex Reducing": _REDUCING,
    "Hex Long": _LONG,
}


def hex_rows() -> dict[tuple[str, str, float], HexRow]:
    """(type, pipe size as published, length) -> the chart row."""
    return {
        (row.kind, row.size, round(row.length, 3)): row
        for pool in HEX_POOLS.values()
        for row in pool
    }


#: (Material, Finish) a line is made in; no finish is published on brass or
#: stainless. The chart's carbon steel is zinc plated.
HEX_MATERIALS = (("316 Stainless Steel", ""), ("Brass", ""), ("Steel", "Zinc Plated"))
#: Each schedule's materials: the Schedule 40 sheet's two stainless grades
#: and steel black or galvanized; the Schedule 80 sheet's black steel.
A733_MATERIALS = {
    "40": (
        ("Steel", "Black"),
        ("Steel", "Galvanized"),
        ("304 Stainless Steel", ""),
        ("316 Stainless Steel", ""),
    ),
    "80": (("Steel", "Black"),),
}
#: Every line a brand can offer, by family: (kind, schedule, material, finish).
FAMILIES: dict[str, tuple[tuple[str, str, str, str], ...]] = {
    # Material outermost, so a small build's first lines visit every kind.
    "hex": tuple((kind, "", m, f) for m, f in HEX_MATERIALS for kind in HEX_KINDS),
    "close": tuple(
        (CLOSE, sch, m, f) for sch, materials in A733_MATERIALS.items() for m, f in materials
    ),
    "barrel": tuple(
        (BARREL, sch, m, f) for sch, materials in A733_MATERIALS.items() for m, f in materials
    ),
}
#: How often a line is drafted in each family, about its share of the spec
#: space (126 hex, 60 close and about 880 barrel SKUs).
FAMILY_WEIGHTS = (("hex", 0.17), ("close", 0.08), ("barrel", 0.75))


def a733_cells(kind: str, schedule: str, size: str) -> list[tuple[str, str]]:
    """The (size, length) cells a line of ``kind`` draws its window from, in
    ``schedule``: every size at its close length for a close nipple, the
    lengths the A733 table offers ``size`` in for a barrel nipple."""
    if kind == CLOSE:
        return [(each, row["close"]) for each, row in _A733_ROWS.items()]
    return [(size, length) for length in _A733_ROWS[size]["lengths"][schedule]]


HEX_PROVENANCE = table_provenance((LENGTH, HEX_CHART), (HEX, HEX_CHART)) + "; " + NO_STANDARD
A733_PROVENANCE = table_provenance((LENGTH, A733), (OD, A733))


VOCAB = (
    AttrSpec("Type", "line"),
    AttrSpec(MATERIAL, "line"),
    AttrSpec(FINISH, "line"),
    AttrSpec("Thread Type", "line"),
    AttrSpec(SCHEDULE, "line"),
    AttrSpec(PIPE_SIZE, "sku"),
    AttrSpec(LENGTH, "sku", kind="length"),
    AttrSpec(OD, "sku", kind="length"),
    AttrSpec(HEX, "sku", kind="length"),
    AttrSpec(PRESSURE, "sku", kind="count"),
)


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: a family, one (kind, schedule, material, finish) of it, a window of its rows."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    family = _weighted(rng, FAMILY_WEIGHTS)
    combos = FAMILIES[family]
    kind, schedule, material, finish = combos[gen._rotate(f"nipple:{family}", len(combos))]
    hexed = kind in HEX_KINDS
    draft = LineDraft(
        item="Hex Pipe Nipple" if hexed else "Pipe Nipple",
        brand=brand,
        series=f"{'HN' if hexed else 'PN'}{rng.randint(100, 999)}",
        category=category,
        provenance=HEX_PROVENANCE if hexed else A733_PROVENANCE,
    )
    draft.line_attrs = [keyword_attribute("Type", kind), keyword_attribute(MATERIAL, material)]
    if finish:
        draft.line_attrs.append(keyword_attribute(FINISH, finish))
    draft.line_attrs.append(keyword_attribute("Thread Type", "NPT"))
    if schedule:
        draft.line_attrs.append(keyword_attribute(SCHEDULE, f"Schedule {schedule}"))
    draft.descriptors = [("Type", kind), (MATERIAL, material)]
    style = feed_style(brand, "in", BRANDS)
    count = gen._variant_count()
    # The windows' rotations are keyed by kind (and a barrel line's size), not
    # by material: each material's first line would otherwise start at the
    # table's first row, and a small build would offer the 1/8 in size alone.
    if hexed:
        for row in _window(gen, f"nipple:{kind}", list(HEX_POOLS[kind]), count):
            psi = row.brass_psi if material == "Brass" else row.psi
            child = ChildDraft(system="in")
            child.primary = numeric_attribute(PIPE_SIZE, row.size, nps(row.ends[0]))
            child.also = gen._length(LENGTH, row.length, style)
            child.attrs = [
                child.primary,
                child.also,
                gen._length(HEX, row.hex, style),
                numeric_attribute(PRESSURE, f"{psi:,}", float(psi)),
            ]
            draft.children.append(child)
        return draft
    barrel = SIZES[gen._rotate("nipple:barrel:size", len(SIZES))] if kind == BARREL else ""
    cells = a733_cells(kind, schedule, barrel)
    for size, length in _window(gen, f"nipple:{kind}:{barrel}", cells, count):
        child = ChildDraft(system="in")
        child.primary = numeric_attribute(PIPE_SIZE, f"{size} in", nps(size))
        child.also = gen._length(LENGTH, nps(length), style)
        child.attrs = [child.primary, child.also, gen._length(OD, _A733_ROWS[size]["od"], style)]
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

#: The drawing's extent (docs/adding-a-type.md "Figure and extent"): the
#: largest drawn is the 4 in nipple 12 in long, plus 0.1" and rounded to 0.05".
EXTENT = (4.6, 12.1)

#: The thread lines drawn on each threaded end, and how far an end's thread
#: runs as a fraction of the close nipple's length (a close nipple is all thread).
_THREAD_LINES = 6
_THREAD_SHARE = 0.5


def _inches(record: Mapping[str, str], name: str) -> float | None:
    with contextlib.suppress(KeyError, DimensionParseError):
        return parse_length(record[name]).inches
    return None


def _ends(record: Mapping[str, str]) -> tuple[str, str] | None:
    """The record's two end sizes, the larger first, or None."""
    sizes = record.get(PIPE_SIZE, "").removesuffix(" in").split(" x ")
    if not all(size in _A733_ROWS for size in sizes):
        return None
    return sizes[0], sizes[-1]


def _threads(fig: Figure, r: float, y0: float, y1: float) -> None:
    step = (y1 - y0) / _THREAD_LINES
    fig.lines([((-r, y0 + k * step), (r, y0 + k * step)) for k in range(1, _THREAD_LINES)])


def figure(record: dict[str, str]) -> Drawn:
    """The nipple standing on its end, in side view: the pipe with its thread
    at both ends, and a hex nipple's wrench hex between them."""
    ends = _ends(record)
    length = _inches(record, LENGTH)
    if ends is None or not length:
        fig = Figure(size_in=2.0)
        fig.rect(-0.42, 0.0, 0.42, 2.0)
        return Drawn(fig, "nominal")
    big, small = (_A733_ROWS[end] for end in ends)
    rb, rs = big["od"] / 2, small["od"] / 2
    fig = Figure(size_in=length)
    flats = _inches(record, HEX)
    if flats:
        # The hex seen across its corners, as long as a third of its flats.
        corners = flats * 2 / 3**0.5
        h = flats / 3
        mid0 = (length - h) / 2
        fig.rect(-rb, 0.0, rb, mid0)
        fig.rect(-corners / 2, mid0, corners / 2, mid0 + h)
        fig.rect(-rs, mid0 + h, rs, length)
        fig.lines([((-flats / 2, mid0), (-flats / 2, mid0 + h))])
        fig.lines([((flats / 2, mid0), (flats / 2, mid0 + h))])
        _threads(fig, rb, 0.0, mid0)
        _threads(fig, rs, mid0 + h, length)
        return Drawn(fig, "record")
    thread = min(length / 2, nps(big["close"]) * _THREAD_SHARE)
    fig.rect(-rb, 0.0, rb, length)
    _threads(fig, rb, 0.0, thread)
    _threads(fig, rb, length - thread, length)
    return Drawn(fig, "record")


# --- price ------------------------------------------------------------------------

#: The census ending mix of the 81 nipples (``breadth_categories.hex_pipe_nipples``),
#: restated here as the rigid caster restates its own: the type was a breadth
#: row, so :data:`...core.price.ENDINGS` does not carry it.
ENDINGS = {
    "other": 0.716,
    "other .x5": 0.1728,
    "other .x9": 0.0494,
    ".00": 0.0247,
    ".95": 0.0123,
    ".50": 0.0123,
    ".98": 0.0123,
}

#: What a material multiplies the price by. GENERATED, not measured: the
#: census keys a nipple's price on its pipe size only, so these only order the
#: materials as a distributor's price list does, steel cheapest and 316 dearest.
MATERIAL_FACTORS = {
    "Steel": 1.0,
    "Brass": 1.5,
    "304 Stainless Steel": 1.8,
    "316 Stainless Steel": 2.1,
}

#: Hand-set against the census's 81 nipples (p10 3.33, p50 5.2, p90 16.24),
#: scored by ``price_report``'s deepened-category rows, as the threaded rod's
#: is; not fitted by ``scripts/fit_price_model.py``. The anchor is a 1/2 in
#: standard-tier steel nipple 2 in long. The pipe-size slope is cut from the
#: census's 0.826 to 0.45: the census nipples span 3 size cells (11 SKUs with a
#: pair), and at 0.826 this type's 1/8 to 4 in sizes spread wider than the
#: census p90/p10. The length slope and the material factors are GENERATED (the
#: census has no price on length or material).
PRICE = PriceModel(
    # @fit-begin
    3.6, 0.5, 0.45, 0.2, 0.08,
    # @fit-end
    endings=ENDINGS,
    length_slope=0.2,
    anchor_length=2.0,
    materials=MATERIAL_FACTORS,
)  # fmt: skip


def claims(facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str) -> list[str]:
    """No standard is claimed: A733's own tables were not read, and no
    standard fixes a hex nipple's dimensions."""
    return []


SPEC = TypeSpec(
    KEY,
    category=("Hose, Tube, Fittings & Valves", "Pipe Fittings", "Hex Pipe Nipples"),
    standards_family="motion",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=build,
    share=0.015,
    price=PRICE,
    claims=claims,
    may_claim=frozenset(),
    key_attributes=(PIPE_SIZE,),
    compat=False,
    use_lines=(
        "Joins two female NPT fittings, or a fitting to a valve, at a fixed spacing.",
        "Extends a threaded pipe run by a short, stocked length.",
    ),
)
