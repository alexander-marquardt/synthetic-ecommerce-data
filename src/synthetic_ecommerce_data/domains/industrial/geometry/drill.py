"""The numbers a drill's drawing is built from, read off a product record.

This module draws nothing. :func:`geometry_from_record` turns the attributes a
drill record publishes into a :class:`DrillGeometry`, or refuses with one of
:data:`~.attrs.REFUSALS` when the record cannot be drawn to scale. The text-free
SKU drawing in :mod:`..drawing.figures` reads it.

* The **point** is the included angle the record publishes as ``Point Angle``.
  A record whose point angle is absent -- or whose angle attribute carries a
  length unit, which this catalog reproduces at a measured rate -- is refused
  rather than drawn to a conventional 118 degrees.
* The **shank** needs ``Shank Dia.``. A jobber drill's shank is usually the
  nominal diameter, but "usually" is a convention, not this record, and drawing
  the shank at the drill size would put a diameter in the picture the record
  does not carry.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from synthetic_ecommerce_data.core.dimensions import (
    Length,
    parse_included_angle_degrees,
    parse_length,
)
from synthetic_ecommerce_data.domains.industrial.geometry.attrs import (
    ImpossibleGeometryError,
    require,
)


@dataclass(frozen=True)
class DrillGeometry:
    """Every number the drawing uses, and nothing else."""

    dia: Length
    shank_d: Length
    flute_len: Length
    oal: Length
    point_deg: float

    @property
    def max_d(self) -> float:
        return max(self.dia.inches, self.shank_d.inches)

    @property
    def point_height(self) -> float:
        """Axial height of the point cone, from its included angle and the diameter."""
        half = math.radians(self.point_deg / 2.0)
        return (self.dia.inches / 2.0) / math.tan(half)


def geometry_from_record(record: dict) -> DrillGeometry:
    geom = DrillGeometry(
        dia=parse_length(require(record, "Size")),
        shank_d=parse_length(require(record, "Shank Dia.")),
        flute_len=parse_length(require(record, "Flute Length")),
        oal=parse_length(require(record, "Overall Length")),
        point_deg=parse_included_angle_degrees(require(record, "Point Angle")),
    )
    if geom.flute_len.inches >= geom.oal.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: flute length {geom.flute_len.display()} is not "
            f"shorter than overall length {geom.oal.display()}; there is no shank to draw"
        )
    if geom.point_height >= geom.flute_len.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: a {geom.point_deg:g} degree point on "
            f"{geom.dia.display()} is taller than the flute length {geom.flute_len.display()}"
        )
    return geom
