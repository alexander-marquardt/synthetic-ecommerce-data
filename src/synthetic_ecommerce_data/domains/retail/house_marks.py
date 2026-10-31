"""The composite marks of the brand house styles (:mod:`house_styles`)."""

# ruff: noqa: E501 -- SVG literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

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


def m_twin_arcs(c: str) -> list[str]:
    return [_stroke("M-.85,.2 A.85,.85 0 0 1 .05,-.65", 0.15, c),
            _stroke("M-.05,.65 A.85,.85 0 0 0 .85,-.2", 0.15, c), _dot(0, 0, 0.14, c)]


def m_notched_square(c: str) -> list[str]:
    return [f'<path d="M-.75,-.75 L.75,-.75 L.75,.75 L-.75,.75 Z M-.25,-.75 L-.25,-.25 L.25,-.25 '
            f'L.25,-.75 Z" fill="{c}" fill-rule="evenodd"/>']


def m_comet(c: str) -> list[str]:
    return [_dot(.45, -.35, .3, c), _stroke("M.2,-.1 L-.8,.7", 0.14, c),
            _stroke("M.05,-.35 L-.7,.2", 0.1, c)]


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


def m_coconut_palm(c: str) -> list[str]:
    return [
        _stroke("M0,.85 Q.12,.25 -.05,-.3", 0.14, c),
        _stroke("M-.05,-.3 Q-.4,-.8 -.85,-.45", 0.1, c),
        _stroke("M-.05,-.3 Q.35,-.85 .85,-.4", 0.1, c),
        _stroke("M-.05,-.3 Q-.05,-.7 -.1,-.9", 0.1, c),
        _dot(0.14, -0.12, 0.12, c),
    ]


#: Mark name -> drawing in unit space (-1..1), painted in the brand color.
def m_toy_pair_dots(c: str) -> list[str]:
    return [_dot(-0.4, 0, 0.3, c), _dot(0.4, 0, 0.3, c)]


def m_toy_ring_dot(c: str) -> list[str]:
    return [_ring(0, 0, 0.5, 0.12, c), _dot(0, 0, 0.18, c)]


def m_toy_star(c: str) -> list[str]:
    return [_star(0, 0, 0.7, c)]


def m_toy_three_rings(c: str) -> list[str]:
    return [_ring(x, 0, 0.3, 0.09, c) for x in (-0.6, 0, 0.6)]


def m_toy_diag_dots(c: str) -> list[str]:
    return [_dot(-0.5, 0.5, 0.2, c), _dot(0, 0, 0.25, c), _dot(0.5, -0.5, 0.3, c)]


def m_toy_stack_rings(c: str) -> list[str]:
    return [_ring(0, y, 0.3, 0.09, c) for y in (-0.5, 0, 0.5)]


# Ten marks of their own for the brands whose rows had borrowed one another brand's (a mark is one
# brand's logo: test_no_two_brands_share_a_mark). Drawn in the same unit box as the marks above.
def m_saltire(c: str) -> list[str]:
    return [_stroke("M-.7,-.7 L.7,.7 M.7,-.7 L-.7,.7", 0.16, c), _dot(0, 0, 0.2, c)]


def m_well(c: str) -> list[str]:
    return [_ring(0, 0, 0.8, 0.12, c), _ring(0, 0, 0.45, 0.12, c), _dot(0, 0, 0.14, c)]


def m_oak_leaf(c: str) -> list[str]:
    return [
        f'<path d="M0,-.85 Q.75,-.3 .45,.45 Q0,.85 -.45,.45 Q-.75,-.3 0,-.85 Z" fill="{c}"/>',
        _stroke("M0,-.5 L0,.85", 0.1, "#ffffff"),
    ]


def m_plume(c: str) -> list[str]:
    return [
        f'<path d="M-.7,.8 Q-.8,-.5 .6,-.85 Q.2,-.1 -.7,.8 Z" fill="{c}"/>',
        _stroke("M-.7,.8 L.1,-.2", 0.07, "#ffffff"),
    ]


def m_egg_pair(c: str) -> list[str]:
    return [
        f'<ellipse cx="-.38" cy=".1" rx=".32" ry=".5" fill="{c}"/>',
        f'<ellipse cx=".38" cy="-.1" rx=".32" ry=".5" fill="none" stroke="{c}" stroke-width=".1"/>',
    ]


def m_paw_print(c: str) -> list[str]:
    pads = ((-0.55, -0.15), (-0.2, -0.6), (0.2, -0.6), (0.55, -0.15))
    toes = [_dot(x, y, 0.15, c) for x, y in pads]
    return [f'<ellipse cx="0" cy=".35" rx=".42" ry=".34" fill="{c}"/>', *toes]


def m_toggle(c: str) -> list[str]:
    return [
        f'<rect x="-.8" y="-.3" width="1.6" height=".6" rx=".3" fill="none" stroke="{c}" stroke-width=".12"/>',
        _stroke("M-.3,-.3 L-.3,.3", 0.1, c),
        _dot(0.4, 0, 0.16, c),
    ]


def m_chevron_trio(c: str) -> list[str]:
    rows = (-0.7, -0.15, 0.4)
    return [_stroke(f"M-.7,{_n(y)} L0,{_n(y + 0.4)} L.7,{_n(y)}", 0.13, c) for y in rows]


def m_ripples(c: str) -> list[str]:
    return [_dot(0, 0, 0.14, c), _ring(0, 0, 0.45, 0.09, c), _ring(0, 0, 0.8, 0.07, c)]


def m_tail_comb(c: str) -> list[str]:
    spokes = " ".join(f"M0,.8 L{_n(x)},-.8" for x in (-0.7, -0.35, 0, 0.35, 0.7))
    return [_stroke(spokes, 0.1, c), _dot(0, 0.8, 0.15, c)]


# Knacks' mark (gen#722): a shoe's laces crossing between two rows of eyelets, in straight strokes.
def m_laced_eyelets(c: str) -> list[str]:
    eyelets = [_dot(x, y, 0.13, c) for x in (-0.6, 0.6) for y in (-0.7, 0, 0.7)]
    return [_stroke("M-.6,-.7 L.6,0 L-.6,.7 M.6,-.7 L-.6,0 L.6,.7", 0.12, c), *eyelets]


MARKS = {
    name[2:]: fn for name, fn in list(globals().items()) if name.startswith("m_") and callable(fn)
}


def mark_svg(name: str, cx: float, cy: float, size: float, color: str) -> str:
    """The composite mark ``name``, ``size`` px across, centered on (cx, cy)."""
    body = "".join(MARKS[name](color))
    return (
        f'<g class="mark" transform="translate({_n(cx)} {_n(cy)}) scale({_n(size / 2)})">{body}</g>'
    )
