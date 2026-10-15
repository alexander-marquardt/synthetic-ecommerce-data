"""Home and beauty shapes for the retail drawing kit (prototype, round 2).

Same house style as :mod:`kit`: flat outlines, one ink color, the product's
main surface painted with the record's fill. A few shapes take ``params``:
``photo_frame(size="5x7")`` draws the photo opening to scale and dimensions
it, and ``mattress_topper(depth="5cm")`` dimensions its depth.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from html import escape

from kit import (
    FONT,
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _mirror,
    _panel,
    _path,
    _shade,
    _tint,
    _word,
    register,
)
from kit_garments import _dark, _f, _lerp, _poly
from kit_lighting import styled_table_lamp

METAL = "#cfd5da"
GOLD = "#d6b56a"


def _text(
    x: float, y: float, text: str, size: float = 12, color: str = INK, extra: str = ""
) -> str:
    return (
        f'<text x="{x:g}" y="{y:g}" font-family="{FONT}" font-size="{size:g}" '
        f'text-anchor="middle" fill="{color}"{extra}>{escape(text)}</text>'
    )


def _dim(x1: float, y1: float, x2: float, y2: float, text: str) -> list[str]:
    """A dimension line with end ticks and its measurement on a white chip."""
    tick = (
        f"M{x1 - 5},{y1} L{x1 + 5},{y1} M{x2 - 5},{y2} L{x2 + 5},{y2}"
        if x1 == x2
        else f"M{x1},{y1 - 5} L{x1},{y1 + 5} M{x2},{y2 - 5} L{x2},{y2 + 5}"
    )
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    w = 10 + 7 * len(text)
    return [
        _line(f"M{x1},{y1} L{x2},{y2}", 1.2),
        _line(tick, 1.2),
        f'<rect x="{mx - w / 2:.1f}" y="{my - 9:.1f}" width="{w:.1f}" height="18" rx="3" fill="#ffffff" stroke="{INK}" stroke-width=".8"/>',
        _text(mx, my + 4.5, text, 12),
    ]


# --------------------------------------------------------------------------
# Bedding
# --------------------------------------------------------------------------

# One mattress-shaped slab in an oblique view: left, back, right, front corners.
_A, _B, _C, _D = (48, 196), (226, 134), (352, 180), (174, 244)


def _down(p: tuple[float, float], t: float) -> tuple[float, float]:
    return (p[0], p[1] + t)


def _slab(paint: str, depth: float, top_dy: float = 0) -> tuple[list[str], list]:
    A, B, C, D = (_down(p, top_dy) for p in (_A, _B, _C, _D))
    left = [A, D, _down(D, depth), _down(A, depth)]
    right = [D, C, _down(C, depth), _down(D, depth)]
    parts = [
        _path(_poly(left), paint),
        _dark(_poly(left), 0.12),
        _path(_poly(right), paint),
        _dark(_poly(right), 0.24),
        _path(_poly([A, B, C, D]), paint),
    ]
    return parts, [A, B, C, D]


def mattress_topper(paint: str, fill: Fill, label: str | None, depth: str = "5cm") -> list[str]:
    """A thick quilted slab with dimpled stitching, its depth dimensioned."""
    t = 38
    out, (A, B, C, D) = _slab(paint, t, 10)
    grid, dots = [], []
    for k in range(1, 6):
        grid.append(f"M{_f(_lerp(A, B, k / 6))} L{_f(_lerp(D, C, k / 6))}")
        grid.append(f"M{_f(_lerp(A, D, k / 6))} L{_f(_lerp(B, C, k / 6))}")
        for j in range(1, 6):
            p = _lerp(_lerp(A, D, j / 6), _lerp(B, C, j / 6), k / 6)
            dots.append(
                f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.4" fill="{INK}" fill-opacity=".5"/>'
            )
    out.append(_line(" ".join(grid), 1.2, ' stroke-dasharray="5 4" stroke-opacity=".7"'))
    out += dots
    sides = " ".join(
        f"M{_f(_lerp(a, b, k / 6))} L{_f(_down(_lerp(a, b, k / 6), t))}"
        for a, b in ((A, D), (D, C))
        for k in range(1, 6)
    )
    out.append(_line(sides, 1.0, ' stroke-dasharray="4 4" stroke-opacity=".5"'))
    out += _dim(C[0] + 18, C[1], C[0] + 18, C[1] + t, depth)
    return out


def mattress_protector(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A fitted cover on a deep mattress: a gathered skirt and beading water drops."""
    t = 64
    out, (A, B, C, D) = _slab(paint, t, -6)
    gathers = []
    for a, b in ((A, D), (D, C)):
        for k in range(1, 24):
            p = _down(_lerp(a, b, k / 24), t)
            gathers.append(f"M{p[0]:.1f},{p[1] - 2:.1f} L{p[0] + 1:.1f},{p[1] - 12:.1f}")
    out.append(_line(" ".join(gathers), 1.0, ' stroke-opacity=".6"'))
    out.append(
        _line(
            f"M{_f(_down(A, 10))} L{_f(_down(D, 10))} L{_f(_down(C, 10))}",
            1.2,
            ' stroke-dasharray="6 4"',
        )
    )
    drop = "M0,-24 C8,-10 15,-2 15,8 A15,15 0 0 1 -15,8 C-15,-2 -8,-10 0,-24 Z"
    for (x, y), s in (((196, 176), 1.0), ((246, 190), 0.6), ((160, 204), 0.5)):
        out.append(
            f'<g transform="translate({x} {y}) scale({s})">{_path(drop, "#8cc8ee", 2)}'
            f"{_highlight('M-7,6 Q-7,-2 -2,-8', 3, 0.8)}</g>"
        )
    return out


def pillow(paint: str, fill: Fill, label: str | None) -> list[str]:
    d = "M78,116 Q200,92 322,116 Q346,216 322,316 Q200,340 78,316 Q54,216 78,116 Z"
    folds = "M78,116 Q98,136 116,140 M322,116 Q302,136 284,140 M78,316 Q98,296 116,292 M322,316 Q302,296 284,292"
    return [
        '<ellipse cx="200" cy="338" rx="130" ry="10" fill="#000000" fill-opacity=".08"/>',
        _path(d, paint),
        _path(
            d,
            "none",
            1.2,
            ' transform="translate(200 216) scale(.9) translate(-200 -216)" stroke-dasharray="5 4"',
        ),
        _line(folds, 1.4, ' stroke-opacity=".7"'),
        _highlight("M110,150 Q150,128 200,126", 6, 0.35),
    ]


def duvet(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A duvet laid flat, box-stitched, with its corner turned back; ``label`` is its tog."""
    p1, p2, corner = (232, 340), (340, 236), (340, 340)
    # Reflect the corner across the fold line p1-p2 for the flap's tip.
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    t = ((corner[0] - p1[0]) * dx + (corner[1] - p1[1]) * dy) / (dx * dx + dy * dy)
    foot = (p1[0] + t * dx, p1[1] + t * dy)
    tip = (2 * foot[0] - corner[0], 2 * foot[1] - corner[1])
    body = f"M60,84 Q200,76 340,84 Q348,160 340,{p2[1]} L{p1[0]},{p1[1]} Q146,348 60,340 Q52,212 60,84 Z"
    out = [
        _path(body, paint),
        _line(
            "M153,84 L153,342 M247,82 L247,320 M58,170 L344,170 M56,255 L342,255",
            1.2,
            ' stroke-dasharray="6 4" stroke-opacity=".7"',
        ),
        _path(f"M{_f(p1)} L{_f(p2)} L{_f(tip)} Z", "#f4f1ea"),
        _line(
            f"M{_f(_lerp(p1, tip, 0.12))} L{_f(_lerp(p2, tip, 0.12))}",
            1.0,
            ' stroke-dasharray="4 3"',
        ),
    ]
    if label:
        out += [
            f'<circle cx="122" cy="132" r="40" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
            _word(label.split()[0], 122, 124, 60, 26),
            _text(122, 154, " ".join(label.split()[1:]) or "", 13),
        ]
    return out


# --------------------------------------------------------------------------
# Bathroom and beach
# --------------------------------------------------------------------------


def bath_towel(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A stack of three folded towels, each with a woven border band."""
    out = ['<ellipse cx="200" cy="344" rx="150" ry="9" fill="#000000" fill-opacity=".08"/>']
    for k, y in enumerate((280, 220, 160)):
        x0 = 78 + 6 * (k % 2)
        d = f"M{x0 + 26},{y} L{x0 + 246},{y} L{x0 + 246},{y + 58} L{x0 + 26},{y + 58} Q{x0},{y + 58} {x0},{y + 29} Q{x0},{y} {x0 + 26},{y} Z"
        band = f"M{x0 + 196},{y} L{x0 + 214},{y} L{x0 + 214},{y + 58} L{x0 + 196},{y + 58} Z"
        out += [
            _path(d, paint),
            _path(
                band, _tint(fill.base, 0.35) if fill.pattern == "solid" else "#ffffff", LW_DETAIL
            ),
            _line(
                f"M{x0 + 246},{y + 14} L{x0 + 236},{y + 14} M{x0 + 246},{y + 29} L{x0 + 238},{y + 29} M{x0 + 246},{y + 44} L{x0 + 236},{y + 44}",
                1.2,
            ),
            _line(
                f"M{x0 + 30},{y + 18} L{x0 + 186},{y + 18} M{x0 + 22},{y + 36} L{x0 + 186},{y + 36}",
                1.2,
                ' stroke-dasharray="1 5" stroke-opacity=".6"',
            ),
        ]
    return out


def beach_towel(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A long towel half rolled up, with fringed ends."""
    fringe = " ".join(f"M{x},40 L{x + 1},26" for x in range(124, 280, 7))
    return [
        _path("M120,40 L280,40 L280,290 L120,290 Z", paint),
        _line(fringe, 1.4),
        _line("M120,50 L280,50", 1.2, ' stroke-dasharray="4 3"'),
        _path(
            "M112,282 L288,282 Q312,282 312,314 Q312,346 288,346 L112,346 Q88,346 88,314 Q88,282 112,282 Z",
            paint,
        ),
        _dark(
            "M112,282 L288,282 Q312,282 312,314 Q312,346 288,346 L112,346 Q88,346 88,314 Q88,282 112,282 Z",
            0.1,
        ),
        f'<ellipse cx="292" cy="314" rx="18" ry="32" fill="{_tint(fill.base, 0.2)}" stroke="{INK}" stroke-width="{LW}"/>',
        _line("M292,286 Q304,300 300,316 Q296,332 288,330 Q280,326 284,312 Q290,302 294,312", 1.4),
        _line(" ".join(f"M{x},346 L{x + 1},358" for x in range(112, 280, 7)), 1.4),
    ]


# --------------------------------------------------------------------------
# Dining and living
# --------------------------------------------------------------------------


def dinner_set(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A plate stood up behind a bowl and a mug, all in one decoration."""
    return [
        f'<circle cx="168" cy="162" r="116" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<circle cx="168" cy="162" r="82" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<circle cx="168" cy="162" r="74" fill="none" stroke="{INK}" stroke-width="1" stroke-opacity=".4"/>',
        _path("M62,272 Q66,346 150,350 Q234,346 238,272 Z", paint),
        f'<ellipse cx="150" cy="272" rx="88" ry="18" fill="#ffffff" stroke="{INK}" stroke-width="{LW}"/>',
        _dark("M66,276 Q78,300 150,304 Q222,300 234,276 Q226,290 150,292 Q74,290 66,276 Z", 0.06),
        _path("M316,240 Q362,236 360,276 Q358,314 314,310", "none", 12),
        _path(
            "M316,240 Q362,236 360,276 Q358,314 314,310",
            "none",
            5,
            stroke=_tint(fill.base, 0.0) if fill.pattern == "solid" else "#ffffff",
        ),
        _path("M250,214 L250,334 Q284,346 318,334 L318,214 Z", paint),
        f'<ellipse cx="284" cy="214" rx="34" ry="9" fill="#ffffff" stroke="{INK}" stroke-width="{LW}"/>',
    ]


def cutlery_set(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A fork, knife and spoon with painted handles."""
    fork = (
        "M126,64 L132,64 L132,124 L137,124 L137,64 L143,64 L143,124 L148,124 L148,64 "
        "L154,64 L154,124 L159,124 L159,64 L165,64 L165,146 Q165,174 150,184 L150,206 "
        "L140,206 L140,184 Q126,174 126,146 Z"
    )
    knife = "M194,58 Q216,70 212,210 L190,210 L190,66 Q190,58 194,58 Z"
    spoon = "M258,148 L260,206 L250,206 L252,148 Z"
    out = [
        '<ellipse cx="200" cy="350" rx="120" ry="8" fill="#000000" fill-opacity=".08"/>',
        _path(fork, METAL),
        _path(knife, METAL),
        _path(spoon, METAL),
        f'<ellipse cx="255" cy="104" rx="26" ry="44" fill="{METAL}" stroke="{INK}" stroke-width="{LW}"/>',
        _highlight("M240,84 Q244,70 254,66", 4, 0.8),
        _highlight("M196,72 L196,196", 3, 0.7),
    ]
    for cx in (145, 201, 255):
        out.append(
            f'<rect x="{cx - 12}" y="204" width="24" height="140" rx="11" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>'
        )
        out.append(
            f'<circle cx="{cx}" cy="226" r="2.4" fill="{METAL}" stroke="{INK}" stroke-width=".8"/>'
        )
        out.append(
            f'<circle cx="{cx}" cy="322" r="2.4" fill="{METAL}" stroke="{INK}" stroke-width=".8"/>'
        )
    return out


def table_lamp(
    paint: str,
    fill: Fill,
    label: str | None,
    shade: str | None = None,
    style: str | None = None,
    shade_color: str = "white",
    power: str = "plug-in",
) -> list[str]:
    """A tapered shade on a gourd base.

    With ``shade`` (a ``#rrggbb`` the record names), the base takes the record's own color
    and pattern and the shade takes ``shade``. Without it the shade is the painted surface
    and the base the accent color, as the ceramic lamp's record reads.

    With ``style`` (gen#197: bedside, ceramic, touch, mushroom) the lighting rows' lamp is
    drawn instead (:func:`kit_lighting.styled_table_lamp`): the base in the record's fill, the
    shade in the SKU's ``shade_color``, a cable or a battery by ``power``.
    """
    if style is not None:
        return styled_table_lamp(paint, fill, style, shade_color, power)
    base = "M200,206 C150,206 140,262 156,296 C166,318 176,326 172,338 L228,338 C224,326 234,318 244,296 C260,262 250,206 200,206 Z"
    base_paint, shade_paint = (paint, shade) if shade else (fill.accent, paint)
    plinth = _shade(fill.base if shade else fill.accent, 0.2)
    return [
        _path(
            "M110,186 Q200,214 290,186 Z", "#fbe7a1", 1.0, ' fill-opacity=".8" stroke-opacity="0"'
        ),
        _line("M200,186 L200,208", 6),
        _path(base, base_paint),
        _highlight("M168,236 Q156,262 166,290", 6, 0.4),
        f'<rect x="158" y="336" width="84" height="14" rx="4" fill="{plinth}" stroke="{INK}" stroke-width="{LW}"/>',
        _line("M240,344 Q300,352 318,330 Q332,306 352,322", 2.4),
        f'<rect x="346" y="318" width="16" height="22" rx="3" fill="#ffffff" stroke="{INK}" stroke-width="1.4" transform="rotate(30 354 329)"/>',
        _path("M146,62 L254,62 L294,186 L106,186 Z", shade_paint),
        _line("M144,70 L256,70 M108,178 L292,178", 1.2, ' stroke-opacity=".6"'),
    ]


def sofa(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A three-seater: back, rolled arms, three seat cushions and a scatter cushion."""
    arm = "M44,174 Q44,142 76,142 Q108,142 108,174 L108,314 L44,314 Z"
    out = [
        _path("M84,104 Q200,92 316,104 L316,232 L84,232 Z", paint),
        _line("M161,100 L161,232 M239,100 L239,232", 1.4, ' stroke-opacity=".7"'),
        _path("M100,228 L300,228 L300,314 L100,314 Z", paint),
        _dark("M100,276 L300,276 L300,314 L100,314 Z", 0.14),
        _line("M167,228 L167,276 M233,228 L233,276 M100,276 L300,276", 1.6),
        _path(
            "M118,232 L118,170 Q118,160 128,160 L176,164 Q184,166 182,176 L180,236 Z",
            fill.accent,
            LW_DETAIL,
        ),
    ]
    out += [_path(arm, paint), _path(_mirror(arm), paint)]
    out += [
        _dark("M44,174 Q44,142 76,142 Q108,142 108,174 Z", 0.12),
        _dark(_mirror("M44,174 Q44,142 76,142 Q108,142 108,174 Z"), 0.12),
    ]
    for x in (56, 330):
        out.append(
            f'<path d="M{x},314 L{x + 14},314 L{x + 11},338 L{x + 3},338 Z" fill="#6b4a2e" stroke="{INK}" stroke-width="{LW_DETAIL}" stroke-linejoin="round"/>'
        )
    return out


def photo_frame(paint: str, fill: Fill, label: str | None, size: str = "5x7") -> list[str]:
    """A frame whose photo opening is drawn to scale (22 px per inch) and dimensioned."""
    w_in, h_in = (float(v) for v in size.lower().split("x"))
    scale, mat, rail = 22, 16, 20
    pw, ph = w_in * scale, h_in * scale
    cx, cy = 186, 184
    px, py = cx - pw / 2, cy - ph / 2
    ox, oy = px - mat - rail, py - mat - rail
    ow, oh = pw + 2 * (mat + rail), ph + 2 * (mat + rail)
    hills = (
        f"M{px:.1f},{py + ph * 0.7:.1f} Q{px + pw * 0.3:.1f},{py + ph * 0.45:.1f} {px + pw * 0.55:.1f},{py + ph * 0.66:.1f} "
        f"Q{px + pw * 0.8:.1f},{py + ph * 0.5:.1f} {px + pw:.1f},{py + ph * 0.62:.1f} L{px + pw:.1f},{py + ph:.1f} L{px:.1f},{py + ph:.1f} Z"
    )
    out = [
        f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{ow:.1f}" height="{oh:.1f}" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<rect x="{ox + rail:.1f}" y="{oy + rail:.1f}" width="{pw + 2 * mat:.1f}" height="{ph + 2 * mat:.1f}" fill="#f7f5ef" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _line(
            f"M{ox:.1f},{oy:.1f} L{ox + rail:.1f},{oy + rail:.1f} M{ox + ow:.1f},{oy:.1f} L{ox + ow - rail:.1f},{oy + rail:.1f} "
            f"M{ox:.1f},{oy + oh:.1f} L{ox + rail:.1f},{oy + oh - rail:.1f} M{ox + ow:.1f},{oy + oh:.1f} L{ox + ow - rail:.1f},{oy + oh - rail:.1f}",
            1.2,
        ),
        f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="#c4e0f2" stroke="{INK}" stroke-width="1.2"/>',
        f'<circle cx="{px + pw * 0.72:.1f}" cy="{py + ph * 0.28:.1f}" r="{min(pw, ph) * 0.1:.1f}" fill="#f4c84a"/>',
        _path(hills, "#7fae6a", 1.2),
    ]
    out += _dim(px, oy + oh + 16, px + pw, oy + oh + 16, f"{w_in:g} in")
    out += _dim(ox + ow + 18, py, ox + ow + 18, py + ph, f"{h_in:g} in")
    return out


# --------------------------------------------------------------------------
# Beauty
# --------------------------------------------------------------------------


def fragrance(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A faceted glass bottle tinted with the fill; ``label`` is the fragrance's name."""
    out = [
        f'<rect x="170" y="52" width="60" height="54" rx="6" fill="{fill.accent}" stroke="{INK}" stroke-width="{LW}"/>',
        _highlight("M180,62 L180,96", 4, 0.5),
        f'<rect x="184" y="104" width="32" height="22" fill="{METAL}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<rect x="114" y="124" width="172" height="228" rx="26" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
        _dark("M128,168 L272,168 L272,330 Q272,340 262,340 L138,340 Q128,340 128,330 Z", 0.14),
        _line(
            "M114,154 L140,124 M286,154 L260,124 M114,322 L140,352 M286,322 L260,352",
            1.2,
            ' stroke-opacity=".6"',
        ),
        _line("M200,126 L200,336", 1.0, ' stroke-opacity=".35"'),
        _highlight("M132,170 L132,300", 6, 0.45),
        f'<rect x="138" y="204" width="124" height="80" rx="4" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
    ]
    if label:
        out.append(_word(label, 200, 234, 110, 28))
    out.append(_text(200, 270, "EAU DE PARFUM", 9, INK, ' letter-spacing="1.5"'))
    return out


def lipstick(paint: str, fill: Fill, label: str | None) -> list[str]:
    """An open lipstick (the bullet carries the shade) beside its cap."""
    return [
        f'<rect x="114" y="198" width="66" height="154" rx="5" fill="{fill.accent}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<rect x="114" y="332" width="66" height="20" fill="{GOLD}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _highlight("M126,212 L126,320", 5, 0.35),
        _path("M220,154 L220,110 Q220,98 232,92 L256,76 Q262,74 262,82 L262,154 Z", paint),
        _highlight("M228,148 L228,112", 4, 0.45),
        f'<rect x="214" y="150" width="54" height="54" fill="{METAL}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<rect x="206" y="200" width="70" height="16" fill="{GOLD}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<rect x="206" y="214" width="70" height="138" rx="5" fill="{fill.accent}" stroke="{INK}" stroke-width="{LW}"/>',
        _highlight("M218,228 L218,336", 5, 0.35),
    ]


def moisturiser_jar(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = "M104,196 L296,196 L296,316 Q296,346 266,346 L134,346 Q104,346 104,316 Z"
    return [
        _path(body, paint),
        f'<rect x="96" y="138" width="208" height="60" rx="10" fill="{fill.accent}" stroke="{INK}" stroke-width="{LW}"/>',
        _line(
            " ".join(f"M{x},146 L{x},190" for x in range(110, 296, 10)),
            1.0,
            ' stroke-opacity=".35"',
        ),
        _highlight("M116,214 L116,320", 6, 0.4),
        *_panel(126, 226, 148, 86, label, 30),
    ]


def eyeliner(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A sharpened pencil and the line it draws, both in the shade."""
    pencil = [
        f'<rect x="76" y="194" width="200" height="32" rx="4" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<rect x="56" y="192" width="28" height="36" rx="6" fill="{fill.accent}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<rect x="84" y="192" width="12" height="36" fill="{METAL}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _path("M276,194 L326,206 L326,214 L276,226 Z", "#e8c99a"),
        _path("M318,204 L348,210 L318,216 Z", _shade(fill.base, 0.25), LW_DETAIL),
        _highlight("M104,201 L268,201", 3, 0.4),
    ]
    return [
        _path("M70,338 Q140,300 210,322 T342,296", "none", 7, stroke=fill.base),
        f'<g transform="rotate(-28 200 210)">{"".join(pencil)}</g>',
    ]


def gift_set(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A wide box tied with ribbon and a bow, labelled ``Gift Set``."""
    ribbon = fill.accent
    return [
        _path("M320,176 L356,150 L356,306 L320,332 Z", paint),
        _dark("M320,176 L356,150 L356,306 L320,332 Z", 0.22),
        _path("M56,176 L92,150 L356,150 L320,176 Z", paint),
        _dark("M56,176 L92,150 L356,150 L320,176 Z", 0.06),
        _path("M56,176 L320,176 L320,332 L56,332 Z", paint),
        _path("M174,176 L198,176 L198,332 L174,332 Z", ribbon, LW_DETAIL),
        _path("M174,176 L198,176 L234,150 L210,150 Z", ribbon, LW_DETAIL),
        _path("M320,248 L356,222 L356,238 L320,264 Z", ribbon, LW_DETAIL),
        _path("M204,160 C170,118 150,140 168,156 C176,164 194,164 204,160 Z", ribbon),
        _path("M204,160 C238,118 258,140 240,156 C232,164 214,164 204,160 Z", ribbon),
        _path("M204,160 L190,190 L198,192 L204,170 L212,192 L220,190 Z", ribbon, LW_DETAIL),
        f'<circle cx="204" cy="160" r="7" fill="{_shade(ribbon, 0.15)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        *_panel(214, 216, 96, 70, label, 26),
    ]


register(
    {
        "mattress_topper": mattress_topper,
        "mattress_protector": mattress_protector,
        "pillow": pillow,
        "duvet": duvet,
        "bath_towel": bath_towel,
        "beach_towel": beach_towel,
        "dinner_set": dinner_set,
        "cutlery_set": cutlery_set,
        "table_lamp": table_lamp,
        "sofa": sofa,
        "photo_frame": photo_frame,
        "fragrance": fragrance,
        "lipstick": lipstick,
        "moisturiser_jar": moisturiser_jar,
        "eyeliner": eyeliner,
        "gift_set": gift_set,
    },
    {"mattress_topper": 10, "mattress_protector": 10},
)
