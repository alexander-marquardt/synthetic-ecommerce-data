"""The twelve product drawings, and the per-line marking that differentiates them.

Why generic
-----------
A real distributor does not photograph every length of the same screw. The
archived reference pages measure 73.5% of records pointing at an image whose id
is not the product's own, and a category listing of four end mills from one
series at 1/2, 3/8, 1/4 and 1/8 inch shows the same photograph four times:
whatever differs between them is invisible at catalog size. **A family shares
one image**, so one drawing per product line -- shared by that line's 4 to 20
SKUs -- is not a cheap approximation of what a catalog does; it is what a
catalog does.

Two drawings live here, and they assert different things
--------------------------------------------------------
:func:`render` and :func:`render_record` draw **the type**. One of twelve shapes,
asserting exactly one thing: *this product is a ball nose end mill*, *this
product is a flat washer*. That is true of every record of that type from the
product type alone, so the file is the same file whatever the record says --
``tests/test_generic.py`` asserts that byte for byte.

:func:`render_line` draws **one product line**. Same twelve shapes, re-styled from
that line's own published attributes by :mod:`.marking`: the outline in the
brand's colour, the fill in the coating's, the section hatched for the
material, the flutes drawn at the published count and leaning the published
way, and a stamp setting every published value verbatim. These are what the
catalog's 500 lines show, and two of them differ if and only if the two
records differ -- ``tests/test_line_drawings.py`` asserts that in both
directions.

What no drawing here carries
----------------------------
**No dimension, no callout, no number read off a size, no SKU.** Not an
estimated one, not a typical one, none. Everything the marking reads is a
``line``-scope attribute, constant over the whole line; a line's SKUs have a
median 5.5x spread of sizes, so a drawing that stated a size would be wrong for
most of the line it stands behind. The sizes are on the record and render
beside the image, where they are the record's own values. So a drawing here
cannot contradict its data on a measurement -- there is no measurement in it to
contradict with -- and that property is structural rather than something a
reviewer has to keep checking.

For the same reason no drawing here carries a SKU. One image stands behind a
whole line, and a SKU printed on it would be wrong for all but one of them.

What is not here
----------------
The dimensioned per-record drawings in :mod:`.endmill`, :mod:`.fastener`,
:mod:`.drill`, :mod:`.tap`, :mod:`.washer` and :mod:`.flapdisc` still exist and
are still the right thing for a detail view of a handful of demo products,
where the point being made is that cutting diameter and shank diameter are
different measurements. They are not what the catalog's cards use.
"""

from __future__ import annotations

import math
import textwrap
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

from matplotlib.patches import Circle, PathPatch, Polygon, Rectangle, Wedge

from ..catalog.entry import published
from . import canvas as cv
from .attrs import MissingAttributeError, UnsupportedFeatureError, require_any
from .fastener import dome_profile
from .kinds import DRILL, END_MILL, FASTENER, FLAP_DISC, HAMMER, TAP, WASHER, classify
from .marking import NEUTRAL, Marking, marking_for_line
from .profiles import CARD, Profile

__all__ = [
    "IMAGES",
    "IMAGE_IDS",
    "MissingAttributeError",
    "NOT_TO_SCALE",
    "UnsupportedFeatureError",
    "build",
    "STYLE_VALUES",
    "build_line",
    "drawing_for_record",
    "image_id_for_record",
    "marking_for_line",
    "render",
    "render_all",
    "render_line",
    "render_record",
]

#: Drawn on the detail profile, under the name. The card is 150 CSS pixels
#: wide and carries the drawing and its stamp alone.
NOT_TO_SCALE = "generic drawing · not to scale · this product's dimensions are on its record"

#: What the detail sheet says above the stamp, so the reader knows the block is
#: the record's own text rather than the draughtsman's summary of it.
STAMP_HEADING = "published attributes"

#: Every drawing is built in a frame one unit high, centred on the origin. The
#: card is the narrower profile at 150 x 220, giving a frame 0.682 wide, so
#: nothing may reach past about x = +-0.31.
FRAME_HEIGHT = 1.0
TOP = 0.42
BOTTOM = -0.42

#: Where the drawing sits on each profile, with a stamp and without one. A
#: drawing with no line behind it has no stamp and keeps the whole sheet.
_CARD_RECT_PLAIN = (0.0, 0.0, 1.0, 1.0)
_CARD_RECT_STAMPED = (0.0, 0.175, 1.0, 0.825)
_DETAIL_RECT_PLAIN = (0.0, 0.10, 1.0, 0.80)
_DETAIL_RECT_STAMPED = (0.0, 0.10, 0.56, 0.80)

#: Stamp type sizes. The card is rendered at 4x for high-density displays, so
#: 6 pt on a 3-inch figure at 200 dpi is 17 raster pixels -- legible in the
#: file, a caption-weight texture at the 150 px the card is displayed at.
FS_STAMP_CARD = 6.0
FS_STAMP_DETAIL = 8.0

#: How many stamp lines the card's band holds before the type is set smaller.
#: Nothing is ever dropped: a stamp that stopped part-way would be a drawing
#: claiming to show a record it was showing half of.
_CARD_STAMP_ROOM = 4


@dataclass(frozen=True)
class GenericImage:
    """One of the twelve: its id, what it is called, and what draws it."""

    image_id: str
    label: str
    draw: object

    def __call__(self, ax, mark: Marking) -> None:
        self.draw(ax, mark)  # type: ignore[operator]


# --- drawing helpers -------------------------------------------------------


def _hatched(ax, patch, mark: Marking):
    """Lay the material's section hatch over a patch already on the axes.

    Drawn as its own overlay rather than as the patch's own ``hatch`` so the
    hatch has a colour of its own. Matplotlib takes a patch's hatch colour from
    its edge colour, and the edge here is the brand's -- a hatch at full
    outline weight and full outline colour buries the part it describes.
    """
    if not mark.hatch:
        return patch
    path = patch.get_path().transformed(patch.get_patch_transform())
    ax.add_patch(
        PathPatch(
            path,
            fc="none",
            ec=cv.HATCH,
            lw=0.0,
            hatch=mark.hatch,
            zorder=patch.get_zorder() + 0.1,
        )
    )
    return patch


def _bar(ax, half_width, y0, y1, mark, *, coated=True, fill=None, hatched=True, zorder=2):
    """A rectangular section of the part, in this line's colours.

    ``coated`` says whether the coating tint reaches this section. It does not
    on a tool's shank -- a coating is applied to the cutting portion and the
    shank is ground steel -- and it does on a fastener, which is finished all
    over.

    ``hatched`` says whether the material hatch marks this section. It does not
    on a tool's shank or a socket opening: what the material attribute names is
    the CUTTING material -- ``End Mill Material``, ``Drill Bit Material`` -- so
    the hatch marks the part of the tool that attribute is about.
    """
    face = fill if fill is not None else ((mark.tint if coated else None) or cv.BODY_FILL)
    patch = Rectangle(
        (-half_width, y0),
        half_width * 2,
        y1 - y0,
        fc=face,
        ec=mark.ink,
        lw=cv.LW_BODY,
        joinstyle="miter",
        zorder=zorder,
    )
    ax.add_patch(patch)
    if hatched:
        _hatched(ax, patch, mark)
    return patch


def _flutes(ax, clip, half_width, y0, y1, mark, *, rise, pitch):
    """Flute edges leaning across the body.

    When the record publishes a flute count, exactly that many edges are drawn
    across the flute run, evenly spaced -- so the count is not a code to look
    up, it is the number of lines a reader counts. When the record is silent
    the surface is drawn with a conventional fluted hatch at a fixed spacing
    instead, which says *this surface is fluted* and states no count: the
    drawing does not get to invent one.
    """
    hand = mark.lean
    style = {} if mark.flutes is not None else {"ls": (0, (6, 4))}
    if mark.flutes is not None:
        step = (y1 - y0) / mark.flutes
        starts = [y0 + step * (k + 0.5) - rise / 2 for k in range(mark.flutes)]
    else:
        y = y0 - rise
        starts = []
        while y < y1:
            starts.append(y)
            y += pitch
    for start in starts:
        line = ax.plot(
            [-half_width, half_width],
            [start, start + rise] if hand > 0 else [start + rise, start],
            color=cv.FLUTE,
            lw=cv.LW_FLUTE,
            zorder=3,
            solid_capstyle="butt",
            **style,
        )[0]
        line.set_clip_path(clip)


def _thread(ax, half_width, y0, y1, mark, pitch, root=0.72):
    """A 60-degree thread form, drawn as two zig-zag flanks half a pitch apart.

    Leaning the way the record says the thread turns: a left-hand thread is a
    different product, and drawing every thread right-handed would make the
    published direction decorative.
    """
    r_minor = half_width * root
    hand = mark.lean
    clip = Rectangle((-half_width, y0), half_width * 2, y1 - y0, transform=ax.transData)
    for sign, phase in ((-1, 0.0), (1, 0.5)):
        xs: list[float] = []
        ys: list[float] = []
        y = y0 - pitch
        while y < y1 + pitch:
            xs.extend([sign * r_minor, sign * half_width])
            if hand > 0:
                ys.extend([y + phase * pitch, y + (phase + 0.5) * pitch])
            else:
                ys.extend([y + (phase + 0.5) * pitch, y + phase * pitch])
            y += pitch
        line = ax.plot(
            xs, ys, color=mark.ink, lw=cv.LW_BODY * 0.55, zorder=4, solid_joinstyle="miter"
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


def _hex_socket(ax, centre, across, mark, zorder=6):
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
            ec=mark.ink,
            lw=cv.LW_BODY * 0.8,
            zorder=zorder,
        )
    )


def _end_view_flutes(ax, centre, radius, mark, zorder=6):
    """The flute count, drawn where a flute count is actually readable.

    An end mill in elevation shows its flutes edge on; the end view is where
    two flutes are visibly two. Drawn only when the record publishes a count,
    and only on the profile with room for it.
    """
    if mark.flutes is None:
        return
    cx, cy = centre
    _hatched(
        ax,
        ax.add_patch(
            Circle(
                (cx, cy),
                radius,
                fc=mark.tint or cv.BODY_FILL,
                ec=mark.ink,
                lw=cv.LW_BODY * 0.8,
                zorder=zorder,
            )
        ),
        mark,
    )
    for k in range(mark.flutes):
        theta = 2 * math.pi * k / mark.flutes
        ax.plot(
            [cx + radius * 0.22 * math.cos(theta), cx + radius * math.cos(theta)],
            [cy + radius * 0.22 * math.sin(theta), cy + radius * math.sin(theta)],
            color=cv.FLUTE,
            lw=cv.LW_FLUTE,
            zorder=zorder + 1,
        )


# --- the twelve ------------------------------------------------------------


def _draw_end_mill(ax, mark: Marking, ball: bool) -> None:
    """Shank above, flutes below, and the cutting end that names the tool."""
    half, shank_half = 0.076, 0.088
    cut_top = 0.02
    body_bottom = BOTTOM + (half if ball else 0.0)
    _bar(ax, shank_half, cut_top, TOP, mark, coated=False, fill=cv.SHANK_FILL, hatched=False)
    if ball:
        _hatched(
            ax,
            ax.add_patch(
                Wedge(
                    (0.0, body_bottom),
                    half,
                    180,
                    360,
                    fc=mark.tint or cv.BODY_FILL,
                    ec=mark.ink,
                    lw=cv.LW_BODY,
                    zorder=2,
                )
            ),
            mark,
        )
    _bar(ax, half, body_bottom, cut_top, mark)
    clip = Rectangle((-half, BOTTOM), half * 2, cut_top - BOTTOM, transform=ax.transData)
    _flutes(ax, clip, half, BOTTOM, cut_top, mark, rise=0.125, pitch=0.058)


def _draw_end_mill_square(ax, mark) -> None:
    _draw_end_mill(ax, mark, ball=False)


def _draw_end_mill_ball(ax, mark) -> None:
    _draw_end_mill(ax, mark, ball=True)


def _draw_drill(ax, mark: Marking) -> None:
    """The point, the twisted flutes, and the plain shank the chuck grips."""
    half = 0.080
    cone = 0.098
    flute_top = 0.13
    _bar(ax, half, flute_top, TOP, mark, coated=False, fill=cv.SHANK_FILL, hatched=False)
    _bar(ax, half, BOTTOM + cone, flute_top, mark)
    _hatched(
        ax,
        ax.add_patch(
            Polygon(
                [(-half, BOTTOM + cone), (0.0, BOTTOM), (half, BOTTOM + cone)],
                closed=True,
                fc=mark.tint or cv.BODY_FILL,
                ec=mark.ink,
                lw=cv.LW_BODY,
                joinstyle="miter",
                zorder=3,
            )
        ),
        mark,
    )
    # Clipped to the cylindrical body: the point is a ground cone, and a
    # flute drawn across it would be drawing a tool that does not exist.
    clip = Rectangle(
        (-half, BOTTOM + cone), half * 2, flute_top - BOTTOM - cone, transform=ax.transData
    )
    # A twist drill's flute is a wide swept land, not a hairline, so each one
    # is drawn as the pair of edges that bound it. A twist drill has two
    # flutes and does not publish a count; the pair is the drawing's own
    # statement about what a twist drill is, not a value read off a record.
    plain = replace(mark, flutes=None)
    for offset in (0.0, 0.034):
        _flutes(
            ax,
            clip,
            half,
            BOTTOM + cone - offset,
            flute_top,
            plain,
            rise=0.185,
            pitch=0.084,
        )
    ax.plot([-half, half], [flute_top, flute_top], color=mark.ink, lw=cv.LW_BODY, zorder=4)


def _draw_tap(ax, mark: Marking) -> None:
    """Threads below, plain shank, and the square drive the wrench turns."""
    half, shank_half = 0.074, 0.062
    thread_top = 0.02
    square_from = 0.25
    _bar(
        ax,
        shank_half,
        thread_top,
        square_from,
        mark,
        coated=False,
        fill=cv.SHANK_FILL,
        hatched=False,
    )
    _bar(ax, half, BOTTOM, thread_top, mark)
    _thread(ax, half, BOTTOM, thread_top, mark, pitch=0.046)
    # The flutes a spiral point tap is ground with, over the threaded run.
    clip = Rectangle((-half, BOTTOM), half * 2, thread_top - BOTTOM, transform=ax.transData)
    _flutes(ax, clip, half, BOTTOM, thread_top, mark, rise=0.10, pitch=0.070)
    # The drive square, marked with the drafting convention for a square
    # section: crossed diagonals across the flat. They say "square"; they say
    # nothing about how big it is.
    square_half = shank_half * 0.92
    _bar(
        ax,
        square_half,
        square_from,
        TOP,
        mark,
        coated=False,
        fill=cv.SHANK_FILL,
        hatched=False,
        zorder=4,
    )
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


def _screw_body(ax, shank_half, seat, thread_to, mark) -> None:
    _bar(ax, shank_half, BOTTOM, seat, mark, fill=mark.tint or cv.SHANK_FILL)
    _thread(ax, shank_half, BOTTOM, thread_to, mark, pitch=0.040)


def _draw_socket_head_screw(ax, mark: Marking) -> None:
    head_half, head_h = 0.105, 0.115
    seat = _HEAD_TOP - head_h
    _screw_body(ax, 0.062, seat, seat - 0.05, mark)
    _bar(ax, head_half, seat, _HEAD_TOP, mark)
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
            ec=mark.ink,
            lw=cv.LW_BODY * 0.8,
            joinstyle="miter",
            zorder=4,
        )
    )
    ax.add_patch(
        Circle(
            (0.0, _END_VIEW_CENTRE),
            _END_VIEW_R,
            fc=mark.tint or cv.BODY_FILL,
            ec=mark.ink,
            lw=cv.LW_BODY,
            zorder=5,
        )
    )
    _hex_socket(ax, (0.0, _END_VIEW_CENTRE), _END_VIEW_R * 1.15, mark)


def _draw_flat_head_screw(ax, mark: Marking) -> None:
    head_half, head_h = 0.128, 0.078
    seat = _HEAD_TOP - head_h
    shank_half = 0.062
    _screw_body(ax, shank_half, seat, seat - 0.03, mark)
    # The countersink is what makes this a flat head: the head sinks into the
    # work and the length is measured over it.
    _hatched(
        ax,
        ax.add_patch(
            Polygon(
                [
                    (-head_half, _HEAD_TOP),
                    (-shank_half, seat),
                    (shank_half, seat),
                    (head_half, _HEAD_TOP),
                ],
                closed=True,
                fc=mark.tint or cv.BODY_FILL,
                ec=mark.ink,
                lw=cv.LW_BODY,
                joinstyle="miter",
                zorder=5,
            )
        ),
        mark,
    )
    mouth = head_half * 0.46
    for sign in (-1, 1):
        ax.plot(
            [sign * head_half, sign * mouth],
            [_HEAD_TOP, _HEAD_TOP],
            color=mark.ink,
            lw=cv.LW_BODY,
            zorder=6,
        )
    ax.add_patch(
        Circle(
            (0.0, _END_VIEW_CENTRE),
            _END_VIEW_R,
            fc=mark.tint or cv.BODY_FILL,
            ec=mark.ink,
            lw=cv.LW_BODY,
            zorder=5,
        )
    )
    _hex_socket(ax, (0.0, _END_VIEW_CENTRE), _END_VIEW_R * 0.98, mark)


def _draw_button_head_screw(ax, mark: Marking) -> None:
    """A dome, not a cylinder.

    The arc is struck by the same function the dimensioned renderer uses, from
    a head diameter and a head height -- here the generic drawing's own
    proportions rather than a record's, because this drawing stands for a
    product type and carries no line's numbers. What it must not do is share a
    silhouette with the socket head: a button head is a different product, and
    a reader who cannot tell them apart is being shown the wrong one.
    """
    head_half, head_h = 0.112, 0.056
    seat = _HEAD_TOP - head_h
    shank_half = 0.062
    _screw_body(ax, shank_half, seat, seat - 0.05, mark)
    _hatched(
        ax,
        ax.add_patch(
            Polygon(
                dome_profile(head_half, head_h, seat),
                closed=True,
                fc=mark.tint or cv.BODY_FILL,
                ec=mark.ink,
                lw=cv.LW_BODY,
                zorder=5,
            )
        ),
        mark,
    )
    ax.add_patch(
        Circle(
            (0.0, _END_VIEW_CENTRE),
            _END_VIEW_R,
            fc=mark.tint or cv.BODY_FILL,
            ec=mark.ink,
            lw=cv.LW_BODY,
            zorder=5,
        )
    )
    # Also a smaller socket than a full socket head's: ISO 7380-1 M6 takes a
    # 4 mm key where ISO 4762 M6 takes 5.
    _hex_socket(ax, (0.0, _END_VIEW_CENTRE), _END_VIEW_R * 0.92, mark)


def _draw_low_head_screw(ax, mark: Marking) -> None:
    """The socket head cap screw's cylinder at about half the height.

    Not wider: DIN 7984's head diameter equals ISO 4762's at every size this
    catalog offers and ASME B18.3.1G's is a few thousandths under ASME B18.3's,
    so the head half-width here is the socket head drawing's own. The height is
    the whole difference between the two products, and it belongs in the
    silhouette rather than in the marking -- a low head screw drawn to a full
    head's proportions is a picture of the screw the shopper did not order.
    """
    head_half, head_h = 0.105, 0.062
    seat = _HEAD_TOP - head_h
    _screw_body(ax, 0.062, seat, seat - 0.05, mark)
    _bar(ax, head_half, seat, _HEAD_TOP, mark)
    mouth = head_half * 0.52
    ax.add_patch(
        Rectangle(
            (-mouth, _HEAD_TOP - head_h * 0.52),
            mouth * 2,
            head_h * 0.52,
            fc=cv.SHANK_FILL,
            ec=mark.ink,
            lw=cv.LW_BODY * 0.8,
            joinstyle="miter",
            zorder=4,
        )
    )
    ax.add_patch(
        Circle(
            (0.0, _END_VIEW_CENTRE),
            _END_VIEW_R,
            fc=mark.tint or cv.BODY_FILL,
            ec=mark.ink,
            lw=cv.LW_BODY,
            zorder=5,
        )
    )
    # A smaller socket than a full head's, because a shallower head holds one:
    # DIN 7984 M6 takes a 4 mm key where ISO 4762 M6 takes 5, and ASME
    # B18.3.1G's 1/4 in takes 1/8 where ASME B18.3's takes 3/16.
    _hex_socket(ax, (0.0, _END_VIEW_CENTRE), _END_VIEW_R * 0.90, mark)


def _draw_hex_bolt(ax, mark: Marking) -> None:
    across_half, head_h = 0.120, 0.090
    seat = _HEAD_TOP - head_h
    shank_half = 0.064
    # A bolt is threaded for part of its length and plain under the head.
    _screw_body(ax, shank_half, seat, BOTTOM + 0.34, mark)
    _bar(ax, across_half, seat, _HEAD_TOP, mark)
    # Three faces show in elevation; the two vertical edges between them are
    # what makes the head read as a hexagon rather than a cylinder.
    for sign in (-1, 1):
        ax.plot(
            [sign * across_half / math.sqrt(3), sign * across_half / math.sqrt(3)],
            [seat, _HEAD_TOP],
            color=mark.ink,
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
            fc=mark.tint or cv.BODY_FILL,
            ec=mark.ink,
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


def _draw_washer(ax, mark: Marking) -> None:
    """Face view and edge view, because a washer is a hole and a thickness."""
    r_out, r_in = 0.250, 0.115
    centre = 0.10
    ax.add_patch(
        Circle(
            (0.0, centre),
            r_out,
            fc=mark.tint or cv.BODY_FILL,
            ec=mark.ink,
            lw=cv.LW_BODY,
            zorder=2,
        )
    )
    ax.add_patch(Circle((0.0, centre), r_in, fc=cv.PAPER, ec=mark.ink, lw=cv.LW_BODY, zorder=3))
    y1 = -0.28
    y0 = y1 - 0.055
    # The edge view is the section, so it is the view that carries the hatch.
    _bar(ax, r_out, y0, y1, mark, fill=mark.tint or cv.SHANK_FILL)
    for sign in (-1, 1):
        ax.plot(
            [sign * r_in, sign * r_in],
            [y0, y1],
            color=cv.MUTED,
            lw=cv.LW_HIDDEN,
            ls=(0, (4, 3)),
            zorder=3,
        )


def _draw_hammer(ax, mark: Marking) -> None:
    """A flat striking face one side of the eye, a rounded pein the other."""
    head_y, head_half_h = 0.250, 0.062
    face_x, pein_x = -0.230, 0.140
    _hatched(
        ax,
        ax.add_patch(
            Rectangle(
                (face_x, head_y - head_half_h),
                pein_x - face_x,
                head_half_h * 2,
                fc=mark.tint or cv.BODY_FILL,
                ec=mark.ink,
                lw=cv.LW_BODY,
                joinstyle="miter",
                zorder=3,
            )
        ),
        mark,
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
            fc=mark.tint or cv.BODY_FILL,
            ec=mark.ink,
            lw=cv.LW_BODY,
            zorder=2,
        )
    )
    ax.add_patch(
        Circle(
            (pein_x + 0.046, head_y),
            head_half_h * 0.62,
            fc=mark.tint or cv.BODY_FILL,
            ec=mark.ink,
            lw=cv.LW_BODY,
            zorder=2,
        )
    )
    # A chamfer at the striking face, the way a hammer face is dressed.
    for sign in (-1, 1):
        ax.plot(
            [face_x, face_x + 0.022],
            [head_y + sign * head_half_h, head_y + sign * head_half_h * 0.62],
            color=mark.ink,
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
            ec=mark.ink,
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
            ec=mark.ink,
            lw=cv.LW_BODY,
            joinstyle="round",
            zorder=2,
        )
    )


def _draw_flap_disc(ax, mark: Marking) -> None:
    """Overlapping abrasive leaves round a hub, which is what a flap disc is."""
    r_out, r_hub, r_arbor = 0.268, 0.104, 0.050
    flaps = 34
    step = 2 * math.pi / flaps
    lean = step * 2.8 * mark.lean
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
                fc=mark.tint or cv.BODY_FILL,
                ec=cv.FLUTE,
                lw=cv.LW_FLUTE * 0.7,
                zorder=3,
            )
        )
    _hatched(
        ax,
        ax.add_patch(
            Circle(
                (0.0, 0.0),
                r_hub,
                fc=cv.SHANK_FILL,
                ec=mark.ink,
                lw=cv.LW_BODY,
                zorder=4,
            )
        ),
        mark,
    )
    ax.add_patch(Circle((0.0, 0.0), r_arbor, fc=cv.PAPER, ec=mark.ink, lw=cv.LW_BODY, zorder=5))


#: The twelve, in the order the catalog's product types are declared. The id is
#: the catalog's own product-type key, so a drawing reference says what the
#: drawing is of and nothing has to be looked up to know.
IMAGES: dict[str, GenericImage] = {
    image.image_id: image
    for image in (
        GenericImage("end_mill_square", "Square End Mill", _draw_end_mill_square),
        GenericImage("end_mill_ball", "Ball Nose End Mill", _draw_end_mill_ball),
        GenericImage("drill_jobber", "Jobber Length Drill Bit", _draw_drill),
        GenericImage("tap_spiral_point", "Spiral Point Tap", _draw_tap),
        GenericImage("screw_socket_head", "Socket Head Cap Screw", _draw_socket_head_screw),
        GenericImage("screw_flat_head", "Flat Head Socket Cap Screw", _draw_flat_head_screw),
        GenericImage("screw_button_head", "Button Head Socket Cap Screw", _draw_button_head_screw),
        GenericImage("screw_low_head", "Low Head Socket Cap Screw", _draw_low_head_screw),
        GenericImage("bolt_hex", "Hex Head Bolt", _draw_hex_bolt),
        GenericImage("washer_flat", "Flat Washer", _draw_washer),
        GenericImage("hammer_ball_pein", "Ball Pein Hammer", _draw_hammer),
        GenericImage("abrasive_flap_disc", "Flap Disc", _draw_flap_disc),
    )
}

IMAGE_IDS: tuple[str, ...] = tuple(IMAGES)

#: Which drawing a kind uses when the record's style decides it.
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
        "button": "screw_button_head",
        "button head": "screw_button_head",
        "dome": "screw_button_head",
        "low socket": "screw_low_head",
        "low head": "screw_low_head",
        "low socket head": "screw_low_head",
        "hex": "bolt_hex",
    },
}

#: Which drawing a kind uses when no style attribute is involved.
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
    FASTENER: "Head Type",
}

#: Other names an OBSERVED record publishes a style attribute under. The
#: generator writes the census's generic ``Head Type``; the observed cap screw
#: fixture says ``Screw Head Type``, verbatim, and must still draw.
_OBSERVED_SPELLINGS: dict[str, tuple[str, ...]] = {"Head Type": ("Screw Head Type",)}


#: Which drawing each publishable style value names, by the attribute that
#: publishes it -- the table above, re-keyed from the kind to the attribute.
#:
#: Derived rather than written out a second time: a style added above is one a
#: sweep over the vocabulary can try, without anyone remembering to add it
#: here as well. It carries the DRAWING and not just the value because several
#: spellings name one shape -- ``button`` and ``button head`` are the same
#: picture -- and a sweep that wants a different picture has to be able to ask
#: for one rather than taking the next value along and comparing two drawings
#: that were never going to differ.
STYLE_DRAWINGS: dict[str, dict[str, str]] = {
    _STYLE_ATTRIBUTE[kind]: dict(values) for kind, values in _BY_STYLE.items()
}

#: The style values each style attribute may publish, by attribute name.
STYLE_VALUES: dict[str, tuple[str, ...]] = {
    name: tuple(sorted(table)) for name, table in STYLE_DRAWINGS.items()
}


def drawing_for_record(record: dict) -> str:
    """Which of the twelve shapes this record's product is drawn as.

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
    published = (
        str(require_any(record, attribute, *_OBSERVED_SPELLINGS.get(attribute, ()))).strip().lower()
    )
    try:
        return _BY_STYLE[kind][published]
    except KeyError as exc:
        raise UnsupportedFeatureError(
            f"record {record.get('sku', '?')!r}: {attribute} {published!r} is not a style "
            "any of the generic drawings is of"
        ) from exc


#: The name this had when the drawings were also the catalog's image
#: ids. They are no longer the same thing -- a catalog image id is now one per
#: product line -- so the function that names a SHAPE is spelled
#: :func:`drawing_for_record`, and this stays for callers that predate the split.
image_id_for_record = drawing_for_record


def _stamp_card(fig, mark: Marking) -> None:
    """The card's stamp band: every published value, under a rule."""
    lines = mark.stamp_lines()
    if not lines:
        return
    size = FS_STAMP_CARD
    if len(lines) > _CARD_STAMP_ROOM:
        # Set smaller rather than cut short, and re-wrap wider to match: the
        # alternative is a stamp that silently stopped being the whole record.
        scale = _CARD_STAMP_ROOM / len(lines)
        size = FS_STAMP_CARD * max(scale, 0.68)
        lines = mark.stamp_lines(columns=int(58 / max(scale, 0.68)))
    fig.add_artist(
        Rectangle(
            (0.06, 0.163),
            0.88,
            0.0012,
            transform=fig.transFigure,
            fc=cv.MUTED,
            ec="none",
        )
    )
    y = 0.135
    for text in lines:
        fig.text(0.5, y, text, fontsize=size, color=cv.MUTED, ha="center", va="top")
        y -= (size + 2.2) / (fig.get_size_inches()[1] * 72)


def _stamp_detail(fig, mark: Marking) -> None:
    """The detail sheet's title block: every published attribute, name and value.

    Names included, because the detail profile has the width for them. This is
    the record's ``line``-scope half set out in full, which is what makes the
    encoding legible without a legend: a reader who wants to know why two
    drawings differ reads the block rather than decoding the colours.
    """
    if not mark.rows:
        return
    fig.text(
        0.60,
        0.845,
        STAMP_HEADING,
        fontsize=cv.FS_FOOT,
        color=cv.MUTED,
        style="italic",
    )
    rows = mark.rows
    step = 0.036
    size = FS_STAMP_DETAIL
    room = 18
    if len(rows) > room:
        scale = room / len(rows)
        step *= scale
        size *= max(scale, 0.66)
    y = 0.805
    for name, value in rows:
        fig.text(0.60, y, name, fontsize=size, color=cv.MUTED)
        # Not at an internal hyphen: a published value is a token, not prose.
        wrapped = textwrap.wrap(value, width=22, break_on_hyphens=False) or [value]
        fig.text(0.97, y, wrapped[0], fontsize=size, color=cv.INK, fontweight="bold", ha="right")
        y -= step
        for extra in wrapped[1:]:
            fig.text(0.97, y, extra, fontsize=size, color=cv.INK, fontweight="bold", ha="right")
            y -= step


def build(image_id: str, profile: Profile = CARD, mark: Marking = NEUTRAL):
    """Build one drawing: ``(figure, axes)``.

    With the default :data:`~.marking.NEUTRAL` marking this is the drawing of
    a product TYPE -- plain line work, no line's values on it. Pass a marking
    from :func:`~.marking.marking_for_line` for a product line's own drawing.
    """
    try:
        image = IMAGES[image_id]
    except KeyError as exc:
        raise MissingAttributeError(f"no generic drawing is called {image_id!r}") from exc
    fig = cv.new_figure(profile)
    stamped = bool(mark.rows)
    if profile.verbose:
        rect = _DETAIL_RECT_STAMPED if stamped else _DETAIL_RECT_PLAIN
    else:
        rect = _CARD_RECT_STAMPED if stamped else _CARD_RECT_PLAIN
    ax = cv.frame_axes(fig, rect, FRAME_HEIGHT)
    image(ax, mark)
    if profile.verbose:
        _end_view_flutes(ax, (0.235, -0.30), 0.072, mark)
        fig.text(
            0.5 if not stamped else 0.28,
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
        _stamp_detail(fig, mark)
    else:
        _stamp_card(fig, mark)
    return fig, ax


def render(image_id: str, path: str | Path, profile: Profile = CARD) -> Path:
    """Write the drawing of a product TYPE at the profile's exact pixel size."""
    fig, _ = build(image_id, profile)
    return cv.save(fig, path, profile)


def render_record(record: dict, path: str | Path, profile: Profile = CARD) -> Path:
    """Write the type drawing this record's product shows.

    The drawing of a TYPE, not of the record: the same file comes out whatever
    the record's values are. This is the fallback a refused dimensioned drawing
    takes, where there is no product line in hand to mark the drawing with.
    """
    return render(drawing_for_record(record), path, profile)


def build_line(line: dict, facets_by_sku: Mapping[str, Mapping], profile: Profile = CARD):
    """Build the drawing of one product LINE: ``(figure, axes)``.

    ``line`` is the catalog's nested parent document -- it carries ``brand``
    and the line's own ``attributes``, which is everything the marking reads
    and nothing a SKU varies. A nested entry carries no spelling (#42), so the
    published values the card stamp prints are read from ``flat.jsonl``
    ``facets``, joined on the line's first SKU: a line attribute is the same on
    every SKU beneath it.
    """
    sku = line["variants"][0]["sku"]
    entries = [
        {"name": name, "value": value}
        for name, value in published(line["attributes"], facets_by_sku[sku])
    ]
    record = {entry["name"]: entry["value"] for entry in entries}
    record["sku"] = line.get("product_id", "?")
    if "product_type" in line:
        record["product_type"] = line["product_type"]
    mark = marking_for_line(line["brand"], entries)
    return build(drawing_for_record(record), profile, mark)


def render_line(
    line: dict, facets_by_sku: Mapping[str, Mapping], path: str | Path, profile: Profile = CARD
) -> Path:
    """Write one product line's own drawing."""
    fig, _ = build_line(line, facets_by_sku, profile)
    return cv.save(fig, path, profile)


def render_all(out_dir: str | Path, profile: Profile = CARD) -> list[Path]:
    """All twelve type drawings, named by the drawing they are."""
    out_dir = Path(out_dir)
    return [render(image_id, out_dir / f"{image_id}.png", profile) for image_id in IMAGE_IDS]
