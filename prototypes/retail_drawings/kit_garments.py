"""Parametric legwear and tops for the retail drawing kit (prototype, round 2).

Two shapes, each driven by ``params`` so one function draws a whole family:

* ``trousers(fit=..., rise=..., style=..., waist=...)``: one silhouette per
  leg fit (skinny ... cigarette), built from a profile of the left leg's
  outer and inner seam at the hip, thigh, knee, calf and hem, splined and
  mirrored. The rise moves the waistband up or down above a fixed crotch.
* ``top(neckline=..., sleeve=..., kind=...)``: a body, a neckline cut with
  the garment's inside showing through it, and one of four sleeve lengths.
  ``kind`` adds a knit's rib bands (jumper) or a button placket (cardigan).

Round 1's ``jeans_straight`` and ``jeans_bootcut`` names are kept as aliases.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, SIZE, Fill, _line, _path, _shade, _tint, register

Pt = tuple[float, float]


def _f(p: Pt) -> str:
    return f"{p[0]:.1f},{p[1]:.1f}"


def smooth(points: list[Pt]) -> str:
    """A Catmull-Rom spline through ``points`` as cubic segments.

    The pen must already stand on ``points[0]``; no ``M`` is emitted.
    """
    pts = [points[0], *points, points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f"C{_f(c1)} {_f(c2)} {_f(p2)}")
    return " ".join(out)


def mirror(points: list[Pt]) -> list[Pt]:
    return [(SIZE - x, y) for x, y in points]


def _x_at(points: list[Pt], y: float) -> float:
    """The x of the polyline ``points`` (top to bottom) at height ``y``."""
    for (x1, y1), (x2, y2) in zip(points, points[1:], strict=False):
        if y1 <= y <= y2 and y2 > y1:
            return x1 + (x2 - x1) * (y - y1) / (y2 - y1)
    return points[-1][0] if y > points[-1][1] else points[0][0]


def _lerp(a: Pt, b: Pt, t: float) -> Pt:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _inside_color(fill: Fill) -> str:
    """The garment's inside: a shade of a light color, a tint of a dark one."""
    r, g, b = (int(fill.base[i : i + 2], 16) for i in (1, 3, 5))
    light = (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.4
    return _shade(fill.base, 0.35) if light else _tint(fill.base, 0.4)


def _dark(d: str, opacity: float = 0.22) -> str:
    """A shadow laid over a painted area, so pattern fills shade too."""
    return f'<path d="{d}" fill="#000000" fill-opacity="{opacity:g}" stroke="none"/>'


# --------------------------------------------------------------------------
# Legwear
# --------------------------------------------------------------------------

CROTCH_Y = 178
HIP_Y = 150
HEM_Y = 362
#: rise -> (waistband top, waistband bottom, waist x of the left side)
RISES = {"high": (36, 64, 136), "mid": (64, 90, 131), "low": (92, 114, 125)}

#: fit -> outer x at the hip, then (outer x, inner x) of the LEFT leg at the
#: thigh, knee, calf and hem. The right leg is the mirror image.
FITS: dict[str, dict] = {
    # Skinny hugs the leg to a narrow ankle with a wide gap between the legs;
    # slim tapers only a little and stays close to straight below the knee.
    "skinny": {"hip": 128, "legs": [(136, 195), (153, 186), (159, 184), (163, 183)]},
    "slim": {"hip": 126, "legs": [(128, 197), (133, 195), (136, 194), (138, 194)]},
    "straight": {"hip": 125, "legs": [(125, 197), (129, 195), (130, 195), (131, 195)]},
    # Bootcut runs straight to the knee, then opens a little: no pinch at the knee.
    "bootcut": {"hip": 126, "legs": [(128, 197), (132, 195), (129, 196), (119, 198)]},
    "flared": {"hip": 127, "legs": [(130, 196), (146, 190), (120, 193), (90, 197)]},
    "wide_leg": {"hip": 118, "legs": [(111, 196), (103, 196), (99, 196), (95, 196)]},
    "barrel": {"hip": 124, "legs": [(110, 194), (92, 178), (106, 182), (140, 188)]},
    "balloon": {"hip": 120, "legs": [(106, 197), (96, 197), (112, 196), (151, 186)], "cuff": True},
    "carrot": {
        "hip": 106,
        "legs": [(117, 197), (133, 193), (144, 191), (154, 189)],
        "pleats": True,
    },
    "cigarette": {
        "hip": 127,
        "legs": [(131, 196), (140, 192), (141, 192), (141, 192)],
        "hem_y": 314,
    },
    # Tapered: room at the thigh, narrowing steadily to the ankle.
    "tapered": {"hip": 123, "legs": [(121, 197), (137, 192), (147, 189), (155, 188)]},
    # Relaxed: loose and straight from the hip, a wide gap-free hem.
    "relaxed": {"hip": 120, "legs": [(115, 197), (117, 196), (118, 196), (119, 196)]},
    # Mom: roomy hip and thigh, a gentle taper to an ankle-length hem.
    "mom": {"hip": 121, "legs": [(117, 196), (130, 193), (138, 191), (144, 190)], "hem_y": 340},
    # Boyfriend: slouchy and a little tapered, the hem rolled up.
    "boyfriend": {"hip": 121, "legs": [(118, 196), (125, 194), (130, 193), (134, 192)], "cuff": True},
    # Kick flare: slim to the calf, then a small flare at a cropped hem.
    "kick_flare": {"hip": 127, "legs": [(131, 196), (141, 192), (137, 193), (119, 196)], "hem_y": 336},
    # Super skinny: narrower than skinny at every point, down to a sprayed-on ankle.
    "super_skinny": {"hip": 129, "legs": [(140, 193), (158, 185), (164, 183), (167, 182)]},
    # Jegging: skinny through the leg, cut at the ankle bone.
    "jegging": {"hip": 130, "legs": [(138, 194), (155, 186), (160, 184), (163, 183)], "hem_y": 348},
    # Baggy: the widest straight leg, the hem stacked on the shoe.
    "baggy": {"hip": 114, "legs": [(105, 197), (100, 197), (98, 197), (97, 197)], "cuff": True},
    # Culotte: wide from the hip, cropped at mid calf.
    "culotte": {"hip": 119, "legs": [(108, 196), (98, 196), (92, 196), (88, 196)], "hem_y": 296},
    # Athletic: room at the seat and thigh, then a steep taper to the ankle.
    "athletic": {"hip": 119, "legs": [(113, 197), (132, 193), (143, 190), (149, 189)]},
    # Cropped: a straight leg that stops above the ankle.
    "cropped": {"hip": 125, "legs": [(125, 197), (128, 196), (129, 196), (130, 196)], "hem_y": 322},
}


def _leg_outline(fit: str, rise: str) -> tuple[list[Pt], list[Pt]]:
    """The left leg's outer seam (waist to hem) and inner seam (crotch to hem)."""
    _, bb, wx = RISES[rise]
    spec = FITS[fit]
    hem = spec.get("hem_y", HEM_Y)
    ys = [210, 210 + (hem - 210) * 0.4, 210 + (hem - 210) * 0.71, hem]
    # A hip much wider than the waistband (carrot, balloon) would leave the
    # band's corner at a sharp angle; an easing point lets the seam leave the
    # band almost vertically and swell out below it.
    flare = wx - spec["hip"]
    ease = [(wx - 0.12 * flare, bb + 0.35 * (HIP_Y - bb))] if flare > 8 else []
    outer = [
        (wx, bb),
        *ease,
        (spec["hip"], HIP_Y),
        *[(o, y) for (o, _), y in zip(spec["legs"], ys, strict=True)],
    ]
    inner = [(197, CROTCH_Y), *[(i, y) for (_, i), y in zip(spec["legs"], ys, strict=True)]]
    return outer, inner


def trousers(
    paint: str,
    fill: Fill,
    label: str | None,
    fit: str = "straight",
    rise: str = "mid",
    style: str = "jeans",
    waist: str = "standard",
    cargo: str = "",
) -> list[str]:
    """Jeans or tailored trousers in one of :data:`FITS`, at one of :data:`RISES`.

    ``style`` is ``jeans`` (rivets, coin pocket, J-stitch) or ``tailored``
    (slant pockets, pressed creases). ``waist="elasticated"`` swaps the fly and
    button for a gathered band and a drawstring. ``cargo="yes"`` adds a flapped
    patch pocket on each outer thigh (gen#447: cargo trousers show their pockets).
    """
    bt, bb, wx = RISES[rise]
    if waist == "elasticated":
        bt -= 8
    spec = FITS[fit]
    hem = spec.get("hem_y", HEM_Y)
    oL, iL = _leg_outline(fit, rise)
    oR, iR = mirror(oL), mirror(iL)
    d = (
        f"M{_f(oL[0])} {smooth(oL)} L{_f(iL[-1])} {smooth(iL[::-1])} "
        f"L{_f(iR[0])} {smooth(iR)} L{_f(oR[-1])} {smooth(oR[::-1])} Z"
    )
    out = [_path(d, paint)]

    # Hem: a stitch line (or an ankle cuff) just above the hem of each leg.
    for o, i in ((oL, iL), (oR, iR)):
        if spec.get("cuff"):
            y0 = hem - 18
            cuff = f"M{_x_at(o, y0):.1f},{y0} L{_x_at(i, y0):.1f},{y0} L{i[-1][0]:.1f},{hem} L{o[-1][0]:.1f},{hem} Z"
            out += [_path(cuff, paint, LW_DETAIL), _dark(cuff, 0.15)]
            xs = [_x_at(o, y0), _x_at(i, y0)]
            lo, hi = min(xs), max(xs)
            out.append(
                _line(
                    " ".join(
                        f"M{x:.1f},{y0 - 2} L{x + 1.5:.1f},{y0 - 16}"
                        for x in range(int(lo) + 6, int(hi) - 3, 7)
                    ),
                    1.0,
                    ' stroke-opacity=".6"',
                )
            )
        else:
            y0 = hem - 9
            out.append(_line(f"M{_x_at(o, y0):.1f},{y0} L{_x_at(i, y0):.1f},{y0}", 1.2))

    # Waistband, its loops and closure.
    band = f"M{wx},{bt} L{SIZE - wx},{bt} L{SIZE - wx},{bb} L{wx},{bb} Z"
    out += [_path(band, paint, LW), _dark(band, 0.16)]
    if waist == "elasticated":
        out.append(
            _line(
                " ".join(
                    f"M{x},{bt + 4} L{x + 2},{bb - 4}" for x in range(wx + 6, SIZE - wx - 4, 6)
                ),
                1.0,
                ' stroke-opacity=".55"',
            )
        )
        cy = (bt + bb) / 2
        out += [
            _line(
                f"M196,{cy} Q186,{bb + 30} 178,{bb + 52} M204,{cy} Q214,{bb + 30} 222,{bb + 52}",
                2.4,
            ),
            f'<circle cx="178" cy="{bb + 54}" r="3.5" fill="#ffffff" stroke="{INK}" stroke-width="1.2"/>',
            f'<circle cx="222" cy="{bb + 54}" r="3.5" fill="#ffffff" stroke="{INK}" stroke-width="1.2"/>',
            _line(f"M200,{bb} L200,{CROTCH_Y - 4}", 1.2, ' stroke-opacity=".6"'),
        ]
    else:
        fly = bb + (CROTCH_Y - bb) * 0.7
        out += [
            _line(f"M200,{bb} L200,{CROTCH_Y - 2}"),
            _line(f"M209,{bb} L209,{fly - 10:.1f} Q209,{fly:.1f} 200,{fly + 5:.1f}", 1.2),
            *[
                f'<rect x="{x - 3}" y="{bt - 3}" width="6" height="{bb - bt + 8}" fill="none" stroke="{INK}" stroke-width="1.2"/>'
                for x in (wx + 20, SIZE - wx - 20)
            ],
        ]
        btn = "#d6b56a" if style == "jeans" else _shade(fill.base, 0.45)
        out.append(
            f'<circle cx="200" cy="{(bt + bb) / 2:g}" r="4.5" fill="{btn}" stroke="{INK}" stroke-width="1.2"/>'
        )

    # Pockets.
    py = bb + 34
    for side in (1, -1):

        def X(x: float, s: int = side) -> float:
            return x if s == 1 else SIZE - x

        ox = _x_at(oL, py)
        if style == "jeans":
            out.append(
                _line(f"M{X(wx + 36):.1f},{bb} Q{X(wx + 32):.1f},{py - 4} {X(ox + 1):.1f},{py}")
            )
            out.append(
                f'<circle cx="{X(ox + 4):.1f}" cy="{py - 2}" r="2.2" fill="#d6b56a" stroke="{INK}" stroke-width=".8"/>'
            )
        else:
            out.append(_line(f"M{X(wx + 26):.1f},{bb} L{X(ox + 2):.1f},{py + 12}"))
    if style == "jeans" and waist != "elasticated":
        cx = SIZE - wx - 44
        out.append(_line(f"M{cx},{bb} L{cx},{bb + 20} L{cx + 20},{bb + 20} L{cx + 20},{bb}", 1.0))

    # Fit cues: pleats (carrot), a pressed crease (tailored), a curved
    # front seam (barrel), drape folds (balloon).
    if cargo == "yes":
        out += _cargo_pockets(oL)
    if spec.get("pleats"):
        for x in (wx + 30, wx + 42):
            out.append(
                _line(
                    f"M{x},{bb} L{x - 2},{bb + 40} M{SIZE - x},{bb} L{SIZE - x + 2},{bb + 40}", 1.4
                )
            )
    if style == "tailored" or fit == "barrel":
        mid = [
            ((a[0] + b[0]) / 2, a[1]) for a, b in zip(oL[-4:], iL[-4:], strict=True)
        ]  # thigh, knee, calf, hem
        top = (_x_at(oL, bb + 40) / 2 + 100, bb + 40)
        for pts in ([top, *mid], mirror([top, *mid])):
            dash = ' stroke-dasharray="5 4"' if fit == "barrel" else ' stroke-opacity=".5"'
            out.append(_line(f"M{_f(pts[0])} {smooth(pts)}", 1.4, dash))
    if fit == "balloon":
        for x0 in (136, 166):
            fold = [(x0, 200), (x0 - 12, 260), (x0 + 2, 318)]
            for pts in (fold, mirror(fold)):
                out.append(_line(f"M{_f(pts[0])} {smooth(pts)}", 1.2, ' stroke-opacity=".5"'))
    return out


def _cargo_pockets(outer: list[Pt]) -> list[str]:
    """A flapped patch pocket on each outer thigh, the lower-body kit's own ``cargo-pocket``."""
    from kit_lowerbody import _cargo_pocket  # deferred: kit_lowerbody imports this module

    top = 214
    return [_cargo_pocket(side, _x_at(outer, top), top, 34, 58) for side in (1, -1)]


def _polo_collar(paint: str) -> list[str]:
    """A polo's folded collar, its placket and its two buttons."""
    flap = "M172,58 L202,104 L184,120 L150,84 Z"
    placket = "M193,104 L207,104 L207,196 L193,196 Z"
    return [
        _path(placket, paint, LW_DETAIL),
        _dark(placket, 0.1),
        *[
            f'<circle cx="200" cy="{y}" r="3.6" fill="#ffffff" stroke="{INK}" stroke-width="1.2"/>'
            for y in (128, 160)
        ],
        *[_path(f, paint, LW_DETAIL) for f in (flap, _mirror_path(flap))],
        _dark(flap, 0.12),
        _dark(_mirror_path(flap), 0.12),
    ]


def _mirror_path(d: str) -> str:
    """The absolute ``M/L ... Z`` path ``d`` reflected about the sheet's center line."""
    pts = [tuple(map(float, p.strip("MLZ ").split(","))) for p in d.split() if "," in p]
    return _poly([(SIZE - x, y) for x, y in pts])


def shirt_dress(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A shirt dress: a pointed collar, short sleeves, a buttoned placket to the hem and a belt at
    the waist (gen#447: it is not the strappy sundress ``dress`` draws)."""
    sleeve = "M158,72 L116,98 L100,146 L136,160 L152,130 Z"
    body = "M158,66 L242,66 L252,172 L306,358 Q200,376 94,358 L148,172 Z"
    collar = "M170,52 L200,100 L182,112 L152,76 Z"
    belt = "M150,172 L250,172 L252,192 L148,192 Z"
    return [
        _path(sleeve, paint),
        _path(_mirror_path(sleeve), paint),
        _path(body, paint),
        _path(collar, paint, LW_DETAIL),
        _path(_mirror_path(collar), paint, LW_DETAIL),
        _dark(collar, 0.12),
        _dark(_mirror_path(collar), 0.12),
        _line("M200,100 L200,364"),
        *[
            f'<circle cx="200" cy="{y}" r="3.6" fill="#ffffff" stroke="{INK}" stroke-width="1.2"/>'
            for y in (122, 150, 214, 250, 286, 322)
        ],
        _path(belt, _shade(fill.base, 0.2), LW_DETAIL),
        f'<rect x="188" y="170" width="24" height="24" rx="3" fill="none" stroke="{INK}" stroke-width="2"/>',
        _line("M96,350 Q200,370 304,350", 1.2, ' stroke-dasharray="4 3"'),
    ]


def _fit_alias(fit: str):
    def draw(paint: str, fill: Fill, label: str | None, **params) -> list[str]:
        return trousers(paint, fill, label, fit=fit, **params)

    return draw


# --------------------------------------------------------------------------
# Tops
# --------------------------------------------------------------------------

SHOULDER: Pt = (124, 88)
UNDERARM: Pt = (112, 164)
HEM_L: Pt = (110, 348)

#: neckline -> (left neck point, front cut from the right neck point back to
#: the left one, rib band drawn just outside the cut)
NECKLINES = {
    "crew": ((168, 72), "Q200,108 168,72", "M161,76 Q200,120 239,76"),
    "v_neck": ((170, 72), "L200,148 L170,72", "M162,76 L200,162 L238,76"),
    "boat": ((144, 80), "Q200,98 144,80", "M138,87 Q200,108 262,87"),
    "scoop": ((160, 72), "C240,166 160,166 160,72", "M152,76 C152,180 248,180 248,76"),
    "square": ((156, 72), "L244,130 L156,130 L156,72", "M146,74 L146,142 L254,142 L254,74"),
    "roll_neck": ((172, 76), "Q200,88 172,76", ""),
    # A polo's opening: a short placket slit under the collar.
    "polo": ((176, 72), "L200,112 L176,72", "M170,76 L200,124 L230,76"),
}
#: Deeper cuts a cardigan opens to.
CARDIGAN_NECKS = {
    "v_neck": ((170, 72), "L200,196 L170,72", "M162,76 L200,210 L238,76"),
}

#: sleeve -> polygon of the LEFT sleeve: shoulder, cuff outer, cuff inner, underarm
SLEEVES = {
    "short": [SHOULDER, (68, 142), (96, 176), (112, 160)],
    "three_quarter": [SHOULDER, (86, 114), (68, 262), (104, 268), (114, 170)],
    "long": [SHOULDER, (84, 114), (60, 330), (98, 336), (114, 170)],
}


def _cuff(poly: list[Pt], depth: float) -> list[Pt]:
    """The band at a sleeve's end, ``depth`` of the way back up the sleeve."""
    if len(poly) == 4:  # short: the shoulder is the top of the outer edge
        o_top, o_end, i_end, i_top = poly
    else:
        _, o_top, o_end, i_end, i_top = poly
    return [_lerp(o_end, o_top, depth), o_end, i_end, _lerp(i_end, i_top, depth)]


def _poly(points: list[Pt]) -> str:
    return "M" + " L".join(_f(p) for p in points) + " Z"


def top(
    paint: str,
    fill: Fill,
    label: str | None,
    neckline: str = "crew",
    sleeve: str = "short",
    kind: str = "tee",
) -> list[str]:
    """A tee, jumper or cardigan with a visible neckline and sleeve length.

    ``neckline`` is one of :data:`NECKLINES`; ``sleeve`` is ``sleeveless``,
    ``short``, ``three_quarter`` or ``long``; ``kind`` is ``tee``, ``jumper``,
    ``cardigan`` or ``polo`` (a folded collar over a two-button placket, gen#447).
    """
    necks = CARDIGAN_NECKS if kind == "cardigan" and neckline in CARDIGAN_NECKS else NECKLINES
    (nx, ny), cut, band = necks[neckline]
    knit = kind in ("jumper", "cardigan")
    out: list[str] = []

    # Sleeves sit behind the body.
    if sleeve != "sleeveless":
        poly = SLEEVES[sleeve]
        for pts in (poly, mirror(poly)):
            out.append(_path(_poly(pts), paint))
            cuff = _cuff(pts, 0.1 if sleeve == "long" else 0.16)
            if knit or sleeve == "long":
                out += [_path(_poly(cuff), paint, LW_DETAIL), _dark(_poly(cuff), 0.12)]
                if knit:
                    ribs = " ".join(
                        f"M{_f(_lerp(cuff[0], cuff[3], t))} L{_f(_lerp(cuff[1], cuff[2], t))}"
                        for t in (0.2, 0.4, 0.6, 0.8)
                    )
                    out.append(_line(ribs, 1.0, ' stroke-opacity=".5"'))
            else:
                out.append(_line(f"M{_f(cuff[0])} L{_f(cuff[3])}", 1.2, ' stroke-dasharray="4 3"'))

    # Body: left neck point, shoulder, armhole, side, hem, and back up.
    sx, sy = SHOULDER
    ux, uy = UNDERARM
    hx, hy = HEM_L
    if sleeve == "sleeveless":
        sx, sy = (146, 82)
        arm_l = f"L{sx},{sy} Q{sx - 4},{uy - 14} {ux - 2},{uy + 2}"
        arm_r = f"L{SIZE - ux + 2},{uy + 2} Q{SIZE - sx + 4},{uy - 14} {SIZE - sx},{sy}"
    else:
        arm_l = f"L{sx},{sy} L{ux},{uy}"
        arm_r = f"L{SIZE - ux},{uy} L{SIZE - sx},{sy}"
    body = f"M{nx},{ny} {arm_l} L{hx},{hy} L{SIZE - hx},{hy} {arm_r} L{SIZE - nx},{ny} {cut} Z"
    out.append(_path(body, paint))
    if sleeve == "sleeveless":
        out.append(
            _line(
                f"M{sx + 7},{sy + 2} Q{sx + 3},{uy - 8} {ux + 6},{uy + 4}",
                1.2,
                ' stroke-dasharray="4 3"',
            )
        )
        out.append(
            _line(
                f"M{SIZE - sx - 7},{sy + 2} Q{SIZE - sx - 3},{uy - 8} {SIZE - ux - 6},{uy + 4}",
                1.2,
                ' stroke-dasharray="4 3"',
            )
        )

    # The garment's inside, seen through the neckline, and its rib band.
    if neckline != "roll_neck":
        inside = f"M{nx},{ny} Q200,{ny + 10} {SIZE - nx},{ny} {cut} Z"
        out.append(_path(inside, _inside_color(fill), LW_DETAIL))
        if neckline == "square":
            # A solid binding round the square cut, so its corners read even
            # on a busy print: the print's own accent color, or the base on a solid.
            trim = fill.base if fill.pattern == "solid" else fill.accent
            binding = f"{band} L{SIZE - nx},{ny} {cut} Z"
            out += [_path(binding, trim, LW_DETAIL), _dark(binding, 0.08)]
        else:
            out.append(_line(band, 2.0 if knit else 1.4))
    else:
        collar = "M168,84 L170,30 Q200,22 230,30 L232,84 Q200,94 168,84 Z"
        out += [
            _path(collar, paint),
            _dark("M170,30 Q200,22 230,30 L231,54 Q200,46 169,54 Z", 0.12),
            _line("M169,54 Q200,46 231,54", 1.6),
            _line(
                " ".join(
                    f"M{x},{58 + abs(x - 200) * 0.05:.1f} L{x},{84 + (2 if x == 200 else 0)}"
                    for x in range(176, 228, 8)
                ),
                1.0,
                ' stroke-opacity=".45"',
            ),
        ]

    if kind == "polo":
        out += _polo_collar(paint)

    # Hem: a stitched hem on a tee, a rib band on a knit.
    if knit:
        rib = f"M{hx + 1},{hy - 26} L{SIZE - hx - 1},{hy - 26} L{SIZE - hx},{hy} L{hx},{hy} Z"
        out += [_path(rib, paint, LW_DETAIL), _dark(rib, 0.12)]
        out.append(
            _line(
                " ".join(f"M{x},{hy - 23} L{x},{hy - 3}" for x in range(hx + 8, SIZE - hx - 4, 8)),
                1.0,
                ' stroke-opacity=".45"',
            )
        )
    else:
        out.append(_line(f"M{hx},{hy - 10} L{SIZE - hx},{hy - 10}", 1.2, ' stroke-dasharray="4 3"'))

    if kind == "cardigan":
        top_y = {"v_neck": 196, "crew": 104}.get(neckline, 110)
        out += [
            _path(f"M193,{top_y} L193,{hy} L207,{hy} L207,{top_y} Z", paint, LW_DETAIL),
            _dark(f"M193,{top_y} L193,{hy} L207,{hy} L207,{top_y} Z", 0.1),
            *[
                f'<circle cx="200" cy="{y:.0f}" r="4.6" fill="{_tint(fill.accent, 0.1)}" stroke="{INK}" stroke-width="1.2"/>'
                for y in [top_y + 14 + k * (hy - 40 - top_y - 14) / 4 for k in range(5)]
            ],
            *[
                _path(_poly(p), paint, LW_DETAIL)
                for p in (
                    [(128, 250), (172, 250), (172, 296), (128, 296)],
                    mirror([(128, 250), (172, 250), (172, 296), (128, 296)]),
                )
            ],
        ]
    return out


register(
    {
        "trousers": trousers,
        "top": top,
        "shirt_dress": shirt_dress,
        "jeans_straight": _fit_alias("straight"),
        "jeans_bootcut": _fit_alias("bootcut"),
    },
    {"top": 6},
)

import kit_outerwear  # noqa: E402,F401 -- registers bomber_jacket and puffer_jacket (gen#447)
