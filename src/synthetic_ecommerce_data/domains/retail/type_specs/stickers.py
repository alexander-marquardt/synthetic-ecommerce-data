"""Stickers (gen#887): Toys > Arts & Crafts > Stickers, sheets of kids' stickers.

The leaf came with the merchandise of the invented kids' films (:mod:`kids_films`): a film's
sticker sheets sell here beside two plain ranges of the same house, so ``stickers`` finds more
than film products. A sheet's SKU carries no color (a sheet holds many), and the drawing is
:func:`sticker_sheet`, drawn in code: a paper sheet holding die-cut stickers, the largest in the
row's first color. Every name here is invented.
"""

# ruff: noqa: E501 -- data rows and SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.retail import barry_plotter, kids_films
from synthetic_ecommerce_data.domains.retail.kit import PAPER, Fill, _line, _path, _shade, register
from synthetic_ecommerce_data.domains.retail.type_registry import Row, TypeSpec, cw

_STAR = "#f2c230"
_HEART = "#e8607a"
_LEAF = "#5f9a4a"


def _star(cx: float, cy: float, r: float) -> str:
    """A five-point star path centered on ``(cx, cy)``."""
    pts = []
    for i in range(10):
        rad = r if i % 2 == 0 else r * 0.45
        ang = math.radians(-90 + i * 36)
        pts.append(f"{cx + rad * math.cos(ang):.1f},{cy + rad * math.sin(ang):.1f}")
    return "M" + " L".join(pts) + " Z"


def sticker_sheet(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A sheet of die-cut stickers: a round one in the row's color, a star, a heart, a leaf and
    two small dots, each inside its white cut line, on a paper backing with a peeled corner."""
    del label
    sheet = "M104,64 L296,64 L296,300 L262,336 L104,336 Z"
    out = [
        _path(sheet, PAPER),
        _path("M296,300 L262,300 L262,336 Z", _shade(PAPER, 0.12)),
        '<circle cx="168" cy="130" r="46" fill="#ffffff" stroke="#c9c6bd" stroke-width="1.6"/>',
        f'<circle cx="168" cy="130" r="38" fill="{paint}" stroke="{_shade(paint, 0.3)}" stroke-width="2"/>',
        _path(_star(244, 128, 40), "#ffffff", 1.6, "", "#c9c6bd"),
        _path(_star(244, 128, 32), _STAR, 2, "", _shade(_STAR, 0.3)),
        _path("M160,266 C112,232 120,196 146,196 C158,196 160,204 160,210 C160,204 162,196 174,196 C200,196 208,232 160,266 Z", _HEART, 2, "", _shade(_HEART, 0.3)),
        _path("M232,262 C226,222 246,200 272,196 C276,224 262,256 232,262 Z", _LEAF, 2, "", _shade(_LEAF, 0.3)),
        _line("M234,258 L266,204", 1.6, "", _shade(_LEAF, 0.4)),
        f'<circle cx="138" cy="304" r="13" fill="{paint}" stroke="{_shade(paint, 0.3)}" stroke-width="1.6"/>',
        f'<circle cx="190" cy="304" r="13" fill="{_STAR}" stroke="{_shade(_STAR, 0.3)}" stroke-width="1.6"/>',
    ]
    return out


register({"sticker_sheet": sticker_sheet})

_PATH = kids_films.KINDS["ST"].path

ROWS = (
    Row("STKGLT", "Glitter Star Sticker Sheets", "Little Fernby", "Toys", _PATH, "Stickers", 3.5, "sticker_sheet",
        "Six sheets of glitter stickers: stars, moons and planets that peel off cleanly for cards and diaries.",
        (cw("Purple", "#7b4fa0"),), audience="kids", colorless=True),
    Row("STKPUF", "Puffy Animal Sticker Sheets", "Little Fernby", "Toys", _PATH, "Stickers", 4.5, "sticker_sheet",
        "Four sheets of raised, squashy animal stickers for little hands, from foxes to whales.",
        (cw("Green", "#3c8d4f"),), audience="kids", colorless=True),
    *kids_films.rows_of("Stickers"),
)

SPEC = TypeSpec(
    key="stickers",
    department="Toys",
    product_type="Stickers",
    rows=(*ROWS, *barry_plotter.rows_of("Stickers")),
)
