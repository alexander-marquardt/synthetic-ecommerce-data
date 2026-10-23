"""The numbers a flat washer's drawing is built from, read off a product record.

This module draws nothing; the text-free SKU drawing in :mod:`..drawing.figures`
reads :func:`geometry_from_record`.

A washer is the one product in this catalog whose drawing needs nothing the
record does not carry: ``Inside Dia.``, ``Outside Dia.`` and ``Thickness`` come
from the washer standard the line is built to and are published on every SKU.
So a washer is refused only through a value that cannot be read or a pair that
contradicts itself, never through sparsity.
"""

from __future__ import annotations

from dataclasses import dataclass

from synthetic_ecommerce_data.core.dimensions import Length, parse_length
from synthetic_ecommerce_data.domains.industrial.geometry.attrs import (
    ImpossibleGeometryError,
    require,
)


@dataclass(frozen=True)
class WasherGeometry:
    """Every number the drawing uses, and nothing else."""

    inside_d: Length
    outside_d: Length
    thickness: Length


def geometry_from_record(record: dict) -> WasherGeometry:
    geom = WasherGeometry(
        inside_d=parse_length(require(record, "Inside Dia.")),
        outside_d=parse_length(require(record, "Outside Dia.")),
        thickness=parse_length(require(record, "Thickness")),
    )
    if geom.inside_d.inches >= geom.outside_d.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: inside diameter {geom.inside_d.display()} is not "
            f"smaller than outside diameter {geom.outside_d.display()}; there is no washer left"
        )
    return geom
