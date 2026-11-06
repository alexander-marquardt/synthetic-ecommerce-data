"""Fixed shapes for the breadth categories: six plain geometric ones and five products, all in code.

The products are the C-clamp (#803) and, since the maintainer found them "a bit too square" as
boxes (#873), the ball valve, bench vise, thread pitch gage and T-slot nut.

alexander-marquardt/synthetic-ecommerce-data#34: the breadth categories
exist to fill out category BREADTH cheaply -- "just something to fill up the
image" (maintainer, 2026-09-30) -- not to be exercised in the demo, so their
drawings are not read from the record at all. Every function here returns
IDENTICAL geometry whatever it is called with: the shape says "this is
roughly a sphere / a bar / a box / a disc / a tube / a bracket" and nothing
more specific. That is the opposite of every other drawing in this package,
which reads its geometry from the record's own published values -- and it is
deliberate here: a breadth SKU's dimensions are cheap filler, and a drawing
that scaled to them would assert a precision the record does not have. A
product's sizes still differ: :mod:`.breadth_rungs` draws the same shape
smaller by its rank among them (gen#719), which says bigger or smaller and no
dimension.

Color and section hatch still come from the record's own Material/Finish
(:mod:`.style`), through the same :func:`.draw_sku` pipeline every other type
uses -- only the GEOMETRY is fixed. No test pins this: each function begins
``del record``, so the fixed geometry holds by construction.
``tests/test_breadth.py`` runs every breadth drawing through :func:`.svg_problems`
but does not compare two records' bytes.
"""

from __future__ import annotations

import math

from synthetic_ecommerce_data.core.drawing.model import Figure, arc
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn, Record


def sphere(record: Record) -> Drawn:
    """A ball: one disc."""
    del record
    fig = Figure(size_in=1.0)
    fig.disc((0.0, 0.0), 0.5)
    return Drawn(fig, "nominal")


def cylinder(record: Record) -> Drawn:
    """A round bar, rod or pin: a body with rounded ends."""
    del record
    length, dia = 2.4, 0.5
    half = length / 2
    fig = Figure(size_in=length)
    fig.rect(-half + dia / 2, -dia / 2, half - dia / 2, dia / 2)
    fig.disc((-half + dia / 2, 0.0), dia / 2)
    fig.disc((half - dia / 2, 0.0), dia / 2)
    return Drawn(fig, "nominal")


def block(record: Record) -> Drawn:
    """A rectangular part, drawn with a shallow isometric offset."""
    del record
    w, h, skew = 1.8, 1.2, 0.5
    fig = Figure(size_in=w + skew)
    fig.poly(((0.0, skew), (w, skew), (w, skew + h), (0.0, skew + h)))
    fig.poly(((0.0, skew), (skew, 0.0), (w + skew, 0.0), (w, skew)), "plain")
    fig.poly(((w, skew), (w + skew, 0.0), (w + skew, h), (w, skew + h)), "plain")
    return Drawn(fig, "nominal")


def disc(record: Record) -> Drawn:
    """A flat ring or plate: a disc with a bore."""
    del record
    od, bore = 1.6, 0.5
    fig = Figure(size_in=od)
    fig.disc((0.0, 0.0), od / 2)
    fig.disc((0.0, 0.0), bore / 2, "hole")
    return Drawn(fig, "nominal")


def tube(record: Record) -> Drawn:
    """A hollow cylinder: a body with a bore visible at each end."""
    del record
    length, od, wall = 2.2, 0.6, 0.12
    half = length / 2
    # The end discs sit INSET by their own radius, the same way ``cylinder``'s
    # rounded ends do: a disc of radius ``od / 2`` centred at
    # ``half - od / 2`` reaches exactly to ``half``, so the total extent is
    # ``length`` -- not ``length + od``, which a disc centred AT the rect's
    # edge would draw (the bug this shape shipped with once, caught by
    # ``tests/test_sku_drawings.py::test_no_product_exceeds_its_types_extent``).
    inset = half - od / 2
    fig = Figure(size_in=length)
    fig.rect(-inset, -od / 2, inset, od / 2)
    fig.disc((-inset, 0.0), od / 2)
    fig.disc((-inset, 0.0), od / 2 - wall, "hole")
    fig.disc((inset, 0.0), od / 2)
    fig.disc((inset, 0.0), od / 2 - wall, "hole")
    return Drawn(fig, "nominal")


def bracket(record: Record) -> Drawn:
    """An L-shaped angle bracket, with two mounting holes."""
    del record
    a, b, t = 1.6, 1.6, 0.3
    fig = Figure(size_in=max(a, b))
    fig.poly(((0.0, 0.0), (a, 0.0), (a, t), (t, t), (t, b), (0.0, b)))
    fig.disc((t / 2 + 0.12, b - 0.3), 0.06, "hole")
    fig.disc((a - 0.3, t / 2 + 0.12), 0.06, "hole")
    return Drawn(fig, "nominal")


def c_clamp(record: Record) -> Drawn:
    """A C-clamp: a C frame, a threaded screw through its lower boss, a swivel pad and a T-handle.

    The frame opens to the right; the screw rises through the boss at the end of the lower arm
    and presses its pad up toward the fixed jaw under the upper arm. 1.6 by 2.0 inches.
    """
    del record
    screw_x, screw_r = 1.14, 0.06
    fig = Figure(size_in=2.0)
    fig.poly(
        (
            (1.25, 0.0),
            (0.22, 0.0),
            (0.0, 0.22),
            (0.0, 1.28),
            (0.22, 1.5),
            (1.0, 1.5),
            (1.0, 1.24),
            (0.38, 1.24),
            (0.26, 1.12),
            (0.26, 0.38),
            (0.38, 0.26),
            (1.25, 0.26),
        )
    )
    fig.rect(0.98, 0.26, 1.3, 0.34, "plain")
    fig.rect(screw_x - screw_r, 0.8, screw_x + screw_r, 1.93, "plain")
    crests = [0.9 + 0.06 * i for i in range(5)] + [1.66 + 0.06 * i for i in range(4)]
    fig.lines(((screw_x - screw_r, y), (screw_x + screw_r, y - 0.03)) for y in crests)
    fig.poly(((0.98, 0.7), (1.3, 0.7), (1.26, 0.8), (1.02, 0.8)))
    fig.rect(0.98, 1.18, 1.3, 1.62)
    fig.rect(0.73, 1.89, 1.55, 1.97, "plain")
    fig.disc((0.73, 1.93), 0.05, "plain")
    fig.disc((1.55, 1.93), 0.05, "plain")
    fig.disc((screw_x, 1.93), 0.07)
    return Drawn(fig, "nominal")


#: The vinyl sleeve on a ball valve's lever: the red a quarter-turn valve's handle is sold in.
LEVER_GRIP = "#b5342b"


def _ellipse(centre: tuple[float, float], rx: float, ry: float, steps: int = 24):
    cx, cy = centre
    return [
        (cx + rx * math.cos(2 * math.pi * k / steps), cy + ry * math.sin(2 * math.pi * k / steps))
        for k in range(steps)
    ]


def ball_valve(record: Record) -> Drawn:
    """A ball valve from the side: a round body between two threaded pipe ends, and a lever.

    The pipe runs left to right through the body. The stem rises from the body's top through a
    packing nut to the lever, which lies along the pipe as an open valve's does, its end in a
    vinyl grip. 3.0 by 1.75 inches (#873).
    """
    del record
    cx, cy, r = 1.5, 1.15, 0.6
    fig = Figure(size_in=3.0)
    for x0, x1, flat in ((0.0, 0.8, 0.55), (2.2, 3.0, 2.45)):
        fig.rect(x0, cy - 0.32, x1, cy + 0.32)
        fig.lines([((flat, cy - 0.32), (flat, cy + 0.32))])
    crests = [0.06 + 0.08 * i for i in range(5)] + [2.62 + 0.08 * i for i in range(5)]
    fig.lines(((x, cy - 0.32), (x + 0.05, cy + 0.32)) for x in crests)
    fig.disc((cx, cy), r)
    fig.rect(1.43, 0.18, 1.57, 0.6, "plain")
    fig.rect(1.3, 0.42, 1.7, 0.58, "plain")
    fig.rect(1.28, 0.06, 2.5, 0.22)
    fig.disc((cx, 0.14), 0.1, "plain")
    fig.poly(
        [(2.2, 0.0), *arc((2.86, 0.14), 0.14, -90.0, 90.0, 8), (2.2, 0.28)], "grip", LEVER_GRIP
    )
    return Drawn(fig, "nominal")


def _steps(start: float, end: float, count: int) -> list[float]:
    return [start + (end - start) * k / count for k in range(count + 1)]


def bench_vise(record: Record) -> Drawn:
    """A bench vise from the side, jaws up: a fixed jaw with an anvil behind it, a sliding jaw on
    its beam, serrated jaw plates with the throat between them, the screw and its handle bar, and
    a swivel base. 2.84 by 2.4 inches (#873)."""
    del record
    fig = Figure(size_in=2.84)
    fig.rect(0.25, 2.2, 2.6, 2.4)
    fig.poly(((0.55, 2.2), (2.25, 2.2), (2.1, 2.0), (0.7, 2.0)), "plain")
    fig.rect(1.1, 1.15, 2.3, 1.45, "plain")
    fig.poly(((0.0, 0.42), (0.5, 0.42), (0.5, 0.0), (0.95, 0.0), (0.95, 0.55), (1.1, 0.55),
              (1.1, 1.2), (1.0, 2.0), (0.6, 2.0), (0.5, 0.8), (0.0, 0.8)))  # fmt: skip
    fig.poly(((1.45, 0.0), (1.95, 0.0), (1.95, 0.6), (2.1, 0.75), (2.1, 1.5), (1.35, 1.5),
              (1.35, 0.55), (1.45, 0.55)))  # fmt: skip
    fig.rect(0.95, 0.0, 1.05, 0.5, "dark")
    fig.rect(1.35, 0.0, 1.45, 0.5, "dark")
    fig.lines(((x0, y), (x0 + 0.1, y)) for x0 in (0.95, 1.35) for y in _steps(0.07, 0.42, 5))
    fig.rect(2.1, 0.95, 2.75, 1.07, "plain")
    fig.rect(2.72, 0.4, 2.8, 1.62, "plain")
    for y in (0.4, 1.62):
        fig.disc((2.76, y), 0.08, "plain")
    fig.disc((2.75, 1.01), 0.09, "plain")
    for x in (0.45, 2.4):
        fig.disc((x, 2.3), 0.05, "hole")
    return Drawn(fig, "nominal")


#: A pitch gage's fanned leaves: each one's angle (degrees, negative is up) and its tooth pitch.
GAGE_LEAVES = ((-14.0, 0.08), (-26.0, 0.1), (-38.0, 0.12), (-50.0, 0.15))


def pitch_gage(record: Record) -> Drawn:
    """A thread pitch gage: steel leaves fanned out of their case about one pivot, each with a row
    of thread teeth of its own pitch along its edge. 2.94 by 2.17 inches (#873)."""
    del record
    px, py, length, half = 0.22, 2.13, 2.55, 0.13
    fig = Figure(size_in=2.94)
    for angle, pitch in GAGE_LEAVES:
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        teeth = []
        u = length - 0.12
        while u > 0.5:
            teeth += [(u, -half), (u - pitch / 2, -half + 0.05)]
            u -= pitch
        local = [(-0.13, half), (length - 0.1, half), (length, 0.0), *teeth, (-0.13, -half)]
        fig.poly(((px + a * c - b * s, py + a * s + b * c) for a, b in local), "plain")
    fig.poly([(0.0, 1.92), (2.73, 1.92), *arc((2.73, 2.13), 0.21, -90.0, 90.0, 8), (0.0, 2.34)])
    fig.disc((px, py), 0.11, "plain")
    fig.disc((px, py), 0.04, "dark")
    return Drawn(fig, "nominal")


def t_slot_nut(record: Record) -> Drawn:
    """A T-slot nut seen along its slot, turned a little: the T of its neck and flange, their top
    faces and right sides, and the tapped hole down through the neck. 2.0 by 1.3 inches (#873)."""
    del record
    fig = Figure(size_in=2.0)
    for face in (
        ((0.0, 0.8), (0.45, 0.8), (0.85, 0.5), (0.4, 0.5)),
        ((1.15, 0.8), (1.6, 0.8), (2.0, 0.5), (1.55, 0.5)),
        ((1.6, 0.8), (2.0, 0.5), (2.0, 1.0), (1.6, 1.3)),
        ((1.15, 0.3), (1.55, 0.0), (1.55, 0.5), (1.15, 0.8)),
        ((0.45, 0.3), (1.15, 0.3), (1.55, 0.0), (0.85, 0.0)),
    ):
        fig.poly(face, "plain")
    fig.poly(((0.45, 0.3), (1.15, 0.3), (1.15, 0.8), (1.6, 0.8), (1.6, 1.3), (0.0, 1.3),
              (0.0, 0.8), (0.45, 0.8)))  # fmt: skip
    fig.poly(_ellipse((1.0, 0.15), 0.17, 0.09), "hole")
    fig.poly(_ellipse((1.0, 0.16), 0.11, 0.055), "dark")
    return Drawn(fig, "nominal")


#: One entry per fixed shape: its drawing function, and the extent
#: (:func:`..drawing.product_scale_for`) it is scaled at. Not derived from
#: any SKU's own dimensions -- these are the same numbers whatever the
#: breadth row -- so every breadth product of one shape shares one scale by
#: construction, the same guarantee :data:`..catalog.taxonomy.DRAWING` gives
#: the twelve original types.
BREADTH_SHAPES: dict[str, tuple] = {
    "sphere": (sphere, (1.0, 1.0)),
    "cylinder": (cylinder, (2.4, 0.6)),
    "block": (block, (2.3, 1.7)),
    "disc": (disc, (1.6, 1.6)),
    "tube": (tube, (2.2, 0.6)),
    "bracket": (bracket, (1.6, 1.6)),
    "c_clamp": (c_clamp, (1.6, 2.0)),
    "ball_valve": (ball_valve, (3.0, 1.75)),
    "bench_vise": (bench_vise, (2.84, 2.4)),
    "pitch_gage": (pitch_gage, (2.94, 2.17)),
    "t_slot_nut": (t_slot_nut, (2.0, 1.3)),
}
