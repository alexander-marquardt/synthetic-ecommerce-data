"""Brand house styles for the retail drawings (prototype for #125).

Every brand is one declared row of :data:`HOUSE_STYLES`, never a hash of
its name, so each brand looks designed and two brands cannot collide
(``test_house_styles.py`` refuses a duplicate row, a duplicate mark, a
duplicate lockup and a brand with no row). A row sets:

* the sheet: ``paper`` tint, a faint background ``texture`` and a ``frame``;
* the product's outline: ``ink`` color, stroke ``weight``, ``dashed`` and
  ``joins`` (round or sharp). The product's own fill and pattern are never
  touched: they belong to the product, not the brand;
* the logo: a composite ``mark`` from :data:`MARKS` in the brand ``color``,
  set in a ``layout`` at ``place``. About half the brands use a full lockup
  (mark plus wordmark); the rest show the mark alone in a corner plus a small
  text ``tag``;
* the wordmark treatment: ``font``, ``weight``, ``case``, ``spacing``, ``italic``.

:func:`dress` wraps a product drawing in its brand's house style.
"""

# ruff: noqa: E501 -- SVG literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math
import re
from dataclasses import astuple, dataclass, fields
from html import escape

SIZE = 400
DEFAULT_INK = "#2b3440"
MARK_ONLY_SIZE = 60  # px across: 15% of the sheet's width, the cap
LOCKUP_MARK_SIZE = 56
NAME_SIZE = 21.0
NAME_MIN = 15.0
NAME_MAX_WIDTH = 250.0
EDGE = 16  # gap between the sheet's edge and a logo

FONTS = {
    "sans": "Helvetica, Arial, sans-serif",
    "serif": "Georgia, 'Times New Roman', serif",
    "mono": "'Courier New', Courier, monospace",
    "humanist": "'Trebuchet MS', Verdana, sans-serif",
}
#: Average glyph advance per font size, for laying out text without a font engine.
ADVANCE = {"sans": 0.56, "serif": 0.55, "mono": 0.6, "humanist": 0.54}
TEXTURES = ("none", "dots", "lines", "grid", "diagonal", "hatch")
FRAMES = ("none", "thin", "double", "rounded", "heavy", "ticks")
LAYOUTS = (
    "mark_only",
    "mark_left",
    "mark_right",
    "mark_above",
    "pill",
    "badge",
    "band_top",
    "band_bottom",
)
PLACES = ("top_left", "top_center", "top_right", "bottom_left", "bottom_center", "bottom_right")
CORNERS = ("top_left", "top_right", "bottom_left", "bottom_right")
TAGS = ("none", "outline", "rect", "flag", "plain", "underline", "stamp", "tab")
CASES = ("title", "caps", "smallcaps", "lower")


#: A real brand (:mod:`real_brands`, gen#341) draws no logo: its style row carries this mark,
#: so the name is text in the title and the ``brand`` field and the drawing shows no mark.
NO_MARK = "none"


@dataclass(frozen=True)
class HouseStyle:
    """One brand's look. See the module docstring for what each field does."""

    paper: str
    texture: str
    frame: str
    color: str
    ink: str
    stroke: float  # outline weight, 1.0 = the kit's own
    dashed: bool
    joins: str  # round | sharp
    mark: str
    layout: str
    place: str
    tag: str  # mark_only brands only; "none" for a lockup
    font: str
    weight: int  # 400 | 700
    case: str
    spacing: float  # letter-spacing, px
    italic: bool = False

    def __post_init__(self) -> None:
        checks = (
            ("texture", TEXTURES),
            ("frame", FRAMES),
            ("joins", ("round", "sharp")),
            ("mark", (*MARKS, NO_MARK)),
            ("layout", LAYOUTS),
            ("place", PLACES),
            ("tag", TAGS),
            ("font", tuple(FONTS)),
            ("weight", (400, 700)),
            ("case", CASES),
        )
        for name, allowed in checks:
            if getattr(self, name) not in allowed:
                raise ValueError(f"{name}={getattr(self, name)!r}; one of {allowed}")
        if self.layout == "mark_only":
            if self.place not in CORNERS:
                raise ValueError("a mark-only logo sits in a corner")
            if self.tag == "none":
                raise ValueError("a mark-only brand carries a text tag")
        elif self.tag != "none":
            raise ValueError("a lockup already carries the name; tag must be 'none'")
        if self.layout.startswith("band_") and self.place != (
            "top_center" if self.layout == "band_top" else "bottom_center"
        ):
            raise ValueError("a band sits at the top or bottom center")

    @property
    def top_logo(self) -> bool:
        return self.place.startswith("top")


# --------------------------------------------------------------------------
# Composite marks, drawn in unit space (a box from -1 to 1) and scaled.
# --------------------------------------------------------------------------


def _n(v: float) -> str:
    return f"{v:.3f}".rstrip("0").rstrip(".")


def _star(x: float, y: float, r: float, c: str) -> str:
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append(f"{_n(x + rr * math.cos(a))},{_n(y + rr * math.sin(a))}")
    return f'<polygon points="{" ".join(pts)}" fill="{c}"/>'


def _ring(x: float, y: float, r: float, w: float, c: str) -> str:
    return f'<circle cx="{_n(x)}" cy="{_n(y)}" r="{_n(r)}" fill="none" stroke="{c}" stroke-width="{_n(w)}"/>'


def _dot(x: float, y: float, r: float, c: str, extra: str = "") -> str:
    return f'<circle cx="{_n(x)}" cy="{_n(y)}" r="{_n(r)}" fill="{c}"{extra}/>'


def _stroke(d: str, w: float, c: str, join: str = "round") -> str:
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{_n(w)}" stroke-linecap="round" stroke-linejoin="{join}"/>'


def _diamond(x: float, y: float, h: float) -> str:
    return f"M{_n(x)},{_n(y - h)} L{_n(x + h)},{_n(y)} L{_n(x)},{_n(y + h)} L{_n(x - h)},{_n(y)} Z"


def _hexagon(x: float, y: float, r: float) -> str:
    pts = [(x + r * math.cos(math.pi / 3 * k), y + r * math.sin(math.pi / 3 * k)) for k in range(6)]
    return "M" + " L".join(f"{_n(a)},{_n(b)}" for a, b in pts) + " Z"


def m_squares_circle(c: str) -> list[str]:
    out = []
    for k in range(8):
        a = 360 / 8 * k
        out.append(
            f'<rect x="-.14" y="-.86" width=".28" height=".28" fill="{c}" transform="rotate({a:g})"/>'
        )
    return [*out, _dot(0, 0, 0.18, c)]


def m_three_stars(c: str) -> list[str]:
    return [_star(-0.62, 0.14, 0.4, c), _star(0, -0.16, 0.56, c), _star(0.62, 0.14, 0.4, c)]


def m_circles_line(c: str) -> list[str]:
    return [_dot(x, 0, r, c) for x, r in ((-0.74, 0.14), (-0.36, 0.19), (0.12, 0.25), (0.68, 0.31))]


def m_dot_triangle(c: str) -> list[str]:
    out = []
    for row in range(3):
        for k in range(row + 1):
            out.append(_dot((k - row / 2) * 0.6, -0.58 + row * 0.56, 0.22, c))
    return out


def m_interlocking_rings(c: str) -> list[str]:
    return [_ring(x, y, 0.38, 0.11, c) for x, y in ((-0.5, -0.14), (0, 0.18), (0.5, -0.14))]


def m_chevron_stack(c: str) -> list[str]:
    return [
        _stroke(f"M-.62,{_n(y + 0.3)} L0,{_n(y - 0.24)} L.62,{_n(y + 0.3)}", 0.17, c, "miter")
        for y in (-0.52, -0.02, 0.48)
    ]


def m_sunburst(c: str) -> list[str]:
    lines = " ".join(
        f"M{_n(0.5 * math.cos(a))},{_n(0.5 * math.sin(a))} L{_n(0.94 * math.cos(a))},{_n(0.94 * math.sin(a))}"
        for a in (k * math.pi / 6 for k in range(12))
    )
    return [_dot(0, 0, 0.32, c), _stroke(lines, 0.1, c)]


def m_diamond_grid(c: str) -> list[str]:
    d = " ".join(_diamond(x, y, 0.24) for x in (-0.6, 0, 0.6) for y in (-0.6, 0, 0.6))
    return [f'<path d="{d}" fill="{c}"/>']


def m_crescent_dot(c: str) -> list[str]:
    big, small, off = 0.72, 0.6, 0.34
    x = (big**2 - small**2 + off**2) / (2 * off)
    y = math.sqrt(big**2 - x**2)
    large = 1 if x > off else 0
    d = f"M{_n(x)},{_n(-y)} A{big},{big} 0 1 0 {_n(x)},{_n(y)} A{small},{small} 0 {large} 1 {_n(x)},{_n(-y)} Z"
    return [
        f'<path d="{d}" fill="{c}" transform="translate(-.18 0) rotate(-25)"/>',
        _dot(0.62, -0.46, 0.17, c),
    ]


def m_wave_arcs(c: str) -> list[str]:
    return [
        _stroke(f"M-.86,{_n(y)} Q-.43,{_n(y - 0.34)} 0,{_n(y)} T.86,{_n(y)}", 0.15, c)
        for y in (-0.48, 0.02, 0.52)
    ]


def m_petals(c: str) -> list[str]:
    out = [
        _dot(0.56 * math.cos(a), 0.56 * math.sin(a), 0.32, c)
        for a in (k * math.pi / 3 for k in range(6))
    ]
    return [*out, _dot(0, 0, 0.22, "#ffffff")]


def m_spokes(c: str) -> list[str]:
    ends = [
        (0.78 * math.cos(a), 0.78 * math.sin(a))
        for a in (k * math.pi / 3 + math.pi / 6 for k in range(6))
    ]
    d = " ".join(f"M0,0 L{_n(x)},{_n(y)}" for x, y in ends)
    return [_stroke(d, 0.1, c), *[_dot(x, y, 0.16, c) for x, y in ends]]


def m_lozenge_chain(c: str) -> list[str]:
    return [
        f'<path d="{_diamond(x, 0, 0.46)}" fill="none" stroke="{c}" stroke-width=".11" stroke-linejoin="miter"/>'
        for x in (-0.48, 0, 0.48)
    ]


def m_hex_trio(c: str) -> list[str]:
    d = " ".join(_hexagon(x, y, 0.36) for x, y in ((0, -0.4), (-0.42, 0.33), (0.42, 0.33)))
    return [f'<path d="{d}" fill="{c}"/>']


def m_checker(c: str) -> list[str]:
    cells = "".join(
        f'<rect x="{_n(-0.75 + 0.5 * i)}" y="{_n(-0.75 + 0.5 * j)}" width=".5" height=".5" fill="{c}"/>'
        for i in range(3)
        for j in range(3)
        if (i + j) % 2 == 0
    )
    return [
        cells,
        f'<rect x="-.75" y="-.75" width="1.5" height="1.5" fill="none" stroke="{c}" stroke-width=".08"/>',
    ]


def m_scallops(c: str) -> list[str]:
    d = " ".join(f"M{_n(x - 0.3)},.12 A.3,.3 0 0 1 {_n(x + 0.3)},.12 Z" for x in (-0.6, 0, 0.6))
    return [
        f'<path d="{d}" fill="{c}"/>',
        f'<rect x="-.9" y=".26" width="1.8" height=".16" fill="{c}"/>',
        _dot(0, -0.56, 0.16, c),
    ]


def m_three_drops(c: str) -> list[str]:
    def drop(x: float, y: float, s: float) -> str:
        return (
            f"M{_n(x)},{_n(y - s)} C{_n(x + 0.2 * s)},{_n(y - 0.55 * s)} {_n(x + 0.62 * s)},{_n(y - 0.1 * s)} "
            f"{_n(x + 0.62 * s)},{_n(y + 0.3 * s)} A{_n(0.62 * s)},{_n(0.62 * s)} 0 0 1 {_n(x - 0.62 * s)},{_n(y + 0.3 * s)} "
            f"C{_n(x - 0.62 * s)},{_n(y - 0.1 * s)} {_n(x - 0.2 * s)},{_n(y - 0.55 * s)} {_n(x)},{_n(y - s)} Z"
        )

    return [
        f'<path d="{drop(-0.6, 0.18, 0.48)} {drop(0, -0.08, 0.62)} {drop(0.6, 0.18, 0.48)}" fill="{c}"/>'
    ]


def m_peaks(c: str) -> list[str]:
    return [
        f'<path d="M-.95,.6 L-.45,-.2 L.05,.6 Z M-.05,.6 L.45,-.2 L.95,.6 Z" fill="{c}" fill-opacity=".55"/>',
        f'<path d="M-.5,.6 L0,-.72 L.5,.6 Z" fill="{c}"/>',
    ]


def m_zigzag_dots(c: str) -> list[str]:
    pts = [(-0.84 + 0.42 * k, 0.32 if k % 2 == 0 else -0.32) for k in range(5)]
    d = "M" + " L".join(f"{_n(x)},{_n(y)}" for x, y in pts)
    return [_stroke(d, 0.12, c, "miter"), *[_dot(x, y, 0.15, c) for x, y in pts]]


def m_stacked_bars(c: str) -> list[str]:
    return [
        f'<path d="M-.9,-.55 L.9,-.55 L.9,-.3 L-.9,-.3 Z M-.6,-.12 L.6,-.12 L.6,.13 L-.6,.13 Z '
        f'M-.3,.31 L.3,.31 L.3,.56 L-.3,.56 Z" fill="{c}"/>'
    ]


def m_half_disc(c: str) -> list[str]:
    return [
        f'<path d="M-.8,.25 A.8,.8 0 0 1 .8,.25 Z" fill="{c}"/>',
        _stroke("M-.8,.5 L.8,.5", 0.11, c),
        _stroke("M-.5,.75 L.5,.75", 0.11, c),
    ]


def m_slanted_blades(c: str) -> list[str]:
    return [
        f'<path d="M-.9,.6 L-.35,-.6 L-.05,-.6 L-.6,.6 Z" fill="{c}"/>',
        f'<path d="M-.1,.6 L.45,-.6 L.75,-.6 L.2,.6 Z" fill="{c}" fill-opacity=".7"/>',
    ]


def m_rainbow(c: str) -> list[str]:
    return [
        _stroke(f"M{_n(-r)},.5 A{_n(r)},{_n(r)} 0 0 1 {_n(r)},.5", 0.16, c) for r in (0.9, 0.6, 0.3)
    ]


def m_venn(c: str) -> list[str]:
    return [
        _dot(0.36 * math.cos(a), 0.36 * math.sin(a) + 0.06, 0.48, c, ' fill-opacity=".55"')
        for a in (-math.pi / 2, math.pi / 6, 5 * math.pi / 6)
    ]


def m_quad_squares(c: str) -> list[str]:
    return [
        f'<rect x="-.82" y="-.82" width=".72" height=".72" fill="{c}"/>',
        f'<rect x=".14" y="-.78" width=".64" height=".64" fill="none" stroke="{c}" stroke-width=".1"/>',
        f'<rect x="-.82" y=".1" width=".72" height=".72" fill="{c}"/>',
        f'<rect x=".1" y=".1" width=".72" height=".72" fill="{c}"/>',
    ]


def m_target(c: str) -> list[str]:
    return [_ring(0, 0, 0.84, 0.12, c), _ring(0, 0, 0.54, 0.12, c), _dot(0, 0, 0.24, c)]


def m_plus_four(c: str) -> list[str]:
    d = " ".join(
        f"M{_n(x - 0.38)},{_n(y)} L{_n(x + 0.38)},{_n(y)} M{_n(x)},{_n(y - 0.38)} L{_n(x)},{_n(y + 0.38)}"
        for x in (-0.5, 0.5)
        for y in (-0.5, 0.5)
    )
    return [_stroke(d, 0.2, c, "miter").replace('stroke-linecap="round"', 'stroke-linecap="butt"')]


def m_orbit(c: str) -> list[str]:
    a = -math.pi / 4
    return [
        _ring(0, 0, 0.74, 0.1, c),
        _dot(0, 0, 0.3, c),
        _dot(0.74 * math.cos(a), 0.74 * math.sin(a), 0.18, c),
    ]


def m_nested(c: str) -> list[str]:
    return [
        _ring(0, 0, 0.88, 0.09, c),
        f'<path d="{_diamond(0, 0, 0.62)}" fill="none" stroke="{c}" stroke-width=".09"/>',
        f'<rect x="-.2" y="-.2" width=".4" height=".4" fill="{c}"/>',
    ]


def m_leaf_pair(c: str) -> list[str]:
    leaf = "M0,0 Q.36,-.3 .82,0 Q.36,.3 0,0 Z"
    return [
        _stroke("M0,.8 L0,-.1", 0.1, c),
        f'<path d="{leaf}" fill="{c}" transform="translate(0 .1) rotate(-38)"/>',
        f'<path d="{leaf}" fill="{c}" transform="translate(0 .32) rotate(-142)"/>',
        f'<path d="{leaf}" fill="{c}" transform="translate(0 -.1) rotate(-90) scale(.8)"/>',
    ]


# The marks of the brands the scaled build adds (scale.EXTRA_BRANDS, gen#125).


def m_arch(c: str) -> list[str]:
    return [
        f'<path d="M-.7,.8 L-.7,-.1 A.7,.7 0 0 1 .7,-.1 L.7,.8 Z" fill="{c}"/>',
        '<path d="M-.3,.8 L-.3,.1 A.3,.3 0 0 1 .3,.1 L.3,.8 Z" fill="#ffffff"/>',
    ]


def m_bar_trio(c: str) -> list[str]:
    return [
        f'<rect x="{_n(x)}" y="{_n(0.8 - h)}" width=".38" height="{_n(h)}" fill="{c}"/>'
        for x, h in ((-0.8, 0.8), (-0.19, 1.3), (0.42, 1.6))
    ]


def m_cross_ring(c: str) -> list[str]:
    return [_ring(0, 0, 0.8, 0.12, c), _stroke("M0,-.45 L0,.45 M-.45,0 L.45,0", 0.18, c)]


def m_dot_ring(c: str) -> list[str]:
    return [
        _dot(0.7 * math.cos(k * math.pi / 4), 0.7 * math.sin(k * math.pi / 4), 0.14, c)
        for k in range(8)
    ]


def m_half_moons(c: str) -> list[str]:
    return [
        f'<path d="M-.85,{_n(y)} A.85,.85 0 0 1 .85,{_n(y)} Z" fill="{c}"/>' for y in (-0.05, 0.75)
    ]


def m_keyhole(c: str) -> list[str]:
    return [_ring(0, 0, 0.84, 0.1, c), _dot(0, -0.2, 0.24, c),
            f'<path d="M-.14,-.1 L.14,-.1 L.24,.5 L-.24,.5 Z" fill="{c}"/>']  # fmt: skip


def m_ladder(c: str) -> list[str]:
    rungs = " ".join(f"M-.4,{_n(y)} L.4,{_n(y)}" for y in (-0.5, -0.1, 0.3, 0.7))
    return [_stroke(f"M-.4,-.85 L-.4,.85 M.4,-.85 L.4,.85 {rungs}", 0.12, c, "miter")]


def m_triangle_pair(c: str) -> list[str]:
    return [
        f'<path d="M-.9,.6 L-.3,-.6 L.3,.6 Z" fill="{c}"/>',
        f'<path d="M-.1,.6 L.5,-.6 L1,.6 Z" fill="none" stroke="{c}" stroke-width=".1"/>',
    ]


def m_square_dot(c: str) -> list[str]:
    return [
        f'<rect x="-.78" y="-.78" width="1.56" height="1.56" fill="none" stroke="{c}" stroke-width=".14"/>',
        _dot(0, 0, 0.32, c),
    ]


def m_wheat_ear(c: str) -> list[str]:
    grain = "M0,0 Q.2,-.14 .36,0 Q.2,.14 0,0 Z"
    out = [_stroke("M0,.9 L0,-.8", 0.08, c)]
    for y in (-0.55, -0.2, 0.15):
        out += [f'<path d="{grain}" fill="{c}" transform="translate(0 {_n(y)}) rotate(-50)"/>',
                f'<path d="{grain}" fill="{c}" transform="translate(0 {_n(y)}) rotate(-130)"/>']  # fmt: skip
    return out


def m_bell(c: str) -> list[str]:
    return [
        f'<path d="M-.6,.5 Q-.6,-.7 0,-.7 Q.6,-.7 .6,.5 L.75,.62 L-.75,.62 Z" fill="{c}"/>',
        _dot(0, 0.8, 0.14, c),
    ]


def m_diamond_dot(c: str) -> list[str]:
    return [
        f'<path d="{_diamond(0, 0, 0.88)}" fill="none" stroke="{c}" stroke-width=".12"/>',
        _dot(0, 0, 0.22, c),
    ]


def m_pinwheel(c: str) -> list[str]:
    blade = "M0,0 L.8,0 L0,-.6 Z"
    return [f'<path d="{blade}" fill="{c}" transform="rotate({a})"/>' for a in (0, 90, 180, 270)]


def m_ring_pair(c: str) -> list[str]:
    return [_ring(-0.34, 0, 0.5, 0.14, c), _dot(0.48, 0, 0.36, c)]


def m_striped_disc(c: str) -> list[str]:
    stripes = " ".join(f"M-.8,{_n(y)} L.8,{_n(y)}" for y in (-0.48, -0.16, 0.16, 0.48))
    return [_ring(0, 0, 0.82, 0.08, c), _stroke(stripes, 0.14, c).replace("round", "butt", 1)]


def m_arrow_up(c: str) -> list[str]:
    return [
        f'<path d="M0,-.9 L.7,-.1 L.26,-.1 L.26,.85 L-.26,.85 L-.26,-.1 L-.7,-.1 Z" fill="{c}"/>'
    ]


def m_hourglass(c: str) -> list[str]:
    return [
        f'<path d="M-.6,-.85 L.6,-.85 L0,0 Z" fill="{c}"/>',
        f'<path d="M-.6,.85 L.6,.85 L0,0 Z" fill="none" stroke="{c}" stroke-width=".1"/>',
    ]


def m_fan(c: str) -> list[str]:
    ribs = " ".join(
        f"M0,.6 L{_n(0.9 * math.cos(a))},{_n(0.6 - 0.9 * math.sin(a))}"
        for a in (math.pi * k / 6 for k in range(1, 6))
    )
    return [_stroke(ribs, 0.1, c), _dot(0, 0.6, 0.14, c)]


def m_steps(c: str) -> list[str]:
    return [
        f'<path d="M-.85,.85 L-.85,.3 L-.3,.3 L-.3,-.25 L.25,-.25 L.25,-.8 L.85,-.8 L.85,.85 Z" fill="{c}"/>'
    ]


def m_crown(c: str) -> list[str]:
    return [f'<path d="M-.8,.6 L-.8,-.5 L-.4,0 L0,-.7 L.4,0 L.8,-.5 L.8,.6 Z" fill="{c}"/>']


def m_grapes(c: str) -> list[str]:
    dots = [(-0.4, -0.3), (0.0, -0.3), (0.4, -0.3), (-0.2, 0.1), (0.2, 0.1), (0.0, 0.5)]
    return [f'<circle cx="{x}" cy="{y}" r=".24" fill="{c}"/>' for x, y in dots]


def m_cask(c: str) -> list[str]:
    return [
        f'<path d="M-.55,-.8 Q-.9,0 -.55,.8 L.55,.8 Q.9,0 .55,-.8 Z" fill="{c}"/>',
        _stroke("M-.8,-.3 L.8,-.3 M-.8,.3 L.8,.3", 0.1, "#ffffff"),
    ]


def m_orchard_leaf(c: str) -> list[str]:
    return [
        f'<path d="M-.7,.7 Q-.8,-.6 .7,-.7 Q.8,.6 -.7,.7 Z" fill="{c}"/>',
        _stroke("M-.55,.55 L.45,-.45", 0.1, "#ffffff"),
    ]


# The marks of the brands the breadth and scale-only templates add (breadth_rows,
# scale_rows), one per brand.


def m_bean(c: str) -> list[str]:
    return [
        f'<ellipse cx="0" cy="0" rx=".55" ry=".85" fill="{c}" transform="rotate(25)"/>',
        _stroke("M-.1,-.75 Q.25,0 -.1,.75", 0.12, "#ffffff"),
    ]


def m_rivet_pair(c: str) -> list[str]:
    return [_ring(x, 0, 0.36, 0.12, c) for x in (-0.45, 0.45)] + [
        _dot(x, 0, 0.12, c) for x in (-0.45, 0.45)
    ]


def m_sprout(c: str) -> list[str]:
    return [
        _stroke("M0,.85 L0,-.1", 0.12, c),
        f'<path d="M0,-.1 Q-.75,-.2 -.7,-.8 Q-.1,-.75 0,-.1 Z" fill="{c}"/>',
        f'<path d="M0,.15 Q.75,.05 .7,-.55 Q.1,-.5 0,.15 Z" fill="{c}"/>',
    ]


def m_fold(c: str) -> list[str]:
    return [
        f'<path d="M-.8,-.8 L.8,-.8 L.8,.2 L-.2,.8 L-.8,.8 Z" fill="{c}"/>',
        '<path d="M.8,.2 L-.2,.2 L-.2,.8 Z" fill="#ffffff"/>',
    ]


def m_comb(c: str) -> list[str]:
    teeth = " ".join(f"M{_n(x)},-.1 L{_n(x)},.75" for x in (-0.6, -0.3, 0, 0.3, 0.6))
    return [
        f'<rect x="-.8" y="-.6" width="1.6" height=".5" rx=".12" fill="{c}"/>',
        _stroke(teeth, 0.11, c),
    ]


def m_teapot(c: str) -> list[str]:
    return [
        f'<path d="M-.55,.6 Q-.7,-.35 0,-.35 Q.7,-.35 .55,.6 Z" fill="{c}"/>',
        _stroke("M.5,0 L.9,-.4", 0.12, c),
        _ring(-0.65, 0.1, 0.22, 0.1, c),
        _dot(0, -0.5, 0.12, c),
    ]


def m_droplet_leaf(c: str) -> list[str]:
    return [
        f'<path d="M0,-.85 Q.65,0 .45,.45 Q0,.95 -.45,.45 Q-.65,0 0,-.85 Z" fill="{c}"/>',
        _stroke("M0,.6 L0,-.3 M0,.15 L.2,-.05 M0,.35 L-.2,.15", 0.08, "#ffffff"),
    ]


def m_puddle(c: str) -> list[str]:
    return [
        f'<ellipse cx="0" cy=".45" rx=".85" ry=".28" fill="{c}"/>',
        _ring(0, 0.45, 0.45, 0.08, "#ffffff"),
        _dot(0, -0.45, 0.2, c),
    ]


def m_bubbles(c: str) -> list[str]:
    return [
        _ring(-0.3, 0.25, 0.45, 0.1, c),
        _ring(0.4, -0.25, 0.32, 0.1, c),
        _dot(0.35, 0.55, 0.14, c),
    ]


def m_bull_horns(c: str) -> list[str]:
    """A bull's head: a round muzzle between two upswept horns (Blue Bull, gen#326)."""
    horns = "M-0.35,-0.1 C-0.95,-0.1 -0.95,-0.7 -0.6,-0.85 M0.35,-0.1 C0.95,-0.1 0.95,-0.7 0.6,-0.85"
    return [
        f'<path d="{horns}" fill="none" stroke="{c}" stroke-width=".16" stroke-linecap="round"/>',
        _dot(0, 0.15, 0.5, c),
        _dot(-0.2, 0.3, 0.08, "#ffffff"),
        _dot(0.2, 0.3, 0.08, "#ffffff"),
    ]


# The beauty depth marks (gen#214): one per invented beauty brand, so no two brands share one.


def m_lash_fan(c: str) -> list[str]:
    lashes = " ".join(
        f"M{_n(0.5 * math.sin(math.radians(a)))},.7 "
        f"L{_n(0.95 * math.sin(math.radians(a)))},{_n(0.7 - 1.5 * math.cos(math.radians(a)))}"
        for a in (-50, -25, 0, 25, 50)
    )
    return [
        _stroke(lashes, 0.1, c),
        f'<rect x="-.4" y=".65" width=".8" height=".2" rx=".08" fill="{c}"/>',
    ]


def m_dropper(c: str) -> list[str]:
    return [
        f'<path d="M-.22,-.3 L.22,-.3 L.22,.1 Q.22,.2 0,.2 Q-.22,.2 -.22,.1 Z" fill="{c}"/>',
        f'<ellipse cx="0" cy="-.62" rx=".26" ry=".3" fill="{c}"/>',
        f'<path d="M0,.35 Q.28,.7 0,.9 Q-.28,.7 0,.35 Z" fill="{c}"/>',
    ]


def m_compact(c: str) -> list[str]:
    return [
        _ring(0, 0, 0.8, 0.14, c),
        f'<path d="M-.8,.05 L.8,.05" stroke="{c}" stroke-width=".1"/>',
        _dot(0, -0.35, 0.18, c),
        _dot(0, 0.45, 0.18, c),
    ]


def m_jar(c: str) -> list[str]:
    return [
        f'<rect x="-.55" y="-.75" width="1.1" height=".3" rx=".08" fill="{c}"/>',
        f'<rect x="-.7" y="-.35" width="1.4" height="1.1" rx=".25" fill="{c}"/>',
        _stroke("M-.35,.0 L-.35,.5", 0.1, "#ffffff"),
    ]


def m_tube(c: str) -> list[str]:
    return [
        f'<path d="M-.3,-.3 L.3,-.3 L.4,.8 L-.4,.8 Z" fill="{c}"/>',
        f'<rect x="-.18" y="-.8" width=".36" height=".45" rx=".06" fill="{c}"/>',
        _stroke("M-.4,.75 L.4,.75", 0.12, "#ffffff"),
    ]


def m_mist_cloud(c: str) -> list[str]:
    return [
        f'<path d="M-.7,.2 Q-.7,-.2 -.3,-.2 Q-.2,-.65 .25,-.5 Q.7,-.5 .65,.2 Z" fill="{c}"/>',
        _dot(-0.45, 0.55, 0.08, c),
        _dot(0, 0.6, 0.08, c),
        _dot(0.45, 0.55, 0.08, c),
        _dot(-0.2, 0.85, 0.06, c),
        _dot(0.25, 0.85, 0.06, c),
    ]


def m_sparkle(c: str) -> list[str]:
    four = "M0,-.9 Q.1,-.1 .9,0 Q.1,.1 0,.9 Q-.1,.1 -.9,0 Q-.1,-.1 0,-.9 Z"
    return [f'<path d="{four}" fill="{c}"/>', _dot(0.6, -0.6, 0.12, c), _dot(-0.6, 0.6, 0.09, c)]


def m_feather(c: str) -> list[str]:
    veins = " ".join(
        f"M{_n(x)},{_n(y)} L{_n(x + 0.3)},{_n(y - 0.1)}"
        for x, y in ((-0.3, 0.45), (-0.1, 0.15), (0.1, -0.15))
    )
    return [
        f'<path d="M-.5,.8 Q-.9,-.4 .6,-.8 Q.9,.3 -.5,.8 Z" fill="{c}"/>',
        _stroke("M-.6,.9 L.5,-.7", 0.08, "#ffffff"),
        _stroke(veins, 0.06, "#ffffff"),
    ]


def m_shell(c: str) -> list[str]:
    ribs = " ".join(f"M0,.7 L{_n(x)},-.5" for x in (-0.5, -0.17, 0.17, 0.5))
    return [
        f'<path d="M-.85,.2 Q-.85,-.85 0,-.85 Q.85,-.85 .85,.2 Z" fill="{c}"/>',
        _stroke(ribs, 0.07, "#ffffff"),
        f'<rect x="-.3" y=".3" width=".6" height=".3" rx=".1" fill="{c}"/>',
    ]


def m_lip_swipe(c: str) -> list[str]:
    return [
        f'<path d="M-.35,.8 L-.35,.0 L.35,.0 L.35,.8 Z" fill="{c}"/>',
        f'<path d="M-.3,-.05 L-.3,-.5 L.3,-.9 L.3,-.05 Z" fill="{c}"/>',
        _stroke("M-.35,.4 L.35,.4", 0.1, "#ffffff"),
    ]


def m_flask(c: str) -> list[str]:
    return [
        f'<path d="M-.2,-.85 L.2,-.85 L.2,-.3 L.75,.7 Q.8,.85 .6,.85 L-.6,.85 Q-.8,.85 -.75,.7 L-.2,-.3 Z" fill="{c}"/>',
        _stroke("M-.4,.5 L.4,.5", 0.1, "#ffffff"),
    ]


def m_moon_stars(c: str) -> list[str]:
    return [
        f'<path d="M.3,-.8 A.85,.85 0 1 0 .3,.8 A.65,.65 0 1 1 .3,-.8 Z" fill="{c}"/>',
        _star(0.5, -0.1, 0.28, c),
    ]


def m_pearl_row(c: str) -> list[str]:
    return [
        _dot(x, y, r, c)
        for x, y, r in ((-0.6, 0.2, 0.28), (0, -0.1, 0.34), (0.6, 0.2, 0.28), (0, 0.6, 0.2))
    ]


def m_rose_bud(c: str) -> list[str]:
    return [
        f'<path d="M0,-.8 Q.7,-.6 .55,.05 Q.35,.45 0,.45 Q-.35,.45 -.55,.05 Q-.7,-.6 0,-.8 Z" fill="{c}"/>',
        _stroke("M0,-.5 Q.25,-.3 0,-.05 Q-.2,-.3 0,-.5", 0.07, "#ffffff"),
        _stroke("M0,.45 L0,.9", 0.1, c),
    ]


#: Mark name -> drawing in unit space (-1..1), painted in the brand color.
MARKS = {
    name[2:]: fn for name, fn in list(globals().items()) if name.startswith("m_") and callable(fn)
}


def mark_svg(name: str, cx: float, cy: float, size: float, color: str) -> str:
    """The composite mark ``name``, ``size`` px across, centered on (cx, cy)."""
    body = "".join(MARKS[name](color))
    return (
        f'<g class="mark" transform="translate({_n(cx)} {_n(cy)}) scale({_n(size / 2)})">{body}</g>'
    )


# --------------------------------------------------------------------------
# Wordmarks
# --------------------------------------------------------------------------


def _cased(style: HouseStyle, text: str) -> str:
    return {"caps": text.upper(), "lower": text.lower()}.get(style.case, text)


def text_width(style: HouseStyle, text: str, size: float) -> float:
    """An estimate of ``text``'s width in ``style``'s wordmark treatment."""
    f = ADVANCE[style.font] * {"caps": 1.22, "smallcaps": 1.1}.get(style.case, 1.0)
    f *= 1.07 if style.weight == 700 else 1.0
    return len(text) * (size * f + style.spacing)


def name_size(style: HouseStyle, text: str, max_width: float = NAME_MAX_WIDTH) -> float:
    """The largest wordmark size up to :data:`NAME_SIZE` that fits ``max_width``."""
    size = NAME_SIZE
    while size > NAME_MIN and text_width(style, text, size) > max_width:
        size -= 0.5
    return size


def wordmark(
    style: HouseStyle,
    text: str,
    x: float,
    y: float,
    size: float,
    color: str,
    anchor: str = "start",
) -> str:
    """``text`` set in ``style``'s treatment; (x, y) is the baseline anchor."""
    attrs = [
        f'x="{x:.1f}" y="{y:.1f}"',
        f'font-family="{FONTS[style.font]}"',
        f'font-size="{size:g}"',
        f'font-weight="{style.weight}"',
        f'fill="{color}"',
        f'text-anchor="{anchor}"',
    ]
    if style.spacing:
        attrs.append(f'letter-spacing="{style.spacing:g}"')
    if style.case == "smallcaps":
        attrs.append('font-variant="small-caps"')
    if style.italic:
        attrs.append('font-style="italic"')
    return f"<text {' '.join(attrs)}>{escape(_cased(style, text))}</text>"


# --------------------------------------------------------------------------
# Sheet: paper, texture, frame
# --------------------------------------------------------------------------


def _texture(style: HouseStyle, uid: str) -> tuple[str, str]:
    """(pattern def, the rect that paints it) for the paper's texture."""
    c, t = style.color, style.texture
    if t == "none":
        return "", ""
    tile, body = {
        "dots": (14, f'<circle cx="7" cy="7" r="1.1" fill="{c}" fill-opacity=".22"/>'),
        "lines": (
            10,
            f'<path d="M0,9.5 L10,9.5" stroke="{c}" stroke-opacity=".12" stroke-width="1"/>',
        ),
        "grid": (
            16,
            f'<path d="M0,15.5 L16,15.5 M15.5,0 L15.5,16" stroke="{c}" stroke-opacity=".1" stroke-width="1"/>',
        ),
        "diagonal": (
            10,
            f'<path d="M-2,2 L2,-2 M0,10 L10,0 M8,12 L12,8" stroke="{c}" stroke-opacity=".1" stroke-width="1"/>',
        ),
        "hatch": (
            12,
            f'<path d="M0,12 L12,0 M0,0 L12,12" stroke="{c}" stroke-opacity=".08" stroke-width="1"/>',
        ),
    }[t]
    pid = f"tex-{uid}"
    return (
        f'<pattern id="{pid}" width="{tile}" height="{tile}" patternUnits="userSpaceOnUse">{body}</pattern>',
        f'<rect width="{SIZE}" height="{SIZE}" fill="url(#{pid})"/>',
    )


def _frame(style: HouseStyle) -> list[str]:
    c = style.color
    f = style.frame
    if f == "thin":
        return [
            f'<rect x="6" y="6" width="388" height="388" fill="none" stroke="{c}" stroke-width="1"/>'
        ]
    if f == "double":
        return [
            f'<rect x="6" y="6" width="388" height="388" fill="none" stroke="{c}" stroke-width="1.6"/>',
            f'<rect x="11" y="11" width="378" height="378" fill="none" stroke="{c}" stroke-width=".8"/>',
        ]
    if f == "rounded":
        return [
            f'<rect x="8" y="8" width="384" height="384" rx="22" fill="none" stroke="{c}" stroke-width="2"/>'
        ]
    if f == "heavy":
        return [
            f'<rect x="7" y="7" width="386" height="386" fill="none" stroke="{c}" stroke-width="4"/>'
        ]
    if f == "ticks":
        t, a, b = 24, 10, SIZE - 10
        d = (
            f"M{a},{a + t} L{a},{a} L{a + t},{a} M{b - t},{a} L{b},{a} L{b},{a + t} "
            f"M{b},{b - t} L{b},{b} L{b - t},{b} M{a + t},{b} L{a},{b} L{a},{b - t}"
        )
        return [
            f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="square"/>'
        ]
    return []


# --------------------------------------------------------------------------
# Logos: a lockup (mark + wordmark) or a corner mark plus a small tag
# --------------------------------------------------------------------------


def _x_for(place: str, width: float) -> float:
    """The left x of a ``width``-wide block at ``place``."""
    if place.endswith("left"):
        return EDGE + 4
    if place.endswith("right"):
        return SIZE - EDGE - 4 - width
    return (SIZE - width) / 2


#: Layout -> the lockup's height in px (the mark plus, for mark_above, a line of type).
LOCKUP_HEIGHT = {
    "band_top": 64,
    "band_bottom": 64,
    "mark_left": LOCKUP_MARK_SIZE,
    "mark_right": LOCKUP_MARK_SIZE,
    "mark_above": LOCKUP_MARK_SIZE + 4 + NAME_SIZE,
    "pill": 50,
    "badge": 58,
}


def _lockup(style: HouseStyle, brand: str) -> list[str]:
    c, m, lay = style.color, LOCKUP_MARK_SIZE, style.layout
    top = style.top_logo
    h = LOCKUP_HEIGHT[lay]
    if lay in ("band_top", "band_bottom"):
        y0 = 0 if lay == "band_top" else SIZE - h
        size = name_size(style, brand, 270)
        w = m + 12 + text_width(style, brand, size)
        x0 = (SIZE - w) / 2
        return [
            f'<rect x="0" y="{y0}" width="{SIZE}" height="{h}" fill="{c}"/>',
            mark_svg(style.mark, x0 + m / 2, y0 + h / 2, m - 6, "#ffffff"),
            wordmark(style, brand, x0 + m + 12, y0 + h / 2 + size * 0.36, size, "#ffffff"),
        ]
    if lay in ("mark_left", "mark_right"):
        size = name_size(style, brand)
        tw = text_width(style, brand, size)
        w = m + 10 + tw
        x0 = _x_for(style.place, w)
        cy = EDGE + m / 2 if top else SIZE - EDGE - m / 2
        mx, tx = (x0 + m / 2, x0 + m + 10) if lay == "mark_left" else (x0 + tw + 10 + m / 2, x0)
        return [
            mark_svg(style.mark, mx, cy, m, c),
            wordmark(style, brand, tx, cy + size * 0.36, size, style.ink),
        ]
    if lay == "mark_above":
        size = name_size(style, brand)
        tw = text_width(style, brand, size)
        w = max(m, tw)
        cx = _x_for(style.place, w) + w / 2
        y0 = EDGE if top else SIZE - EDGE - h
        return [
            mark_svg(style.mark, cx, y0 + m / 2, m, c),
            wordmark(style, brand, cx, y0 + m + 4 + size * 0.8, size, style.ink, "middle"),
        ]
    # pill (filled, white type) or badge (outlined, brand-color type)
    size = name_size(style, brand, 230)
    tw = text_width(style, brand, size)
    mk = h - 14
    w = 12 + mk + 10 + tw + 16
    x0 = _x_for(style.place, w)
    y0 = EDGE if top else SIZE - EDGE - h
    filled = lay == "pill"
    box = (
        f'<rect x="{x0:.1f}" y="{y0}" width="{w:.1f}" height="{h}" rx="{h / 2:g}" fill="{c}"/>'
        if filled
        else f'<rect x="{x0:.1f}" y="{y0}" width="{w:.1f}" height="{h}" rx="6" fill="#ffffff" stroke="{c}" stroke-width="2"/>'
    )
    ink = "#ffffff" if filled else c
    return [
        box,
        mark_svg(style.mark, x0 + 12 + mk / 2, y0 + h / 2, mk, ink),
        wordmark(style, brand, x0 + 12 + mk + 10, y0 + h / 2 + size * 0.36, size, ink),
    ]


TAG_SIZE = 16.0


def _tag(style: HouseStyle, brand: str, place: str) -> list[str]:
    """The small text tag a mark-only brand carries at ``place``."""
    c, t, s = style.color, style.tag, TAG_SIZE
    tw = text_width(style, brand, s)
    pad = 9
    w, h = tw + 2 * pad, 28
    top = place.startswith("top")
    x0 = _x_for(place, w)
    y0 = EDGE if top else SIZE - EDGE - h
    base = y0 + h / 2 + s * 0.36
    if t == "tab":  # a woven label hanging from the top edge
        return [
            f'<rect x="{x0:.1f}" y="0" width="{w:.1f}" height="{h + 12}" fill="{c}"/>',
            wordmark(style, brand, x0 + pad, h / 2 + 12 + s * 0.36, s, "#ffffff"),
        ]
    if t == "rect":
        return [
            f'<rect x="{x0:.1f}" y="{y0}" width="{w:.1f}" height="{h}" fill="{c}"/>',
            wordmark(style, brand, x0 + pad, base, s, "#ffffff"),
        ]
    if t == "flag":
        n = 8
        d = f"M{x0:.1f},{y0} L{x0 + w + n:.1f},{y0} L{x0 + w:.1f},{y0 + h / 2:g} L{x0 + w + n:.1f},{y0 + h} L{x0:.1f},{y0 + h} Z"
        return [f'<path d="{d}" fill="{c}"/>', wordmark(style, brand, x0 + pad, base, s, "#ffffff")]
    if t == "outline":
        return [
            f'<rect x="{x0:.1f}" y="{y0}" width="{w:.1f}" height="{h}" rx="{h / 2:g}" fill="#ffffff" stroke="{c}" stroke-width="1.4"/>',
            wordmark(style, brand, x0 + pad, base, s, c),
        ]
    if t == "stamp":
        return [
            f'<g transform="rotate(-4 {x0 + w / 2:.1f} {y0 + h / 2:g})">'
            f'<rect x="{x0:.1f}" y="{y0}" width="{w:.1f}" height="{h}" fill="none" stroke="{c}" stroke-width="1.6"/>'
            f'<rect x="{x0 + 3:.1f}" y="{y0 + 3}" width="{w - 6:.1f}" height="{h - 6}" fill="none" stroke="{c}" stroke-width=".7"/>'
            f"{wordmark(style, brand, x0 + pad, base, s, c)}</g>"
        ]
    if t == "underline":
        return [
            wordmark(style, brand, x0 + pad, base - 2, s, c),
            f'<rect x="{x0 + pad:.1f}" y="{base + 3:.1f}" width="{tw:.1f}" height="1.6" fill="{c}"/>',
        ]
    return [wordmark(style, brand, x0 + pad, base, s + 1, c)]  # plain


def _opposite(corner: str) -> str:
    """The tag's place for a mark-only brand: the diagonally opposite corner."""
    v, h = corner.split("_")
    return f"{'bottom' if v == 'top' else 'top'}_{'right' if h == 'left' else 'left'}"


def tag_place(style: HouseStyle) -> str:
    """Where a mark-only brand's tag sits: the same side, other corner, unless
    that is the top (the product's top is clearer than its sides)."""
    v, h = style.place.split("_")
    if style.tag == "tab":
        return f"top_{'right' if h == 'left' else 'left'}"
    if v == "top":
        return _opposite(style.place)
    return f"bottom_{'right' if h == 'left' else 'left'}"


def logo(style: HouseStyle, brand: str) -> list[str]:
    if style.mark == NO_MARK:  # a real brand: text only, never a logo, wordmark or trade dress
        return []
    if style.layout != "mark_only":
        return _lockup(style, brand)
    v, h = style.place.split("_")
    r = MARK_ONLY_SIZE / 2
    cx = EDGE + r if h == "left" else SIZE - EDGE - r
    cy = EDGE + r if v == "top" else SIZE - EDGE - r
    return [
        mark_svg(style.mark, cx, cy, MARK_ONLY_SIZE, style.color),
        *_tag(style, brand, tag_place(style)),
    ]


# --------------------------------------------------------------------------
# The product's outline in the brand's hand
# --------------------------------------------------------------------------

_WIDTH = re.compile(r'stroke-width="([0-9]*\.?[0-9]+)"')


def restyle(fragment: str, style: HouseStyle) -> str:
    """The product drawing's ink strokes in ``style``'s color, weight, dash and joins.

    Only strokes in the kit's ink color change; fills, patterns and white
    gloss strokes are the product's and stay as drawn.
    """

    def one(el: str) -> str:
        if f'stroke="{DEFAULT_INK}"' not in el:
            return el
        m = _WIDTH.search(el)
        width = float(m.group(1)) if m else 1.0
        el = el.replace(f'stroke="{DEFAULT_INK}"', f'stroke="{style.ink}"')
        if m:
            el = el[: m.start()] + f'stroke-width="{width * style.stroke:.2f}"' + el[m.end() :]
        if style.joins == "sharp":
            el = el.replace('stroke-linejoin="round"', 'stroke-linejoin="miter"').replace(
                'stroke-linecap="round"', 'stroke-linecap="butt"'
            )
            if "stroke-linejoin" not in el:
                el = el.replace("/>", ' stroke-linejoin="miter"/>', 1)
        if style.dashed and width >= 2.5 and "stroke-dasharray" not in el:
            el = el.replace("/>", ' stroke-dasharray="9 4"/>', 1)
        return el

    return re.sub(
        r"<(?:path|rect|circle|ellipse|polygon|polyline|line)\b[^>]*/>",
        lambda m: one(m.group(0)),
        fragment,
    )


def product_transform(style: HouseStyle) -> str:
    """Shrink the product a little and move it clear of a lockup.

    Products span about y 28..362 of the sheet; at scale 0.78 that is 66..326
    before the shift, so the shift is what the lockup's reach (edge gap plus
    height plus 6 px of air) needs beyond that.
    """
    if style.layout == "mark_only":
        s, dy = 0.86, 0.0
    else:
        s = 0.78
        reach = (0 if style.layout.startswith("band_") else EDGE) + LOCKUP_HEIGHT[style.layout] + 6
        dy = max(10.0, reach - 66.0) if style.top_logo else min(-10.0, (SIZE - 326.0) - reach)
    t = SIZE / 2 * (1 - s)
    return f"translate({t:g} {t + dy:g}) scale({s:g})"


def dress(style: HouseStyle, brand: str, uid: str) -> tuple[list[str], list[str], list[str]]:
    """(defs, sheet, overlay): what sits under and over the restyled product."""
    tex_def, tex_rect = _texture(style, uid)
    sheet = [f'<rect width="{SIZE}" height="{SIZE}" fill="{style.paper}"/>', tex_rect]
    return [tex_def], [p for p in sheet if p], [*_frame(style), *logo(style, brand)]


def H(
    paper,
    texture,
    frame,
    color,
    ink,
    stroke,
    dashed,
    joins,
    mark,
    layout,
    place,
    tag,
    font,
    weight,
    case,
    spacing,
    italic=False,
):  # noqa: N802 -- a table row reads best positionally
    return HouseStyle(
        paper,
        texture,
        frame,
        color,
        ink,
        stroke,
        dashed,
        joins,
        mark,
        layout,
        place,
        tag,
        font,
        weight,
        case,
        spacing,
        italic,
    )


# fmt: off
#: Brand -> its house style. One row per brand, every value chosen by hand.
#   paper      texture     frame      color     ink        stroke dashed joins    mark                 layout         place            tag         font        weight case         spacing italic
HOUSE_STYLES: dict[str, HouseStyle] = {
    # Lockups: mark + wordmark.
    "Harbour & Pine":       H("#f1f5f9", "none",     "double",  "#1f4e79", "#1f3550", 1.0,  False, "round", "chevron_stack",     "mark_left",   "top_left",      "none",     "sans",     700, "caps",      1.5),
    "Larkmoor":             H("#fbf0f1", "none",     "rounded", "#b0476a", "#4a2537", 0.75, False, "round", "interlocking_rings", "mark_above", "top_center",    "none",     "serif",    400, "title",     3.0, True),
    "Ottery Denim":         H("#edf0f3", "grid",     "none",    "#c26b2a", "#1d2a3a", 1.35, False, "sharp", "diamond_grid",      "band_top",    "top_center",    "none",     "mono",     700, "caps",      2.0),
    "Little Fernby":        H("#fff6dc", "dots",     "ticks",   "#e0683f", "#2f4a6b", 1.1,  True,  "round", "petals",            "pill",        "bottom_center", "none",     "humanist", 700, "lower",     0.0),
    "Stridewell":           H("#ffffff", "none",     "none",    "#e23b2e", "#111111", 1.35, False, "sharp", "circles_line",      "mark_right",  "top_left",      "none",     "sans",     700, "caps",      0.0, True),
    "Saltmarsh":            H("#eef6f6", "lines",    "none",    "#1c7c7d", "#1d3b40", 1.0,  False, "round", "wave_arcs",         "band_bottom", "bottom_center", "none",     "humanist", 400, "lower",     1.0),
    "Calderby & Lune":      H("#f3f3f1", "none",     "heavy",   "#2b2b2b", "#1b1b1b", 0.9,  False, "sharp", "lozenge_chain",     "badge",       "top_center",    "none",     "serif",    400, "caps",      2.5),
    "Hollinwray Knits":     H("#f7f1ea", "hatch",    "rounded", "#a0522d", "#4b3426", 1.1,  True,  "round", "checker",           "mark_left",   "bottom_left",   "none",     "serif",    700, "lower",     0.0),
    "Goldfield Farms":      H("#fff8e6", "none",     "ticks",   "#c8870f", "#3d3115", 1.1,  False, "round", "sunburst",          "mark_above",  "top_right",     "none",     "sans",     700, "caps",      1.0),
    "Crunchworth":          H("#fff1ea", "dots",     "none",    "#e0542d", "#2a2a2a", 1.35, False, "sharp", "zigzag_dots",       "pill",        "top_left",      "none",     "sans",     700, "caps",      0.5),
    "Lanternby":            H("#f9f5ec", "none",     "thin",    "#b8801f", "#3b3122", 1.0,  False, "round", "three_stars",       "mark_right",  "bottom_center", "none",     "serif",    400, "smallcaps", 1.0),
    "Quillon Sleep":        H("#f1f3fa", "none",     "rounded", "#5b6bb5", "#2c3354", 0.75, False, "round", "crescent_dot",      "mark_left",   "top_right",     "none",     "humanist", 400, "title",     0.5),
    "Velling Apothecary":   H("#f4f1f6", "none",     "double",  "#5e4b6e", "#2f2638", 0.8,  False, "round", "plus_four",         "mark_above",  "bottom_center", "none",     "serif",    400, "caps",      4.0),
    "Kestlewood Cosmetics": H("#fdf0f3", "none",     "none",    "#c2185b", "#1a1a1a", 1.0,  False, "sharp", "orbit",             "badge",       "bottom_center", "none",     "sans",     400, "lower",     2.0),
    # Mark alone in a corner, plus a small text tag.
    "Wrenfield":            H("#f6f1e6", "lines",    "thin",    "#6b1f2a", "#3a2a22", 1.0,  False, "sharp", "nested",            "mark_only",   "top_left",      "plain",    "serif",    400, "title",     0.0, True),
    "Thistle & Wren":       H("#f3f6f0", "diagonal", "thin",    "#2f5d3a", "#233324", 1.0,  False, "round", "leaf_pair",         "mark_only",   "top_right",     "tab",      "serif",    700, "caps",      1.0),
    "Bramblewood":          H("#f8f1f7", "none",     "thin",    "#7a3e75", "#3d2a4f", 0.75, False, "round", "spokes",            "mark_only",   "bottom_right",  "plain",    "serif",    400, "lower",     1.0, True),
    "Ferrowick Denim":      H("#f6efe6", "none",     "thin",    "#8a5a2b", "#2e2219", 1.2,  False, "sharp", "hex_trio",          "mark_only",   "top_left",      "rect",     "mono",     700, "caps",      1.0),
    "Meadowgate Dairy":     H("#f2f8f1", "none",     "rounded", "#3f8f4a", "#24402a", 1.0,  False, "round", "scallops",          "mark_only",   "top_left",      "outline",  "humanist", 400, "title",     0.0),
    "Vine & Valley":        H("#f8f0f2", "lines",    "double",  "#7b2340", "#3b1a26", 0.9,  False, "round", "dot_triangle",      "mark_only",   "top_left",      "stamp",    "serif",    400, "smallcaps", 1.0),
    "Hollowbrook Cellars":  H("#f6f1ea", "none",     "heavy",   "#5a2a3a", "#2a1a20", 1.1,  True,  "sharp", "cask",             "mark_only",   "bottom_left",   "rect",     "serif",    700, "caps",      2.0),
    "Stonepine Estate":     H("#eef2ec", "lines",    "thin",    "#3f5a3a", "#1f2a1c", 0.9,  False, "sharp", "grapes",             "mark_only",   "top_right",     "outline",  "serif",    400, "smallcaps", 1.5),
    "Orchardgate Cider Co.": H("#f9f3df", "dots",    "ticks",   "#a8742a", "#3a2a14", 1.0,  False, "round", "orchard_leaf",          "mark_only",   "bottom_right",  "tab",      "humanist", 700, "title",     0.5),
    "Olivar Grove":         H("#f5f5e9", "none",     "ticks",   "#6b7a2a", "#33391a", 1.0,  False, "round", "three_drops",       "mark_only",   "top_right",     "rect",     "serif",    700, "caps",      2.0),
    "Copper Hill Preserves": H("#fbf1e7", "none",    "double",  "#b5562b", "#4a2a1a", 1.0,  False, "round", "peaks",             "mark_only",   "top_left",      "flag",     "serif",    400, "title",     0.0),
    "Pantry Mill":          H("#f4efe4", "hatch",    "heavy",   "#3b5b7a", "#2b3440", 1.2,  False, "sharp", "squares_circle",    "mark_only",   "top_left",      "underline", "mono",    400, "caps",      2.0),
    "Hearth & Table":       H("#f7efe8", "none",     "rounded", "#8c3b2a", "#3a2620", 1.0,  False, "round", "rainbow",           "mark_only",   "bottom_right",  "flag",     "serif",    700, "lower",     0.0),
    "Crofter's Bakehouse":  H("#f6efe2", "lines",    "rounded", "#9c6b30", "#4a3520", 1.1,  False, "round", "venn",              "mark_only",   "top_right",     "outline",  "serif",    400, "smallcaps", 0.0),
    "Brackenmere Home":     H("#f3f1ea", "diagonal", "double",  "#4f6b4a", "#2a3328", 1.0,  False, "sharp", "quad_squares",      "mark_only",   "top_right",     "underline", "serif",   400, "caps",      3.0),
    "Pewley Table":         H("#ffffff", "grid",     "thin",    "#2f5e8c", "#22344a", 0.9,  False, "round", "target",            "mark_only",   "top_left",      "stamp",    "sans",     400, "caps",      2.0),
    # The brands the scaled build adds (scale.EXTRA_BRANDS): lockups, then marks alone.
    "Marrowgate":           H("#f4f2ee", "dots",     "heavy",   "#3d4f7a", "#1e2638", 1.2,  False, "sharp", "arch",              "mark_right",  "top_right",     "none",     "serif",    700, "caps",      2.0),
    "Pellbrook":            H("#eef4f0", "none",     "thin",    "#2e7d5b", "#1f3a2e", 0.9,  True,  "round", "ring_pair",         "band_bottom", "bottom_center", "none",     "sans",     400, "caps",      3.0),
    "Osier & Vane":         H("#f6f0e8", "grid",     "rounded", "#8a4b2f", "#3a2418", 1.0,  False, "round", "fan",               "mark_above",  "top_left",      "none",     "humanist", 700, "smallcaps", 1.0),
    "Tallow Street":        H("#f2f2f2", "diagonal", "none",    "#444444", "#141414", 1.35, False, "sharp", "bar_trio",          "badge",       "top_left",      "none",     "mono",     400, "caps",      1.0),
    "Dovecote Lane":        H("#fbf3f6", "none",     "double",  "#a05a7a", "#40263a", 0.75, True,  "round", "half_moons",        "pill",        "top_center",    "none",     "serif",    400, "title",     1.0, True),
    "Larchwood Living":     H("#f1efe6", "lines",    "heavy",   "#5a6b3a", "#2c331d", 1.1,  False, "round", "triangle_pair",     "mark_left",   "bottom_right",  "none",     "sans",     400, "title",     0.0),
    "Brightwater Botanics": H("#eef7f5", "dots",     "double",  "#2a8c82", "#1b3f3b", 0.9,  False, "round", "dot_ring",          "band_top",    "top_center",    "none",     "humanist", 400, "caps",      2.5),
    "Mossgill Dairy":       H("#f3f8ee", "none",     "ticks",   "#4f8a3a", "#25401c", 1.2,  True,  "sharp", "wheat_ear",         "mark_right",  "bottom_left",   "none",     "humanist", 700, "lower",     0.5),
    "Cobbleway":            H("#f5efe8", "hatch",    "thin",    "#7a4a2a", "#33241a", 1.35, False, "sharp", "steps",             "mark_above",  "bottom_left",   "none",     "mono",     700, "title",     0.0),
    "Pipwick Toys":         H("#fff4e0", "dots",     "rounded", "#e06a1f", "#2b3a5a", 1.2,  True,  "round", "pinwheel",          "pill",        "bottom_left",   "none",     "sans",     700, "lower",     1.5),
    "Hushwell":             H("#f3f1f8", "none",     "rounded", "#6a5a9a", "#2e2846", 0.8,  False, "round", "hourglass",         "mark_only",   "bottom_left",   "tab",      "humanist", 400, "lower",     2.0),
    "Emberly Home":         H("#fbf2ec", "diagonal", "heavy",   "#b5502f", "#3d2219", 1.1,  True,  "sharp", "keyhole",           "mark_only",   "top_right",     "plain",    "sans",     700, "title",     0.0),
    "Cobble & Kiln":        H("#f2efe9", "grid",     "double",  "#6e5a48", "#2d251e", 1.3,  False, "sharp", "square_dot",        "mark_only",   "bottom_left",   "stamp",    "mono",     700, "lower",     0.0),
    "Orrin Skin":           H("#fdf3ef", "none",     "thin",    "#c46b5a", "#3a2420", 0.75, True,  "round", "diamond_dot",       "mark_only",   "bottom_right",  "outline",  "sans",     400, "smallcaps", 3.0),
    "Wheatsheaf Lane":      H("#fbf6e6", "lines",    "ticks",   "#b08a2a", "#3b3018", 1.0,  False, "sharp", "crown",             "mark_only",   "top_left",      "tab",      "sans",     400, "lower",     1.0),
    "Barrowby Kitchen":     H("#f6efe6", "dots",     "heavy",   "#9a3b2b", "#3a1e18", 1.2,  True,  "round", "striped_disc",      "mark_only",   "bottom_right",  "rect",     "humanist", 700, "caps",      0.5),
    "Treadmoor":            H("#eef0f2", "hatch",    "none",    "#3a4a5a", "#161e26", 1.35, True,  "sharp", "arrow_up",          "mark_only",   "top_right",     "underline", "humanist", 700, "title",    1.5),
    "Rookery Garden Co.":   H("#f0f5ec", "none",     "heavy",   "#3f6b35", "#1f3319", 1.0,  True,  "round", "ladder",            "mark_only",   "bottom_left",   "flag",     "serif",    700, "title",     2.0),
    "Ribbonvale":           H("#fbeff3", "dots",     "thin",    "#c0336b", "#3e1a2a", 0.9,  False, "sharp", "bell",              "mark_only",   "top_left",      "outline",  "mono",     400, "smallcaps", 0.5, True),
    "Clearbrook Household": H("#eef6fb", "grid",     "rounded", "#2f7fb5", "#1a3448", 1.0,  False, "sharp", "cross_ring",        "mark_only",   "bottom_right",  "tab",      "sans",     700, "caps",      1.0),
    # The brands of the breadth and scale-only templates (breadth_rows, scale_rows).
    "Calderwick Denim":     H("#eef1f6", "diagonal", "ticks",   "#2c4a7a", "#17243a", 1.25, True,  "sharp", "rivet_pair",        "badge",       "bottom_right",  "none",     "mono",     700, "lower",     2.5),
    "Kettleby Tea Co.":     H("#f7f3e8", "lines",    "rounded", "#5e7a3a", "#2a3519", 0.85, False, "round", "teapot",            "mark_above",  "top_right",     "none",     "serif",    700, "smallcaps", 1.5, True),
    "Brewhollow Roasters":  H("#f3ece4", "grid",     "none",    "#6b3f24", "#2e1a10", 1.3,  True,  "round", "bean",              "band_bottom", "bottom_center", "none",     "humanist", 400, "caps",      3.0),
    "Fenwold Nursery":      H("#eff6ea", "hatch",    "double",  "#4a7d2c", "#203616", 1.05, False, "sharp", "sprout",            "pill",        "top_right",     "none",     "serif",    400, "lower",     0.5),
    "Hollin Hair":          H("#f8eff4", "lines",    "none",    "#8a3f6e", "#3a1a2e", 0.8,  True,  "round", "comb",              "mark_only",   "top_left",      "stamp",    "humanist", 400, "caps",      2.5, True),
    "Mirefield Naturals":   H("#f0f6f1", "diagonal", "thin",    "#3a8a6a", "#183a2c", 0.95, False, "sharp", "droplet_leaf",      "mark_only",   "top_right",     "flag",     "mono",     400, "title",     1.5),
    "Puddlecombe Toys":     H("#eaf4fb", "dots",     "ticks",   "#2a86c4", "#16344a", 1.25, False, "round", "puddle",            "mark_only",   "bottom_right",  "plain",    "sans",     700, "smallcaps", 2.0, True),
    "Freshfold":            H("#f4f8fb", "hatch",    "rounded", "#4a90a8", "#1e3a44", 0.9,  True,  "sharp", "fold",              "mark_only",   "bottom_left",   "underline", "serif",   700, "caps",      1.5),
    "Soapwell":             H("#f2f0fa", "none",     "double",  "#6a5ac0", "#26204a", 1.15, True,  "round", "bubbles",           "mark_only",   "top_left",      "rect",     "sans",     400, "title",     2.5),
    # Invented brands of the Mens clothing depth (gen#310): a color or category word in the name.
    "Black Curlew":         H("#f2f2f0", "diagonal", "thin",    "#1a1a1a", "#262626", 1.2,  False, "sharp", "stacked_bars",      "mark_left",   "bottom_left",   "none",     "sans",     700, "smallcaps", 1.5),
    "Yellow Plover":        H("#fffbe6", "lines",    "ticks",   "#d9a400", "#3a3000", 0.85, True,  "round", "half_disc",         "badge",       "bottom_center", "none",     "humanist", 400, "caps",      0.5, True),
    "Blue Bull":            H("#eef2f8", "hatch",    "double",  "#1f4e9c", "#14284a", 1.1,  False, "round", "bull_horns",        "mark_right",  "top_right",     "none",     "serif",    700, "caps",      1.2),
    "Jacket Wren":          H("#eef3ee", "grid",     "double",  "#3f6b4f", "#1e3327", 1.05, False, "round", "slanted_blades",    "mark_only",   "top_right",     "stamp",    "mono",     400, "title",     1.0),
    # The invented brands of the apparel decoys (decoy_apparel, gen#311, class 7).
    "Red Plover":           H("#fbf1ee", "lines",    "thin",    "#b5382c", "#3a1a16", 1.0,  False, "round", "bell",              "mark_left",   "bottom_left",   "none",     "serif",    400, "title",     1.0),
    "Blue Otter":           H("#eef3fa", "dots",     "double",  "#2f5d9a", "#182b48", 1.1,  False, "sharp", "fold",              "mark_above",  "top_left",      "none",     "sans",     700, "caps",      2.0),
    "Green Stoat":          H("#eff6ee", "diagonal", "rounded", "#3f7d3a", "#1d3a1b", 1.2,  True,  "round", "sprout",            "band_top",    "top_center",     "none",     "humanist", 400, "lower",     0.5),
    "Yellow Wagtail":       H("#fcf7e3", "grid",     "heavy",   "#c49a1c", "#41330a", 1.0,  False, "sharp", "bubbles",           "pill",        "top_center",    "none",     "mono",     400, "smallcaps", 1.5),
    "Black Lapwing":        H("#f1f1f1", "none",     "none",    "#222222", "#111111", 1.3,  False, "sharp", "ladder",            "mark_right",  "top_right",     "none",     "sans",     700, "caps",      3.0),
    "White Dormouse":       H("#ffffff", "hatch",    "ticks",   "#8a8a8a", "#2e2e2e", 0.9,  True,  "round", "steps",             "badge",       "bottom_center", "none",     "serif",    400, "title",     0.0),
    "Jumper Jay":           H("#f7eefa", "lines",    "thin",    "#8a3fa0", "#341a3e", 1.0,  False, "round", "puddle",            "band_bottom", "bottom_center",      "none",     "humanist", 700, "title",     1.0),
    # A real brand (real_brands.ALLOWED, gen#341): text only, so the drawing carries no logo.
    "Nike":                 H("#f6f6f6", "none",     "rounded", "#111111", "#111111", 1.0,  False, "round", "none",              "mark_left",   "bottom_left",   "none",     "sans",     400, "lower",     0.5),
    "Coat Crake":           H("#f3efe8", "dots",     "double",  "#7a5a3a", "#30241a", 1.1,  False, "sharp", "comb",              "mark_only",   "bottom_left",   "stamp",    "mono",     700, "lower",     2.0),
    # The beauty depth brands (type_specs, gen#214): invented, text only.
    "Aldermist":           H("#fbf1f1", "dots", "double", "#b0486a", "#3a1a28", 0.85, False, "sharp", "mist_cloud", "mark_only", "top_left", "outline", "humanist", 700, "caps", 1.0),
    "Citrus Heron":        H("#f1f5f8", "lines", "rounded", "#4a8a52", "#1e3a22", 0.90, False, "round", "sparkle", "mark_only", "top_right", "flag", "serif", 400, "smallcaps", 1.5),
    "Clay Wren":           H("#f4f1fa", "grid", "heavy", "#9a3a78", "#38183a", 0.95, False, "sharp", "jar", "mark_only", "bottom_left", "underline", "humanist", 400, "lower", 2.0),
    "Cloth Wren":          H("#f2f7ef", "diagonal", "ticks", "#6a4fa0", "#2a1c3e", 1.00, False, "round", "feather", "mark_only", "bottom_right", "tab", "serif", 700, "title", 2.5),
    "Dewy Finch":          H("#faf3e6", "hatch", "none", "#2f7f7a", "#123a38", 1.05, False, "sharp", "dropper", "mark_only", "top_left", "rect", "humanist", 400, "caps", 1.0),
    "Fenmere":             H("#eef3f3", "none", "thin", "#3a6f8f", "#16303e", 0.85, True, "round", "flask", "mark_only", "top_right", "plain", "serif", 400, "smallcaps", 1.5),
    "Pearlbrook":          H("#f8f0f6", "dots", "double", "#b9803a", "#3e2a12", 0.90, False, "sharp", "pearl_row", "mark_only", "bottom_left", "stamp", "humanist", 700, "lower", 2.0),
    "Red Kestrel":         H("#fbf1f1", "lines", "rounded", "#b0486a", "#3a1a28", 0.95, False, "round", "lip_swipe", "mark_only", "bottom_right", "outline", "serif", 400, "title", 2.5),
    "Rose Kestrel":        H("#f1f5f8", "grid", "heavy", "#4a8a52", "#1e3a22", 1.00, False, "sharp", "rose_bud", "mark_only", "top_left", "flag", "humanist", 400, "caps", 1.0),
    "Sorrel & Salt":       H("#f4f1fa", "diagonal", "ticks", "#9a3a78", "#38183a", 1.05, False, "round", "shell", "mark_only", "top_right", "underline", "serif", 700, "smallcaps", 1.5),
    "Thornlea Skin":       H("#f2f7ef", "hatch", "none", "#6a4fa0", "#2a1c3e", 0.85, False, "sharp", "tube", "mark_only", "bottom_left", "tab", "serif", 400, "lower", 2.0),
    "Vanilla Wren":        H("#faf3e6", "none", "thin", "#2f7f7a", "#123a38", 0.90, True, "round", "compact", "mark_only", "bottom_right", "rect", "serif", 400, "title", 2.5),
    "Veilmoor":            H("#eef3f3", "dots", "double", "#3a6f8f", "#16303e", 0.95, False, "sharp", "moon_stars", "mark_only", "top_left", "plain", "humanist", 700, "caps", 1.0),
    "Vitamin C Orchard":   H("#f8f0f6", "lines", "rounded", "#b9803a", "#3e2a12", 1.00, False, "round", "lash_fan", "mark_only", "top_right", "stamp", "serif", 400, "smallcaps", 1.5),
}
# fmt: on


def lockup_key(style: HouseStyle) -> tuple:
    """What makes a logo's arrangement and wordmark: no two brands share it."""
    return (
        style.layout,
        style.place,
        style.tag,
        style.font,
        style.weight,
        style.case,
        style.spacing,
        style.italic,
    )


def field_names() -> list[str]:
    return [f.name for f in fields(HouseStyle)]


def differing(a: HouseStyle, b: HouseStyle) -> int:
    return sum(x != y for x, y in zip(astuple(a), astuple(b), strict=True))
