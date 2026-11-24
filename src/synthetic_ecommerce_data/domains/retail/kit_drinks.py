"""The drinks a grocer sells, each drawn as its real container (gen#1127).

Every drink used to be one of two shapes, ``kit.bottle`` or ``kit.tin``, painted in its line's
color and shrunk by :mod:`pack_scale`, so a half bottle of wine stood small in a mostly empty
frame. This module draws a drink as the container it is sold in, at that container's real
proportions.

==============  ===================================================  ==================
shape           draws                                                params
==============  ===================================================  ==================
wine_bottle     a wine bottle of its style: Bordeaux (high            wine, pack_size,
                shoulders: red, port, sherry, vermouth), Burgundy     largest
                (sloping shoulders: white, rosé) or a heavy
                sparkling bottle with a mushroom cork under a wire
                cage (sparkling, Champagne). A foil capsule, the
                glass of the style, the wine's color through it,
                a front label, a highlight and a ground shadow.
==============  ===================================================  ==================

THE SIZE. Each SKU draws its own ``pack_size`` (a per-SKU drawing param, as a pizza's is), at the
real height and diameter of that size of bottle (:data:`DIMENSIONS`), so a magnum is stouter
than a 750ml and a half bottle slimmer. The line's ``largest`` size spans :data:`FULL_SHARE` of
the product area's height (the house style's 334 high box). A smaller size steps down by its
real height ratio to the largest, compressed by :data:`STEP_POWER` and never below
:data:`MIN_SHARE` of the largest's height. A single image is seen alone, so the step only has to
read; a real step (a 375ml is 0.7 of a magnum's height) would leave the half bottle in a mostly
empty frame again. No :mod:`pack_scale` factor applies on top (``pack_scale.SELF_SIZED``).

THE COLOR. The record's fill is the wine's own color (a Malbec's purple, a Fino's straw). It is
drawn below the fill line through the glass: :func:`through_glass` mixes it with the glass's
color by how much the glass hides (:data:`GLASSES`), so a white wine in clear flint glass shows
its straw, and a red in green glass shows dark.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import functools
import re
from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail.house_styles import PRODUCT_SPAN, PRODUCT_TOP
from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _mix,
    _panel,
    _path,
    _rim,
    _shade,
    register,
)

#: The bottle's foot: every size of a line stands on this baseline, on the sheet's center line.
BASE_Y = PRODUCT_TOP + PRODUCT_SPAN - 8
CX = 200.0
#: The share of the product area's height the line's largest size spans.
FULL_SHARE = 0.97
#: The least share of the largest's height a smaller size is drawn at.
MIN_SHARE = 0.8
#: How much of the real height step between two sizes is drawn: the real ratio to this power.
STEP_POWER = 0.3


@dataclass(frozen=True)
class Form:
    """A bottle's outline, as its radius (a share of the body's) at each share of its height.

    ``profile`` is ``(t, r)`` points from the foot (t 0) to the lip (t 1), joined smoothly.
    ``fill_line`` is where the wine stands, ``capsule`` where the foil starts, and ``label`` the
    front label's bottom and top."""

    profile: tuple[tuple[float, float], ...]
    fill_line: float
    capsule: float
    label: tuple[float, float]
    cork: float = (
        0.0  # the share of the height a sparkling bottle's mushroom cork stands above its lip
    )


FORMS = {
    # high, square shoulders and a straight body (a claret)
    "bordeaux": Form(
        (
            (0, 0.9),
            (0.015, 1),
            (0.64, 1),
            (0.675, 0.92),
            (0.705, 0.66),
            (0.735, 0.44),
            (0.76, 0.4),
            (0.965, 0.37),
            (0.97, 0.42),
            (1, 0.42),
        ),
        0.79,
        0.84,
        (0.12, 0.5),
    ),
    # long sloping shoulders running into the neck
    "burgundy": Form(
        (
            (0, 0.9),
            (0.015, 1),
            (0.47, 1),
            (0.56, 0.95),
            (0.65, 0.78),
            (0.73, 0.55),
            (0.8, 0.4),
            (0.965, 0.36),
            (0.97, 0.41),
            (1, 0.41),
        ),
        0.8,
        0.84,
        (0.1, 0.43),
    ),
    # a heavy sparkling bottle: sloping shoulders, a lip bead, a cork above
    "sparkling": Form(
        (
            (0, 0.9),
            (0.022, 1),
            (0.525, 1),
            (0.623, 0.95),
            (0.721, 0.76),
            (0.809, 0.52),
            (0.874, 0.37),
            (0.962, 0.34),
            (0.967, 0.4),
            (0.995, 0.4),
            (1, 0.34),
        ),
        0.8,
        0.765,
        (0.11, 0.46),
        0.085,
    ),
}

#: The bottle's real (height, diameter) in mm by content in ml, per form; a size between two is
#: drawn between them (a cube root of the content, as real bottles grow).
DIMENSIONS = {
    "bordeaux": {
        200: (190, 52),
        375: (250, 61),
        500: (270, 66),
        750: (300, 77),
        1000: (330, 86),
        1500: (355, 104),
    },
    "burgundy": {
        200: (190, 56),
        375: (240, 66),
        500: (265, 70),
        750: (295, 82),
        1000: (325, 90),
        1500: (345, 112),
    },
    "sparkling": {
        200: (195, 58),
        375: (245, 72),
        500: (270, 78),
        750: (305, 89),
        1000: (330, 96),
        1500: (375, 115),
    },
}

#: Glass -> (its color, how much of the wine's color it hides).
GLASSES = {
    "flint": ("#e6ece4", 0.15),
    "pale_green": ("#a9c19a", 0.3),
    "green": ("#2e4a2c", 0.45),
    "dark": ("#1f271c", 0.55),
}


@dataclass(frozen=True)
class Style:
    """A wine style's bottle: its form, its glass and its capsule's foil."""

    form: str
    glass: str
    foil: str


STYLES = {
    "red": Style("bordeaux", "green", "#7a1f2a"),
    "white": Style("burgundy", "flint", "#c9a646"),
    "rose": Style("burgundy", "flint", "#d98a9a"),
    "sparkling": Style("sparkling", "pale_green", "#b9bfc4"),
    "champagne": Style("sparkling", "dark", "#c8a447"),
    "port": Style("bordeaux", "dark", "#5a1a22"),
    "sherry": Style("bordeaux", "green", "#2a2a2a"),
    "vermouth": Style("bordeaux", "flint", "#b03a2e"),
}

_ML = re.compile(r"^([\d.]+) ?(ml|L|cl)$")
_ML_PER = {"ml": 1.0, "cl": 10.0, "L": 1000.0}


def millilitres(pack_size: str) -> float:
    """``"750ml"`` -> 750, ``"1.5L"`` -> 1500."""
    m = _ML.match(pack_size.strip())
    if m is None:
        raise ValueError(f"a wine bottle of {pack_size!r} names no volume")
    return float(m[1]) * _ML_PER[m[2]]


def pack_of(pack_size: str, net_volume_ml: str = "") -> str:
    """The pack to draw: a SKU's ``net_volume_ml`` ("330.0") where its row sells sizes by volume
    (a hand-written row has no ``pack_size``), else ``pack_size``."""
    return f"{float(net_volume_ml):g}ml" if net_volume_ml else pack_size


def dimensions(form: str, ml: float) -> tuple[float, float]:
    """The real (height, diameter) in mm of a ``form`` bottle holding ``ml``."""
    table = DIMENSIONS[form]
    if ml in table:
        return table[ml]
    near = min(table, key=lambda k: abs(k - ml))
    k = (ml / near) ** (1 / 3)
    h, d = table[near]
    return h * k, d * k


def through_glass(wine: str, glass: str) -> str:
    """The wine's color ``wine`` as it shows through ``glass`` (:data:`GLASSES`)."""
    tint, hides = GLASSES[glass]
    return _mix(wine, tint, hides)


def drawn_height(form: str, pack_size: str, largest: str) -> float:
    """The bottle's drawn height in kit units: the largest size at :data:`FULL_SHARE` of the
    product area's height, a smaller one its real height step compressed (:data:`STEP_POWER`),
    never below :data:`MIN_SHARE` of the largest's."""
    full = FULL_SHARE * PRODUCT_SPAN
    own = dimensions(form, millilitres(pack_size))[0]
    top = dimensions(form, millilitres(largest))[0]
    ratio = min(1.0, own / top)
    return full * max(MIN_SHARE, ratio**STEP_POWER)


@functools.cache
def _slopes(pts: tuple[tuple[float, float], ...]) -> list[float]:
    """The profile's slope at each point, for a monotone cubic (Fritsch-Carlson): flat where the
    outline turns or runs flat, else the weighted harmonic mean of its two sides' slopes. A
    shoulder of several points is then one smooth curve, never overshooting a point."""
    hs = [t1 - t0 for (t0, _), (t1, _) in zip(pts, pts[1:], strict=False)]
    ds = [
        (r1 - r0) / h
        for ((_, r0), (_, r1)), h in zip(zip(pts, pts[1:], strict=False), hs, strict=True)
    ]
    m = [ds[0], *([0.0] * (len(pts) - 2)), ds[-1]]
    for k in range(1, len(pts) - 1):
        if ds[k - 1] * ds[k] > 0:
            w1, w2 = 2 * hs[k] + hs[k - 1], hs[k] + 2 * hs[k - 1]
            m[k] = (w1 + w2) / (w1 / ds[k - 1] + w2 / ds[k])
    return m


def _radius(form: Form, t: float) -> float:
    """The profile's radius at ``t``: a monotone cubic through its points (:func:`_slopes`)."""
    pts = form.profile
    m = _slopes(pts)
    for k, ((t0, r0), (t1, r1)) in enumerate(zip(pts, pts[1:], strict=False)):
        if t0 <= t <= t1:
            h = t1 - t0
            u = (t - t0) / h
            return (
                (2 * u**3 - 3 * u**2 + 1) * r0
                + (u**3 - 2 * u**2 + u) * h * m[k]
                + (-2 * u**3 + 3 * u**2) * r1
                + (u**3 - u**2) * h * m[k + 1]
            )
    return pts[-1][1]


def _side(form: Form, t_from: float, t_to: float, step: float = 0.005) -> list[float]:
    ts = [t_from]
    while ts[-1] + step < t_to:
        ts.append(ts[-1] + step)
    ts.append(t_to)
    # the profile's own points, so a shoulder's corner is drawn where it is
    ts = sorted({*ts, *(t for t, _ in form.profile if t_from < t < t_to)})
    return ts


def _outline(
    form: Form, h: float, half: float, t_from: float, t_to: float, grow: float = 0.0
) -> str:
    """The closed outline of the bottle between heights ``t_from`` and ``t_to``: up the right
    side, back down the left. ``grow`` widens it (the foil stands proud of the glass)."""
    ts = _side(form, t_from, t_to)
    right = [(CX + (half * _radius(form, t)) + grow, BASE_Y - t * h) for t in ts]
    left = [(2 * CX - x, y) for x, y in reversed(right)]
    pts = right + left
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"


def _cork(form: Form, h: float, half: float, foil: str) -> list[str]:
    """A sparkling bottle's mushroom cork under its wire cage, standing on the lip."""
    lip = BASE_Y - h
    top = lip - form.cork * h
    r = half * 0.36
    cork = f"M{CX - r * 0.9:.1f},{lip:.1f} L{CX - r:.1f},{top + r * 0.6:.1f} Q{CX - r:.1f},{top:.1f} {CX:.1f},{top:.1f} Q{CX + r:.1f},{top:.1f} {CX + r:.1f},{top + r * 0.6:.1f} L{CX + r * 0.9:.1f},{lip:.1f} Z"
    cap = (top + lip) / 2
    wires = f"M{CX - r * 0.95:.1f},{cap:.1f} L{CX + r * 0.95:.1f},{cap:.1f} M{CX - r * 0.6:.1f},{top + 2:.1f} L{CX - r * 0.8:.1f},{lip:.1f} M{CX + r * 0.6:.1f},{top + 2:.1f} L{CX + r * 0.8:.1f},{lip:.1f}"
    return [
        _path(cork, "#d9c49a", LW, ' class="bottle"'),
        f'<circle cx="{CX:g}" cy="{top + r * 0.35:.1f}" r="{r * 0.32:.1f}" fill="{foil}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _line(wires, 1.1, ' stroke-opacity=".85"'),
    ]


def wine_bottle(paint: str, fill: Fill, label: str | None, wine: str = "red", pack_size: str = "750ml",
                largest: str = "") -> list[str]:  # fmt: skip
    """A bottle of ``wine`` (a :data:`STYLES` key) holding ``pack_size``, in a line whose largest
    size is ``largest`` (the SKU's own size when empty). ``fill.base`` is the wine's color."""
    if wine not in STYLES:
        raise ValueError(f"no wine style {wine!r}; known: {sorted(STYLES)}")
    style = STYLES[wine]
    form = FORMS[style.form]
    h_mm, d_mm = dimensions(style.form, millilitres(pack_size))
    h = drawn_height(style.form, pack_size, largest or pack_size)
    glass_h = h / (1 + form.cork)  # the cork stands above the glass
    half = glass_h * d_mm / h_mm / 2
    glass, _ = GLASSES[style.glass]
    wine_color = through_glass(fill.base, style.glass)
    lip = form.profile[-1][0]
    lo, hi = form.label
    label_y, label_top = BASE_Y - hi * glass_h, BASE_Y - lo * glass_h
    out = [
        f'<ellipse class="ground" cx="{CX:g}" cy="{BASE_Y + 1:g}" rx="{half * 1.5:.1f}" ry="{min(6.0, max(3.0, half * 0.12)):.1f}" fill="#000000" fill-opacity=".12"/>',
        _path(_outline(form, glass_h, half, 0, lip), glass, LW, ' class="bottle"'),
        _path(
            _outline(form, glass_h, half, 0, form.fill_line),
            wine_color,
            LW_DETAIL,
            ' class="wine"',
            wine_color,
        ),
        _line(
            f"M{CX - half * _radius(form, form.fill_line):.1f},{BASE_Y - form.fill_line * glass_h:.1f} L{CX + half * _radius(form, form.fill_line):.1f},{BASE_Y - form.fill_line * glass_h:.1f}",
            1.2,
            ' stroke-opacity=".6"',
        ),
    ]
    width = 1.72 * half
    body_top = max(t for t, r in form.profile if r == 1)
    out += [
        _highlight(
            f"M{CX - half * 0.62:.1f},{BASE_Y - 0.06 * glass_h:.1f} L{CX - half * 0.62:.1f},{BASE_Y - (body_top - 0.02) * glass_h:.1f}",
            max(3.0, half * 0.1),
            0.45,
        ),
        _highlight(
            f"M{CX - half * 0.3:.1f},{BASE_Y - (body_top + 0.06) * glass_h:.1f} L{CX - half * 0.24:.1f},{BASE_Y - (form.capsule - 0.02) * glass_h:.1f}",
            2.2,
            0.35,
        ),
        _line(
            f"M{CX + half * 0.7:.1f},{BASE_Y - 0.06 * glass_h:.1f} L{CX + half * 0.7:.1f},{BASE_Y - (body_top - 0.02) * glass_h:.1f}",
            max(3.0, half * 0.12),
            ' stroke-opacity=".18" class="shade"',
            _shade(glass, 0.6),
        ),
        *_panel(CX - width / 2, label_y, width, label_top - label_y, label, 30, rim=_rim(half)),
        _path(
            _outline(form, glass_h, half, form.capsule, lip, 1.2),
            style.foil,
            LW,
            ' class="capsule"',
        ),
        _line(
            f"M{CX - half * _radius(form, form.capsule + 0.02) - 1:.1f},{BASE_Y - (form.capsule + 0.02) * glass_h:.1f} L{CX + half * _radius(form, form.capsule + 0.02) + 1:.1f},{BASE_Y - (form.capsule + 0.02) * glass_h:.1f}",
            1.0,
            ' stroke-opacity=".6"',
        ),
    ]
    if form.cork:
        out += _cork(form, glass_h, half, style.foil)
    return out


register({"wine_bottle": wine_bottle})
