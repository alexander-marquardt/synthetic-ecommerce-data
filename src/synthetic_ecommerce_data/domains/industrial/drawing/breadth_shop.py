"""Breadth types drawn as their own product, third slice: shop tools, fasteners and power
transmission (#1216).

Fixed geometry, lit, laid out as :mod:`.breadth_products` says, except that a type whose ``Style``
or ``Piece Count`` is a different product to look at reads it, inside the same outline.
:data:`SHOP` maps a type key to its drawing; ``BREADTH_PRODUCTS`` holds it.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from synthetic_ecommerce_data.core.drawing.model import Figure, Point, arc
from synthetic_ecommerce_data.domains.industrial.drawing.breadth_light import (
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
    new,
    slab,
    thread,
)
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn, Record

BIRCH = "#d8b789"
POUCH = "#5d6a56"
NYLON = "#f0ece0"
MACHINE = "#4f6b84"


def _stated(record: Record, name: str, otherwise: str) -> str:
    """``record``'s value of ``name``, in either case (:func:`.breadth_rungs.ratios`)."""
    return {key.casefold(): value for key, value in record.items()}.get(name.casefold(), otherwise)


def _bolt(fig: Figure, c: Point, r: float) -> None:
    """A socket screw's head."""
    disc(fig, c, r, "plain", steps=4)
    fig.poly(hexagon(c, r * 0.5), "dark")


# --- sets --------------------------------------------------------------------------------------


def seal_pick_set(record: Record) -> Drawn:
    """A nylon seal pick set in its pouch: hooked, straight and angled tips."""
    count = int(_stated(record, "Piece Count", "5"))
    fig = new()
    slab(fig, [(0.0, 0.0), (1.64, 0.0), (1.64, 2.0), (0.0, 2.0)], "handle", POUCH)
    step = 1.44 / count
    for k in range(count):
        x = 0.1 + step * (k + 0.5)
        bend = (0.1, 0.0, -0.1, 0.06, -0.06)[k]
        fig.poly([(x - 0.04, 1.0), (x - 0.04, 0.4), (x - 0.04 + bend, 0.2), (x + bend, 0.16),
                  (x + 0.04, 0.4), (x + 0.04, 1.0)], "handle", NYLON)  # fmt: skip
        col(fig, x - 0.11, 0.8, x + 0.11, 1.8, "handle", NYLON)
        fig.lines(((x - 0.11, y), (x + 0.11, y)) for y in (0.9, 0.97, 1.04))
    fig.rect(0.0, 1.3, 1.64, 2.0, "handle", POUCH)
    light(fig, (0.0, 1.3, 1.64, 2.0), across=True)
    fig.lines(((0.1 + step * k, 1.3), (0.1 + step * k, 2.0)) for k in range(count + 1))
    return done(fig)


def fastener_extractor_set(record: Record) -> Drawn:
    """A screw extractor set in its open case: square shanks over reverse spirals."""
    count = int(_stated(record, "Piece Count", "5"))
    fig = new()
    slab(fig, [(0.0, 0.06), (0.06, 0.0), (1.58, 0.0), (1.64, 0.06), (1.64, 1.94), (1.58, 2.0),
               (0.06, 2.0), (0.0, 1.94)], "handle", GRIP_RED, t=0.07)  # fmt: skip
    fig.rect(0.1, 0.1, 1.54, 0.4, "handle", PAPER_LABEL)
    fig.lines([((0.2, 0.2), (1.1, 0.2)), ((0.2, 0.3), (0.8, 0.3))])
    fig.rect(0.1, 0.5, 1.54, 1.9, "dark")
    step = 1.4 / count
    for k in range(count):
        x, w = 0.12 + step * (k + 0.5), 0.11 - 0.011 * k
        top = 0.58 + 0.06 * k
        fig.rect(x - w * 0.8, top, x + w * 0.8, top + 0.36, "plain")
        fig.rect(x - w * 0.8, top, x - w * 0.2, top + 0.36, "gloss")
        fig.poly([(x - w, top + 0.36), (x + w, top + 0.36), (x + w * 0.45, 1.82),
                  (x - w * 0.45, 1.82)])  # fmt: skip
        fig.poly([(x + w * 0.4, top + 0.36), (x + w, top + 0.36), (x + w * 0.45, 1.82)], "shade")
        fig.lines(((x - w * 0.8, y), (x + w * 0.8, y + 0.12)) for y in (1.05, 1.25, 1.45, 1.6))
    return done(fig)


# --- cutting and hand tools --------------------------------------------------------------------


def center_punch(record: Record) -> Drawn:
    """A center punch, corner to corner: the struck head, or an automatic's spring cap, the knurled
    grip and the ground point."""
    automatic = _stated(record, "Style", "Standard") == "Automatic"
    fig = new()
    if automatic:
        slab(fig, [(0.1, 0.0), (0.54, 0.0), (0.64, 0.1), (0.64, 0.4), (0.0, 0.4), (0.0, 0.1)],
             "plain")  # fmt: skip
        light(fig, (0.0, 0.1, 0.64, 0.4))
        fig.lines(((0.08 + 0.12 * k, 0.06), (0.08 + 0.12 * k, 0.34)) for k in range(5))
        bar(fig, 0.04, 0.4, 0.6, 0.48, "dark")
    else:
        slab(fig, [(0.1, 0.0), (0.54, 0.0), (0.64, 0.1), (0.64, 0.48), (0.0, 0.48), (0.0, 0.1)])
    col(fig, 0.0, 0.48, 0.64, 1.34)
    for y in range(6):
        at = 0.56 + 0.11 * y
        fig.lines([((0.0, at), (0.64, at + 0.16)), ((0.64, at), (0.0, at + 0.16))])
    col(fig, 0.08, 1.34, 0.56, 1.7, "plain")
    fig.poly([(0.08, 1.7), (0.56, 1.7), (0.42, 2.0), (0.32, 2.2), (0.22, 2.0)], "plain")
    fig.poly([(0.42, 1.7), (0.56, 1.7), (0.42, 2.0), (0.32, 2.2)], "shade")
    return done(laid(fig, LAID))


def grooving_cutter(record: Record) -> Drawn:
    """A grooving cutter: a ring of ground teeth, the relieved web and the keyed bore."""
    del record
    fig = new()
    c, teeth = (0.82, 0.82), 16
    rim = []
    for k in range(teeth):
        a = math.radians(360 * k / teeth)
        for r, d in ((0.82, 0.0), (0.82, 0.12), (0.76, 0.3), (0.72, 0.36)):
            rim.append((c[0] + r * math.cos(a + d), c[1] + r * math.sin(a + d)))
    fig.poly(rim)
    disc(fig, c, 0.7, bore=0.5)
    disc(fig, c, 0.48, "plain", bore=0.22)
    fig.disc(c, 0.2, "dark")
    fig.rect(0.76, 0.56, 0.88, 0.68, "dark")
    return done(fig)


def bit_sharpener(record: Record) -> Drawn:
    """A drill bit sharpener: the housing, the bit ports on its sloped face and the switch."""
    del record
    fig = new()
    slab(fig, [(0.2, 0.0), (1.44, 0.0), (1.64, 0.5), (1.64, 2.0), (0.0, 2.0), (0.0, 0.5)],
         "handle", SAFETY, t=0.08)  # fmt: skip
    fig.poly([(0.26, 0.1), (1.38, 0.1), (1.5, 0.5), (0.14, 0.5)], "handle", RUBBER)
    for k in range(4):
        fig.disc((0.4 + 0.28 * k, 0.32), 0.05 + 0.015 * k, "hole")
    disc(fig, (0.82, 1.06), 0.42, "plain")
    disc(fig, (0.82, 1.06), 0.28)
    fig.disc((0.82, 1.06), 0.1, "dark")
    fig.rect(0.14, 1.64, 0.5, 1.86, "dark")
    fig.rect(0.14, 1.64, 0.32, 1.86, "handle", GRIP_RED)
    fig.rect(0.7, 1.64, 1.5, 1.86, "handle", PAPER_LABEL)
    fig.lines([((0.78, 1.71), (1.42, 1.71)), ((0.78, 1.79), (1.2, 1.79))])
    return done(fig)


def nut_splitter(record: Record) -> Drawn:
    """A nut splitter: the screw with its hex, the body, the ring and the chisel over the nut."""
    del record
    fig = new()
    hexes(fig, 0.46, 0.0, 1.18, 0.26, "plain")
    thread(fig, 0.52, 0.26, 1.12, 0.5)
    body = [(0.24, 0.46), (1.4, 0.46), (1.6, 0.8), (1.64, 1.2), *arc((0.82, 1.2), 0.82, 0, 180, 16),
            (0.0, 1.2), (0.04, 0.8)]  # fmt: skip
    slab(fig, body, t=0.07)
    fig.disc((0.82, 1.3), 0.38, "hole")
    fig.poly(hexagon((0.82, 1.38), 0.3), "plain")
    fig.disc((0.82, 1.38), 0.15, "dark")
    slab(fig, [(0.64, 0.8), (1.0, 0.8), (1.0, 0.96), (0.82, 1.18), (0.64, 0.96)], "plain", t=0.04)
    return done(fig)


def pitch_gage(record: Record) -> Drawn:
    """A thread pitch gauge: the case, its two screws and notched leaves fanned from each end."""
    del record
    fig = new()
    for base, sign in (((0.82, 0.84), -1), ((0.82, 1.16), 1)):
        for degrees in (-72, 72, -36, 36, 0):
            a = math.radians(degrees)
            u = (math.sin(a), sign * math.cos(a))
            v = (-u[1], u[0])
            edge = [(0.2, -0.15), (0.78, -0.15), (0.84, -0.09), (0.84, 0.15)]
            for k in range(4):
                edge += [(0.79 - 0.08 * k, 0.08), (0.75 - 0.08 * k, 0.15)]
            edge += [(0.2, 0.15)]
            fig.poly([(base[0] + u[0] * p + v[0] * q, base[1] + u[1] * p + v[1] * q)
                      for p, q in edge], "plain")  # fmt: skip
    slab(fig, [(0.34, 0.62), (0.46, 0.5), (1.18, 0.5), (1.3, 0.62), (1.3, 1.38), (1.18, 1.5),
               (0.46, 1.5), (0.34, 1.38)], t=0.07)  # fmt: skip
    fig.rect(0.52, 0.86, 1.12, 1.14, "handle", PAPER_LABEL)
    fig.lines([((0.6, 0.95), (1.04, 0.95)), ((0.6, 1.05), (0.9, 1.05))])
    for y in (0.68, 1.32):
        _bolt(fig, (0.82, y), 0.11)
    return done(fig)


def tap_wrench(record: Record) -> Drawn:
    """A T-handle tap wrench: the sliding bar, the knurled body and the chuck jaws on a tap."""
    del record
    fig = new()
    bar(fig, 0.1, 0.1, 1.54, 0.36, "plain")
    for x in (0.12, 1.52):
        disc(fig, (x, 0.23), 0.14, "plain", steps=6)
    col(fig, 0.46, 0.0, 1.18, 0.56)
    col(fig, 0.52, 0.56, 1.12, 1.0)
    col(fig, 0.4, 1.0, 1.24, 1.56)
    fig.lines(((0.48 + 0.1 * k, 1.06), (0.48 + 0.1 * k, 1.5)) for k in range(8))
    slab(fig, [(0.4, 1.56), (1.24, 1.56), (1.06, 1.84), (0.58, 1.84)], "plain")
    fig.rect(0.72, 1.7, 0.92, 2.0, "plain")
    fig.rect(0.79, 1.84, 0.85, 2.0, "dark")
    return done(fig)


def circle_cutter(record: Record) -> Drawn:
    """An adjustable circle cutter: the shank, the beam with its scale, the pilot drill and the
    cutting bit clamped out on the arm."""
    del record
    fig = new()
    col(fig, 0.36, 0.0, 0.72, 0.62, "plain")
    slab(fig, [(0.14, 0.5), (0.94, 0.5), (0.94, 1.26), (0.14, 1.26)])
    bar(fig, 0.0, 0.68, 1.64, 1.04, "plain")
    fig.lines(((1.0 + 0.08 * k, 0.68), (1.0 + 0.08 * k, 0.78)) for k in range(4))
    _bolt(fig, (0.54, 0.86), 0.14)
    slab(fig, [(1.2, 0.58), (1.64, 0.58), (1.64, 1.4), (1.2, 1.4)])
    _bolt(fig, (1.42, 0.84), 0.11)
    col(fig, 0.4, 1.26, 0.68, 1.84, "plain")
    fig.lines(((0.4, y), (0.68, y - 0.14)) for y in (1.48, 1.64, 1.8))
    fig.poly([(0.4, 1.84), (0.68, 1.84), (0.54, 2.0)], "plain")
    slab(fig, [(1.3, 1.4), (1.54, 1.4), (1.54, 1.66), (1.36, 1.8)], "plain", t=0.04)
    return done(fig)


def bench_vise(record: Record) -> Drawn:
    """A bench vise: the anvil and jaws, the sliding jaw's screw and handle, and the base."""
    del record
    fig = new()
    slab(fig, [(0.06, 1.56), (1.22, 1.56), (1.32, 1.76), (1.32, 2.0), (0.0, 2.0), (0.0, 1.76)])
    for x in (0.16, 1.16):
        _bolt(fig, (x, 1.86), 0.09)
    drum(fig, 0.16, 1.28, 1.14, 1.64, 0.08, "handle", RUBBER)
    slab(fig, [(0.0, 0.5), (0.5, 0.42), (0.5, 0.2), (0.82, 0.2), (0.82, 1.4), (0.1, 1.4),
               (0.0, 1.0)], "handle", MACHINE, t=0.08)  # fmt: skip
    slab(fig, [(0.92, 0.2), (1.2, 0.2), (1.36, 0.56), (1.36, 1.3), (0.82, 1.3), (0.82, 0.8),
               (0.92, 0.7)], "handle", MACHINE, t=0.08)  # fmt: skip
    for x0, x1 in ((0.68, 0.84), (0.9, 1.06)):
        col(fig, x0, 0.1, x1, 0.46, "plain")
    bar(fig, 1.36, 0.82, 1.5, 1.06, "plain")
    col(fig, 1.44, 0.3, 1.56, 1.6, "plain")
    for y in (0.3, 1.6):
        disc(fig, (1.5, y), 0.12, "plain", steps=5)
    return done(fig)


def cutter_rack(record: Record) -> Drawn:
    """A cutter rack: two tiers of holes, an end mill standing in each."""
    del record
    fig = new()
    for x in (0.0, 1.48):
        col(fig, x, 0.4, x + 0.16, 2.0)
    for tier in range(2):
        y = 0.64 + 0.84 * tier
        for k in range(4):
            x, w = 0.19 + 0.33 * k, 0.12 + 0.04 * k
            x += (0.27 - w) / 2
            fig.rect(x, y - 0.56 + 0.06 * (3 - k), x + w, y, "plain")
            fig.rect(x + w * 0.12, y - 0.56 + 0.06 * (3 - k), x + w * 0.3, y, "gloss")
            fig.rect(x + w * 0.68, y - 0.56 + 0.06 * (3 - k), x + w, y, "shade")
            fig.lines(((x, y - 0.1 - 0.1 * j), (x + w, y - 0.18 - 0.1 * j)) for j in range(3))
        slab(fig, [(0.06, y - 0.06), (1.58, y - 0.06), (1.64, y + 0.1), (1.64, y + 0.36),
                   (0.0, y + 0.36), (0.0, y + 0.1)])  # fmt: skip
        fig.rect(0.24, y + 0.16, 1.4, y + 0.28, "handle", PAPER_LABEL)
    slab(fig, [(0.0, 1.84), (1.64, 1.84), (1.64, 2.0), (0.0, 2.0)], t=0.04)
    return done(fig)


def induction_heater(record: Record) -> Drawn:
    """A bench induction heater: a bearing on the yoke over the coil, the housing, its display and
    its keys."""
    del record
    fig = new()
    for x in (0.1, 1.2):
        col(fig, x, 0.14, x + 0.34, 1.0, "dark")
    bar(fig, 0.0, 0.1, 1.64, 0.4, "plain")
    disc(fig, (0.82, 0.5), 0.44, "plain")
    disc(fig, (0.82, 0.5), 0.3)
    fig.disc((0.82, 0.5), 0.2, "dark")
    bar(fig, 0.6, 0.18, 1.04, 0.36, "plain")
    slab(fig, [(0.0, 0.96), (1.64, 0.96), (1.64, 2.0), (0.0, 2.0)], "handle", MACHINE, t=0.08)
    fig.rect(0.16, 1.12, 1.0, 1.52, "dark")
    fig.rect(0.22, 1.18, 0.94, 1.46, "handle", "#9fd3b0")
    fig.lines([((0.32, 1.28), (0.8, 1.28)), ((0.32, 1.37), (0.66, 1.37))])
    disc(fig, (1.3, 1.32), 0.18, "handle", GRIP_RED, steps=6)
    for k in range(4):
        bar(fig, 0.16 + 0.35 * k, 1.66, 0.42 + 0.35 * k, 1.84, "handle", PAPER_LABEL)
    return done(fig)


# --- tool holding ------------------------------------------------------------------------------


def _taper(fig: Figure) -> None:
    """A CAT taper: the pull stud, the taper and the V-flange with its drive slot."""
    col(fig, 0.66, 0.0, 0.98, 0.1, "plain")
    col(fig, 0.72, 0.1, 0.92, 0.2, "plain")
    fig.poly([(0.46, 0.2), (1.18, 0.2), (1.5, 0.96), (0.14, 0.96)])
    fig.poly([(0.56, 0.2), (0.66, 0.2), (0.5, 0.96), (0.32, 0.96)], "gloss")
    fig.poly([(0.98, 0.2), (1.18, 0.2), (1.5, 0.96), (1.12, 0.96)], "shade")
    col(fig, 0.0, 0.96, 1.64, 1.12, "plain")
    col(fig, 0.1, 1.12, 1.54, 1.2, "dark")
    col(fig, 0.0, 1.2, 1.64, 1.36, "plain")
    fig.rect(0.7, 0.96, 0.94, 1.36, "dark")


def collet_chuck(record: Record) -> Drawn:
    """A CAT40 collet chuck: the taper, the V-flange, the body and the slotted collet nut."""
    del record
    fig = new()
    _taper(fig)
    col(fig, 0.3, 1.36, 1.34, 1.54)
    col(fig, 0.2, 1.54, 1.44, 1.92)
    for x in (0.34, 0.58, 1.0, 1.24):
        fig.rect(x - 0.04, 1.66, x + 0.04, 1.92, "dark")
    slab(fig, [(0.2, 1.92), (1.44, 1.92), (1.32, 2.0), (0.32, 2.0)], "plain", t=0.02)
    return done(fig)


def side_lock_holder(record: Record) -> Drawn:
    """A CAT40 side-lock end mill holder: the taper, the V-flange and the nose with its two set
    screws."""
    del record
    fig = new()
    _taper(fig)
    col(fig, 0.16, 1.36, 1.48, 1.92)
    slab(fig, [(0.16, 1.92), (1.48, 1.92), (1.38, 2.0), (0.26, 2.0)], "plain", t=0.02)
    for x in (0.54, 1.1):
        _bolt(fig, (x, 1.64), 0.19)
    return done(fig)


def milling_collet(record: Record) -> Drawn:
    """A milling collet: the tapered nose with its bore, the slotted body and the drawn end."""
    del record
    fig = new()
    body = [(0.2, 0.44), (1.44, 0.44), (1.44, 1.5), (1.5, 1.56), (1.5, 1.8), (1.3, 2.0),
            (0.34, 2.0), (0.14, 1.8), (0.14, 1.56), (0.2, 1.5)]  # fmt: skip
    slab(fig, body)
    fig.rect(0.34, 0.5, 0.52, 1.96, "gloss")
    fig.rect(1.1, 0.5, 1.4, 1.9, "shade")
    for x in (0.56, 1.08):
        fig.rect(x - 0.03, 0.7, x + 0.03, 1.7, "dark")
        fig.disc((x, 1.7), 0.06, "dark")
    bar(fig, 0.14, 1.5, 1.5, 1.6, "plain")
    fig.poly([(0.0, 0.2), (1.64, 0.2), (1.44, 0.74), (0.2, 0.74)], "plain")
    fig.poly([(1.2, 0.2), (1.64, 0.2), (1.44, 0.74), (1.1, 0.74)], "shade")
    fig.poly([(0.16, 0.2), (0.36, 0.2), (0.46, 0.74), (0.34, 0.74)], "gloss")
    fig.poly(ell((0.82, 0.2), 0.82, 0.2), "plain")
    fig.poly(ell((0.82, 0.2), 0.34, 0.09), "dark")
    fig.lines([((0.0, 0.2), (0.48, 0.2)), ((1.16, 0.2), (1.64, 0.2)), ((0.82, 0.29), (0.82, 0.74))])
    return done(fig)


def wheel_mandrel(record: Record) -> Drawn:
    """A wheel mandrel: the slotted screw, the two flanges that hold a wheel and the shank."""
    del record
    fig = new()
    slab(fig, [(0.26, 0.1), (0.36, 0.0), (1.28, 0.0), (1.38, 0.1), (1.38, 0.36), (0.26, 0.36)])
    fig.rect(0.72, 0.0, 0.92, 0.18, "dark")
    col(fig, 0.0, 0.36, 1.64, 0.64, "plain")
    thread(fig, 0.4, 0.64, 1.24, 0.78)
    col(fig, 0.0, 0.78, 1.64, 1.06, "plain")
    slab(fig, [(0.1, 1.06), (1.54, 1.06), (1.28, 1.22), (0.36, 1.22)])
    col(fig, 0.36, 1.22, 1.28, 1.94)
    slab(fig, [(0.36, 1.94), (1.28, 1.94), (1.22, 2.0), (0.42, 2.0)], "plain", t=0.01)
    return done(fig)


# --- fasteners, anchors and dowels -------------------------------------------------------------


def fluted_dowels(record: Record) -> Drawn:
    """Fluted dowels: three birch pins side by side, fluted along their length and chamfered."""
    del record
    fig = new()
    for x in (0.0, 0.56, 1.12):
        fig.poly([(x + 0.07, 0.0), (x + 0.45, 0.0), (x + 0.52, 0.1), (x + 0.52, 1.9),
                  (x + 0.45, 2.0), (x + 0.07, 2.0), (x, 1.9), (x, 0.1)],
                 "handle", BIRCH)  # fmt: skip
        light(fig, (x, 0.1, x + 0.52, 1.9))
        fig.lines(((x + 0.06 + 0.1 * k, 0.08), (x + 0.06 + 0.1 * k, 1.92)) for k in range(5))
        fig.lines([((x, 0.1), (x + 0.52, 0.1)), ((x, 1.9), (x + 0.52, 1.9))])
    return done(fig)


def wedge_anchor(record: Record) -> Drawn:
    """A wedge anchor: the threaded stud, its nut and washer, the expansion clip and the cone."""
    del record
    fig = new()
    thread(fig, 0.34, 0.0, 1.3, 0.28)
    hexes(fig, 0.06, 0.24, 1.58, 0.64)
    bar(fig, 0.0, 0.64, 1.64, 0.8, "plain")
    thread(fig, 0.34, 0.8, 1.3, 1.16)
    col(fig, 0.34, 1.16, 1.3, 1.32, "plain")
    slab(fig, [(0.38, 1.32), (1.26, 1.32), (1.32, 1.4), (1.36, 1.7), (0.28, 1.7), (0.32, 1.4)],
         "plain")  # fmt: skip
    for x in (0.6, 1.04):
        fig.rect(x - 0.02, 1.42, x + 0.02, 1.7, "dark")
    slab(fig, [(0.42, 1.7), (1.22, 1.7), (1.38, 1.92), (1.34, 2.0), (0.3, 2.0), (0.26, 1.92)])
    return done(fig)


def u_bolt(record: Record) -> Drawn:
    """A U-bolt: the bent rod, its threaded legs, the saddle plate and a nut on each leg."""
    del record
    fig = new()
    c, outer, inner = (0.82, 0.82), 0.82, 0.44
    fig.poly([*arc(c, outer, 180, 360, 20), (1.64, 1.3), (1.26, 1.3), *arc(c, inner, 360, 180, 16),
              (0.38, 1.3), (0.0, 1.3)])  # fmt: skip
    fig.poly([*arc(c, 0.76, 180, 350, 16), *arc(c, 0.66, 350, 180, 16)], "gloss")
    fig.poly([*arc(c, 0.56, 190, 360, 16), *arc(c, inner, 360, 190, 16)], "shade")
    for x in (0.0, 1.26):
        thread(fig, x, 1.0, x + 0.38, 2.0)
    bar(fig, 0.0, 1.26, 1.64, 1.54, "plain")
    for x in (0.0, 1.16):
        hexes(fig, x, 1.54, x + 0.48, 1.8)
    return done(fig)


def sems_bolt(record: Record) -> Drawn:
    """A SEMS bolt: the hex head, its captive lock and flat washers and the threaded shank."""
    del record
    fig = new()
    slab(fig, [(0.2, 0.06), (0.3, 0.0), (1.34, 0.0), (1.44, 0.06)], "plain", t=0.02)
    hexes(fig, 0.14, 0.06, 1.5, 0.52)
    bar(fig, 0.22, 0.52, 1.42, 0.64, "plain")
    fig.poly([(0.74, 0.52), (0.8, 0.52), (0.9, 0.64), (0.84, 0.64)], "dark")
    bar(fig, 0.0, 0.64, 1.64, 0.78, "plain")
    thread(fig, 0.4, 0.78, 1.24, 1.92)
    slab(fig, [(0.4, 1.92), (1.24, 1.92), (1.14, 2.0), (0.5, 2.0)], "plain", t=0.02)
    return done(fig)


def _hex_prism(fig: Figure, y0: float, y1: float, r: float, ry: float) -> None:
    """A hex standing on its end, seen from a little above: three faces and the top."""
    cx = 0.82
    half, back = r, r / 2
    fig.poly([(cx - half, y0), (cx - back, y0 + ry), (cx - back, y1 + ry), (cx - half, y1)])
    fig.poly(
        [(cx - half, y0), (cx - back, y0 + ry), (cx - back, y1 + ry), (cx - half, y1)], "gloss"
    )
    fig.rect(cx - back, y0 + ry, cx + back, y1 + ry)
    right = [(cx + half, y0), (cx + back, y0 + ry), (cx + back, y1 + ry), (cx + half, y1)]
    fig.poly(right)
    fig.poly(right, "shade")
    fig.poly([(cx - half, y0), (cx - back, y0 - ry), (cx + back, y0 - ry), (cx + half, y0),
              (cx + back, y0 + ry), (cx - back, y0 + ry)], "plain")  # fmt: skip


def flange_nut(record: Record) -> Drawn:
    """A serrated flange nut: the threaded hex on its flange, serrated under the rim."""
    del record
    fig = new()
    drum(fig, 0.0, 0.84, 1.64, 1.94, 0.46, top="part")
    for k in range(1, 12):
        a = math.radians(15 * k)
        x, y = 0.82 + 0.82 * math.cos(a), 1.48 + 0.46 * math.sin(a)
        fig.poly([(x - 0.05, y), (x + 0.05, y), (x, y - 0.14)], "dark")
    _hex_prism(fig, 0.36, 1.02, 0.66, 0.34)
    fig.poly(ell((0.82, 0.36), 0.36, 0.2), "dark")
    crest = ell((0.82, 0.4), 0.3, 0.14, 0, 360, 10)
    fig.lines(zip(crest, crest[1:], strict=False))
    return done(fig)


def t_slot_nut(record: Record) -> Drawn:
    """A T-slot nut: the raised neck with its threaded bore on the wider base."""
    del record
    fig = new()
    for x0, x1 in ((0.0, 0.36), (1.28, 1.64)):
        fig.rect(x0, 0.5, x1, 1.1, "plain")
    fig.rect(0.36, 0.0, 1.28, 0.62, "plain")
    fig.poly(ell((0.82, 0.31), 0.36, 0.22), "part")
    fig.poly(ell((0.82, 0.31), 0.28, 0.17), "dark")
    fig.rect(1.28, 0.5, 1.46, 1.1, "shade")
    slab(fig, [(0.36, 0.62), (1.28, 0.62), (1.28, 1.1), (0.36, 1.1)])
    slab(fig, [(0.0, 1.1), (1.64, 1.1), (1.64, 1.9), (0.0, 1.9)], t=0.1)
    fig.rect(1.3, 1.2, 1.54, 1.8, "shade")
    return done(fig)


def flat_gasket(record: Record) -> Drawn:
    """A flat rubber flange gasket: the bore and four bolt holes, cut from sheet."""
    del record
    fig = new()
    r, edge = 0.3, []
    for cx, cy, start in ((1.34, 1.34, 0), (0.3, 1.34, 90), (0.3, 0.3, 180), (1.34, 0.3, 270)):
        edge += arc((cx, cy), r, start, start + 90, 6)
    slab(fig, edge, "handle", RUBBER, t=0.06)
    fig.disc((0.82, 0.82), 0.28, "hole")
    c = (0.82, 0.82)
    fig.poly([*arc(c, 0.36, 150, 300, 12), *arc(c, 0.29, 300, 150, 12)], "shade")
    fig.poly([*arc(c, 0.36, -30, 120, 12), *arc(c, 0.29, 120, -30, 12)], "gloss")
    for x in (0.28, 1.36):
        for y in (0.28, 1.36):
            fig.disc((x, y), 0.1, "hole")
    fig.poly([(0.3, 0.1), (1.1, 0.1), (1.0, 0.2), (0.4, 0.2)], "gloss")
    return done(fig)


# --- springs, balls, collars and pulleys -------------------------------------------------------


def compression_spring(record: Record) -> Drawn:
    """A compression spring: closed ends and open coils, the far side of each coil behind."""
    del record
    fig = new()
    turns, pitch, wire = 5, 0.36, 0.26
    for k in range(turns):
        y = 0.13 + pitch * k
        fig.poly([(0.08, y + 0.02), (1.56, y + 0.18), (1.56, y + 0.36), (0.08, y + 0.2)], "dark")
    for k in range(turns + 1):
        y = pitch * k - (0.06 if k == turns else 0.0)
        tilt = 0.0 if k in (0, turns) else 0.06
        pts = [(0.0, y + tilt + 0.08), (0.1, y + tilt), (1.54, y - tilt), (1.64, y - tilt + 0.08),
               (1.64, y - tilt + wire - 0.08), (1.54, y - tilt + wire),
               (0.1, y + tilt + wire), (0.0, y + tilt + wire - 0.08)]  # fmt: skip
        fig.poly(pts)
        for a, b, kind in ((0.14, 0.34, "gloss"), (0.66, 1.0, "shade")):
            fig.poly([(0.06, y + tilt + wire * a), (1.58, y - tilt + wire * a),
                      (1.58, y - tilt + wire * b), (0.06, y + tilt + wire * b)], kind)  # fmt: skip
    return done(fig)


def _ball(fig: Figure, role: str, fill: str | None) -> None:
    """A ball: two shadow crescents, the darker at the rim, and a highlight up left."""
    c = (0.82, 0.82)
    fig.disc(c, 0.82, role, fill)
    for start, end, depth in ((-50, 140, 0.3), (-30, 120, 0.16)):
        rim = arc(c, 0.82, start, end, 24)
        span = len(rim) - 1
        inner = []
        for k, (x, y) in enumerate(rim):
            share = depth * math.sin(math.pi * k / span) / 0.82
            inner.append((x + (c[0] - x) * share, y + (c[1] - y) * share))
        fig.poly([*rim, *inner[::-1]], "shade")
    fig.poly(
        [*arc((0.6, 0.56), 0.4, 150, 330, 14), *arc((0.66, 0.62), 0.36, 320, 160, 14)], "gloss"
    )


def precision_ball(record: Record) -> Drawn:
    """A ground steel ball, mirror bright: its highlights and the dark reflection of the bench."""
    del record
    fig = new()
    _ball(fig, "part", None)
    fig.poly(ell((0.52, 0.44), 0.2, 0.14), "gloss")
    fig.poly(ell((0.5, 0.42), 0.1, 0.07), "gloss")
    fig.poly([*ell((0.82, 1.0), 0.7, 0.2, 10, 170, 14), *ell((0.82, 1.0), 0.7, 0.08, 170, 10, 14)],
             "shade")  # fmt: skip
    return done(fig)


def rubber_ball(record: Record) -> Drawn:
    """A solid rubber ball: matte, with the seam its mold leaves."""
    del record
    fig = new()
    _ball(fig, "handle", RUBBER)
    fig.poly(ell((0.5, 0.48), 0.2, 0.14), "gloss")
    seam = ell((0.82, 0.82), 0.82, 0.24, 8, 172, 16)
    fig.lines(zip(seam, seam[1:], strict=False))
    return done(fig)


def shaft_collar(record: Record) -> Drawn:
    """A shaft collar: the ring, its bore, and its clamp screw; a two-piece one is split on both
    sides, with a screw at each."""
    two = _stated(record, "Style", "One-Piece") == "Two-Piece"
    fig = new()
    drum(fig, 0.0, 0.0, 1.64, 1.9, 0.62)
    fig.poly(ell((0.82, 0.62), 0.42, 0.31), "dark")
    fig.poly(ell((0.82, 0.74), 0.3, 0.18), "shade")
    if two:
        fig.poly([(0.0, 0.58), (0.4, 0.58), (0.4, 0.66), (0.0, 0.66)], "dark")
        fig.poly([(1.24, 0.58), (1.64, 0.58), (1.64, 0.66), (1.24, 0.66)], "dark")
        for x in (0.4, 1.24):
            _bolt(fig, (x, 1.46), 0.19)
        fig.rect(0.02, 0.66, 0.08, 1.26, "dark")
    else:
        fig.rect(0.78, 0.92, 0.86, 1.9, "dark")
        _bolt(fig, (1.2, 1.46), 0.22)
    return done(fig)


def timing_pulley(record: Record) -> Drawn:
    """A timing belt pulley: the two flanges, the toothed face and the bored hub; an idler's face is
    smooth, on a bearing."""
    idler = _stated(record, "Style", "Standard") == "Idler"
    fig = new()
    drum(fig, 0.0, 1.06, 1.64, 1.98, 0.36, "plain", top="dark")
    drum(fig, 0.1, 0.4, 1.54, 1.72, 0.32)
    if not idler:
        for k in range(1, 12):
            x = 0.82 - 0.7 * math.cos(math.pi * k / 12)
            dip = 0.32 * math.sin(math.pi * k / 12)
            fig.rect(x - 0.028, 0.76 + dip, x + 0.028, 1.4 + dip, "dark")
    drum(fig, 0.0, 0.0, 1.64, 0.88, 0.38)
    if idler:
        fig.poly(ell((0.82, 0.38), 0.52, 0.24), "dark")
        fig.poly(ell((0.82, 0.38), 0.4, 0.18), "plain")
    else:
        drum(fig, 0.38, 0.08, 1.26, 0.6, 0.2)
        fig.disc((0.82, 0.54), 0.05, "dark")
    fig.poly(ell((0.82, 0.38 if idler else 0.28), 0.24, 0.11), "dark")
    return done(fig)


def hose_clamp(record: Record) -> Drawn:
    """A hose clamp: the band, seen from a little above, and its worm screw; a spring clamp has two
    tangs to squeeze instead."""
    spring = _stated(record, "Style", "Worm Gear") == "Spring"
    fig = new()
    top, low, ry = 0.84, 1.48, 0.44
    front = [*ell((0.82, top), 0.82, ry, 180, 0, 16), *ell((0.82, low), 0.82, ry, 0, 180, 16)]
    fig.poly([(0.0, top), *ell((0.82, top), 0.82, ry, 180, 360, 18), (1.64, low),
              *ell((0.82, low), 0.78, ry - 0.04, 360, 180, 18), (0.0, low)], "plain")  # fmt: skip
    fig.poly([*ell((0.82, top), 0.78, ry - 0.04, 180, 360, 16),
              *ell((0.82, low), 0.78, ry - 0.04, 360, 180, 16)], "shade")  # fmt: skip
    fig.poly(front)
    for a, b, kind in ((16, 60, "shade"), (126, 148, "gloss")):
        fig.poly([*ell((0.82, top), 0.82, ry, a, b, 6), *ell((0.82, low), 0.82, ry, b, a, 6)], kind)
    if spring:
        for x in (0.42, 0.9):
            slab(fig, [(x, 1.0), (x, 0.46), (x + 0.06, 0.4), (x + 0.26, 0.4), (x + 0.32, 0.46),
                       (x + 0.32, 1.0)], "plain")  # fmt: skip
        slab(fig, [(0.3, 1.36), (1.34, 1.36), (1.34, 1.62), (0.3, 1.62)], "plain")
    else:
        fig.lines(((0.2 + 0.11 * k, 1.36), (0.24 + 0.11 * k, 1.66)) for k in range(12))
        slab(fig, [(0.3, 0.96), (1.16, 0.96), (1.16, 1.56), (0.3, 1.56)], "plain")
        bar(fig, 0.36, 1.02, 1.1, 1.36)
        fig.lines(((0.42 + 0.1 * k, 1.36), (0.48 + 0.1 * k, 1.02)) for k in range(7))
        hexes(fig, 1.16, 0.98, 1.46, 1.4, "plain")
        fig.rect(1.16, 1.15, 1.46, 1.22, "dark")
    return done(fig)


# --- valves, casters and padlocks --------------------------------------------------------------


def ball_valve(record: Record) -> Drawn:
    """A ball valve: the lever in its vinyl sleeve, the stem and packing nut, the body and the two
    hex ends."""
    del record
    fig = new()
    slab(fig, [(0.46, 0.2), (0.62, 0.06), (1.58, 0.0), (1.64, 0.1), (1.64, 0.34), (1.0, 0.4),
               (0.46, 0.4)], "handle", GRIP_BLUE)  # fmt: skip
    hexes(fig, 0.62, 0.36, 1.02, 0.6, "plain")
    col(fig, 0.5, 0.58, 1.14, 0.8)
    disc(fig, (0.82, 1.34), 0.66)
    for x0, x1 in ((0.0, 0.36), (1.28, 1.64)):
        bar(fig, x0, 0.8, x1, 1.88)
        fig.rect(x0, 0.8, x1, 1.07, "gloss")
        fig.lines([((x0, 1.07), (x1, 1.07)), ((x0, 1.61), (x1, 1.61))])
    bar(fig, 0.34, 0.94, 0.46, 1.74, "plain")
    bar(fig, 1.18, 0.94, 1.3, 1.74, "plain")
    fig.rect(0.64, 1.24, 1.0, 1.44, "plain")
    fig.lines([((0.7, 1.34), (0.94, 1.34))])
    return done(fig)


def swivel_caster(record: Record) -> Drawn:
    """A swivel caster: the top plate, its bolts, the swivel, the fork, the wheel and its axle."""
    del record
    fig = new()
    for x in (0.2, 1.22):
        hexes(fig, x, 0.0, x + 0.22, 0.12, "plain")
    slab(fig, [(0.0, 0.1), (1.64, 0.1), (1.64, 0.32), (0.0, 0.32)], "plain")
    bar(fig, 0.3, 0.32, 1.34, 0.5)
    disc(fig, (0.82, 1.28), 0.72, "handle", RUBBER, bore=0.5)
    disc(fig, (0.82, 1.28), 0.48, "handle", PAPER_LABEL)
    slab(fig, [(0.3, 0.5), (1.34, 0.5), (1.3, 0.8), (1.04, 1.36), (0.94, 1.5), (0.7, 1.5),
               (0.6, 1.36), (0.34, 0.8)])  # fmt: skip
    disc(fig, (0.82, 1.3), 0.14, "plain", steps=6)
    fig.poly(hexagon((0.82, 1.3), 0.08), "dark")
    return done(fig)


def padlock(record: Record) -> Drawn:
    """A laminated padlock: the hardened shackle, the riveted steel plates and the keyway."""
    del record
    fig = new()
    c = (0.82, 0.62)
    fig.poly([*arc(c, 0.62, 180, 360, 18), (1.44, 0.9), (1.18, 0.9), *arc(c, 0.36, 360, 180, 14),
              (0.46, 0.9), (0.2, 0.9)], "plain")  # fmt: skip
    fig.poly([*arc(c, 0.58, 180, 340, 14), *arc(c, 0.5, 340, 180, 14)], "gloss")
    fig.poly([*arc(c, 0.46, 200, 360, 14), *arc(c, 0.36, 360, 200, 14)], "shade")
    slab(fig, [(0.0, 0.92), (0.08, 0.84), (1.56, 0.84), (1.64, 0.92), (1.64, 1.92), (1.56, 2.0),
               (0.08, 2.0), (0.0, 1.92)], t=0.08)  # fmt: skip
    fig.lines(((0.0, 0.98 + 0.12 * k), (1.64, 0.98 + 0.12 * k)) for k in range(8))
    for x in (0.16, 1.48):
        for y in (0.98, 1.86):
            disc(fig, (x, y), 0.08, "plain", steps=4)
    disc(fig, (0.82, 1.44), 0.24, "handle", SAFETY, steps=8)
    fig.disc((0.82, 1.38), 0.06, "dark")
    fig.rect(0.79, 1.38, 0.85, 1.58, "dark")
    return done(fig)


#: Type key -> its drawing.
SHOP: dict[str, Callable[[Record], Drawn]] = {
    "ball_stock_precision": precision_ball,
    "ball_stock_rubber": rubber_ball,
    "ball_valves": ball_valve,
    "bench_vises": bench_vise,
    "bit_sharpeners": bit_sharpener,
    "center_punches": center_punch,
    "circle_cutters": circle_cutter,
    "compression_springs": compression_spring,
    "cutter_storage_racks": cutter_rack,
    "fastener_extractors": fastener_extractor_set,
    "flat_gaskets": flat_gasket,
    "fluted_dowels": fluted_dowels,
    "grooving_cutters": grooving_cutter,
    "hose_clamps": hose_clamp,
    "induction_heaters": induction_heater,
    "keyed_padlocks": padlock,
    "milling_collets": milling_collet,
    "milling_tool_holders": collet_chuck,
    "nut_splitters": nut_splitter,
    "seal_pick_sets": seal_pick_set,
    "sems_bolts": sems_bolt,
    "serrated_flange_nuts": flange_nut,
    "shaft_collars": shaft_collar,
    "side_lock_holders": side_lock_holder,
    "swivel_casters": swivel_caster,
    "t_slot_nuts": t_slot_nut,
    "tap_wrenches": tap_wrench,
    "thread_pitch_gages": pitch_gage,
    "timing_pulleys": timing_pulley,
    "u_bolts": u_bolt,
    "wedge_anchors": wedge_anchor,
    "wheel_mandrels": wheel_mandrel,
}
