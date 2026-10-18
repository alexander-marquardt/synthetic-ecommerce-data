"""The shapes the builders hand the post-pass, and the tables both read.

A type builder returns a :class:`LineDraft` of :class:`ChildDraft` children;
the post-pass (:mod:`.finishing`, :mod:`.defects`, :mod:`.titles`) turns it
into a product line. They live apart from :mod:`.generate` so that the three
post-pass modules and the generator import them without importing each other
(split from generate.py, elastic/prism-industrial-products#266). ``generate``
re-exports every name here, where the type modules have always found them.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from synthetic_ecommerce_data.core.model import Attribute

#: The attribute a type's titles must name when its variant axis is not its
#: size: the census title core is "<Item>, <key dim>, ...". Measured on the
#: first 100K build, bearing titles were 0.01 distinct and carried no size at
#: all ("Radial Ball Bearing, Double Seal Closure Type, Chrome Steel", 452
#: times); wheels 0.06 and flap discs 0.22 named only their grit.
KEY_DIMENSIONS: dict[str, tuple[str, ...]] = {
    # A bearing is named by its number AND its bore: the bore is what a
    # shopper fits it to (the review of the 100K catalog, 2026-09-29).
    "bearing_radial_ball": ("Bearing Number", "Bore Dia."),
    "wheel_depressed_center": ("Wheel Dia.",),
    "abrasive_flap_disc": ("Diameter",),
    # Not a dimension, but it names what the screw IS, so it leads. Last in
    # the title, the value's trailing "Point" reads as a cut "Point Type".
    "set_screws_hex_socket": ("Point Type",),
}


#: Lines in a row a (type, brand) may draft without making a SKU before its
#: spec space counts as spent. See ``Generator._finish_line``.
MAX_MISSES = 20


def _weighted(rng: random.Random, table) -> object:
    """Pick from a ``((value, weight), ...)`` table."""
    values = [value for value, _ in table]
    weights = [weight for _, weight in table]
    return rng.choices(values, weights=weights, k=1)[0]


#: Keys that hold ONE unit each: a restated value would put the other unit
#: under them, so the unit-mixing defect leaves them alone.
UNIT_SPLIT_KEYS = frozenset({"diameter", "dowel_dia_in", "dowel_dia_mm"})


@dataclass
class ChildDraft:
    """A child before the shared post-pass touches it."""

    attrs: list[Attribute] = field(default_factory=list)
    #: The dimension a title would name -- the one a shopper reads as "the"
    #: size of the product.
    primary: Attribute | None = None
    #: Other dimensions on the same child, by the class name the reference
    #: statistics use: other_length, length_of_cut, neck, flute.
    secondary: dict[str, Attribute] = field(default_factory=dict)
    #: A second dimension the title names, labelled, right after the primary in
    #: every title style: for a child the primary alone does not tell from a
    #: sibling (a rectangular bar beside the square bar of its width). The
    #: collision repair cannot be left to find it: it accepts a title that
    #: names a value the SKU's siblings do not publish, and a unit defect on
    #: the sibling's width makes the shared width such a value on both.
    also: Attribute | None = None
    system: str = "in"
    #: A deliberately awkward single variant that carries NO variant-scope
    #: attribute: everything it publishes is on its product. A grouped view
    #: must render a selector with zero axes (elastic/prism-industrial-products#103).
    zero_axis: bool = False


@dataclass
class LineDraft:
    item: str
    brand: str
    series: str
    category: tuple[str, ...]
    line_attrs: list[Attribute] = field(default_factory=list)
    children: list[ChildDraft] = field(default_factory=list)
    provenance: str = ""
    #: Extra title segments the type wants, before the dimension segment.
    descriptors: list[tuple[str, str]] = field(default_factory=list)
    #: Set by ``_finish_line``; the builders need not.
    type_key: str = ""
    #: The dimensional standard EVERY child's dimensions were read from, when
    #: the line's dimensions are not already a standard's by provenance (the
    #: hex nut: :func:`.newtypes.nut_row`). Empty when no one standard fits.
    standard: str = ""
    #: The title is the item alone: no brand, no qualifier, no segments (the incidental-word
    #: text-match decoy of :mod:`.hammers`, whose short indexed title outranks real hits).
    bare_title: bool = False


#: The word a terse title uses for an end mill's end shape, by its
#: ``End Mill Style``: ``SGL Sq End`` / ``SGL Ball End``.
END_SHAPE_WORD: dict[str, str] = {"Square": "Sq", "Ball Nose": "Ball"}
#: The cutting end of each end mill type. ``End Mill Style`` said the same thing and is
#: no longer published (#497), so the type key decides.
END_SHAPE_OF_TYPE: dict[str, str] = {"end_mill_square": "Square", "end_mill_ball": "Ball Nose"}
