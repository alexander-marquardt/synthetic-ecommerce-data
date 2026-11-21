"""Milk drawn as the jug or carton it is sold in, filling its picture (gen#1128).

==============  ===================================================  ==========
shape           draws                                                params
==============  ===================================================  ==========
milk_jug        a translucent plastic jug of white milk, seen a      flavor,
                little from the side: a handle at the back, a cap    pack_size
                in the fat level's colour, the label in that colour
milk_carton     a gable-top carton (a plant milk): the front, the    pack_size
                side and its gable, a screw cap on the roof
==============  ===================================================  ==========

Before gen#1128 every milk and plant milk drew the kit's generic ``carton``, painted in its
line's first flavour, and ``pack_scale`` shrank a 1 pint to 0.63: it covered a fifth of its
product area, and a Semi Skimmed SKU of a Whole-first line drew blue.

``flavor`` and ``pack_size`` are the SKU's own values (per-SKU drawing params, as a pizza's are),
so each fat level and size is its own picture. A jug's cap and label take its fat level's colour
from :data:`FAT_CAPS`, as UK shelves code it (whole blue, semi skimmed green, skimmed red). Each
size is drawn in its own proportions (:data:`JUGS`, :data:`CARTONS`): a larger pack is wider and
deeper. Each still fills at least half the product area, so neither shape takes a ``pack_scale``
factor (:data:`pack_scale.SELF_SIZED`). Each carries a gloss (``class="gloss"``), and stands on a
ground shadow (``class="ground"``) outside the ``dairy`` group, which the fill measure counts.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _line,
    _panel,
    _path,
    _shade,
    _tint,
    register,
)

#: A milk's fat level -> its cap and label colour.
FAT_CAPS = {
    "Whole": "#2f63c0",
    "Semi Skimmed": "#2f9a4c",
    "Skimmed": "#d0312d",
    "Lactose Free": "#7a4aa8",
}
#: A jug's pack size -> its front's width and its side's depth. A larger jug is wider and deeper.
JUGS = {"1 pint": (166.0, 58.0), "2 pint": (184.0, 68.0), "4 pint": (210.0, 82.0)}
#: A plant milk carton's pack size -> its front's width and its side's depth.
CARTONS = {"500ml": (150.0, 62.0), "1L": (168.0, 70.0), "2L": (190.0, 80.0)}
#: The SKU fields each shape draws from, which ``grocery`` sets as its drawing params.
SKU_PARAMS = {"milk_jug": ("flavor", "pack_size"), "milk_carton": ("pack_size",)}

#: The baseline every pack stands on, and the milk's white.
BASE = 350.0
MILK = "#fcfcf7"
PLASTIC = "#e3edf2"


def _ground(width: float) -> str:
    return f'<ellipse class="ground" cx="200" cy="{BASE + 2:g}" rx="{width / 2 + 20:g}" ry="11" fill="#000000" fill-opacity=".14"/>'


def _gloss(d: str, width: float) -> str:
    return f'<path class="gloss" d="{d}" fill="none" stroke="#ffffff" stroke-width="{width:g}" stroke-linecap="round" stroke-opacity=".7"/>'


def _size(table: dict[str, tuple[float, float]], pack_size: str, shape: str) -> tuple[float, float]:
    if pack_size not in table:
        raise ValueError(f"no {shape} of {pack_size!r}; known: {sorted(table)}")
    return table[pack_size]


def milk_jug(
    paint: str, fill: Fill, label: str | None, flavor: str = "Whole", pack_size: str = "2 pint"
) -> list[str]:
    """A plastic milk jug of ``pack_size`` with a cap and label in ``flavor``'s colour."""
    if flavor not in FAT_CAPS:
        raise ValueError(f"no milk of {flavor!r}; known: {sorted(FAT_CAPS)}")
    fw, sw = _size(JUGS, pack_size, "milk_jug")
    color = FAT_CAPS[flavor]
    xl = 200 - (fw + sw) / 2
    xf, xr = xl + fw, xl + fw + sw
    rise = sw * 0.26  # the side's foot rises as it goes back
    top, neck, cap_foot, cap_top = 118.0, 84.0, 70.0, 38.0
    nx, nh = xl + fw * 0.4, fw * 0.13 + 4
    # the jug's outline from the neck round the shoulder, the foot and the back, and over the handle
    outer = (
        f"M{nx - nh:g},{cap_foot:g} L{nx - nh:g},{neck:g} C{nx - nh:g},{neck + 18:g} {xl:g},{top - 18:g} {xl:g},{top + 10:g} "
        f"L{xl:g},{BASE - 16:g} Q{xl:g},{BASE:g} {xl + 16:g},{BASE:g} L{xf:g},{BASE:g} L{xr - 14:g},{BASE - rise:g} "
        f"Q{xr:g},{BASE - rise - 2:g} {xr:g},{BASE - rise - 16:g} L{xr:g},{top + 30:g} "
        f"C{xr:g},{neck - 4:g} {xr - 20:g},{neck - 18:g} {xr - 44:g},{neck - 18:g} L{nx + nh + 6:g},{neck - 18:g} "
        f"Q{nx + nh:g},{neck - 18:g} {nx + nh:g},{neck - 26:g} L{nx + nh:g},{cap_foot:g} Z"
    )
    # the gap the hand goes through, wound against the outline so it stays unpainted
    hx0, hx1, hy0, hy1 = nx + nh + 18, xr - 20, neck - 2, top + 12
    hole = (
        f" M{hx0:g},{hy0 + 8:g} Q{hx0:g},{hy0:g} {hx0 + 10:g},{hy0:g} L{hx1 - 14:g},{hy0:g} Q{hx1:g},{hy0:g} {hx1:g},{hy0 + 16:g} "
        f"L{hx1:g},{hy1 - 6:g} Q{hx1:g},{hy1:g} {hx1 - 12:g},{hy1:g} Q{(hx0 + hx1) / 2:g},{hy1 - 4:g} {hx0:g},{hy0 + 30:g} Z"
    )
    level = top + 22  # the milk stands just under the shoulder
    milk = (
        f"M{xl + 5:g},{level:g} L{xf:g},{level:g} L{xr - 6:g},{level - rise * 0.5:g} L{xr - 6:g},{BASE - rise - 12:g} "
        f"L{xf:g},{BASE - 5:g} L{xl + 16:g},{BASE - 5:g} Q{xl + 5:g},{BASE - 5:g} {xl + 5:g},{BASE - 16:g} Z"
    )
    side = (
        f"M{xf:g},{top + 4:g} L{xr:g},{top + 30:g} L{xr:g},{BASE - rise - 16:g} Q{xr:g},{BASE - rise - 2:g} {xr - 14:g},{BASE - rise:g} "
        f"L{xf:g},{BASE:g} Z"
    )
    lx, ly, lw, lh = xl + 10, level + 22, fw - 20, BASE - 34 - (level + 22)
    ridges = " ".join(
        f"M{x:.1f},{cap_top + 6:g} L{x:.1f},{cap_foot - 2:g}" for x in _steps(nx - nh, nx + nh, 6)
    )
    return [
        _ground(fw + sw),
        '<g class="dairy">',
        f'<path class="milk" d="{milk}" fill="{MILK}"/>',
        _path(outer + hole, PLASTIC, LW, ' class="jug" fill-opacity=".5"'),
        f'<path d="{side}" fill="#000000" fill-opacity=".07"/>',
        _line(f"M{xf:g},{top + 4:g} L{xf:g},{BASE:g}", LW_DETAIL, ' stroke-opacity=".6"'),
        _line(
            f"M{xl + 3:g},{level:g} L{xf:g},{level:g} L{xr - 4:g},{level - rise * 0.5:g}",
            LW_DETAIL,
            ' stroke-opacity=".45"',
        ),
        f'<rect class="label" x="{lx:g}" y="{ly:g}" width="{lw:g}" height="{lh:g}" rx="8" fill="{color}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        *_panel(
            lx + 8, ly + 24, lw - 16, lh - 48, f"{flavor} Milk", 40
        ),  # the SKU's own fat level, not its line's first
        f'<rect x="{nx - nh - 3:g}" y="{cap_foot - 2:g}" width="{2 * nh + 6:g}" height="8" rx="2" fill="{_tint(color, 0.5)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<rect class="cap" x="{nx - nh - 6:g}" y="{cap_top:g}" width="{2 * nh + 12:g}" height="{cap_foot - cap_top:g}" rx="6" fill="{color}" stroke="{INK}" stroke-width="{LW}"/>',
        _line(ridges, 1.0, ' stroke-opacity=".45"'),
        _gloss(f"M{xl + 14:g},{level + 12:g} L{xl + 14:g},{BASE - 26:g}", 8),
        _gloss(f"M{nx + nh + 14:g},{neck - 10:g} L{xr - 40:g},{neck - 10:g}", 4),
        _gloss(f"M{nx - nh + 10:g},{cap_top + 8:g} L{nx - nh + 10:g},{cap_foot - 8:g}", 4),
        "</g>",
    ]


def milk_carton(paint: str, fill: Fill, label: str | None, pack_size: str = "1L") -> list[str]:
    """A gable-top carton of ``pack_size``, its front in the record's paint, a cap on the roof."""
    fw, sw = _size(CARTONS, pack_size, "milk_carton")
    xl = 200 - (fw + sw) / 2
    xf, xr = xl + fw, xl + fw + sw
    eaves, ridge, fin = 118.0, 66.0, 46.0
    rl, rr = xl + sw / 2, (xf + xr) / 2  # the ridge's ends
    base = fill.base
    cx, cy = xl + fw * 0.34 + sw * 0.25, (eaves + ridge) / 2 + 4
    return [
        _ground(fw + sw),
        '<g class="dairy">',
        _path(
            f"M{xf:g},{eaves:g} L{xr:g},{eaves:g} L{xr:g},{BASE:g} L{xf:g},{BASE:g} Z",
            _shade(base, 0.2),
            extra=' class="carton"',
        ),
        _path(f"M{xf:g},{eaves:g} L{xr:g},{eaves:g} L{rr:g},{ridge:g} Z", _shade(base, 0.32)),
        _path(
            f"M{xl:g},{eaves:g} L{xf:g},{eaves:g} L{rr:g},{ridge:g} L{rl:g},{ridge:g} Z",
            _tint(base, 0.3),
        ),
        _path(
            f"M{rl:g},{ridge:g} L{rr:g},{ridge:g} L{rr:g},{fin:g} L{rl:g},{fin:g} Z",
            _tint(base, 0.6),
        ),
        _path(
            f"M{xl:g},{eaves:g} L{xf:g},{eaves:g} L{xf:g},{BASE:g} L{xl:g},{BASE:g} Z",
            paint,
            extra=' class="carton"',
        ),
        f'<rect x="{cx - 20:g}" y="{cy - 16:g}" width="40" height="16" fill="{fill.accent}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<ellipse cx="{cx:g}" cy="{cy - 16:g}" rx="20" ry="6" fill="{_tint(fill.accent, 0.4)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        *_panel(xl + 12, eaves + 64, fw - 24, 112, label, 44),
        _gloss(f"M{xl + 12:g},{eaves + 14:g} L{xl + 12:g},{BASE - 22:g}", 7),
        _gloss(f"M{rl + 10:g},{ridge + 8:g} L{xl + 22:g},{eaves - 8:g}", 4),
        "</g>",
    ]


def _steps(a: float, b: float, n: int) -> list[float]:
    """``n`` points evenly inside (a, b)."""
    return [a + (b - a) * (i + 1) / (n + 1) for i in range(n)]


register({"milk_jug": milk_jug, "milk_carton": milk_carton})
