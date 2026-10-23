"""The numbers an end mill's drawing is built from, read off a product record.

This module draws nothing; the text-free SKU drawing in :mod:`..drawing.figures`
reads :func:`geometry_from_record`.

``End Mill Style`` decides the cutting end and is **required**. A ball nose and
a square end are different tools and the record says which; a drawing that
showed a square end on a record reading ``Ball Nose`` would contradict its own
data. The attribute is published on essentially every end mill in the reference
corpus -- 132 records carry it against 129 carrying ``Milling Dia.`` -- so
requiring it asks for nothing a real record withholds.

``Cutting Direction`` decides which way the flutes lean and
``Single End/Double End`` decides whether there is a second cutting end. Both
are followed when published; when the record is silent the usual form is used.

``Corner Radius`` rounds the corners of a square end. On a ball nose there are
no corners to round, so a record publishing both is refused rather than drawn
with one of them ignored.

The flutes
----------
A helix of angle ``h`` on a cylinder of diameter ``d`` advances
``lead = pi * d / tan(h)`` per turn. Both the lead and the spacing of the
edges come from :attr:`EndMillGeometry.helix_lead`, which is the only place the
formula appears.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from synthetic_ecommerce_data.core.dimensions import (
    Length,
    parse_angle_degrees,
    parse_count,
    parse_length,
)
from synthetic_ecommerce_data.domains.industrial.geometry.attrs import (
    ImpossibleGeometryError,
    UnsupportedFeatureError,
    require,
)

#: ``End Mill Style`` values and the cutting end each one means.
END_STYLES: dict[str, str] = {
    "square": "square",
    "square end": "square",
    "ball": "ball",
    "ball end": "ball",
    "ball nose": "ball",
}


#: ``Cutting Direction`` values and which way the flutes lean. A right-hand
#: helix rises to the right in this view; a left-hand one rises to the left.
HANDS: dict[str, int] = {"right hand": 1, "left hand": -1}


@dataclass(frozen=True)
class EndMillGeometry:
    """Every number the drawing uses, and nothing else."""

    cut_d: Length
    shank_d: Length
    loc: Length
    oal: Length
    flutes: int
    helix_deg: float
    #: "square" or "ball", from the required ``End Mill Style``.
    style: str = "square"
    #: +1 right hand, -1 left hand. ``hand_published`` says whether the record
    #: chose it or the drawing defaulted.
    hand: int = 1
    hand_published: bool = True
    double_end: bool = False
    ends_published: bool = True
    #: Corner radius on a square end, when the record publishes one.
    corner_radius: Length | None = None

    @property
    def max_d(self) -> float:
        return max(self.cut_d.inches, self.shank_d.inches)

    @property
    def shoulder(self) -> float:
        """Height of the flute/shank boundary above the cutting tip, in inches."""
        return self.loc.inches

    @property
    def ball_radius(self) -> float:
        """Radius of the ball nose, which is half the cutting diameter."""
        return self.cut_d.inches / 2.0

    @property
    def helix_lead(self) -> float:
        """Axial advance of one flute per full turn, in inches.

        A helix of angle ``h`` on a cylinder of diameter ``d`` unrolls to a
        straight line making angle ``h`` with the axis over a width equal to
        the circumference, so one turn advances ``pi * d / tan(h)``.
        """
        return math.pi * self.cut_d.inches / math.tan(math.radians(self.helix_deg))

    @property
    def axial_flute_pitch(self) -> float:
        """Axial distance between successive flute edges on the visible face.

        With ``n`` flutes an edge crosses the visible face every ``1/n`` of a
        lead. Drawing the flutes at any other spacing would make helix angle
        and flute count decorative.
        """
        return self.helix_lead / self.flutes

    @property
    def face_rise(self) -> float:
        """Axial rise of ONE flute across the face the drawing shows.

        The visible face is half a turn -- the flute enters at one silhouette
        edge and leaves at the other -- so the rise is half a lead, not a whole
        one and not the ``d / tan(h)`` that the unrolled *diameter* would give.
        That last one was what this drew before: shorter by a factor of pi/2,
        which renders a published 30 degree helix at a measured 42.2 degrees.
        """
        return self.helix_lead / 2.0


#: The cutting end of each end mill type, for a record that states no ``End Mill Style``
#: (the attribute repeated the product type and is no longer published, #497).
STYLE_OF_TYPE = {"end_mill_square": "Square", "end_mill_ball": "Ball Nose"}


def _style_of(record: dict) -> str:
    stated = record.get("End Mill Style") or STYLE_OF_TYPE.get(str(record.get("product_type")))
    published = str(stated if stated else require(record, "End Mill Style")).strip().lower()
    try:
        return END_STYLES[published]
    except KeyError as exc:
        raise UnsupportedFeatureError(
            f"record {record.get('sku', '?')!r}: end mill style "
            f"{published!r} is not a cutting end the drawing knows how to build"
        ) from exc


def geometry_from_record(record: dict) -> EndMillGeometry:
    style = _style_of(record)
    hand_raw = str(record.get("Cutting Direction", "")).strip().lower()
    if hand_raw and hand_raw not in HANDS:
        raise UnsupportedFeatureError(
            f"record {record.get('sku', '?')!r}: cutting direction {hand_raw!r} is neither hand"
        )
    ends_raw = str(record.get("Single End/Double End", "")).strip().lower()
    if ends_raw and ends_raw not in ("single end", "double end"):
        raise UnsupportedFeatureError(
            f"record {record.get('sku', '?')!r}: {ends_raw!r} is not a number of cutting ends"
        )
    radius_raw = record.get("Corner Radius")
    geom = EndMillGeometry(
        cut_d=parse_length(require(record, "Milling Dia.")),
        shank_d=parse_length(require(record, "Shank Dia.")),
        loc=parse_length(require(record, "Length of Cut")),
        oal=parse_length(require(record, "Overall Length")),
        flutes=parse_count(require(record, "Number of Flutes")),
        helix_deg=parse_angle_degrees(require(record, "Helix Angle")),
        style=style,
        hand=HANDS.get(hand_raw, 1),
        hand_published=bool(hand_raw),
        double_end=ends_raw == "double end",
        ends_published=bool(ends_raw),
        corner_radius=parse_length(radius_raw) if radius_raw else None,
    )
    cutting = geom.loc.inches * (2 if geom.double_end else 1)
    if cutting >= geom.oal.inches:
        ends = "two lengths of cut" if geom.double_end else "length of cut"
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: {ends} {geom.loc.display()} is not "
            f"shorter than overall length {geom.oal.display()}; there is no shank to draw"
        )
    if geom.style == "ball" and geom.corner_radius is not None:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: a ball nose has no corners, and this record "
            f"publishes a corner radius of {geom.corner_radius.display()}"
        )
    if geom.corner_radius is not None and geom.corner_radius.inches > geom.cut_d.inches / 2:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: a corner radius of "
            f"{geom.corner_radius.display()} does not fit on a {geom.cut_d.display()} cutter"
        )
    if geom.style == "ball" and geom.ball_radius >= geom.loc.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: a ball nose on {geom.cut_d.display()} is deeper "
            f"than the length of cut {geom.loc.display()}"
        )
    return geom
