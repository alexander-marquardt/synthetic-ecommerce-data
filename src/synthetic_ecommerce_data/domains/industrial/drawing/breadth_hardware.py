"""Breadth types drawn as their own product, second slice: hand tools, hardware and storage (#1216).

Fixed geometry, lit, laid out as :mod:`.breadth_products` says. :data:`HARDWARE` maps a type key to
its drawing; ``BREADTH_PRODUCTS`` holds it.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from synthetic_ecommerce_data.core.drawing.model import Figure, Point, arc
from synthetic_ecommerce_data.domains.industrial.drawing.breadth_light import (
    BOX,
    GRIP_BLUE,
    GRIP_RED,
    LAID,
    PAPER_LABEL,
    RUBBER,
    SAFETY,
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

FOAM = "#e8902f"
WALNUT = "#8a5a34"
BELT = "#6b6f76"
SOCK = "#8d949c"


def _case(fig: Figure, fill: str, split: float = 0.0) -> None:
    """A molded case seen from above: its shell, the recessed tray, and below ``split`` the line
    its lid folds on."""
    slab(fig, [(0.0, 0.1), (0.1, 0.0), (1.54, 0.0), (1.64, 0.1), (1.64, 1.9), (1.54, 2.0),
               (0.1, 2.0), (0.0, 1.9)], "handle", fill, t=0.07)  # fmt: skip
    if split:
        fig.rect(0.0, split - 0.02, 1.64, split + 0.02, "dark")


def _bolt(fig: Figure, c: Point, r: float) -> None:
    """A screw head with its hex recess."""
    disc(fig, c, r, "plain", steps=4)
    fig.poly(hexagon(c, r * 0.5), "dark")


def _screwdriver(fig: Figure, x: float, y0: float, y1: float, w: float, grip: str) -> None:
    """A screwdriver hung by its handle: the grip on top, the blade below."""
    mid = y0 + 0.45 * (y1 - y0)
    fig.rect(x + w * 0.36, mid, x + w * 0.64, y1, "plain")
    col(fig, x, y0, x + w, mid, "handle", grip)
    fig.rect(x + w * 0.1, mid, x + w * 0.9, mid + 0.08, "plain")


# --- hand tools --------------------------------------------------------------------------------


def hex_key(record: Record) -> Drawn:
    """A long-arm hex key: a black L of hex bar, its bend and its chamfered ends."""
    del record
    fig = new()
    t, r = 0.34, 0.42
    inner = r - t * 0.6
    pts = [(0.0, 0.04), (0.05, 0.0), (t - 0.05, 0.0), (t, 0.04), (t, 2.0 - t - inner)]
    pts += [*reversed(arc((t + inner, 2.0 - t - inner), inner, 90, 180, 6))]
    pts += [(1.06, 2.0 - t), (1.1, 2.0 - t + 0.05), (1.1, 1.95), (1.06, 2.0), (r, 2.0)]
    pts += [*arc((r, 2.0 - r), r, 90, 180, 8)]
    fig.poly(pts)
    fig.rect(0.0, 0.04, t * 0.27, 2.0 - r, "gloss")
    fig.rect(t * 0.73, 0.04, t, 2.0 - t - inner, "shade")
    fig.rect(r, 2.0 - t * 0.27, 1.06, 2.0, "shade")
    fig.rect(t + inner, 2.0 - t, 1.06, 2.0 - t * 0.73, "gloss")
    return done(laid(fig, -12))


def nut_driver(record: Record) -> Drawn:
    """A hollow-shaft nut driver, corner to corner: a fluted grip, the shaft and the hex socket."""
    del record
    fig = new()
    col(fig, 0.06, 0.0, 0.62, 0.14, "handle", RUBBER)
    col(fig, 0.0, 0.14, 0.68, 0.95, "handle", GRIP_RED)
    fig.lines(((x, 0.2), (x, 0.88)) for x in (0.1, 0.24, 0.44, 0.58))
    slab(fig, [(0.0, 0.95), (0.68, 0.95), (0.54, 1.1), (0.14, 1.1)], "handle", RUBBER)
    col(fig, 0.2, 1.1, 0.48, 1.75, "plain")
    hexes(fig, 0.12, 1.75, 0.56, 2.15)
    fig.rect(0.22, 2.05, 0.46, 2.15, "dark")
    return done(laid(fig, LAID))


def spanner_wrench(record: Record) -> Drawn:
    """An adjustable hook spanner: the hinged hook, its pivot, and the handle with its hang hole."""
    del record
    fig = new()
    c = (0.82, 0.7)
    hook = [*arc(c, 0.7, 120, 395, 22), (1.14, 0.96), *arc(c, 0.4, 385, 150, 18), (0.5, 1.1)]
    slab(fig, hook, t=0.06)
    fig.poly([(1.12, 1.16), (1.4, 1.1), (1.2, 0.84), (0.98, 0.9)], "plain")
    slab(fig, [(0.16, 0.82), (0.62, 0.96), (0.76, 1.3), (0.86, 1.9), (0.72, 2.0), (0.44, 2.0),
               (0.3, 1.9), (0.18, 1.3)], t=0.07)  # fmt: skip
    disc(fig, (0.38, 1.02), 0.15, "plain")
    fig.disc((0.38, 1.02), 0.05, "dark")
    fig.disc((0.58, 1.8), 0.09, "hole")
    return done(fig)


def thread_file(record: Record) -> Drawn:
    """A thread restoring file, corner to corner: a square bar toothed at both ends in different
    pitches."""
    del record
    fig = new()
    hexes(fig, 0.0, 0.6, 0.6, 1.6, "handle")
    for y0, pitch in ((0.0, 0.07), (1.6, 0.11)):
        col(fig, 0.04, y0, 0.56, y0 + 0.6)
        for k in range(int(0.56 / pitch)):
            y = y0 + 0.04 + pitch * k
            fig.poly([(0.04, y), (0.56, y), (0.56, y + pitch * 0.4), (0.04, y + pitch * 0.4)],
                     "dark")  # fmt: skip
    return done(laid(fig, LAID))


def snap_ring_pliers(record: Record) -> Drawn:
    """Convertible retaining ring pliers: two fine tips, the pivot and the dipped grips."""
    del record
    fig = new()
    grip = [(0.24, 0.96), (0.8, 1.0), (0.78, 1.4), (0.66, 2.0), (0.06, 2.0), (0.0, 1.46)]
    jaw = [(0.8, 0.12), (0.7, 0.06), (0.36, 0.3), (0.14, 0.66), (0.36, 1.04), (0.82, 1.02)]
    for flip in (list, mirror):
        slab(fig, flip(grip), "handle", GRIP_RED)
        slab(fig, flip(jaw))
    for x in (0.62, 1.02):
        col(fig, x - 0.06, 0.0, x + 0.06, 0.22, "plain")
    disc(fig, (0.82, 0.8), 0.22, "plain")
    _bolt(fig, (0.82, 0.8), 0.12)
    return done(fig)


def cold_chisel(record: Record) -> Drawn:
    """A cold chisel, corner to corner: a hex body, a struck head and the forged cutting edge."""
    del record
    fig = new()
    slab(fig, [(0.1, 0.0), (0.6, 0.0), (0.7, 0.14), (0.0, 0.14)], "plain")
    hexes(fig, 0.0, 0.14, 0.7, 1.4)
    slab(fig, [(0.0, 1.4), (0.7, 1.4), (0.62, 1.95), (0.08, 1.95)])
    slab(fig, [(0.08, 1.95), (0.62, 1.95), (0.5, 2.15), (0.2, 2.15)], "plain")
    return done(laid(fig, LAID))


def pneumatic_cut_off_tool(record: Record) -> Drawn:
    """An air cut-off tool: the wheel under its guard, the body, its lever and air inlet."""
    del record
    fig = new()
    c = (0.82, 0.72)
    disc(fig, c, 0.72, "handle", RUBBER, bore=0.2)
    fig.poly([*arc(c, 0.82, 190, 400, 22), *arc(c, 0.5, 400, 190, 16)])
    fig.poly([*arc(c, 0.8, 200, 280, 10), *arc(c, 0.7, 280, 200, 10)], "gloss")
    fig.poly([*arc(c, 0.82, 340, 400, 8), *arc(c, 0.6, 400, 340, 8)], "shade")
    disc(fig, c, 0.2, "plain")
    _bolt(fig, c, 0.11)
    col(fig, 0.4, 0.92, 1.24, 1.82)
    for y in (1.5, 1.6, 1.7):
        fig.lines([((0.4, y), (1.24, y))])
    slab(fig, [(1.16, 1.0), (1.5, 1.1), (1.5, 1.8), (1.24, 1.72)], "handle", GRIP_RED)
    bar(fig, 0.5, 1.76, 1.14, 1.9, "plain")
    hexes(fig, 0.62, 1.86, 1.02, 2.0, "plain")
    return done(fig)


# --- sets --------------------------------------------------------------------------------------


def _hex_bit(fig: Figure, x: float, y: float, w: float, h: float) -> None:
    """A hex bit socket: the chrome socket and the hex bit in it."""
    hexes(fig, x + w * 0.3, y + h * 0.5, x + w * 0.7, y + h)
    col(fig, x, y, x + w, y + h * 0.6, "plain")
    bar(fig, x, y + h * 0.4, x + w, y + h * 0.48, "dark")


def _small_hex_bit(fig: Figure, x: float, y: float, w: float, h: float) -> None:
    """:func:`_hex_bit` in a set of many, in four shapes: a drawing has a size cap."""
    fig.rect(x + w * 0.3, y + h * 0.5, x + w * 0.7, y + h, "plain")
    fig.rect(x, y, x + w, y + h * 0.6, "plain")
    fig.rect(x + w * 0.12, y, x + w * 0.3, y + h * 0.6, "gloss")
    fig.rect(x + w * 0.64, y, x + w, y + h * 0.6, "shade")


def bit_socket_set(record: Record) -> Drawn:
    """A hex key bit socket set on a ratchet: the case, the ratchet and two rows of bits."""
    del record
    fig = new()
    _case(fig, RUBBER)
    fig.rect(0.1, 0.12, 1.54, 0.72, "handle", GRIP_BLUE)
    bar(fig, 0.5, 0.34, 1.48, 0.52, "handle", GRIP_RED)
    bar(fig, 0.24, 0.36, 0.64, 0.5, "plain")
    disc(fig, (0.34, 0.43), 0.22, "plain", steps=6)
    fig.rect(0.28, 0.37, 0.4, 0.49, "dark")
    for row in range(2):
        fig.rect(0.1, 0.8 + 0.58 * row, 1.54, 1.3 + 0.58 * row, "dark")
        for k in range(5):
            _small_hex_bit(fig, 0.16 + 0.28 * k, 0.86 + 0.58 * row, 0.2, 0.4)
    return done(fig)


def hex_bit_socket_set(record: Record) -> Drawn:
    """A hex bit socket set on its rail: four sockets, the smallest first, clipped in a row."""
    del record
    fig = new()
    bar(fig, 0.0, 0.0, 1.64, 0.34, "handle", GRIP_RED)
    for k in range(4):
        w = 0.28 + 0.035 * k
        x = 0.02 + 0.4 * k + (0.4 - w) / 2
        fig.rect(x - 0.01, 0.16, x + w + 0.01, 0.34, "dark")
        _hex_bit(fig, x, 0.2, w, 1.62 + 0.04 * k)
    bar(fig, 0.0, 1.78, 1.64, 2.0, "handle", GRIP_RED)
    return done(fig)


def driver_bit_set(record: Record) -> Drawn:
    """A screwdriver bit set: an open case, its bit holder and rows of colored-collar bits."""
    del record
    fig = new()
    _case(fig, GRIP_RED, 0.82)
    fig.rect(0.1, 0.1, 1.54, 0.74, "handle", RUBBER)
    col(fig, 0.2, 0.2, 0.44, 0.64, "plain")
    for k, fill in enumerate((GRIP_BLUE, SAFETY, GRIP_RED)):
        fig.rect(0.56 + 0.32 * k, 0.24, 0.82 + 0.32 * k, 0.6, "handle", fill)
        light(fig, (0.56 + 0.32 * k, 0.24, 0.82 + 0.32 * k, 0.6))
    for row in range(2):
        y = 0.92 + 0.52 * row
        fig.rect(0.1, y, 1.54, y + 0.46, "handle", RUBBER)
        for k in range(6):
            x, w = 0.17 + 0.225 * k, 0.16
            fig.poly([(x, y + 0.04), (x + w, y + 0.04), (x + w, y + 0.28), (x + 0.11, y + 0.42),
                      (x + 0.05, y + 0.42), (x, y + 0.28)], "plain")  # fmt: skip
            fig.rect(x, y + 0.04, x + w * 0.3, y + 0.28, "gloss")
            fig.rect(x + w * 0.7, y + 0.04, x + w, y + 0.28, "shade")
    return done(fig)


def pin_punch_set(record: Record) -> Drawn:
    """A pin punch set in its roll pouch: five knurled punches, the thickest first."""
    del record
    fig = new()
    slab(fig, [(0.0, 0.0), (1.64, 0.0), (1.64, 2.0), (0.0, 2.0)], "handle", WALNUT)
    for k in range(5):
        x, w = 0.1 + 0.3 * k, 0.26
        tip = 0.13 - 0.02 * k
        col(fig, x + w / 2 - tip / 2, 0.2, x + w / 2 + tip / 2, 0.9, "plain")
        col(fig, x, 0.86, x + w, 1.8)
        for j in range(4):
            y = 0.95 + 0.07 * j
            fig.lines([((x, y), (x + w, y + 0.05))])
    fig.rect(0.0, 1.36, 1.64, 2.0, "handle", WALNUT)
    light(fig, (0.0, 1.36, 1.64, 2.0), across=True)
    fig.lines(((0.06 + 0.3 * k, 1.36), (0.06 + 0.3 * k, 2.0)) for k in range(6))
    return done(fig)


# --- couplings, rivets, anchors and collets ----------------------------------------------------


def rigid_coupling(record: Record) -> Drawn:
    """A rigid shaft coupling: a long sleeve, its bore, the split and two pairs of clamp screws."""
    del record
    fig = new()
    drum(fig, 0.0, 0.0, 1.64, 2.0, 0.34)
    fig.poly(ell((0.82, 0.34), 0.42, 0.18), "dark")
    fig.rect(0.79, 0.66, 0.85, 2.0, "dark")
    for x in (0.46, 1.18):
        for y in (0.98, 1.6):
            _bolt(fig, (x, y), 0.17)
    return done(fig)


def quick_coupling(record: Record) -> Drawn:
    """A quick-disconnect coupling: the plug, the knurled sleeve, the hex and the pipe thread."""
    del record
    fig = new()
    thread(fig, 0.36, 0.0, 1.28, 0.4)
    hexes(fig, 0.16, 0.38, 1.48, 0.78)
    col(fig, 0.0, 0.78, 1.64, 1.5)
    fig.lines(((0.06 + 0.12 * k, 0.9), (0.06 + 0.12 * k, 1.34)) for k in range(13))
    bar(fig, 0.0, 0.78, 1.64, 0.88, "plain")
    bar(fig, 0.0, 1.38, 1.64, 1.5, "plain")
    bar(fig, 0.3, 1.5, 1.34, 1.6, "handle", RUBBER)
    col(fig, 0.34, 1.6, 1.3, 1.86, "plain")
    slab(fig, [(0.34, 1.86), (1.3, 1.86), (1.2, 2.0), (0.44, 2.0)], "plain")
    return done(fig)


def blind_rivet(record: Record) -> Drawn:
    """A blind rivet: the mandrel, the domed flange, the hollow body and the mandrel's head."""
    del record
    fig = new()
    col(fig, 0.68, 0.0, 0.96, 0.5, "plain")
    dome = [*ell((0.82, 0.62), 0.82, 0.26, 180, 360, 18), (1.64, 0.7), (0.0, 0.7)]
    fig.poly(dome)
    fig.poly(ell((0.45, 0.5), 0.22, 0.06), "gloss")
    fig.rect(1.15, 0.54, 1.6, 0.7, "shade")
    col(fig, 0.32, 0.7, 1.32, 1.66)
    fig.poly([(0.32, 1.66), (1.32, 1.66), *ell((0.82, 1.66), 0.5, 0.34, 0, 180, 16)], "plain")
    fig.poly([(1.02, 1.66), (1.32, 1.66), *ell((0.82, 1.66), 0.5, 0.34, 0, 66, 8)], "shade")
    return done(fig)


def wall_anchor(record: Record) -> Drawn:
    """A nylon screw anchor: the collar, the ribbed body with its side fins, and the split tip."""
    del record
    fig = new()
    for flip in (list, mirror):
        slab(fig, flip([(0.28, 0.5), (0.02, 0.62), (0.02, 1.0), (0.28, 1.2)]), t=0.05)
    slab(fig, [(0.14, 0.2), (1.5, 0.2), (1.36, 1.5), (1.22, 2.0), (0.42, 2.0), (0.28, 1.5)])
    fig.poly([(0.24, 0.3), (0.44, 0.3), (0.54, 1.9), (0.44, 1.9)], "gloss")
    fig.poly([(1.18, 0.3), (1.48, 0.3), (1.35, 1.5), (1.22, 1.98), (1.1, 1.98)], "shade")
    for k in range(5):
        y = 0.5 + 0.2 * k
        fig.lines([((0.22 + 0.02 * k, y), (1.42 - 0.02 * k, y + 0.06))])
    fig.rect(0.78, 1.3, 0.86, 2.0, "dark")
    bar(fig, 0.0, 0.0, 1.64, 0.22, "plain")
    return done(fig)


def collet(record: Record) -> Drawn:
    """An ER collet: the nose ring and its groove, the slotted taper and the bore."""
    del record
    fig = new()
    taper = [(0.0, 0.66), (1.64, 0.66), (1.3, 2.0), (0.34, 2.0)]
    slab(fig, [(0.14, 0.5), (1.5, 0.5), (1.5, 0.68), (0.14, 0.68)], "dark")
    slab(fig, taper)
    fig.poly([(0.16, 0.7), (0.4, 0.7), (0.58, 1.98), (0.44, 1.98)], "gloss")
    fig.poly([(1.2, 0.7), (1.6, 0.7), (1.3, 1.98), (1.06, 1.98)], "shade")
    for x in (0.4, 0.82, 1.24):
        xb = 0.82 + (x - 0.82) * 0.65
        fig.poly([(x - 0.035, 0.82), (x + 0.035, 0.82), (xb + 0.03, 2.0), (xb - 0.03, 2.0)], "dark")
    drum(fig, 0.06, 0.0, 1.58, 0.58, 0.2)
    fig.poly(ell((0.82, 0.2), 0.3, 0.09), "dark")
    return done(fig)


def counterbore(record: Record) -> Drawn:
    """A piloted counterbore: the shank, the fluted cutter head and the pilot below it."""
    del record
    fig = new()
    col(fig, 0.36, 0.0, 1.28, 0.68)
    fig.rect(0.36, 0.16, 1.28, 0.24, "dark")
    col(fig, 0.0, 0.68, 1.64, 1.6)
    for x in (0.1, 0.62, 1.14):
        fig.poly([(x, 1.6), (x + 0.16, 1.6), (x + 0.38, 0.78), (x + 0.24, 0.78)], "dark")
    slab(fig, [(0.0, 1.6), (1.64, 1.6), (1.6, 1.66), (0.04, 1.66)], "plain", t=0.02)
    col(fig, 0.42, 1.66, 1.22, 1.94, "plain")
    slab(fig, [(0.42, 1.94), (1.22, 1.94), (1.14, 2.0), (0.5, 2.0)], "plain")
    return done(fig)


def handle_wedge(record: Record) -> Drawn:
    """A hammer handle wedge: its driven top, the barbed face and the side that tapers to the
    edge."""
    del record
    fig = new()
    fig.poly([(1.2, 0.28), (1.64, 0.0), (1.2, 2.0)])
    fig.poly([(1.2, 0.28), (1.64, 0.0), (1.2, 2.0)], "shade")
    slab(fig, [(0.0, 0.28), (1.2, 0.28), (1.2, 2.0), (0.0, 2.0)], t=0.08)
    for row in range(3):
        y = 0.6 + 0.44 * row
        for x in (0.2, 0.56, 0.92):
            fig.poly([(x - 0.12, y), (x + 0.12, y), (x, y + 0.2)], "dark")
    slab(fig, [(0.0, 0.28), (0.44, 0.0), (1.64, 0.0), (1.2, 0.28)], "plain")
    return done(fig)


# --- wheels, belts and blades ------------------------------------------------------------------


def backing_pad(record: Record) -> Drawn:
    """A flap disc backing pad: the molded disc, its cooling ribs and the steel arbor nut."""
    del record
    fig = new()
    c = (0.82, 0.82)
    disc(fig, c, 0.82)
    for k in range(12):
        a = math.radians(30 * k)
        at = [(c[0] + r * math.cos(a + d), c[1] + r * math.sin(a + d))
              for r, d in ((0.38, -0.12), (0.7, -0.05), (0.7, 0.05), (0.38, 0.12))]  # fmt: skip
        fig.poly(at, "dark")
    disc(fig, c, 0.34, "plain")
    fig.poly(hexagon(c, 0.22), "part")
    fig.disc(c, 0.11, "dark")
    return done(fig)


def diamond_wheel(record: Record) -> Drawn:
    """A diamond sharpening wheel: the abrasive rim, the aluminum body and its bore."""
    del record
    fig = new()
    c = (0.82, 0.82)
    disc(fig, c, 0.82)
    disc(fig, c, 0.58, "plain")
    for k in range(6):
        a = math.radians(60 * k)
        disc(fig, (c[0] + 0.4 * math.cos(a), c[1] + 0.4 * math.sin(a)), 0.07, "dark", steps=4)
    disc(fig, c, 0.22, "part", steps=6)
    fig.disc(c, 0.12, "hole")
    grit = [(math.radians(25.7 * k), 0.63 + 0.06 * (k % 3)) for k in range(14)]
    for a, r in grit:
        fig.disc((c[0] + r * math.cos(a), c[1] + r * math.sin(a)), 0.018, "dark")
    return done(fig)


def _loop(r: float, span: float = 0.36) -> list[Point]:
    """A racetrack about the middle of the box: round ends of radius ``r``, ``span`` apart."""
    c, top = BOX[0] / 2, BOX[1] / 2
    return [
        *arc((c, top - span / 2), r, 180, 360, 16),
        *arc((c, top + span / 2), r, 0, 180, 16),
    ]


def v_belt(record: Record) -> Drawn:
    """A V-belt coiled as it is sold: two turns of a ribbed belt, the inside of each in shade."""
    del record
    fig = new()
    for r in (0.82, 0.54):
        fig.poly(_loop(r))
        fig.poly([*_loop(r)[:12], *_loop(r - 0.08)[:12][::-1]], "gloss")
        fig.poly([*_loop(r)[17:30], *_loop(r - 0.1)[17:30][::-1]], "shade")
        fig.poly(_loop(r - 0.14), "handle", BELT)
        fig.lines(zip(_loop(r - 0.15)[::2], _loop(r - 0.25)[::2], strict=True))
    fig.poly(_loop(0.28), "hole")
    return done(fig)


def band_saw_blade(record: Record) -> Drawn:
    """A band saw blade coiled as it is sold: three turns, the teeth out, tied at two places."""
    del record
    fig = new()
    c, teeth = (0.82, 1.0), 44
    pts: list[Point] = []
    for k in range(teeth):
        for off, share in ((0.0, 1.0), (0.75, 0.94)):
            a = 2 * math.pi * (k + off) / teeth
            pts.append((c[0] + 0.82 * share * math.cos(a), c[1] + share * math.sin(a)))
    fig.poly(pts)
    for share, role in ((0.86, "part"), (0.68, "plain"), (0.5, "part")):
        fig.poly(ell(c, 0.82 * share, share), role)
        fig.poly([*ell(c, 0.82 * share, share, 180, 280, 12),
                  *ell(c, 0.82 * (share - 0.08), share - 0.08, 280, 180, 12)], "gloss")  # fmt: skip
        fig.poly([*ell(c, 0.82 * share, share, -20, 100, 12),
                  *ell(c, 0.82 * (share - 0.07), share - 0.07, 100, -20, 12)], "shade")  # fmt: skip
    fig.poly(ell(c, 0.82 * 0.36, 0.36), "hole")
    for y in (0.12, 1.5):
        fig.rect(0.74, y, 0.9, y + 0.4, "handle", GRIP_BLUE)
        light(fig, (0.74, y, 0.9, y + 0.4))
    return done(fig)


def pulley_block(record: Record) -> Drawn:
    """A shackle-mount pulley block: the shackle and its pin, the side plates and the sheave."""
    del record
    fig = new()
    slab(fig, [(0.48, 0.5), (0.5, 0.16), (0.66, 0.0), (0.98, 0.0), (1.14, 0.16), (1.16, 0.5)],
         "plain")  # fmt: skip
    fig.poly([(0.68, 0.5), (0.68, 0.28), (0.76, 0.2), (0.88, 0.2), (0.96, 0.28), (0.96, 0.5)],
             "hole")  # fmt: skip
    bar(fig, 0.3, 0.42, 1.34, 0.56, "plain")
    plate = [(0.42, 0.54), (1.22, 0.54), *ell((0.82, 1.24), 0.82, 0.76, -35, 215, 24)]
    slab(fig, plate, t=0.08)
    fig.poly([*ell((0.82, 1.24), 0.82, 0.76, 170, 215, 8),
              *ell((0.82, 1.24), 0.66, 0.6, 215, 170, 8)], "gloss")  # fmt: skip
    fig.poly([*ell((0.82, 1.24), 0.82, 0.76, -30, 80, 12),
              *ell((0.82, 1.24), 0.68, 0.62, 80, -30, 12)], "shade")  # fmt: skip
    disc(fig, (0.82, 1.28), 0.5, "plain")
    fig.disc((0.82, 1.28), 0.36, "dark")
    disc(fig, (0.82, 1.28), 0.3)
    _bolt(fig, (0.82, 1.28), 0.16)
    return done(fig)


# --- storage, holders and fixtures -------------------------------------------------------------


def screwdriver_rack(record: Record) -> Drawn:
    """A bench screwdriver rack: the steel back, two punched shelves and the drivers they hold."""
    del record
    fig = new()
    slab(fig, [(0.0, 0.0), (1.64, 0.0), (1.64, 2.0), (0.0, 2.0)])
    for x in (0.1, 1.54):
        fig.disc((x, 0.1), 0.05, "dark")
    grips = (GRIP_RED, GRIP_BLUE, SAFETY, RUBBER)
    for row in range(2):
        y = 0.2 + 0.9 * row
        for k in range(4):
            _screwdriver(fig, 0.16 + 0.36 * k, y, y + 0.82, 0.22, grips[(k + row) % 4])
        bar(fig, 0.06, y + 0.34, 1.58, y + 0.5, "plain")
    return done(fig)


def drawer_slides(record: Record) -> Drawn:
    """A pair of ball bearing drawer slides, side by side: each outer rail, its ball cage and the
    inner rail drawn out of it."""
    del record
    fig = new()
    for x0 in (0.0, 0.86):
        col(fig, x0, 0.36, x0 + 0.78, 2.0)
        fig.rect(x0 + 0.14, 0.36, x0 + 0.64, 1.94, "dark")
        for y in (0.5, 0.72, 0.94, 1.16):
            for x in (0.18, 0.6):
                fig.disc((x0 + x, y), 0.05, "plain")
        col(fig, x0 + 0.22, 0.0, x0 + 0.56, 1.6, "plain")
        for y in (0.2, 0.75, 1.3):
            fig.poly(ell((x0 + 0.39, y), 0.08, 0.13, steps=12), "dark")
        disc(fig, (x0 + 0.39, 1.78), 0.08, "plain", steps=4)
    return done(fig)


def hammer_holster(record: Record) -> Drawn:
    """A hammer holster: the nylon backing with its belt slots, the stitching, and the steel loop
    the hammer hangs in."""
    del record
    fig = new()
    back = [(0.08, 0.0), (1.56, 0.0), (1.64, 0.1), (1.64, 1.2), (1.4, 1.8), (1.1, 2.0),
            (0.54, 2.0), (0.24, 1.8), (0.0, 1.2), (0.0, 0.1)]  # fmt: skip
    slab(fig, back, t=0.08)
    for x in (0.26, 1.2):
        fig.rect(x, 0.14, x + 0.18, 0.62, "dark")
    fig.lines(((0.12 + 0.14 * k, 0.74), (0.2 + 0.14 * k, 0.74)) for k in range(10))
    ring = ell((0.82, 1.24), 0.56, 0.36)
    fig.poly(ring, "plain")
    fig.poly([*ell((0.82, 1.24), 0.56, 0.36, 190, 290, 12),
              *ell((0.82, 1.24), 0.48, 0.28, 290, 190, 12)], "gloss")  # fmt: skip
    fig.poly([*ell((0.82, 1.24), 0.56, 0.36, 0, 110, 12),
              *ell((0.82, 1.24), 0.48, 0.28, 110, 0, 12)], "shade")  # fmt: skip
    fig.poly(ell((0.82, 1.24), 0.44, 0.25), "dark")
    slab(fig, [(0.56, 0.82), (1.08, 0.82), (1.02, 1.1), (0.62, 1.1)], t=0.05)
    for x in (0.7, 0.94):
        _bolt(fig, (x, 0.94), 0.07)
    return done(fig)


def cutter_case(record: Record) -> Drawn:
    """An end mill storage case, open: the lid with its label and the base with four end mills in
    their pockets."""
    del record
    fig = new()
    _case(fig, GRIP_BLUE, 0.7)
    fig.rect(0.12, 0.12, 1.52, 0.58, "handle", PAPER_LABEL)
    fig.lines(((0.24, y), (1.4, y)) for y in (0.26, 0.36, 0.46))
    for k in range(4):
        x = 0.14 + 0.35 * k
        fig.rect(x, 0.82, x + 0.3, 1.88, "dark")
        col(fig, x + 0.05, 0.88, x + 0.25, 1.34, "plain")
        col(fig, x + 0.05, 1.34, x + 0.25, 1.82)
        for j in range(3):
            y = 1.36 + 0.14 * j
            fig.poly([(x + 0.05, y + 0.14), (x + 0.25, y), (x + 0.25, y + 0.05),
                      (x + 0.05, y + 0.19)], "dark")  # fmt: skip
    return done(fig)


def bit_index_case(record: Record) -> Drawn:
    """An empty drill bit index, open: the lid behind and three stepped rows of graded holes."""
    del record
    fig = new()
    slab(fig, [(0.1, 0.0), (1.54, 0.0), (1.54, 0.62), (0.1, 0.62)], "handle", GRIP_RED, t=0.07)
    fig.rect(0.5, 0.2, 1.14, 0.42, "handle", PAPER_LABEL)
    for row in range(3):
        y = 0.6 + 0.4 * row
        inset = 0.08 - 0.04 * row
        slab(fig, [(inset, y), (1.64 - inset, y), (1.64 - inset, y + 0.42), (inset, y + 0.42)])
        for k in range(5 + row):
            r = (0.11 - 0.02 * row) * (1 - 0.06 * k)
            fig.poly(ell((0.26 + 1.15 * k / (4 + row), y + 0.2), r, r * 0.75, steps=8), "dark")
    slab(fig, [(0.0, 1.8), (1.64, 1.8), (1.64, 2.0), (0.0, 2.0)], "handle", GRIP_RED)
    bar(fig, 0.66, 1.82, 0.98, 1.94, "plain")
    return done(fig)


def cantilever_rack(record: Record) -> Drawn:
    """A cantilever rack from its end: the column, the base and four arms a side, each with the
    stop at its tip."""
    del record
    fig = new()
    for k in range(4):
        y = 0.06 + 0.42 * k
        arm = [(0.66, y + 0.04), (0.08, y + 0.06), (0.08, y - 0.06), (0.0, y - 0.06),
               (0.0, y + 0.22), (0.66, y + 0.3)]  # fmt: skip
        lit = [(0.66, y + 0.04), (0.08, y + 0.06), (0.08, y + 0.11), (0.66, y + 0.09)]
        dim = [(0.66, y + 0.25), (0.0, y + 0.17), (0.0, y + 0.22), (0.66, y + 0.3)]
        for flip in (list, mirror):
            fig.poly(flip(arm))
            fig.poly(flip(lit), "gloss")
            fig.poly(flip(dim), "shade")
    col(fig, 0.6, 0.0, 1.04, 2.0)
    for k in range(6):
        fig.rect(0.78, 0.12 + 0.26 * k, 0.86, 0.24 + 0.26 * k, "dark")
    slab(fig, [(0.0, 1.72), (1.64, 1.72), (1.64, 2.0), (0.0, 2.0)], t=0.06)
    for x in (0.16, 1.48):
        _bolt(fig, (x, 1.86), 0.06)
    return done(fig)


def sharpening_fixture(record: Record) -> Drawn:
    """An end mill sharpening fixture: the ground base, the indexing head and its clamp knob, and
    the end mill it holds."""
    del record
    fig = new()
    col(fig, 0.6, 0.0, 1.04, 0.5, "plain")
    for k in range(3):
        y = 0.04 + 0.14 * k
        fig.poly([(0.6, y + 0.14), (1.04, y), (1.04, y + 0.06), (0.6, y + 0.2)], "dark")
    slab(fig, [(0.06, 0.4), (1.46, 0.4), (1.46, 1.4), (0.06, 1.4)], t=0.07)
    disc(fig, (0.82, 0.92), 0.42, "plain")
    for k in range(12):
        a = math.radians(30 * k)
        fig.disc((0.82 + 0.35 * math.cos(a), 0.92 + 0.35 * math.sin(a)), 0.028, "dark")
    _bolt(fig, (0.82, 0.92), 0.2)
    bar(fig, 1.4, 0.66, 1.64, 0.98, "handle", GRIP_RED)
    slab(fig, [(0.0, 1.36), (1.64, 1.36), (1.64, 2.0), (0.0, 2.0)], t=0.08)
    fig.poly([(0.58, 2.0), (1.06, 2.0), (0.82, 1.74)], "hole")
    for x in (0.22, 1.42):
        _bolt(fig, (x, 1.68), 0.1)
    return done(fig)


def hex_key_holder(record: Record) -> Drawn:
    """A hex key holder: a molded block with a row of graded sleeves, and the keys in it."""
    del record
    fig = new()
    for k in range(5):
        w = 0.2 - 0.02 * k
        x, top = 0.08 + 0.31 * k, 0.0 + 0.14 * k
        col(fig, x, top, x + w, 1.2, "plain")
        bar(fig, x, top, min(x + w + 0.2, 1.64), top + w * 0.9, "plain")
    slab(fig, [(0.0, 0.84), (1.64, 0.84), (1.64, 1.86), (1.5, 2.0), (0.14, 2.0), (0.0, 1.86)],
         "handle", RUBBER, t=0.08)  # fmt: skip
    for k in range(5):
        x = 0.05 + 0.31 * k
        fig.rect(x, 0.84, x + 0.26, 0.96, "dark")
        fig.rect(x + 0.04, 1.1, x + 0.22, 1.3, "handle", PAPER_LABEL)
    bar(fig, 0.2, 1.5, 1.44, 1.74, "handle", GRIP_RED)
    return done(fig)


# --- ear plugs and spill socks -----------------------------------------------------------------


def _plug(fig: Figure, cx: float) -> None:
    """A tapered foam ear plug, its round tip up and its flared base down."""
    tip = ell((cx, 0.36), 0.28, 0.36, 180, 360, 14)
    body = [*tip, (cx + 0.38, 1.78), *ell((cx, 1.78), 0.38, 0.22, 0, 180, 14)]
    fig.poly(body, "handle", FOAM)
    fig.poly([(cx - 0.2, 0.26), (cx - 0.06, 0.18), (cx - 0.06, 1.86), (cx - 0.28, 1.78)], "gloss")
    fig.poly([(cx + 0.06, 0.06), (cx + 0.2, 0.12), (cx + 0.28, 0.38), (cx + 0.38, 1.78),
              (cx + 0.2, 1.96), (cx + 0.04, 1.99)], "shade")


def ear_plugs(record: Record) -> Drawn:
    """A pair of foam ear plugs, and between them the cord of a corded pair."""
    fig = new()
    for cx in (0.38, 1.26):
        _plug(fig, cx)
    if record.get("Type") == "Corded":
        fig.poly([*ell((0.82, 1.84), 0.47, 1.0, 180, 360, 24),
                  *ell((0.82, 1.84), 0.4, 0.92, 360, 180, 24)], "handle", GRIP_BLUE)  # fmt: skip
    return done(fig)


def _tube(fig: Figure, pts: Sequence[Point]) -> None:
    """One run of a filled sock: its body and the light along it."""
    fig.poly(pts, "handle", SOCK)
    ys = [p[1] for p in pts]
    y0, h = min(ys), max(ys) - min(ys)
    fig.rect(0.24, y0 + 0.12 * h, 1.4, y0 + 0.28 * h, "gloss")
    fig.rect(0.24, y0 + 0.58 * h, 1.4, y0 + h, "shade")


def spill_socks(record: Record) -> Drawn:
    """Absorbent socks stacked as they are shipped: three filled tubes, their ends tied off."""
    del record
    fig = new()
    for k in range(3):
        y, h = 0.67 * k, 0.66
        rows = ((0.0, 0.5), (0.1, 0.32), (0.16, 0.1), (0.34, 0.0))
        left = [(x, y + h * f) for x, f in rows]
        low = [(x, y + h * (1 - f)) for x, f in rows[1:]][::-1]
        _tube(fig, [*left, *[(BOX[0] - x, yy) for x, yy in left[::-1]],
                    *[(BOX[0] - x, yy) for x, yy in low[::-1]], *low])  # fmt: skip
        for x in (0.14, 1.4):
            bar(fig, x, y + 0.1, x + 0.1, y + h - 0.1, "handle", SAFETY)
        fig.lines(((0.36 + 0.2 * j, y + 0.04), (0.3 + 0.2 * j, y + h - 0.04)) for j in range(5))
    return done(fig)


#: The breadth types of this module: type key -> its drawing.
HARDWARE: dict[str, Callable[[Record], Drawn]] = {
    "backing_pads": backing_pad,
    "band_saw_blades": band_saw_blade,
    "bench_tool_racks": screwdriver_rack,
    "bit_index_cases": bit_index_case,
    "bit_socket_sets": bit_socket_set,
    "blind_rivets": blind_rivet,
    "cantilever_racks": cantilever_rack,
    "cold_chisels": cold_chisel,
    "cutter_sharpening_fixtures": sharpening_fixture,
    "cutter_storage_cases": cutter_case,
    "diamond_wheels": diamond_wheel,
    "drawer_slides": drawer_slides,
    "driver_bit_sets": driver_bit_set,
    "foam_ear_plugs": ear_plugs,
    "grub_screw_keys": hex_key,
    "handle_wedges": handle_wedge,
    "hex_bit_socket_sets": hex_bit_socket_set,
    "micro_collets": collet,
    "nut_drivers_hex": nut_driver,
    "nylon_wall_anchors": wall_anchor,
    "pin_punch_sets": pin_punch_set,
    "piloted_counterbores": counterbore,
    "pneumatic_cut_off_tools": pneumatic_cut_off_tool,
    "quick_disconnect_couplings": quick_coupling,
    "rigging_pulleys": pulley_block,
    "rigid_shaft_couplings": rigid_coupling,
    "snap_ring_pliers": snap_ring_pliers,
    "spanner_wrenches": spanner_wrench,
    "spill_socks": spill_socks,
    "thread_restoring_files": thread_file,
    "tool_holsters": hammer_holster,
    "v_belts": v_belt,
    "wrench_organizers": hex_key_holder,
}
