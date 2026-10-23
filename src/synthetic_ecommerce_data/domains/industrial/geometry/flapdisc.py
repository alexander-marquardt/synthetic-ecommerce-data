"""The numbers a flap disc's drawing is built from, read off a product record.

This module draws nothing; the text-free SKU drawing in :mod:`..drawing.figures`
reads :func:`geometry_from_record`.

* The **disc diameter** and the **arbor hole** are published, and are the two
  numbers the drawing is built from.
* There is **no edge view**. A flap disc record publishes ``Flap Disc Shape``
  -- Type 27 flat or Type 29 conical -- but no thickness and no cone angle, so
  an edge view would be a profile drawn to numbers the record does not carry.
"""

from __future__ import annotations

from dataclasses import dataclass

from synthetic_ecommerce_data.core.dimensions import Length, parse_length
from synthetic_ecommerce_data.domains.industrial.geometry.attrs import (
    ImpossibleGeometryError,
    require,
)


@dataclass(frozen=True)
class FlapDiscGeometry:
    """Every number the drawing uses, and nothing else."""

    disc_d: Length
    arbor_d: Length


def geometry_from_record(record: dict) -> FlapDiscGeometry:
    geom = FlapDiscGeometry(
        disc_d=parse_length(require(record, "Diameter")),
        arbor_d=parse_length(require(record, "Arbor Hole")),
    )
    if geom.arbor_d.inches >= geom.disc_d.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: an arbor hole of {geom.arbor_d.display()} is not "
            f"smaller than the {geom.disc_d.display()} disc it is in"
        )
    return geom
