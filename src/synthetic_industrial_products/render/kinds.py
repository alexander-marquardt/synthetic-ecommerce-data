"""What a record is, read off the attribute names it publishes.

Catalogs in this vertical do not publish a machine-readable product class; what
they publish is a set of attribute names, and those names are the signal. This
module is the one place that mapping lives, so the dimensioned renderer and the
undimensioned type drawing can never disagree about what a record is.

Every name used as a signal here is **unique to one product type's
vocabulary**. Names the corpus genuinely shares between types -- ``Overall
Length``, ``Thread Length``, ``Shank Dia.``, ``Item`` -- identify nothing and
are deliberately absent from the signatures below. ``tests/test_kinds.py``
asserts that against :mod:`..catalog.vocab`, so a vocabulary change that made a
signature ambiguous fails there rather than silently drawing a tap as a screw.

The one pair that shares a kind is the socket screw and the hex bolt: the
corpus shares ``Screw Head Type`` and ``Dia./Thread Size`` between them because
they are both threaded fasteners, and one renderer draws both.
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
            "End Mill Material",
            "End Mill Cutting Type",
            "End Mill Application",
            "Helix Angle",
            "Length of Cut",
        }
    ),
    FASTENER: frozenset(
        {
            "Screw Head Type",
            "Dia./Thread Size",
            "Screw Style",
            "Bolt Style",
            "Width Across Flats",
            "Drive Type",
        }
    ),
    DRILL: frozenset(
        {
            "Drill Size",
            "Drill Bit Material",
            "Drill Point Type",
            "Drill Bit Finish",
            "Drill Bit Direction",
            "Point Angle",
            "Decimal Equivalent",
            "Flute Length",
            "Shank Type",
        }
    ),
    TAP: frozenset(
        {
            "Tap Style",
            "Tap Material",
            "Tap Finish",
            "Chamfer Style",
            "Thread Size",
            "Pitch",
            "Square Size",
        }
    ),
    WASHER: frozenset(
        {
            "Washer Type",
            "Washer Size",
            "Inside Dia.",
            "Outside Dia.",
            "Thickness",
        }
    ),
    HAMMER: frozenset(
        {
            "Hammer Head Material",
            "Hammer Face Type",
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
            "Flap Disc Shape",
            "Mounting Type",
            "Grit",
            "Disc Dia.",
            "Arbor Hole Size",
            "Max. RPM",
        }
    ),
}

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
    """The kind key for ``record``, from the attribute names it carries."""
    names = set(record)
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
