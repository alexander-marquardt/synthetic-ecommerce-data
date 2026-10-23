"""The numbers a screw or bolt's drawing is built from, read off a product record.

This module draws nothing; the text-free SKU drawing in :mod:`..drawing.figures`
reads :func:`geometry_from_record` and :func:`dome_profile`.

Everything comes out of the record's own attributes. Two consequences are worth
stating, because the alternative in both cases would be to put a number in the
picture that the record does not contain:

* The countersink angle is **computed** from ``Head Dia.``, ``Head Height`` and
  the thread's major diameter, not taken from a standard's table. For the
  reference record that arithmetic lands on an 82 degree included angle, which
  is what the inch flat-head standard specifies -- a check on the attributes,
  not a value borrowed from elsewhere.
* A **button head's dome** is the spherical cap that ``Head Dia.`` and
  ``Head Height`` describe -- the chord and the rise determine exactly one
  sphere -- so it is computed the same way the countersink angle is, rather
  than being a curve that looked about right.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from synthetic_ecommerce_data.core.dimensions import Length, Thread, parse_length, parse_thread
from synthetic_ecommerce_data.domains.industrial.geometry.attrs import (
    UnsupportedFeatureError,
    require,
    require_any,
)

#: Head styles the drawing can build from ``Head Dia.`` and ``Head Height``
#: alone. ``countersunk`` heads sink into the work, so the published length is
#: measured over the head; every other style is measured under it.
COUNTERSUNK = {"flat", "flat head", "countersunk", "flat countersunk"}


CYLINDRICAL = {
    "socket",
    "socket cap",
    "cylindrical",
    "cheese",
    "socket head",
    "hex",
    # A low head socket cap screw is the same cylinder at about half the
    # height. The difference between it and a full socket head is entirely in
    # the two dimensions the record publishes, so it is drawn from those and
    # needs no outline of its own: a head profile invented to make the two look
    # different would be asserting something no attribute says, while these
    # dimensions already draw the squat head DIN 7984 describes.
    "low socket",
    "low head",
    "low socket head",
}


#: Head styles whose profile is a shallow DOME rather than a cylinder.
#:
#: A button head is not a socket head with different numbers -- it is a
#: different shape, and the shape is implied by the two published dimensions:
#: a spherical cap of chord ``Head Dia.`` and rise ``Head Height``. Drawing one
#: as a cylinder is the ``Screw Head Type`` defect over again, where socket and
#: hex produced the same picture and 524 hex bolts were drawn with round heads.
DOMED = {"button", "button head", "dome", "domed"}


#: Head styles whose end view is a HEXAGON and not a circle.
#:
#: The elevation of a hex head across its flats really is the same rectangle a
#: cylindrical head gives, which is why both live in ``CYLINDRICAL``. The end
#: view is not: it is six flats, and drawing a circle there puts a round head
#: on 524 hex bolts. The attribute-coverage sweep caught that -- ``Screw Head
#: Type`` moved nothing in the drawing of a socket screw, because socket and
#: hex produced the same picture.
HEX_HEADED = {"hex", "hex head", "hexagon"}


class UnsupportedHeadError(UnsupportedFeatureError):
    """The head style is not one the drawing can derive from the attributes."""


@dataclass(frozen=True)
class FastenerGeometry:
    thread: Thread
    length: Length
    thread_length: Length
    head_dia: Length
    head_height: Length
    head_style: str
    drive_type: str
    drive_size: Length | None
    width_across_flats: Length | None = None

    @property
    def countersunk(self) -> bool:
        return self.head_style.strip().lower() in COUNTERSUNK

    @property
    def domed(self) -> bool:
        return self.head_style.strip().lower() in DOMED

    @property
    def hex_headed(self) -> bool:
        return self.head_style.strip().lower() in HEX_HEADED

    @property
    def across_flats(self) -> float:
        """Width across the flats of a hex head, in inches.

        ``Width Across Flats`` when the record publishes it -- it is the name
        the corpus uses for a bolt -- and ``Head Dia.`` otherwise, which for a
        hex head IS the across-flats dimension and is what the elevation is
        already drawn to.
        """
        return (self.width_across_flats or self.head_dia).inches

    @property
    def total_height(self) -> float:
        """Tip to top of head. Countersunk length is measured over the head."""
        if self.countersunk:
            return self.length.inches
        return self.length.inches + self.head_height.inches

    @property
    def shank_length(self) -> float:
        return self.total_height - self.head_height.inches

    @property
    def length_seat(self) -> float:
        """Where the published ``Length`` stops, measured up from the tip.

        A countersunk screw's length is measured OVER the head, because the
        head sinks into the work; every other style's is measured UNDER it.
        ``total_height`` has always known that, and the dimension LINE did not:
        it ran tip to top on both, so a socket cap screw's drawing labelled a
        span of length-plus-head-height with the length. In both cases the span
        the label belongs against is simply the published length.
        """
        return self.length.inches

    @property
    def length_witness_radius(self) -> float:
        """What the length dimension's upper witness line ties to."""
        return (self.head_dia if self.countersunk else self.thread.major).inches / 2

    @property
    def threaded_length(self) -> float:
        """Thread run, clamped to the shank the head leaves behind.

        A fully threaded countersunk screw publishes a thread length equal to
        its nominal length, which is longer than the shank because the length
        is measured over the head. Clamping draws the thread running right up
        under the head, which is what such a screw is.
        """
        return min(self.thread_length.inches, self.shank_length)

    @property
    def countersink_included_angle(self) -> float:
        """Included angle of the countersink, in degrees, from the dimensions."""
        if not self.countersunk:
            raise UnsupportedHeadError(
                f"head style {self.head_style!r} is not countersunk; it has no cone angle"
            )
        half_rise = (self.head_dia.inches - self.thread.major.inches) / 2
        return 2 * math.degrees(math.atan2(half_rise, self.head_height.inches))

    @property
    def max_width(self) -> float:
        return max(self.head_dia.inches, self.thread.major.inches)


def geometry_from_record(record: dict) -> FastenerGeometry:
    head_style = str(require_any(record, "Head Type", "Screw Head Type")).strip()
    key = head_style.lower()
    if key not in COUNTERSUNK and key not in CYLINDRICAL and key not in DOMED:
        raise UnsupportedHeadError(
            f"head style {head_style!r} cannot be built from Head Dia. and Head Height "
            "alone; its profile is not implied by any attribute on the record"
        )
    drive_size_raw = record.get("Drive Size")
    flats_raw = record.get("Width Across Flats")
    geom = FastenerGeometry(
        thread=parse_thread(require(record, "Dia./Thread Size")),
        length=parse_length(require(record, "Length")),
        thread_length=parse_length(require(record, "Thread Length")),
        head_dia=parse_length(require(record, "Head Dia.")),
        head_height=parse_length(require(record, "Head Height")),
        head_style=head_style,
        drive_type=str(record.get("Drive Type", "")).strip(),
        drive_size=parse_length(drive_size_raw) if drive_size_raw else None,
        width_across_flats=parse_length(flats_raw) if flats_raw else None,
    )
    return geom


#: Points the dome's arc is drawn with. Enough that the curve reads as a
#: curve at drawing size and no more; the shape is the arc, not the
#: sampling.
_DOME_STEPS = 48


def dome_profile(r_head: float, rise: float, seat: float) -> list[tuple[float, float]]:
    """The arc of a spherical cap of chord ``2 * r_head`` and rise ``rise``.

    Both numbers come off the record -- ``Head Dia.`` and ``Head Height`` --
    and they determine the cap completely: a sphere of radius
    ``(r^2 + h^2) / 2h`` is the only one through the head's rim and its crown.
    Nothing here is chosen to look right.

    The rim angle is taken with ``atan2`` and not with ``asin(r / radius)``.
    The two agree for every button head in any of these standards, because a
    button head is a shallow cap and its rise is well under its radius -- and
    they disagree exactly when it is not: a rise GREATER than the radius puts
    the sphere's centre above the seat, and ``asin`` then returns the acute
    angle, which draws the MINOR arc. That arc is a bulge whose ends are not
    on the rim at all, so the drawing quietly stops being of the head the
    record describes, and it gets SHORTER as the published head height grows.
    Found by planting a taller dome and watching the drawing shrink.
    """
    radius = (r_head * r_head + rise * rise) / (2 * rise)
    centre = seat + rise - radius
    half_angle = math.atan2(r_head, radius - rise)
    return [
        (
            radius * math.sin(-half_angle + 2 * half_angle * k / _DOME_STEPS),
            centre + radius * math.cos(-half_angle + 2 * half_angle * k / _DOME_STEPS),
        )
        for k in range(_DOME_STEPS + 1)
    ]
