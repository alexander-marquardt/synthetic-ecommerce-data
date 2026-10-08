"""Each brand's copy: its title template and its description template.

A real catalog's brand section reads uniformly -- every product one maker lists
follows that maker's template -- and two makers read slightly differently.
So the voice here is a function of the BRAND alone, drawn once from a stream
seeded by the brand's name: deterministic, and never re-rolled per product.
Variety between two products of one brand comes from their specs, their
series and their description facts, not from shuffled wording.

The title keeps the census structure as its core (``<Item>, <key dim>
<role>, <material>, <coating>, <flutes>``, :func:`.naming.build_title`). The
voice only chooses among census-observed variants -- descriptive or terse,
the brand name first or not, the label spelling of each attribute, where a
tight delimiter falls -- and adds words AROUND the core: a qualifier before
the item and, where the record publishes ``Package Quantity``, a pack
segment at the end.

Nothing a voice adds may state a fact the record does not carry. The
qualifiers are words true of every product in their family
(:data:`.brands.PRODUCT_WORDS`); the use lines are true of every product of
their type; a benefit line is stated only when the record carries the value
it is about; the pack line only with the record's own quantity.
``tests/test_catalog_brands_voice.py`` holds every SKU to that.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from functools import cache

from . import brands
from .naming import LABEL_FORMS
from .typespec import RegistryTable

#: What every product of a type is for. True of the TYPE, so true of every
#: product of it, and naming no dimension, material, grade or rating.
_USE_LINES: dict[str, tuple[str, ...]] = {
    "end_mill_square": (
        "For slotting, profiling and facing on milling machines.",
        "Cuts slots, pockets and square shoulders.",
    ),
    "end_mill_ball": (
        "For contouring and profiling curved surfaces.",
        "Cuts radiused slots and contoured surfaces.",
    ),
    "drill_jobber": (
        "For hole-making in the shop.",
        "Drills holes in general shop work.",
    ),
    "tap_spiral_point": (
        "Pushes chips ahead of the tap.",
        "Cuts internal threads in through holes.",
    ),
    "screw_flat_head": (
        "Sits flush in a countersunk hole.",
        "For fastening where the head must not stand proud.",
    ),
    "screw_button_head": (
        "A low, rounded head for fastening where clearance is tight.",
        "Driven with a hex key; the rounded head leaves no sharp edge.",
    ),
    "screw_low_head": (
        "A reduced-height head for tight clearances.",
        "Driven with a hex key where a standard head would not fit.",
    ),
    "bolt_hex": (
        "Tightened with a wrench, for machinery and structural assembly.",
        "Fastens parts with a nut or into a tapped hole.",
    ),
    "washer_flat": (
        "Spreads the load under a bolt head or nut.",
        "Protects the surface under a fastener and spreads its load.",
    ),
    "hammer_ball_pein": (
        "For peening, riveting and general metalwork.",
        "Shapes metal and sets rivets.",
    ),
    "abrasive_flap_disc": (
        "For blending, deburring and finishing.",
        "Grinds and finishes in one step.",
    ),
    "nut_hex": (
        "Mates with a bolt or threaded rod of the same thread.",
        "Tightened with a wrench onto a bolt or threaded rod.",
    ),
    "bearing_radial_ball": (
        "Supports a rotating shaft.",
        "Carries a rotating shaft in its housing.",
    ),
    "wheel_depressed_center": (
        "For grinding and surface preparation.",
        "The depressed center keeps the hub clear of the work.",
    ),
    "hex_key": (
        "Drives hex socket fasteners.",
        "Turns hex socket screws.",
    ),
    "kit_assortment": (
        "Every size in one case.",
        "A set of the common sizes, kept together.",
    ),
}
# A read registers the type modules first, so a type in its own module is listed.
USE_LINES: RegistryTable[str, tuple[str, ...]] = RegistryTable(_USE_LINES)

#: The fallback for a type with no entry above -- the breadth categories
#: (:mod:`.breadth`), which trade a per-type use line for cheap, generic
#: coverage (alexander-marquardt/synthetic-ecommerce-data#34). True of
#: any product regardless of type, so it never states a fact a breadth
#: record does not carry.
GENERIC_USE_LINES: tuple[str, ...] = (
    "For general industrial and shop use.",
    "A general-purpose item for shop and industrial use.",
)

#: A line about the product family: names only the brand, its range and series.
FAMILY_PHRASES: tuple[str, ...] = (
    "Part of the {name} line.",
    "From the {name} range.",
    "{name} series.",
    "Listed in the {name} family.",
)

#: A pack line, used ONLY with the record's own Package Quantity.
PACK_PHRASES: tuple[str, ...] = (
    "Sold in packs of {n}.",
    "Pack of {n}.",
    "{n} per pack.",
)

#: The pack segment a title may end with: a label after the record's value.
PACK_LABELS: tuple[str, ...] = ("per Pack", "Pk", "Pack")

#: A generic benefit of a value, stated only when the record carries it.
BENEFITS: dict[tuple[str, str], str] = {
    ("Finish", "Zinc Plated"): "Zinc plating resists corrosion.",
    ("Finish", "Zinc Yellow"): "Yellow zinc plating resists corrosion.",
    ("Finish", "Hot Dip Galvanized"): "Hot-dip galvanizing protects against corrosion.",
    ("Finish", "Black Oxide"): "Black oxide adds mild corrosion resistance.",
    ("Finish", "TiN"): "The TiN coating reduces wear.",
    ("Finish", "TiAlN"): "The TiAlN coating holds up to heat.",
    ("Finish", "AlTiN"): "The AlTiN coating holds up to heat.",
    ("Material", "18-8 Stainless Steel"): "Stainless steel resists corrosion.",
    ("Material", "316 Stainless Steel"): "316 stainless steel resists corrosion.",
    ("Material", "Brass"): "Brass resists corrosion.",
    ("Material", "Nylon"): "Nylon will not mar the surface under it.",
    ("Material", "Solid Carbide"): "Carbide keeps its edge at high speeds.",
    ("Material", "Cobalt"): "Cobalt steel keeps its hardness when hot.",
    ("Handle Material", "Fiberglass"): "The fiberglass handle absorbs shock.",
    ("Handle Material", "Hickory"): "The hickory handle absorbs shock.",
}


@dataclass(frozen=True)
class Voice:
    brand: str
    descriptive: bool
    brand_first: bool
    #: The qualifier before the item, by family; None for no qualifier.
    qualifier: dict[str, str | None]
    #: The brand's range name, used in product names and descriptions.
    range_word: str | None
    #: One label spelling per attribute, from the census's observed forms.
    labels: dict[str, str]
    #: Where a tight delimiter falls, as a share of the segments; None for never.
    tight_at: float | None
    #: The label of the trailing pack segment; None for no pack segment.
    pack_label: str | None
    use_style: int
    family_style: int
    pack_style: int
    #: The order of the description's tail sentences: use, family, benefit, pack.
    tail_order: tuple[int, ...]


def _stratified(forms, brand: str, attribute: str) -> str:
    """The brand's label spelling for one attribute, spread over the brand book
    so the catalog-wide mix follows the census's observed shares.

    Each brand holds a slice of [0, 1) the size of its market weight, and
    takes the form whose cumulative census share covers the middle of its
    slice. A per-brand random draw was the first version: with a dozen
    brands per family it can miss a spelling outright -- measured, "Flutes"
    (28% in the census) appeared on NO title of the 100K build. The start of
    the slices rotates per attribute, so the same brands do not always take
    the commonest form.
    """
    total = sum(b.weight for b in brands.BRAND_BOOK)
    offset = (sum(map(ord, attribute)) % 97) / 97
    start = sum(b.weight for b in brands.BRAND_BOOK[: brands.BRANDS.index(brand)])
    point = ((start + brands.BY_NAME[brand].weight / 2) / total + offset) % 1.0
    cumulative = 0.0
    weight_total = sum(w for _, w in forms)
    for form, weight in forms:
        cumulative += weight / weight_total
        if point < cumulative:
            return form
    return forms[-1][0]


@cache
def voice_for(brand: str) -> Voice:
    """The brand's voice: a pure function of its name and the brand book."""
    book = brands.BY_NAME[brand]
    rng = random.Random(f"voice:{brand}")
    # A brand that opens its titles with its name adds no qualifier: the two
    # together push a long item past the title cap and shed the segment that
    # tells a SKU from its siblings (measured on the first build of this
    # book: five screw titles lost it). So a title opens "<Brand> <Item>",
    # "<Qualifier> <Item>" or "<Item>" -- one of the three, per brand.
    qualifier = {
        family: (rng.choice(words) if rng.random() < 0.5 and not book.brand_first else None)
        for family, words in brands.PRODUCT_WORDS.items()
    }
    labels = {name: _stratified(forms, brand, name) for name, forms in LABEL_FORMS.items()}
    tight_at = rng.random() if rng.random() < 0.18 else None
    return Voice(
        brand=brand,
        descriptive=book.descriptive,
        brand_first=book.brand_first,
        qualifier=qualifier,
        range_word=rng.choice(brands.RANGE_WORDS) if rng.random() < 0.6 else None,
        labels=labels,
        tight_at=tight_at,
        pack_label=rng.choice(PACK_LABELS) if rng.random() < 0.5 else None,
        use_style=rng.randrange(2),
        family_style=rng.randrange(len(FAMILY_PHRASES)),
        pack_style=rng.randrange(len(PACK_PHRASES)),
        tail_order=tuple(rng.sample(range(4), 4)),
    )


def product_name(brand: str, series: str, item: str, family: str) -> str:
    """A product's name: the brand, its range, the series, then the item."""
    voice = voice_for(brand)
    word = voice.qualifier[family]
    thing = f"{word} {item}" if word else item
    return " ".join(w for w in (brand, voice.range_word, series, "--", thing) if w)


def description_tail(brand: str, series: str, type_key: str, facts: dict[str, str]) -> str:
    """The brand-template sentences after the spec clause.

    ``facts`` is the record's own published attributes, by name. A benefit
    or pack sentence is written only from a fact that is there.
    """
    voice = voice_for(brand)
    name = " ".join(w for w in (brand, voice.range_word, series) if w)
    benefit = next(
        (text for (attr, value), text in BENEFITS.items() if facts.get(attr) == value), None
    )
    quantity = facts.get("Package Quantity")
    sentences = {
        0: USE_LINES.get(type_key, GENERIC_USE_LINES)[voice.use_style],
        1: FAMILY_PHRASES[voice.family_style].format(name=name),
        2: benefit,
        3: PACK_PHRASES[voice.pack_style].format(n=quantity) if quantity else None,
    }
    return " ".join(sentences[i] for i in voice.tail_order if sentences[i])
