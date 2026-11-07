"""Brand house styles for the retail drawings (prototype for #125).

Every brand is one declared row of :data:`HOUSE_STYLES`, never a hash of
its name, so each brand looks designed and two brands cannot collide
(``test_house_styles.py`` refuses a duplicate row, a duplicate mark, a
duplicate lockup and a brand with no row). A row sets:

* the sheet's ``frame``. The paper is the one every drawing sits on
  (:data:`...core.drawing.product_look.PAPER`), with no texture: a brand's tinted
  paper read as a search signal (#849);
* the product's outline: ``ink`` color, stroke ``weight``, ``dashed`` and
  ``joins`` (round or sharp). The product's own fill and pattern are never
  touched: they belong to the product, not the brand;
* the logo: a composite ``mark`` from :data:`MARKS` in the brand ``color``,
  set in a ``layout`` at ``place``. About half the brands use a full lockup
  (mark plus wordmark); the rest show the mark alone in a corner plus a small
  text ``tag``;
* the wordmark treatment: ``font``, ``weight``, ``case``, ``spacing``, ``italic``.

:func:`dress` wraps a product drawing in its brand's house style.
"""

# ruff: noqa: E501 -- SVG literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math
import re
from dataclasses import astuple, dataclass, fields

from synthetic_ecommerce_data.core.drawing import brand_type
from synthetic_ecommerce_data.core.drawing.product_look import PAPER
from synthetic_ecommerce_data.domains.retail import sheet_extent
from synthetic_ecommerce_data.domains.retail.house_marks import (
    MARKS,
    _dot,  # noqa: F401 -- read through this module
    _hexagon,  # noqa: F401 -- read through this module
    _ring,  # noqa: F401 -- read through this module
    _stroke,  # noqa: F401 -- read through this module
    mark_svg,
)

SIZE = 400
DEFAULT_INK = "#2b3440"
MARK_ONLY_SIZE = 60  # px across: 15% of the sheet's width, the cap
LOCKUP_MARK_SIZE = 56
#: The sheet is 400 units; the Studio tile shows it 180 px tall, so a unit is 0.45 px.
TILE_PX_PER_UNIT = 180 / SIZE
NAME_MAX = 40.0  # the largest a wordmark is set; its least is brand_type.min_size
#: The product drawings span y 28..362 of the sheet.
PRODUCT_TOP, PRODUCT_SPAN = 28.0, 334.0
#: The margin the product keeps from an edge no logo text reaches into.
FREE_EDGE = 14.0
EDGE = 16  # gap between the sheet's edge and a logo
#: The room a one- or two-line name has beside a mark, between the sheet's margins.
ROOM = SIZE - 2 * (EDGE + 4)

FRAMES = ("none", "thin", "double", "rounded", "heavy", "ticks")
LAYOUTS = (
    "mark_only",
    "mark_left",
    "mark_right",
    "mark_above",
    "pill",
    "badge",
    "band_top",
    "band_bottom",
)
PLACES = ("top_left", "top_center", "top_right", "bottom_left", "bottom_center", "bottom_right")
CORNERS = ("top_left", "top_right", "bottom_left", "bottom_right")
TAGS = ("none", "outline", "rect", "flag", "plain", "underline", "stamp", "tab")
CASES = ("title", "caps", "smallcaps", "lower")


#: A real brand (:mod:`real_brands`, gen#332) draws no logo: its style row carries this mark,
#: so the name is text in the title and the ``brand`` field and the drawing shows no mark.
NO_MARK = "none"


@dataclass(frozen=True)
class HouseStyle:
    """One brand's look. See the module docstring for what each field does."""

    frame: str
    color: str
    ink: str
    stroke: float  # outline weight, 1.0 = the kit's own
    dashed: bool
    joins: str  # round | sharp
    mark: str
    layout: str
    place: str
    tag: str  # mark_only brands only; "none" for a lockup
    font: str
    weight: int  # 400 | 700
    case: str
    spacing: float  # letter-spacing, px
    italic: bool = False

    def __post_init__(self) -> None:
        checks = (
            ("frame", FRAMES),
            ("joins", ("round", "sharp")),
            ("mark", (*MARKS, NO_MARK)),
            ("layout", LAYOUTS),
            ("place", PLACES),
            ("tag", TAGS),
            ("font", tuple(brand_type.FAMILIES)),
            ("weight", (400, 700)),
            ("case", CASES),
        )
        for name, allowed in checks:
            if getattr(self, name) not in allowed:
                raise ValueError(f"{name}={getattr(self, name)!r}; one of {allowed}")
        if self.layout == "mark_only":
            if self.place not in CORNERS:
                raise ValueError("a mark-only logo sits in a corner")
            if self.tag == "none":
                raise ValueError("a mark-only brand carries a text tag")
        elif self.tag != "none":
            raise ValueError("a lockup already carries the name; tag must be 'none'")
        if self.layout.startswith("band_") and self.place != (
            "top_center" if self.layout == "band_top" else "bottom_center"
        ):
            raise ValueError("a band sits at the top or bottom center")

    @property
    def top_logo(self) -> bool:
        return self.place.startswith("top")


# --------------------------------------------------------------------------
# Wordmarks
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Sheet: the frame
# --------------------------------------------------------------------------


def _frame(style: HouseStyle) -> list[str]:
    c = style.color
    f = style.frame
    if f == "thin":
        return [
            f'<rect x="6" y="6" width="388" height="388" fill="none" stroke="{c}" stroke-width="1"/>'
        ]
    if f == "double":
        return [
            f'<rect x="6" y="6" width="388" height="388" fill="none" stroke="{c}" stroke-width="1.6"/>',
            f'<rect x="11" y="11" width="378" height="378" fill="none" stroke="{c}" stroke-width=".8"/>',
        ]
    if f == "rounded":
        return [
            f'<rect x="8" y="8" width="384" height="384" rx="22" fill="none" stroke="{c}" stroke-width="2"/>'
        ]
    if f == "heavy":
        return [
            f'<rect x="7" y="7" width="386" height="386" fill="none" stroke="{c}" stroke-width="4"/>'
        ]
    if f == "ticks":
        t, a, b = 24, 10, SIZE - 10
        d = (
            f"M{a},{a + t} L{a},{a} L{a + t},{a} M{b - t},{a} L{b},{a} L{b},{a + t} "
            f"M{b},{b - t} L{b},{b} L{b - t},{b} M{a + t},{b} L{a},{b} L{a},{b - t}"
        )
        return [
            f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="square"/>'
        ]
    return []


# --------------------------------------------------------------------------
# Logos: a lockup (mark + wordmark) or a corner mark plus a small tag
# --------------------------------------------------------------------------


def _x_for(place: str, width: float) -> float:
    """The left x of a ``width``-wide block at ``place``."""
    if place.endswith("left"):
        return EDGE + 4
    if place.endswith("right"):
        return SIZE - EDGE - 4 - width
    return (SIZE - width) / 2


#: Air between a logo and the product drawn clear of it.
AIR = 6.0
#: The most a mark and a tag can share one side of a corner-mark sheet: the tag sits in
#: the opposite corner, so its box must clear the mark's corner and a gap.
TAG_PAD = 12


@dataclass(frozen=True)
class Logo:
    """A brand's logo: its SVG parts and how far it reaches into the sheet."""

    parts: list[str]
    top: float = 0.0  # down from the sheet's top edge to the lowest part of a top logo
    bottom: float = 0.0  # up from the sheet's bottom edge to the highest part of a bottom logo


def _cap(style: HouseStyle) -> float:
    """The full capital's height per unit of font size: what a line is centered by."""
    return brand_type.FAMILIES[style.font].cap_height


def _block(style: HouseStyle, brand: str, room: float) -> brand_type.Block:
    """``brand`` set in ``room`` units: the core's fit, in this style's type."""
    return brand_type.set_lines(style, brand, room, NAME_MAX, TILE_PX_PER_UNIT)


def _lines(
    style: HouseStyle,
    block: brand_type.Block,
    x: float,
    center: float,
    color: str,
    anchor: str = "start",
) -> list[str]:
    """The block's lines, the capitals of the whole block centered on ``center``."""
    baselines = block.baselines(center, _cap(style))
    return [
        brand_type.text(style, t, x, b, block.size, color, anchor)
        for t, b in zip(block.lines, baselines, strict=True)
    ]


def _lockup(style: HouseStyle, brand: str) -> Logo:
    c, m, lay = style.color, LOCKUP_MARK_SIZE, style.layout
    top, cap = style.top_logo, _cap(style)
    if lay in ("band_top", "band_bottom"):
        block = _block(style, brand, SIZE - 2 * EDGE - m - 12)
        h = max(64, math.ceil(block.height(cap) + 2 * 14))
        y0 = 0 if lay == "band_top" else SIZE - h
        x0 = (SIZE - (m + 12 + block.width)) / 2
        parts = [
            f'<rect x="0" y="{y0}" width="{SIZE}" height="{h}" fill="{c}"/>',
            mark_svg(style.mark, x0 + m / 2, y0 + h / 2, m - 6, "#ffffff"),
            *_lines(style, block, x0 + m + 12, y0 + h / 2, "#ffffff"),
        ]
        return Logo(parts, top=h if lay == "band_top" else 0, bottom=0 if lay == "band_top" else h)
    if lay in ("mark_left", "mark_right"):
        block = _block(style, brand, ROOM - m - 10)
        h = max(m, math.ceil(block.height(cap)))
        w = m + 10 + block.width
        x0 = _x_for(style.place, w)
        cy = EDGE + h / 2 if top else SIZE - EDGE - h / 2
        mx, tx = (
            (x0 + m / 2, x0 + m + 10) if lay == "mark_left" else (x0 + block.width + 10 + m / 2, x0)
        )
        parts = [mark_svg(style.mark, mx, cy, m, c), *_lines(style, block, tx, cy, style.ink)]
        return Logo(parts, top=EDGE + h if top else 0, bottom=0 if top else EDGE + h)
    if lay == "mark_above":
        block = _block(style, brand, ROOM)
        h = m + 4 + math.ceil(block.height(cap))
        w = max(m, block.width)
        cx = _x_for(style.place, w) + w / 2
        y0 = EDGE if top else SIZE - EDGE - h
        base = y0 + m + 4 + cap * block.size
        parts = [
            mark_svg(style.mark, cx, y0 + m / 2, m, c),
            *(
                brand_type.text(style, t, cx, base + i * block.gap, block.size, style.ink, "middle")
                for i, t in enumerate(block.lines)
            ),
        ]
        return Logo(parts, top=EDGE + h if top else 0, bottom=0 if top else EDGE + h)
    # pill (filled, white type) or badge (outlined, brand-color type)
    h0 = 50 if lay == "pill" else 58
    mk = h0 - 14
    block = _block(style, brand, ROOM - (12 + mk + 10 + 16))
    h = max(h0, math.ceil(block.height(cap) + 2 * 10))
    w = 12 + mk + 10 + block.width + 16
    x0 = _x_for(style.place, w)
    y0 = EDGE if top else SIZE - EDGE - h
    filled = lay == "pill"
    box = (
        f'<rect x="{x0:.1f}" y="{y0}" width="{w:.1f}" height="{h}" rx="{h / 2:g}" fill="{c}"/>'
        if filled
        else f'<rect x="{x0:.1f}" y="{y0}" width="{w:.1f}" height="{h}" rx="6" fill="#ffffff" stroke="{c}" stroke-width="2"/>'
    )
    ink = "#ffffff" if filled else c
    parts = [
        box,
        mark_svg(style.mark, x0 + 12 + mk / 2, y0 + h / 2, mk, ink),
        *_lines(style, block, x0 + 12 + mk + 10, y0 + h / 2, ink),
    ]
    return Logo(parts, top=EDGE + h if top else 0, bottom=0 if top else EDGE + h)


def _tag(style: HouseStyle, brand: str, place: str) -> Logo:
    """The text tag a mark-only brand carries at ``place``, with its reach."""
    c, t, pad, cap = style.color, style.tag, TAG_PAD, _cap(style)
    top = place.startswith("top")
    # The mark sits in a corner of the same side, the tag in the other corner: the
    # tag's box must stop short of the mark's.
    shares = style.top_logo == top
    room = SIZE - 2 * (EDGE + 4) - 2 * pad - 8
    lift = 0.0
    try:
        block = _block(style, brand, room - (MARK_ONLY_SIZE + 8 if shares else 0))
    except ValueError:
        if not shares or style.tag == "tab":
            raise
        # a long name: the tag takes the full width, raised clear of the corner mark
        block, lift = _block(style, brand, room), MARK_ONLY_SIZE + 6
    tw = block.width
    w = tw + 2 * pad
    h = math.ceil(cap * block.size + (len(block.lines) - 1) * block.gap + 0.7 * block.size)
    x0 = _x_for(place, w)
    y0 = EDGE + lift if top else SIZE - EDGE - h - lift
    mid = y0 + h / 2
    reach = (EDGE + lift + h, 0.0) if top else (0.0, EDGE + lift + h)
    if t == "tab":  # a woven label hanging from the top edge
        tab = h + 12
        parts = [
            f'<rect x="{x0:.1f}" y="0" width="{w:.1f}" height="{tab}" fill="{c}"/>',
            *_lines(style, block, x0 + pad, 12 + h / 2, "#ffffff"),
        ]
        return Logo(parts, top=tab)
    if t == "rect":
        parts = [
            f'<rect x="{x0:.1f}" y="{y0}" width="{w:.1f}" height="{h}" fill="{c}"/>',
            *_lines(style, block, x0 + pad, mid, "#ffffff"),
        ]
    elif t == "flag":
        n = 8
        d = f"M{x0:.1f},{y0} L{x0 + w + n:.1f},{y0} L{x0 + w:.1f},{y0 + h / 2:g} L{x0 + w + n:.1f},{y0 + h} L{x0:.1f},{y0 + h} Z"
        parts = [f'<path d="{d}" fill="{c}"/>', *_lines(style, block, x0 + pad, mid, "#ffffff")]
    elif t == "outline":
        parts = [
            f'<rect x="{x0:.1f}" y="{y0}" width="{w:.1f}" height="{h}" rx="{h / 2:g}" fill="#ffffff" stroke="{c}" stroke-width="1.4"/>',
            *_lines(style, block, x0 + pad, mid, c),
        ]
    elif t == "stamp":
        lift = w / 2 * math.sin(math.radians(4))  # the -4 degree turn swings the ends
        reach = (reach[0] + lift, reach[1] + lift)
        parts = [
            f'<g transform="rotate(-4 {x0 + w / 2:.1f} {mid:g})">'
            f'<rect x="{x0:.1f}" y="{y0}" width="{w:.1f}" height="{h}" fill="none" stroke="{c}" stroke-width="1.6"/>'
            f'<rect x="{x0 + 3:.1f}" y="{y0 + 3}" width="{w - 6:.1f}" height="{h - 6}" fill="none" stroke="{c}" stroke-width=".7"/>'
            f"{''.join(_lines(style, block, x0 + pad, mid, c))}</g>"
        ]
    elif t == "underline":
        last = block.baselines(mid, cap)[-1]
        last_w = brand_type.width(style, block.lines[-1], block.size)
        rule = last + brand_type.DESCENDER * block.size + 1.5
        parts = [
            *_lines(style, block, x0 + pad, mid, c),
            f'<rect x="{x0 + pad:.1f}" y="{rule:.1f}" width="{last_w:.1f}" height="1.6" fill="{c}"/>',
        ]
    else:  # plain
        parts = _lines(style, block, x0 + pad, mid, c)
    return Logo(parts, top=reach[0], bottom=reach[1])


def _opposite(corner: str) -> str:
    """The tag's place for a mark-only brand: the diagonally opposite corner."""
    v, h = corner.split("_")
    return f"{'bottom' if v == 'top' else 'top'}_{'right' if h == 'left' else 'left'}"


def tag_place(style: HouseStyle) -> str:
    """Where a mark-only brand's tag sits: the same side, other corner, unless
    that is the top (the product's top is clearer than its sides)."""
    v, h = style.place.split("_")
    if style.tag == "tab":
        return f"top_{'right' if h == 'left' else 'left'}"
    if v == "top":
        return _opposite(style.place)
    return f"bottom_{'right' if h == 'left' else 'left'}"


def _logo(style: HouseStyle, brand: str) -> Logo:
    if style.mark == NO_MARK:  # a real brand: text only, never a logo, wordmark or trade dress
        return Logo([])
    if style.layout != "mark_only":
        return _lockup(style, brand)
    v, h = style.place.split("_")
    r = MARK_ONLY_SIZE / 2
    cx = EDGE + r if h == "left" else SIZE - EDGE - r
    cy = EDGE + r if v == "top" else SIZE - EDGE - r
    tag = _tag(style, brand, tag_place(style))
    return Logo(
        [mark_svg(style.mark, cx, cy, MARK_ONLY_SIZE, style.color), *tag.parts], tag.top, tag.bottom
    )


def logo(style: HouseStyle, brand: str) -> list[str]:
    return _logo(style, brand).parts


def reach(style: HouseStyle, brand: str) -> tuple[float, float]:
    """How far the logo's text reaches down from the sheet's top and up from its bottom.

    A corner mark is not counted: it sits in a corner, which the product leaves free.
    """
    lg = _logo(style, brand)
    return lg.top, lg.bottom


# --------------------------------------------------------------------------
# The product's outline in the brand's hand
# --------------------------------------------------------------------------

_WIDTH = re.compile(r'stroke-width="([0-9]*\.?[0-9]+)"')


def restyle(fragment: str, style: HouseStyle) -> str:
    """The product drawing's ink strokes in ``style``'s color, weight, dash and joins.

    Only strokes in the kit's ink color change; fills, patterns and white
    gloss strokes are the product's and stay as drawn.
    """

    def one(el: str) -> str:
        if f'stroke="{DEFAULT_INK}"' not in el:
            return el
        m = _WIDTH.search(el)
        width = float(m.group(1)) if m else 1.0
        el = el.replace(f'stroke="{DEFAULT_INK}"', f'stroke="{style.ink}"')
        if m:
            el = el[: m.start()] + f'stroke-width="{width * style.stroke:.2f}"' + el[m.end() :]
        if style.joins == "sharp":
            el = el.replace('stroke-linejoin="round"', 'stroke-linejoin="miter"').replace(
                'stroke-linecap="round"', 'stroke-linecap="butt"'
            )
            if "stroke-linejoin" not in el:
                el = el.replace("/>", ' stroke-linejoin="miter"/>', 1)
        if style.dashed and width >= 2.5 and "stroke-dasharray" not in el:
            el = el.replace("/>", ' stroke-dasharray="9 4"/>', 1)
        return el

    return re.sub(
        r"<(?:path|rect|circle|ellipse|polygon|polyline|line)\b[^>]*/>",
        lambda m: one(m.group(0)),
        fragment,
    )


def product_transform(
    style: HouseStyle, brand: str, extra: tuple[float, float] = (0.0, 0.0)
) -> str:
    """Shrink the product a little and move it clear of the logo's text.

    Products span y 28..362 of the sheet (334 tall). The scale is the style's
    (0.86 for a corner mark, 0.78 for a lockup) or less, if the logo's reach top
    and bottom leaves less room; the product then sits as near the middle as
    that reach and :data:`AIR` allow. ``extra`` adds to the reach (top, bottom): the
    licence line a film product sets beside the logo (:mod:`film_emblems`, gen#904).
    """
    s0 = 0.86 if style.layout == "mark_only" else 0.78
    if style.mark == NO_MARK:  # no logo to clear: the product sits where it always did
        dy = 0.0 if style.layout == "mark_only" else (10.0 if style.top_logo else -10.0)
        t = SIZE / 2 * (1 - s0)
        return f"translate({t:g} {t + dy:.1f}) scale({s0:.3f})"
    top, bottom = (r + e for r, e in zip(reach(style, brand), extra, strict=True))
    lo = top + AIR if top else FREE_EDGE
    hi = SIZE - (bottom + AIR if bottom else FREE_EDGE)
    s = min(s0, (hi - lo) / PRODUCT_SPAN)
    t = SIZE / 2 * (1 - s)
    y0 = min(max(t + PRODUCT_TOP * s, lo), hi - PRODUCT_SPAN * s)
    return f"translate({t:g} {y0 - PRODUCT_TOP * s:.1f}) scale({s:.3f})"


#: The area a turned product stays inside, in the kit's own units (#849): the span the kit's
#: drawings take (:data:`PRODUCT_TOP`, :data:`PRODUCT_SPAN`), as wide as it is tall. A drawing
#: that already reaches past it upright keeps its own reach, so 0 degrees changes nothing.
TURN_AREA = (PRODUCT_TOP, PRODUCT_TOP, SIZE - PRODUCT_TOP, PRODUCT_TOP + PRODUCT_SPAN)
_MEASURED = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {0} {0}"><defs>{1}</defs>{2}</svg>'
)


def turn(full: str, defs: str, angle: float) -> str:
    """The transform that turns a product drawing by its product's ``angle`` (#849), or "".

    ``full`` is the drawing at its line's full size (no pack scale, no size rung), so every
    SKU of a product that draws one shape is scaled alike and a smaller size still draws
    smaller. The drawing turns about the center of the box it covers, and is scaled about
    that center just enough that the turned drawing stays inside :data:`TURN_AREA` (measured
    by :func:`.sheet_extent.reach`, through the rotation, not by the turned box's corners).
    """
    if not angle:
        return ""
    box = sheet_extent.reach(_MEASURED.format(SIZE, defs, full))
    if box is None:
        return ""
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    turned = f'<g transform="rotate({angle:g} {cx:.2f} {cy:.2f})">{full}</g>'
    x0, y0, x1, y1 = sheet_extent.reach(_MEASURED.format(SIZE, defs, turned)) or box
    a0, b0 = min(box[0], TURN_AREA[0]), min(box[1], TURN_AREA[1])
    a1, b1 = max(box[2], TURN_AREA[2]), max(box[3], TURN_AREA[3])
    tiny = 1e-9
    k = min(
        1.0,
        (cx - a0) / max(cx - x0, tiny),
        (a1 - cx) / max(x1 - cx, tiny),
        (cy - b0) / max(cy - y0, tiny),
        (b1 - cy) / max(y1 - cy, tiny),
    )
    return (
        f"translate({cx:.2f} {cy:.2f}) scale({k:.3f}) rotate({angle:g}) "
        f"translate({-cx:.2f} {-cy:.2f})"
    )


def dress(style: HouseStyle, brand: str, uid: str) -> tuple[list[str], list[str], list[str]]:
    """(defs, sheet, overlay): what sits under and over the restyled product. The sheet is
    the one paper, whatever the brand (#849); ``uid`` is kept for the callers' signature."""
    del uid
    sheet = [f'<rect width="{SIZE}" height="{SIZE}" fill="{PAPER}"/>']
    return [], sheet, [*_frame(style), *logo(style, brand)]


def H(
    frame,
    color,
    ink,
    stroke,
    dashed,
    joins,
    mark,
    layout,
    place,
    tag,
    font,
    weight,
    case,
    spacing,
    italic=False,
):  # noqa: N802 -- a table row reads best positionally
    return HouseStyle(
        frame,
        color,
        ink,
        stroke,
        dashed,
        joins,
        mark,
        layout,
        place,
        tag,
        font,
        weight,
        case,
        spacing,
        italic,
    )


# fmt: off
#: Brand -> its house style. One row per brand, every value chosen by hand.
#   frame      color     ink        stroke dashed joins    mark                 layout         place            tag         font        weight case         spacing italic
HOUSE_STYLES: dict[str, HouseStyle] = {
    # Lockups: mark + wordmark.
    "Harbour & Pine":       H("double",  "#1f4e79", "#1f3550", 1.0,  False, "round", "chevron_stack",     "mark_left",   "top_left",      "none",     "sans",     700, "caps",      1.5),
    "Larkmoor":             H("rounded", "#b0476a", "#4a2537", 0.75, False, "round", "interlocking_rings", "mark_above", "top_center",    "none",     "serif",    400, "title",     3.0, True),
    "Ottery Denim":         H("none",    "#c26b2a", "#1d2a3a", 1.35, False, "sharp", "diamond_grid",      "band_top",    "top_center",    "none",     "mono",     700, "caps",      2.0),
    "Little Fernby":        H("ticks",   "#e0683f", "#2f4a6b", 1.1,  True,  "round", "petals",            "pill",        "bottom_center", "none",     "humanist", 700, "lower",     0.0),
    "Stridewell":           H("none",    "#e23b2e", "#111111", 1.35, False, "sharp", "circles_line",      "mark_right",  "top_left",      "none",     "sans",     700, "caps",      0.0, True),
    "Saltmarsh":            H("none",    "#1c7c7d", "#1d3b40", 1.0,  False, "round", "wave_arcs",         "band_bottom", "bottom_center", "none",     "humanist", 400, "lower",     1.0),
    "Calderby & Lune":      H("heavy",   "#2b2b2b", "#1b1b1b", 0.9,  False, "sharp", "lozenge_chain",     "badge",       "top_center",    "none",     "serif",    400, "caps",      2.5),
    "Hollinwray Knits":     H("rounded", "#a0522d", "#4b3426", 1.1,  True,  "round", "checker",           "mark_left",   "bottom_left",   "none",     "serif",    700, "lower",     0.0),
    "Goldfield Farms":      H("ticks",   "#c8870f", "#3d3115", 1.1,  False, "round", "sunburst",          "mark_above",  "top_right",     "none",     "sans",     700, "caps",      1.0),
    "Crunchworth":          H("none",    "#e0542d", "#2a2a2a", 1.35, False, "sharp", "zigzag_dots",       "pill",        "top_left",      "none",     "sans",     700, "caps",      0.5),
    "Lanternby":            H("thin",    "#b8801f", "#3b3122", 1.0,  False, "round", "three_stars",       "mark_right",  "bottom_center", "none",     "serif",    400, "smallcaps", 1.0),
    "Quillon Sleep":        H("rounded", "#5b6bb5", "#2c3354", 0.75, False, "round", "crescent_dot",      "mark_left",   "top_right",     "none",     "humanist", 400, "title",     0.5),
    "Velling Apothecary":   H("double",  "#5e4b6e", "#2f2638", 0.8,  False, "round", "plus_four",         "mark_above",  "bottom_center", "none",     "serif",    400, "caps",      4.0),
    "Kestlewood Cosmetics": H("none",    "#c2185b", "#1a1a1a", 1.0,  False, "sharp", "orbit",             "badge",       "bottom_center", "none",     "sans",     400, "lower",     2.0),
    # Mark alone in a corner, plus a small text tag.
    "Wrenfield":            H("thin",    "#6b1f2a", "#3a2a22", 1.0,  False, "sharp", "nested",            "mark_only",   "top_left",      "plain",    "serif",    400, "title",     0.0, True),
    "Thistle & Wren":       H("thin",    "#2f5d3a", "#233324", 1.0,  False, "round", "leaf_pair",         "mark_only",   "top_right",     "tab",      "serif",    700, "caps",      1.0),
    "Bramblewood":          H("thin",    "#7a3e75", "#3d2a4f", 0.75, False, "round", "spokes",            "mark_only",   "bottom_right",  "plain",    "serif",    400, "lower",     1.0, True),
    "Ferrowick Denim":      H("thin",    "#8a5a2b", "#2e2219", 1.2,  False, "sharp", "hex_trio",          "mark_only",   "top_left",      "rect",     "mono",     700, "caps",      1.0),
    "Meadowgate Dairy":     H("rounded", "#3f8f4a", "#24402a", 1.0,  False, "round", "scallops",          "mark_only",   "top_left",      "outline",  "humanist", 400, "title",     0.0),
    "Vine & Valley":        H("double",  "#7b2340", "#3b1a26", 0.9,  False, "round", "dot_triangle",      "mark_only",   "top_left",      "stamp",    "serif",    400, "smallcaps", 1.0),
    "Hollowbrook Cellars":  H("heavy",   "#5a2a3a", "#2a1a20", 1.1,  True,  "sharp", "cask",             "mark_only",   "bottom_left",   "rect",     "serif",    700, "caps",      2.0),
    "Stonepine Estate":     H("thin",    "#3f5a3a", "#1f2a1c", 0.9,  False, "sharp", "grapes",             "mark_only",   "top_right",     "outline",  "serif",    400, "smallcaps", 1.5),
    "Orchardgate Cider Co.": H("ticks",   "#a8742a", "#3a2a14", 1.0,  False, "round", "orchard_leaf",          "mark_only",   "bottom_right",  "tab",      "humanist", 700, "title",     0.5),
    "Olivar Grove":         H("ticks",   "#6b7a2a", "#33391a", 1.0,  False, "round", "three_drops",       "mark_only",   "top_right",     "rect",     "serif",    700, "caps",      2.0),
    "Copper Hill Preserves": H("double",  "#b5562b", "#4a2a1a", 1.0,  False, "round", "peaks",             "mark_only",   "top_left",      "flag",     "serif",    400, "title",     0.0),
    "Pantry Mill":          H("heavy",   "#3b5b7a", "#2b3440", 1.2,  False, "sharp", "squares_circle",    "mark_only",   "top_left",      "underline", "mono",    400, "caps",      2.0),
    "Hearth & Table":       H("rounded", "#8c3b2a", "#3a2620", 1.0,  False, "round", "rainbow",           "mark_only",   "bottom_right",  "flag",     "serif",    700, "lower",     0.0),
    "Crofter's Bakehouse":  H("rounded", "#9c6b30", "#4a3520", 1.1,  False, "round", "venn",              "mark_only",   "top_right",     "outline",  "serif",    400, "smallcaps", 0.0),
    "Brackenmere Home":     H("double",  "#4f6b4a", "#2a3328", 1.0,  False, "sharp", "quad_squares",      "mark_only",   "top_right",     "underline", "serif",   400, "caps",      3.0),
    "Pewley Table":         H("thin",    "#2f5e8c", "#22344a", 0.9,  False, "round", "target",            "mark_only",   "top_left",      "stamp",    "sans",     400, "caps",      2.0),
    # The brands the scaled build adds (scale.EXTRA_BRANDS): lockups, then marks alone.
    "Marrowgate":           H("heavy",   "#3d4f7a", "#1e2638", 1.2,  False, "sharp", "arch",              "mark_right",  "top_right",     "none",     "serif",    700, "caps",      2.0),
    "Pellbrook":            H("thin",    "#2e7d5b", "#1f3a2e", 0.9,  True,  "round", "ring_pair",         "band_bottom", "bottom_center", "none",     "sans",     400, "caps",      3.0),
    "Osier & Vane":         H("rounded", "#8a4b2f", "#3a2418", 1.0,  False, "round", "fan",               "mark_above",  "top_left",      "none",     "humanist", 700, "smallcaps", 1.0),
    "Tallow Street":        H("none",    "#444444", "#141414", 1.35, False, "sharp", "bar_trio",          "badge",       "top_left",      "none",     "mono",     400, "caps",      1.0),
    "Dovecote Lane":        H("double",  "#a05a7a", "#40263a", 0.75, True,  "round", "half_moons",        "pill",        "top_center",    "none",     "serif",    400, "title",     1.0, True),
    "Larchwood Living":     H("heavy",   "#5a6b3a", "#2c331d", 1.1,  False, "round", "triangle_pair",     "mark_left",   "bottom_right",  "none",     "sans",     400, "title",     0.0),
    "Brightwater Botanics": H("double",  "#2a8c82", "#1b3f3b", 0.9,  False, "round", "dot_ring",          "band_top",    "top_center",    "none",     "humanist", 400, "caps",      2.5),
    "Mossgill Dairy":       H("ticks",   "#4f8a3a", "#25401c", 1.2,  True,  "sharp", "wheat_ear",         "mark_right",  "bottom_left",   "none",     "humanist", 700, "lower",     0.5),
    "Cobbleway":            H("thin",    "#7a4a2a", "#33241a", 1.35, False, "sharp", "steps",             "mark_above",  "bottom_left",   "none",     "mono",     700, "title",     0.0),
    "Pipwick Toys":         H("rounded", "#e06a1f", "#2b3a5a", 1.2,  True,  "round", "pinwheel",          "pill",        "bottom_left",   "none",     "sans",     700, "lower",     1.5),
    "Hushwell":             H("rounded", "#6a5a9a", "#2e2846", 0.8,  False, "round", "hourglass",         "mark_only",   "bottom_left",   "tab",      "humanist", 400, "lower",     2.0),
    "Emberly Home":         H("heavy",   "#b5502f", "#3d2219", 1.1,  True,  "sharp", "keyhole",           "mark_only",   "top_right",     "plain",    "sans",     700, "title",     0.0),
    "Cobble & Kiln":        H("double",  "#6e5a48", "#2d251e", 1.3,  False, "sharp", "square_dot",        "mark_only",   "bottom_left",   "stamp",    "mono",     700, "lower",     0.0),
    "Orrin Skin":           H("thin",    "#c46b5a", "#3a2420", 0.75, True,  "round", "diamond_dot",       "mark_only",   "bottom_right",  "outline",  "sans",     400, "smallcaps", 3.0),
    "Wheatsheaf Lane":      H("ticks",   "#b08a2a", "#3b3018", 1.0,  False, "sharp", "crown",             "mark_only",   "top_left",      "tab",      "sans",     400, "lower",     1.0),
    "Barrowby Kitchen":     H("heavy",   "#9a3b2b", "#3a1e18", 1.2,  True,  "round", "striped_disc",      "mark_only",   "bottom_right",  "rect",     "humanist", 700, "caps",      0.5),
    "Treadmoor":            H("none",    "#3a4a5a", "#161e26", 1.35, True,  "sharp", "arrow_up",          "mark_only",   "top_right",     "underline", "humanist", 700, "title",    1.5),
    "Rookery Garden Co.":   H("heavy",   "#3f6b35", "#1f3319", 1.0,  True,  "round", "ladder",            "mark_only",   "bottom_left",   "flag",     "serif",    700, "title",     2.0),
    "Ribbonvale":           H("thin",    "#c0336b", "#3e1a2a", 0.9,  False, "sharp", "bell",              "mark_only",   "top_left",      "outline",  "mono",     400, "smallcaps", 0.5, True),
    "Clearbrook Household": H("rounded", "#2f7fb5", "#1a3448", 1.0,  False, "sharp", "cross_ring",        "mark_only",   "bottom_right",  "tab",      "sans",     700, "caps",      1.0),
    # The brands of the breadth and scale-only templates (breadth_rows, scale_rows).
    "Calderwick Denim":     H("ticks",   "#2c4a7a", "#17243a", 1.25, True,  "sharp", "rivet_pair",        "badge",       "bottom_right",  "none",     "mono",     700, "lower",     2.5),
    "Kettleby Tea Co.":     H("rounded", "#5e7a3a", "#2a3519", 0.85, False, "round", "teapot",            "mark_above",  "top_right",     "none",     "serif",    700, "smallcaps", 1.5, True),
    "Brewhollow Roasters":  H("none",    "#6b3f24", "#2e1a10", 1.3,  True,  "round", "bean",              "band_bottom", "bottom_center", "none",     "humanist", 400, "caps",      3.0),
    "Fenwold Nursery":      H("double",  "#4a7d2c", "#203616", 1.05, False, "sharp", "sprout",            "pill",        "top_right",     "none",     "serif",    400, "lower",     0.5),
    "Hollin Hair":          H("none",    "#8a3f6e", "#3a1a2e", 0.8,  True,  "round", "comb",              "mark_only",   "top_left",      "stamp",    "humanist", 400, "caps",      2.5, True),
    "Mirefield Naturals":   H("thin",    "#3a8a6a", "#183a2c", 0.95, False, "sharp", "droplet_leaf",      "mark_only",   "top_right",     "flag",     "mono",     400, "title",     1.5),
    "Puddlecombe Toys":     H("ticks",   "#2a86c4", "#16344a", 1.25, False, "round", "puddle",            "mark_only",   "bottom_right",  "plain",    "sans",     700, "smallcaps", 2.0, True),
    "Freshfold":            H("rounded", "#4a90a8", "#1e3a44", 0.9,  True,  "sharp", "fold",              "mark_only",   "bottom_left",   "underline", "serif",   700, "caps",      1.5),
    "Soapwell":             H("double",  "#6a5ac0", "#26204a", 1.15, True,  "round", "bubbles",           "mark_only",   "top_left",      "rect",     "sans",     400, "title",     2.5),
    # Invented brands of the Mens clothing depth (gen#310): a color or category word in the name.
    "Black Curlew":         H("thin",    "#1a1a1a", "#262626", 1.2,  False, "sharp", "stacked_bars",      "mark_left",   "bottom_left",   "none",     "sans",     700, "smallcaps", 1.5),
    "Yellow Plover":        H("ticks",   "#d9a400", "#3a3000", 0.85, True,  "round", "half_disc",         "badge",       "bottom_center", "none",     "humanist", 400, "caps",      0.5, True),
    "Blue Bull":            H("double",  "#1f4e9c", "#14284a", 1.1,  False, "round", "bull_horns",        "mark_right",  "top_right",     "none",     "serif",    700, "caps",      1.2),
    "Jacket Wren":          H("double",  "#3f6b4f", "#1e3327", 1.05, False, "round", "slanted_blades",    "mark_only",   "top_right",     "stamp",    "mono",     400, "title",     1.0),
    # Invented brands of the knitwear depth (gen#309): a color or category word in the name, each a
    # full lockup so the drawing's logo text is the brand.
    "White Heron":          H("rounded", "#3d5a80", "#1b2a40", 0.95, False, "round", "twin_arcs",         "mark_above",  "top_center",    "none",     "serif",    700, "title",     2.3),
    "Red Kite":             H("heavy",   "#b3382c", "#401410", 1.1,  True,  "sharp", "comet",             "pill",        "bottom_right",  "none",     "sans",     400, "lower",     0.8),
    "Cardigan Finch":       H("ticks",   "#7a5c2e", "#33260f", 1.0,  False, "round", "notched_square",    "mark_right",  "top_left",      "none",     "humanist", 700, "caps",      1.7),
    # The invented brands of the apparel decoys (decoy_apparel, gen#311, class 7).
    "Red Plover":           H("thin",    "#b5382c", "#3a1a16", 1.0,  False, "round", "egg_pair",              "mark_left",   "bottom_left",   "none",     "serif",    400, "title",     1.0),
    "Blue Otter":           H("double",  "#2f5d9a", "#182b48", 1.1,  False, "sharp", "ripples",              "mark_above",  "top_left",      "none",     "sans",     700, "caps",      2.0),
    "Green Stoat":          H("rounded", "#3f7d3a", "#1d3a1b", 1.2,  True,  "round", "paw_print",            "band_top",    "top_center",     "none",     "humanist", 400, "lower",     0.5),
    "Yellow Wagtail":       H("heavy",   "#c49a1c", "#41330a", 1.0,  False, "sharp", "tail_comb",           "pill",        "top_center",    "none",     "mono",     400, "smallcaps", 1.5),
    "Black Lapwing":        H("none",    "#222222", "#111111", 1.3,  False, "sharp", "plume",            "mark_right",  "top_right",     "none",     "sans",     700, "caps",      3.0),
    "White Dormouse":       H("ticks",   "#8a8a8a", "#2e2e2e", 0.9,  True,  "round", "oak_leaf",             "badge",       "bottom_center", "none",     "serif",    400, "title",     0.0),
    "Jumper Jay":           H("thin",    "#8a3fa0", "#341a3e", 1.0,  False, "round", "chevron_trio",            "band_bottom", "bottom_center",      "none",     "humanist", 700, "title",     1.0),
    # The invented sportswear brand (gen#722).
    "Knacks":               H("rounded", "#111111", "#111111", 1.0,  False, "round", "laced_eyelets",     "mark_left",   "bottom_left",   "none",     "sans",     400, "lower",     0.5),
    "Coat Crake":           H("double",  "#7a5a3a", "#30241a", 1.1,  False, "sharp", "toggle",              "mark_only",   "bottom_left",   "stamp",    "mono",     700, "lower",     2.0),
    # The beauty depth brands (type_specs, gen#214): invented, text only.
    "Aldermist":           H("double", "#b0486a", "#3a1a28", 0.85, False, "sharp", "mist_cloud", "mark_only", "top_left", "outline", "humanist", 700, "caps", 1.0),
    "Citrus Heron":        H("rounded", "#4a8a52", "#1e3a22", 0.90, False, "round", "sparkle", "mark_only", "top_right", "flag", "serif", 400, "smallcaps", 1.5),
    "Clay Wren":           H("heavy", "#9a3a78", "#38183a", 0.95, False, "sharp", "jar", "mark_only", "bottom_left", "underline", "humanist", 400, "lower", 2.0),
    "Cloth Wren":          H("ticks", "#6a4fa0", "#2a1c3e", 1.00, False, "round", "feather", "mark_only", "bottom_right", "tab", "serif", 700, "title", 2.5),
    "Dewy Finch":          H("none", "#2f7f7a", "#123a38", 1.05, False, "sharp", "dropper", "mark_only", "top_left", "rect", "humanist", 400, "caps", 1.0),
    "Fenmere":             H("thin", "#3a6f8f", "#16303e", 0.85, True, "round", "flask", "mark_only", "top_right", "plain", "serif", 400, "smallcaps", 1.5),
    "Pearlbrook":          H("double", "#b9803a", "#3e2a12", 0.90, False, "sharp", "pearl_row", "mark_only", "bottom_left", "stamp", "humanist", 700, "lower", 2.0),
    "Red Kestrel":         H("rounded", "#b0486a", "#3a1a28", 0.95, False, "round", "lip_swipe", "mark_only", "bottom_right", "outline", "serif", 400, "title", 2.5),
    "Rose Kestrel":        H("heavy", "#4a8a52", "#1e3a22", 1.00, False, "sharp", "rose_bud", "mark_only", "top_left", "flag", "humanist", 400, "caps", 1.0),
    "Sorrel & Salt":       H("ticks", "#9a3a78", "#38183a", 1.05, False, "round", "shell", "mark_only", "top_right", "underline", "serif", 700, "smallcaps", 1.5),
    "Thornlea Skin":       H("none", "#6a4fa0", "#2a1c3e", 0.85, False, "sharp", "tube", "mark_only", "bottom_left", "tab", "serif", 400, "lower", 2.0),
    "Coconut Plover":      H("thin", "#2f7f7a", "#123a38", 0.95, False, "round", "coconut_palm", "mark_only", "bottom_left", "rect", "humanist", 700, "title", 1.5),
    "Vanilla Wren":        H("thin", "#2f7f7a", "#123a38", 0.90, True, "round", "compact", "mark_only", "bottom_right", "rect", "serif", 400, "title", 2.5),
    "Veilmoor":            H("double", "#3a6f8f", "#16303e", 0.95, False, "sharp", "moon_stars", "mark_only", "top_left", "plain", "humanist", 700, "caps", 1.0),
    "Vitamin C Orchard":   H("rounded", "#b9803a", "#3e2a12", 1.00, False, "round", "lash_fan", "mark_only", "top_right", "stamp", "serif", 400, "smallcaps", 1.5),
    # Invented brands of the toy text-match decoys (gen#424): a toy type word beside the name.
    "Tumblewick":           H("thin",    "#3b5bdb", "#1b2a5c", 1.0,  False, "round", "toy_pair_dots",     "mark_left",   "bottom_left",   "none",     "sans",     700, "caps",      1.5),
    "Quillbury":            H("double",  "#c0392b", "#4a1a16", 1.1,  False, "sharp", "toy_ring_dot",      "mark_only",   "top_left",      "underline", "serif",   400, "title",     2.0),
    "Kite Lane Toys":       H("rounded", "#2e8b57", "#16392a", 0.95, True,  "round", "toy_star",          "mark_right",  "top_right",     "none",     "humanist", 700, "smallcaps", 1.0),
    "Dewhatch":             H("ticks",   "#1c8ec7", "#12394f", 1.05, False, "round", "toy_three_rings",   "mark_above",  "bottom_center", "none",     "sans",     400, "caps",      2.5),
    "Pennyfold":            H("heavy",   "#d9822b", "#4a2e12", 1.2,  False, "sharp", "toy_diag_dots",     "mark_only",   "bottom_right",  "stamp",    "mono",     700, "title",     0.5),
    "Hobbleby":             H("thin",    "#c2539a", "#4a1c3a", 0.9,  True,  "round", "toy_stack_rings",   "badge",       "bottom_left",   "none",     "serif",    400, "smallcaps", 1.5, True),
    "Tidewell":             H("thin",    "#1c7c7d", "#0f3b3c", 1.0,  False, "round", "well",         "mark_left",   "bottom_right",  "none",     "sans",     400, "caps",      1.5),
    "Skerry & Cole":        H("double",  "#7a2e3a", "#2b1a1d", 1.05, False, "sharp", "saltire",      "badge",       "top_left",      "none",     "serif",    700, "smallcaps", 1.0),
}
# fmt: on


def lockup_key(style: HouseStyle) -> tuple:
    """What makes a logo's arrangement and wordmark: no two brands share it."""
    return (
        style.layout,
        style.place,
        style.tag,
        style.font,
        style.weight,
        style.case,
        style.spacing,
        style.italic,
    )


def field_names() -> list[str]:
    return [f.name for f in fields(HouseStyle)]


def differing(a: HouseStyle, b: HouseStyle) -> int:
    return sum(x != y for x, y in zip(astuple(a), astuple(b), strict=True))


from synthetic_ecommerce_data.domains.retail import (  # noqa: E402
    appliance_brand_styles,  # noqa: E402,F401 -- gen#334, #721: eight marks and styles join the tables
    bicycle_brand_styles,  # noqa: E402,F401 -- gen#718: seven marks and styles join the tables
    color_word_brand_styles,  # noqa: E402,F401 -- gen#312: six marks and styles join the tables
    diy_brand_styles,  # noqa: E402,F401 -- gen#191: four marks and styles join the tables
    electronics_brand_styles,  # noqa: E402,F401 -- gen#332, #721, #724: 17 marks and styles of the Electronics department join the tables
    grocery_brand_styles,  # noqa: E402,F401 -- gen#376: 22 marks and styles of the 50K grocery tier join the tables
    luggage_brand_styles,  # noqa: E402,F401 -- gen#209: three marks and styles join the tables
    place_brand_styles,  # noqa: E402,F401 -- gen#663: 15 marks and styles of the class 6 place brands join the tables
)
