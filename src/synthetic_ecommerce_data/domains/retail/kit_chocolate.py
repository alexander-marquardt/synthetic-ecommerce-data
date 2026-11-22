"""The chocolate box (gen#609), bar, sharing bag, hot chocolate and chocolate orange (gen#1125).

================  ===================================================  ============
shape             draws                                                params
================  ===================================================  ============
chocolate_box     an opened gift box seen from a little above, its      pack_size,
                  lid standing behind it, the chocolates in their       chocolate
                  paper cups on the tray
chocolate_bar     an opened bar, its wrapper torn back over the foil    pack_size,
                  to show the glossy segmented block, broken pieces     chocolate
                  in front; a multipack a stack of its bars
chocolate_bag     a stand-up sharing bag, its buttons or bites seen     pack_size,
                  through a window and a few spilled in front           chocolate,
                                                                        piece
hot_chocolate     a lidded tub of drinking chocolate, a mug filled      pack_size,
                  with glossy cocoa in front of it                      chocolate
chocolate_orange  a ball of glossy segments in its opened foil, two     pack_size,
                  segments loose in front                               chocolate
================  ===================================================  ============

Every chocolate shows glossed: a highlight at the top left and a shade at the foot right. Each
shape draws its own weight (a 150g box is smaller than a 400g one, never under its smallest
scale), so the pack scale (gen#543) gives it no factor and every size fills half its product
area (docs/retail-prototype/chocolate-fill-1125.md). A box's label panel sits on the lid, a
bag's above its window, a hot chocolate's on its tub and a chocolate orange's on its foil.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math
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


#: The foil under a bar's wrapper, and its crinkles.
FOIL, FOIL_CRINKLE = "#d8c47e", "#a8904a"
#: The deep tone a wrapper too pale to read on white paper is moved towards (a cocoa brown).
COCOA = "#2a1d14"
#: The least contrast a wrapper keeps against white paper (WCAG's ratio, as for large text).
WRAPPER_CONTRAST = 3.0
#: A bar's drawn size: the largest bar's top face, the smallest scale a lighter one is drawn at,
#: and the weight at and above which a bar is the full one.
BAR_W, BAR_H, BAR_SMALLEST, BAR_FULL_G = 328.0, 196.0, 0.9, 200.0
#: A broken piece's segment pitch, and the center the drawing is placed about (the product area's).
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
    # The piece sits on the front bar's foot, high enough that it and its turn stay on the
    # sheet: at the 4-bar stack's foot it reached 3.3 past the bottom edge (gen#242).
    out += _piece(x0 + w * 0.6, y0 + h - 20, 2, 2, 9, choc, gloss)
    return out


#: A box's drawn size: the weight at and above which it is the full one, and its smallest scale.
BOX_FULL_G, BOX_SMALLEST = 400.0, 0.84
#: A sharing bag's: the same.
BAG_FULL_G, BAG_SMALLEST = 250.0, 0.9
#: The box's tray, the paper cups the chocolates sit in, and a cup's pleats.
TRAY, CUP, CUP_PLEAT = "#c9a752", "#4a3020", "#2a1a10"
#: The center a box or bag is drawn about, and scaled about for its weight.
PACK_CENTER = (200.0, CENTER_Y)
#: An assortment's second chocolate, and the drizzle across a third of its pieces.
_ALSO = {"milk": "dark", "dark": "milk", "white": "milk"}
_DRIZZLE = {"milk": "white", "dark": "white", "white": "dark"}


def own_scale(pack_size: str | None, full: float, smallest: float) -> float:
    """The scale a pack of ``pack_size`` is drawn at: 1 at ``full`` grams and above, the cube
    root of its share below, never under ``smallest``; 1 with no weight named."""
    _, grams = pack_items(pack_size)
    return 1.0 if grams is None else max(smallest, min(1.0, (grams / full) ** (1 / 3)))


def _scaled(k: float, parts: list[str], cls: str) -> list[str]:
    """``parts`` in a ``<g class=cls>`` scaled by ``k`` about :data:`PACK_CENTER`."""
    cx, cy = PACK_CENTER
    at = (
        f' transform="translate({cx * (1 - k):.2f} {cy * (1 - k):.2f}) scale({k:.4f})"'
        if k != 1
        else ""
    )
    return [f'<g class="{cls}"{at}>', *parts, "</g>"]


def _disc(cx: float, cy: float, rx: float, ry: float) -> str:
    """An ellipse as a path of four curves."""
    a, b = rx * 0.5523, ry * 0.5523
    return (f"M{cx + rx:.1f},{cy:.1f} C{cx + rx:.1f},{cy + b:.1f} {cx + a:.1f},{cy + ry:.1f} {cx:.1f},{cy + ry:.1f} "
            f"C{cx - a:.1f},{cy + ry:.1f} {cx - rx:.1f},{cy + b:.1f} {cx - rx:.1f},{cy:.1f} "
            f"C{cx - rx:.1f},{cy - b:.1f} {cx - a:.1f},{cy - ry:.1f} {cx:.1f},{cy - ry:.1f} "
            f"C{cx + a:.1f},{cy - ry:.1f} {cx + rx:.1f},{cy - b:.1f} {cx + rx:.1f},{cy:.1f} Z")  # fmt: skip


def _button(cx: float, cy: float, r: float, choc: str, gloss: str) -> list[str]:
    """A chocolate button seen from a little above: a disc on its shaded edge, a raised rim."""
    ring = _line(_disc(cx, cy, r * 0.68, r * 0.55), 1.2, stroke=_mix(choc, "#ffffff", 0.3))
    edge = _disc(cx, cy + r * 0.18, r, r * 0.8)
    return _chocolate(_disc(cx, cy, r, r * 0.8), edge, [ring], choc, gloss)


def _bite(cx: float, cy: float, r: float, choc: str, gloss: str) -> list[str]:
    """A chocolate bite: a small block, its top face square on, its front edge in shade."""
    top = _rect(cx - r, cy - r * 0.8, 2 * r, 1.6 * r)
    groove = _line(f"M{cx - r * 0.6:.1f},{cy - r * 0.1:.1f} L{cx + r * 0.6:.1f},{cy - r * 0.1:.1f}",
                   1.2, stroke=_shade(choc, 0.45))  # fmt: skip
    return _chocolate(top, _rect(cx - r, cy + r * 0.8, 2 * r, r * 0.42), [groove], choc, gloss)


def _praline(kind: int, cx: float, cy: float, rx: float, ry: float, colors: tuple[str, str, str],
             gloss: str) -> list[str]:  # fmt: skip
    """One chocolate of an assortment in its paper cup: ``kind`` 0 a round truffle, 1 a square
    praline in the second chocolate, 2 a dome with a drizzle of the third across it."""
    choc, also, drizzle = colors
    cup = _path(_disc(cx, cy + ry * 0.12, rx, ry), CUP, 1.2, stroke=CUP_PLEAT)
    pleats = _line(" ".join(f"M{cx + rx * t:.1f},{cy + ry * 0.7:.1f} L{cx + rx * t * 1.1:.1f},{cy + ry * 1.05:.1f}"
                            for t in (-0.6, -0.2, 0.2, 0.6)), 1.0, stroke=CUP_PLEAT)  # fmt: skip
    out = [cup, pleats]
    px, py = rx * 0.8, ry * 0.78
    if kind == 1:
        top = _rect(cx - px * 0.88, cy - py * 0.9, px * 1.76, py * 1.5)
        ridge = _line(f"M{cx - px * 0.5:.1f},{cy - py * 0.2:.1f} L{cx + px * 0.5:.1f},{cy - py * 0.2:.1f}",
                      1.2, stroke=_shade(also, 0.45))  # fmt: skip
        return out + _chocolate(
            top, _rect(cx - px * 0.88, cy + py * 0.6, px * 1.76, py * 0.32), [ridge], also, gloss
        )
    extra = []
    if kind == 2:
        zig = " ".join(
            f"L{cx - px * 0.7 + i * px * 0.28:.1f},{cy - py * (0.35 if i % 2 else -0.1):.1f}"
            for i in range(6)
        )
        extra = [_line(f"M{cx - px * 0.7:.1f},{cy + py * 0.1:.1f} {zig}", 2.6, stroke=drizzle)]
    return out + _chocolate(
        _disc(cx, cy - py * 0.12, px, py), _disc(cx, cy, px, py), extra, choc, gloss
    )


def chocolate_box(
    paint: str, fill: Fill, label: str | None, pack_size: str | None = None,
    chocolate: str | None = None,
) -> list[str]:  # fmt: skip
    """An opened gift box seen from a little above: the lid stands behind it with a ribbon and
    the label panel, and the tray holds the chocolates in their paper cups, an assortment of
    truffles, square pralines in a second chocolate and drizzled domes. A box under
    :data:`BOX_FULL_G` is drawn smaller (:func:`own_scale`), and holds fewer chocolates."""
    k = own_scale(pack_size, BOX_FULL_G, BOX_SMALLEST)
    _, grams = pack_items(pack_size)
    cols, rows = (6, 4) if grams is None or grams >= 300 else (5, 3) if grams >= 200 else (4, 3)
    choc = chocolate_color(chocolate, fill.base)
    kind = next((name for name, hex_ in CHOCOLATE.items() if hex_ == choc), "milk")
    colors = (choc, CHOCOLATE[_ALSO[kind]], CHOCOLATE[_DRIZZLE[kind]])
    box = wrapper_color(fill.base) if fill.pattern == "solid" else paint
    gloss = f"choc-gloss-{choc[1:]}"
    lid = _mix(box, "#ffffff", 0.14)
    out = [
        _tag("lid", _path("M74,40 L326,40 L340,140 L60,140 Z", lid)),
        _line("M78,50 L322,50", 1.2, ' stroke-opacity=".5"'),
        _tag("ribbon", _path("M276,40 L298,40 L304,140 L282,140 Z", RIBBON, LW_DETAIL)),
        _tag("ribbon", _path("M287,46 C262,24 252,52 287,50 C322,52 312,24 287,46 Z", _shade(RIBBON, 0.1), LW_DETAIL)),
        *_panel(90, 58, 172, 64, label, 34),
        _tag("wrapper", _path("M50,132 L350,132 L364,296 L36,296 Z", box)),
        _path("M36,296 L364,296 L364,340 L36,340 Z", _shade(box, 0.28)),
        _line("M36,310 L364,310", 1.6, ' stroke-opacity=".8"', RIBBON),
        _tag("tray", _path("M64,144 L336,144 L348,284 L52,284 Z", TRAY, LW_DETAIL)),
    ]  # fmt: skip
    top, bottom = 144.0, 284.0
    for r in range(rows):
        t = (r + 0.5) / rows
        y = top + (bottom - top) * t
        left, right = 64 + (52 - 64) * t, 336 + (348 - 336) * t
        cw, ch = (right - left) / cols, (bottom - top) / rows
        for c in range(cols):
            out += _praline(
                (c + r) % 3, left + cw * (c + 0.5), y, cw * 0.42, ch * 0.4, colors, gloss
            )
    ground = (f'<ellipse class="ground" cx="200" cy="{CENTER_Y + (348 - CENTER_Y) * k:.1f}" '
              f'rx="{176 * k:.1f}" ry="12" fill="#000000" fill-opacity=".14"/>')  # fmt: skip
    return [GLOSS.format(gloss), ground, *_scaled(k, out, "box")]


def chocolate_bag(
    paint: str, fill: Fill, label: str | None, pack_size: str | None = None,
    chocolate: str | None = None, piece: str | None = None,
) -> list[str]:  # fmt: skip
    """A stand-up sharing bag: a crimped top seal, the label panel, a window showing the
    ``piece`` it holds (``"buttons"``, or else bites) and a few spilled at its foot. The bag is
    the flavour's color, kept visible on white paper (:func:`wrapper_color`); a bag under
    :data:`BAG_FULL_G` is drawn smaller (:func:`own_scale`)."""
    k = own_scale(pack_size, BAG_FULL_G, BAG_SMALLEST)
    choc = chocolate_color(chocolate, fill.base)
    bag = wrapper_color(fill.base) if fill.pattern == "solid" else paint
    gloss = f"choc-gloss-{choc[1:]}"
    draw = _button if piece == "buttons" else _bite
    seal = (
        "M86,34 "
        + " ".join(f"L{86 + i * 12:.0f},{34 if i % 2 else 28}" for i in range(1, 20))
        + " L314,34 L314,60 L86,60 Z"
    )
    out = [
        _tag("wrapper", _path("M86,56 L314,56 C324,150 334,240 338,312 Q338,336 314,336 L86,336 "
                              "Q62,336 62,312 C66,240 76,150 86,56 Z", bag)),
        _path(seal, _shade(bag, 0.22)),
        _line("M88,48 L312,48", 1.0, ' stroke-dasharray="4 4"'),
        _line("M96,72 C90,150 84,230 80,300", 9, ' stroke-opacity=".22"', "#ffffff"),
        *_panel(108, 74, 184, 66, label, 36),
        _tag("window", _path(_disc(200, 232, 104, 74), _shade(choc, 0.55), 2.0, stroke=_mix(bag, "#ffffff", 0.5))),
    ]  # fmt: skip
    r = 21.0
    for row, y in enumerate((186.0, 218.0, 250.0, 280.0)):
        half = 104 * (1 - ((y - 232) / 74) ** 2) ** 0.5 - r
        n = max(1, int(2 * half // (2 * r)) + 1)
        span = 2 * r * (n - 1)
        out += [
            p
            for i in range(n)
            for p in draw(
                200 - span / 2 + 2 * r * i + (r * 0.5 if row % 2 else 0), y, r, choc, gloss
            )
        ]
    out.append(_line(_disc(200, 232, 104, 74), 2.0, stroke=_mix(bag, "#ffffff", 0.5)))
    out.append(_line("M136,184 C150,172 168,166 186,164", 6, ' stroke-opacity=".45"', "#ffffff"))
    for x, y in ((92, 334), (140, 348), (196, 340), (252, 350), (306, 334)):
        out += draw(x, y, 24.0, choc, gloss)
    ground = (f'<ellipse class="ground" cx="200" cy="{CENTER_Y + (364 - CENTER_Y) * k:.1f}" '
              f'rx="{170 * k:.1f}" ry="11" fill="#000000" fill-opacity=".14"/>')  # fmt: skip
    return [GLOSS.format(gloss), ground, *_scaled(k, out, "sharing-bag")]


#: A hot chocolate's drawn size (a tub of drinking chocolate): the weight at and above which it
#: is the full one, and its smallest scale.
HOT_FULL_G, HOT_SMALLEST = 400.0, 0.9
#: A chocolate orange's: the same.
ORANGE_FULL_G, ORANGE_SMALLEST = 175.0, 0.9
#: The steam over a filled mug, and the segments a chocolate orange shows from its pole.
STEAM = "#9a9a9a"
ORANGE_MERIDIANS = (-72.0, -48.0, -24.0, 0.0, 24.0, 48.0, 72.0)
#: Where the dimples of the orange's peel, pressed into its chocolate, sit on the ball (in radii).
ORANGE_DIMPLES = ((-0.5, -0.35), (-0.2, -0.55), (0.25, -0.4), (0.55, -0.15), (-0.62, 0.1),
                  (-0.3, 0.05), (0.1, -0.1), (0.38, 0.2), (-0.45, 0.45), (0.0, 0.35),
                  (0.6, 0.42), (-0.1, 0.65), (0.3, 0.62), (0.15, -0.7))  # fmt: skip


def hot_chocolate(
    paint: str, fill: Fill, label: str | None, pack_size: str | None = None,
    chocolate: str | None = None,
) -> list[str]:  # fmt: skip
    """A tub of drinking chocolate and, in front of it, a mug filled with it: the tub is the
    flavour's color (:func:`wrapper_color`) under a lid in its shade, with the label panel and
    a sheen down its left side; the mug's cocoa is the ``chocolate`` the drink is made of,
    glossed, a swirl on it and steam above. A tub under :data:`HOT_FULL_G` is drawn smaller
    (:func:`own_scale`)."""
    k = own_scale(pack_size, HOT_FULL_G, HOT_SMALLEST)
    choc = chocolate_color(chocolate, fill.base)
    tub = wrapper_color(fill.base) if fill.pattern == "solid" else paint
    lid = _shade(tub, 0.3)
    mug = _mix(tub, "#ffffff", 0.78)
    gloss = f"choc-gloss-{choc[1:]}"
    out = [
        _tag("wrapper", _path("M44,72 L276,72 L276,326 C276,340 224,350 160,350 "
                              "C96,350 44,340 44,326 Z", tub)),
        _line("M60,104 C58,180 58,250 60,316", 10, ' stroke-opacity=".22"', "#ffffff"),
        _tag("lid", _path("M38,44 L282,44 L282,88 C282,98 228,106 160,106 "
                          "C92,106 38,98 38,88 Z", lid)),
        _path(_disc(160, 44, 122, 20), _mix(lid, "#ffffff", 0.18)),
        _line("M40,80 C80,92 240,92 280,80", 1.2, ' stroke-opacity=".5"'),
        *_panel(64, 130, 192, 92, label, 38),
        _tag("mug", _path("M202,214 L340,214 L332,340 C332,350 306,356 271,356 "
                          "C236,356 210,350 210,340 Z", mug)),
        _tag("mug", _path("M338,234 C384,228 386,318 330,314 L331,296 C362,298 362,250 337,252 Z", mug)),
        _path(_disc(271, 214, 69, 16), _mix(mug, "#ffffff", 0.4)),
        *_chocolate(_disc(271, 216, 60, 12), _disc(271, 218, 60, 12),
                    [_line("M244,216 C258,208 286,210 296,218 C286,224 262,222 258,216", 1.4,
                           stroke=_mix(choc, "#ffffff", 0.45))], choc, gloss),
        _line("M246,196 C234,178 260,170 248,150 M276,194 C264,172 292,166 280,140 "
              "M304,198 C294,182 318,176 308,158", 3, ' stroke-opacity=".6"', STEAM),
    ]  # fmt: skip
    ground = (f'<ellipse class="ground" cx="200" cy="{CENTER_Y + (360 - CENTER_Y) * k:.1f}" '
              f'rx="{170 * k:.1f}" ry="11" fill="#000000" fill-opacity=".14"/>')  # fmt: skip
    return [GLOSS.format(gloss), ground, *_scaled(k, out, "hot-chocolate")]


def _meridian(cx: float, cy: float, r: float, phi: float) -> str:
    """A groove between two segments of a ball of radius ``r``: the meridian at ``phi``
    degrees from the front, seen from a little above, from the top pole to the foot."""
    bulge = r * math.sin(math.radians(phi)) * 1.33
    top, foot = cy - r * 0.86, cy + r
    return (f"M{cx:.1f},{top:.1f} C{cx + bulge:.1f},{top + r * 0.3:.1f} "
            f"{cx + bulge:.1f},{foot - r * 0.4:.1f} {cx + bulge * 0.12:.1f},{foot:.1f}")  # fmt: skip


def _segment(cx: float, cy: float, w: float, h: float, angle: float, choc: str,
             gloss: str) -> list[str]:  # fmt: skip
    """One segment of a chocolate orange lying loose: its rounded outer face and the flat
    inner face it broke from the ball along."""
    top = (f"M{cx - w / 2:.1f},{cy:.1f} C{cx - w / 2:.1f},{cy - h:.1f} {cx + w / 2:.1f},{cy - h:.1f} "
           f"{cx + w / 2:.1f},{cy:.1f} Z")  # fmt: skip
    edge = _rect(cx - w / 2 + 3, cy - 2, w - 6, h * 0.3)
    groove = _line(f"M{cx - w * 0.3:.1f},{cy - h * 0.3:.1f} C{cx - w * 0.1:.1f},{cy - h * 0.6:.1f} "
                   f"{cx + w * 0.1:.1f},{cy - h * 0.6:.1f} {cx + w * 0.3:.1f},{cy - h * 0.3:.1f}",
                   1.2, stroke=_shade(choc, 0.45))  # fmt: skip
    return _chocolate(top, edge, [groove], choc, gloss, f"rotate({angle:g} {cx:.1f} {cy:.1f})")


def chocolate_orange(
    paint: str, fill: Fill, label: str | None, pack_size: str | None = None,
    chocolate: str | None = None,
) -> list[str]:  # fmt: skip
    """A chocolate orange: a ball of segments in the ``chocolate`` it is made of, glossed, its
    grooves running from the top pole, sitting in its opened foil (the flavour's color, kept
    visible on white paper by :func:`wrapper_color`), two loose segments in front and the
    label panel on the foil. An orange under :data:`ORANGE_FULL_G` is drawn smaller
    (:func:`own_scale`)."""
    k = own_scale(pack_size, ORANGE_FULL_G, ORANGE_SMALLEST)
    choc = chocolate_color(chocolate, fill.base)
    foil = wrapper_color(fill.base) if fill.pattern == "solid" else paint
    gloss = f"choc-gloss-{choc[1:]}"
    cx, cy, r = 200.0, 166.0, 138.0
    petals = " ".join(
        f"{'M' if i == 0 else 'L'}{200 + rx * math.cos(math.radians(a)):.1f},{298 + ry * math.sin(math.radians(a)):.1f}"
        for i, a in enumerate(range(0, 360, 12))
        for rx, ry in [(176, 66) if i % 2 == 0 else (150, 52)]
    )
    grooves = [
        _line(_meridian(cx, cy, r, phi), 1.6, stroke=_shade(choc, 0.5)) for phi in ORANGE_MERIDIANS
    ]
    dimples = [
        _path(
            _disc(cx + r * u, cy + r * v, 3.2, 2.4),
            _shade(choc, 0.25),
            0.6,
            stroke=_shade(choc, 0.4),
        )
        for u, v in ORANGE_DIMPLES
    ]
    crinkles = " ".join(
        f"M{200 + 70 * math.cos(math.radians(a)):.1f},{298 + 26 * math.sin(math.radians(a)):.1f} "
        f"L{200 + 158 * math.cos(math.radians(a)):.1f},{298 + 58 * math.sin(math.radians(a)):.1f}"
        for a in range(6, 360, 24)
    )
    out = [
        _tag("wrapper", _path(f"{petals} Z", foil)),
        _line(crinkles, 1.2, ' stroke-opacity=".55"', _mix(foil, "#ffffff", 0.5)),
        *_chocolate(_disc(cx, cy, r, r), _disc(cx, cy + 8, r * 0.98, r), [*grooves, *dimples], choc, gloss),
        _path(_disc(cx, cy - r * 0.86, 12, 5), _shade(choc, 0.2), 1.2, stroke=_shade(choc, 0.5)),
        *_panel(128, 318, 144, 38, label, 22),
    ]  # fmt: skip
    out += _segment(70, 336, 76, 50, -16, choc, gloss)
    out += _segment(330, 340, 76, 50, 14, choc, gloss)
    ground = (f'<ellipse class="ground" cx="200" cy="{CENTER_Y + (366 - CENTER_Y) * k:.1f}" '
              f'rx="{176 * k:.1f}" ry="11" fill="#000000" fill-opacity=".14"/>')  # fmt: skip
    return [GLOSS.format(gloss), ground, *_scaled(k, out, "chocolate-orange")]


register(
    {
        "chocolate_box": chocolate_box,
        "chocolate_bar": chocolate_bar,
        "chocolate_bag": chocolate_bag,
        "hot_chocolate": hot_chocolate,
        "chocolate_orange": chocolate_orange,
    }
)
