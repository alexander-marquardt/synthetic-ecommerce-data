"""A soft drink drawn as its real can or bottle, a multipack as its cans (gen#1127, slice 2).

Every soft drink used to draw the generic ``kit.bottle``, shrunk by :mod:`pack_scale`, and a
6 x 330ml was six copies of that bottle. ``soft_drink`` draws the container each pack is sold in,
at its real proportions, from the SKU's own ``pack_size`` and ``flavor`` (per-SKU drawing params):

==================  =========================================================================
pack                draws
==================  =========================================================================
500ml, 1L, 1.5L     a clear PET bottle: a screw cap, a neck ring, a waist rib, a petaloid
                    foot, the drink in its flavor's color through the plastic, a wrap label
330ml (``small``    a clear glass bottle with a crown cap (a brewed ginger beer), or
glass or can)       a ring-pull can
N x 330ml           N ring-pull cans in two rows under a card carrier, so the pack draws its
                    count (``pack_copies.SELF_DRAWN_SHAPES``)
==================  =========================================================================

THE SIZE. A bottle follows the wine bottle's rule (:mod:`kit_drinks`): the line's ``largest``
single spans ``FULL_SHARE`` of the product area's height and a smaller one steps down by its
real height ratio to the power ``STEP_POWER``, never below ``MIN_SHARE`` of it. A can is short
and wide, so it is drawn at the full height wherever it stands, and a multipack's cans fill the
area's width: each paints half the product area or more. No ``pack_scale`` factor applies.

THE COLOR. :data:`LIQUIDS` is each flavor's drink as it is poured (a cola dark, a cloudy
lemonade pale). A bottle shows it through its clear wall (:data:`CLEAR`); a can is printed in it.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math
import re

from synthetic_ecommerce_data.domains.retail.house_styles import PRODUCT_SPAN, TURN_AREA
from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    RIM_TILT,
    Fill,
    _highlight,
    _line,
    _mix,
    _panel,
    _path,
    _rim,
    _shade,
    _word,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_drinks import (
    BASE_Y,
    CX,
    FULL_SHARE,
    MIN_SHARE,
    STEP_POWER,
    Form,
    _outline,
    _radius,
    millilitres,
    pack_of,
)

#: Each flavor's drink as it is poured: shown through a bottle's wall and printed on its can.
LIQUIDS = {
    "Cola": "#3b1c10",
    "Orange Crush": "#f08a24",
    "Cloudy Lemonade": "#f4ecb4",
    "Ginger Beer": "#d9b26a",
    "Fiery Ginger Beer": "#c47f22",
    "Root Beer": "#4a2414",
    "Elderflower Presse": "#e9edc4",
    "Sparkling Mint Water": "#d4eedf",
    "Sparkling Lemon Water": "#f1f0d2",
    "Sparkling Lime Water": "#dfeccb",
}
#: A clear wall's tint, and how much of the drink's color it hides.
CLEAR, CLEAR_HIDES = "#eef3f5", 0.12
#: The silver of a can's lid, neck and foot, and of a ring-pull.
SILVER = "#c9ced3"

FORMS = {
    # a PET bottle: a petaloid foot, a waist rib, a rounded shoulder, a neck ring under the cap
    "pet": Form(
        (
            (0, 0.8),
            (0.03, 1),
            (0.3, 1),
            (0.325, 0.94),
            (0.35, 1),
            (0.58, 1),
            (0.68, 0.86),
            (0.77, 0.56),
            (0.83, 0.38),
            (0.86, 0.36),
            (0.865, 0.44),
            (0.875, 0.44),
            (0.88, 0.36),
            (0.9, 0.36),
        ),
        0.76,
        0.9,  # where the screw cap starts (it stands to the top, t 1)
        (0.38, 0.56),
    ),
    # a glass soda bottle: a short body, long tapering shoulders, a crown cap on a bead
    "glass": Form(
        (
            (0, 0.9),
            (0.02, 1),
            (0.48, 1),
            (0.6, 0.86),
            (0.72, 0.54),
            (0.8, 0.38),
            (0.93, 0.35),
            (0.935, 0.42),
            (0.955, 0.42),
            (0.96, 0.36),
        ),
        0.82,
        0.96,  # where the crown cap starts
        (0.12, 0.42),
    ),
}

#: The container's real (height, diameter) in mm by content in ml.
DIMENSIONS = {
    "pet": {330: (175, 58), 500: (215, 65), 1000: (285, 80), 1500: (315, 92), 2000: (335, 105)},
    "glass": {275: (210, 60), 330: (225, 62), 750: (290, 80)},
    "can": {250: (134, 53), 330: (115, 66), 440: (148, 66), 500: (168, 66)},
}

_MULTI = re.compile(r"^(\d+) x (.+)$")
#: A multipack's rear row stands this share of a can's height above the front row, and half a
#: can to the right, so each rear can shows between two front ones.
REAR_RISE = 0.32
#: The card carrier's top, as a share of the front cans' height from their foot.
CARRIER = 0.42


def dimensions(form: str, ml: float) -> tuple[float, float]:
    """The real (height, diameter) in mm of a ``form`` container holding ``ml``; a size between
    two of :data:`DIMENSIONS` grows from the nearest by the cube root of the content."""
    table = DIMENSIONS[form]
    if ml in table:
        return table[ml]
    near = min(table, key=lambda k: abs(k - ml))
    k = (ml / near) ** (1 / 3)
    h, d = table[near]
    return h * k, d * k


def container(pack_size: str, small: str = "can") -> tuple[str, int, float]:
    """``(form, count, ml)``: what ``pack_size`` is sold in. ``"6 x 330ml"`` is 6 cans; a single
    of 330ml or less is ``small`` (a ``"glass"`` bottle or a ``"can"``); a larger one is PET."""
    m = _MULTI.match(pack_size.strip())
    if m:
        return "can", int(m[1]), millilitres(m[2])
    ml = millilitres(pack_size)
    return (small if ml <= 330 else "pet"), 1, ml


def through_clear(liquid: str) -> str:
    """The drink ``liquid`` as it shows through a clear bottle's wall."""
    return _mix(liquid, CLEAR, CLEAR_HIDES)


def drawn_height(pack_size: str, largest: str, small: str = "can") -> float:
    """The container's drawn height in kit units: a bottle against the line's ``largest`` single
    as a wine bottle is (:func:`kit_drinks.drawn_height`), a can always at the full height."""
    full = FULL_SHARE * PRODUCT_SPAN
    form, _, ml = container(pack_size, small)
    if form == "can":
        return full
    top_form, _, top_ml = container(largest, small)
    ratio = min(1.0, dimensions(form, ml)[0] / dimensions(top_form, top_ml)[0])
    return full * max(MIN_SHARE, ratio**STEP_POWER)


def _ground(half: float) -> str:
    ry = min(6.0, max(3.0, half * 0.12))
    return f'<ellipse class="ground" cx="{CX:g}" cy="{BASE_Y + 1:g}" rx="{half * 1.5:.1f}" ry="{ry:.1f}" fill="#000000" fill-opacity=".12"/>'


def _ink_on(color: str) -> str:
    """Ink or white, whichever reads on ``color``."""
    r, g, b = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    return INK if 0.299 * r + 0.587 * g + 0.114 * b > 140 else "#ffffff"


def bottle(form_name: str, h: float, d_over_h: float, liquid: str, label: str | None,
           wall: str = CLEAR, hides: float = CLEAR_HIDES, shape: Form | None = None) -> list[str]:  # fmt: skip
    """A PET or glass bottle ``h`` high, the drink below its fill line, its cap on top. ``wall``
    is the glass's tint and ``hides`` how much of the drink's color it hides (a clear wall by
    default; a beer's brown glass, :mod:`kit_beer`); ``shape`` a form not in :data:`FORMS`."""
    form = shape or FORMS[form_name]
    half = h * d_over_h / 2
    top = form.profile[-1][0]
    drink = _mix(liquid, wall, hides)
    lo, hi = form.label
    label_y, label_bot = BASE_Y - hi * h, BASE_Y - lo * h
    body_top = max(t for t, r in form.profile if r == 1)
    out = [
        _ground(half),
        _path(_outline(form, h, half, 0, top), wall, LW, ' class="bottle"'),
        _path(
            _outline(form, h, half, 0, form.fill_line), drink, LW_DETAIL, ' class="drink"', drink
        ),
        _line(
            f"M{CX - half * _radius(form, form.fill_line):.1f},{BASE_Y - form.fill_line * h:.1f} L{CX + half * _radius(form, form.fill_line):.1f},{BASE_Y - form.fill_line * h:.1f}",
            1.2,
            ' stroke-opacity=".6"',
        ),
    ]
    if form_name == "pet":  # the wrap label in the drink's color, the word on a white panel
        band = _mix(liquid, "#ffffff", 0.15)
        out.append(
            _path(
                f"M{CX - half:.1f},{label_y:.1f} L{CX + half:.1f},{label_y:.1f} L{CX + half:.1f},{label_bot:.1f} L{CX - half:.1f},{label_bot:.1f} Z",
                band,
                LW_DETAIL,
                ' class="wrap"',
            )
        )
        out += _panel(CX - half * 0.8, label_y + 4, half * 1.6, label_bot - label_y - 8, label, 30)
        feet = " ".join(
            f"M{CX + half * x:.1f},{BASE_Y:.1f} L{CX + half * x * 1.06:.1f},{BASE_Y - 0.03 * h:.1f}"
            for x in (-0.45, 0.0, 0.45)
        )
        out.append(_line(feet, 1.4, ' stroke-opacity=".5" class="foot"'))
    else:
        out += _panel(
            CX - half * 0.86, label_y, half * 1.72, label_bot - label_y, label, 30, rim=_rim(half)
        )
    out += [
        _highlight(
            f"M{CX - half * 0.62:.1f},{BASE_Y - 0.06 * h:.1f} L{CX - half * 0.62:.1f},{BASE_Y - (body_top - 0.02) * h:.1f}",
            max(3.0, half * 0.1),
            0.45,
        ),
        _line(
            f"M{CX + half * 0.7:.1f},{BASE_Y - 0.06 * h:.1f} L{CX + half * 0.7:.1f},{BASE_Y - (body_top - 0.02) * h:.1f}",
            max(3.0, half * 0.12),
            ' stroke-opacity=".18" class="shade"',
            _shade(wall, 0.6),
        ),
    ]
    return out + _cap(form_name, form, h, half, liquid)


def _cap(form_name: str, form: Form, h: float, half: float, liquid: str) -> list[str]:
    """A PET bottle's ridged screw cap, or a glass bottle's crimped crown cap, on its neck."""
    r = half * _radius(form, form.capsule) * 1.12
    y0, y1 = BASE_Y - h, BASE_Y - (form.capsule - 0.005) * h
    if form_name == "pet":
        cap = _shade(liquid, 0.25) if _ink_on(liquid) == INK else _mix(liquid, "#ffffff", 0.25)
        ridges = " ".join(
            f"M{CX + r * x:.1f},{y0 + 2:.1f} L{CX + r * x:.1f},{y1 - 2:.1f}"
            for x in (-0.6, -0.2, 0.2, 0.6)
        )
        return [
            _path(
                f"M{CX - r:.1f},{y1:.1f} L{CX - r:.1f},{y0 + 2:.1f} Q{CX - r:.1f},{y0:.1f} {CX - r + 2:.1f},{y0:.1f} L{CX + r - 2:.1f},{y0:.1f} Q{CX + r:.1f},{y0:.1f} {CX + r:.1f},{y0 + 2:.1f} L{CX + r:.1f},{y1:.1f} Z",
                cap,
                LW,
                ' class="cap"',
            ),
            _line(ridges, 1.0, ' stroke-opacity=".5"'),
        ]
    n = 7
    crimp = " ".join(
        f"L{CX - r + 2 * r * (i + 0.5) / n:.1f},{y1 + 2.5:.1f} L{CX - r + 2 * r * (i + 1) / n:.1f},{y1:.1f}"
        for i in range(n)
    )
    return [
        _path(
            f"M{CX - r:.1f},{y1:.1f} {crimp} L{CX + r:.1f},{y0 + 2:.1f} L{CX - r:.1f},{y0 + 2:.1f} Z",
            "#c8a447",
            LW,
            ' class="cap"',
        )
    ]


def can(
    cx: float, foot: float, w: float, h: float, livery: str, label: str | None, word: bool = True
) -> list[str]:
    """A ring-pull can ``w`` wide and ``h`` high standing on ``foot`` at ``cx``: a printed
    body in ``livery``, a silver neck, lid and foot, a ring-pull, a highlight and a shade."""
    a = w / 2
    ry = a * RIM_TILT
    lid, lid_a = foot - h + ry, a * 0.88
    neck, chime = lid + 0.07 * h, foot - ry - 0.03 * h
    bot = foot - ry
    side = f"L{cx - a:.1f},{neck:.1f} L{cx - a:.1f},{chime:.1f} L{cx - a * 0.95:.1f},{bot:.1f} Q{cx - a * 0.95:.1f},{foot:.1f} {cx:.1f},{foot:.1f} Q{cx + a * 0.95:.1f},{foot:.1f} {cx + a * 0.95:.1f},{bot:.1f} L{cx + a:.1f},{chime:.1f} L{cx + a:.1f},{neck:.1f}"
    body = f"M{cx - lid_a:.1f},{lid:.1f} {side} L{cx + lid_a:.1f},{lid:.1f} Z"
    printed = f"M{cx - a:.1f},{neck + 3:.1f} L{cx - a:.1f},{chime - 3:.1f} L{cx + a:.1f},{chime - 3:.1f} L{cx + a:.1f},{neck + 3:.1f} Z"
    ink = _ink_on(livery)
    out = [
        _path(body, SILVER, LW, ' class="can"'),
        _path(printed, livery, LW_DETAIL, ' class="livery"'),
        f'<ellipse cx="{cx:.1f}" cy="{lid:.1f}" rx="{lid_a:.1f}" ry="{ry * 0.88:.1f}" fill="{_mix(SILVER, "#ffffff", 0.3)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<ellipse cx="{cx:.1f}" cy="{lid - ry * 0.25:.1f}" rx="{a * 0.2:.1f}" ry="{ry * 0.22:.1f}" fill="{_shade(SILVER, 0.4)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<ellipse class="ring-pull" cx="{cx:.1f}" cy="{lid + ry * 0.3:.1f}" rx="{a * 0.16:.1f}" ry="{ry * 0.2:.1f}" fill="none" stroke="{INK}" stroke-width="{LW_DETAIL * 1.4:.1f}"/>',
    ]
    if word and label:
        out.append(_word(label, cx, (neck + chime) / 2, w * 0.8, w * 0.22, ink))
    out += [
        _highlight(
            f"M{cx - a * 0.6:.1f},{neck + 6:.1f} L{cx - a * 0.6:.1f},{chime - 6:.1f}",
            max(3.0, a * 0.12),
            0.45,
        ),
        _line(
            f"M{cx + a * 0.72:.1f},{neck + 6:.1f} L{cx + a * 0.72:.1f},{chime - 6:.1f}",
            max(3.0, a * 0.14),
            ' stroke-opacity=".2" class="shade"',
            "#000000",
        ),
    ]
    return out


def multipack(n: int, d_over_h: float, livery: str, label: str | None) -> list[str]:
    """``n`` cans in two rows, the rear row raised and set half a can over, the front row in a
    card carrier printed with the label: as wide as the product area holds. Two rows hold the
    packs a grocer sells (4 and 6); a larger pack would draw its cans small."""
    front = math.ceil(n / 2)
    rear = n - front
    across = front + (0.5 if rear else 0)
    tall = FULL_SHARE * PRODUCT_SPAN / (1 + REAR_RISE * bool(rear))  # a can's height that fits
    w = min(FULL_SHARE * (TURN_AREA[2] - TURN_AREA[0]) / across, tall * d_over_h)
    h = w / d_over_h
    out = [_ground(across * w / 2 / 1.4)]  # the shadow's own 1.5 would run past the frame
    left = CX - across * w / 2 + w / 2
    for i in range(rear):  # the rear row first, so the front row stands before it
        out += can(
            left + (i + 0.5) * w, BASE_Y - REAR_RISE * h, w * 0.98, h, livery, None, word=False
        )
    for i in range(front):
        out += can(left + i * w, BASE_Y, w * 0.98, h, livery, label)
    top = BASE_Y - CARRIER * h
    x0, x1 = left - w / 2 - 2, left + (front - 0.5) * w + 2
    card = _mix(livery, "#ffffff", 0.35)
    out.append(
        _path(
            f"M{x0:.1f},{top:.1f} L{x1:.1f},{top:.1f} L{x1:.1f},{BASE_Y - 2:.1f} L{x0:.1f},{BASE_Y - 2:.1f} Z",
            card,
            LW,
            ' class="carrier"',
        )
    )
    out += _panel(
        (x0 + x1) / 2 - w * 0.9,
        top + 6,
        w * 1.8,
        CARRIER * h - 14,
        f"{n} x {label}" if label else f"{n} cans",
        26,
    )
    return out


def soft_drink(paint: str, fill: Fill, label: str | None, flavor: str = "", pack_size: str = "500ml",
               largest: str = "", small: str = "can",
               net_volume_ml: str = "") -> list[str]:  # fmt: skip
    """A ``flavor`` soft drink in its ``pack_size`` container, in a line whose largest single is
    ``largest`` (the SKU's own size when empty). ``small`` is what a 330ml single is sold in,
    ``net_volume_ml`` the pack of a row that sells its sizes by volume (:func:`kit_drinks.pack_of`)."""
    pack_size = pack_of(pack_size, net_volume_ml)
    if flavor and flavor not in LIQUIDS:
        raise ValueError(f"no soft drink flavor {flavor!r}; known: {sorted(LIQUIDS)}")
    liquid = LIQUIDS.get(flavor, fill.base)
    form, n, ml = container(pack_size, small)
    h_mm, d_mm = dimensions(form, ml)
    if n > 1:
        return multipack(n, d_mm / h_mm, liquid, label)
    h = drawn_height(pack_size, largest or pack_size, small)
    if form == "can":
        w = h * d_mm / h_mm
        return [_ground(w / 2), *can(CX, BASE_Y, w, h, liquid, label)]
    return bottle(form, h, d_mm / h_mm, liquid, label)


register({"soft_drink": soft_drink})
