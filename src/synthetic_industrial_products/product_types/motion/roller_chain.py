"""Roller chain: a breadth category deepened into a modelled type (#53).

Every size row is ANSI/ASME B29.1's standard series, chain numbers 25 to 240:

* ``Pitch``, ``Roller Dia.`` and ``Inside Width`` (the width between the
  roller link plates) are B29.1's nominal dimensions, in inches. Chains 25
  and 35 are rollerless (bushing) chains, so they publish no ``Roller Dia.``.
* No tensile strength is published: the B29.1 editions disagree on the
  minimum ultimate tensile strength (the 1993 table's 3,700 lbf for a 40
  chain against the later 12,500 lbf x pitch squared, 3,125), so the type
  omits it rather than pick one.
* ``ANSI Number`` is the B29.1 designation: the chain number, with ``-2`` or
  ``-3`` for a double or triple strand chain.

The lengths (10 ft boxes, 50 and 100 ft reels), the strand counts and the
material and finish each chain number is stocked in are a distributor's
offer, not a table; they choose which rows a line offers and fix no
published dimension.

The display name is ``Pitch``, as real catalogs print it, but the machine key
is ``chain_pitch``: a metric tap publishes ``Pitch`` too, for its thread
pitch, and the two are different concepts (#36).
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING, Any

from ...catalog.formats import LengthStyle
from ...catalog.model import keyword_attribute, length_attribute, numeric_attribute
from ...catalog.newtypes import _weighted, _window, table_provenance
from ...catalog.price import PriceModel
from ...catalog.typespec import TypeSpec
from ...catalog.vocab import AttrSpec
from ...drawing.figures import Drawn, _length_or
from ...drawing.model import Figure, arc

if TYPE_CHECKING:
    from ...catalog.generate import LineDraft

STANDARD = "ASME B29.1"

#: The machine key of this type's ``Pitch`` (see the module docstring).
PITCH_KEY = "chain_pitch"

#: B29.1 standard series: (chain number, pitch, roller diameter or None for a
#: rollerless chain, width between roller link plates), inches.
ANSI: tuple[tuple[str, Fraction, Fraction | None, Fraction], ...] = (
    ("25", Fraction(1, 4), None, Fraction(1, 8)),
    ("35", Fraction(3, 8), None, Fraction(3, 16)),
    ("40", Fraction(1, 2), Fraction(5, 16), Fraction(5, 16)),
    ("50", Fraction(5, 8), Fraction(2, 5), Fraction(3, 8)),
    ("60", Fraction(3, 4), Fraction(15, 32), Fraction(1, 2)),
    ("80", Fraction(1), Fraction(5, 8), Fraction(5, 8)),
    ("100", Fraction(5, 4), Fraction(3, 4), Fraction(3, 4)),
    ("120", Fraction(3, 2), Fraction(7, 8), Fraction(1)),
    ("140", Fraction(7, 4), Fraction(1), Fraction(1)),
    ("160", Fraction(2), Fraction(9, 8), Fraction(5, 4)),
    ("180", Fraction(9, 4), Fraction(45, 32), Fraction(45, 32)),
    ("200", Fraction(5, 2), Fraction(25, 16), Fraction(3, 2)),
    ("240", Fraction(3), Fraction(15, 8), Fraction(15, 8)),
)

STRANDS = {1: "Single Strand", 2: "Double Strand", 3: "Triple Strand"}

#: Every brand spells a chain's dimensions as B29.1's table does, an inch
#: fraction, rather than in its own feed's style. The facet derivation counts
#: distinct spellings, not magnitudes (#77): four brand spellings of 13 sizes
#: over the default build's 68 chains read as a range, which no dimension of
#: this catalog may be.
SPELLING = LengthStyle("in", '"', "fraction")

#: A length, in feet, and the inches the price model scales it by.
FEET_PER_LENGTH = {10: 120.0, 50: 600.0, 100: 1200.0}


@dataclass(frozen=True)
class Offer:
    """One stocked offer: strands, material, finish, length, and its chain numbers."""

    strands: int
    material: str
    finish: str
    feet: int
    first: str
    last: str

    def rows(self) -> list[tuple[str, Fraction, Fraction | None, Fraction]]:
        numbers = [row[0] for row in ANSI]
        return list(ANSI[numbers.index(self.first) : numbers.index(self.last) + 1])


#: (offer, weight): how often a line is drafted in each.
OFFERS: tuple[tuple[Offer, float], ...] = (
    (Offer(1, "Steel", "Plain", 10, "25", "240"), 0.28),
    (Offer(1, "Steel", "Plain", 50, "25", "80"), 0.08),
    (Offer(1, "Steel", "Plain", 100, "25", "60"), 0.06),
    (Offer(2, "Steel", "Plain", 10, "25", "240"), 0.18),
    (Offer(3, "Steel", "Plain", 10, "40", "160"), 0.10),
    (Offer(1, "Steel", "Nickel Plated", 10, "35", "80"), 0.10),
    (Offer(2, "Steel", "Nickel Plated", 10, "40", "60"), 0.04),
    (Offer(1, "18-8 Stainless Steel", "Plain", 10, "25", "100"), 0.12),
    (Offer(1, "316 Stainless Steel", "Plain", 10, "40", "60"), 0.04),
)

ITEM = "Roller Chain"

VOCAB = (
    AttrSpec("Item", "line"),
    AttrSpec("Style", "line"),
    AttrSpec("Material", "line"),
    AttrSpec("Finish", "line", 0.9),
    AttrSpec("Length", "line"),
    AttrSpec("Pitch", "sku"),
    AttrSpec("ANSI Number", "sku"),
    AttrSpec("Roller Dia.", "sku", 0.9, kind="length"),
    AttrSpec("Inside Width", "sku", 0.9, kind="length"),
)

PROVENANCE = table_provenance(
    ("Pitch", STANDARD), ("Roller Dia.", STANDARD), ("Inside Width", STANDARD)
)


def ansi_number(number: str, strands: int) -> str:
    return number if strands == 1 else f"{number}-{strands}"


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: an offer, and a window of its chain numbers."""
    # Imported here: generate imports the type tables, which discover this module.
    from ...catalog.brands import pick_brand
    from ...catalog.generate import ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    offer = _weighted(rng, OFFERS)
    style_name = STRANDS[offer.strands]
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"RC{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
        standard=STANDARD,
    )
    draft.line_attrs = [
        keyword_attribute("Item", ITEM),
        keyword_attribute("Style", style_name),
        keyword_attribute("Material", offer.material),
        keyword_attribute("Finish", offer.finish),
        numeric_attribute("Length", f"{offer.feet} ft", FEET_PER_LENGTH[offer.feet]),
    ]
    draft.descriptors = [("Style", style_name), ("Material", offer.material)]
    style = SPELLING
    key = f"roller-chain:{offer.strands}:{offer.material}:{offer.finish}:{offer.feet}"
    for number, pitch, roller, width in _window(gen, key, offer.rows(), gen._variant_count()):
        child = ChildDraft(system="in")
        child.primary = dataclasses.replace(
            length_attribute("Pitch", gen._publish(float(pitch), style)), key=PITCH_KEY
        )
        child.attrs = [
            child.primary,
            keyword_attribute("ANSI Number", ansi_number(number, offer.strands)),
        ]
        if roller is not None:
            child.attrs.append(length_attribute("Roller Dia.", gen._publish(float(roller), style)))
        child.attrs.append(length_attribute("Inside Width", gen._publish(float(width), style)))
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

_STRAND_COUNT = {name: count for count, name in STRANDS.items()}
#: Proportions of pitch the drawing uses for what no record publishes: the link
#: plate's height, the plate's thickness and the pin's radius.
_PLATE_HEIGHT = 0.95
_PLATE_THICKNESS = 0.12
_PIN_RADIUS = 0.16
#: A rollerless chain's bushing, drawn where a roller would be.
_BUSHING = 0.52


def chain(record: dict[str, str]) -> Drawn:
    """Side view of two pitches (plates, rollers, pins) above the top view of every strand."""
    pitch, ok_p = _length_or(record, "Pitch", 0.5)
    roller, ok_r = _length_or(record, "Roller Dia.", _BUSHING * pitch)
    width, ok_w = _length_or(record, "Inside Width", 0.5 * pitch)
    strands = _STRAND_COUNT.get(record.get("Style", ""), 1)
    source = "record" if ok_p and ok_r and ok_w else ("partial" if ok_p else "nominal")
    plate = _PLATE_HEIGHT * pitch
    thick = _PLATE_THICKNESS * pitch
    fig = Figure(size_in=2 * pitch + plate)
    ends = (0.0, 2 * pitch)
    fig.poly([*arc((ends[0], 0.0), plate / 2, 90, 270), *arc((ends[1], 0.0), plate / 2, -90, 90)])
    for k in range(3):
        fig.disc((k * pitch, 0.0), roller / 2, "plain")
        fig.disc((k * pitch, 0.0), _PIN_RADIUS * pitch, "hole")
    top = plate / 2 + 0.3 * plate
    x0, x1 = -plate / 2, 2 * pitch + plate / 2
    for s in range(strands):
        y = top + s * (width + 3 * thick)
        fig.rect(x0, y, x1, y + thick)
        fig.rect(x0, y + thick, x1, y + thick + width, "plain")
        fig.rect(x0, y + thick + width, x1, y + 2 * thick + width)
        fig.lines(((k * pitch, y + thick), (k * pitch, y + thick + width)) for k in range(3))
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: What a multiple strand chain costs against the single strand chain of its
#: pitch, material, length and brand. GENERATED, not measured: the census's 71
#: prices are not split by strand count. A double strand chain is two single
#: chains' plates and rollers on shared pins, a triple strand chain three, and
#: each sells a little under that multiple of the single chain.
STRAND_FACTORS = {STRANDS[1]: 1.0, STRANDS[2]: 1.9, STRANDS[3]: 2.8}

#: The census's roller-chain endings (``breadth_categories.roller_chain.endings``).
ENDINGS = {"other .x5": 0.3239, ".00": 0.2958, ".50": 0.2676, "other": 0.0986, ".95": 0.0141}

#: Fitted by hand to the census's 71 roller-chain prices (p10 74.1, p50 358,
#: p90 773 USD; ``price.DEEPENED_CENSUS``): the anchor and the noise, scored by
#: the p50 and p90/p10 rows at both sizes. The census measures no size slope
#: for this category (no within-page pairs), so the pitch slope and the length
#: slope are GENERATED, not measured: a chain's steel grows about as pitch
#: squared, and a 100 ft reel costs nearly ten 10 ft boxes.
PRICE = PriceModel(
    # @fit-begin
    116.0,
    0.5,
    1.2,
    0.28,
    0.1,
    # @fit-end
    endings=ENDINGS,
    pack_attribute="Length",
    pack_slope=0.93,
    pack_ref=120.0,
    option_attribute="Style",
    option_factors=STRAND_FACTORS,
)

SPEC = TypeSpec(
    "roller_chain",
    category=("Motion Control & Fluid Power", "Chain & Sprockets", "Roller Chains"),
    standards_family="motion",
    vocab=VOCAB,
    figure=chain,
    # 240-2 and 160-3, the largest drawn: 8.85 x 9.25 in.
    extent=(8.95, 9.35),
    make=build,
    share=0.016,
    price=PRICE,
    use_lines=(
        "Runs on sprockets of the same ANSI chain number.",
        "Joins end to end with a connecting link of the same ANSI chain number.",
    ),
)
