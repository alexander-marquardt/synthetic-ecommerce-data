"""Reading attributes off a record, and the refusals that reading them produces.

Every dimensioned drawing refuses the same three ways -- an attribute the
drawing needs is absent, a published value cannot be read, or the values
contradict each other -- and the caller that routes a refusal to the
undimensioned type drawing has to be able to catch all of them. Defining them
once, here, is what makes :data:`REFUSALS` a set that cannot drift out of date
as drawings are added.
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.dimensions import DimensionParseError


class MissingAttributeError(KeyError):
    """The record does not carry an attribute the drawing needs."""


class ImpossibleGeometryError(ValueError):
    """The record's own dimensions contradict each other."""


class UnsupportedFeatureError(ValueError):
    """A feature the record names is not one the attributes determine."""


#: Every way a dimensioned drawing says "not from this record". A caller that
#: catches these is catching a refusal; anything else is a bug in a drawing
#: and must not be quietly turned into a type drawing.
REFUSALS: tuple[type[Exception], ...] = (
    MissingAttributeError,
    ImpossibleGeometryError,
    UnsupportedFeatureError,
    DimensionParseError,
)


def require_any(record: dict, *keys: str) -> str:
    """The value of the first of ``keys`` the record publishes, or a refusal.

    For one concept published under several names -- the generator writes the
    census's generic ``Head Type``, while an observed record may say ``Screw
    Head Type``. A drawing reads what the record publishes, as it comes.
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
