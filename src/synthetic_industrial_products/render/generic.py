"""The ten generic product drawings, one per product type and style.

Why generic
-----------
A real distributor does not photograph every length of the same screw. The
archived reference pages measure 73.5% of records pointing at an image whose id
is not the product's own, and a category listing of four end mills from one
series at 1/2, 3/8, 1/4 and 1/8 inch shows the same photograph four times:
whatever differs between them is invisible at catalog size. **A family shares
one image**, so one drawing per product type and style is not a cheap
approximation of what a catalog does -- it is what a catalog does.

What each drawing asserts
-------------------------
Exactly one thing: *this product is a ball nose end mill*, *this product is a
flat washer*. That is true of every record of that type, from the product type
alone, and it stays true whatever the record's dimensions say or fail to say.

**No drawing here carries a dimension, a callout, or a number.** Not an
estimated one, not a typical one, none. The dimensions are on the record and
render beside the image, where they are the record's own values; a drawing that
restated one would be a second source that could disagree with the first. So
these cannot contradict their data -- there is no numeric claim in them to
contradict it with -- and that property is structural rather than something a
reviewer has to keep checking.

For the same reason no drawing here carries a SKU. One image stands behind
thousands of products, and a SKU printed on it would be wrong for all but one
of them.

What is not here
----------------
The dimensioned per-record drawings in :mod:`.endmill`, :mod:`.fastener`,
:mod:`.drill`, :mod:`.tap`, :mod:`.washer` and :mod:`.flapdisc` still exist and
are still the right thing for a detail view of a handful of demo products,
where the point being made is that cutting diameter and shank diameter are
different measurements. They are not what the catalog's 4,480 cards use.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from matplotlib.patches import Circle, Polygon, Rectangle, Wedge

from . import canvas as cv
from .attrs import MissingAttributeError, UnsupportedFeatureError, require

__all__ = [
    "IMAGES",
    "IMAGE_IDS",
    "MissingAttributeError",
    "NOT_TO_SCALE",
    "UnsupportedFeatureError",
    "build",
    "image_id_for_record",
    "render",
    "render_all",
    "render_record",
]
from .kinds import DRILL, END_MILL, FASTENER, FLAP_DISC, HAMMER, TAP, WASHER, classify
from .profiles import CARD, Profile

#: Drawn on the detail profile, under the name. The card is 150 CSS pixels
#: wide and carries the drawing alone.
NOT_TO_SCALE = "generic drawing · not to scale · this product's dimensions are on its record"

#: Every drawing is built in a frame one unit high, centred on the origin. The
#: card is the narrower profile at 150 x 220, giving a frame 0.682 wide, so
#: nothing may reach past about x = +-0.31.
FRAME_HEIGHT = 1.0
TOP = 0.42
BOTTOM = -0.42


@dataclass(frozen=True)
class GenericImage:
    """One of the ten: its id, what it is called, and what draws it."""

    image_id: str
    label: str
    draw: object

    def __call__(self, ax) -> None:
        self.draw(ax)  # type: ignore[operator]


# --- drawing helpers -------------------------------------------------------


def _bar(ax, half_width, y0, y1, fill=cv.BODY_FILL, zorder=2):
    patch = Rectangle(
        (-half_width, y0),
        half_width * 2,
        y1 - y0,
        fc=fill,
        ec=cv.INK,
        lw=cv.LW_BODY,
        joinstyle="miter",
        zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def _helical_flutes(ax, clip, half_width, y0, y1, rise, pitch, hand=1):
    """Flute edges leaning across the body, at a fixed spacing.

    Conventional representation, the way drafting shows a thread or a knurl:
    it states that the surface is fluted. It states no helix angle, because no
    helix angle is claimed anywhere on the drawing.
    """
    y = y0 - rise
    while y < y1:
        line = ax.plot(
            [-half_width, half_width],
            [y, y + rise] if hand > 0 else [y + rise, y],
            color=cv.FLUTE,
            lw=cv.LW_FLUTE,
            zorder=3,
            solid_capstyle="butt",
        )[0]
        line.set_clip_path(clip)
        y += pitch


def _thread(ax, half_width, y0, y1, pitch, root=0.72):
    """A 60-degree thread form, drawn as two zig-zag flanks half a pitch apart."""
    r_minor = half_width * root
    clip = Rectangle((-half_width, y0), half_width * 2, y1 - y0, transform=ax.transData)
    for sign, phase in ((-1, 0.0), (1, 0.5)):
        xs: list[float] = []
        ys: list[float] = []
        y = y0 - pitch
        while y < y1 + pitch:
            xs.extend([sign * r_minor, sign * half_width])
            ys.extend([y + phase * pitch, y + (phase + 0.5) * pitch])
            y += pitch
        line = ax.plot(
            xs, ys, color=cv.INK, lw=cv.LW_BODY * 0.55, zorder=4, solid_joinstyle="miter"
        )[0]
        line.set_clip_path(clip)
    for sign in (-1, 1):
        ax.plot(
            [sign * r_minor, sign * r_minor],
            [y0, y1],
            color=cv.MUTED,
            lw=cv.LW_HIDDEN,
            zorder=3,
        )


def _hex_socket(ax, centre, across, zorder=6):
    """A hex socket seen face on: the shape that makes a socket screw one."""
    cx, cy = centre
    r = (across / 2) / math.cos(math.radians(30))
    ax.add_patch(
        Polygon(
            [
                (
                    cx + r * math.cos(math.radians(30 + 60 * k)),
                    cy + r * math.sin(math.radians(30 + 60 * k)),
                )
                for k in range(6)
            ],
            closed=True,
            fc=cv.SHANK_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY * 0.8,
            zorder=zorder,
        )
    )


# --- the ten ---------------------------------------------------------------


def _draw_end_mill(ax, ball: bool) -> None:
    """Shank above, flutes below, and the cutting end that names the tool."""
    half, shank_half = 0.076, 0.088
    cut_top = 0.02
    body_bottom = BOTTOM + (half if ball else 0.0)
    _bar(ax, shank_half, cut_top, TOP, cv.SHANK_FILL)
    if ball:
        ax.add_patch(
            Wedge(
                (0.0, body_bottom),
                half,
                180,
                360,
                fc=cv.BODY_FILL,
                ec=cv.INK,
                lw=cv.LW_BODY,
                zorder=2,
            )
        )
    _bar(ax, half, body_bottom, cut_top)
    clip = Rectangle((-half, BOTTOM), half * 2, cut_top - BOTTOM, transform=ax.transData)
    _helical_flutes(ax, clip, half, BOTTOM, cut_top, rise=0.125, pitch=0.058)


def _draw_end_mill_square(ax) -> None:
    _draw_end_mill(ax, ball=False)


def _draw_end_mill_ball(ax) -> None:
    _draw_end_mill(ax, ball=True)


def _draw_drill(ax) -> None:
    """The point, the twisted flutes, and the plain shank the chuck grips."""
    half = 0.080
    cone = 0.098
    flute_top = 0.13
    _bar(ax, half, flute_top, TOP, cv.SHANK_FILL)
    body = _bar(ax, half, BOTTOM + cone, flute_top)
    ax.add_patch(
        Polygon(
            [(-half, BOTTOM + cone), (0.0, BOTTOM), (half, BOTTOM + cone)],
            closed=True,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=3,
        )
    )
    # Clipped to the cylindrical body: the point is a ground cone, and a
    # flute drawn across it would be drawing a tool that does not exist.
    clip = Rectangle(
        (-half, BOTTOM + cone), half * 2, flute_top - BOTTOM - cone, transform=ax.transData
    )
    # A twist drill's flute is a wide swept land, not a hairline, so each one
    # is drawn as the pair of edges that bound it.
    for offset in (0.0, 0.034):
        _helical_flutes(ax, clip, half, BOTTOM + cone - offset, flute_top, rise=0.185, pitch=0.084)
    ax.plot([-half, half], [flute_top, flute_top], color=cv.INK, lw=cv.LW_BODY, zorder=4)
    del body


def _draw_tap(ax) -> None:
    """Threads below, plain shank, and the square drive the wrench turns."""
    half, shank_half = 0.074, 0.062
    thread_top = 0.02
    square_from = 0.25
    _bar(ax, shank_half, thread_top, square_from, cv.SHANK_FILL)
    _bar(ax, half, BOTTOM, thread_top)
    _thread(ax, half, BOTTOM, thread_top, pitch=0.046)
    # The drive square, marked with the drafting convention for a square
    # section: crossed diagonals across the flat. They say "square"; they say
    # nothing about how big it is.
    square_half = shank_half * 0.92
    _bar(ax, square_half, square_from, TOP, cv.SHANK_FILL, zorder=4)
    for a, b in (
        ((-square_half, square_from), (square_half, TOP)),
        ((-square_half, TOP), (square_half, square_from)),
    ):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=cv.MUTED, lw=cv.LW_HIDDEN, zorder=5)


#: Fasteners are drawn head down the page with a small end view above it: the
#: head's true shape -- a hex socket, a hexagon -- is the one thing that tells
#: a socket cap screw from a hex bolt at 150 pixels wide, and in elevation it
#: is edge on.
_END_VIEW_CENTRE = 0.315
_END_VIEW_R = 0.100
_HEAD_TOP = 0.155


def _screw_body(ax, shank_half, seat, thread_to) -> None:
    _bar(ax, shank_half, BOTTOM, seat, cv.SHANK_FILL)
    _thread(ax, shank_half, BOTTOM, thread_to, pitch=0.040)


def _draw_socket_head_screw(ax) -> None:
    head_half, head_h = 0.105, 0.115
    seat = _HEAD_TOP - head_h
    _screw_body(ax, 0.062, seat, thread_to=seat - 0.05)
    _bar(ax, head_half, seat, _HEAD_TOP)
    # The socket, drawn as the opening it makes in the head's top face. Its
    # depth is not drawn -- on a per-record drawing it is not a published
    # attribute, and a generic drawing has nothing to publish it from either.
    mouth = head_half * 0.58
    ax.add_patch(
        Rectangle(
            (-mouth, _HEAD_TOP - head_h * 0.34),
            mouth * 2,
            head_h * 0.34,
            fc=cv.SHANK_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY * 0.8,
            joinstyle="miter",
            zorder=4,
        )
    )
    ax.add_patch(
        Circle(
            (0.0, _END_VIEW_CENTRE),
            _END_VIEW_R,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            zorder=5,
        )
    )
    _hex_socket(ax, (0.0, _END_VIEW_CENTRE), _END_VIEW_R * 1.15)


def _draw_flat_head_screw(ax) -> None:
    head_half, head_h = 0.128, 0.078
    seat = _HEAD_TOP - head_h
    shank_half = 0.062
    _screw_body(ax, shank_half, seat, thread_to=seat - 0.03)
    # The countersink is what makes this a flat head: the head sinks into the
    # work and the length is measured over it.
    ax.add_patch(
        Polygon(
            [
                (-head_half, _HEAD_TOP),
                (-shank_half, seat),
                (shank_half, seat),
                (head_half, _HEAD_TOP),
            ],
            closed=True,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=5,
        )
    )
    mouth = head_half * 0.46
    for sign in (-1, 1):
        ax.plot(
            [sign * head_half, sign * mouth],
            [_HEAD_TOP, _HEAD_TOP],
            color=cv.INK,
            lw=cv.LW_BODY,
            zorder=6,
        )
    ax.add_patch(
        Circle(
            (0.0, _END_VIEW_CENTRE),
            _END_VIEW_R,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            zorder=5,
        )
    )
    _hex_socket(ax, (0.0, _END_VIEW_CENTRE), _END_VIEW_R * 0.98)


def _draw_hex_bolt(ax) -> None:
    across_half, head_h = 0.120, 0.090
    seat = _HEAD_TOP - head_h
    shank_half = 0.064
    # A bolt is threaded for part of its length and plain under the head.
    _screw_body(ax, shank_half, seat, thread_to=BOTTOM + 0.34)
    _bar(ax, across_half, seat, _HEAD_TOP)
    # Three faces show in elevation; the two vertical edges between them are
    # what makes the head read as a hexagon rather than a cylinder.
    for sign in (-1, 1):
        ax.plot(
            [sign * across_half / math.sqrt(3), sign * across_half / math.sqrt(3)],
            [seat, _HEAD_TOP],
            color=cv.INK,
            lw=cv.LW_BODY * 0.7,
            zorder=4,
        )
    r = _END_VIEW_R / math.cos(math.radians(30))
    ax.add_patch(
        Polygon(
            [
                (
                    r * math.cos(math.radians(60 * k)),
                    _END_VIEW_CENTRE + r * math.sin(math.radians(60 * k)),
                )
                for k in range(6)
            ],
            closed=True,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            zorder=5,
        )
    )
    ax.add_patch(
        Circle(
            (0.0, _END_VIEW_CENTRE),
            shank_half,
            fill=False,
            ec=cv.MUTED,
            lw=cv.LW_HIDDEN,
            ls=(0, (5, 4)),
            zorder=6,
        )
    )


def _draw_washer(ax) -> None:
    """Face view and edge view, because a washer is a hole and a thickness."""
    r_out, r_in = 0.250, 0.115
    centre = 0.10
    ax.add_patch(Circle((0.0, centre), r_out, fc=cv.BODY_FILL, ec=cv.INK, lw=cv.LW_BODY, zorder=2))
    ax.add_patch(Circle((0.0, centre), r_in, fc=cv.PAPER, ec=cv.INK, lw=cv.LW_BODY, zorder=3))
    y1 = -0.28
    y0 = y1 - 0.055
    ax.add_patch(
        Rectangle(
            (-r_out, y0),
            r_out * 2,
            y1 - y0,
            fc=cv.SHANK_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=2,
        )
    )
    for sign in (-1, 1):
        ax.plot(
            [sign * r_in, sign * r_in],
            [y0, y1],
            color=cv.MUTED,
            lw=cv.LW_HIDDEN,
            ls=(0, (4, 3)),
            zorder=3,
        )


def _draw_hammer(ax) -> None:
    """A flat striking face one side of the eye, a rounded pein the other."""
    head_y, head_half_h = 0.250, 0.062
    face_x, pein_x = -0.230, 0.140
    ax.add_patch(
        Rectangle(
            (face_x, head_y - head_half_h),
            pein_x - face_x,
            head_half_h * 2,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=3,
        )
    )
    # The pein: the neck behind it and the ball itself, which is the feature
    # the product type is named for.
    ax.add_patch(
        Polygon(
            [
                (pein_x, head_y - head_half_h),
                (pein_x + 0.042, head_y - head_half_h * 0.60),
                (pein_x + 0.042, head_y + head_half_h * 0.60),
                (pein_x, head_y + head_half_h),
            ],
            closed=True,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            zorder=2,
        )
    )
    ax.add_patch(
        Circle(
            (pein_x + 0.046, head_y),
            head_half_h * 0.62,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            zorder=2,
        )
    )
    # A chamfer at the striking face, the way a hammer face is dressed.
    for sign in (-1, 1):
        ax.plot(
            [face_x, face_x + 0.022],
            [head_y + sign * head_half_h, head_y + sign * head_half_h * 0.62],
            color=cv.INK,
            lw=cv.LW_BODY * 0.7,
            zorder=4,
        )
    # The eye, where the handle passes through, and the handle below it.
    ax.add_patch(
        Rectangle(
            (-0.052, head_y - head_half_h - 0.032),
            0.104,
            head_half_h * 2 + 0.064,
            fc=cv.SHANK_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=4,
        )
    )
    ax.add_patch(
        Polygon(
            [
                (-0.036, head_y),
                (0.036, head_y),
                (0.030, BOTTOM + 0.15),
                (0.050, BOTTOM + 0.040),
                (0.032, BOTTOM),
                (-0.032, BOTTOM),
                (-0.050, BOTTOM + 0.040),
                (-0.030, BOTTOM + 0.15),
            ],
            closed=True,
            fc=cv.SHANK_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="round",
            zorder=2,
        )
    )


def _draw_flap_disc(ax) -> None:
    """Overlapping abrasive leaves round a hub, which is what a flap disc is."""
    r_out, r_hub, r_arbor = 0.268, 0.104, 0.050
    flaps = 34
    step = 2 * math.pi / flaps
    lean = step * 2.8
    for k in range(flaps):
        theta = step * k
        ax.add_patch(
            Polygon(
                [
                    (r_hub * math.cos(theta), r_hub * math.sin(theta)),
                    (r_out * math.cos(theta + lean), r_out * math.sin(theta + lean)),
                    (
                        r_out * math.cos(theta + lean + step * 1.9),
                        r_out * math.sin(theta + lean + step * 1.9),
                    ),
                    (
                        r_hub * math.cos(theta + step * 1.9),
                        r_hub * math.sin(theta + step * 1.9),
                    ),
                ],
                closed=True,
                fc=cv.BODY_FILL,
                ec=cv.FLUTE,
                lw=cv.LW_FLUTE * 0.7,
                zorder=3,
            )
        )
    ax.add_patch(Circle((0.0, 0.0), r_hub, fc=cv.SHANK_FILL, ec=cv.INK, lw=cv.LW_BODY, zorder=4))
    ax.add_patch(Circle((0.0, 0.0), r_arbor, fc=cv.PAPER, ec=cv.INK, lw=cv.LW_BODY, zorder=5))


#: The ten, in the order the catalog's product types are declared. The id is
#: the catalog's own product-type key, so an image reference says what the
#: image is a drawing of and nothing has to be looked up to know.
IMAGES: dict[str, GenericImage] = {
    image.image_id: image
    for image in (
        GenericImage("end_mill_square", "Square End Mill", _draw_end_mill_square),
        GenericImage("end_mill_ball", "Ball Nose End Mill", _draw_end_mill_ball),
        GenericImage("drill_jobber", "Jobber Length Drill Bit", _draw_drill),
        GenericImage("tap_spiral_point", "Spiral Point Tap", _draw_tap),
        GenericImage("screw_socket_head", "Socket Head Cap Screw", _draw_socket_head_screw),
        GenericImage("screw_flat_head", "Flat Head Socket Cap Screw", _draw_flat_head_screw),
        GenericImage("bolt_hex", "Hex Head Bolt", _draw_hex_bolt),
        GenericImage("washer_flat", "Flat Washer", _draw_washer),
        GenericImage("hammer_ball_pein", "Ball Pein Hammer", _draw_hammer),
        GenericImage("abrasive_flap_disc", "Flap Disc", _draw_flap_disc),
    )
}

IMAGE_IDS: tuple[str, ...] = tuple(IMAGES)

#: Which image a drawing kind uses when the record's style decides it.
_BY_STYLE: dict[str, dict[str, str]] = {
    END_MILL: {"square": "end_mill_square", "ball nose": "end_mill_ball", "ball": "end_mill_ball"},
    FASTENER: {
        "socket": "screw_socket_head",
        "socket cap": "screw_socket_head",
        "socket head": "screw_socket_head",
        "cylindrical": "screw_socket_head",
        "cheese": "screw_socket_head",
        "flat": "screw_flat_head",
        "flat head": "screw_flat_head",
        "countersunk": "screw_flat_head",
        "flat countersunk": "screw_flat_head",
        "hex": "bolt_hex",
    },
}

#: Which image a drawing kind uses when no style attribute is involved.
_BY_KIND: dict[str, str] = {
    DRILL: "drill_jobber",
    TAP: "tap_spiral_point",
    WASHER: "washer_flat",
    HAMMER: "hammer_ball_pein",
    FLAP_DISC: "abrasive_flap_disc",
}

#: The attribute that decides the style, per kind.
_STYLE_ATTRIBUTE: dict[str, str] = {
    END_MILL: "End Mill Style",
    FASTENER: "Screw Head Type",
}


def image_id_for_record(record: dict) -> str:
    """Which of the ten this record's product shows.

    Read off the attribute names, like everything else here. Two kinds need a
    style attribute as well, and it is required rather than defaulted: a square
    end mill and a ball nose are different products, and a drawing that picked
    one because the record was silent would be asserting something the record
    does not say.
    """
    kind = classify(record)
    if kind in _BY_KIND:
        return _BY_KIND[kind]
    attribute = _STYLE_ATTRIBUTE[kind]
    published = str(require(record, attribute)).strip().lower()
    try:
        return _BY_STYLE[kind][published]
    except KeyError as exc:
        raise UnsupportedFeatureError(
            f"record {record.get('sku', '?')!r}: {attribute} {published!r} is not a style "
            "any of the generic drawings is of"
        ) from exc


def build(image_id: str, profile: Profile = CARD):
    """Build one of the ten: ``(figure, axes)``."""
    try:
        image = IMAGES[image_id]
    except KeyError as exc:
        raise MissingAttributeError(f"no generic drawing is called {image_id!r}") from exc
    fig = cv.new_figure(profile)
    rect = (0.0, 0.10, 1.0, 0.80) if profile.verbose else (0.0, 0.0, 1.0, 1.0)
    ax = cv.frame_axes(fig, rect, FRAME_HEIGHT)
    image(ax)
    if profile.verbose:
        fig.text(
            0.5,
            0.94,
            image.label,
            fontsize=cv.FS_TITLE,
            fontweight="bold",
            color=cv.INK,
            ha="center",
        )
        fig.text(
            0.5,
            0.045,
            NOT_TO_SCALE,
            fontsize=cv.FS_FOOT,
            color=cv.MUTED,
            ha="center",
            style="italic",
        )
    return fig, ax


def render(image_id: str, path: str | Path, profile: Profile = CARD) -> Path:
    """Write one of the ten to ``path`` at the profile's exact pixel size."""
    fig, _ = build(image_id, profile)
    return cv.save(fig, path, profile)


def render_record(record: dict, path: str | Path, profile: Profile = CARD) -> Path:
    """Write the generic drawing this record's product shows."""
    return render(image_id_for_record(record), path, profile)


def render_all(out_dir: str | Path, profile: Profile = CARD) -> list[Path]:
    """All ten, named by their image id."""
    out_dir = Path(out_dir)
    return [render(image_id, out_dir / f"{image_id}.png", profile) for image_id in IMAGE_IDS]
