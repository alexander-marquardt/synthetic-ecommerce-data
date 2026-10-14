"""Attribute vocabularies, one per product type, named the way the census names them.

A catalog's attribute names are not a schema somebody designed. They are the
union of what every supplier sent. Two properties of that are load-bearing for
a facet-extraction test bed:

* **One concept, one name, across types.** Material is ``Material`` on an end
  mill, a drill, a tap and a screw alike, because that is what the reference
  census does (160 of 496 records). An earlier version kept these vocabularies
  deliberately DISJOINT and minted ``Fastener Material``, ``Drill Bit
  Material`` and so on; that rule is retired, and :mod:`.names` is the gate that
  replaced it (elastic/prism-industrial-products#103). Types still differ in
  WHICH attributes they carry -- a hammer and a hex bolt share almost nothing --
  and facet discovery scoped to one type still returns that type's names.

* **Inconsistent spelling of one idea.** The measured corpus names the
  measurement-system attribute three ways -- ``Dimension Type`` (141),
  ``Measurement System`` (49), ``System of Measurement`` (22) -- with one
  shared value vocabulary. A field map has to absorb that, so the catalog has
  to contain it.

The one attribute that spans every type is ``Standards``, and it is
multi-valued. That shape -- several values under one name on one product -- is
the only one that exposes the ``reverse_nested`` counting trap, where a naive
nested aggregation counts *values* and reports more matches than there are
products.
"""

from __future__ import annotations

from dataclasses import dataclass

from synthetic_ecommerce_data.core.typespec import RegistryTable

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

#: The multi-valued attribute. WHICH standards a line may claim is a truth
#: table by what the line is (:mod:`.conformance`), not a pool per family.
STANDARDS_NAME = "Standards"

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
    _spec("Material", "line"),
    _spec("Finish", "line", 0.74),
    _spec("Number of Flutes", "line", kind="count"),
    _spec("Helix Angle", "line", 0.88, kind="angle"),
    _spec("Cutting Direction", "line", 0.90),
    _spec("Single End/Double End", "line", 0.74),
    _spec("Cutting Type", "line", 0.66),
    _spec("End Mill Application", "line", 0.38),
    _spec("Material Grade - Machining", "line", 0.42),
    _spec("Coolant Fed", "line", 0.24),
    _spec("List Number", "line", 0.58),
    _spec("Milling Dia.", "sku", kind="length"),
    _spec("Shank Dia.", "sku", kind="length"),
    _spec("Length of Cut", "sku", kind="length"),
    _spec("Overall Length", "sku", 0.92, kind="length"),
    # Census rate applied exactly once (by _apply_sparsity, the only gate
    # left on these two): 0.2727 and 0.4034 in by_family.end_mill of
    # 06_attribute_sparsity.json, rounded to two places as every other spec
    # in this table is. A second, builder-level gate at 0.18/0.22 used to
    # square this to ~3%/~5% (alexander-marquardt/synthetic-ecommerce-data#39).
    _spec("Neck Length", "sku", 0.27, kind="length"),
    _spec("Corner Radius", "sku", 0.40, kind="length"),
)

#: Jobber drills. Shares no dimension name with the end mill: a drill has a
#: Drill Size and a Flute Length where a mill has a Milling Dia. and a Length
#: of Cut, and the corpus keeps them apart.
_DRILL = (
    _spec("Item", "line"),
    _spec("Material", "line"),
    _spec("Point Type", "line", 0.78),
    _spec("Point Angle", "line", 0.82, kind="angle"),
    _spec("Finish", "line", 0.70),
    _spec("Shank Type", "line", 0.54),
    _spec("Cutting Direction", "line", 0.62),
    _spec("List Number", "line", 0.44),
    _spec("Size", "sku", kind="length"),
    _spec("Decimal Equivalent", "sku", 0.74, kind="length"),
    _spec("Flute Length", "sku", 0.86, kind="length"),
    _spec("Overall Length", "sku", 0.90, kind="length"),
    _spec("Shank Dia.", "sku", 0.68, kind="length"),
)

#: Spiral point taps.
_TAP = (
    _spec("Item", "line"),
    _spec("Tap Style", "line"),
    _spec("Material", "line", 0.80),
    _spec("Finish", "line", 0.66),
    _spec("Thread Direction", "line", 0.84),
    _spec("Thread Type", "line", 0.72),
    _spec("Tap Chamfer", "line", 0.58),
    _spec("Number of Flutes", "line", 0.76, kind="count"),
    _spec("Thread Size", "sku"),
    # A metric tap publishes Thread Pitch (mm), an inch tap Threads per Inch: one per
    # SKU, at the same presence, so the sparsity draw count is unchanged.
    _spec("Thread Pitch", "sku", 0.88),
    _spec("Threads per Inch", "sku", 0.88),
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
#: A shopper's ``5/16-18 x 3/4`` names the last of those on a socket, button
#: or low head. Binding it to ``Thread Length`` would return confidently wrong
#: results -- so the attribute exists rather than being approximated by a
#: neighbour.
#:
#: The COUNTERSUNK line does not carry it (:data:`_FLAT_HEAD_SCREW`). A flat
#: head is sold by its length OVER the head -- ISO 10642 and ASME B18.3 both
#: measure it that way -- so its "x 3/4" is its ``Length``, and the shank under
#: a toleranced cone is not a length any distributor lists. Publishing it as
#: length-less-head-height put 12.56mm and 1.3910" in the facet beside the
#: stocked lengths.
_SOCKET_SCREW = (
    _spec("Item", "line"),
    _spec("Type", "line"),
    _spec("Head Type", "line"),
    _spec("Drive Type", "line"),
    _spec("Material", "line"),
    _spec("Finish", "line", 0.82),
    _spec("Thread Direction", "line", 0.64),
    _spec("Thread Type", "line", 0.70),
    _spec("Rockwell Hardness", "line", 0.48),
    _spec("Meets/Exceeds", "line", 0.40),
    # Unconditional, as on the hex bolt: the shown price is a pack's (every
    # census socket screw is pack-sold, ``price.PACK_COUNTS``), so a record
    # that left the pack unstated would show a price for a quantity it does
    # not name (#65).
    _spec("Package Quantity", "line", kind="count"),
    _spec("Dia./Thread Size", "sku"),
    _spec("Length", "sku", kind="length"),
    _spec("Length under Head", "sku", kind="length"),
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

#: The countersunk line: every socket-screw attribute but ``Length under Head``.
_FLAT_HEAD_SCREW = tuple(spec for spec in _SOCKET_SCREW if spec.name != "Length under Head")

#: Hex bolts. Shares Dia./Thread Size and Length with the socket screw -- they
#: are both threaded fasteners and the corpus does share those -- but the head
#: is described by width across flats, not a head diameter.
#:
#: ``Grade`` and ``Fastener Finish`` are unconditional HERE and optional on
#: every other fastener, and the asymmetry is deliberate. The reference distributor's
#: parametric example is ``hex head cap screw: 7/16-14, 1-3/4" length under
#: head, grade 8 steel, zinc finish`` -- four attribute-value pairs, two of
#: them these -- and at 0.72 and 0.78 presence, drawn once per LINE, whether
#: their own query had an answer was decided by a sparsity roll. Measured: the
#: one line that carried the grade and the finish the query names lost the
#: finish to that roll, and the query resolved to nothing.
#:
#: This is the precedent issue #8 set for ``Length Under Head``: an attribute a
#: reference query BINDS to is published rather than approximated by a
#: neighbour or left to chance. It is also what the source does -- a
#: distributor's hex cap screw listing states the grade and the finish on
#: every row, because they are what the category is selected on.
_HEX_BOLT = (
    _spec("Item", "line"),
    _spec("Type", "line"),
    _spec("Head Type", "line"),
    _spec("Material", "line"),
    _spec("Finish", "line"),
    _spec("Grade", "line"),
    _spec("Thread Direction", "line", 0.60),
    _spec("Thread Type", "line", 0.66),
    # Unconditional: the shown price is a pack's (98.8% of census bolts are
    # pack-sold, ``price.PACK_COUNTS``), so every record states the pack it
    # prices (#65).
    _spec("Package Quantity", "line", kind="count"),
    _spec("Dia./Thread Size", "sku"),
    _spec("Length", "sku", kind="length"),
    _spec("Length under Head", "sku", kind="length"),
    _spec("Thread Length", "sku", kind="length"),
    _spec("Width Across Flats", "sku", kind="length"),
    _spec("Head Height", "sku", kind="length"),
    _spec("Head Dia.", "sku", kind="length"),
)

#: Flat washers. No thread, no head, no drive: four measurements and a
#: material. Nothing here appears on a cutting tool.
_WASHER = (
    _spec("Item", "line"),
    _spec("Type", "line"),
    _spec("Material", "line"),
    _spec("Finish", "line", 0.74),
    _spec("Size", "sku"),
    _spec("Inside Dia.", "sku", kind="length"),
    _spec("Outside Dia.", "sku", kind="length"),
    _spec("Thickness", "sku", kind="length"),
)

#: Ball pein hammers. Deliberately the most distant vocabulary in the catalog.
_HAMMER = (
    _spec("Item", "line"),
    _spec("Material", "line"),
    _spec("Handle Material", "line"),
    _spec("Handle Grip Material", "line", 0.62),
    _spec("Face Type", "line", 0.58),
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
    _spec("Shape", "line", 0.68),
    _spec("Mounting Type", "line", 0.58),
    _spec("Grit", "sku", kind="count"),
    _spec("Diameter", "sku", kind="length"),
    _spec("Arbor Hole", "sku", 0.90, kind="length"),
    _spec("Max. RPM", "sku", 0.82, kind="count"),
)

#: Hex nuts (elastic/prism-industrial-products#103). Generic names throughout:
#: a nut's height is ``Height`` and its style is ``Type`` -- the census has no
#: ``Nut Height`` worth following (2 records) and the gate refuses ``Nut ...``.
_NUT = (
    _spec("Item", "line"),
    _spec("Type", "line"),
    _spec("Material", "line"),
    _spec("Finish", "line", 0.9),
    _spec("Grade", "line", 0.9),
    _spec("Thread Type", "line", 0.8),
    _spec("Thread Direction", "line", 0.55),
    _spec("Package Quantity", "line", 0.85, kind="count"),
    _spec("Thread Size", "sku"),
    _spec("Width Across Flats", "sku", kind="length"),
    _spec("Height", "sku", 0.9, kind="length"),
)

#: Radial ball bearings. A product is one bearing number; its variants are the
#: closures, which is how the type really varies (6204, 6204-ZZ, 6204-2RS).
_BEARING = (
    _spec("Item", "line"),
    _spec("Type", "line"),
    _spec("Bearing Number", "line"),
    _spec("Series", "line", 0.8),
    _spec("Bore Dia.", "line", kind="length"),
    _spec("Outside Dia.", "line", kind="length"),
    _spec("Width", "line", kind="length"),
    _spec("Material", "line", 0.9),
    _spec("Cage Material", "line", 0.7),
    _spec("ABEC Rating", "line", 0.75),
    _spec("Row Type", "line", 0.6),
    _spec("Lubricant", "line", 0.5),
    _spec("Dynamic Load Capacity", "line", 0.8, kind="count"),
    _spec("Static Load Capacity", "line", 0.8, kind="count"),
    _spec("Closure Type", "sku"),
    _spec("Max. RPM", "sku", 0.85, kind="count"),
)

#: Depressed-center grinding wheels. A product is one diameter x thickness x
#: abrasive; its variants are the grits. Grit is a sizing-system value, not a
#: unit (ruling 2026-09-25: one vocabulary per sizing system).
_WHEEL = (
    _spec("Item", "line"),
    _spec("Type", "line"),
    _spec("Wheel Dia.", "line", kind="length"),
    _spec("Thickness", "line", kind="length"),
    _spec("Arbor Hole", "line", 0.95, kind="length"),
    _spec("Connector Type", "line", 0.6),
    _spec("Abrasive Material", "line"),
    _spec("Bond Type", "line", 0.7),
    _spec("Max. RPM", "line", 0.9, kind="count"),
    _spec("Application", "line", 0.6),
    _spec("Package Quantity", "line", 0.8, kind="count"),
    _spec("Grit", "sku", kind="count"),
    _spec("Grade", "line", 0.7),
)

#: Hex keys. A product is one brand's arm length, tip and finish; its variants
#: are sizes.
_HEX_KEY = (
    _spec("Item", "line"),
    _spec("Type", "line", 0.8),
    _spec("Tip Style", "line"),
    _spec("Material", "line", 0.85),
    _spec("Finish", "line", 0.8),
    _spec("Size", "sku", kind="length"),
    _spec("Overall Length", "sku", 0.9, kind="length"),
    _spec("Overall Width", "sku", 0.6, kind="length"),
)

#: Assortment kits: one SKU each, its contents a multi-valued field of its
#: own (``Sizes Included``) and its piece count a real number (``Number of
#: Pieces``, so pack wording may name it). Census names throughout.
_KIT = (
    _spec("Item", "line"),
    _spec("Type", "line"),
    _spec("Material", "line", 0.85),
    _spec("Finish", "line", 0.8),
    _spec("Container Type", "line", 0.8),
    _spec("Tip Style", "line"),
    _spec("Number of Pieces", "sku"),
    _spec("Sizes Included", "sku"),
)

_VOCAB: dict[str, tuple[AttrSpec, ...]] = {
    "end_mill_square": _END_MILL,
    "end_mill_ball": _END_MILL,
    "drill_jobber": _DRILL,
    "tap_spiral_point": _TAP,
    "screw_flat_head": _FLAT_HEAD_SCREW,
    "screw_button_head": _SOCKET_SCREW,
    "screw_low_head": _SOCKET_SCREW,
    "bolt_hex": _HEX_BOLT,
    "washer_flat": _WASHER,
    "hammer_ball_pein": _HAMMER,
    "abrasive_flap_disc": _FLAP_DISC,
    "nut_hex": _NUT,
    "bearing_radial_ball": _BEARING,
    "wheel_depressed_center": _WHEEL,
    "hex_key": _HEX_KEY,
    "kit_assortment": _KIT,
}
# A read registers the type modules first, so a type in its own module is listed.
VOCAB: RegistryTable[str, tuple[AttrSpec, ...]] = RegistryTable(_VOCAB)

#: Which pool of standards designations each type draws from.
_STANDARDS_FAMILY: dict[str, str] = {
    "end_mill_square": "cutting_tool",
    "end_mill_ball": "cutting_tool",
    "drill_jobber": "cutting_tool",
    "tap_spiral_point": "cutting_tool",
    "screw_flat_head": "fastener",
    "screw_button_head": "fastener",
    "screw_low_head": "fastener",
    "bolt_hex": "fastener",
    "washer_flat": "fastener",
    "hammer_ball_pein": "hand_tool",
    "abrasive_flap_disc": "abrasive",
    "nut_hex": "fastener",
    "bearing_radial_ball": "motion",
    "wheel_depressed_center": "abrasive",
    "hex_key": "hand_tool",
    "kit_assortment": "hand_tool",
}
# A read registers the type modules first, so a type in its own module is listed.
STANDARDS_FAMILY: RegistryTable[str, str] = RegistryTable(_STANDARDS_FAMILY)


def names_for(type_key: str) -> frozenset[str]:
    """Every attribute name a product of this type may publish."""
    return frozenset(spec.name for spec in VOCAB[type_key])


#: The measurement-system fact is one attribute under three spellings
#: (:data:`MEASUREMENT_SYSTEM_NAMES`). It is product-constant in every type, which also
#: settles ``dimension_type``, the facet key of the commonest spelling: a product is
#: metric or inch, never both, and a builder fixes one system per line.
MEASUREMENT_SYSTEM_SPELLINGS: frozenset[str] = frozenset(
    name for name, _ in MEASUREMENT_SYSTEM_NAMES
)


def product_constant_names(type_key: str) -> frozenset[str]:
    """The attribute names every SKU of one product of this type agrees on (gen#63).

    The type's ``line``-scope vocabulary (brand-level properties: material, finish,
    grade, head or point style, ...) and the measurement system. The rest of the
    vocabulary (``sku`` scope: the size ladder, pack quantity) is :func:`variant_names`.
    ``tests/test_product_constant.py`` holds the build to this declaration."""
    return frozenset(s.name for s in VOCAB[type_key] if s.scope == "line") | (
        MEASUREMENT_SYSTEM_SPELLINGS
    )


def variant_names(type_key: str) -> frozenset[str]:
    """The attribute names the SKUs of one product of this type may differ on."""
    return frozenset(s.name for s in VOCAB[type_key] if s.scope == "sku")
