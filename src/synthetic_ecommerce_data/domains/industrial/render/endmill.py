"""Dimensioned end-mill drawing, derived entirely from a product record.

The tool stands vertically, shank up and cutting end down: that is how the
industry draws one, and it is the only orientation in which a long thin tool
fills a portrait card.

What the record decides
-----------------------
``End Mill Style`` decides the cutting end and is **required**. A ball nose and
a square end are different tools and the record says which; a drawing that
showed a square end on a record reading ``Ball Nose`` would contradict its own
data, which is the one thing this renderer exists not to do. The attribute is
published on essentially every end mill in the reference corpus -- 132 records
carry it against 129 carrying ``Milling Dia.`` -- so requiring it asks for
nothing a real record withholds.

``Cutting Direction`` decides which way the flutes lean and
``Single End/Double End`` decides whether there is a second cutting end. Both
are followed when published. Neither can be left undrawn -- a tool has to be
drawn leaning some way, and with some number of ends -- so when the record is
silent the usual form is drawn and the detail sheet says, in the attribute
table, that the record did not publish it.

``Corner Radius`` rounds the corners of a square end. On a ball nose there are
no corners to round, so a record publishing both is refused rather than drawn
with one of them ignored.

The flutes
----------
A helix of angle ``h`` on a cylinder of diameter ``d`` advances
``lead = pi * d / tan(h)`` per turn. The face the drawing shows is half a turn,
so one flute rises ``lead / 2`` across it, and with ``n`` flutes an edge crosses
that face every ``lead / n``. Both come from :attr:`EndMillGeometry.helix_lead`,
which is the only place the formula appears.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from matplotlib.patches import Circle, Polygon, Rectangle, Wedge

from synthetic_ecommerce_data.core.dimensions import (
    Length,
    parse_angle_degrees,
    parse_count,
    parse_length,
)
from synthetic_ecommerce_data.domains.industrial.render import canvas as cv
from synthetic_ecommerce_data.domains.industrial.render.attrs import (
    NOT_PUBLISHED,
    ImpossibleGeometryError,
    MissingAttributeError,
    UnsupportedFeatureError,
    drawing_title,
    provenance_note,
    require,
    spec_table,
)
from synthetic_ecommerce_data.domains.industrial.render.profiles import CARD, Profile

#: The refusal classes are re-exported under this module's name: a caller
#: handling an end-mill refusal should not have to know they are defined
#: elsewhere, and both are part of this renderer's published surface.
__all__ = [
    "EndMillGeometry",
    "ImpossibleGeometryError",
    "MissingAttributeError",
    "UnsupportedFeatureError",
    "build",
    "geometry_from_record",
    "render",
]

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

#: Where the end view's flute edges stop, as a fraction of the cutting radius.
#: A break, not a dimension: see :func:`_draw_end_view`.
CENTRE_BREAK = 0.18

#: Fraction of the frame height the tool occupies, and the largest fraction of
#: the frame width its widest diameter may take before the tool is scaled down
#: to leave room for the callouts.
FILL_V = 0.78
FILL_H = 0.30


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
            f"{published!r} is not a cutting end this renderer knows how to draw"
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


def _arc(centre, radius, start_deg, end_deg, direction, steps=16):
    """Points along an arc, mirrored about the centre's y when ``direction`` is -1."""
    cx, cy = centre
    out = []
    for k in range(steps + 1):
        angle = math.radians(start_deg + (end_deg - start_deg) * k / steps)
        out.append((cx + radius * math.cos(angle), cy + direction * radius * math.sin(angle)))
    return out


def _cutting_end(ax, geom: EndMillGeometry, y_from: float, direction: int):
    """One cutting end, drawn from ``y_from`` running ``direction`` (+1 up).

    Returns the patch the flutes are clipped to, so a flute can never be drawn
    where there is no cutting portion to cut it into.
    """
    cut_d = geom.cut_d.inches
    loc = geom.loc.inches
    r = cut_d / 2
    y0 = min(y_from, y_from + direction * loc)
    if geom.style == "ball":
        # The ball is a half-sphere of the cutting radius, so the cylindrical
        # part of the flute run is what is left of the length of cut above it.
        centre = y_from + direction * r
        ball = Wedge(
            (0.0, centre),
            r,
            180 if direction > 0 else 0,
            360 if direction > 0 else 180,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            zorder=2,
        )
        ax.add_patch(ball)
        body = Rectangle(
            (-r, min(centre, centre + direction * (loc - r))),
            cut_d,
            loc - r,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=2,
        )
        ax.add_patch(body)
        # One clip region covering both, so the flutes run into the ball.
        clip = Rectangle((-r, y0), cut_d, loc, transform=ax.transData)
        return clip
    radius = geom.corner_radius.inches if geom.corner_radius else 0.0
    if not radius:
        patch = Rectangle(
            (-r, y0),
            cut_d,
            loc,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=2,
        )
        ax.add_patch(patch)
        return patch
    # Radii on the CUTTING corners only. The other two meet the shank and are
    # not corners of the tool at all.
    tip = y_from
    points = [(-r, y_from + direction * loc)]
    points.extend(_arc((-r + radius, tip + direction * radius), radius, 180, 270, direction))
    points.extend(_arc((r - radius, tip + direction * radius), radius, 270, 360, direction))
    points.append((r, y_from + direction * loc))
    patch = Polygon(
        points,
        closed=True,
        fc=cv.BODY_FILL,
        ec=cv.INK,
        lw=cv.LW_BODY,
        joinstyle="miter",
        zorder=2,
    )
    ax.add_patch(patch)
    return patch


def _draw_flutes(ax, geom: EndMillGeometry, clip, y0: float, y1: float) -> None:
    """Flute edges across one cutting portion, at the record's own helix.

    ``face_rise`` is the axial rise of one flute across the visible face and
    ``axial_flute_pitch`` the axial gap between successive ones; both come from
    the helix lead, so helix angle and flute count are not decoration.
    """
    cut_d = geom.cut_d.inches
    rise = geom.face_rise * geom.hand
    pitch = geom.axial_flute_pitch
    y = y0 - abs(rise)
    while y < y1:
        line = ax.plot(
            [-cut_d / 2, cut_d / 2],
            [y, y + rise] if geom.hand > 0 else [y - rise, y],
            color=cv.FLUTE,
            lw=cv.LW_FLUTE,
            zorder=3,
            solid_capstyle="butt",
        )[0]
        line.set_clip_path(clip)
        y += pitch


def _draw_body(ax, geom: EndMillGeometry) -> None:
    """Silhouette plus flutes, centred on the origin."""
    shank_d = geom.shank_d.inches
    oal, loc = geom.oal.inches, geom.loc.inches
    y_tip = -oal / 2.0
    shank_from = y_tip + loc
    shank_to = y_tip + oal - (loc if geom.double_end else 0.0)

    ax.add_patch(
        Rectangle(
            (-shank_d / 2, shank_from),
            shank_d,
            shank_to - shank_from,
            fc=cv.SHANK_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=2,
        )
    )

    clip = _cutting_end(ax, geom, y_tip, +1)
    _draw_flutes(ax, geom, clip, y_tip, y_tip + loc)
    if geom.double_end:
        top = y_tip + oal
        clip = _cutting_end(ax, geom, top, -1)
        _draw_flutes(ax, geom, clip, top - loc, top)


def _draw_end_view(ax, geom: EndMillGeometry) -> None:
    """The cutting end seen along the axis: both diameters, and the flute count."""
    r_cut = geom.cut_d.inches / 2
    r_shank = geom.shank_d.inches / 2
    ax.add_patch(
        Circle(
            (0, 0),
            r_shank,
            fill=False,
            ec=cv.MUTED,
            lw=cv.LW_HIDDEN,
            ls=(0, (5, 4)),
            zorder=2,
        )
    )
    ax.add_patch(Circle((0, 0), r_cut, fc=cv.BODY_FILL, ec=cv.INK, lw=cv.LW_BODY, zorder=3))
    # The flute edges stop short of the axis. Whether they run all the way to
    # it is what ``End Mill Cutting Type`` says, and the radius at which a
    # non-centre-cutting grind stops is not published, so the centre is left
    # as a break -- the attribute is listed on the sheet instead of drawn.
    inner = r_cut * CENTRE_BREAK
    for k in range(geom.flutes):
        theta = 2 * math.pi * k / geom.flutes
        ax.plot(
            [inner * math.cos(theta), r_cut * math.cos(theta)],
            [inner * math.sin(theta), r_cut * math.sin(theta)],
            color=cv.FLUTE,
            lw=cv.LW_FLUTE * 1.3,
            zorder=4,
            solid_capstyle="butt",
        )
    ax.plot([0], [0], marker="+", color=cv.MUTED, ms=5, mew=cv.LW_FLUTE)


def _frame_height(fig, rect, geom: EndMillGeometry) -> float:
    by_length = geom.oal.inches / FILL_V
    box_ratio = cv.frame_width(fig, rect, 1.0)
    by_width = (geom.max_d / FILL_H) / box_ratio
    return max(by_length, by_width)


def _render_card(record: dict, geom: EndMillGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.0, 0.0, 1.0, 1.0)
    frame_h = _frame_height(fig, rect, geom)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    _draw_body(ax, geom)

    y_tip = -geom.oal.inches / 2
    overhang = frame_w * 0.05
    gap = frame_w * 0.035
    cv.diameter_callout(
        ax,
        y_tip + geom.loc.inches * 0.45,
        geom.cut_d.inches,
        f"Ø{geom.cut_d.display()}",
        "milling",
        side=1,
        overhang=overhang,
        gap=gap,
    )
    cv.diameter_callout(
        ax,
        y_tip + geom.loc.inches + (geom.oal.inches - geom.loc.inches) * 0.55,
        geom.shank_d.inches,
        f"Ø{geom.shank_d.display()}",
        "shank",
        side=-1,
        overhang=overhang,
        gap=gap,
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


def _render_detail(record: dict, geom: EndMillGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.04, 0.05, 0.50, 0.82)
    frame_h = _frame_height(fig, rect, geom)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    _draw_body(ax, geom)

    oal, loc = geom.oal.inches, geom.loc.inches
    cut_d, shank_d = geom.cut_d.inches, geom.shank_d.inches
    y_tip = -oal / 2
    overhang = frame_w * 0.04
    gap = frame_w * 0.03

    # Both length dimensions stack on the left, shortest nearest the tool, and
    # both diameter callouts go right: no label can land on another dimension.
    x_oal = -frame_w * 0.42
    cv.length_dimension(ax, x_oal, y_tip, y_tip + oal, geom.oal.display())
    cv.witness(ax, x_oal, -shank_d / 2, y_tip + oal)
    cv.witness(ax, x_oal, -cut_d / 2, y_tip)
    ax.text(
        x_oal - frame_w * 0.055,
        0,
        "overall length",
        rotation=90,
        ha="center",
        va="center",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    x_loc = -frame_w * 0.26
    cv.length_dimension(ax, x_loc, y_tip, y_tip + loc, geom.loc.display())
    cv.witness(ax, x_loc, -cut_d / 2, y_tip + loc)
    ax.text(
        x_loc - frame_w * 0.055,
        y_tip + loc / 2,
        "length of cut",
        rotation=90,
        ha="center",
        va="center",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    cv.diameter_callout(
        ax,
        y_tip + loc * 0.5,
        cut_d,
        f"Ø{geom.cut_d.display()}",
        "milling dia.",
        side=1,
        overhang=overhang,
        gap=gap,
    )
    cv.diameter_callout(
        ax,
        y_tip + oal - (oal - loc) * 0.35,
        shank_d,
        f"Ø{geom.shank_d.display()}",
        "shank dia.",
        side=1,
        overhang=overhang,
        gap=gap,
    )

    end_rect = (0.62, 0.55, 0.30, 0.30)
    ax_end = cv.frame_axes(fig, end_rect, geom.max_d * 2.2)
    _draw_end_view(ax_end, geom)
    ax_end.text(
        0,
        -geom.max_d * 1.0,
        f"end view · {geom.flutes} flutes",
        ha="center",
        va="top",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    title = drawing_title(record, "End Mill")
    fig.text(0.04, 0.955, title, fontsize=cv.FS_TITLE, fontweight="bold", color=cv.INK)
    fig.text(0.04, 0.925, str(record.get("sku", "")), fontsize=cv.FS_SPEC, color=cv.MUTED)

    specs = [
        ("Milling Dia.", geom.cut_d.display()),
        ("Shank Dia.", geom.shank_d.display()),
        ("Length of Cut", geom.loc.display()),
        ("Overall Length", geom.oal.display()),
        ("Corner Radius", geom.corner_radius.display() if geom.corner_radius else ""),
        ("Neck Length", record.get("Neck Length", "")),
        ("Number of Flutes", str(geom.flutes)),
        ("Helix Angle", record.get("Helix Angle", "")),
        ("Cutting Direction", record.get("Cutting Direction") or NOT_PUBLISHED),
        ("Single End/Double End", record.get("Single End/Double End") or NOT_PUBLISHED),
        ("Cutting Type", record.get("Cutting Type", "")),
        ("Coolant Fed", record.get("Coolant Fed", "")),
        ("Material", record.get("Material", "")),
        # The catalog spells the coating "Finish", the census's generic name;
        # "Finish - Machining" is its minority spelling. A record carries one.
        ("Finish", record.get("Finish", "")),
        ("Finish - Machining", record.get("Finish - Machining", "")),
    ]
    spec_table(fig, specs)
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
    """Render ``record`` to ``path`` at ``profile``'s exact pixel size."""
    fig, _, _ = build(record, profile)
    return cv.save(fig, path, profile)
