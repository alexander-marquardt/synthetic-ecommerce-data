"""The Barry Plotter range's badge pictures, one per motif (gen#942): data only.

Each motif of the range (:data:`barry_plotter.MOTIFS`) is a film of its own, and a product
prints its motif's badge (:mod:`film_emblems`), so the 15 green stoneware mugs a
``green barry plotter cup`` search returns show 15 pictures, not one mug 15 times. A picture
is one large subject: the creature or scene of its motif, with nothing so fine that it
disappears at mug-badge size. Barry himself, the kid gardener of gen#928 (round-rimmed glasses,
tousled dark hair), sits small in an inset at the lower right of every badge
(:func:`with_barry`), so the 15 still read as one franchise.

The drawings are original (MIT, like the rest of the code) and drawn after nothing from the real
films: no owl, wand, scar, robe, pointed hat, castle, train or house scarf. They are drawn in the
badge's unit box, -1 to 1 on each axis, y down, inside the white disc and clear of its ring: with
M, L, Q, C and Z path commands, circles and ellipses, so a test can bound every point
(``tests/test_barry_plotter_motifs_942.py``).
"""

# ruff: noqa: E501 -- SVG literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math
from collections.abc import Callable

#: The badge's ink, the same as :data:`film_emblems.EMBLEM_INK` (not the kit's ink, so a brand's
#: restyle never changes it).
INK = "#25303b"

SKIN, HAIR, BARK, SOIL, LEAF, GOLD, SKY = (
    "#f3cfa4", "#3b2a1f", "#9a6232", "#7a5232", "#5fae4a", "#f2c12e", "#cfe8f7",
)  # fmt: skip


def _p(d: str, fill: str = "none", w: float = 0.05, stroke: str = INK) -> str:
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w:g}" stroke-linecap="round" stroke-linejoin="round"/>'


def _c(cx: float, cy: float, r: float, fill: str, w: float = 0.05) -> str:
    stroke = f' stroke="{INK}" stroke-width="{w:g}"' if w else ""
    return f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="{fill}"{stroke}/>'


def _e(cx: float, cy: float, rx: float, ry: float, fill: str, w: float = 0.05) -> str:
    stroke = f' stroke="{INK}" stroke-width="{w:g}"' if w else ""
    return f'<ellipse cx="{cx:g}" cy="{cy:g}" rx="{rx:g}" ry="{ry:g}" fill="{fill}"{stroke}/>'


def _limb(d: str, color: str, w: float) -> str:
    """A thick stroke of ``color`` with an ink outline: a stalk, a handle, a path."""
    return _p(d, "none", w + 0.06) + _p(d, "none", w, color)


def _star(cx: float, cy: float, s: float, fill: str = GOLD) -> str:
    """A four-pointed sparkle."""
    k = 0.3 * s
    pts = ((0, -s), (k, -k), (s, 0), (k, k), (0, s), (-k, k), (-s, 0), (-k, -k))
    d = "M" + " L".join(f"{cx + x:.3g},{cy + y:.3g}" for x, y in pts) + " Z"
    return _p(d, fill, 0.03)


def _ring(cx: float, cy: float, inner: float, outer: float, n: int, turn: float = 0.0) -> str:
    """A closed outline of ``n`` points alternating ``outer`` and ``inner`` radii: a cog, a petal
    rosette's rim."""
    pts = []
    for i in range(2 * n):
        a = turn + math.pi * i / n
        r = outer if i % 2 == 0 else inner
        pts.append(f"{cx + r * math.cos(a):.3f},{cy + r * math.sin(a):.3f}")
    return "M" + " L".join(pts) + " Z"


def _g(transform: str, *parts: str) -> str:
    return f'<g transform="{transform}">{"".join(parts)}</g>'


# -- Barry, in the corner of every badge ------------------------------------------------------

#: Barry's head (gen#928's kid gardener): ears, face, tousled dark hair, round-rimmed glasses and a
#: smile. Glasses and hair are generic; no scar.
_BARRY_HEAD = (
    _c(-0.34, -0.02, 0.07, SKIN, 0.04),
    _c(0.34, -0.02, 0.07, SKIN, 0.04),
    _c(0, -0.06, 0.34, SKIN),
    _p(
        "M-0.37,-0.02 Q-0.44,-0.3 -0.3,-0.44 L-0.34,-0.54 L-0.2,-0.5 L-0.16,-0.64 L-0.04,-0.54 L0.06,-0.66 L0.14,-0.53 L0.28,-0.58 L0.26,-0.46 Q0.44,-0.3 0.37,-0.02 L0.3,-0.16 L0.22,-0.1 L0.16,-0.22 L0.06,-0.12 L-0.02,-0.24 L-0.1,-0.12 L-0.18,-0.22 L-0.26,-0.1 L-0.3,-0.18 Z",
        HAIR,
        0.04,
    ),
    _c(-0.14, -0.02, 0.1, "#eef6fb", 0.045),
    _c(0.14, -0.02, 0.1, "#eef6fb", 0.045),
    _p(
        "M-0.04,-0.03 Q0,-0.07 0.04,-0.03 M-0.24,-0.04 L-0.33,-0.06 M0.24,-0.04 L0.33,-0.06",
        "none",
        0.04,
    ),
    _c(-0.14, -0.01, 0.03, INK, 0),
    _c(0.14, -0.01, 0.03, INK, 0),
    _p("M-0.1,0.13 Q0,0.21 0.1,0.13", "none", 0.04),
)

#: The inset Barry sits in: its center and radius in the unit box.
INSET = (0.48, 0.47, 0.25)


def barry_corner() -> str:
    """Barry's head in a small white inset at the badge's lower right."""
    x, y, r = INSET
    return _c(x, y, r, "#ffffff", 0.03) + _g(
        f"translate({x:g} {y + 0.088:g}) scale(0.44)", *_BARRY_HEAD
    )


def with_barry(picture: Callable[[], str]) -> Callable[[], str]:
    """``picture`` with Barry in its corner: the badge picture of one motif."""

    def drawn() -> str:
        return picture() + barry_corner()

    drawn.__doc__ = picture.__doc__
    return drawn


# -- the 15 motifs ----------------------------------------------------------------------------


def talking_scarecrow() -> str:
    """Talking Scarecrow: a scarecrow on its post in a patched red shirt and a straw hat, mouth
    open, with a speech bubble."""
    straw = "#d9a93a"
    return "".join([
        _p("M-0.17,-0.1 L-0.07,-0.1 L-0.07,0.8 L-0.17,0.8 Z", BARK),
        _p("M-0.78,-0.02 L0.5,-0.02 L0.5,0.06 L-0.78,0.06 Z", BARK),
        _p("M-0.5,-0.06 L-0.7,-0.16 M-0.5,0.02 L-0.74,0.02 M-0.5,0.08 L-0.7,0.2 M0.26,-0.06 L0.46,-0.16 M0.26,0.02 L0.5,0.02 M0.26,0.08 L0.46,0.2", "none", 0.06, straw),
        _p("M-0.5,-0.08 L0.26,-0.08 L0.18,0.44 L-0.42,0.44 Z", "#c8473a"),
        _p("M-0.36,0.14 L-0.2,0.14 L-0.2,0.3 L-0.36,0.3 Z", "#f2d14b", 0.035),
        _p("M0.0,0.04 L0.12,0.04 L0.12,0.16 L0.0,0.16 Z", "#6f9a45", 0.035),
        _c(-0.12, -0.32, 0.22, "#e9c77b"),
        _c(-0.2, -0.36, 0.035, INK, 0),
        _c(-0.04, -0.36, 0.035, INK, 0),
        _e(-0.12, -0.23, 0.08, 0.055, "#7a1c1a", 0.035),
        _p("M-0.3,-0.5 L-0.26,-0.72 L0.02,-0.72 L0.06,-0.5 Z", straw),
        _p("M-0.44,-0.52 L0.2,-0.52 L0.2,-0.45 L-0.44,-0.45 Z", straw),
        _e(0.46, -0.5, 0.21, 0.14, "#ffffff", 0.04),
        _p("M0.32,-0.4 L0.16,-0.3 L0.38,-0.37", "#ffffff", 0.04),
        _c(0.38, -0.5, 0.03, INK, 0),
        _c(0.46, -0.5, 0.03, INK, 0),
        _c(0.54, -0.5, 0.03, INK, 0),
    ])  # fmt: skip


def moonlit_glasshouse() -> str:
    """Moonlit Glasshouse: a glasshouse of pale panes under a big crescent moon, its plants
    glowing."""
    return "".join([
        _p("M0.32,-0.74 C-0.02,-0.68 -0.04,-0.16 0.32,-0.12 C0.1,-0.26 0.1,-0.6 0.32,-0.74 Z", "#f2d14b"),
        _star(-0.6, -0.38, 0.09, "#f2d14b"),
        _star(0.6, -0.12, 0.08, "#f2d14b"),
        _p("M-0.72,0.04 L-0.22,-0.4 L0.28,0.04 Z", "#bfe2f2"),
        _p("M-0.66,0.04 L0.22,0.04 L0.22,0.54 L-0.66,0.54 Z", "#d6eef8"),
        _c(-0.52, 0.44, 0.09, "#f6e27a", 0),
        _c(-0.3, 0.42, 0.1, "#f6e27a", 0),
        _c(-0.06, 0.44, 0.09, "#f6e27a", 0),
        _c(-0.52, 0.44, 0.06, LEAF, 0.035),
        _c(-0.3, 0.42, 0.07, LEAF, 0.035),
        _c(-0.06, 0.44, 0.06, LEAF, 0.035),
        _p("M-0.22,-0.4 L-0.22,0.54 M-0.44,0.04 L-0.44,0.54 M0,0.04 L0,0.54 M-0.66,0.28 L0.22,0.28 M-0.22,-0.4 L-0.46,0.04 M-0.22,-0.4 L0.02,0.04", "none", 0.03),
    ])  # fmt: skip


def enchanted_allotment() -> str:
    """Enchanted Allotment: three raised beds of green plants, a winding path between them, and
    sparkles."""
    beds = ((-0.72, -0.4, -0.2, -0.08), (0.04, -0.56, 0.54, -0.24), (-0.64, 0.14, -0.1, 0.46))
    parts = [
        _limb(
            "M-0.04,0.82 C0.02,0.5 0.06,0.24 -0.06,0.06 C-0.16,-0.08 -0.04,-0.3 -0.12,-0.66",
            "#e2c48a",
            0.13,
        )
    ]
    for x0, y0, x1, y1 in beds:
        parts.append(_p(f"M{x0:g},{y0:g} L{x1:g},{y0:g} L{x1:g},{y1:g} L{x0:g},{y1:g} Z", SOIL))
        cy, step = (y0 + y1) / 2, (x1 - x0) / 3
        parts += [_c(x0 + step * (i + 0.5), cy, 0.075, LEAF, 0.035) for i in range(3)]
    parts += [_star(0.04, -0.78, 0.11), _star(0.66, 0.0, 0.1), _star(-0.8, 0.0, 0.09)]
    return "".join(parts)


def _hatchling(cx: float, cy: float, r: float, color: str) -> str:
    return "".join([
        _p(f"M{cx:g},{cy - r:g} Q{cx + 0.02:g},{cy - r - 0.12:g} {cx + 0.1:g},{cy - r - 0.12:g} Q{cx + 0.08:g},{cy - r - 0.02:g} {cx:g},{cy - r:g} Z", LEAF, 0.03),
        _c(cx, cy, r, color),
        _c(cx - 0.06, cy - 0.02, 0.045, "#ffffff", 0.025),
        _c(cx + 0.06, cy - 0.02, 0.045, "#ffffff", 0.025),
        _c(cx - 0.055, cy - 0.015, 0.02, INK, 0),
        _c(cx + 0.065, cy - 0.015, 0.02, INK, 0),
        _p(f"M{cx - 0.05:g},{cy + 0.07:g} Q{cx:g},{cy + 0.12:g} {cx + 0.05:g},{cy + 0.07:g}", "none", 0.03),
    ])  # fmt: skip


def hatchlings() -> str:
    """Hatchlings: three round little creatures, each with a leaf sprout, climbing out of a torn
    seed packet."""
    return "".join([
        _hatchling(-0.4, -0.36, 0.17, "#7cc46a"),
        _hatchling(-0.14, -0.5, 0.19, "#f19ac0"),
        _hatchling(0.12, -0.36, 0.17, "#7fb6e6"),
        _p("M-0.52,0.62 L-0.52,-0.2 L-0.42,-0.28 L-0.32,-0.2 L-0.22,-0.28 L-0.12,-0.2 L-0.02,-0.28 L0.08,-0.2 L0.2,-0.28 L0.2,0.62 Z", "#f1e3c2"),
        _c(-0.16, 0.24, 0.15, "#e98bb0", 0.04),
        _c(-0.16, 0.24, 0.06, "#f2d14b", 0.035),
        _p("M-0.4,0.5 L0.08,0.5", "none", 0.04),
    ])  # fmt: skip


def _snail(cx: float, cy: float, s: float) -> str:
    body = "#c9b48a"
    spiral = []
    for i in range(22):
        a = i * 0.45
        r = 0.4 * s * (1 - i / 24)
        spiral.append(f"{cx + r * math.cos(a):.3f},{cy + r * math.sin(a):.3f}")
    return "".join([
        _c(cx, cy, 0.66 * s, "#f6f9c8", 0),
        _e(cx + 0.05 * s, cy + 0.44 * s, 0.85 * s, 0.17 * s, body, 0.04),
        _p(f"M{cx + 0.72 * s:.3f},{cy + 0.12 * s:.3f} L{cx + 0.66 * s:.3f},{cy - 0.32 * s:.3f} M{cx + 0.86 * s:.3f},{cy + 0.12 * s:.3f} L{cx + 0.98 * s:.3f},{cy - 0.3 * s:.3f}", "none", 0.035),
        _c(cx + 0.66 * s, cy - 0.34 * s, 0.07 * s, INK, 0),
        _c(cx + 0.98 * s, cy - 0.32 * s, 0.07 * s, INK, 0),
        _c(cx + 0.8 * s, cy + 0.28 * s, 0.2 * s, body, 0.04),
        _c(cx, cy, 0.5 * s, "#d7e85a"),
        _p("M" + " L".join(spiral), "none", 0.04),
    ])  # fmt: skip


def snail_parade() -> str:
    """Snail Parade: three snails with glowing shells in a line, the smallest leading."""
    return _snail(-0.36, 0.2, 0.42) + _snail(0.16, -0.18, 0.3) + _snail(0.42, -0.56, 0.2)


def compost_dragon() -> str:
    """Compost Dragon: a green dragon asleep, curled on a brown compost heap, snoring Zs."""
    green, belly, spike = "#5aa55a", "#9fd08a", "#e6874a"
    return "".join([
        _p("M-0.8,0.42 Q-0.6,-0.02 -0.16,0.0 Q0.26,0.02 0.34,0.42 Z", SOIL),
        _p("M-0.6,0.28 L-0.5,0.26 M-0.3,0.18 L-0.2,0.2 M0.0,0.3 L0.1,0.28 M-0.42,0.36 L-0.34,0.38", "none", 0.04, "#4a321e"),
        _limb("M0.04,-0.02 Q0.42,0.0 0.36,-0.26 Q0.3,-0.4 0.16,-0.32", green, 0.09),
        _p("M0.16,-0.32 L0.06,-0.26 L0.14,-0.42 Z", spike, 0.035),
        _p("M-0.44,-0.2 L-0.38,-0.36 L-0.3,-0.22 Z M-0.26,-0.24 L-0.18,-0.4 L-0.1,-0.24 Z M-0.08,-0.22 L0.0,-0.36 L0.06,-0.18 Z", spike, 0.035),
        _e(-0.2, -0.06, 0.34, 0.19, green),
        _p("M-0.36,0.02 Q-0.2,0.12 0.04,0.02", belly, 0.035),
        _p("M-0.28,-0.1 Q-0.16,-0.4 0.02,-0.28 Q-0.06,-0.16 -0.28,-0.1 Z", "#7fc07f", 0.035),
        _p("M-0.62,-0.4 L-0.68,-0.56 L-0.54,-0.43 Z M-0.5,-0.41 L-0.48,-0.56 L-0.42,-0.39 Z", "#e6c35a", 0.035),
        _c(-0.56, -0.26, 0.17, green),
        _e(-0.72, -0.2, 0.11, 0.08, green),
        _c(-0.77, -0.22, 0.02, INK, 0),
        _p("M-0.62,-0.3 Q-0.56,-0.25 -0.5,-0.3", "none", 0.04),
        _p("M0.1,-0.64 L0.26,-0.64 L0.1,-0.48 L0.26,-0.48 M0.34,-0.8 L0.46,-0.8 L0.34,-0.68 L0.46,-0.68", "none", 0.045),
    ])  # fmt: skip


def potting_shed() -> str:
    """Potting Shed: a crooked wooden shed with a slanted roof, a crooked door, a window and a
    leaning chimney pipe."""
    return "".join([
        _p("M0.02,-0.3 L0.1,-0.31 L0.16,-0.54 L0.07,-0.56 Z", "#8a8f96", 0.04),
        _p("M0.12,-0.6 Q0.2,-0.7 0.12,-0.76 Q0.06,-0.82 0.14,-0.86", "none", 0.035),
        _p("M-0.6,-0.02 L0.2,-0.08 L0.24,0.62 L-0.56,0.66 Z", "#b07a45"),
        _p("M-0.58,0.18 L0.21,0.12 M-0.57,0.36 L0.22,0.3 M-0.57,0.52 L0.23,0.46", "none", 0.025),
        _p("M-0.76,0.02 L-0.24,-0.58 L0.38,-0.06 Z", "#5b6e7a"),
        _p("M-0.18,0.2 L0.06,0.18 L0.08,0.64 L-0.16,0.65 Z", "#7a4a26"),
        _c(0.02, 0.42, 0.03, "#f2d14b", 0.02),
        _p("M-0.48,0.08 L-0.28,0.07 L-0.27,0.26 L-0.47,0.27 Z", SKY, 0.04),
        _p("M-0.38,0.075 L-0.37,0.265 M-0.475,0.17 L-0.275,0.165", "none", 0.03),
    ])  # fmt: skip


def wheelbarrow_race() -> str:
    """Wheelbarrow Race: a red wheelbarrow full of soil speeding right, with speed lines and a
    checkered flag."""
    return "".join([
        _p("M-0.72,-0.42 L-0.44,-0.42 M-0.86,0.3 L-0.62,0.3 M-0.8,0.44 L-0.6,0.44", "none", 0.05),
        _p("M-0.84,0.04 L-0.5,0.1 L0.08,0.26 M-0.48,0.08 L-0.5,0.34 M-0.3,0.12 L-0.32,0.34", "none", 0.06),
        _p("M-0.66,-0.28 Q-0.22,-0.54 0.2,-0.28 Z", SOIL),
        _p("M-0.7,-0.28 L0.24,-0.28 L0.04,0.08 L-0.56,0.08 Z", "#c8473a"),
        _c(0.08, 0.26, 0.18, "#3a3a3e"),
        _c(0.08, 0.26, 0.05, "#d9d9d9", 0.03),
        _p("M0.3,-0.12 L0.3,-0.7", "none", 0.05),
        _p("M0.3,-0.7 L0.58,-0.66 L0.58,-0.44 L0.3,-0.48 Z", "#ffffff", 0.04),
        _p("M0.3,-0.7 L0.44,-0.68 L0.44,-0.57 L0.3,-0.59 Z M0.44,-0.57 L0.58,-0.55 L0.58,-0.44 L0.44,-0.46 Z", INK, 0.02),
    ])  # fmt: skip


def scary_raven() -> str:
    """Scary Raven: a black raven on a fence post, wings raised, with a big yellow glaring eye and
    a grey beak."""
    black, wing = "#2a2a2e", "#44444c"
    return "".join([
        _p("M-0.14,0.32 L0.06,0.32 L0.06,0.86 L-0.14,0.86 Z", BARK),
        _p("M-0.4,0.2 L-0.74,0.46 L-0.62,0.52 L-0.32,0.3 Z", black),
        _p("M-0.2,-0.12 Q-0.6,-0.62 -0.78,-0.3 L-0.62,-0.26 L-0.72,-0.12 L-0.54,-0.1 L-0.6,0.04 Q-0.38,0.02 -0.2,-0.12 Z", wing),
        _p("M0.0,-0.12 Q0.1,-0.62 0.44,-0.7 L0.38,-0.58 L0.56,-0.56 L0.42,-0.46 L0.52,-0.38 Q0.3,-0.3 0.0,-0.12 Z", wing),
        _e(-0.1, 0.02, 0.36, 0.3, black),
        _p("M-0.1,0.3 L-0.12,0.38 M0.0,0.3 L0.02,0.38", "none", 0.05, "#e6874a"),
        _p("M0.36,-0.36 L0.66,-0.26 L0.36,-0.18 Z", "#8a8f96"),
        _c(0.2, -0.3, 0.2, black),
        _c(0.25, -0.34, 0.075, "#f2d14b", 0.03),
        _c(0.27, -0.33, 0.035, INK, 0),
        _p("M0.12,-0.48 L0.36,-0.4", "none", 0.05, "#f2d14b"),
    ])  # fmt: skip


def clockwork_mole() -> str:
    """Clockwork Mole: a grey mole popping out of a molehill, a brass cog on its side and a
    wind-up key in its back."""
    fur, brass = "#6b6676", "#d4a73a"
    ux, uy = 0.86, -0.51  # across the key's stem
    kx, ky = -0.46, -0.42  # the key's hub
    return "".join([
        _p(f"M-0.34,-0.2 L{kx:g},{ky:g}", "none", 0.07, brass),
        _c(kx + 0.11 * ux, ky + 0.11 * uy, 0.1, brass, 0.04),
        _c(kx - 0.11 * ux, ky - 0.11 * uy, 0.1, brass, 0.04),
        _c(kx, ky, 0.05, brass, 0.04),
        _e(-0.18, 0.02, 0.4, 0.32, fur),
        _p("M0.16,-0.08 Q0.38,-0.02 0.44,0.04 Q0.32,0.14 0.14,0.12 Z", fur),
        _c(0.45, 0.04, 0.065, "#f19ac0", 0.035),
        _c(0.06, -0.06, 0.035, INK, 0),
        _p(_ring(-0.26, 0.02, 0.1, 0.15, 8), brass, 0.035),
        _c(-0.26, 0.02, 0.04, fur, 0.03),
        _p("M-0.76,0.5 Q-0.2,0.08 0.34,0.5 Z", SOIL),
        _e(0.02, 0.3, 0.13, 0.08, "#f2b8a0", 0.04),
        _e(-0.38, 0.32, 0.13, 0.08, "#f2b8a0", 0.04),
    ])  # fmt: skip


def frost_fairy() -> str:
    """Frost Fairy: a small fairy in an icy blue dress with two pairs of pale wings, frost sparkles
    around her."""
    wing, dress, ice = "#e3f3fc", "#8fc6ec", "#7ab8e6"
    return _g("translate(-0.1 -0.04)", *[
        _p("M-0.06,-0.1 Q-0.56,-0.62 -0.62,-0.12 Q-0.4,0.02 -0.06,-0.1 Z", wing, 0.04),
        _p("M0.06,-0.1 Q0.56,-0.62 0.62,-0.12 Q0.4,0.02 0.06,-0.1 Z", wing, 0.04),
        _p("M-0.04,0.0 Q-0.44,0.04 -0.42,0.32 Q-0.2,0.32 -0.04,0.0 Z", wing, 0.04),
        _p("M0.04,0.0 Q0.4,0.04 0.36,0.26 Q0.18,0.28 0.04,0.0 Z", wing, 0.04),
        _p("M-0.1,-0.16 L0.1,-0.16 L0.26,0.4 L-0.26,0.4 Z", dress),
        _p("M-0.09,-0.1 L-0.26,0.08 M0.09,-0.1 L0.24,-0.28", "none", 0.05),
        _c(-0.26, 0.08, 0.035, "#f3cfa4", 0.025),
        _star(0.28, -0.36, 0.08, ice),
        _p("M-0.1,0.4 L-0.12,0.56 M0.1,0.4 L0.12,0.56", "none", 0.05),
        _c(0, -0.3, 0.13, "#f3cfa4"),
        _p("M-0.14,-0.3 Q-0.16,-0.48 0,-0.47 Q0.16,-0.48 0.14,-0.3 Q0.04,-0.4 -0.14,-0.3 Z", "#f4f8fb", 0.035),
        _c(-0.045, -0.29, 0.02, INK, 0),
        _c(0.045, -0.29, 0.02, INK, 0),
        _star(-0.54, 0.42, 0.1, ice),
        _star(0.56, 0.06, 0.07, ice),
        _star(-0.46, -0.5, 0.08, ice),
    ])  # fmt: skip


def _beetle() -> str:
    """A beetle seen from above, its wings dotted with glowing spots, about 0.7 across."""
    shell, dark, glow = "#5a3f9c", "#2f2a55", "#f2e25a"
    return "".join([
        _p("M-0.26,-0.12 L-0.46,-0.24 M-0.3,0.04 L-0.52,0.04 M-0.26,0.2 L-0.46,0.34 M0.26,-0.12 L0.46,-0.24 M0.3,0.04 L0.52,0.04 M0.26,0.2 L0.46,0.34", "none", 0.05),
        _p("M-0.06,-0.5 Q-0.14,-0.64 -0.24,-0.66 M0.06,-0.5 Q0.14,-0.64 0.24,-0.66", "none", 0.04),
        _c(0, -0.44, 0.1, dark),
        _e(0, -0.28, 0.2, 0.1, dark),
        _e(0, 0.08, 0.3, 0.36, shell),
        _p("M0,-0.24 L0,0.44", "none", 0.04),
        _c(-0.13, -0.04, 0.05, glow, 0),
        _c(0.12, 0.06, 0.05, glow, 0),
        _c(-0.12, 0.22, 0.05, glow, 0),
        _c(0.13, 0.26, 0.04, glow, 0),
    ])  # fmt: skip


def midnight_beetles() -> str:
    """Midnight Beetles: a big violet beetle with glowing spots and a smaller one behind it, under
    a crescent moon and stars."""
    return "".join(
        [
            _p(
                "M0.52,-0.76 C0.28,-0.72 0.26,-0.36 0.52,-0.32 C0.38,-0.42 0.38,-0.64 0.52,-0.76 Z",
                "#f2d14b",
            ),
            _star(-0.64, -0.36, 0.08, "#f2d14b"),
            _star(0.66, 0.0, 0.07, "#f2d14b"),
            _g("translate(-0.5 0.24) scale(0.42)", _beetle()),
            _g("translate(0.0 -0.06) scale(1.1)", _beetle()),
        ]
    )


def whispering_bramble() -> str:
    """Whispering Bramble: a round bramble bush with a face, blackberries in its leaves, thorny
    shoots, whispering to one side."""
    bush, stem, berry = "#4f8f3f", "#3e6e30", "#3b2147"
    lobes = ((-0.44, -0.04, 0.26), (-0.12, -0.26, 0.3), (0.2, -0.04, 0.26), (-0.12, 0.14, 0.3))
    return "".join([
        _limb("M0.36,0.1 Q0.62,0.06 0.6,-0.22 Q0.58,-0.36 0.46,-0.36", stem, 0.04),
        _limb("M-0.6,0.18 Q-0.82,0.2 -0.78,0.42", stem, 0.04),
        _p("M0.6,-0.12 L0.68,-0.14 L0.62,-0.06 Z M0.52,0.06 L0.56,0.14 L0.47,0.1 Z M-0.74,0.24 L-0.82,0.28 L-0.74,0.32 Z", stem, 0.03),
        *(_c(x, y, r, bush, 0.1) for x, y, r in lobes),
        *(_c(x, y, r, bush, 0) for x, y, r in lobes),
        *(_c(x, y, 0.065, berry, 0.03) for x, y in ((-0.5, -0.14), (0.24, -0.16), (-0.36, 0.24), (0.14, 0.24), (-0.12, -0.44))),
        _e(-0.24, -0.08, 0.06, 0.075, "#ffffff", 0.03),
        _e(0.0, -0.08, 0.06, 0.075, "#ffffff", 0.03),
        _c(-0.27, -0.07, 0.03, INK, 0),
        _c(-0.03, -0.07, 0.03, INK, 0),
        _e(-0.18, 0.1, 0.06, 0.045, "#2a1a1a", 0.03),
        _p("M-0.6,-0.42 Q-0.68,-0.34 -0.64,-0.22 M-0.68,-0.54 Q-0.8,-0.4 -0.76,-0.24", "none", 0.045),
    ])  # fmt: skip


def giant_sunflower() -> str:
    """Giant Sunflower: one huge sunflower head with a ring of yellow petals on a tall stem with
    two leaves."""
    cx, cy, n = -0.06, -0.16, 14
    petals = []
    for i in range(n):
        a = 2 * math.pi * i / n
        ca, sa, w = math.cos(a), math.sin(a), 0.11
        tip = (cx + 0.6 * ca, cy + 0.6 * sa)
        left = (cx + 0.3 * ca - w * sa, cy + 0.3 * sa + w * ca)
        right = (cx + 0.3 * ca + w * sa, cy + 0.3 * sa - w * ca)
        cl = (cx + 0.5 * ca - w * sa, cy + 0.5 * sa + w * ca)
        cr = (cx + 0.5 * ca + w * sa, cy + 0.5 * sa - w * ca)
        petals.append(
            f"M{left[0]:.3f},{left[1]:.3f} Q{cl[0]:.3f},{cl[1]:.3f} {tip[0]:.3f},{tip[1]:.3f} "
            f"Q{cr[0]:.3f},{cr[1]:.3f} {right[0]:.3f},{right[1]:.3f} Z"
        )
    seeds = [
        (cx + r * math.cos(a), cy + r * math.sin(a))
        for r, k in ((0.1, 5), (0.2, 9))
        for a in (2 * math.pi * j / k for j in range(k))
    ]
    return "".join([
        _limb("M-0.08,0.3 Q-0.04,0.56 -0.12,0.84", "#5a9a3c", 0.08),
        _p("M-0.09,0.56 Q-0.42,0.4 -0.6,0.58 Q-0.32,0.72 -0.09,0.56 Z", LEAF),
        _p("M-0.06,0.44 Q0.14,0.3 0.26,0.44 Q0.1,0.56 -0.06,0.44 Z", LEAF),
        *(_p(d, GOLD, 0.035) for d in petals),
        _c(cx, cy, 0.3, "#6b3e1f"),
        *(_c(x, y, 0.025, "#3a2210", 0) for x, y in seeds),
    ])  # fmt: skip


def flying_trowel() -> str:
    """Flying Trowel: a garden trowel with a wooden handle flying up and to the right on two white
    wings, with motion lines."""
    return "".join([
        _p("M-0.34,0.74 L-0.16,0.56 M-0.08,0.8 L0.06,0.66 M-0.62,0.46 L-0.48,0.32", "none", 0.045),
        _p("M-0.18,0.04 Q-0.56,-0.26 -0.66,-0.06 L-0.52,-0.02 L-0.6,0.08 L-0.44,0.08 L-0.46,0.18 Q-0.3,0.14 -0.18,0.04 Z", "#ffffff", 0.04),
        _limb("M-0.24,0.24 L-0.54,0.54", "#a8693a", 0.13),
        _p("M-0.12,0.12 L-0.24,0.24", "none", 0.07),
        _p("M-0.14,0.14 Q-0.16,-0.3 0.52,-0.52 Q0.3,0.16 -0.14,0.14 Z", "#b8c2cc"),
        _p("M-0.06,0.06 L0.36,-0.36", "none", 0.03, "#8a949e"),
        _p("M-0.04,0.2 Q0.22,0.5 0.1,0.64 L0.02,0.5 L-0.06,0.6 L-0.08,0.44 L-0.18,0.48 Q-0.14,0.32 -0.04,0.2 Z", "#ffffff", 0.04),
    ])  # fmt: skip


#: Each motif's picture, by the motif's name in :data:`barry_plotter.MOTIFS`.
PICTURES: dict[str, Callable[[], str]] = {
    "Talking Scarecrow": talking_scarecrow,
    "Moonlit Glasshouse": moonlit_glasshouse,
    "Enchanted Allotment": enchanted_allotment,
    "Hatchlings": hatchlings,
    "Snail Parade": snail_parade,
    "Compost Dragon": compost_dragon,
    "Potting Shed": potting_shed,
    "Wheelbarrow Race": wheelbarrow_race,
    "Scary Raven": scary_raven,
    "Clockwork Mole": clockwork_mole,
    "Frost Fairy": frost_fairy,
    "Midnight Beetles": midnight_beetles,
    "Whispering Bramble": whispering_bramble,
    "Giant Sunflower": giant_sunflower,
    "Flying Trowel": flying_trowel,
}
