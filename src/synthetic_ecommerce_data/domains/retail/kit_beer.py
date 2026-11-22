"""A beer drawn as its real can, bottle or 4-pack (gen#1127, slice 3).

A lager, sour or alcohol free beer used to draw the generic ``kit.tin``, and a pale ale or fruit
beer the generic ``kit.bottle``, each shrunk by :mod:`pack_scale`; a 4-pack was four copies of
that one drawing. ``beer`` draws the container each pack is sold in, at its real proportions,
from the SKU's own ``pack_size`` and its line's ``sold_in`` and ``glass`` (per-SKU drawing params):

=======================  ====================================================================
pack                     draws
=======================  ====================================================================
330ml, 500ml in a        a glass beer bottle: a crown cap on a bead, a long neck, a label,
bottle line              the beer through the glass (:data:`GLASSES`: brown, clear, green)
330ml, 440ml in a can    a ring-pull can printed in the beer's own color (``kit_soft_drinks``)
line; a 440ml anywhere   (a 440ml is a can size)
N x 440ml, N x 330ml     N cans in two rows under a card carrier (``kit_soft_drinks``)
N x 500ml in a bottle    N bottles in a row in a card basket printed with the label
line
=======================  ====================================================================

A drawing that shows its count takes no copies (``pack_copies.SELF_DRAWN_SHAPES``).

THE SIZE. A bottle follows the wine bottle's rule (:mod:`kit_drinks`): the line's ``largest``
single bottle spans ``FULL_SHARE`` of the product area's height and a smaller one steps down
by its real height ratio to the power ``STEP_POWER``, never below ``MIN_SHARE`` of it. A can
stands at the full height wherever it is sold. A 4-pack fills the area's width. No
``pack_scale`` factor applies.

THE COLOR. The beer's color is its flavor's (``fill.base``: a lager gold, a stout dark, a fruit
beer in its fruit). A can is printed in it; a bottle shows it through its glass, which hides
some of it (brown glass most, clear glass least).
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped.

from __future__ import annotations

import re

from synthetic_ecommerce_data.domains.retail.house_styles import PRODUCT_SPAN, TURN_AREA
from synthetic_ecommerce_data.domains.retail.kit import LW, Fill, _mix, _panel, _path, register
from synthetic_ecommerce_data.domains.retail.kit_drinks import (
    BASE_Y,
    CX,
    FULL_SHARE,
    MIN_SHARE,
    STEP_POWER,
    Form,
    millilitres,
)
from synthetic_ecommerce_data.domains.retail.kit_soft_drinks import (
    CLEAR,
    CLEAR_HIDES,
    _ground,
    bottle,
    can,
    multipack,
)
from synthetic_ecommerce_data.domains.retail.kit_soft_drinks import (
    dimensions as can_dimensions,
)

#: A beer bottle: a straight body, a rounded shoulder, a long neck, a bead under the crown cap.
FORM = Form(
    (
        (0, 0.9),
        (0.02, 1),
        (0.6, 1),
        (0.68, 0.88),
        (0.75, 0.6),
        (0.8, 0.44),
        (0.84, 0.4),
        (0.93, 0.39),
        (0.935, 0.46),
        (0.955, 0.46),
        (0.96, 0.4),
    ),
    0.86,
    0.96,  # where the crown cap starts
    (0.14, 0.5),
)

#: A beer bottle's real (height, diameter) in mm by content in ml: a 330ml squat craft bottle
#: and a 500ml ale bottle.
BOTTLES = {275: (200, 60), 330: (205, 64), 500: (245, 75)}
#: The bottle sizes a shop sells beer in: a 440ml (or any other) is a can.
BOTTLE_SIZES = frozenset(BOTTLES)

#: Glass -> (its tint, how much of the beer's color it hides).
GLASSES = {
    "brown": ("#5c3414", 0.5),
    "green": ("#2f5a2c", 0.4),
    "clear": (CLEAR, CLEAR_HIDES),
}

_MULTI = re.compile(r"^(\d+) x (.+)$")
#: A basket's top, as a share of its bottles' height from their foot: it hides their labels.
BASKET = 0.55


def container(pack_size: str, sold_in: str = "can") -> tuple[str, int, float]:
    """``(form, count, ml)``: what ``pack_size`` is sold in, in a line ``sold_in`` cans or bottles.
    A bottle line sells a bottle of a :data:`BOTTLE_SIZES` size and a can of any other."""
    m = _MULTI.match(pack_size.strip())
    n, ml = (int(m[1]), millilitres(m[2])) if m else (1, millilitres(pack_size))
    form = "bottle" if sold_in == "bottle" and ml in BOTTLE_SIZES else "can"
    return form, n, ml


def dimensions(form: str, ml: float) -> tuple[float, float]:
    """The real (height, diameter) in mm of a ``form`` container holding ``ml``."""
    if form == "can":
        return can_dimensions("can", ml)
    if ml in BOTTLES:
        return BOTTLES[ml]
    near = min(BOTTLES, key=lambda k: abs(k - ml))
    k = (ml / near) ** (1 / 3)
    h, d = BOTTLES[near]
    return h * k, d * k


def drawn_height(pack_size: str, largest: str, sold_in: str = "can") -> float:
    """The container's drawn height in kit units: a bottle against the line's ``largest`` single
    bottle as a wine bottle is (:func:`kit_drinks.drawn_height`), a can always at the full height."""
    full = FULL_SHARE * PRODUCT_SPAN
    form, _, ml = container(pack_size, sold_in)
    if form == "can":
        return full
    top_ml = millilitres(largest) if largest else ml
    ratio = min(1.0, dimensions(form, ml)[0] / dimensions(form, top_ml)[0])
    return full * max(MIN_SHARE, ratio**STEP_POWER)


def through(beer: str, glass: str) -> str:
    """The beer's color ``beer`` as it shows through ``glass`` (:data:`GLASSES`)."""
    tint, hides = GLASSES[glass]
    return _mix(beer, tint, hides)


def basket(n: int, d_over_h: float, beer: str, glass: str, label: str | None) -> list[str]:
    """``n`` bottles side by side in a card basket printed with the label, as wide as the
    product area holds."""
    tint, hides = GLASSES[glass]
    w = min(FULL_SHARE * (TURN_AREA[2] - TURN_AREA[0]) / n, FULL_SHARE * PRODUCT_SPAN * d_over_h)
    h = w / d_over_h
    left = CX - n * w / 2 + w / 2
    out = [_ground(n * w / 2 / 1.4)]
    for i in range(n):  # each bottle without its own shadow, moved to its place in the row
        parts = bottle("beer", h, d_over_h * 0.96, beer, None, tint, hides, FORM)[1:]
        out.append(f'<g transform="translate({left + i * w - CX:.1f} 0)">{"".join(parts)}</g>')
    top = BASE_Y - BASKET * h
    x0, x1 = left - w / 2 - 2, left + (n - 0.5) * w + 2
    out.append(
        _path(
            f"M{x0:.1f},{top:.1f} L{x1:.1f},{top:.1f} L{x1:.1f},{BASE_Y - 2:.1f} L{x0:.1f},{BASE_Y - 2:.1f} Z",
            _mix(beer, "#ffffff", 0.35),
            LW,
            ' class="carrier"',
        )
    )
    out += _panel(
        CX - w * 1.2,
        top + 8,
        w * 2.4,
        BASKET * h - 18,
        f"{n} x {label}" if label else f"{n} bottles",
        28,
    )
    return out


def beer(paint: str, fill: Fill, label: str | None, pack_size: str = "330ml", largest: str = "",
         sold_in: str = "can", glass: str = "brown") -> list[str]:  # fmt: skip
    """A beer in its ``pack_size`` container, in a line ``sold_in`` cans or bottles in ``glass``,
    whose largest single bottle is ``largest`` (the SKU's own size when empty)."""
    if sold_in not in ("can", "bottle"):
        raise ValueError(f"a beer line is sold in cans or bottles, not {sold_in!r}")
    if glass not in GLASSES:
        raise ValueError(f"no beer glass {glass!r}; known: {sorted(GLASSES)}")
    color = fill.base
    form, n, ml = container(pack_size, sold_in)
    h_mm, d_mm = dimensions(form, ml)
    if n > 1:
        if form == "bottle":
            return basket(n, d_mm / h_mm, color, glass, label)
        return multipack(n, d_mm / h_mm, color, label)
    h = drawn_height(pack_size, largest, sold_in)
    if form == "can":
        w = h * d_mm / h_mm
        return [_ground(w / 2), *can(CX, BASE_Y, w, h, color, label)]
    tint, hides = GLASSES[glass]
    return bottle("beer", h, d_mm / h_mm, color, label, tint, hides, FORM)


register({"beer": beer})
