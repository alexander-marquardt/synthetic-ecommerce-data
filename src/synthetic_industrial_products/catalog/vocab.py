"""Attribute vocabularies, one per product type, deliberately disjoint.

A catalog's attribute names are not a schema somebody designed. They are the
union of what every supplier sent, so the same idea arrives under several
names and two unrelated product types share almost nothing. Both properties
are load-bearing for a facet-extraction test bed:

* **Disjointness.** A hex bolt and a ball pein hammer have one measurement in
  common and no vocabulary in common. A facet discovery pass scoped to one
  product type must come back with that type's names and nothing else, and it
  can only be shown to do that if the vocabularies really are disjoint.

* **Inconsistent spelling of one idea.** The measured corpus names the
  measurement-system attribute three ways -- ``Dimension Type`` (141),
  ``Measurement System`` (49), ``System of Measurement`` (22) -- with one
  shared value vocabulary. A field map has to absorb that, so the catalog has
  to contain it. The same applies to material and finish, which arrive as
  ``Material - Machining``, ``Fastener Finish``, ``Abrasive Material`` and
  ``Handle Material`` depending on who supplied the row.

The one attribute that spans every type is ``Standards``, and it is
multi-valued. That shape -- several values under one name on one product -- is
the only one that exposes the ``reverse_nested`` counting trap, where a naive
nested aggregation counts *values* and reports more matches than there are
products.
"""

from __future__ import annotations

from dataclasses import dataclass

#: The three verbatim spellings of the measurement-system attribute, with the
#: weights measured in 08_measurement_system.json (141 / 49 / 22 of 212).
MEASUREMENT_SYSTEM_NAMES: tuple[tuple[str, float], ...] = (
    ("Dimension Type", 0.665),
    ("Measurement System", 0.231),
    ("System of Measurement", 0.104),
)

#: Its value vocabulary, shared across all three spellings. Weights from the
#: same file: 151 / 35 / 19 / 5 of 212 (the two "Wire" values are a different
#: product family and are not reproduced here).
MEASUREMENT_SYSTEM_VALUES: tuple[tuple[str, float], ...] = (
    ("Fractional Inch", 0.717),
    ("Metric", 0.166),
    ("Inch", 0.090),
    ("Decimal Inch", 0.024),
)

#: Presence rate of the measurement-system attribute: 212 of 496 records.
MEASUREMENT_SYSTEM_PRESENCE = 0.4274

#: The multi-valued attribute, and the pools it draws from per type family.
#: Real standards designations; a product carries 1-3 of them.
STANDARDS_NAME = "Standards"

STANDARDS_POOL: dict[str, tuple[str, ...]] = {
    "cutting_tool": (
        "ANSI B94.19",
        "ANSI B212.15",
        "DIN 338",
        "DIN 6527",
        "ISO 1641",
        "RoHS 2011/65/EU",
        "REACH",
    ),
    "fastener": (
        "ASME B18.3",
        "ASME B18.2.1",
        "ISO 4762",
        "ISO 10642",
        "ISO 4014",
        "ISO 7089",
        "DIN 912",
        "DIN 125A",
        "ASTM A574",
        "SAE J429",
        "RoHS 2011/65/EU",
    ),
    "hand_tool": (
        "ASME B107.400",
        "ANSI B107.5",
        "GS Mark",
        "RoHS 2011/65/EU",
    ),
    "abrasive": (
        "ANSI B7.1",
        "oSa Certified",
        "EN 13743",
        "RoHS 2011/65/EU",
    ),
}

#: Presence rate of the Standards attribute, from 06_attribute_sparsity.json
#: (43 of 496 records carry it). Raised for this catalog, because the facet it
#: feeds is one of the things under test and a 9% fill rate leaves too little
#: signal; the deviation is recorded rather than hidden.
STANDARDS_PRESENCE = 0.55


@dataclass(frozen=True)
class AttrSpec:
    """One attribute name a product type may publish.

    ``scope`` is the data model's spine: ``line`` attributes are constant over
    a manufacturer's product line and live on the parent, ``sku`` attributes
    vary between the individual purchasable items and live on the children.
    """

    name: str
    #: "line" or "sku".
    scope: str
    #: Probability the attribute is present at all. Sparsity is measured, not
    #: assumed: real records are ragged and a fully-populated one is a tell.
    presence: float = 1.0
    #: "keyword", "length", "count", "angle", "weight", "multi".
    kind: str = "keyword"


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


#: End mills. The richest vocabulary in the corpus: end_mill records average
#: 16.98 attributes against a corpus mean of 13.12.
_END_MILL = (
    _spec("Item", "line"),
    _spec("End Mill Style", "line"),
    # On EVERY end mill, not at the 0.62 the reference corpus measured. That
    # corpus's end mills could leave material unstated because their category
    # trail named it; this catalog's trail no longer does (material is not a
    # path level -- see ``taxonomy``), so a line without this attribute would
    # carry its material nowhere. The real catalog's own ``End Mill Material``
    # facet covers practically every end mill (59,358 values against 56,178
    # ``Square End Mills`` in its ``square end mill`` listing,
    # elastic/prism-industrial-products ``data/facet_vocabulary.json``).
    # Presence 1.0 still draws its sparsity roll, so the random stream is
    # unchanged by this.
    _spec("End Mill Material", "line"),
    _spec("Finish - Machining", "line", 0.74),
    _spec("Number of Flutes", "line", kind="count"),
    _spec("Helix Angle", "line", 0.88, kind="angle"),
    _spec("Cutting Direction", "line", 0.90),
    _spec("Single End/Double End", "line", 0.74),
    _spec("End Mill Cutting Type", "line", 0.66),
    _spec("End Mill Application", "line", 0.38),
    _spec("Material Grade - Machining", "line", 0.42),
    _spec("Coolant Fed", "line", 0.24),
    _spec("List Number", "line", 0.58),
    _spec("Milling Dia.", "sku", kind="length"),
    _spec("Shank Dia.", "sku", kind="length"),
    _spec("Length of Cut", "sku", kind="length"),
    _spec("Overall Length", "sku", 0.92, kind="length"),
    _spec("Neck Length", "sku", 0.18, kind="length"),
    _spec("Corner Radius", "sku", 0.22, kind="length"),
)

#: Jobber drills. Shares no dimension name with the end mill: a drill has a
#: Drill Size and a Flute Length where a mill has a Milling Dia. and a Length
#: of Cut, and the corpus keeps them apart.
_DRILL = (
    _spec("Item", "line"),
    _spec("Drill Bit Material", "line"),
    _spec("Drill Point Type", "line", 0.78),
    _spec("Point Angle", "line", 0.82, kind="angle"),
    _spec("Drill Bit Finish", "line", 0.70),
    _spec("Shank Type", "line", 0.54),
    _spec("Drill Bit Direction", "line", 0.62),
    _spec("List Number", "line", 0.44),
    _spec("Drill Size", "sku", kind="length"),
    _spec("Decimal Equivalent", "sku", 0.74, kind="length"),
    _spec("Flute Length", "sku", 0.86, kind="length"),
    _spec("Overall Length", "sku", 0.90, kind="length"),
    _spec("Shank Dia.", "sku", 0.68, kind="length"),
)

#: Spiral point taps.
_TAP = (
    _spec("Item", "line"),
    _spec("Tap Style", "line"),
    _spec("Tap Material", "line", 0.80),
    _spec("Tap Finish", "line", 0.66),
    _spec("Thread Direction", "line", 0.84),
    _spec("Thread Type", "line", 0.72),
    _spec("Chamfer Style", "line", 0.58),
    _spec("Number of Flutes", "line", 0.76, kind="count"),
    _spec("Thread Size", "sku"),
    _spec("Pitch", "sku", 0.88),
    _spec("Overall Length", "sku", 0.84, kind="length"),
    _spec("Thread Length", "sku", 0.70, kind="length"),
    _spec("Shank Dia.", "sku", 0.74, kind="length"),
    _spec("Square Size", "sku", 0.46, kind="length"),
)

#: Socket head cap screws, in all four head styles the catalog carries. The
#: renderer reads Screw Head Type, Dia./Thread Size, Length, Thread Length,
#: Head Dia. and Head Height, so those are unconditional here: a record that
#: cannot be drawn is a record whose image would have to be faked.
#:
#: ``Length Under Head`` is a THIRD length beside the other two, and the three
#: are genuinely three measurements:
#:
#: * ``Length`` is the screw's nominal length, which a countersunk screw
#:   measures OVER its head and every other style measures under it;
#: * ``Thread Length`` is how much of the shank carries thread;
#: * ``Length Under Head`` is the whole shank, head excluded.
#:
#: A shopper's ``5/16-18 x 3/4`` names the last of those. Binding it to
#: ``Thread Length`` would return confidently wrong results, and on a
#: countersunk screw binding it to ``Length`` is wrong by a head height -- so
#: the attribute exists rather than being approximated by a neighbour.
_SOCKET_SCREW = (
    _spec("Item", "line"),
    _spec("Screw Style", "line"),
    _spec("Screw Head Type", "line"),
    _spec("Drive Type", "line"),
    _spec("Fastener Material", "line"),
    _spec("Fastener Finish", "line", 0.82),
    _spec("Thread Direction", "line", 0.64),
    _spec("Thread Type", "line", 0.70),
    _spec("Rockwell Hardness", "line", 0.48),
    _spec("Meets/Exceeds", "line", 0.40),
    _spec("Dia./Thread Size", "sku"),
    _spec("Length", "sku", kind="length"),
    _spec("Length Under Head", "sku", kind="length"),
    _spec("Thread Length", "sku", kind="length"),
    _spec("Head Dia.", "sku", kind="length"),
    _spec("Head Height", "sku", kind="length"),
    # UNCONDITIONAL, and the reason is entailment rather than taste. Every
    # one of these records publishes ``Drive Type`` on 100% of rows -- it says
    # the screw HAS a hex socket -- so a record omitting the size of that
    # socket contradicts its own neighbouring attribute. Measured at 0.86 it
    # did exactly that on 20 of the 24 M12x1.75 socket screws
    # (elastic/prism#9284). Unlike ``Pitch`` on a tap, the size is not
    # derivable from what is published: "Hex Socket" does not say 10mm.
    #
    # Same precedent as ``Grade`` and ``Fastener Finish`` on the hex bolt
    # below -- an attribute a shopper's query BINDS to is published, not left
    # to a sparsity roll.
    _spec("Drive Size", "sku", kind="length"),
)

#: Hex bolts. Shares Dia./Thread Size and Length with the socket screw -- they
#: are both threaded fasteners and the corpus does share those -- but the head
#: is described by width across flats, not a head diameter.
#:
#: ``Grade`` and ``Fastener Finish`` are unconditional HERE and optional on
#: every other fastener, and the asymmetry is deliberate. The customer's
#: parametric example is ``hex head cap screw: 7/16-14, 1-3/4" length under
#: head, grade 8 steel, zinc finish`` -- four attribute-value pairs, two of
#: them these -- and at 0.72 and 0.78 presence, drawn once per LINE, whether
#: their own query had an answer was decided by a sparsity roll. Measured: the
#: one line that carried the grade and the finish the query names lost the
#: finish to that roll, and the query resolved to nothing.
#:
#: This is the precedent issue #8 set for ``Length Under Head``: an attribute a
#: customer's query BINDS to is published rather than approximated by a
#: neighbour or left to chance. It is also what the source does -- a
#: distributor's hex cap screw listing states the grade and the finish on
#: every row, because they are what the category is selected on.
_HEX_BOLT = (
    _spec("Item", "line"),
    _spec("Bolt Style", "line"),
    _spec("Screw Head Type", "line"),
    _spec("Fastener Material", "line"),
    _spec("Fastener Finish", "line"),
    _spec("Grade", "line"),
    _spec("Thread Direction", "line", 0.60),
    _spec("Thread Type", "line", 0.66),
    _spec("Dia./Thread Size", "sku"),
    _spec("Length", "sku", kind="length"),
    _spec("Length Under Head", "sku", kind="length"),
    _spec("Thread Length", "sku", kind="length"),
    _spec("Width Across Flats", "sku", kind="length"),
    _spec("Head Height", "sku", kind="length"),
    _spec("Head Dia.", "sku", kind="length"),
)

#: Flat washers. No thread, no head, no drive: four measurements and a
#: material. Nothing here appears on a cutting tool.
_WASHER = (
    _spec("Item", "line"),
    _spec("Washer Type", "line"),
    _spec("Fastener Material", "line"),
    _spec("Fastener Finish", "line", 0.74),
    _spec("Washer Size", "sku"),
    _spec("Inside Dia.", "sku", kind="length"),
    _spec("Outside Dia.", "sku", kind="length"),
    _spec("Thickness", "sku", kind="length"),
)

#: Ball pein hammers. Deliberately the most distant vocabulary in the catalog.
_HAMMER = (
    _spec("Item", "line"),
    _spec("Hammer Head Material", "line"),
    _spec("Handle Material", "line"),
    _spec("Handle Grip Material", "line", 0.62),
    _spec("Hammer Face Type", "line", 0.58),
    _spec("Head Weight", "sku", kind="weight"),
    _spec("Overall Length", "sku", 0.88, kind="length"),
    _spec("Face Dia.", "sku", 0.72, kind="length"),
    _spec("Handle Length", "sku", 0.64, kind="length"),
)

#: Flap discs.
_FLAP_DISC = (
    _spec("Item", "line"),
    _spec("Abrasive Material", "line"),
    _spec("Backing Material", "line", 0.76),
    _spec("Flap Disc Shape", "line", 0.68),
    _spec("Mounting Type", "line", 0.58),
    _spec("Grit", "sku", kind="count"),
    _spec("Disc Dia.", "sku", kind="length"),
    _spec("Arbor Hole Size", "sku", 0.90, kind="length"),
    _spec("Max. RPM", "sku", 0.82, kind="count"),
)

VOCAB: dict[str, tuple[AttrSpec, ...]] = {
    "end_mill_square": _END_MILL,
    "end_mill_ball": _END_MILL,
    "drill_jobber": _DRILL,
    "tap_spiral_point": _TAP,
    "screw_socket_head": _SOCKET_SCREW,
    "screw_flat_head": _SOCKET_SCREW,
    "screw_button_head": _SOCKET_SCREW,
    "screw_low_head": _SOCKET_SCREW,
    "bolt_hex": _HEX_BOLT,
    "washer_flat": _WASHER,
    "hammer_ball_pein": _HAMMER,
    "abrasive_flap_disc": _FLAP_DISC,
}

#: Which pool of standards designations each type draws from.
STANDARDS_FAMILY: dict[str, str] = {
    "end_mill_square": "cutting_tool",
    "end_mill_ball": "cutting_tool",
    "drill_jobber": "cutting_tool",
    "tap_spiral_point": "cutting_tool",
    "screw_socket_head": "fastener",
    "screw_flat_head": "fastener",
    "screw_button_head": "fastener",
    "screw_low_head": "fastener",
    "bolt_hex": "fastener",
    "washer_flat": "fastener",
    "hammer_ball_pein": "hand_tool",
    "abrasive_flap_disc": "abrasive",
}

#: Attribute names every type is allowed to share, because the corpus shares
#: them. Everything else must be unique to its type; test_vocab enforces it.
SHARED_NAMES: frozenset[str] = frozenset(
    {
        "Item",
        STANDARDS_NAME,
        "Overall Length",
        "Shank Dia.",
        "Number of Flutes",
        "List Number",
        "Thread Direction",
        "Thread Type",
        "Thread Length",
        "Length",
        "Length Under Head",
        "Dia./Thread Size",
        "Fastener Material",
        "Fastener Finish",
        "Screw Head Type",
        "Head Dia.",
        "Head Height",
        *(name for name, _ in MEASUREMENT_SYSTEM_NAMES),
    }
)


def names_for(type_key: str) -> frozenset[str]:
    """Every attribute name a product of this type may publish."""
    return frozenset(spec.name for spec in VOCAB[type_key])
