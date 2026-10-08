"""Brand house styles for the industrial drawings: an OPT-IN render path, default off.

The catalog's own drawing (:func:`synthetic_industrial_products.drawing.
draw_product`) is unchanged and stays the default: :func:`render` returns its
bytes untouched unless ``house=True``, and ``test_industrial_styles.py`` pins that
the default render of the whole golden catalog is byte-identical to the
committed ``images.jsonl``. Adopting the house style in the emitted catalog is
a later, separate change.

With ``house=True`` the product is drawn by the catalog's own painter (its
figure, scale, fill and section hatch, unchanged) and then dressed in its
brand's row of :data:`HOUSE_STYLES`. A row sets, in an industrial visual
language:

* the sheet: ``paper`` (two brands on blueprint-tinted paper), a faint
  ``texture`` (blueprint or millimetre grid, dots, brushed plate), a ``frame``
  (rule, double, heavy, rounded, corner brackets, rivet corners, or an
  engineering-drawing border with zone ticks) and an optional hazard-stripe
  ``band``, used by six brands of forty-five;
* the product's outline: ``ink`` colour, stroke ``weight`` and ``joins``;
  the product's fill and hatch belong to the record and never change;
* the logo: a ``mark`` built from simple shapes (gear teeth, a hex nut, a
  triangle of bolts, chevrons, a crosshair...), optionally inside an
  ``enclose`` outline, set in a ``layout`` (riveted plate, badge, title
  block, colour band, stencil bar, inspection stamp, or mark beside or above
  the name) at ``place``;
* the name: ``font`` (DIN, condensed, stencil, slab, impact...), ``weight``,
  ``case`` and ``spacing``.

The opt-in drawing carries the brand's name as text. The default drawing is
text-free by ruling (``svg_problems``); adopting this path needs that ruling
revisited for the wordmark.

The domain-neutral machinery is ``prototypes/house_kit.py``, shared with
``retail_drawings``.
"""

# ruff: noqa: E501 -- SVG literals and the style table read better whole (prototype only).

from __future__ import annotations

import math
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import house_kit as hk  # noqa: E402

from synthetic_industrial_products.catalog import brands  # noqa: E402
from synthetic_industrial_products.drawing import (  # noqa: E402
    FIGURES,
    draw_product,
    product_scale_for,
)
from synthetic_industrial_products.drawing import svg as sheet_svg  # noqa: E402
from synthetic_industrial_products.drawing.sheet import paint  # noqa: E402
from synthetic_industrial_products.drawing.style import HouseStyle as SheetStyle  # noqa: E402
from synthetic_industrial_products.drawing.style import material_hatch, part_fill  # noqa: E402
from synthetic_industrial_products.render.marking import (  # noqa: E402
    FINISH_ATTRIBUTES,
    MATERIAL_ATTRIBUTES,
)

W, H = sheet_svg.WIDTH, sheet_svg.HEIGHT  # 200 x 300, the catalog's sheet
EDGE = 14  # gap between the sheet's edge and a logo
MARK = 28  # px across: 14% of the sheet's width
NAME_SIZE = 13.0
NAME_MIN = 7.5
SCALE = 0.78  # the product, shrunk to make room for the logo
HAZARD_H = 6  # the hazard band's height
HAZARD_INSET = 13
WHITE = "#ffffff"

FONTS = {
    "din": "'DIN Alternate', 'Barlow', Helvetica, Arial, sans-serif",
    "condensed": "'DIN Condensed', 'Arial Narrow', 'Roboto Condensed', sans-serif",
    "stencil": "Stencil, 'Stencil Std', 'Arial Black', sans-serif",
    "slab": "Rockwell, 'Roboto Slab', 'Courier New', serif",
    "impact": "Impact, 'Haettenschweiler', 'Arial Narrow', sans-serif",
    "grotesk": "'Helvetica Neue', Helvetica, Arial, sans-serif",
    "futura": "Futura, 'Century Gothic', 'Trebuchet MS', sans-serif",
    "mono": "'Courier New', Courier, monospace",
}
#: Average glyph advance per em, for laying out a name without a font engine.
ADVANCE = {
    "din": 0.55,
    "condensed": 0.42,
    "stencil": 0.62,
    "slab": 0.58,
    "impact": 0.45,
    "grotesk": 0.56,
    "futura": 0.56,
    "mono": 0.6,
}
TEXTURES = ("none", "blueprint", "grid", "dots", "brushed")
FRAMES = ("none", "rule", "double", "heavy", "rounded", "corners", "rivets", "drawing")
BANDS = ("none", "hazard_top", "hazard_bottom")
ENCLOSURES = ("none", "circle", "hex", "square", "shield", "diamond")
LAYOUTS = (
    "plate",
    "badge",
    "title_block",
    "band_top",
    "band_bottom",
    "stencil_bar",
    "stamp",
    "mark_left",
    "mark_above",
)
PLACES = ("top_left", "top_centre", "top_right", "bottom_left", "bottom_centre", "bottom_right")
CASES = ("caps", "title")

#: Layout -> the lockup's height in px.
LOCKUP_HEIGHT = {
    "plate": 32,
    "badge": 30,
    "title_block": 46,
    "band_top": 36,
    "band_bottom": 36,
    "stencil_bar": 30,
    "stamp": 30,
    "mark_left": MARK,
    "mark_above": MARK + 3 + 12,
}
TITLE_BLOCK_W = 150
TITLE_MARK_CELL = 32
TITLE_TOP_ROW = 30


@dataclass(frozen=True)
class HouseStyle:
    """One industrial brand's look. See the module docstring for each field."""

    paper: str
    texture: str
    frame: str
    band: str
    colour: str
    ink: str
    stroke: float  # outline weight, 1.0 = the catalog's own at full size
    joins: str  # round | sharp
    mark: str
    enclose: str
    layout: str
    place: str
    font: str
    weight: int  # 400 | 700
    case: str
    spacing: float  # letter-spacing, px
    italic: bool = False

    def __post_init__(self) -> None:
        checks = (
            ("texture", TEXTURES),
            ("frame", FRAMES),
            ("band", BANDS),
            ("joins", ("round", "sharp")),
            ("mark", tuple(MARKS)),
            ("enclose", ENCLOSURES),
            ("layout", LAYOUTS),
            ("place", PLACES),
            ("font", tuple(FONTS)),
            ("weight", (400, 700)),
            ("case", CASES),
        )
        for name, allowed in checks:
            if getattr(self, name) not in allowed:
                raise ValueError(f"{name}={getattr(self, name)!r}; one of {allowed}")
        fixed = {"band_top": ("top_centre",), "band_bottom": ("bottom_centre",)}
        fixed["title_block"] = ("bottom_left", "bottom_right")
        if self.layout in fixed and self.place not in fixed[self.layout]:
            raise ValueError(f"a {self.layout} sits at {fixed[self.layout]}")
        if self.stroke < 1.0:
            raise ValueError("the outline never drops below the catalog's own weight")

    @property
    def top_logo(self) -> bool:
        return self.place.startswith("top")


# --------------------------------------------------------------------------
# Marks: simple machine shapes in unit space (-1..1), painted in one colour.
# Holes are true holes (even-odd fill), so a mark reads on a plate as well
# as on paper.
# --------------------------------------------------------------------------

n = hk.n


def _circle_d(x: float, y: float, r: float) -> str:
    return f"M{n(x + r)},{n(y)} A{n(r)},{n(r)} 0 1 0 {n(x - r)},{n(y)} A{n(r)},{n(r)} 0 1 0 {n(x + r)},{n(y)} Z"


def _holed(d: str, c: str) -> str:
    return f'<path d="{d}" fill="{c}" fill-rule="evenodd"/>'


def _gear_d(teeth: int, outer: float, root: float) -> str:
    pts = []
    step = 2 * math.pi / teeth
    for k in range(teeth):
        a = k * step - math.pi / 2
        for da, r in ((-0.3, root), (-0.18, outer), (0.18, outer), (0.3, root)):
            pts.append((r * math.cos(a + da * step * 1.6), r * math.sin(a + da * step * 1.6)))
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts) + " Z"


def m_gear(c: str) -> list[str]:
    return [_holed(_gear_d(8, 0.96, 0.72) + " " + _circle_d(0, 0, 0.3), c)]


def m_gear_fine(c: str) -> list[str]:
    return [_holed(_gear_d(14, 0.96, 0.8) + " " + _circle_d(0, 0, 0.55), c), hk.dot(0, 0, 0.2, c)]


def m_hex_nut(c: str) -> list[str]:
    return [_holed(hk.polygon_d(0, 0, 0.96, 6) + " " + _circle_d(0, 0, 0.42), c)]


def m_bolt_triangle(c: str) -> list[str]:
    centres = [(0.6 * math.cos(a), 0.6 * math.sin(a) + 0.1) for a in (-math.pi / 2, math.pi / 6, 5 * math.pi / 6)]
    d = " ".join(hk.polygon_d(x, y, 0.34, 6) + " " + _circle_d(x, y, 0.13) for x, y in centres)
    tri = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in centres) + " Z"
    return [
        f'<path d="{tri}" fill="none" stroke="{c}" stroke-width=".09"/>',
        _holed(d, c),
    ]


def m_chevrons(c: str) -> list[str]:
    return [
        f'<path d="M-.74,{n(y + 0.36)} L0,{n(y - 0.3)} L.74,{n(y + 0.36)}" fill="none" stroke="{c}" stroke-width=".26" stroke-linejoin="miter"/>'
        for y in (-0.3, 0.32)
    ]


def m_chevron_trio(c: str) -> list[str]:
    return [
        f'<path d="M{n(x - 0.22)},-.7 L{n(x + 0.24)},0 L{n(x - 0.22)},.7" fill="none" stroke="{c}" stroke-width=".2" stroke-linejoin="miter"/>'
        for x in (-0.52, 0, 0.52)
    ]


def m_crosshair(c: str) -> list[str]:
    d = "M0,-.96 L0,-.3 M0,.3 L0,.96 M-.96,0 L-.3,0 M.3,0 L.96,0"
    return [
        hk.ring(0, 0, 0.64, 0.12, c),
        f'<path d="{d}" fill="none" stroke="{c}" stroke-width=".12"/>',
        hk.dot(0, 0, 0.1, c),
    ]


def m_bolt_square(c: str) -> list[str]:
    return [
        f'<rect x="-.72" y="-.72" width="1.44" height="1.44" fill="none" stroke="{c}" stroke-width=".1"/>',
        *[hk.dot(x, y, 0.17, c) for x in (-0.72, 0.72) for y in (-0.72, 0.72)],
        _holed(hk.polygon_d(0, 0, 0.32, 6) + " " + _circle_d(0, 0, 0.12), c),
    ]


def m_bearing(c: str) -> list[str]:
    balls = [hk.dot(0.64 * math.cos(a), 0.64 * math.sin(a), 0.15, c) for a in (k * math.pi / 4 for k in range(8))]
    return [hk.ring(0, 0, 0.9, 0.12, c), hk.ring(0, 0, 0.38, 0.12, c), *balls]


def m_torx(c: str) -> list[str]:
    return [hk.star(0, 0, 0.82, c, points=6, inner=0.62).replace("/>", f' stroke="{c}" stroke-width=".18" stroke-linejoin="round"/>')]


def m_phillips(c: str) -> list[str]:
    a, b = 0.13, 0.6
    cross = f"M{-a},{-b} L{a},{-b} L{a},{-a} L{b},{-a} L{b},{a} L{a},{a} L{a},{b} L{-a},{b} L{-a},{a} L{-b},{a} L{-b},{-a} L{-a},{-a} Z"
    return [_holed(_circle_d(0, 0, 0.92) + " " + cross, c)]


def m_ibeam(c: str) -> list[str]:
    d = "M-.76,-.82 L.76,-.82 L.76,-.54 L.15,-.54 L.15,.54 L.76,.54 L.76,.82 L-.76,.82 L-.76,.54 L-.15,.54 L-.15,-.54 L-.76,-.54 Z"
    return [f'<path d="{d}" fill="{c}"/>']


def m_knurl(c: str) -> list[str]:
    s = 0.78
    segs = []
    for k in (-s, 0.0, s):
        if k >= 0:
            segs.append(((-s + k, -s), (s, s - k)))
            segs.append(((s, k - s), (k - s, s)))
        else:
            segs.append(((-s, -s - k), (s + k, s)))
            segs.append(((k + s, -s), (-s, k + s)))
    d = " ".join(f"M{n(a[0])},{n(a[1])} L{n(b[0])},{n(b[1])}" for a, b in segs)
    return [
        f'<rect x="{-s}" y="{-s}" width="{2 * s}" height="{2 * s}" fill="none" stroke="{c}" stroke-width=".12"/>',
        f'<path d="{d}" fill="none" stroke="{c}" stroke-width=".1"/>',
    ]


def m_spark(c: str) -> list[str]:
    return [hk.star(0, 0, 0.96, c, points=4, inner=0.3)]


def m_delta(c: str) -> list[str]:
    return [
        f'<path d="M0,-.82 L.9,.72 L-.9,.72 Z" fill="none" stroke="{c}" stroke-width=".14" stroke-linejoin="miter"/>',
        hk.dot(0, 0.22, 0.2, c),
    ]


def m_speed_bars(c: str) -> list[str]:
    d = " ".join(f"M{n(x - 0.1)},.7 L{n(x + 0.3)},-.7 L{n(x + 0.56)},-.7 L{n(x + 0.16)},.7 Z" for x in (-0.86, -0.36, 0.14))
    return [f'<path d="{d}" fill="{c}"/>']


def m_hex_socket(c: str) -> list[str]:
    return [_holed(_circle_d(0, 0, 0.92) + " " + hk.polygon_d(0, 0, 0.46, 6, math.pi / 6), c)]


def m_rivet_row(c: str) -> list[str]:
    return [
        f'<rect x="-.94" y="-.3" width="1.88" height=".6" rx=".3" fill="none" stroke="{c}" stroke-width=".1"/>',
        *[hk.dot(x, 0, 0.17, c) for x in (-0.6, 0, 0.6)],
        f'<path d="M-.94,-.62 L.94,-.62 M-.94,.62 L.94,.62" stroke="{c}" stroke-width=".1"/>',
    ]


def m_square_drive(c: str) -> list[str]:
    return [hk.ring(0, 0, 0.88, 0.12, c), f'<path d="{hk.diamond(0, 0, 0.52)}" fill="{c}"/>']


def m_thread(c: str) -> list[str]:
    d = " ".join(f"M-.42,{n(y + 0.14)} L.42,{n(y - 0.14)}" for y in (-0.6, -0.3, 0, 0.3, 0.6))
    return [
        f'<rect x="-.42" y="-.92" width=".84" height="1.84" fill="none" stroke="{c}" stroke-width=".11"/>',
        f'<path d="{d}" fill="none" stroke="{c}" stroke-width=".11"/>',
    ]


def m_bolt_circle(c: str) -> list[str]:
    d = _circle_d(0, 0, 0.9) + " " + _circle_d(0, 0, 0.32) + " " + " ".join(
        _circle_d(0.61 * math.cos(a), 0.61 * math.sin(a), 0.12) for a in (k * math.pi / 3 for k in range(6))
    )
    return [_holed(d, c)]


#: Motif name -> drawing in unit space, painted in the brand colour.
MARKS = hk.register_marks(globals())

_ENCLOSURE = {
    "circle": lambda c: hk.ring(0, 0, 0.94, 0.1, c),
    "hex": lambda c: f'<path d="{hk.polygon_d(0, 0, 0.98, 6, math.pi / 6)}" fill="none" stroke="{c}" stroke-width=".1"/>',
    "square": lambda c: f'<rect x="-.9" y="-.9" width="1.8" height="1.8" fill="none" stroke="{c}" stroke-width=".1"/>',
    "shield": lambda c: f'<path d="M-.82,-.92 L.82,-.92 L.82,.08 Q.82,.7 0,.98 Q-.82,.7 -.82,.08 Z" fill="none" stroke="{c}" stroke-width=".1"/>',
    "diamond": lambda c: f'<path d="{hk.diamond(0, 0, 0.98)}" fill="none" stroke="{c}" stroke-width=".1"/>',
}


def mark_svg(style: HouseStyle, cx: float, cy: float, size: float, colour: str) -> str:
    """``style``'s mark (motif, in its enclosure if any), ``size`` px across at (cx, cy)."""
    motif = "".join(MARKS[style.mark](colour))
    if style.enclose == "none":
        return hk.mark_group(motif, cx, cy, size)
    body = _ENCLOSURE[style.enclose](colour) + f'<g transform="scale(.56)">{motif}</g>'
    return hk.mark_group(body, cx, cy, size)


# --------------------------------------------------------------------------
# Names
# --------------------------------------------------------------------------


def text_width(style: HouseStyle, text: str, size: float) -> float:
    return hk.text_width(ADVANCE[style.font], style, text, size)


def name_size(style: HouseStyle, text: str, max_width: float, start: float = NAME_SIZE) -> float:
    return hk.fit_size(ADVANCE[style.font], style, text, max_width, start, NAME_MIN)


def wordmark(style: HouseStyle, text: str, x: float, y: float, size: float, colour: str, anchor: str = "start") -> str:
    return hk.wordmark(FONTS[style.font], style, text, x, y, size, colour, anchor)


def on(fill: str) -> str:
    """Type and mark colour that reads on ``fill``: white on a dark fill, near-black on a light one."""
    r, g, b = (int(fill[i : i + 2], 16) for i in (1, 3, 5))
    return "#1b1b1b" if 0.299 * r + 0.587 * g + 0.114 * b > 160 else WHITE


#: Layout -> the widest the name may be set, px.
def name_room(style: HouseStyle) -> float:
    if style.layout == "title_block":
        return TITLE_BLOCK_W - TITLE_MARK_CELL - 10
    if style.layout == "mark_above":
        return W - 2 * EDGE
    inner = {"plate": 22, "badge": 22, "stamp": 20, "stencil_bar": 22, "band_top": 24, "band_bottom": 24}
    return W - 2 * EDGE - inner.get(style.layout, MARK) - 22


# --------------------------------------------------------------------------
# Sheet: paper, texture, frame, hazard band
# --------------------------------------------------------------------------

TEXTURE_TILES = {
    "blueprint": (10, '<path d="M0,9.5 L10,9.5 M9.5,0 L9.5,10" stroke="{c}" stroke-opacity=".16" stroke-width=".6"/>'),
    "grid": (5, '<path d="M0,4.75 L5,4.75 M4.75,0 L4.75,5" stroke="{c}" stroke-opacity=".07" stroke-width=".5"/>'),
    "dots": (8, '<circle cx="4" cy="4" r=".7" fill="{c}" fill-opacity=".2"/>'),
    "brushed": (6, '<path d="M0,1.5 L6,1.5 M0,4.2 L4,4.2" stroke="{c}" stroke-opacity=".07" stroke-width=".5"/>'),
}


def _frame(style: HouseStyle) -> list[str]:
    c, f = style.colour, style.frame
    if f == "rule":
        return [f'<rect x="6" y="6" width="{W - 12}" height="{H - 12}" fill="none" stroke="{c}" stroke-width="1"/>']
    if f == "double":
        return [
            f'<rect x="5" y="5" width="{W - 10}" height="{H - 10}" fill="none" stroke="{c}" stroke-width="1.4"/>',
            f'<rect x="9" y="9" width="{W - 18}" height="{H - 18}" fill="none" stroke="{c}" stroke-width=".6"/>',
        ]
    if f == "heavy":
        return [f'<rect x="6" y="6" width="{W - 12}" height="{H - 12}" fill="none" stroke="{c}" stroke-width="3.2"/>']
    if f == "rounded":
        return [f'<rect x="6" y="6" width="{W - 12}" height="{H - 12}" rx="12" fill="none" stroke="{c}" stroke-width="1.6"/>']
    if f == "corners":
        a, b, t = 6, (W - 6, H - 6), 18
        d = (
            f"M{a},{a + t} L{a},{a} L{a + t},{a} M{b[0] - t},{a} L{b[0]},{a} L{b[0]},{a + t} "
            f"M{b[0]},{b[1] - t} L{b[0]},{b[1]} L{b[0] - t},{b[1]} M{a + t},{b[1]} L{a},{b[1]} L{a},{b[1] - t}"
        )
        return [f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="square"/>']
    if f == "rivets":
        rivets = [
            hk.dot(x, y, 2.4, c) + hk.dot(x - 0.7, y - 0.7, 0.8, WHITE, ' fill-opacity=".7"')
            for x in (12, W - 12)
            for y in (12, H - 12)
        ]
        return [f'<rect x="6" y="6" width="{W - 12}" height="{H - 12}" rx="3" fill="none" stroke="{c}" stroke-width="1.2"/>', *rivets]
    if f == "drawing":
        # An engineering-drawing border: outer and inner rules, zone ticks between.
        ticks = []
        for k in (1, 2, 3):
            x = W * k / 4
            ticks += [f"M{n(x)},4 L{n(x)},10", f"M{n(x)},{H - 4} L{n(x)},{H - 10}"]
        for k in (1, 2, 3, 4, 5):
            y = H * k / 6
            ticks += [f"M4,{n(y)} L10,{n(y)}", f"M{W - 4},{n(y)} L{W - 10},{n(y)}"]
        return [
            f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="none" stroke="{c}" stroke-width=".8"/>',
            f'<rect x="10" y="10" width="{W - 20}" height="{H - 20}" fill="none" stroke="{c}" stroke-width="1.4"/>',
            f'<path d="{" ".join(ticks)}" fill="none" stroke="{c}" stroke-width=".8"/>',
        ]
    return []


def _hazard(style: HouseStyle, uid: str) -> tuple[str, list[str]]:
    """(pattern def, the band) for a hazard-stripe band, or ``("", [])``."""
    if style.band == "none":
        return "", []
    pid = f"haz-{uid}"
    y = HAZARD_INSET if style.band == "hazard_top" else H - HAZARD_INSET - HAZARD_H
    pattern = (
        f'<pattern id="{pid}" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="8" height="8" fill="#f2c200"/><rect width="4" height="8" fill="#1f1f1f"/></pattern>'
    )
    return pattern, [
        f'<rect x="{HAZARD_INSET}" y="{y}" width="{W - 2 * HAZARD_INSET}" height="{HAZARD_H}" fill="url(#{pid})"/>'
    ]


def _side_offset(style: HouseStyle, top: bool) -> float:
    """Extra room a hazard band takes on the logo's side of the sheet."""
    side = "hazard_top" if top else "hazard_bottom"
    return HAZARD_H + 4 if style.band == side else 0


# --------------------------------------------------------------------------
# Logos
# --------------------------------------------------------------------------


def _x_for(place: str, width: float) -> float:
    if place.endswith("left"):
        return EDGE + 2
    if place.endswith("right"):
        return W - EDGE - 2 - width
    return (W - width) / 2


def _y_for(style: HouseStyle, h: float) -> float:
    top = style.top_logo
    off = _side_offset(style, top)
    return EDGE + off if top else H - EDGE - off - h


def _mark_and_name(style: HouseStyle, brand: str, x0: float, cy: float, mk: float, size: float, mark_c: str, name_c: str) -> list[str]:
    return [
        mark_svg(style, x0 + mk / 2, cy, mk, mark_c),
        wordmark(style, brand, x0 + mk + 7, cy + size * 0.36, size, name_c),
    ]


def _title_block(style: HouseStyle, brand: str) -> list[str]:
    c, w, h = style.colour, TITLE_BLOCK_W, LOCKUP_HEIGHT["title_block"]
    x0 = W - 10 - w if style.place == "bottom_right" else 10
    y0 = H - 10 - h - _side_offset(style, False)
    cell = TITLE_MARK_CELL
    size = name_size(style, brand, name_room(style), 12)
    thirds = [x0 + w * k / 3 for k in (1, 2)]
    grid = (
        f"M{n(x0)},{n(y0 + TITLE_TOP_ROW)} L{n(x0 + w)},{n(y0 + TITLE_TOP_ROW)} "
        f"M{n(x0 + cell)},{n(y0)} L{n(x0 + cell)},{n(y0 + TITLE_TOP_ROW)} "
        + " ".join(f"M{n(x)},{n(y0 + TITLE_TOP_ROW)} L{n(x)},{n(y0 + h)}" for x in thirds)
    )
    # Filled-in fields of a drawing form, as faint strokes rather than words.
    fields = " ".join(
        f"M{n(x + 5)},{n(y0 + TITLE_TOP_ROW + 7)} L{n(x + w / 3 - 12)},{n(y0 + TITLE_TOP_ROW + 7)} "
        f"M{n(x + 5)},{n(y0 + TITLE_TOP_ROW + 11.5)} L{n(x + w / 6)},{n(y0 + TITLE_TOP_ROW + 11.5)}"
        for x in (x0, *thirds)
    )
    return [
        f'<rect x="{n(x0)}" y="{n(y0)}" width="{w}" height="{h}" fill="{style.paper}" stroke="{c}" stroke-width="1.2"/>',
        f'<path d="{grid}" fill="none" stroke="{c}" stroke-width=".7"/>',
        f'<path d="{fields}" fill="none" stroke="{style.ink}" stroke-opacity=".35" stroke-width="1.2"/>',
        mark_svg(style, x0 + cell / 2, y0 + TITLE_TOP_ROW / 2, 22, c),
        wordmark(style, brand, x0 + cell + 5, y0 + TITLE_TOP_ROW / 2 + size * 0.36, size, style.ink),
    ]


def logo(style: HouseStyle, brand: str) -> list[str]:
    c, lay = style.colour, style.layout
    h = LOCKUP_HEIGHT[lay]
    if lay == "title_block":
        return _title_block(style, brand)
    size = name_size(style, brand, name_room(style))
    if lay in ("band_top", "band_bottom"):
        y0 = 0 if lay == "band_top" else H - h
        mk = 24
        w = mk + 7 + text_width(style, brand, size)
        x0 = (W - w) / 2
        ink = on(c)
        return [
            f'<rect x="0" y="{y0}" width="{W}" height="{h}" fill="{c}"/>',
            *_mark_and_name(style, brand, x0, y0 + h / 2, mk, size, ink, ink),
        ]
    if lay == "mark_above":
        size = name_size(style, brand, name_room(style), 12)
        w = max(MARK, text_width(style, brand, size))
        cx = _x_for(style.place, w) + w / 2
        y0 = _y_for(style, h)
        return [
            mark_svg(style, cx, y0 + MARK / 2, MARK, c),
            wordmark(style, brand, cx, y0 + MARK + 3 + size * 0.8, size, style.ink, "middle"),
        ]
    if lay == "mark_left":
        w = MARK + 7 + text_width(style, brand, size)
        x0 = _x_for(style.place, w)
        return _mark_and_name(style, brand, x0, _y_for(style, h) + h / 2, MARK, size, c, style.ink)
    mk = h - 10
    tw = text_width(style, brand, size)
    w = 8 + mk + 7 + tw + 8
    x0 = _x_for(style.place, w)
    y0 = _y_for(style, h)
    cy = y0 + h / 2
    if lay == "plate":
        ink = on(c)
        rivets = "".join(
            hk.dot(x, y, 1.3, ink, ' fill-opacity=".55"') for x in (x0 + 3.5, x0 + w - 3.5) for y in (y0 + 3.5, y0 + h - 3.5)
        )
        return [
            f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{h}" rx="2" fill="{c}"/>',
            rivets,
            *_mark_and_name(style, brand, x0 + 8, cy, mk, size, ink, ink),
        ]
    if lay == "badge":
        return [
            f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{h}" rx="6" fill="{WHITE}" stroke="{c}" stroke-width="1.4"/>',
            *_mark_and_name(style, brand, x0 + 8, cy, mk, size, c, c),
        ]
    if lay == "stencil_bar":
        return [
            f'<path d="M{n(x0)},{n(y0 + 1)} L{n(x0 + w)},{n(y0 + 1)} M{n(x0)},{n(y0 + h - 1)} L{n(x0 + w)},{n(y0 + h - 1)}" stroke="{c}" stroke-width="2.4"/>',
            *_mark_and_name(style, brand, x0 + 8, cy, mk, size, c, style.ink),
        ]
    # stamp: an inspection stamp, double-ruled and set a few degrees off square
    return [
        f'<g transform="rotate(-3 {n(x0 + w / 2)} {n(cy)})">'
        f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{h}" fill="none" stroke="{c}" stroke-width="1.6"/>'
        f'<rect x="{n(x0 + 2.5)}" y="{n(y0 + 2.5)}" width="{n(w - 5)}" height="{h - 5}" fill="none" stroke="{c}" stroke-width=".6"/>'
        + "".join(_mark_and_name(style, brand, x0 + 8, cy, mk, size, c, c))
        + "</g>"
    ]


# --------------------------------------------------------------------------
# The product, painted by the catalog and placed clear of the logo
# --------------------------------------------------------------------------


def product_transform(style: HouseStyle) -> str:
    """Shrink the product to :data:`SCALE` and move it clear of the logo.

    The catalog paints inside an 18 px margin, so the product's top is at
    ``ty + 14`` and its bottom at ``ty + 220`` once scaled.
    """
    t = W / 2 * (1 - SCALE)
    base = H / 2 * (1 - SCALE)
    h = LOCKUP_HEIGHT[style.layout]
    if style.layout.startswith("band_"):
        reach = h + 4
    elif style.layout == "title_block":
        reach = 10 + h + 4 + _side_offset(style, False)
    else:
        reach = EDGE + _side_offset(style, style.top_logo) + h + 4
    top = style.top_logo and style.layout != "title_block"
    ty = max(base, reach - 14) if top else min(base, (H - reach) - 220)
    return f"translate({n(t)} {n(ty)}) scale({SCALE:g})"


_HEAD = re.compile(r'^<svg[^>]*><rect width="\d+" height="\d+" fill="[^"]*"/>')


def _first(record: Mapping[str, str], names) -> str | None:
    for name in names:
        value = record.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _painted(product_type: str, style: HouseStyle, record: Mapping[str, str], scale: float) -> str:
    """The catalog's own drawing of ``record`` in ``style``'s ink, without its sheet."""
    figure_fn, _ = FIGURES[product_type]
    material = _first(record, MATERIAL_ATTRIBUTES)
    data = paint(
        figure_fn(dict(record)).figure,
        SheetStyle(ink=style.ink, paper=style.paper, frame="none"),
        part_fill(_first(record, FINISH_ATTRIBUTES), material),
        material_hatch(material),
        scale,
    ).decode("utf-8")
    body = _HEAD.sub("", data, count=1)
    if body == data or not body.endswith("</svg>"):
        raise ValueError("the catalog's sheet changed shape; the house style cannot lift the product")
    return body[: -len("</svg>")]


def branded_svg(product_type: str, brand: str, record: Mapping[str, str], scale: float) -> str:
    """One SKU's drawing dressed in its brand's house style. Raises ``KeyError`` for a brand with no row."""
    style = HOUSE_STYLES[brand]
    uid = brands.BY_NAME[brand].code
    tex_def, tex_rect = hk.texture(style.texture, style.colour, uid, W, H, TEXTURE_TILES)
    haz_def, haz = _hazard(style, uid)
    product = hk.restyle_strokes(
        _painted(product_type, style, record, scale),
        style.ink,
        to_ink=style.ink,
        factor=style.stroke / SCALE,
        sharp=style.joins == "sharp",
    )
    return hk.compose(
        W,
        H,
        tex_def + haz_def,
        [f'<rect width="{W}" height="{H}" fill="{style.paper}"/>', tex_rect],
        product_transform(style),
        product,
        [*_frame(style), *haz, *logo(style, brand)],
    )


def render(
    product_type: str, brand: str, records: Sequence[Mapping[str, str]], *, house: bool = False
) -> list[bytes]:
    """SVG bytes for each SKU of one product.

    ``house=False`` (the default) is the catalog's own drawing, byte for byte:
    exactly what :func:`draw_product` returns and the emitted catalog carries.
    ``house=True`` dresses each SKU in its brand's house style.
    """
    if not house:
        return [data for data, _ in draw_product(product_type, brand, records)]
    scale = product_scale_for(product_type, records)
    return [branded_svg(product_type, brand, r, scale).encode("utf-8") for r in records]


def H_(paper, texture, frame, band, colour, ink, stroke, joins, mark, enclose, layout, place, font, weight, case, spacing):  # noqa: N802 -- a table row reads best positionally
    return HouseStyle(paper, texture, frame, band, colour, ink, stroke, joins, mark, enclose, layout, place, font, weight, case, spacing)


# fmt: off
#: Brand -> its house style. One row per brand in the brand book, every value chosen by hand.
#   paper      texture      frame       band             colour     ink        stroke joins    mark             enclose    layout          place            font         weight case     spacing
HOUSE_STYLES: dict[str, HouseStyle] = {
    "Dravenholt":        H_("#f4f4f1", "none",      "double",   "none",          "#1f3a5f", "#1c2a3d", 1.15, "sharp", "gear",          "none",    "plate",        "top_left",      "din",       700, "caps",  1.5),
    "Hollisdane":        H_("#ffffff", "none",      "rule",     "none",          "#b3261e", "#2a1c1c", 1.0,  "round", "chevrons",      "square",  "mark_left",    "top_left",      "grotesk",   700, "caps",  0.5),
    "Varnstrom":         H_("#f6f3ea", "none",      "heavy",    "hazard_bottom", "#2d2f33", "#1f1f1f", 1.3,  "sharp", "hex_nut",       "none",    "stencil_bar",  "top_centre",    "stencil",   400, "caps",  2.0),
    "Druvanholm":        H_("#f1f3f5", "brushed",   "rivets",   "none",          "#46647e", "#26313d", 1.15, "sharp", "bolt_triangle", "none",    "plate",        "top_centre",    "condensed", 700, "caps",  2.0),
    "Estrimore":         H_("#e6eef7", "blueprint", "drawing",  "none",          "#1f5fbf", "#173a6b", 1.0,  "round", "crosshair",     "none",    "title_block",  "bottom_right",  "din",       400, "caps",  1.0),
    "Iron Heron":        H_("#f4f4f1", "none",      "corners",  "none",          "#c0392b", "#2b2b2b", 1.3,  "sharp", "spark",         "diamond", "badge",        "top_left",      "impact",    400, "caps",  1.0),
    "Kessingmoor":       H_("#f3efe6", "none",      "rounded",  "none",          "#2e6b3a", "#1f3324", 1.0,  "round", "gear_fine",     "none",    "mark_above",   "top_centre",    "futura",    700, "caps",  2.5),
    "Ingleward":         H_("#ffffff", "dots",      "rule",     "none",          "#7a1f2b", "#2e1a1d", 1.15, "round", "torx",          "circle",  "badge",        "bottom_centre", "slab",      700, "title", 0.0),
    "Tervasko":          H_("#f6f3ea", "none",      "none",     "hazard_top",    "#c77700", "#2b2418", 1.5,  "sharp", "chevron_trio",  "none",    "band_bottom",  "bottom_centre", "impact",    400, "caps",  1.5),
    "Vellinhorst":       H_("#f1f3f5", "none",      "double",   "none",          "#13737a", "#12383b", 1.0,  "round", "bearing",       "none",    "mark_left",    "bottom_left",   "din",       700, "caps",  1.0),
    # Cutting-tool specialists.
    "Quillon Carbide":   H_("#eaf0f6", "blueprint", "drawing",  "none",          "#2340a0", "#1a2b5c", 1.0,  "sharp", "knurl",         "diamond", "title_block",  "bottom_left",   "condensed", 700, "caps",  1.0),
    "Tessaly Cutters":   H_("#ffffff", "grid",      "rule",     "none",          "#6d1a36", "#2e1520", 1.15, "sharp", "delta",         "none",    "mark_left",    "top_right",     "condensed", 400, "caps",  2.0),
    "Orrinford":         H_("#f4f4f1", "none",      "drawing",  "none",          "#3a4450", "#1f252c", 1.0,  "round", "crosshair",     "square",  "title_block",  "bottom_right",  "mono",      700, "caps",  0.0),
    "Kaldermark":        H_("#f7f5f0", "none",      "heavy",    "none",          "#a3471b", "#3a2215", 1.3,  "sharp", "speed_bars",    "none",    "plate",        "bottom_right",  "impact",    400, "caps",  0.5),
    "Pellanor":          H_("#f1f3f5", "none",      "corners",  "none",          "#1b5e6b", "#173236", 1.0,  "round", "spark",         "circle",  "mark_above",   "top_left",      "din",       400, "caps",  3.0),
    "Wendlow Tool":      H_("#ffffff", "none",      "double",   "none",          "#b3261e", "#1b1b1b", 1.15, "sharp", "chevrons",      "none",    "band_top",     "top_centre",    "condensed", 700, "caps",  1.5),
    "Varrick Precision": H_("#f3efe6", "grid",      "drawing",  "none",          "#2d2f33", "#1b1b1b", 1.0,  "round", "ibeam",         "square",  "title_block",  "bottom_right",  "condensed", 400, "caps",  1.0),
    "Lark & Lathe":      H_("#f6f3ea", "none",      "rounded",  "none",          "#5f6b2a", "#2e3318", 1.0,  "round", "thread",        "circle",  "badge",        "top_right",     "slab",      400, "title", 1.0),
    # Fastener specialists.
    "Rivenhall":         H_("#f1f3f5", "brushed",   "rivets",   "none",          "#4b5563", "#252a31", 1.3,  "sharp", "rivet_row",     "none",    "plate",        "top_left",      "stencil",   400, "caps",  1.0),
    "Caddernook":        H_("#ffffff", "none",      "rule",     "none",          "#1f5fbf", "#182a4a", 1.15, "round", "hex_socket",    "none",    "mark_left",    "top_centre",    "grotesk",   700, "caps",  2.0),
    "Pellwarren":        H_("#f4f4f1", "dots",      "corners",  "none",          "#2e6b3a", "#1d2b20", 1.0,  "sharp", "bolt_square",   "none",    "stamp",        "top_right",     "mono",      700, "caps",  1.0),
    "Cobbet & Pryce":    H_("#f7f5f0", "none",      "double",   "none",          "#7a4a1f", "#33231a", 1.15, "round", "hex_nut",       "shield",  "badge",        "top_centre",    "slab",      700, "caps",  0.5),
    "Lintmoor":          H_("#eef2ef", "none",      "rivets",   "none",          "#13737a", "#163135", 1.0,  "sharp", "phillips",      "none",    "plate",        "bottom_centre", "din",       700, "caps",  2.0),
    "Morvennick":        H_("#ffffff", "none",      "heavy",    "none",          "#c0392b", "#2a1a18", 1.5,  "sharp", "square_drive",  "none",    "band_top",     "top_centre",    "stencil",   400, "caps",  1.5),
    "Selvanock":         H_("#f3efe6", "none",      "rule",     "none",          "#5b3f8c", "#2a2140", 1.0,  "round", "torx",          "none",    "mark_above",   "bottom_centre", "futura",    400, "caps",  1.5),
    "Tall Mast":         H_("#f1f3f5", "none",      "none",     "none",          "#1f3a5f", "#1c2a3d", 1.3,  "sharp", "bolt_triangle", "circle",  "stencil_bar",  "bottom_centre", "condensed", 700, "caps",  3.0),
    # Abrasive specialists.
    "Grisenne":          H_("#ffffff", "none",      "none",     "hazard_bottom", "#e8641b", "#2b2b2b", 1.3,  "sharp", "spark",         "none",    "band_top",     "top_centre",    "impact",    400, "caps",  0.5),
    "Braddlestow":       H_("#f6f3ea", "dots",      "rounded",  "none",          "#b3261e", "#2b1d1d", 1.15, "round", "chevron_trio",  "hex",     "badge",        "bottom_left",   "grotesk",   700, "caps",  1.0),
    "Tannerby":          H_("#f4f4f1", "none",      "double",   "none",          "#7a4a1f", "#33231a", 1.0,  "round", "delta",         "circle",  "mark_left",    "bottom_right",  "slab",      400, "caps",  1.0),
    "Brennavik":         H_("#f1f3f5", "none",      "corners",  "hazard_top",    "#2d2f33", "#1b1b1b", 1.3,  "sharp", "speed_bars",    "square",  "plate",        "bottom_left",   "condensed", 700, "caps",  1.5),
    "Salt Meadow Works": H_("#f7f5f0", "none",      "rule",     "none",          "#4d6b2f", "#26331b", 1.0,  "round", "gear",          "hex",     "mark_above",   "top_right",     "futura",    700, "title", 0.5),
    # Hand-tool specialists.
    "Ashcombe Forge":    H_("#f3efe6", "none",      "heavy",    "none",          "#2d2f33", "#1b1b1b", 1.5,  "sharp", "hex_nut",       "square",  "stamp",        "bottom_right",  "slab",      700, "caps",  1.5),
    "Pennock & Hale":    H_("#ffffff", "none",      "double",   "none",          "#1f5fbf", "#182a4a", 1.0,  "round", "square_drive",  "circle",  "badge",        "top_left",      "futura",    700, "caps",  1.0),
    "Brindlecote":       H_("#f6f3ea", "brushed",   "rivets",   "none",          "#6d1a36", "#2e1520", 1.15, "sharp", "thread",        "none",    "plate",        "top_right",     "slab",      700, "caps",  1.0),
    "Ivenhoft":          H_("#f1f3f5", "none",      "rule",     "none",          "#c77700", "#2b2418", 1.15, "round", "hex_socket",    "diamond", "mark_left",    "bottom_centre", "impact",    400, "caps",  1.0),
    "Lantern Rock":      H_("#f4f4f1", "none",      "corners",  "hazard_bottom", "#2e6b3a", "#1d2b20", 1.3,  "sharp", "crosshair",     "hex",     "stencil_bar",  "top_left",      "stencil",   400, "caps",  1.0),
    # Bearing specialists.
    "Quarrenby":         H_("#eef2ef", "none",      "double",   "none",          "#13737a", "#12383b", 1.0,  "round", "bearing",       "circle",  "plate",        "top_centre",    "futura",    700, "caps",  2.0),
    "Quennick":          H_("#ffffff", "grid",      "drawing",  "none",          "#1f3a5f", "#1c2a3d", 1.0,  "round", "bolt_circle",   "none",    "title_block",  "bottom_left",   "din",       700, "caps",  1.5),
    "Lorcastle":         H_("#f3efe6", "none",      "rounded",  "none",          "#5b3f8c", "#2a2140", 1.0,  "round", "gear_fine",     "circle",  "badge",        "bottom_right",  "din",       400, "title", 1.0),
    "Spindlewick":       H_("#f1f3f5", "none",      "rule",     "none",          "#0f7fa6", "#163240", 1.15, "round", "bearing",       "hex",     "mark_above",   "bottom_left",   "grotesk",   400, "caps",  2.0),
    "Tin Kestrel":       H_("#f7f5f0", "none",      "corners",  "none",          "#46647e", "#26313d", 1.0,  "sharp", "chevrons",      "diamond", "mark_left",    "top_left",      "condensed", 700, "caps",  1.0),
    "Harnell":           H_("#ffffff", "none",      "heavy",    "none",          "#a3471b", "#3a2215", 1.3,  "sharp", "bolt_circle",   "square",  "band_bottom",  "bottom_centre", "din",       700, "caps",  2.0),
    # Two-and-three-family makers.
    "Quellmarsh":        H_("#f4f4f1", "dots",      "double",   "none",          "#3a4450", "#1f252c", 1.15, "round", "knurl",         "none",    "stamp",        "top_left",      "condensed", 700, "caps",  2.0),
    "Crennick Works":    H_("#f6f3ea", "none",      "rivets",   "hazard_top",    "#e8641b", "#2b2b2b", 1.3,  "sharp", "gear",          "square",  "stencil_bar",  "bottom_centre", "impact",    400, "caps",  2.0),
    "Stone Wicket":      H_("#eef2ef", "none",      "heavy",    "none",          "#4b5563", "#252a31", 1.5,  "sharp", "ibeam",         "none",    "plate",        "bottom_right",  "stencil",   400, "caps",  1.0),
}
# fmt: on


def mark_key(style: HouseStyle) -> tuple[str, str]:
    """A logo mark: its motif and enclosure. No two brands share one."""
    return (style.mark, style.enclose)


def lockup_key(style: HouseStyle) -> tuple:
    """A logo's arrangement and name treatment. No two brands share one."""
    return (style.layout, style.place, style.font, style.weight, style.case, style.spacing, style.italic)
