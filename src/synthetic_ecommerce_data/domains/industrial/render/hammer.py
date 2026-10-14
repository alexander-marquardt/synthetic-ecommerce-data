"""Why a ball pein hammer gets no dimensioned drawing.

This module draws nothing. It exists because "there is no hammer renderer" and
"a hammer cannot be drawn from what a hammer record publishes" are different
statements, and the second one is the true one -- so it is written down here,
where anyone looking for the hammer renderer will find it, rather than left as
an absence for the next reader to rediscover.

A hammer record publishes four measurements::

    Head Weight     16 oz
    Overall Length  12-9/16"
    Face Dia.       0.9200"
    Handle Length   11-1/16"

Every view of a hammer needs an extent none of those gives.

* **Side elevation** -- the head across, the handle down -- needs the head's
  length along its own axis, face to pein. No attribute carries it, and it is
  the largest thing in the drawing: an eye reading that picture would be
  reading a number nothing in the record says.
* **Face view** -- looking down the head axis, so the head's length is hidden
  -- needs the width of the handle, which no attribute carries either.
* Deriving the head length from ``Head Weight`` would mean assuming a shape and
  a density. The countersink angle on a cap screw is derived, and legitimately:
  it follows from three published lengths by trigonometry alone. A head length
  from a weight follows from an assumption, which is a different thing.

So every hammer gets the undimensioned type drawing in :mod:`.fallback`, which
asserts that the product is a ball pein hammer -- true from the attribute names
it publishes -- and asserts nothing about its size. That is the correct
outcome for this product type, not a gap in the renderer.

If the vocabulary ever gains the missing extent -- a ``Head Length``, or a
``Face to Pein`` -- this is the module to fill in, and
:func:`geometry_from_record` is the function that would stop raising.
"""

from __future__ import annotations

from pathlib import Path

from synthetic_ecommerce_data.domains.industrial.render.attrs import UnsupportedFeatureError
from synthetic_ecommerce_data.domains.industrial.render.profiles import CARD, Profile

__all__ = ["NOT_DERIVABLE", "UnsupportedFeatureError", "geometry_from_record", "render"]

NOT_DERIVABLE = (
    "a hammer's head length is not published by any attribute, and every view "
    "of a hammer needs it or the handle width; the drawing would have to invent one"
)


def geometry_from_record(record: dict):
    """Always refuses. See the module docstring for what is missing and why."""
    raise UnsupportedFeatureError(f"record {record.get('sku', '?')!r}: {NOT_DERIVABLE}")


def render(record: dict, path: str | Path, profile: Profile = CARD) -> Path:
    """Refuses, which :func:`..render.render_record` turns into the type drawing.

    Refusing rather than quietly returning the type drawing itself is what
    keeps the batch report honest: every hammer is counted where it belongs,
    under a refusal with a reason, and not among the records drawn to scale.
    """
    del path, profile
    geometry_from_record(record)
    raise AssertionError("unreachable")  # pragma: no cover
