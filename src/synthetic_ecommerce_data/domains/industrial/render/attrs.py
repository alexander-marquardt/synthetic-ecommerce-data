"""Reading attributes off a record, and the refusals that reading them produces.

Every dimensioned renderer refuses the same three ways -- an attribute the
drawing needs is absent, a published value cannot be read, or the values
contradict each other -- and the caller that routes a refusal to the
undimensioned type drawing has to be able to catch all of them. Defining them
once, here, is what makes :data:`REFUSALS` a set that cannot drift out of date
as renderers are added.
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.dimensions import DimensionParseError
from synthetic_ecommerce_data.domains.industrial.render import canvas as cv


def drawing_title(record: dict, fallback: str) -> str:
    """What a drawing is headed with: the label of the record's product type.

    The record used to carry an ``Item`` attribute for this; it repeated the product
    type and is no longer published (#497), so the type's own label heads the drawing.
    """
    from synthetic_ecommerce_data.domains.industrial.type_labels import (  # noqa: PLC0415
        PRODUCT_TYPE_LABELS,
    )

    return str(PRODUCT_TYPE_LABELS.get(str(record.get("product_type", "")), fallback))


class MissingAttributeError(KeyError):
    """The record does not carry an attribute the drawing needs."""


class ImpossibleGeometryError(ValueError):
    """The record's own dimensions contradict each other."""


class UnsupportedFeatureError(ValueError):
    """A feature the record names is not one the attributes determine."""


#: Every way a dimensioned renderer says "not from this record". A caller that
#: catches these is catching a refusal; anything else is a bug in a renderer
#: and must not be quietly turned into a type drawing.
REFUSALS: tuple[type[Exception], ...] = (
    MissingAttributeError,
    ImpossibleGeometryError,
    UnsupportedFeatureError,
    DimensionParseError,
)


#: Attributes no drawing shows, and the reason each one cannot be shown.
#:
#: This is the escape hatch for
#: ``tests/test_derivation.py::test_every_published_attribute_reaches_the_drawing``,
#: which takes every attribute a record publishes, changes it, and requires the
#: output to move. An attribute that is neither read nor named here fails that
#: test -- which is how ``End Mill Style`` being published on every end mill
#: and read by nothing would have been caught, and was not, by 39 mutations
#: with no zeros.
#:
#: The test checks the declarations in BOTH directions: a name in here whose
#: value DOES move a drawing fails too, so these cannot quietly go stale.
NOT_DRAWN: dict[str, str] = {
    # The measurement-system attribute, under all three spellings the corpus
    # uses for it.
    "Dimension Type": (
        "says which system the record's values are in. Every value on the "
        "drawing is printed exactly as the record published it, units and all, "
        "so there is nothing for this to add -- and the catalog publishes it "
        "contradicting its own units at a measured rate, which is a fact about "
        "the data rather than about the picture"
    ),
    "Measurement System": (
        "the same attribute as Dimension Type under a second spelling; see the reason there"
    ),
    "System of Measurement": (
        "the same attribute as Dimension Type under a third spelling; see the reason there"
    ),
    "Standards": (
        "conformance claims -- ISO 4762, RoHS, oSa Certified. A standard a "
        "product is built to is not a shape or a size, so a drawing of the "
        "product has nothing to show for it"
    ),
    "List Number": (
        "the supplier's own catalogue code for the line. An identifier, not a "
        "property of the object, and the drawing already carries the SKU"
    ),
    "Application": (
        "what the tool is FOR -- roughing, finishing, or both. A use, not a "
        "form: two mills that differ only in this are the same drawing"
    ),
    "Material Grade - Machining": (
        "a performance grade -- general purpose against high performance. "
        "Nothing about it is visible in an outline"
    ),
    "Units per Pack": (
        "how many pieces the line is sold in. A commercial quantity: a pack "
        "of 25 bolts and a pack of 100 hold the same bolt, and the figure "
        "draws one piece"
    ),
}


def require_any(record: dict, *keys: str) -> str:
    """The value of the first of ``keys`` the record publishes, or a refusal.

    For one concept published under several names -- the generator writes the
    census's generic ``Head Type``, while an observed record may say ``Screw
    Head Type``. A renderer reads what the record publishes, as it comes.
    """
    for key in keys:
        if key in record:
            return record[key]
    raise MissingAttributeError(
        f"record {record.get('sku', '?')!r} has none of {list(keys)!r}; the drawing needs one"
    )


def require(record: dict, key: str) -> str:
    """The value of ``key``, or a refusal naming the record and the attribute."""
    try:
        return record[key]
    except KeyError as exc:
        raise MissingAttributeError(
            f"record {record.get('sku', '?')!r} has no {key!r}; the drawing needs it"
        ) from exc


#: Characters a spec value may run to before it is set smaller. Measured from
#: the table's width: past this a value collides with its own label.
LONG_VALUE = 16

#: The value to pass for an attribute the record does not carry but the drawing
#: had to take a position on anyway -- which way a helix leans, how many
#: cutting ends a mill has. The row is kept, and set in muted italic so it does
#: not read as a measurement, because "the record is silent and the drawing
#: chose" is a thing the reader is entitled to know.
NOT_PUBLISHED = "not published"

#: Rows a table can hold at the default spacing before it runs off the sheet.
ROOMY_ROWS = 10


def spec_table(fig, rows, y: float = 0.44, step: float = 0.042) -> float:
    """The detail profile's attribute table, and the y it stopped at.

    Values are written as the record published them. A row whose value is
    empty is dropped rather than shown blank: the record does not carry it, and
    a blank row reads as a measurement of nothing.

    A long value is set smaller rather than truncated or wrapped. The table is
    a fixed width and some of this catalog's values are not short -- ``18-8
    Stainless Steel`` is twenty characters -- and a value that has run into its
    own label is a value the reader cannot check against the record.
    """
    kept = [(name, str(value)) for name, value in rows if value]
    if len(kept) > ROOMY_ROWS:
        # A long table is set tighter rather than cut short. Dropping rows to
        # fit would mean the sheet silently stopped being the whole record.
        scale = ROOMY_ROWS / len(kept)
        step *= scale
        size = cv.FS_SPEC * max(scale, 0.72)
    else:
        size = cv.FS_SPEC
    for name, text in kept:
        fig.text(0.62, y, name, fontsize=size, color=cv.MUTED)
        silent = text == NOT_PUBLISHED
        fig.text(
            0.955,
            y,
            text,
            fontsize=size if len(text) <= LONG_VALUE else size * 0.80,
            color=cv.MUTED if silent else cv.INK,
            fontweight="normal" if silent else "bold",
            style="italic" if silent else "normal",
            ha="right",
        )
        y -= step
    return y


def provenance_note(fig) -> None:
    """The footer every dimensioned detail drawing carries."""
    fig.text(
        0.04,
        0.018,
        "drawn from this record's attribute values",
        fontsize=cv.FS_FOOT,
        color=cv.MUTED,
        style="italic",
    )
