"""Dimensioned cap-screw drawing, derived entirely from a product record.

What is drawn and what is not
-----------------------------
Everything in the drawing comes out of the record's own attributes. Two
consequences are worth stating, because the alternative in both cases would be
to put a number in the picture that the record does not contain:

* The countersink angle is **computed** from ``Head Dia.``, ``Head Height`` and
  the thread's major diameter, not taken from a standard's table. For the
  reference record that arithmetic lands on an 82 degree included angle, which
  is what the inch flat-head standard specifies -- a check on the attributes,
  not a value borrowed from elsewhere.
* A **button head's dome** is the spherical cap that ``Head Dia.`` and
  ``Head Height`` describe -- the chord and the rise determine exactly one
  sphere -- so it is computed the same way the countersink angle is, rather
  than being a curve that looked about right.
* The **depth** of a socket drive is not derivable from any published
  attribute, so it is not drawn. The socket appears as the opening it makes in
  the head's top face (side view) and as its true across-flats shape (end
  view). Drawing a recess to some invented depth would be the one line in the
  picture that the data could not defend.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from matplotlib.patches import Circle, Polygon, Rectangle

from synthetic_ecommerce_data.core.dimensions import Length, Thread, parse_length, parse_thread
from synthetic_ecommerce_data.domains.industrial.render import canvas as cv
from synthetic_ecommerce_data.domains.industrial.render import forms
from synthetic_ecommerce_data.domains.industrial.render.attrs import (
    ImpossibleGeometryError,
    MissingAttributeError,
    UnsupportedFeatureError,
    drawing_title,
    provenance_note,
    require,
    require_any,
    spec_table,
)
from synthetic_ecommerce_data.domains.industrial.render.profiles import CARD, Profile

#: Re-exported for the same reason as in :mod:`.endmill`.
__all__ = [
    "FastenerGeometry",
    "ImpossibleGeometryError",
    "MissingAttributeError",
    "UnsupportedHeadError",
    "build",
    "dome_profile",
    "drive_mouth_width",
    "drive_outline",
    "geometry_from_record",
    "render",
]

FILL_V = 0.78
FILL_H = 0.42

#: Gap between the elevation and the end view above it, in head diameters.
END_VIEW_GAP = 0.30

#: Head styles this renderer can build from ``Head Dia.`` and ``Head Height``
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
    """The head style is not one this renderer can derive from the attributes."""


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
#: curve at the card's 600 px width and no more; the shape is the arc, not the
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


def _head_outline(geom: FastenerGeometry, y_tip: float) -> list[tuple[float, float]]:
    top = y_tip + geom.total_height
    seat = top - geom.head_height.inches
    r_head = geom.head_dia.inches / 2
    r_shank = geom.thread.major.inches / 2
    if geom.countersunk:
        return [(-r_head, top), (-r_shank, seat), (r_shank, seat), (r_head, top)]
    if geom.domed:
        return dome_profile(r_head, geom.head_height.inches, seat)
    return [(-r_head, seat), (-r_head, top), (r_head, top), (r_head, seat)]


def _draw_body(ax, geom: FastenerGeometry, y_tip: float) -> None:
    r_shank = geom.thread.major.inches / 2

    ax.add_patch(
        Rectangle(
            (-r_shank, y_tip),
            r_shank * 2,
            geom.shank_length,
            fc=cv.SHANK_FILL,
            ec="none",
            zorder=1,
        )
    )
    # Thread roots, then the outline of the unthreaded run, then the form.
    forms.thread_roots(ax, minor_in=geom.thread.minor_in, y_from=y_tip, length=geom.threaded_length)
    for sign in (-1, 1):
        ax.plot(
            [sign * r_shank, sign * r_shank],
            [y_tip + geom.threaded_length, y_tip + geom.shank_length],
            color=cv.INK,
            lw=cv.LW_BODY,
            zorder=3,
        )
    ax.plot(
        [-r_shank, r_shank],
        [y_tip, y_tip],
        color=cv.INK,
        lw=cv.LW_BODY,
        zorder=3,
    )
    forms.draw_thread(
        ax,
        major_in=geom.thread.major.inches,
        minor_in=geom.thread.minor_in,
        pitch_in=geom.thread.pitch_in,
        y_from=y_tip,
        length=geom.threaded_length,
    )

    ax.add_patch(
        Polygon(
            _head_outline(geom, y_tip),
            closed=False,
            fill=True,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=5,
        )
    )

    # Top face, interrupted by the drive opening. The socket's depth is not a
    # published attribute, so only its mouth is drawn.
    top = y_tip + geom.total_height
    r_head = geom.head_dia.inches / 2
    mouth = drive_mouth_width(geom)
    half_drive = (mouth / 2) if mouth else 0.0
    # A dome has no flat top face to draw across: its outline already runs from
    # rim to crown, and a chord struck at the crown would be an edge the part
    # does not have.
    if not geom.domed:
        if half_drive > 0:
            for sign in (-1, 1):
                ax.plot(
                    [sign * r_head, sign * half_drive],
                    [top, top],
                    color=cv.INK,
                    lw=cv.LW_BODY,
                    zorder=6,
                )
        else:
            ax.plot([-r_head, r_head], [top, top], color=cv.INK, lw=cv.LW_BODY, zorder=6)

    if geom.hex_headed:
        # The two edges between the three faces an across-flats view shows.
        for sign in (-1, 1):
            # A hexagon seen across its flats shows three faces, and the two
            # edges between them project to half a side length from the axis:
            # s/2 = W/(2*sqrt(3)) = r/sqrt(3).
            ax.plot(
                [sign * r_head / math.sqrt(3), sign * r_head / math.sqrt(3)],
                [top - geom.head_height.inches, top],
                color=cv.INK,
                lw=cv.LW_BODY * 0.7,
                zorder=6,
            )


def drive_outline(geom: FastenerGeometry, centre: tuple[float, float] = (0.0, 0.0)):
    """The drive recess as seen along the axis, or ``None`` if not determined.

    A single across-size determines a hex socket, a square socket and a slot.
    It does not determine a Torx or a cross recess -- those are lobed shapes
    whose profile no attribute on the record carries -- so for those the drawing
    shows no recess rather than a plausible-looking wrong one.
    """
    if geom.drive_size is None:
        return None
    cx, cy = centre
    across = geom.drive_size.inches
    kind = geom.drive_type.lower()
    if "hex" in kind:
        r = (across / 2) / math.cos(math.radians(30))
        return [
            (
                cx + r * math.cos(math.radians(30 + 60 * k)),
                cy + r * math.sin(math.radians(30 + 60 * k)),
            )
            for k in range(6)
        ]
    if "square" in kind:
        h = across / 2
        return [(cx - h, cy - h), (cx - h, cy + h), (cx + h, cy + h), (cx + h, cy - h)]
    if "slot" in kind:
        h = across / 2
        r = geom.head_dia.inches / 2
        return [(cx - r, cy - h), (cx - r, cy + h), (cx + r, cy + h), (cx + r, cy - h)]
    return None


def drive_mouth_width(geom: FastenerGeometry) -> float | None:
    """Width of the opening the drive makes in the head's top face, or ``None``.

    ``None`` means the same thing it means for :func:`drive_outline`: the record
    does not determine the shape, so the top face is drawn unbroken.
    """
    if drive_outline(geom) is None:
        return None
    assert geom.drive_size is not None
    return geom.drive_size.inches


def _draw_end_view(ax, geom: FastenerGeometry, centre: tuple[float, float] = (0.0, 0.0)) -> None:
    """The head seen along the axis: head diameter, and the drive's true shape."""
    cx, cy = centre
    r_head = geom.head_dia.inches / 2
    if geom.hex_headed:
        # Six flats, to the published across-flats dimension. A circle here
        # would be a round head on a product the record calls hexagonal.
        r_corner = (geom.across_flats / 2) / math.cos(math.radians(30))
        ax.add_patch(
            Polygon(
                [
                    (
                        cx + r_corner * math.cos(math.radians(60 * k)),
                        cy + r_corner * math.sin(math.radians(60 * k)),
                    )
                    for k in range(6)
                ],
                closed=True,
                fc=cv.BODY_FILL,
                ec=cv.INK,
                lw=cv.LW_BODY,
                zorder=3,
            )
        )
    else:
        ax.add_patch(Circle((cx, cy), r_head, fc=cv.BODY_FILL, ec=cv.INK, lw=cv.LW_BODY, zorder=3))
    ax.add_patch(
        Circle(
            (cx, cy),
            geom.thread.major.inches / 2,
            fill=False,
            ec=cv.MUTED,
            lw=cv.LW_HIDDEN,
            ls=(0, (5, 4)),
            zorder=4,
        )
    )
    outline = drive_outline(geom, centre)
    if outline is not None:
        ax.add_patch(
            Polygon(
                outline,
                closed=True,
                fc=cv.SHANK_FILL,
                ec=cv.INK,
                lw=cv.LW_BODY * 0.8,
                zorder=5,
            )
        )


def _frame_height(fig, rect, geom: FastenerGeometry) -> float:
    box_ratio = cv.frame_width(fig, rect, 1.0)
    return max(geom.total_height / FILL_V, (geom.max_width / FILL_H) / box_ratio)


def _card_content_height(geom: FastenerGeometry) -> float:
    """Elevation plus the end view stacked above it, with the gap between."""
    return geom.total_height + END_VIEW_GAP * geom.head_dia.inches + geom.head_dia.inches


def _render_card(record: dict, geom: FastenerGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.0, 0.0, 1.0, 1.0)
    content_h = _card_content_height(geom)
    box_ratio = cv.frame_width(fig, rect, 1.0)
    frame_h = max(content_h / FILL_V, (geom.max_width / FILL_H) / box_ratio)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    # A screw is squat where an end mill is long, so the portrait card has
    # vertical room the elevation does not need. It goes to the end view, which
    # is the only place the drive type is visible as a shape.
    y_tip = -content_h / 2
    _draw_body(ax, geom, y_tip)

    ax_end_centre = (
        y_tip + geom.total_height + END_VIEW_GAP * geom.head_dia.inches + geom.head_dia.inches / 2
    )
    _draw_end_view(ax, geom, centre=(0.0, ax_end_centre))

    overhang = frame_w * 0.05
    gap = frame_w * 0.035
    cv.diameter_callout(
        ax,
        y_tip + geom.threaded_length * 0.45,
        geom.thread.major.inches,
        geom.thread.designation,
        "thread",
        side=1,
        overhang=overhang,
        gap=gap,
    )
    x_len = -frame_w * 0.28
    cv.length_dimension(
        ax, x_len, y_tip, y_tip + geom.length_seat, geom.length.display(), fontsize=cv.FS_CALLOUT
    )
    cv.witness(ax, x_len, -geom.thread.major.inches / 2, y_tip)
    cv.witness(ax, x_len, -geom.length_witness_radius, y_tip + geom.length_seat)
    ax.text(
        x_len - frame_w * 0.075,
        y_tip + geom.length_seat / 2,
        "length",
        rotation=90,
        ha="center",
        va="center",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )
    ax.text(
        0,
        -frame_h * 0.47,
        str(record.get("sku", "")),
        ha="center",
        va="bottom",
        color=cv.MUTED,
        fontsize=cv.FS_FOOT,
    )
    return fig, ax


def _render_detail(record: dict, geom: FastenerGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.04, 0.05, 0.50, 0.82)
    frame_h = _frame_height(fig, rect, geom)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    y_tip = -geom.total_height / 2
    _draw_body(ax, geom, y_tip)

    overhang = frame_w * 0.04
    gap = frame_w * 0.03
    top = y_tip + geom.total_height

    x_len = -frame_w * 0.40
    cv.length_dimension(ax, x_len, y_tip, y_tip + geom.length_seat, geom.length.display())
    cv.witness(ax, x_len, -geom.length_witness_radius, y_tip + geom.length_seat)
    cv.witness(ax, x_len, -geom.thread.major.inches / 2, y_tip)
    ax.text(
        x_len - frame_w * 0.055,
        y_tip + geom.length_seat / 2,
        "length",
        rotation=90,
        ha="center",
        va="center",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    x_thr = -frame_w * 0.25
    cv.length_dimension(
        ax, x_thr, y_tip, y_tip + geom.threaded_length, geom.thread_length.display()
    )
    cv.witness(ax, x_thr, -geom.thread.major.inches / 2, y_tip + geom.threaded_length)
    ax.text(
        x_thr - frame_w * 0.055,
        y_tip + geom.threaded_length / 2,
        "thread length",
        rotation=90,
        ha="center",
        va="center",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    cv.diameter_callout(
        ax,
        y_tip + geom.threaded_length * 0.5,
        geom.thread.major.inches,
        geom.thread.designation,
        "thread",
        side=1,
        overhang=overhang,
        gap=gap,
    )
    cv.diameter_callout(
        ax,
        top + frame_h * 0.06,
        geom.head_dia.inches,
        f"Ø{geom.head_dia.display()}",
        "head dia.",
        side=1,
        overhang=overhang,
        gap=gap,
    )

    end_rect = (0.62, 0.55, 0.30, 0.30)
    ax_end = cv.frame_axes(fig, end_rect, geom.head_dia.inches * 2.0)
    _draw_end_view(ax_end, geom)
    label = f"end view · {geom.drive_type.lower()}" if geom.drive_type else "end view"
    if geom.hex_headed:
        label = "end view · hex head"
    if geom.drive_size:
        label += f" {geom.drive_size.display()}"
    ax_end.text(
        0,
        -geom.head_dia.inches * 0.85,
        label,
        ha="center",
        va="top",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    fig.text(
        0.04,
        0.955,
        drawing_title(record, "Cap Screw"),
        fontsize=cv.FS_TITLE,
        fontweight="bold",
        color=cv.INK,
    )
    fig.text(0.04, 0.925, str(record.get("sku", "")), fontsize=cv.FS_SPEC, color=cv.MUTED)

    specs = [
        ("Dia./Thread Size", geom.thread.designation),
        ("Length", geom.length.display()),
        ("Thread Length", geom.thread_length.display()),
        ("Head Dia.", geom.head_dia.display()),
        ("Head Height", geom.head_height.display()),
        ("Drive Type", geom.drive_type),
        ("Drive Size", geom.drive_size.display() if geom.drive_size else ""),
        ("Material", record.get("Material", "")),
        ("Finish", record.get("Finish", "")),
        ("Grade", record.get("Grade", "")),
        ("Thread Type", record.get("Thread Type", "")),
        ("Thread Direction", record.get("Thread Direction", "")),
        ("Hardness", record.get("Hardness", "")),
        ("Width Across Flats", record.get("Width Across Flats", "")),
        ("Type", record.get("Type", "")),
    ]
    y = spec_table(fig, specs)
    if geom.countersunk:
        fig.text(0.62, y - 0.012, "countersink (derived)", fontsize=cv.FS_SPEC, color=cv.MUTED)
        fig.text(
            0.955,
            y - 0.012,
            f"{geom.countersink_included_angle:.0f}° incl.",
            fontsize=cv.FS_SPEC,
            color=cv.DIM,
            fontweight="bold",
            ha="right",
        )
    provenance_note(fig)
    return fig, ax


def build(record: dict, profile: Profile = CARD):
    """Build the figure without writing it: ``(figure, elevation axes, geometry)``.

    Exposed so a caller -- a test, or an embedder -- can measure the drawing in
    the figure's own coordinates instead of guessing at pixels.
    """
    geom = geometry_from_record(record)
    builder = _render_detail if profile.verbose else _render_card
    fig, ax = builder(record, geom, profile)
    return fig, ax, geom


def render(record: dict, path: str | Path, profile: Profile = CARD) -> Path:
    fig, _, _ = build(record, profile)
    return cv.save(fig, path, profile)
