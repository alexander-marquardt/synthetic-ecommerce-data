"""Roller chain: a breadth category deepened into a modelled type (#53).

Every size row is ANSI/ASME B29.1's standard series, chain numbers 25 to 240,
as published in the distributor's size chart at ``SOURCE_URL`` (retrieved
2026-10-07; ASME's own text was not read):

* ``Pitch``, ``Roller Dia.`` and ``Inside Width`` (the width between the
  roller link plates) are B29.1's nominal dimensions, in inches. Chains 25
  and 35 are rollerless (bushing) chains, so they publish no ``Roller Dia.``.
* No tensile strength is published: the two tables the dimensions were checked
  against (``SOURCE_URL`` and ``RULE_URL`` below) disagree on it. The B29.1-2011
  table gives a 40 chain a minimum of 3,125 lbf (12,500 lbf x pitch squared);
  the distributor's chart gives its own chain 3,970 lb. One is the standard's
  floor and the other a maker's figure, so the type omits it rather than pick.
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
from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING, Any

from synthetic_ecommerce_data.core.drawing.model import Figure, arc
from synthetic_ecommerce_data.core.formats import LengthStyle
from synthetic_ecommerce_data.core.model import (
    keyword_attribute,
    length_attribute,
    numeric_attribute,
)
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn, _length_or
from synthetic_ecommerce_data.domains.industrial.newtypes import _weighted, _window
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

if TYPE_CHECKING:
    from synthetic_ecommerce_data.domains.industrial.generate import LineDraft

STANDARD = "ASME B29.1"

#: The machine key of this type's ``Pitch`` (see the module docstring).
PITCH_KEY = "chain_pitch"

#: Where the table below was read. ASME sells B29.1 and its text was NOT read;
#: every value is checked against published tables of the standard's series,
#: both retrieved 2026-10-07:
#:
#: * ``SOURCE_URL``, a chain distributor's size chart, prints pitch, roller
#:   width and roller diameter to three decimals of an inch for chains 25 to
#:   240. All 13 pitches, all 13 widths and all 11 roller diameters below are
#:   its single strand rows (its multiple strand tables repeat them).
#: * ``RULE_URL`` (revision 1363315204), whose table is headed "ASME/ANSI
#:   B29.1-2011 Roller chain standard sizes", prints the same 13 pitches, the
#:   same roller diameter for 10 of the 11 roller chains, and the same width
#:   for chains 25 to 80. It also states the numbering rule: the digits left of
#:   the last count eighths of an inch of pitch, and a last digit of 5 is a
#:   rollerless bushing chain. That is why 25 and 35 publish no roller
#:   diameter; both tables print their BUSHING diameters (0.130 and 0.200 in)
#:   in that column.
#:
#: The one disagreement: the 180 chain's roller is 1.406 in (45/32) on
#: ``SOURCE_URL``, in each of its five strand tables, and 1.460 in on
#: ``RULE_URL``. 45/32 is kept: it is the value the distributor sells to, it is
#: 5/8 of the pitch as the 200 and 240 chains' rollers are on both tables, and
#: 1.460 is 1.406 with two digits exchanged.
SOURCE_URL = "https://usarollerchain.com/pages/roller-chain-size-chart"
RULE_URL = "https://en.wikipedia.org/wiki/Roller_chain"

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
    AttrSpec("Style", "line"),
    AttrSpec("Material", "line"),
    AttrSpec("Finish", "line", 0.9),
    AttrSpec("Length", "line"),
    AttrSpec("Pitch", "sku"),
    AttrSpec("ANSI Number", "sku"),
    AttrSpec("Roller Dia.", "sku", 0.9, kind="length"),
    AttrSpec("Inside Width", "sku", 0.9, kind="length"),
)

#: Not ``table_provenance``: that says "read from the ASME B29.1 table", and
#: ASME's text was not read, only a distributor's chart of its dimensions.
PROVENANCE = (
    f"Pitch and Roller Dia. and Inside Width are {STANDARD} dimensions as "
    f"published in the size chart at {SOURCE_URL} (retrieved 2026-10-07)"
)


def ansi_number(number: str, strands: int) -> str:
    return number if strands == 1 else f"{number}-{strands}"


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: an offer, and a window of its chain numbers."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

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
        retired(keyword_attribute("Item", ITEM)),  # keeps the stream stable for #497
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
#: Proportions of pitch the drawing uses for what no record publishes: the
#: roller link (inner) plate's height, the pin link (outer) plate's, drawn
#: lower so the roller link plates behind it show, the plate's thickness and
#: the pin's radius.
_INNER_HEIGHT = 0.95
_OUTER_HEIGHT = 0.82
_PLATE_THICKNESS = 0.12
_PIN_RADIUS = 0.16
#: A rollerless chain's bushing, drawn where a roller would be.
_BUSHING = 0.52
#: The pitches drawn: a roller link, a pin link, a roller link.
_PITCHES = 3
#: Chords in a plate's half-round end. At the sheet's scale the end is at most
#: some 25 px in radius, so a chord of 30 degrees departs from the arc by less
#: than a pixel, and the six plate outlines are the drawing's largest paths.
_ARC = 6


def _plate(x: float, pitch: float, height: float) -> list[tuple[float, float]]:
    """A link plate seen from the side: one pitch long, round about each of its two pins."""
    radius = height / 2
    return [*arc((x, 0.0), radius, 90, 270, _ARC), *arc((x + pitch, 0.0), radius, -90, 90, _ARC)]


def chain(record: dict[str, str]) -> Drawn:
    """Side view of three links (plates, rollers, pins) above the top view of every strand."""
    pitch, ok_p = _length_or(record, "Pitch", 0.5)
    roller, ok_r = _length_or(record, "Roller Dia.", _BUSHING * pitch)
    width, ok_w = _length_or(record, "Inside Width", 0.5 * pitch)
    strands = _STRAND_COUNT.get(record.get("Style", ""), 1)
    source = "record" if ok_p and ok_r and ok_w else ("partial" if ok_p else "nominal")
    inner, outer = _INNER_HEIGHT * pitch, _OUTER_HEIGHT * pitch
    thick = _PLATE_THICKNESS * pitch
    fig = Figure(size_in=_PITCHES * pitch + inner)
    links = [(k * pitch, k % 2 == 1) for k in range(_PITCHES)]
    pins = [k * pitch for k in range(_PITCHES + 1)]
    # The pin link is the outer one, so it is drawn last, over the roller links' ends.
    for x, is_pin_link in sorted(links, key=lambda link: link[1]):
        fig.poly(_plate(x, pitch, outer if is_pin_link else inner))
    for x in pins:
        fig.disc((x, 0.0), roller / 2, "plain")
        fig.disc((x, 0.0), _PIN_RADIUS * pitch, "hole")
    # From above, per strand: pin link plates outermost, roller link plates
    # inside them, a roller between the roller link plates at every pin.
    # One strand is laid out once and repeated a strand's width further down,
    # every strand in ONE path: a triple strand chain's thirty rectangles, each
    # a styled element of its own, took the drawing past the size the sheet
    # allows. A plate from above is an edge view, so it is plain like the
    # rollers: its outline is wider than the plate is thick, and a hatch under
    # it would never show.
    top = inner / 2 + 0.3 * inner
    step = width + 4 * thick
    strand = []
    for x, is_pin_link in links:
        near = 0.0 if is_pin_link else thick
        far = step - thick if is_pin_link else step - 2 * thick
        half = (outer if is_pin_link else inner) / 2
        strand += [(x - half, y, x + pitch + half, y + thick) for y in (near, far)]
    for x in pins:
        strand.append((x - roller / 2, 2 * thick, x + roller / 2, 2 * thick + width))
    fig.bars(
        (
            (x0, top + s * step + y0, x1, top + s * step + y1)
            for s in range(strands)
            for x0, y0, x1, y1 in strand
        ),
        "plain",
    )
    fig.lines(((x, top), (x, top + strands * step)) for x in pins)
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


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """Every row is B29.1's standard series, whatever the material or strands."""
    return (STANDARD,)


SPEC = TypeSpec(
    "roller_chain",
    category=("Motion Control & Fluid Power", "Chain & Sprockets", "Roller Chains"),
    standards_family="motion",
    vocab=VOCAB,
    figure=chain,
    # The largest drawn: a 240 chain is 11.85 in wide, and 240-2 is 10.34 in tall.
    extent=(11.95, 10.45),
    make=build,
    share=0.016,
    price=PRICE,
    claims=claims,
    may_claim=frozenset({STANDARD}),
    key_attributes=("Pitch",),
    compat=False,
    use_lines=(
        "Runs on sprockets of the same ANSI chain number.",
        "Joins end to end with a connecting link of the same ANSI chain number.",
    ),
)
