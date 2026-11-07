"""Combination wrenches, deepened from a breadth row into a modelled type (#836, slice 2).

A combination wrench has an open end and a box end of the same size: the
open end slips onto a hex from the side, the box end rings it on 6 or 12
points.

**Sizes.** A wrench's size is the width across flats of the hex it turns. The
inch sizes are read from the standards library's hex nut widths across flats
(``asme_b18_2_2_hex_nuts_in``) and, where the nut table has no such width,
from ASME B18.2.1's hex cap screw heads (``fastener_standards``); the metric
ones from ISO 4017's hex cap screw heads and, where it has none, from
DIN 933's. So every size turns a hex fastener the catalog sells. Each kind
stocks a run of those sizes (:data:`KINDS`), and the breadth row's sizes are
each a run's first size on some line whatever the seed (:data:`BREADTH_SIZES`).
ASME B107.100, the flat wrench standard the issue names, was not read: the
standard is sold, and only its table of contents is public (it names
Category 6 Combination Wrench and its Tables 5.1.1-1 and 5.1.1-1M, sizes in
U.S. Customary and SI units). So no line claims it, no record publishes a
length the standard would give (overall length, head thickness), and the
sizes it lists beyond these hex widths (13/16 in, 1 in, 9 mm, 11 mm and so on) are not offered.

**Names.** ``Size``, ``Type``, ``Material`` and ``Finish`` are census names.
The census has no wrench family and no name for how many points a box end
has (its ``Point Type`` is a set screw's or a drill's point), so the type
publishes ``Number of Points``, cased like the census's ``Number of
Flutes``, from ``names.NAME_EXCEPTIONS``.

**Lines.** A line is one brand's wrenches of one kind in one unit system. A
kind is a type (standard, long pattern, stubby or ratcheting), the box end's
points and a finish: a chrome plated chrome vanadium wrench, or an industrial
alloy steel one in black oxide. The combinations are rotated, not drawn, so
every kind and system is built.

**Price.** The census measured 158 combination wrench prices while the type
was a breadth row; they stay its census (``price.DEEPENED_CENSUS``) and the
model is fitted to them (:data:`PRICE`).
"""

from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction
from typing import Any, NamedTuple

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure, regular_polygon
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial import standards
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import MM_PER_INCH, table_provenance
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "combination_wrenches"
ITEM = "Combination Wrench"


def _inch_flats() -> dict[Fraction, str]:
    """Each inch width across flats (in inches) and the standard it was read from."""
    flats = {
        Fraction(row["flats_in"]): "ASME B18.2.2"
        for row in library.table("asme_b18_2_2_hex_nuts_in").rows
    }
    for row in standards.rows("ASME B18.2.1"):
        if row["present_in_source"]:
            width = Fraction(row["width_across_flats_in"]).limit_denominator(64)
            flats.setdefault(width, "ASME B18.2.1")
    return dict(sorted(flats.items()))


def _mm_flats() -> dict[float, str]:
    """Each metric width across flats (in mm) and the standard it was read from."""
    flats: dict[float, str] = {}
    for standard in ("ISO 4017", "DIN 933"):
        for row in standards.rows(standard):
            if row["present_in_source"]:
                flats.setdefault(float(row["width_across_flats_mm"]), standard)
    return dict(sorted(flats.items()))


INCH_FLATS = _inch_flats()
MM_FLATS = _mm_flats()


class Kind(NamedTuple):
    """One kind of line: what it publishes, and the run of sizes it stocks
    (smallest and largest, inch then metric)."""

    type: str
    points: str
    material: str
    finish: str
    inch: tuple[str, str]
    mm: tuple[float, float]


#: Every kind a brand can offer, and the run each stocks: a stubby wrench is
#: made in the small sizes, a ratcheting box in the middle ones, and a 6-point
#: box from 5/16 in and 7 mm.
CRV, CHROME = "Chrome Vanadium Steel", "Chrome Plated"
KINDS = (
    Kind("Standard", "12-Point", CRV, CHROME, ("1/4", "3/2"), (5.5, 30.0)),
    Kind("Standard", "6-Point", CRV, CHROME, ("5/16", "9/8"), (7.0, 24.0)),
    Kind("Standard", "12-Point", "Alloy Steel", "Black Oxide", ("5/16", "3/2"), (8.0, 30.0)),
    Kind("Long Pattern", "12-Point", CRV, CHROME, ("5/16", "15/16"), (8.0, 24.0)),
    Kind("Stubby", "12-Point", CRV, CHROME, ("1/4", "3/4"), (7.0, 19.0)),
    Kind("Ratcheting", "12-Point", CRV, CHROME, ("5/16", "15/16"), (8.0, 19.0)),
)
#: Every line a brand can offer: a kind in a unit system.
COMBOS = tuple((kind, system) for kind in KINDS for system in ("in", "mm"))

#: The sizes the breadth row offered (its ``size_values``), each still offered. The first inch
#: lines start their runs at these in turn (:func:`_run`), so no seed's variant counts can
#: leave one out (#50: seed 20260918 built no 5/8 or 3/4 in wrench).
BREADTH_SIZES = tuple(
    Fraction(s) for s in ("1/4", "5/16", "3/8", "7/16", "1/2", "9/16", "5/8", "3/4")
)


def sizes_in(kind: Kind, metric: bool) -> tuple[float, ...]:
    """``kind``'s stocked sizes in one unit system, in inches."""
    if metric:
        low, high = kind.mm
        return tuple(mm / MM_PER_INCH for mm in MM_FLATS if low <= mm <= high)
    low, high = (Fraction(end) for end in kind.inch)
    return tuple(float(width) for width in INCH_FLATS if low <= width <= high)


def flats_standard(size_in: float, metric: bool) -> str:
    """The standard a size (in inches) was read from."""
    if metric:
        return MM_FLATS[round(size_in * MM_PER_INCH, 1)]
    return INCH_FLATS[Fraction(size_in).limit_denominator(64)]


def _run(gen: Any, type_key: str, kind: Kind, system: str, count: int) -> list[float]:
    """The ``count`` contiguous sizes a line stocks.

    The pool's rotation alone starts each (kind, system)'s runs at its short end, and with a
    few lines to a key the long breadth sizes were a variant count's luck. So the type's
    first inch lines start at each of :data:`BREADTH_SIZES` in turn (or as near as the kind's
    run allows) and the rotation picks the later ones. Both are rotations, not draws.
    """
    pool = sorted(sizes_in(kind, system == "mm"))
    run = gen._offered_run(f"sizes:{kind.type}:{kind.finish}:{system}", pool, count)
    if system == "mm":
        return run
    step = gen._rotation_step(f"breadth:{type_key}")
    if step >= len(BREADTH_SIZES):
        return run
    anchor = float(BREADTH_SIZES[step])
    start = next((i for i, size in enumerate(pool) if size >= anchor - 1e-9), 0)
    start = min(start, len(pool) - count)
    return pool[start : start + count]


def provenance(sizes: list[float], metric: bool) -> str:
    standards_read = dict.fromkeys(flats_standard(size, metric) for size in sizes)
    return table_provenance(*(("Size", standard) for standard in standards_read))


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Type", "line"),
    _spec("Number of Points", "line"),
    _spec("Material", "line", 0.85),
    # Always published: it tells an alloy steel line from a chrome vanadium one.
    _spec("Finish", "line"),
    _spec("Size", "sku", kind="length"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    kind, system = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    metric = system == "mm"
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"{'RW' if kind.type == 'Ratcheting' else 'CW'}{rng.randint(100, 999)}",
        category=category,
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", ITEM)),  # keeps the stream stable for #497
        keyword_attribute("Type", kind.type),
        keyword_attribute("Number of Points", kind.points),
        keyword_attribute("Material", kind.material),
        keyword_attribute("Finish", kind.finish),
    ]
    draft.descriptors = [("Type", kind.type), ("Number of Points", kind.points)]
    count = min(gen._variant_count(), len(sizes_in(kind, metric)))
    style = gen._style(system)
    run = _run(gen, type_key, kind, system, count)
    for size_in in run:
        child = ChildDraft(system=system)
        child.primary = gen._length("Size", size_in, style)
        child.attrs = [child.primary]
        draft.children.append(child)
    draft.provenance = provenance(run, metric)
    return draft


#: The census's combination-wrench endings
#: (``breadth_categories.combination_wrenches.endings``).
ENDINGS = {
    "other": 0.6772,
    "other .x5": 0.1772,
    "other .x9": 0.0696,
    ".00": 0.038,
    ".95": 0.019,
    ".50": 0.0127,
    ".98": 0.0063,
}

#: Fitted by hand to the census's 158 combination-wrench prices (p10 4.011,
#: p50 15.38, p90 39.145 USD; ``price.DEEPENED_CENSUS``): the anchor and the
#: noise, scored by the p50 and p90/p10 rows at both sizes. The slope on the
#: size is the census's (0.647, ``price_vs_key_dimension``). The kind factors
#: are GENERATED, not measured: the census's prices are not split by kind; a
#: ratcheting box costs about 1.8 times a standard wrench, a long pattern 1.3
#: times and a stubby 0.9 times.
PRICE = PriceModel(
    # @fit-begin
    15.9,
    0.5,
    0.647,
    0.75,
    0.1,
    # @fit-end
    endings=ENDINGS,
    option_attribute="Type",
    option_factors={"Ratcheting": 1.8, "Long Pattern": 1.3, "Stubby": 0.9},
)


#: The drawing's overall length, in sizes, by type, above a floor in inches:
#: no record publishes a length, so these only proportion the drawing (a
#: distributor's 1/2 in standard wrench is about 7 in long, a stubby 4 in).
LENGTH = {"Standard": 13.0, "Long Pattern": 17.0, "Stubby": 7.5, "Ratcheting": 13.0}
LENGTH_FLOOR = 3.0


def _size(record: Mapping[str, str]) -> float | None:
    try:
        return parse_length(record["Size"]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The wrench lying flat: the open end's jaw on the left, the shank, and
    the box end on the right with its 6 or 12 points."""
    size = _size(record)
    s = size or 0.5
    length = max(LENGTH.get(record.get("Type", ""), LENGTH["Standard"]) * s, LENGTH_FLOOR)
    head = 0.95 * s
    shank = 0.45 * s
    fig = Figure(size_in=length)
    fig.rect(0.0, -shank / 2, length, shank / 2)
    fig.disc((0.0, 0.0), head)
    fig.disc((length, 0.0), head)
    # The open end's jaw: a slot as wide as the size, open to the left.
    fig.rect(-head, -s / 2, 0.15 * s, s / 2, role="hole")
    # The box end's opening: one hexagon, or two at 30 degrees for 12 points.
    radius = s / 3**0.5
    fig.poly(regular_polygon((length, 0.0), radius, 6, 0), role="hole")
    if record.get("Number of Points") != "6-Point":
        fig.poly(regular_polygon((length, 0.0), radius, 6, 30), role="hole")
    return Drawn(fig, "partial" if size else "nominal")


SPEC = TypeSpec(
    KEY,
    category=("Hand Tools", "Wrenches & Keys", "Combination Wrenches"),
    standards_family="hand_tool",
    vocab=VOCAB,
    figure=figure,
    # Measured at the default and ``--lines 39000`` builds (docs/adding-a-type.md
    # "Figure and extent"): the largest drawn is 22.35 x 2.85 in, a 1-1/2 in
    # standard wrench with its two heads.
    extent=(22.45, 2.95),
    make=_make,
    share=0.0135,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Size",),
    compat=False,
    use_lines=(
        "Turns hex nuts and bolt heads where a socket cannot reach.",
        "Holds the nut while a ratchet turns the bolt.",
    ),
)
