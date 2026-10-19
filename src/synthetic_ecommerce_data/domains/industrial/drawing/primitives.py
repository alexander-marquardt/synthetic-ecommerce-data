"""The drawing primitives: the parts a figure is composed from (#74).

A sibling type's figure is built from these shared parts, not drawn from
scratch: a socket screw and a pan head screw share the thread, the shank and
the drive recess; a drill and an end mill share the flutes. Each primitive adds
shapes to a :class:`~synthetic_ecommerce_data.core.drawing.model.Figure` and
takes plain dimensions in inches, so a caller passes what the record published,
or a nominal proportion of it (the declarative layer in :mod:`.compose` keeps
which of the two it was, as the figure's ``source``).

Conventions, shared by every primitive:

* The axis of a long part is ``x = 0``; ``y`` grows from a head's top toward the
  point, as the older figures already drew it. A primitive that stands across
  the axis is symmetric about it.
* ``y0`` is the end of a section nearer the origin and ``y1`` the other end.
  ``drop`` shifts a section that many inches toward the origin: the drafting
  break draws the far part of a long screw closer, and nothing else uses it.
* Shapes are added in the order a reader would draw them (the body, then what
  is cut into it), because that order is the paint order.
* The roles are the ones of :data:`~synthetic_ecommerce_data.core.drawing.model.ROLES`.

Moving a shape out of a figure into this module must leave the SVG bytes of
every drawing it served unchanged; ``tests/test_drawing_primitives_74.py`` pins
the digests of the figures built from these parts.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from synthetic_ecommerce_data.core.drawing.model import Figure, Point, regular_polygon
from synthetic_ecommerce_data.domains.industrial.render import fastener as fastener_geom

#: The share of a pan head's height that is its domed crown; the rest is the
#: straight wall.
PAN_CROWN = 0.5


# --- shanks, bodies and sections ----------------------------------------------


def shank(fig: Figure, r: float, y0: float, y1: float, role: str = "plain") -> None:
    """A plain round shank of radius ``r`` between ``y0`` and ``y1``, seen from the side."""
    fig.rect(-r, y0, r, y1, role)


def round_body(fig: Figure, dia: float, y0: float, y1: float, role: str = "part") -> None:
    """A round bar of diameter ``dia`` between ``y0`` and ``y1`` (a body, not a shank)."""
    fig.rect(-dia / 2, y0, dia / 2, y1, role)


def hex_body(fig: Figure, across_flats: float, y0: float, y1: float, role: str = "part") -> None:
    """A hexagonal body seen from the side: its width is across the CORNERS, and two
    lines a quarter of that from the axis show the faces that turn away."""
    across_corners = across_flats * 2 / math.sqrt(3)
    fig.rect(-across_corners / 2, y0, across_corners / 2, y1, role)
    fig.lines(
        [
            ((-across_corners / 4, y0), (-across_corners / 4, y1)),
            ((across_corners / 4, y0), (across_corners / 4, y1)),
        ]
    )


def chamfer(
    fig: Figure,
    r: float,
    y0: float,
    y1: float,
    length: float,
    inset: float | None = None,
    role: str = "part",
    drop: float = 0.0,
) -> None:
    """A round bar from ``y0`` to ``y1`` with its ``y1`` end chamfered.

    ``length`` is how far along the axis the chamfer runs and ``inset`` how far
    it cuts in across the bar (the same, a 45 degree chamfer, unless given).
    """
    cut = length if inset is None else inset
    fig.poly(
        [
            (-r, y0 - drop),
            (r, y0 - drop),
            (r, y1 - length - drop),
            (r - cut, y1 - drop),
            (-r + cut, y1 - drop),
            (-r, y1 - length - drop),
        ],
        role,
    )


def thread_crests(
    x_half: float, y_from: float, y_to: float, pitch: float
) -> list[tuple[Point, Point]]:
    """The thread's crests across a body of half width ``x_half``: one slanted
    stroke per ``pitch`` between ``y_from`` and ``y_to``."""
    count = int((y_to - y_from) / pitch)
    return [
        ((-x_half, y_from + k * pitch), (x_half, y_from + k * pitch + pitch / 2))
        for k in range(count)
    ]


def thread(
    fig: Figure,
    r: float,
    y0: float,
    y1: float,
    pitch: float,
    chamfer_length: float = 0.0,
    drop: float = 0.0,
) -> None:
    """A threaded section of radius ``r``: the body with its end chamfered, and a
    crest every ``pitch``."""
    chamfer(fig, r, y0, y1, chamfer_length, drop=drop)
    fig.lines(
        [
            ((x0, ya - drop), (x1, yb - drop))
            for (x0, ya), (x1, yb) in thread_crests(r, y0, y1 - chamfer_length, pitch)
        ]
    )


def break_mark(fig: Figure, r: float, y: float, amplitude: float) -> None:
    """A drafting break across a shank of radius ``r`` at ``y``: a zigzag."""
    xs = [-r * 1.15 + k * (2.3 * r / 6) for k in range(7)]
    points = [(x, y + (amplitude if k % 2 else -amplitude)) for k, x in enumerate(xs)]
    fig.lines(list(zip(points, points[1:], strict=False)))


def conical_end(fig: Figure, r: float, y0: float, y_shoulder: float, y_tip: float) -> None:
    """A round body of radius ``r`` from ``y0`` to ``y_shoulder`` that ends in a cone
    to a point at ``y_tip`` (a drill's point)."""
    fig.poly([(-r, y0), (r, y0), (r, y_shoulder), (0, y_tip), (-r, y_shoulder)])


# --- heads --------------------------------------------------------------------
# Every head sits with its top at ``top`` and its seat ``height`` below it.


def head_flat(fig: Figure, head_d: float, shank_r: float, height: float, top: float = 0.0) -> None:
    """A flat (countersunk) head: a cone from the head diameter down to the shank."""
    fig.poly(
        [
            (-head_d / 2, top),
            (head_d / 2, top),
            (shank_r, top + height),
            (-shank_r, top + height),
        ]
    )


def head_button(fig: Figure, head_d: float, height: float, top: float = 0.0) -> None:
    """A button head: the spherical cap that ``head_d`` and ``height`` fix completely."""
    dome = [(x, top + height - y) for x, y in fastener_geom.dome_profile(head_d / 2, height, 0.0)]
    fig.poly(dome + [(head_d / 2, top + height), (-head_d / 2, top + height)])


def head_pan(fig: Figure, head_d: float, height: float, top: float = 0.0) -> None:
    """A pan head: a straight wall under a shallow domed crown (:data:`PAN_CROWN` of the height)."""
    crown = PAN_CROWN * height
    dome = [(x, top + crown - y) for x, y in fastener_geom.dome_profile(head_d / 2, crown, 0.0)]
    fig.poly(dome + [(head_d / 2, top + height), (-head_d / 2, top + height)])


def head_socket(fig: Figure, head_d: float, height: float, top: float = 0.0) -> None:
    """A socket (cylindrical) head, or any straight-sided head: a plain rectangle."""
    fig.rect(-head_d / 2, top, head_d / 2, top + height)


def head_hex(fig: Figure, across_flats: float, height: float, top: float = 0.0) -> None:
    """A hex head seen from the side."""
    hex_body(fig, across_flats, top, top + height)


# --- faces and recesses -------------------------------------------------------


def round_face(fig: Figure, centre: Point, radius: float, role: str = "part") -> None:
    """The round end of a head or body seen end on."""
    fig.disc(centre, radius, role)


def hex_face(fig: Figure, centre: Point, corner_radius: float, role: str = "part") -> None:
    """A hexagon seen end on, a corner at the top of the page's right."""
    fig.poly(regular_polygon(centre, corner_radius, 6, 30), role)


def drive_recess(fig: Figure, centre: Point, key: float) -> None:
    """A hex socket of key size ``key`` (across flats) cut into a face seen end on."""
    hex_face(fig, centre, key / math.sqrt(3), "dark")


# --- flutes -------------------------------------------------------------------


def helix_flutes(
    fig: Figure,
    dia: float,
    y0: float,
    y1: float,
    flutes: int,
    helix_deg: float,
    hand: int = 1,
) -> None:
    """The flute edges across a body of diameter ``dia`` between ``y0`` and ``y1``.

    A steeper helix angle gives a shorter lead and so more strokes; a
    helix under 5 degrees is drawn as 5, as a lead can not be infinite.
    """
    x_half = dia / 2
    lead = math.pi * dia / math.tan(math.radians(max(helix_deg, 5.0)))
    pitch = lead / flutes
    slant = dia * 0.55
    segments = []
    if pitch > 0:
        y = y0 - slant
        while y < y1:
            a = (-x_half * hand, y)
            b = (x_half * hand, y + slant)
            if a[1] >= y0 and b[1] <= y1:
                segments.append((a, b))
            y += pitch
    fig.lines(segments)


def flute_end_view(fig: Figure, centre: Point, radius: float, flutes: int, hand: int = 1) -> None:
    """The cutting end seen end on: the disc and a bent flute line per flute."""
    fig.disc(centre, radius, "plain")
    cx, cy = centre
    segments = []
    for k in range(int(flutes)):
        angle = 2 * math.pi * k / flutes
        tip = (cx + radius * math.cos(angle), cy + radius * math.sin(angle))
        bend = angle + hand * 0.6
        mid = (cx + 0.45 * radius * math.cos(bend), cy + 0.45 * radius * math.sin(bend))
        segments.append(((cx, cy), mid))
        segments.append((mid, tip))
    fig.lines(segments)


# --- rings, tubes and plates ---------------------------------------------------


def ring(fig: Figure, centre: Point, r_out: float, r_in: float) -> None:
    """A flat ring seen end on: a disc of radius ``r_out`` with a hole of ``r_in``."""
    fig.disc(centre, r_out)
    fig.disc(centre, r_in, "hole")


def tube(fig: Figure, r_out: float, r_in: float, y0: float, y1: float) -> None:
    """A hollow cylinder cut through its axis: the two walls between ``y0`` and ``y1``."""
    fig.rect(-r_out, y0, -r_in, y1, "plain")
    fig.rect(r_in, y0, r_out, y1, "plain")


def plate(
    fig: Figure,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    holes: Sequence[tuple[Point, float]] = (),
    role: str = "part",
) -> None:
    """A flat plate seen face on, with a hole at each ``(centre, radius)``."""
    fig.rect(x0, y0, x1, y1, role)
    for centre, radius in holes:
        fig.disc(centre, radius, "hole")
