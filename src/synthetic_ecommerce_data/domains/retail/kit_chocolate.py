"""The chocolate selection box (gen#609) and the chocolate bar (gen#1125).

==============  ===================================================  ============
shape           draws                                                params
==============  ===================================================  ============
chocolate_box   a flat, wide, shallow lidded box seen at a slight     --
                angle, a ribbon across the lid
chocolate_bar   an opened bar, its wrapper torn back over the foil    pack_size,
                to show the glossy segmented block, broken pieces     chocolate
                in front; a multipack a stack of its bars
==============  ===================================================  ============

The record's fill paints the lid and the front of the box; the label panel on the lid carries
the product word, the range name and the band of the style's flavour colors (``kit._panel``).
The pack scale (gen#543) draws a smaller box smaller on the same sheet, so a 150g selection is
visibly smaller than a 400g one. A bar draws its own weight and multipack instead
(docs/retail-prototype/chocolate-fill-1125.md).
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import re

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    Fill,
    _line,
    _mix,
    _panel,
    _path,
    _shade,
    register,
)

RIBBON = "#d9b45a"


def _tag(cls: str, element: str) -> str:
    """``element`` (a ``<path .../>``) with a ``class`` so a test and a reader can find the part."""
    return element.replace("<path ", f'<path class="{cls}" ', 1)


def chocolate_box(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A flat box, wide and shallow: the lid's top face towards the viewer, the front and one
    side below it, a ribbon across the lid and down the front, the label panel on the lid."""
    side = _shade(fill.base, 0.25)
    ribbon = _shade(RIBBON, 0.1)
    return [
        _path("M304,290 L360,200 L360,250 L304,340 Z", side),
        _path("M40,290 L304,290 L304,340 L40,340 Z", paint),
        _line("M40,308 L304,308 M304,308 L360,218", LW_DETAIL, ' stroke-opacity=".7"'),
        _tag("lid", _path("M40,290 L96,200 L360,200 L304,290 Z", _mix(fill.base, "#ffffff", 0.18))),
        _tag("ribbon", _path("M268,290 L324,200 L346,200 L290,290 Z", RIBBON, LW_DETAIL)),
        _tag("ribbon", _path("M268,290 L290,290 L290,340 L268,340 Z", ribbon, LW_DETAIL)),
        *_panel(100, 214, 150, 62, label, 40),
    ]


#: The foil under a bar's wrapper, and its crinkles.
FOIL, FOIL_CRINKLE = "#d8c47e", "#a8904a"
#: The deep tone a wrapper too pale to read on white paper is moved towards (a cocoa brown).
COCOA = "#2a1d14"
#: The least contrast a wrapper keeps against white paper (WCAG's ratio, as for large text).
WRAPPER_CONTRAST = 3.0
#: A bar's drawn size: the largest bar's top face, the smallest scale a lighter one is drawn at,
#: and the weight at and above which a bar is the full one.
BAR_W, BAR_H, BAR_SMALLEST, BAR_FULL_G = 328.0, 196.0, 0.9, 200.0
#: A broken piece's segment pitch, and the centre the drawing is placed about (the product area's).
PIECE_PITCH, CENTER_Y = 40.0, 195.0
#: The gloss over a chocolate surface: a highlight at the top left, a shade at the foot right.
GLOSS = (
    '<linearGradient id="{0}" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#ffffff" stop-opacity=".5"/>'
    '<stop offset=".32" stop-color="#ffffff" stop-opacity="0"/>'
    '<stop offset=".62" stop-color="#000000" stop-opacity="0"/>'
    '<stop offset="1" stop-color="#000000" stop-opacity=".34"/></linearGradient>'
)
#: The chocolate a bar is made of, by its kind: a bar's block is chocolate, whatever the
#: flavour's color on the wrapper (a mint dark bar is dark chocolate in a green wrapper).
CHOCOLATE = {"milk": "#7a4a2a", "dark": "#3a2216", "white": "#f1e4c4"}
_PACK = re.compile(r"(?:(\d+)\s*x\s*)?(\d+(?:\.\d+)?)\s*g", re.IGNORECASE)


def _luminance(color: str) -> float:
    """``color``'s relative luminance (WCAG 2)."""

    def channel(v: int) -> float:
        c = v / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def wrapper_color(base: str) -> str:
    """``base`` moved towards :data:`COCOA` just far enough to keep :data:`WRAPPER_CONTRAST`
    against white paper, so a white chocolate bar's cream wrapper does not vanish on it."""
    for step in range(11):
        color = _mix(base, COCOA, step / 10)
        if 1.05 / (_luminance(color) + 0.05) >= WRAPPER_CONTRAST:
            return color
    return COCOA


def chocolate_color(chocolate: str | None, base: str) -> str:
    """The color of a bar's chocolate: the :data:`CHOCOLATE` of its kind; with no kind, the one
    ``base`` reads as, a pale base white, a very dark one dark, else milk."""
    if chocolate in CHOCOLATE:
        return CHOCOLATE[chocolate]
    lum = _luminance(base)
    return CHOCOLATE["white" if lum > 0.55 else "dark" if lum < 0.04 else "milk"]


def pack_items(pack_size: str | None) -> tuple[int, float | None]:
    """The bars a pack holds and each bar's weight in grams: ``"4 x 35g"`` is (4, 35.0),
    ``"100g"`` (1, 100.0); a pack size that names no weight is one bar of no stated weight."""
    found = _PACK.fullmatch((pack_size or "").strip())
    if not found:
        return 1, None
    return int(found[1] or 1), float(found[2])


def _rect(x: float, y: float, w: float, h: float) -> str:
    return f"M{x:.1f},{y:.1f} L{x + w:.1f},{y:.1f} L{x + w:.1f},{y + h:.1f} L{x:.1f},{y + h:.1f} Z"


def _zigzag(x: float, y0: float, y1: float, lean: float, depth: float, step: float) -> str:
    """The points of a torn edge from ``(x, y0)`` down to ``(x - lean, y1)``, ``depth`` deep."""
    n = max(2, round((y1 - y0) / step))
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(f"L{x - lean * t + (depth if i % 2 else 0):.1f},{y0 + (y1 - y0) * t:.1f}")
    return " ".join(pts)


def _segments(x: float, y: float, w: float, h: float, cols: int, rows: int, choc: str) -> list[str]:
    """The block's segments: each a raised square, a groove between them."""
    pw, ph = w / cols, h / rows
    inset = min(pw, ph) * 0.14
    face = _mix(choc, "#ffffff", 0.1)
    groove = _shade(choc, 0.45)
    out = []
    for c in range(cols):
        for r in range(rows):
            d = _rect(x + c * pw + inset, y + r * ph + inset, pw - 2 * inset, ph - 2 * inset)
            out.append(_path(d, face, 1.2, stroke=groove))
    return out


def _chocolate(
    top: str, edge: str, segments: list[str], choc: str, gloss: str, at: str = ""
) -> list[str]:
    """A chocolate surface: its front edge in shade, its top face, segments, and the gloss."""
    turned = f' transform="{at}"' if at else ""
    return [
        f'<g class="chocolate"{turned}>',
        _path(edge, _shade(choc, 0.35)),
        _path(top, choc),
        *segments,
        f'<path d="{top}" fill="url(#{gloss})" stroke="none"/>',
        "</g>",
    ]


def _piece(
    x: float, y: float, cols: int, rows: int, angle: float, choc: str, gloss: str
) -> list[str]:
    """A piece broken off the bar: ``cols`` x ``rows`` segments, its right side broken."""
    w, h, t = cols * PIECE_PITCH, rows * PIECE_PITCH, PIECE_PITCH * 0.24
    broken = _zigzag(x + w, y, y + h, 0, -9, 13)
    top = f"M{x:.1f},{y:.1f} L{x + w:.1f},{y:.1f} {broken} L{x:.1f},{y + h:.1f} Z"
    edge = _rect(x, y + h - 2, w - 6, t + 2)
    at = f"rotate({angle:g} {x + w / 2:.1f} {y + h / 2:.1f})"
    return _chocolate(top, edge, _segments(x, y, w - 8, h, cols, rows, choc), choc, gloss, at)


def _bar(
    x: float, y: float, w: float, h: float, grid: tuple[int, int], wrapper: str, choc: str,
    gloss: str, label: str | None, opened: bool,
) -> list[str]:  # fmt: skip
    """One bar, its top face at ``(x, y, w, h)``: opened, its wrapper torn back over the foil
    to show the segmented block, and the label panel on the wrapper; else wrapped whole."""
    t = max(7.0, h * 0.08)  # the bar's thickness, seen as its front edge
    out = ['<g class="bar">']
    if not opened:
        out += [
            _tag("wrapper", _path(_rect(x - 4, y - 4, w + 8, h + t + 8), wrapper)),
            _path(_rect(x - 4, y + h, w + 8, t + 4), _shade(wrapper, 0.28), LW_DETAIL),
            _path(_rect(x + 10, y + 8, w - 20, 6), _mix(wrapper, "#ffffff", 0.45), 1.0),
        ]
        return [*out, "</g>"]
    cut, foil = x + w * 0.5, x + w * 0.6
    out += _chocolate(
        _rect(x, y, w, h), _rect(x, y + h, w, t), _segments(x, y, w, h, *grid, choc), choc, gloss
    )
    foil_edge = _zigzag(foil, y - 3, y + h + t + 3, -6, 7, 12)
    out += [
        _path(f"M{x - 2:.1f},{y - 3:.1f} {foil_edge} L{x - 2:.1f},{y + h + t + 3:.1f} Z", FOIL, LW_DETAIL),
        _line(f"M{foil - 30:.1f},{y + 10:.1f} L{foil - 14:.1f},{y + h * 0.4:.1f} "
              f"M{foil - 22:.1f},{y + h * 0.55:.1f} L{foil - 8:.1f},{y + h * 0.9:.1f}",
              1.2, stroke=FOIL_CRINKLE),
    ]  # fmt: skip
    torn = _zigzag(cut + 12, y - 6, y + h + t + 6, 22, 5, 10)
    out += [
        _tag("wrapper", _path(f"M{x - 5:.1f},{y - 6:.1f} {torn} L{x - 5:.1f},{y + h + t + 6:.1f} Z", wrapper)),
        _path(f"M{x - 5:.1f},{y + h:.1f} L{cut - 9:.1f},{y + h:.1f} L{cut - 10:.1f},{y + h + t + 6:.1f} "
              f"L{x - 5:.1f},{y + h + t + 6:.1f} Z", _shade(wrapper, 0.28), LW_DETAIL),
        _path(f"M{cut + 12:.1f},{y - 6:.1f} L{cut + 44:.1f},{y + 14:.1f} L{cut + 8:.1f},{y + 26:.1f} Z",
              "#f4efe6", LW_DETAIL),
        *_panel(x + 12, y + h * 0.14, cut - x - 32, h * 0.68, label, 40),
        "</g>",
    ]  # fmt: skip
    return out


def chocolate_bar(
    paint: str, fill: Fill, label: str | None, pack_size: str | None = None,
    chocolate: str | None = None,
) -> list[str]:  # fmt: skip
    """A chocolate bar seen from a little above, its wrapper torn back over the foil to show
    the glossy segmented block, two broken pieces in front; a multipack (``"4 x 35g"``) is a
    stack of its bars, the front one opened. A bar under :data:`BAR_FULL_G` is drawn a little
    smaller, by about the cube root of its weight, never under :data:`BAR_SMALLEST`. The
    wrapper is the flavour's color, the block the ``chocolate`` it is made of (:func:`chocolate_color`)."""
    n, grams = pack_items(pack_size)
    choc = chocolate_color(chocolate, fill.base)
    wrapper = wrapper_color(fill.base) if fill.pattern == "solid" else paint
    gloss = f"choc-gloss-{choc[1:]}"
    out = [GLOSS.format(gloss)]
    if n == 1:
        k = 1.0 if grams is None else max(BAR_SMALLEST, min(1.0, (grams / BAR_FULL_G) ** (1 / 3)))
        w, h = BAR_W * k, BAR_H * k
        grid = (8, 4) if grams is None or grams >= 150 else (6, 3)
        x, y = 200 - w / 2, CENTER_Y - (h + 96) / 2 + 6
        out.append(f'<ellipse class="ground" cx="200" cy="{y + h + 22:.1f}" rx="{w / 2 + 14:.1f}" '
                   'ry="12" fill="#000000" fill-opacity=".14"/>')  # fmt: skip
        out += _bar(x, y, w, h, grid, wrapper, choc, gloss, label, opened=True)
        out += _piece(x + w * 0.08, y + h - 12, 2, 2, -8, choc, gloss)
        out += _piece(x + w * 0.62, y + h - 4, 2, 2, 10, choc, gloss)
        return out
    w, h = 300.0, 80.0 if n <= 4 else 62.0
    dx, dy = 8.0, (220.0 - h) / (n - 1)
    x0 = 200 - (w + (n - 1) * dx) / 2
    y0 = CENTER_Y + (220 - h) / 2 - 30  # the front bar's top face
    out.append(f'<ellipse class="ground" cx="200" cy="{y0 + h + 18:.1f}" rx="{w / 2 + 20:.1f}" '
               'ry="12" fill="#000000" fill-opacity=".14"/>')  # fmt: skip
    for i in reversed(range(n)):
        out += _bar(
            x0 + i * dx, y0 - i * dy, w, h, (6, 2), wrapper, choc, gloss, label, opened=not i
        )
    out += _piece(x0 + w * 0.6, y0 + h - 6, 2, 2, 9, choc, gloss)
    return out


register({"chocolate_box": chocolate_box, "chocolate_bar": chocolate_bar})
