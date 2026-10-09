"""What a record is: its product type when it says, its attribute names when it does not.

A generated record carries its ``product_type`` (the catalog knows it: the leaf
of its category IS its type), and that decides the drawing. Nothing about the
attribute NAMES is used for a generated record any more, because they no longer
identify a type: since elastic/prism-industrial-products#103 a concept is one
generic name across types (``Material``, ``Finish``, ``Size``), as the census
has it, and a drill's ``Size`` is a washer's ``Size`` too.

An OBSERVED record (:data:`..records.FIXTURES`) carries no type -- catalogs in
this vertical do not publish a machine-readable class -- so for those the
signatures below still read the names. Every name used as a signature is
unique to one kind; ``tests/test_kinds.py`` asserts that against the
vocabulary, so a vocabulary change that made a signature ambiguous fails there
rather than silently drawing a tap as a screw.
"""

from __future__ import annotations

#: Kind keys. These name what gets *drawn*, not what the catalog calls a
#: product type -- square and ball nose end mills are one drawing, and so are
#: socket screws and hex bolts.
END_MILL = "end_mill"
FASTENER = "fastener"
DRILL = "drill"
TAP = "tap"
WASHER = "washer"
HAMMER = "hammer"
FLAP_DISC = "flap_disc"

#: Attribute names that identify a kind. Presence of any one is enough; each
#: set contains at least one name the generator publishes unconditionally, so
#: sparsity cannot make a record unidentifiable.
SIGNATURES: dict[str, frozenset[str]] = {
    END_MILL: frozenset(
        {
            "Milling Dia.",
            "End Mill Style",
            "End Mill Application",
            "Helix Angle",
            "Length of Cut",
        }
    ),
    FASTENER: frozenset(
        {
            "Head Type",
            "Screw Head Type",
            "Dia./Thread Size",
            "Width Across Flats",
            "Drive Type",
        }
    ),
    DRILL: frozenset(
        {
            "Point Type",
            "Point Angle",
            "Decimal Equivalent",
            "Flute Length",
            "Shank Type",
        }
    ),
    TAP: frozenset(
        {
            "Tap Style",
            "Tap Chamfer",
            "Thread Size",
            "Thread Pitch",
            "Square Size",
        }
    ),
    WASHER: frozenset(
        {
            "Inside Dia.",
            "Outside Dia.",
            "Thickness",
        }
    ),
    HAMMER: frozenset(
        {
            "Face Type",
            "Handle Material",
            "Handle Grip Material",
            "Head Weight",
            "Face Dia.",
            "Handle Length",
        }
    ),
    FLAP_DISC: frozenset(
        {
            "Abrasive Material",
            "Backing Material",
            "Shape",
            "Mounting Type",
            "Grit",
            "Arbor Hole",
            "Max. RPM",
        }
    ),
}

#: The kind each catalog product type is drawn as. Several types share one: a
#: square and a ball nose end mill are one renderer, and so are the four hex
#: socket screw styles and the hex bolt.
TYPE_KIND: dict[str, str] = {
    "end_mill_square": END_MILL,
    "end_mill_ball": END_MILL,
    "drill_jobber": DRILL,
    "tap_spiral_point": TAP,
    "screw_socket_head": FASTENER,
    "screw_flat_head": FASTENER,
    "screw_button_head": FASTENER,
    "screw_low_head": FASTENER,
    "bolt_hex": FASTENER,
    "washer_flat": WASHER,
    "hammer_ball_pein": HAMMER,
    "abrasive_flap_disc": FLAP_DISC,
}

#: Keys a record carries that are not published attributes.
RESERVED_KEYS: frozenset[str] = frozenset({"sku", "SKU", "product_type"})

#: What to call each kind when the record carries no ``Item``.
KIND_LABELS: dict[str, str] = {
    END_MILL: "End Mill",
    FASTENER: "Threaded Fastener",
    DRILL: "Twist Drill",
    TAP: "Tap",
    WASHER: "Flat Washer",
    HAMMER: "Ball Pein Hammer",
    FLAP_DISC: "Flap Disc",
}


class UnknownProductError(ValueError):
    """No renderer knows how to draw this record."""


class AmbiguousProductError(ValueError):
    """The record's attribute names identify more than one kind.

    A record that looks like two things is not a record either drawing can be
    trusted on, so it is refused rather than resolved by whichever signature
    happened to be checked first.
    """


def classify(record: dict) -> str:
    """The kind key for ``record``: its product type if it carries one, else its names."""
    product_type = record.get("product_type")
    if product_type is not None:
        try:
            return TYPE_KIND[product_type]
        except KeyError as exc:
            raise UnknownProductError(
                f"record {record.get('sku', '?')!r} is a {product_type!r}, which nothing draws"
            ) from exc
    names = set(record) - RESERVED_KEYS
    matched = sorted(kind for kind, signature in SIGNATURES.items() if names & signature)
    if len(matched) == 1:
        return matched[0]
    if matched:
        raise AmbiguousProductError(
            f"record {record.get('sku', '?')!r} carries attributes of "
            f"{' and '.join(matched)}; no one drawing is true of it"
        )
    raise UnknownProductError(
        f"record {record.get('sku', '?')!r} carries no attribute that identifies what it is"
    )
