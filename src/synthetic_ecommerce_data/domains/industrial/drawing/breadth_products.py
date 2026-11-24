"""Breadth types drawn as the product they are sold as, lit and large (#1216).

A breadth type draws one of the shared shapes of :mod:`.breadth_shapes` until it has a drawing of
its own here. A drawing here is still fixed geometry, the same whatever the record (a breadth SKU's
sizes are cheap filler, so nothing is drawn to scale), but it is the real product: its own parts,
its own colors, a highlight and a shadow (the ``gloss`` and ``shade`` overlays), filling
the figure area. :data:`BREADTH_PRODUCTS` maps a type key to its drawing; the key's row keeps its
``shape`` for the day it has none.

The light and the shared parts are in :mod:`.breadth_light`, and the second slice's drawings, of
hand tools, hardware and storage, in :mod:`.breadth_hardware`.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from synthetic_ecommerce_data.core.drawing.model import Disc, Figure, Lines, Point, Poly, arc
from synthetic_ecommerce_data.domains.industrial.drawing.breadth_hardware import HARDWARE
from synthetic_ecommerce_data.domains.industrial.drawing.breadth_light import (
    GRIP_BLUE,
    GRIP_RED,
    LAID,
    OIL,
    PAPER_LABEL,
    RUBBER,
    SAFETY,
    band,
    bar,
    col,
    disc,
    done,
    drum,
    ell,
    hexagon,
    hexes,
    laid,
    light,
    mirror,
    new,
    slab,
    thread,
)
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn, Record

# --- chain, pin and puller tools ---------------------------------------------------------------


def chain_breaker(record: Record) -> Drawn:
    """A roller chain breaker: a forged block with a chain seat, its screw and a T-bar."""
    del record
    fig = new()
    bar(fig, 0.1, 0.0, 1.54, 0.2, "plain")
    for x in (0.1, 1.54):
        disc(fig, (x, 0.1), 0.1, "plain")
    thread(fig, 0.6, 0.2, 1.04, 0.75)
    slab(fig, [(0.14, 0.7), (1.5, 0.7), (1.64, 0.9), (1.64, 2.0), (0.0, 2.0), (0.0, 0.9)])
    fig.rect(0.3, 1.3, 1.64, 1.52, "dark")
    for x in (0.55, 1.2):
        disc(fig, (x, 1.41), 0.16, "plain")
        fig.disc((x, 1.41), 0.06, "dark")
    slab(fig, [(0.72, 1.06), (0.92, 1.06), (0.87, 1.3), (0.77, 1.3)], "plain")
    return done(fig)


def _puller(jaws: int) -> Figure:
    """A jaw puller: the yoke, the forcing screw with its hex, and hooked jaws."""
    fig = new()
    hexes(fig, 0.6, 0.0, 1.04, 0.22, "plain")
    if jaws > 2:  # noqa: PLR2004 (the middle jaw hides the rest of the screw)
        thread(fig, 0.68, 0.22, 0.96, 0.74)
    else:
        thread(fig, 0.68, 0.22, 0.96, 1.6)
        slab(fig, [(0.82, 1.82), (0.68, 1.6), (0.96, 1.6)], "plain", t=0.09)
    left = [(0.0, 0.62), (0.4, 0.5), (0.48, 1.44), (0.64, 1.6), (0.64, 1.84), (0.2, 2.0),
            (0.0, 1.8)]  # fmt: skip
    slab(fig, left)
    slab(fig, mirror(left))
    if jaws > 2:  # noqa: PLR2004
        slab(fig, [(0.6, 0.7), (1.04, 0.7), (1.02, 1.58), (1.1, 1.72), (0.82, 1.94),
                    (0.54, 1.72), (0.62, 1.58)], t=0.09)  # fmt: skip
    slab(fig, [(0.0, 0.44), (0.3, 0.34), (1.34, 0.34), (1.64, 0.44), (1.64, 0.84), (1.3, 0.92),
                (0.34, 0.92), (0.0, 0.84)])  # fmt: skip
    for x in (0.2, 1.44):
        disc(fig, (x, 0.64), 0.12, "plain")
    if jaws > 2:  # noqa: PLR2004
        disc(fig, (0.82, 0.64), 0.12, "plain")
    return fig


def bearing_puller(record: Record) -> Drawn:
    """A three-jaw bearing puller."""
    del record
    return done(_puller(3))


def gear_puller(record: Record) -> Drawn:
    """A two-jaw sprocket puller."""
    del record
    return done(_puller(2))


def pin_puller(record: Record) -> Drawn:
    """A dowel pin puller: a collet, a rod with its slide weight and a stop knob, corner to
    corner."""
    del record
    fig = new()
    col(fig, 0.0, 0.0, 0.62, 0.2, "plain")
    col(fig, 0.2, 0.2, 0.42, 1.0, "plain")
    col(fig, 0.0, 0.5, 0.62, 1.2)
    for y in (0.6, 0.72, 0.98, 1.1):
        fig.lines([((0.0, y), (0.62, y))])
    col(fig, 0.2, 1.2, 0.42, 1.5, "plain")
    col(fig, 0.06, 1.5, 0.56, 1.95)
    slab(fig, [(0.06, 1.95), (0.56, 1.95), (0.42, 2.25), (0.2, 2.25)], "plain")
    col(fig, 0.25, 2.25, 0.37, 2.4, "plain")
    return done(laid(fig, LAID))


def chain_tensioner(record: Record) -> Drawn:
    """A chain tensioner: a slotted zinc arm and the idler sprocket it presses on the chain."""
    del record
    fig = new()
    slab(fig, [(0.22, 0.85), (1.42, 0.85), (1.42, 1.36), (1.64, 1.46), (1.64, 2.0), (0.0, 2.0),
                (0.0, 1.46), (0.22, 1.36)])  # fmt: skip
    for x in (0.25, 1.39):
        fig.disc((x, 1.78), 0.09, "hole")
    fig.rect(0.74, 1.35, 0.9, 1.72, "dark")
    cx, cy, teeth = 0.82, 0.72, 14
    pts = []
    for k in range(teeth):
        for off, r in ((-0.3, 0.6), (-0.13, 0.72), (0.13, 0.72), (0.3, 0.6)):
            a = 2 * math.pi * (k + off) / teeth
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    fig.poly(pts, "plain")
    disc(fig, (cx, cy), 0.54)
    disc(fig, (cx, cy), 0.24, "plain")
    fig.disc((cx, cy), 0.1, "dark")
    return done(fig)


def drive_guard(record: Record) -> Drawn:
    """A sprocket and chain guard: a powder-coated cover round both sprockets, louvred, with
    bolt tabs."""
    del record
    fig = new()
    for y in (0.62, 1.3):
        fig.rect(0.0, y, 1.64, y + 0.16, "plain")
        for x in (0.07, 1.57):
            fig.disc((x, y + 0.08), 0.03, "dark")
    cx, r = 0.82, 0.68
    body = [*arc((cx, r), r, 180, 360, 14), *arc((cx, 2.0 - r), r, 0, 180, 14)]
    fig.poly(body)
    fig.rect(cx - r + 0.1, r, cx - r + 0.24, 2.0 - r, "gloss")
    fig.poly([(cx + r - 0.3, r), (cx + r, r), *arc((cx, 2.0 - r), r, 0, 70, 8)], "shade")
    for k in range(5):
        y = 0.62 + 0.18 * k
        fig.rect(0.5, y, 1.14, y + 0.08, "dark")
    for y in (0.25, 1.75):
        disc(fig, (cx, y), 0.09, "plain")
    return done(fig)


def grinder_guard(record: Record) -> Drawn:
    """An angle grinder guard: a half-round steel shroud with its clamp collar and screw."""
    del record
    fig = new()
    c, r = (0.82, 0.82), 0.82
    skirt = [*arc(c, r, 160, 380, 22), (1.6, 1.4), *ell((0.82, 1.4), 0.78, 0.5, 0, 180, 14)]
    fig.poly(skirt)
    fig.poly([*arc(c, r, 160, 260, 12), *arc(c, r - 0.16, 260, 160, 12)], "gloss")
    fig.poly([(1.2, 1.25), (1.6, 1.15), (1.6, 1.4), *ell((0.82, 1.4), 0.78, 0.5, 0, 65, 8)],
             "shade")  # fmt: skip
    fig.poly(ell((0.82, 1.28), 0.62, 0.34), "dark")
    disc(fig, (0.82, 0.78), 0.42, "plain", bore=0.3)
    fig.disc((0.82, 0.78), 0.28, "hole")
    bar(fig, 1.16, 0.68, 1.6, 0.9, "plain")
    disc(fig, (1.48, 0.79), 0.09, "plain")
    return done(fig)


# --- cutters, pliers and clamps ----------------------------------------------------------------


def bolt_cutter(record: Record) -> Drawn:
    """A bolt cutter: two long handles with rubber grips, the bolted head and its jaws, open."""
    del record
    fig = new()
    arm = [(0.44, 0.62), (0.8, 0.66), (0.8, 0.95), (0.44, 2.0), (0.0, 2.0), (0.0, 1.9)]
    grip = [(0.28, 1.16), (0.72, 1.18), (0.5, 2.0), (0.0, 2.0), (0.0, 1.84)]
    jaw = [(0.78, 0.0), (0.82, 0.26), (0.8, 0.66), (0.36, 0.72), (0.28, 0.36), (0.5, 0.06)]
    for flip in (list, mirror):
        slab(fig, flip(arm))
        slab(fig, flip(grip), "handle", GRIP_RED)
        slab(fig, flip(jaw))
    for x in (0.5, 1.14):
        disc(fig, (x, 0.6), 0.13, "plain")
    disc(fig, (0.82, 0.86), 0.12, "plain")
    return done(fig)


def lock_nut_pliers(record: Record) -> Drawn:
    """Lock nut pliers: curved jaws round a lock nut, a riveted pivot and dipped grips."""
    del record
    fig = new()
    grip = [(0.26, 0.98), (0.78, 1.0), (0.74, 1.4), (0.64, 2.0), (0.06, 2.0), (0.0, 1.5)]
    jaw = [(0.8, 0.0), (0.46, 0.0), (0.08, 0.24), (0.06, 0.72), (0.4, 1.02), (0.82, 1.0),
           (0.82, 0.62), (0.6, 0.5), (0.6, 0.34), (0.78, 0.24)]  # fmt: skip
    for flip in (list, mirror):
        slab(fig, flip(grip), "handle", GRIP_BLUE)
        slab(fig, flip(jaw))
    disc(fig, (0.82, 0.86), 0.17, "plain")
    fig.disc((0.82, 0.86), 0.05, "dark")
    return done(fig)


def c_clamp(record: Record) -> Drawn:
    """A C-clamp: a forged frame, the screw through its lower boss, a swivel pad and a T-bar."""
    del record
    fig = new()
    thread(fig, 0.94, 0.78, 1.26, 1.8, 0.09)
    frame = [(1.5, 0.0), (0.3, 0.0), (0.0, 0.3), (0.0, 1.22), (0.3, 1.54), (1.5, 1.54),
             (1.5, 1.14), (0.62, 1.14), (0.46, 1.0), (0.46, 0.5), (0.6, 0.38),
             (1.5, 0.38)]  # fmt: skip
    slab(fig, frame, t=0.08)
    slab(fig, [(0.84, 0.38), (1.36, 0.38), (1.36, 0.5), (0.84, 0.5)], "plain")
    slab(fig, [(0.8, 0.64), (1.4, 0.64), (1.3, 0.8), (0.9, 0.8)], "plain")
    col(fig, 0.82, 1.1, 1.38, 1.6)
    bar(fig, 0.56, 1.78, 1.64, 1.98, "plain")
    disc(fig, (1.1, 1.88), 0.14, "plain")
    return done(fig)


# --- bits, gauges and threaded parts -----------------------------------------------------------


def drill_stop_collar(record: Record) -> Drawn:
    """A drill stop collar: a thick steel ring seen from above, its bore and its set screw."""
    del record
    fig = new()
    drum(fig, 0.0, 0.0, 1.64, 2.0, 0.44)
    fig.poly(ell((0.82, 0.44), 0.66, 0.34), "plain")
    fig.poly(ell((0.82, 0.44), 0.4, 0.2), "dark")
    disc(fig, (0.78, 1.36), 0.27, "plain")
    fig.poly(hexagon((0.78, 1.36), 0.15), "dark")
    return done(fig)


def sds_drill_bit(record: Record) -> Drawn:
    """An SDS-Plus hammer drill bit, corner to corner: a carbide tip, a twin flute and the slotted
    shank."""
    del record
    fig = new()
    w = 0.44
    slab(fig, [(0.04, 0.16), (w / 2, 0.0), (w - 0.04, 0.16), (w - 0.04, 0.3), (0.04, 0.3)],
          "plain")  # fmt: skip
    col(fig, 0.02, 0.3, w - 0.02, 1.7)
    for k in range(6):
        y = 0.34 + 0.22 * k
        fig.poly([(0.02, y + 0.2), (w - 0.02, y), (w - 0.02, y + 0.09), (0.02, y + 0.29)], "dark")
    col(fig, 0.05, 1.7, w - 0.05, 2.5, "plain")
    for x in (0.1, 0.26):
        fig.rect(x, 1.95, x + 0.07, 2.35, "dark")
    return done(laid(fig, LAID))


def sleeve_anchor(record: Record) -> Drawn:
    """A hex-head sleeve anchor: the bolt head, its washer, the split sleeve and the cone."""
    del record
    fig = new()
    hexes(fig, 0.14, 0.0, 1.5, 0.38)
    bar(fig, 0.0, 0.38, 1.64, 0.5, "plain")
    col(fig, 0.3, 0.5, 1.34, 1.64)
    fig.lines(((x, 0.7), (x, 1.64)) for x in (0.62, 1.02))
    for y in (0.78, 1.3):
        fig.rect(0.5, y, 0.6, y + 0.2, "dark")
    slab(fig, [(0.3, 1.64), (1.34, 1.64), (1.42, 2.0), (0.22, 2.0)], "plain")
    return done(fig)


def tap_extractor(record: Record) -> Drawn:
    """A tap extractor, corner to corner: its square drive, holder, sliding sleeve and four
    fingers."""
    del record
    fig = new()
    col(fig, 0.16, 0.0, 0.44, 0.3, "plain")
    col(fig, 0.02, 0.3, 0.58, 1.05)
    col(fig, 0.0, 1.05, 0.6, 1.5, "plain")
    for k in range(5):
        fig.lines([((0.0, 1.1 + 0.08 * k), (0.6, 1.1 + 0.08 * k))])
    for k in range(4):
        x = 0.06 + 0.125 * k
        col(fig, x, 1.5, x + 0.1, 2.2)
    return done(laid(fig, LAID))


def thread_chaser(record: Record) -> Drawn:
    """A hex rethreading chaser for a bolt: a hex body, its threaded bore and chip holes."""
    del record
    fig = new()
    c = (0.82, 0.947)
    slab(fig, hexagon(c, 0.947), t=0.1)
    disc(fig, c, 0.64, "plain", bore=0.42)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        fig.disc((c[0] + 0.38 * math.cos(a), c[1] + 0.38 * math.sin(a)), 0.14, "dark")
    disc(fig, c, 0.32, "dark")
    for k in range(4):
        a = math.radians(90 * k)
        fig.disc((c[0] + 0.3 * math.cos(a), c[1] + 0.3 * math.sin(a)), 0.07, "plain")
    fig.disc(c, 0.2, "hole")
    return done(fig)


def thread_plug_gage(record: Record) -> Drawn:
    """A go/no-go thread plug gage, corner to corner: a hex handle with a long go end, a short
    no-go end and its red ring."""
    del record
    fig = new()
    thread(fig, 0.09, 0.0, 0.51, 0.62, 0.07)
    col(fig, 0.16, 0.62, 0.44, 0.7, "plain")
    hexes(fig, 0.0, 0.7, 0.6, 1.66)
    bar(fig, 0.0, 1.66, 0.6, 1.76, "handle", GRIP_RED)
    thread(fig, 0.09, 1.76, 0.51, 2.1, 0.07)
    return done(laid(fig, LAID))


def eye_bolt(record: Record) -> Drawn:
    """A shoulder eye bolt: the forged eye, its shoulder and the threaded shank."""
    del record
    fig = new()
    thread(fig, 0.46, 1.4, 1.18, 2.0)
    slab(fig, [(0.3, 1.16), (1.34, 1.16), (1.46, 1.42), (0.18, 1.42)])
    disc(fig, (0.82, 0.68), 0.68, bore=0.32)
    fig.disc((0.82, 0.68), 0.3, "hole")
    return done(fig)


def magnetic_bit_holder(record: Record) -> Drawn:
    """A magnetic bit holder, corner to corner: a steel sleeve over the bit socket and its
    quarter-inch hex shank."""
    del record
    fig = new()
    hexes(fig, 0.14, 0.0, 0.46, 0.9, "plain")
    bar(fig, 0.16, 0.2, 0.44, 0.32, "dark")
    col(fig, 0.0, 0.9, 0.6, 2.2)
    bar(fig, 0.0, 1.1, 0.6, 1.24, "handle", GRIP_BLUE)
    hexes(fig, 0.17, 2.2, 0.43, 2.36, "plain")
    return done(laid(fig, LAID))


def orb_fitting(record: Record) -> Drawn:
    """An ORB hydraulic fitting: the flared tube end, the hex, the O-ring and the straight
    thread."""
    del record
    fig = new()
    slab(fig, [(0.5, 0.0), (1.14, 0.0), (1.28, 0.18), (0.36, 0.18)], "plain")
    thread(fig, 0.32, 0.18, 1.32, 0.68)
    hexes(fig, 0.0, 0.68, 1.64, 1.24)
    col(fig, 0.36, 1.24, 1.28, 1.3, "plain")
    bar(fig, 0.2, 1.28, 1.44, 1.44, "handle", RUBBER)
    thread(fig, 0.28, 1.44, 1.36, 1.94)
    slab(fig, [(0.28, 1.94), (1.36, 1.94), (1.3, 2.0), (0.34, 2.0)], "plain")
    return done(fig)


def shackle_pin(record: Record) -> Drawn:
    """A screw pin for a shackle: the eye it is turned by, its collar, the shank and the thread."""
    del record
    fig = new()
    disc(fig, (0.82, 0.42), 0.42, bore=0.16)
    fig.disc((0.82, 0.4), 0.14, "hole")
    bar(fig, 0.22, 0.76, 1.42, 0.94, "plain")
    col(fig, 0.42, 0.94, 1.22, 1.5)
    thread(fig, 0.46, 1.5, 1.18, 2.0)
    return done(fig)


def zerk_fitting(record: Record) -> Drawn:
    """A straight grease fitting: the ball nipple, its neck, the hex and the tapered thread."""
    del record
    fig = new()
    disc(fig, (0.82, 0.28), 0.28, "plain")
    fig.disc((0.82, 0.16), 0.07, "dark")
    slab(fig, [(0.6, 0.5), (1.04, 0.5), (1.3, 0.72), (0.34, 0.72)])
    hexes(fig, 0.0, 0.72, 1.64, 1.22)
    thread(fig, 0.2, 1.22, 1.44, 1.96)
    slab(fig, [(0.2, 1.96), (1.44, 1.96), (1.3, 2.0), (0.34, 2.0)], "plain")
    return done(fig)


def alignment_laser(record: Record) -> Drawn:
    """A sprocket alignment laser: an aluminum body, its lens, switch and magnetic feet."""
    del record
    fig = new()
    slab(fig, [(0.16, 0.0), (1.48, 0.0), (1.64, 0.16), (1.64, 1.6), (0.0, 1.6), (0.0, 0.16)],
          t=0.1)  # fmt: skip
    fig.rect(0.1, 0.94, 1.54, 1.14, "handle", SAFETY)
    for x in (0.06, 1.12):
        col(fig, x, 1.6, x + 0.46, 2.0, "plain")
    disc(fig, (0.82, 0.5), 0.34, "plain")
    disc(fig, (0.82, 0.5), 0.2, "dark")
    fig.disc((0.82, 0.5), 0.09, "handle", GRIP_RED)
    fig.rect(0.64, 1.24, 1.0, 1.44, "handle", RUBBER)
    return done(fig)


# --- containers and kits -----------------------------------------------------------------------


def grease_tub(record: Record) -> Drawn:
    """A tub of bearing grease: a lidded tub and its label."""
    del record
    fig = new()
    drum(fig, 0.06, 0.28, 1.58, 2.0, 0.26, "handle", GRIP_BLUE)
    band(fig, 0.06, 0.94, 1.58, 1.5, 0.26, PAPER_LABEL)
    drum(fig, 0.0, 0.0, 1.64, 0.74, 0.26, "handle", RUBBER)
    fig.poly(ell((0.82, 0.26), 0.66, 0.18), "gloss")
    fig.disc((0.82, 1.45), 0.2, "handle", OIL)
    return done(fig)


def threadlocker_bottle(record: Record) -> Drawn:
    """A threadlocker bottle: a red squeeze bottle, its label and its dropper nozzle and cap."""
    del record
    fig = new()
    slab(fig, [(0.68, 0.0), (0.96, 0.0), (1.08, 0.4), (0.56, 0.4)], "plain")
    bar(fig, 0.46, 0.38, 1.18, 0.54, "handle", RUBBER)
    body = [(0.46, 0.54), (1.18, 0.54), (1.5, 0.78), (1.64, 1.0), (1.64, 1.88), (1.52, 2.0),
            (0.12, 2.0), (0.0, 1.88), (0.0, 1.0), (0.14, 0.78)]  # fmt: skip
    fig.poly(body, "handle", GRIP_RED)
    fig.poly([(0.46, 0.54), (0.62, 0.54), (0.3, 0.86), (0.3, 1.95), (0.12, 1.95), (0.14, 0.82)],
             "gloss")  # fmt: skip
    fig.poly([(1.5, 0.78), (1.64, 1.0), (1.64, 1.88), (1.52, 2.0), (1.2, 2.0), (1.2, 0.78)],
             "shade")  # fmt: skip
    fig.rect(0.36, 1.08, 1.4, 1.68, "handle", PAPER_LABEL)
    fig.lines(((0.5, y), (1.26, y)) for y in (1.24, 1.38, 1.52))
    return done(fig)


def anti_seize_can(record: Record) -> Drawn:
    """A brush-top can of anti-seize: a metal can, its screw cap and a label."""
    del record
    fig = new()
    drum(fig, 0.04, 0.42, 1.6, 2.0, 0.24)
    band(fig, 0.04, 0.96, 1.6, 1.56, 0.24, SAFETY)
    drum(fig, 0.32, 0.0, 1.32, 0.7, 0.16, "handle", RUBBER)
    fig.lines(((x, 0.22), (x, 0.56)) for x in (0.5, 0.66, 0.82, 0.98, 1.14))
    return done(fig)


def aerosol_can(record: Record) -> Drawn:
    """An aerosol of chain lubricant: the can, its shoulder, valve, cap and label."""
    del record
    fig = new()
    drum(fig, 0.0, 0.5, 0.9, 2.0, 0.1, "handle", GRIP_BLUE)
    band(fig, 0.0, 0.98, 0.9, 1.5, 0.1, PAPER_LABEL)
    slab(fig, [(0.14, 0.38), (0.76, 0.38), (0.9, 0.58), (0.0, 0.58)], "plain")
    col(fig, 0.16, 0.02, 0.74, 0.4, "handle", GRIP_RED)
    fig.rect(0.14, 1.12, 0.76, 1.2, "handle", OIL)
    return done(fig)


def grease_tube(record: Record) -> Drawn:
    """A squeeze tube of silicone grease: the folded crimp, the flattened body and the cap."""
    del record
    fig = new()
    slab(fig, [(0.0, 0.0), (1.64, 0.0), (1.64, 0.2), (0.0, 0.2)], "plain")
    body = [(0.0, 0.2), (1.64, 0.2), (1.44, 1.45), (1.2, 1.62), (0.44, 1.62), (0.2, 1.45)]
    fig.poly(body, "handle", PAPER_LABEL)
    fig.poly([(0.18, 0.2), (0.4, 0.2), (0.5, 1.45), (0.36, 1.45)], "gloss")
    fig.poly([(1.2, 0.2), (1.64, 0.2), (1.44, 1.45), (1.2, 1.62), (1.1, 1.62)], "shade")
    fig.poly([(0.22, 0.5), (1.42, 0.5), (1.36, 0.95), (0.28, 0.95)], "handle", GRIP_BLUE)
    col(fig, 0.4, 1.62, 1.24, 2.0, "handle", RUBBER)
    return done(fig)


def tapping_fluid_can(record: Record) -> Drawn:
    """A can of tapping fluid: an oblong can, its spout and cap, and its label."""
    del record
    fig = new()
    slab(fig, [(0.66, 0.0), (0.98, 0.0), (1.06, 0.36), (0.58, 0.36)], "handle", GRIP_RED)
    bar(fig, 0.46, 0.34, 1.18, 0.5, "handle", RUBBER)
    slab(fig, [(0.2, 0.5), (1.44, 0.5), (1.64, 0.68), (0.0, 0.68)], "plain")
    col(fig, 0.0, 0.68, 1.64, 2.0, "handle", OIL)
    fig.rect(0.16, 0.92, 1.48, 1.66, "handle", PAPER_LABEL)
    light(fig, (0.16, 0.92, 1.48, 1.66))
    fig.lines(((0.4, y), (1.24, y)) for y in (1.1, 1.28, 1.46))
    return done(fig)


def splicing_kit(record: Record) -> Drawn:
    """An O-ring cord splicing kit: the open case with a coil of cord, a bottle of adhesive, a
    splicing block and a cutter."""
    del record
    fig = new()
    slab(fig, [(0.0, 0.0), (1.64, 0.0), (1.64, 2.0), (0.0, 2.0)], "handle", GRIP_BLUE, 0.1)
    fig.rect(0.12, 0.12, 1.52, 1.88, "plain")
    disc(fig, (0.6, 0.6), 0.44, "handle", RUBBER, bore=0.2)
    fig.disc((0.6, 0.6), 0.2, "plain")
    for r in (0.28, 0.36):
        ring = ell((0.6, 0.6), r, r, steps=20)
        fig.lines(zip(ring, ring[1:], strict=False))
    col(fig, 1.16, 0.5, 1.42, 1.06, "handle", GRIP_RED)
    slab(fig, [(1.24, 0.22), (1.34, 0.22), (1.4, 0.5), (1.18, 0.5)], "plain")
    slab(fig, [(0.2, 1.2), (0.8, 1.2), (0.8, 1.76), (0.2, 1.76)])
    fig.poly([(0.3, 1.2), (0.42, 1.2), (0.36, 1.4)], "dark")
    slab(fig, [(0.96, 1.2), (1.16, 1.2), (1.44, 1.76), (1.2, 1.76)], "handle", SAFETY)
    return done(fig)


def ring_dispenser(record: Record) -> Drawn:
    """A retaining ring dispenser: a stack of rings on its post, over a weighted base."""
    del record
    fig = new()
    drum(fig, 0.66, 0.0, 0.98, 0.5, 0.06)
    drum(fig, 0.16, 0.3, 1.48, 1.66, 0.2, "handle", RUBBER)
    for k in range(9):
        edge = ell((0.82, 0.56 + 0.12 * k), 0.66, 0.2, 0, 180, 12)
        fig.lines(zip(edge, edge[1:], strict=False))
    drum(fig, 0.0, 1.4, 1.64, 2.0, 0.2)
    return done(fig)


#: The breadth types drawn as their own product: type key -> its drawing.
BREADTH_PRODUCTS: dict[str, Callable[[Record], Drawn]] = {
    **HARDWARE,
    "anaerobic_threadlockers": threadlocker_bottle,
    "anti_seize_compounds": anti_seize_can,
    "bearing_greases": grease_tub,
    "bearing_pullers": bearing_puller,
    "c_clamps": c_clamp,
    "chain_breakers": chain_breaker,
    "chain_lubricants": aerosol_can,
    "chain_tensioners": chain_tensioner,
    "compound_cutters": bolt_cutter,
    "conduit_pliers": lock_nut_pliers,
    "cord_splicing_kits": splicing_kit,
    "drill_stop_collars": drill_stop_collar,
    "drive_guards": drive_guard,
    "eye_bolts": eye_bolt,
    "fastener_dispensers": ring_dispenser,
    "gear_pullers": gear_puller,
    "grinder_guards": grinder_guard,
    "magnetic_bit_holders": magnetic_bit_holder,
    "orb_hydraulic_fittings": orb_fitting,
    "pin_pullers": pin_puller,
    "replacement_pins": shackle_pin,
    "sds_drill_bits": sds_drill_bit,
    "shaft_alignment_lasers": alignment_laser,
    "silicone_greases": grease_tube,
    "sleeve_anchors": sleeve_anchor,
    "tap_extractors": tap_extractor,
    "tapping_fluids": tapping_fluid_can,
    "thread_chasers": thread_chaser,
    "thread_plug_gages": thread_plug_gage,
    "zerk_grease_fittings": zerk_fitting,
}


def outline(fig: Figure) -> tuple[Point, ...]:
    """The points a figure's drawn shapes reach, about the centre of its box: what its scale is
    fitted to at each angle (:data:`...core.drawing.product_look.OUTLINES`)."""
    x0, y0, x1, y1 = fig.bounds()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    points: list[Point] = []
    for shape in fig.shapes:
        if isinstance(shape, Poly):
            points += shape.points
        elif isinstance(shape, Disc):
            points += ell(shape.centre, shape.radius, shape.radius, steps=32)
        elif isinstance(shape, Lines):
            points += [p for segment in shape.segments for p in segment]
        else:
            raise TypeError(f"{type(shape).__name__} has no outline")
    return tuple((x - cx, y - cy) for x, y in points)
