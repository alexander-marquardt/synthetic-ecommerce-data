"""The plain screws: one builder and one table for the kinds a hardware shelf sells (#750).

Each kind is a leaf beside the lag screw under ``Fasteners > Bolts, Screws & Cap Screws``. #658
retired the ``Fasteners > Screws`` node, so a shopper's ``screws`` reaches one place. A kind is a
:class:`PlainScrewKind`, whose rows are the gauge or thread and the lengths it comes in.

Two lines in every :data:`SOLD_PERIOD` are sold by the box and take the plural title, in the pack
form retail uses: ``Wood Screws, #8 Gauge, 1-1/4" L, Flat Head, Box of 100``. The third is sold
singly and takes the singular one, so ``screw`` and ``screws`` both have real titles. It publishes
a pack of 1: with no pack at all, a brand's loose screw would read as its boxed one less a dropped
attribute. A SKU's box is its own, because a box holds fewer of a longer screw (:func:`box_of`).

The sizes are the ones hardware listings carry, and no standard's table. The price is GENERATED,
not measured: the price census has no plain screws.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from synthetic_ecommerce_data.core.dimensions import MM_PER_INCH, parse_thread
from synthetic_ecommerce_data.core.model import keyword_attribute, numeric_attribute
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.plain_screw import plain_screw
from synthetic_ecommerce_data.domains.industrial.vocab import (
    MACHINE_SCREW_VOCAB,
    PLAIN_SCREW_VOCAB,
)

#: The node every plain screw sits under, with the lag screw and the cap screws.
PARENT: tuple[str, ...] = ("Fasteners", "Bolts, Screws & Cap Screws")

PROVENANCE = "generated; the sizes hardware listings carry, not read from a standard"

#: A kind's share of ``lines``: about 58 products at the large build, 290 over the five kinds, so
#: the range stays small beside the 24,000 SKUs of the node it joins.
SHARE = 0.0015

#: Which line of a kind is sold singly: the first of every :data:`SOLD_PERIOD`.
SOLD_PERIOD = 3
SOLD_SINGLY_SLOT = 0

#: The share of a kind's lines that are metric, where the kind has metric rows.
METRIC_SHARE = 0.3

#: A size and the lengths it comes in: inches on an inch row, millimetres on a metric one.
Rows = tuple[tuple[str, tuple[float, ...]], ...]


def box_of(length_in: float) -> int:
    """How many screws of ``length_in`` a box holds."""
    if length_in <= 1.0:
        return 200
    return 100 if length_in <= 2.0 else 50


@dataclass(frozen=True)
class PlainScrewKind:
    """What one kind draws: its words, its materials and heads, and its rows."""

    key: str
    item: str
    plural: str
    series: str
    #: Each material, and the finishes it is sold in.
    materials: tuple[tuple[str, tuple[str, ...]], ...]
    heads: tuple[str, ...]
    drives: tuple[str, ...]
    rows: Rows
    #: Shown price (USD) of one standard-tier steel screw of the median size.
    price: float
    use_lines: tuple[str, ...]
    #: The largest drawn ``(width, height)`` in inches of any product of the kind, with a
    #: little headroom (``tests/test_sku_drawings.py`` holds every drawing to it).
    extent: tuple[float, float]
    metric_rows: Rows = ()
    #: The kind's part-number block, where the one its key derives is taken.
    part_number_block: int | None = None

    @property
    def size_attribute(self) -> str:
        """What the kind's size is published as: a thread when it has one, else a gauge."""
        return "Thread Size" if self.is_threaded else "Gauge"

    @property
    def is_threaded(self) -> bool:
        return not self.rows[0][0].removeprefix("#").isdigit()


def _pairs(rows: Rows, per_inch: float) -> list[tuple[str, float]]:
    """Every ``(size, length in inches)`` of ``rows``, in order."""
    return [(size, length / per_inch) for size, lengths in rows for length in lengths]


def _lengths_of_a_line(
    gen: Any, key: str, pairs: list[tuple[str, float]], count: int
) -> list[tuple[str, float]]:
    """``count`` of ``pairs`` from a rotating start, no length twice.

    A walk past the end of one size carries on into the next, so a line may hold two gauges. A
    length it already holds is passed over, so each SKU's length is its own within the line.
    """
    start = gen._rotate(key, len(pairs))
    by_length: dict[float, str] = {}
    for step in range(len(pairs)):
        size, length_in = pairs[(start + step) % len(pairs)]
        by_length.setdefault(length_in, size)
    return [(size, length_in) for length_in, size in by_length.items()][:count]


def _size(kind: PlainScrewKind, size: str) -> Any:
    if kind.is_threaded:
        return keyword_attribute(kind.size_attribute, size)
    return numeric_attribute(kind.size_attribute, size, float(size.removeprefix("#")))


def build(kind: PlainScrewKind):
    """The builder of ``kind``: ``make(generator, type_key, category)``."""

    def make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
        # Imported here: generate imports the type tables, which discover the kinds.
        from synthetic_ecommerce_data.core.brands import pick_brand
        from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

        rng = gen.rng
        brand = pick_brand(rng, type_key, gen._exhausted)
        boxed = gen._rotate(f"plain_screw_sold:{kind.key}", SOLD_PERIOD) != SOLD_SINGLY_SLOT
        material, finishes = rng.choice(kind.materials)
        head = rng.choice(kind.heads)
        draft = LineDraft(
            item=kind.plural if boxed else kind.item,
            brand=brand,
            series=f"{kind.series}{rng.randint(100, 999)}",
            category=category,
            provenance=PROVENANCE,
        )
        draft.line_attrs = [
            keyword_attribute("Head Type", head),
            keyword_attribute("Drive Type", rng.choice(kind.drives)),
            keyword_attribute("Material", material),
            keyword_attribute("Finish", rng.choice(finishes)),
        ]
        draft.descriptors = [("Head Type", head)]
        metric = bool(kind.metric_rows) and rng.random() < METRIC_SHARE
        pairs = _pairs(kind.metric_rows, MM_PER_INCH) if metric else _pairs(kind.rows, 1.0)
        system = "mm" if metric else "in"
        style = gen._style(system)
        count = gen._variant_count()
        walk = f"plain_screw:{kind.key}:{system}"
        for size, length_in in _lengths_of_a_line(gen, walk, pairs, count):
            child = ChildDraft(system=system)
            child.primary = _size(kind, size)
            child.also = gen._length("Length", length_in, style)
            child.attrs = [child.primary, child.also]
            quantity = box_of(length_in) if boxed else 1
            child.attrs.append(numeric_attribute("Units per Pack", str(quantity), float(quantity)))
            if boxed:
                child.pack_phrase = f"Box of {quantity}"
            draft.children.append(child)
        return draft

    return make


def price_model(kind: PlainScrewKind) -> PriceModel:
    """GENERATED, NOT MEASURED: a screw costs about its diameter, and a box less per screw."""
    size = kind.rows[len(kind.rows) // 2][0]
    key = parse_thread(size).major.inches if kind.is_threaded else float(size.removeprefix("#"))
    return PriceModel(
        kind.price,
        key,
        0.9,
        0.15,
        0.05,
        pack_attribute="Units per Pack",
        pack_slope=0.6,
        measured=False,
    )


def spec(kind: PlainScrewKind) -> TypeSpec:
    """The type module's ``SPEC`` for ``kind``."""
    return TypeSpec(
        kind.key,
        label=kind.item,
        part_number_block=kind.part_number_block,
        category=(*PARENT, kind.plural),
        standards_family="fastener",
        vocab=MACHINE_SCREW_VOCAB if kind.is_threaded else PLAIN_SCREW_VOCAB,
        figure=plain_screw,
        extent=kind.extent,
        make=build(kind),
        share=SHARE,
        price=price_model(kind),
        may_claim=frozenset(),
        key_attributes=(kind.size_attribute,),
        fastener=True,
        use_lines=kind.use_lines,
        # A plain screw is not sold to fit a part: no cross-reference to write.
        compat=False,
    )


WOOD = PlainScrewKind(
    key="screw_wood",
    item="Wood Screw",
    plural="Wood Screws",
    series="WS",
    materials=(
        ("Steel", ("Zinc Plated", "Zinc Yellow")),
        ("18-8 Stainless Steel", ("Plain",)),
        ("Brass", ("Plain",)),
    ),
    heads=("Flat Head", "Round Head"),
    drives=("Phillips", "Slotted", "Square"),
    rows=(
        ("#6", (0.5, 0.75, 1.0, 1.25, 1.5)),
        ("#8", (0.75, 1.0, 1.25, 1.5, 2.0, 2.5)),
        ("#10", (1.0, 1.5, 2.0, 2.5, 3.0)),
        ("#12", (1.5, 2.0, 3.0)),
    ),
    price=0.34,
    use_lines=(
        "Drives into a pilot hole in wood and holds by its coarse thread.",
        "The smooth shank under the head pulls two boards tight together.",
    ),
    extent=(0.8, 3.2),
)

MACHINE = PlainScrewKind(
    key="screw_machine",
    item="Machine Screw",
    plural="Machine Screws",
    series="MS",
    materials=(
        ("Steel", ("Zinc Plated", "Black Oxide")),
        ("18-8 Stainless Steel", ("Plain",)),
        ("Brass", ("Plain",)),
    ),
    heads=("Pan Head", "Flat Head", "Round Head"),
    drives=("Phillips", "Slotted"),
    rows=(
        ("#4-40", (0.25, 0.375, 0.5, 0.75)),
        ("#6-32", (0.25, 0.375, 0.5, 0.75, 1.0)),
        ("#8-32", (0.375, 0.5, 0.75, 1.0, 1.25)),
        ("#10-24", (0.5, 0.75, 1.0, 1.5)),
        ("#10-32", (0.5, 0.75, 1.0, 1.5)),
        ("1/4-20", (0.5, 0.75, 1.0, 1.5, 2.0)),
    ),
    metric_rows=(
        ("M3x0.5", (6.0, 8.0, 10.0, 12.0, 16.0)),
        ("M4x0.7", (8.0, 10.0, 12.0, 16.0, 20.0)),
        ("M5x0.8", (10.0, 12.0, 16.0, 20.0, 25.0)),
        ("M6x1", (12.0, 16.0, 20.0, 25.0, 30.0)),
    ),
    price=0.28,
    use_lines=(
        "Threads into a tapped hole or a nut to fasten panels, brackets and electrical parts.",
        "Its fine, even thread holds in metal, where a wood screw would not bite.",
    ),
    extent=(0.8, 2.4),
)

DRYWALL = PlainScrewKind(
    key="screw_drywall",
    item="Drywall Screw",
    plural="Drywall Screws",
    series="DW",
    materials=(("Steel", ("Black Phosphate", "Zinc Plated")),),
    heads=("Bugle Head",),
    drives=("Phillips", "Square"),
    rows=(
        ("#6", (1.0, 1.25, 1.625, 2.0)),
        ("#8", (1.625, 2.0, 2.5, 3.0)),
    ),
    price=0.16,
    use_lines=(
        "Fastens drywall to wood or metal studs without tearing the face paper.",
        "The bugle head sits just under the surface, ready for joint compound.",
    ),
    extent=(0.8, 3.2),
)

SHEET_METAL = PlainScrewKind(
    key="screw_sheet_metal",
    item="Sheet Metal Screw",
    plural="Sheet Metal Screws",
    series="SM",
    materials=(
        ("Steel", ("Zinc Plated",)),
        ("18-8 Stainless Steel", ("Plain",)),
    ),
    heads=("Pan Head", "Hex Washer Head"),
    drives=("Phillips", "Square"),
    rows=(
        ("#6", (0.375, 0.5, 0.75, 1.0)),
        ("#8", (0.5, 0.75, 1.0, 1.5)),
        ("#10", (0.5, 0.75, 1.0, 1.5, 2.0)),
        ("#12", (0.75, 1.0, 1.5)),
    ),
    price=0.24,
    use_lines=(
        "A self tapping screw that cuts its own thread in thin sheet.",
        "Fastens ductwork, flashing and panels with no nut behind them.",
    ),
    extent=(0.8, 2.4),
    part_number_block=9946,
)

DECK = PlainScrewKind(
    key="screw_deck",
    item="Deck Screw",
    plural="Deck Screws",
    series="DK",
    materials=(
        ("Steel", ("Ceramic Coated",)),
        ("316 Stainless Steel", ("Plain",)),
    ),
    heads=("Bugle Head",),
    drives=("Star", "Square"),
    rows=(
        ("#8", (1.25, 1.625, 2.0, 2.5, 3.0)),
        ("#10", (2.0, 2.5, 3.0, 3.5, 4.0)),
    ),
    price=0.3,
    use_lines=(
        "Fastens deck boards to joists and holds outdoors without rusting.",
        "The bugle head sits flush with the board and leaves no sharp edge underfoot.",
    ),
    extent=(0.8, 4.3),
)

#: Every kind, by its type key.
KINDS: dict[str, PlainScrewKind] = {
    kind.key: kind for kind in (WOOD, MACHINE, DRYWALL, SHEET_METAL, DECK)
}
