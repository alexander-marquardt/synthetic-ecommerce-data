"""Tableware and kitchen utensil shapes for the retail drawing kit (gen#198).

Each kind of the tableware rows (:mod:`tableware_rows`) has its own flat drawing in the
kit's house style: outlines in the kit's ink, the record's fill (color and pattern) on
the product's main surface, so a shopper tells a plate from a bowl, a fork from a spoon
and a chef's knife from a bread knife at thumbnail size.

==============  ==================================================  =======================
shape           draws                                               params
==============  ==================================================  =======================
plate           a plate in three-quarter view, its rim and well,    kind, diameter, finish
                drawn to scale over a dimension line
bowl            a bowl from the side, its rim showing the inside    kind
cutlery_piece   one piece, or a pack's count fanned from one point  piece, handle, count, edge
kitchen_knife   a knife lying flat, its blade drawn to scale; a     kind, blade, blade_max
                block set draws the block and its handles
drinking_glass  a glass in the record's tint: stemmed or tumbler    kind
kitchen_utensil one utensil standing up, or a set in its pot        kind, material
chopping_board  a board in three-quarter view with a handle hole    material
grill_press     a cast-iron steak weight: a ribbed slab under a     --
                wooden bar handle
colander        a perforated bowl on a foot ring, with handles      material
==============  ==================================================  =======================

Every params value is a string, as a style row's ``params`` carry it, and every param has
a default, so each shape also draws bare (as a motif does).
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _path, _shade, _tint, register
from kit_garments import _dark
from kit_home import _dim

STEEL = "#cfd5da"
STEEL_DARK = "#8f989f"
WOOD = "#b8875a"
WOOD_DARK = "#7d5634"
BLACK = "#2f2f35"


def _num(value: str, default: float) -> float:
    """The number at the head of a param ("27", "27 cm"), else ``default``."""
    try:
        return float(str(value).split()[0])
    except (ValueError, IndexError):
        return default


def _ellipse(
    cx: float, cy: float, rx: float, ry: float, fill: str, width: float = LW, extra: str = ""
) -> str:
    return (
        f'<ellipse{extra} cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
        f'fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'
    )


def _circle(
    cx: float, cy: float, r: float, fill: str, width: float = LW_DETAIL, extra: str = ""
) -> str:
    return (
        f'<circle{extra} cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
        f'stroke="{INK}" stroke-width="{width}"/>'
    )


def _shadow(cx: float, cy: float, rx: float) -> str:
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{rx * 0.08:.1f}" fill="#000000" fill-opacity=".08"/>'


# --------------------------------------------------------------------------
# Plates and bowls
# --------------------------------------------------------------------------

#: Plate kind -> (well radius as a share of the rim's, the view's squash, an oval's stretch).
PLATE_KINDS = {
    "dinner": (0.68, 0.46, 1.0),
    "side": (0.66, 0.46, 1.0),
    "pasta": (0.56, 0.5, 1.0),
    "serving platter": (0.74, 0.42, 1.0),
}
#: The widest plate, in cm, that fills the sheet; a smaller one is drawn to that scale.
PLATE_SCALE_CM = 36.0


def plate(paint: str, fill: Fill, label: str | None, kind: str = "dinner", diameter: str = "27",
          finish: str = "") -> list[str]:  # fmt: skip
    """A plate seen from above at an angle: the rim in the fill, the well a shade inside it.

    The rim's width on the sheet is its diameter to one scale, so a side plate draws smaller
    than a dinner plate, and the dimension line under it names the size. A pasta plate's
    well is deep (its inner wall shows); a serving platter is an oval. A ``rim band`` finish
    draws a dark band round the edge."""
    well, squash, _ = PLATE_KINDS.get(kind, PLATE_KINDS["dinner"])
    cm = _num(diameter, 27.0)
    rx = 165 * min(cm, PLATE_SCALE_CM) / PLATE_SCALE_CM
    oval = kind == "serving platter"
    ry = rx * (0.62 if oval else 1.0) * squash
    cx, cy = 200.0, 182.0
    inner = _tint(fill.base, 0.35)
    out = [
        _shadow(cx, cy + ry + 14, rx * 0.95),
        _ellipse(cx, cy + 9, rx * 0.97, ry * 0.97, _shade(fill.base, 0.2)),
        _ellipse(cx, cy, rx, ry, paint, extra=' class="rim"'),
    ]
    if "band" in finish.lower():
        out.append(
            _ellipse(
                cx,
                cy,
                rx * 0.93,
                ry * 0.93,
                "none",
                5,
                extra=f' stroke-opacity=".9" style="stroke:{_shade(fill.base, 0.55)}"',
            )
        )
    out.append(
        _ellipse(
            cx,
            cy + (6 if kind == "pasta" else 2),
            rx * well,
            ry * well,
            inner,
            LW_DETAIL,
            extra=' class="well"',
        )
    )
    if kind == "pasta":  # the deep well's far wall in shadow
        out.append(
            _dark(
                f"M{cx - rx * well:.1f},{cy + 6:.1f} A{rx * well:.1f},{ry * well:.1f} 0 0 1 {cx + rx * well:.1f},{cy + 6:.1f} "
                f"A{rx * well * 0.9:.1f},{ry * well * 0.62:.1f} 0 0 0 {cx - rx * well:.1f},{cy + 6:.1f} Z",
                0.16,
            )
        )
    out.append(
        _highlight(
            f"M{cx - rx * 0.8:.1f},{cy - ry * 0.3:.1f} Q{cx - rx * 0.6:.1f},{cy - ry * 0.85:.1f} {cx - rx * 0.15:.1f},{cy - ry * 0.95:.1f}",
            5,
            0.55,
        )
    )
    out += _dim(cx - rx, cy + ry + 52, cx + rx, cy + ry + 52, f"{cm:g} cm")
    return out


#: Bowl kind -> (half the rim's width, depth, half the foot's width, the rim's squash).
BOWL_KINDS = {
    "cereal": (112, 96, 52, 0.26),
    "soup": (118, 86, 46, 0.26),
    "pasta": (150, 58, 70, 0.24),
    "salad": (140, 100, 62, 0.24),
    "serving": (150, 108, 70, 0.22),
    "mixing": (126, 128, 66, 0.26),
}


def bowl(paint: str, fill: Fill, label: str | None, kind: str = "cereal") -> list[str]:
    """A bowl from the side, a little from above: the outside in the fill, the rim's ellipse
    showing the inside a shade lighter. Each kind has its own width and depth; a soup bowl
    swells, a mixing bowl is deep and has a pouring lip."""
    w, h, foot, squash = BOWL_KINDS.get(kind, BOWL_KINDS["cereal"])
    cx = 200.0
    ry = w * squash
    top = 196 - h / 2
    bottom = top + h
    swell = 1.08 if kind == "soup" else 1.0
    body = (
        f"M{cx - w:.1f},{top:.1f} C{cx - w * swell:.1f},{top + h * 0.75:.1f} {cx - foot - 30:.1f},{bottom:.1f} {cx - foot:.1f},{bottom:.1f} "
        f"L{cx + foot:.1f},{bottom:.1f} C{cx + foot + 30:.1f},{bottom:.1f} {cx + w * swell:.1f},{top + h * 0.75:.1f} {cx + w:.1f},{top:.1f} Z"
    )
    out = [
        _shadow(cx, bottom + 16, w * 0.85),
        _path(
            f"M{cx - foot:.1f},{bottom - 2:.1f} L{cx - foot + 6:.1f},{bottom + 12:.1f} L{cx + foot - 6:.1f},{bottom + 12:.1f} L{cx + foot:.1f},{bottom - 2:.1f} Z",
            _shade(fill.base, 0.25),
        ),
        _path(body, paint, extra=' class="bowl"'),
        _dark(
            f"M{cx + w * 0.55:.1f},{top + 8:.1f} C{cx + w * 0.9:.1f},{top + h * 0.6:.1f} {cx + foot + 20:.1f},{bottom - 4:.1f} {cx + foot:.1f},{bottom - 2:.1f} L{cx + w:.1f},{bottom - 2:.1f} L{cx + w:.1f},{top:.1f} Z",
            0.0,
        ),
        _ellipse(cx, top, w, ry, _tint(fill.base, 0.4)),
        _dark(
            f"M{cx - w + 6:.1f},{top:.1f} A{w - 6:.1f},{ry - 4:.1f} 0 0 1 {cx + w - 6:.1f},{top:.1f} A{w - 6:.1f},{ry * 0.55:.1f} 0 0 0 {cx - w + 6:.1f},{top:.1f} Z",
            0.14,
        ),
        _highlight(
            f"M{cx - w * 0.8:.1f},{top + h * 0.25:.1f} Q{cx - w * 0.72:.1f},{top + h * 0.6:.1f} {cx - w * 0.45:.1f},{top + h * 0.8:.1f}",
            6,
            0.5,
        ),
    ]
    if kind == "mixing":  # the pouring lip on the right of the rim
        out.append(
            _path(
                f"M{cx + w - 4:.1f},{top - 12:.1f} Q{cx + w + 26:.1f},{top - 4:.1f} {cx + w + 22:.1f},{top + 6:.1f} Q{cx + w + 4:.1f},{top + 12:.1f} {cx + w - 10:.1f},{top + 10:.1f} Z",
                paint,
            )
        )
    return out


# --------------------------------------------------------------------------
# Cutlery and knives
# --------------------------------------------------------------------------

#: Cutlery piece -> (its head, its length on the sheet, the head's size).
PIECES = {
    "dinner knife": ("knife", 290, 1.0),
    "steak knife": ("steak", 280, 1.0),
    "steak knife and fork": ("steak", 280, 1.0),
    "dinner fork": ("fork", 285, 1.0),
    "dessert spoon": ("spoon", 255, 0.9),
    "teaspoon": ("spoon", 200, 0.68),
    "serving spoon": ("spoon", 310, 1.2),
}


def _cutlery_head(head: str, top: float, s: float, metal: str, edge: str = "serrated") -> list[str]:
    """The working end of one piece, its tip at ``top``, centred on x = 0."""
    if head == "fork":
        w, tine = 19 * s, 56 * s
        d = f"M{-w:.1f},{top + 6:.1f}"
        xs = [-w + i * (2 * w) / 7 for i in range(8)]
        for i in range(0, 8, 2):
            d += f" L{xs[i]:.1f},{top:.1f} L{xs[i + 1]:.1f},{top:.1f} L{xs[i + 1]:.1f},{top + tine:.1f}"
            if i + 2 < 8:
                d += f" L{xs[i + 2]:.1f},{top + tine:.1f}"
        d += f" L{w:.1f},{top + tine + 22 * s:.1f} Q{w:.1f},{top + tine + 46 * s:.1f} 6,{top + tine + 62 * s:.1f} L-6,{top + tine + 62 * s:.1f} Q{-w:.1f},{top + tine + 46 * s:.1f} {-w:.1f},{top + tine + 22 * s:.1f} Z"
        return [_path(d, metal)]
    if head == "spoon":
        rx, ry = 22 * s, 36 * s
        return [
            _path(
                f"M-6,{top + ry * 1.7:.1f} L-5,{top + ry * 2.3:.1f} L5,{top + ry * 2.3:.1f} L6,{top + ry * 1.7:.1f} Z",
                metal,
            ),
            _ellipse(0, top + ry, rx, ry, metal),
            _ellipse(
                0,
                top + ry * 0.95,
                rx * 0.72,
                ry * 0.75,
                "none",
                LW_DETAIL,
                extra=' stroke-opacity=".45"',
            ),
            _highlight(
                f"M{-rx * 0.6:.1f},{top + ry * 0.7:.1f} Q{-rx * 0.5:.1f},{top + ry * 0.25:.1f} {-rx * 0.1:.1f},{top + ry * 0.15:.1f}",
                3,
                0.8,
            ),
        ]
    if head == "steak" and edge == "straight":  # a plain pointed blade, no teeth
        return [
            _path(
                f"M2,{top:.1f} Q12,{top + 40:.1f} 11,{top + 140:.1f} L-11,{top + 140:.1f} L-11,{top + 30:.1f} Q-8,{top + 14:.1f} 2,{top:.1f} Z",
                metal,
            ),
            _highlight(f"M-5,{top + 34:.1f} L-5,{top + 128:.1f}", 3, 0.7),
        ]
    if head == "steak":
        teeth = " ".join(f"L{-11 + (i % 2) * 4:.1f},{top + 30 + i * 8:.1f}" for i in range(14))
        return [
            _path(
                f"M2,{top:.1f} Q12,{top + 40:.1f} 11,{top + 140:.1f} L-11,{top + 140:.1f} L-11,{top + 30:.1f} {teeth} L-11,{top + 140:.1f} L-11,{top + 30:.1f} Q-8,{top + 14:.1f} 2,{top:.1f} Z",
                metal,
            )
        ]
    return [  # a dinner knife: a rounded tip, a straight back
        _path(
            f"M-3,{top:.1f} Q12,{top + 10:.1f} 12,{top + 40:.1f} L11,{top + 140:.1f} L-10,{top + 140:.1f} L-10,{top + 12:.1f} Q-10,{top:.1f} -3,{top:.1f} Z",
            metal,
        ),
        _highlight(f"M-4,{top + 18:.1f} L-4,{top + 128:.1f}", 3, 0.7),
    ]


def _cutlery_handle(handle: str, y0: float, y1: float, paint: str, fill: Fill) -> list[str]:
    """The handle from the neck (``y0``) to the end (``y1``), centred on x = 0."""
    d = f"M-6,{y0:.1f} L-13,{y1 - 14:.1f} Q-13,{y1:.1f} 0,{y1:.1f} Q13,{y1:.1f} 13,{y1 - 14:.1f} L6,{y0:.1f} Z"
    if handle == "wooden":
        return [
            _path(d, WOOD, extra=' class="handle"'),
            _line(
                f"M-4,{y0 + 30:.1f} Q-1,{(y0 + y1) / 2:.1f} -5,{y1 - 20:.1f} M4,{y0 + 40:.1f} Q7,{(y0 + y1) / 2 + 10:.1f} 3,{y1 - 14:.1f}",
                1.2,
                stroke=WOOD_DARK,
            ),
            _circle(0, y0 + 26, 2.6, STEEL, 0.8),
            _circle(0, y1 - 22, 2.6, STEEL, 0.8),
        ]
    out = [
        _path(d, paint, extra=' class="handle"'),
        _highlight(f"M-6,{y0 + 14:.1f} L-9,{y1 - 18:.1f}", 3, 0.5),
    ]
    if handle == "hammered":
        out += [
            _circle(
                -3 + 6 * (i % 2), y0 + 18 + i * 11, 2.6, "none", 0.9, extra=' stroke-opacity=".55"'
            )
            for i in range(int((y1 - y0 - 30) / 11))
        ]
    return out


def cutlery_piece(paint: str, fill: Fill, label: str | None, piece: str = "dinner fork",
                  handle: str = "plain", count: str = "1",
                  edge: str = "serrated") -> list[str]:  # fmt: skip
    """One piece of cutlery standing up, in the record's finish; a pack fans its count.

    The piece's head (tines, a spoon's bowl, a rounded or a serrated pointed blade) and
    its length on the sheet tell the pieces apart: a teaspoon is short, a serving spoon
    long. A wooden handle is wood with two rivets; a hammered one carries its dimples. A
    steak knife's ``edge`` is serrated (teeth) or straight (plain). A ``steak knife and
    fork`` set fans its knives and forks alternately, ``count`` pieces in all."""
    head, length, s = PIECES.get(piece, PIECES["dinner fork"])
    n = max(1, min(int(_num(count, 1)), 8))
    pivot_y = 340.0
    metal = paint
    step = 34 / max(n - 1, 1) if n > 1 else 0
    steps = [-(n - 1) * step / 2 + i * step for i in range(n)]
    out = [_shadow(200, pivot_y + 10, 70 + 10 * n)]
    for i, angle in enumerate(steps):
        h, ln, sc = ("fork", 285, 1.0) if piece == "steak knife and fork" and i % 2 else (head, length, s)
        top = pivot_y - ln
        neck = top + (
            140 if h in ("knife", "steak") else 56 * sc + 62 * sc if h == "fork" else 36 * sc * 2.3
        )
        parts = [
            *_cutlery_head(h, top, sc, metal, edge),
            *_cutlery_handle(handle, neck, pivot_y, paint, fill),
        ]
        out.append(
            f'<g class="piece" transform="translate(200 0) rotate({angle:g} 0 {pivot_y:g})">{"".join(parts)}</g>'
        )
    return out


#: Kitchen knife kind -> (blade height at the heel, the tip's shape, a serrated edge).
KNIFE_KINDS = {
    "chef's": (60, "curve", False),
    "santoku": (54, "sheep", False),
    "bread": (36, "round", True),
    "paring": (30, "point", False),
    "carving": (34, "point", False),
    "utility": (34, "point", False),
}
#: Sheet units per cm of blade: a 25 cm blade and its handle fill the width.
KNIFE_SCALE = 9.6


def _knife(x0: float, y: float, kind: str, blade_cm: float, paint: str, fill: Fill) -> list[str]:
    """One knife lying flat, its handle's end at ``x0`` and its edge's heel at ``y``."""
    h, tip, serrated = KNIFE_KINDS.get(kind, KNIFE_KINDS["chef's"])
    bl = blade_cm * KNIFE_SCALE
    hx = x0 + 104  # the bolster
    end = hx + 12 + bl
    spine = y - h
    if tip == "curve":
        blade = f"M{hx + 12:.1f},{spine:.1f} L{end - bl * 0.25:.1f},{spine + 4:.1f} Q{end - 10:.1f},{spine + h * 0.45:.1f} {end:.1f},{y - h * 0.15:.1f} Q{end - bl * 0.3:.1f},{y + 4:.1f} {hx + 12:.1f},{y:.1f} Z"
    elif tip == "sheep":
        blade = f"M{hx + 12:.1f},{spine:.1f} L{end - bl * 0.3:.1f},{spine:.1f} Q{end:.1f},{spine + 6:.1f} {end:.1f},{y - 4:.1f} L{hx + 12:.1f},{y:.1f} Z"
    elif tip == "round":
        blade = f"M{hx + 12:.1f},{spine:.1f} L{end - 14:.1f},{spine:.1f} Q{end:.1f},{spine + 2:.1f} {end:.1f},{y - h / 2:.1f} Q{end:.1f},{y:.1f} {end - 14:.1f},{y:.1f} L{hx + 12:.1f},{y:.1f} Z"
    else:
        blade = f"M{hx + 12:.1f},{spine:.1f} L{end - bl * 0.35:.1f},{spine:.1f} Q{end - bl * 0.1:.1f},{spine + h * 0.3:.1f} {end:.1f},{y - h * 0.25:.1f} Q{end - bl * 0.4:.1f},{y + 2:.1f} {hx + 12:.1f},{y:.1f} Z"
    out = [
        '<g class="knife">',
        _path(blade, STEEL),
        _highlight(
            f"M{hx + 22:.1f},{spine + 7:.1f} L{end - bl * 0.4:.1f},{spine + 7:.1f}", 3, 0.75
        ),
    ]
    if serrated:
        out.append(
            _line(
                " ".join(
                    f"M{x:.1f},{y:.1f} Q{x + 5:.1f},{y - 7:.1f} {x + 10:.1f},{y:.1f}"
                    for x in range(int(hx + 16), int(end - 22), 10)
                ),
                1.2,
            )
        )
    if tip == "sheep":  # the hollow-ground dimples of a santoku
        out += [
            _ellipse(x, y - 12, 5, 3, "none", 1.1, extra=' stroke-opacity=".6"')
            for x in range(int(hx + 34), int(end - 50), 26)
        ]
    out += [
        _path(
            f"M{hx:.1f},{y - h * 0.62 - 6:.1f} L{hx + 14:.1f},{spine - 2:.1f} L{hx + 14:.1f},{y + 2:.1f} L{hx:.1f},{y + 4:.1f} Z",
            STEEL_DARK,
        ),
        _path(
            f"M{x0:.1f},{y - 26:.1f} Q{x0 - 4:.1f},{y - 8:.1f} {x0 + 6:.1f},{y + 6:.1f} L{hx:.1f},{y + 4:.1f} L{hx:.1f},{y - h * 0.62 - 6:.1f} Q{x0 + 50:.1f},{y - 34:.1f} {x0:.1f},{y - 26:.1f} Z",
            paint,
            extra=' class="handle"',
        ),
        *[_circle(x0 + 26 + i * 28, y - 12, 3.4, STEEL, 1.0) for i in range(3)],
        "</g>",
    ]
    return out


def kitchen_knife(
    paint: str, fill: Fill, label: str | None, kind: str = "chef's", blade: str = "20",
    blade_max: str = "",
) -> list[str]:
    """A kitchen knife lying flat, the handle in the record's color, the blade to scale.

    A chef's knife has a deep curved blade, a santoku a sheepsfoot tip and dimples, a
    bread knife a long serrated edge with a round end, a paring knife a short point. The
    dimension line names the blade's length, or the range ``blade``-``blade_max`` when the
    style is sold in several (one image serves every length). ``kind="block"`` draws a knife block set."""
    if kind == "block":
        return _knife_block(paint, fill)
    cm = _num(blade, 20.0)
    bl = cm * KNIFE_SCALE
    x0 = (400 - (116 + bl)) / 2
    out = [_shadow(200, 236, 150), *_knife(x0, 220, kind, cm, paint, fill)]
    # a paring knife's short line would hide under "8 cm blade": its chip says "8 cm"
    hi = _num(blade_max, cm) if blade_max else cm
    span = f"{cm:g}-{hi:g}" if hi != cm else f"{cm:g}"
    text = f"{span} cm blade" if 10 + 7 * len(f"{span} cm blade") + 20 <= bl else f"{span} cm"
    out += _dim(x0 + 116, 290, x0 + 116 + bl, 290, text)
    return out


def _knife_block(paint: str, fill: Fill) -> list[str]:
    """An angled block in the record's color with five handles of rising size."""
    out = [_shadow(200, 344, 140)]
    for i, (x, w) in enumerate(((150, 22), (182, 24), (214, 26), (246, 24), (276, 20))):
        y = 120 - i * 6 + (i % 2) * 14
        out.append(
            _path(
                f"M{x - w / 2:.1f},{y + 70:.1f} L{x - w / 2 - 22:.1f},{y:.1f} Q{x - 22:.1f},{y - 14:.1f} {x + w / 2 - 22:.1f},{y:.1f} L{x + w / 2:.1f},{y + 70:.1f} Z",
                BLACK,
                extra=' class="handle"',
            )
        )
        out.append(_circle(x - 15, y + 30, 2.6, STEEL, 0.8))
    out += [
        _path("M110,178 L290,150 L330,336 L136,340 Z", paint, extra=' class="block"'),
        _dark("M290,150 L330,336 L300,338 L268,156 Z", 0.18),
        _line("M126,250 L300,236 M132,296 L314,288", 1.2),
        _highlight("M126,196 L148,322", 5, 0.4),
    ]
    return out


# --------------------------------------------------------------------------
# Glassware
# --------------------------------------------------------------------------


def _bowl_glass(
    cx: float, top: float, w: float, h: float, stem_to: float, foot: float, flare: float
) -> tuple[str, str, str]:
    """A stemmed glass's bowl, stem and foot paths: ``w`` half the rim, ``h`` the bowl's depth."""
    bowl_d = (
        f"M{cx - w:.1f},{top:.1f} C{cx - w * flare:.1f},{top + h * 0.7:.1f} {cx - 10:.1f},{top + h:.1f} {cx - 4:.1f},{top + h + 6:.1f} "
        f"L{cx + 4:.1f},{top + h + 6:.1f} C{cx + 10:.1f},{top + h:.1f} {cx + w * flare:.1f},{top + h * 0.7:.1f} {cx + w:.1f},{top:.1f} Z"
    )
    stem = f"M{cx - 4:.1f},{top + h + 4:.1f} L{cx - 4:.1f},{stem_to:.1f} L{cx + 4:.1f},{stem_to:.1f} L{cx + 4:.1f},{top + h + 4:.1f} Z"
    foot_d = f"M{cx - foot:.1f},{stem_to + 8:.1f} Q{cx:.1f},{stem_to - 10:.1f} {cx + foot:.1f},{stem_to + 8:.1f} Q{cx:.1f},{stem_to + 18:.1f} {cx - foot:.1f},{stem_to + 8:.1f} Z"
    return bowl_d, stem, foot_d


#: Stemmed glass kind -> (half the rim, bowl depth, how far the bowl swells past the rim).
STEMMED = {"wine": (58, 130, 1.25), "champagne flute": (30, 175, 1.08), "gin": (92, 112, 1.12)}
#: Tumbler kind -> (half the rim, half the base, height).
TUMBLERS = {"highball": (52, 46, 250), "tumbler": (70, 60, 150), "beer": (64, 48, 262)}


def drinking_glass(paint: str, fill: Fill, label: str | None, kind: str = "wine") -> list[str]:
    """A glass in the record's tint, its outline in ink: a stemmed wine glass, a tall flute
    or a balloon gin glass, or a highball, a heavy-based tumbler or a pint glass."""
    cx = 200.0
    glaze = ' class="glass" fill-opacity=".55"'
    rim_tint = _tint(fill.base, 0.6)
    if kind in STEMMED:
        w, h, flare = STEMMED[kind]
        top = 50.0 if kind != "gin" else 80.0
        stem_to = 318.0
        bowl_d, stem, foot_d = _bowl_glass(
            cx, top, w, h, stem_to, 62 if kind != "champagne flute" else 52, flare
        )
        return [
            _shadow(cx, stem_to + 16, 70),
            _path(foot_d, paint, extra=glaze),
            _path(stem, paint, LW_DETAIL + 0.6, extra=glaze),
            _path(bowl_d, paint, extra=glaze),
            _ellipse(cx, top, w, w * 0.18, rim_tint, LW_DETAIL),
            _highlight(
                f"M{cx - w * 0.6:.1f},{top + 18:.1f} Q{cx - w * 0.75:.1f},{top + h * 0.45:.1f} {cx - w * 0.35:.1f},{top + h * 0.8:.1f}",
                6,
                0.75,
            ),
        ]
    w, base, height = TUMBLERS.get(kind, TUMBLERS["tumbler"])
    bottom = 330.0
    top = bottom - height
    if kind == "beer":  # a nonic pint: the bulge a little below the rim
        body = f"M{cx - w:.1f},{top:.1f} L{cx - w - 6:.1f},{top + 34:.1f} L{cx - w + 2:.1f},{top + 52:.1f} L{cx - base:.1f},{bottom:.1f} L{cx + base:.1f},{bottom:.1f} L{cx + w - 2:.1f},{top + 52:.1f} L{cx + w + 6:.1f},{top + 34:.1f} L{cx + w:.1f},{top:.1f} Z"
    else:
        body = f"M{cx - w:.1f},{top:.1f} L{cx - base:.1f},{bottom:.1f} L{cx + base:.1f},{bottom:.1f} L{cx + w:.1f},{top:.1f} Z"
    thick = 26 if kind == "tumbler" else 14
    return [
        _shadow(cx, bottom + 8, w + 6),
        _path(body, paint, extra=glaze),
        _path(
            f"M{cx - base + 2:.1f},{bottom - thick:.1f} L{cx + base - 2:.1f},{bottom - thick:.1f} L{cx + base:.1f},{bottom:.1f} L{cx - base:.1f},{bottom:.1f} Z",
            _shade(fill.base, 0.15),
            LW_DETAIL,
            extra=' fill-opacity=".7"',
        ),
        _ellipse(cx, top, w, w * 0.18, rim_tint, LW_DETAIL),
        _highlight(
            f"M{cx - w * 0.6:.1f},{top + 20:.1f} L{cx - base * 0.6:.1f},{bottom - thick - 10:.1f}",
            7,
            0.7,
        ),
    ]


# --------------------------------------------------------------------------
# Kitchen utensils
# --------------------------------------------------------------------------


def _utensil_handle(x: float, y0: float, y1: float, color: str) -> list[str]:
    """A long handle from the head (``y0``) down to its hanging hole near ``y1``."""
    return [
        _path(
            f"M{x - 7:.1f},{y0:.1f} L{x - 11:.1f},{y1 - 12:.1f} Q{x:.1f},{y1 + 8:.1f} {x + 11:.1f},{y1 - 12:.1f} L{x + 7:.1f},{y0:.1f} Z",
            color,
            extra=' class="handle"',
        ),
        _circle(x, y1 - 14, 3.8, "#fbfaf6", 1.0),
    ]


def _utensil_head(kind: str, x: float, top: float, paint: str) -> tuple[list[str], float]:
    """The working end of one utensil at ``top``; returns it and where the handle starts."""
    if kind == "spatula":
        d = f"M{x - 30:.1f},{top + 6:.1f} Q{x - 30:.1f},{top:.1f} {x - 22:.1f},{top:.1f} L{x + 22:.1f},{top:.1f} Q{x + 30:.1f},{top:.1f} {x + 30:.1f},{top + 6:.1f} L{x + 26:.1f},{top + 82:.1f} Q{x:.1f},{top + 96:.1f} {x - 26:.1f},{top + 82:.1f} Z"
        return [_path(d, paint, extra=' class="head"')], top + 90
    if kind == "turner":
        d = f"M{x - 38:.1f},{top + 6:.1f} L{x + 34:.1f},{top:.1f} L{x + 30:.1f},{top + 86:.1f} Q{x:.1f},{top + 100:.1f} {x - 28:.1f},{top + 88:.1f} Z"
        slots = _line(
            " ".join(
                f"M{x + dx:.1f},{top + 18:.1f} L{x + dx:.1f},{top + 70:.1f}"
                for dx in (-18, -6, 6, 18)
            ),
            4,
        )
        return [_path(d, paint, extra=' class="head"'), slots], top + 92
    if kind in ("ladle", "slotted spoon"):
        r = 40 if kind == "ladle" else 30
        out = [
            _ellipse(
                x,
                top + r * 0.9,
                r,
                r * 0.9 if kind == "ladle" else r * 1.25,
                paint,
                extra=' class="head"',
            )
        ]
        if kind == "ladle":
            out.append(
                _ellipse(
                    x,
                    top + r * 0.55,
                    r * 0.82,
                    r * 0.32,
                    _tint("#888888", 0.6),
                    LW_DETAIL,
                    extra=' fill-opacity=".35"',
                )
            )
        else:
            out += [
                _circle(x + dx, top + 22 + dy, 3.4, "#fbfaf6", 1.0)
                for dx in (-10, 0, 10)
                for dy in (0, 14, 28)
            ]
        return out, top + r * 1.9
    if kind == "whisk":
        loops = "".join(
            _path(
                f"M{x - 5:.1f},{top + 150:.1f} C{x - w:.1f},{top + 70:.1f} {x - w:.1f},{top:.1f} {x:.1f},{top:.1f} C{x + w:.1f},{top:.1f} {x + w:.1f},{top + 70:.1f} {x + 5:.1f},{top + 150:.1f}",
                "none",
                2.4,
                stroke=paint,
            )
            for w in (44, 30, 16)
        )
        return [
            loops,
            _path(
                f"M{x - 6:.1f},{top + 138:.1f} L{x + 6:.1f},{top + 138:.1f} L{x + 7:.1f},{top + 160:.1f} L{x - 7:.1f},{top + 160:.1f} Z",
                STEEL,
            ),
        ], top + 160
    if kind == "masher":
        d = f"M{x - 40:.1f},{top:.1f} L{x + 40:.1f},{top:.1f} L{x + 40:.1f},{top + 14:.1f} L{x - 40:.1f},{top + 14:.1f} Z"
        return [
            _path(d, paint, extra=' class="head"'),
            _line(f"M{x - 36:.1f},{top + 7:.1f} L{x + 36:.1f},{top + 7:.1f}", 1.0),
            *[_circle(x + dx, top + 7, 2.4, "#fbfaf6", 0.8) for dx in range(-30, 31, 10)],
            _path(
                f"M{x - 30:.1f},{top + 14:.1f} Q{x - 26:.1f},{top + 60:.1f} {x - 5:.1f},{top + 80:.1f} L{x + 5:.1f},{top + 80:.1f} Q{x + 26:.1f},{top + 60:.1f} {x + 30:.1f},{top + 14:.1f}",
                "none",
                4,
                stroke=STEEL_DARK,
            ),
        ], top + 80
    if kind == "peeler":
        return [
            _path(
                f"M{x - 34:.1f},{top:.1f} L{x - 26:.1f},{top:.1f} L{x - 4:.1f},{top + 60:.1f} L{x + 4:.1f},{top + 60:.1f} L{x + 26:.1f},{top:.1f} L{x + 34:.1f},{top:.1f} L{x + 10:.1f},{top + 70:.1f} L{x - 10:.1f},{top + 70:.1f} Z",
                paint,
                extra=' class="head"',
            ),
            _path(
                f"M{x - 28:.1f},{top + 8:.1f} L{x + 28:.1f},{top + 8:.1f} L{x + 28:.1f},{top + 18:.1f} L{x - 28:.1f},{top + 18:.1f} Z",
                STEEL,
                LW_DETAIL,
            ),
            _line(f"M{x - 24:.1f},{top + 13:.1f} L{x + 24:.1f},{top + 13:.1f}", 1.0),
        ], top + 66
    if kind == "tongs":
        arm = "M{a:.1f},{t:.1f} L{b:.1f},{u:.1f} L{c:.1f},{u:.1f} L{d:.1f},{t:.1f} Z"
        return [
            _path(arm.format(a=x - 44, b=x - 10, c=x - 2, d=x - 34, t=top, u=top + 200), STEEL),
            _path(arm.format(a=x + 34, b=x + 2, c=x + 10, d=x + 44, t=top, u=top + 200), STEEL),
            _path(
                f"M{x - 52:.1f},{top - 4:.1f} Q{x - 40:.1f},{top - 14:.1f} {x - 28:.1f},{top - 4:.1f} L{x - 30:.1f},{top + 30:.1f} L{x - 48:.1f},{top + 30:.1f} Z",
                paint,
                extra=' class="head"',
            ),
            _path(
                f"M{x + 28:.1f},{top - 4:.1f} Q{x + 40:.1f},{top - 14:.1f} {x + 52:.1f},{top - 4:.1f} L{x + 48:.1f},{top + 30:.1f} L{x + 30:.1f},{top + 30:.1f} Z",
                paint,
            ),
            _path(
                f"M{x - 14:.1f},{top + 140:.1f} L{x + 14:.1f},{top + 140:.1f} L{x + 12:.1f},{top + 210:.1f} L{x - 12:.1f},{top + 210:.1f} Z",
                paint,
            ),
        ], -1
    # a solid spoon
    return [
        _ellipse(x, top + 36, 28, 38, paint, extra=' class="head"'),
        _highlight(
            f"M{x - 14:.1f},{top + 22:.1f} Q{x - 10:.1f},{top + 10:.1f} {x:.1f},{top + 8:.1f}",
            3,
            0.6,
        ),
    ], top + 72


def _grater(paint: str, fill: Fill) -> list[str]:
    """A four-sided box grater: perforated steel sides, a handle and a base in the color."""
    holes = [
        _ellipse(x, y, 4, 2.4, "none", 1.0)
        for x in range(160, 241, 16)
        for y in range(130, 301, 18)
    ]
    return [
        _shadow(200, 334, 100),
        _path("M150,96 L250,96 L264,322 L136,322 Z", STEEL),
        _dark("M226,96 L250,96 L264,322 L240,322 Z", 0.14),
        *holes,
        _path("M136,316 L264,316 L268,336 L132,336 Z", paint),
        _path(
            "M170,96 Q170,52 200,52 Q230,52 230,96 L218,96 Q218,66 200,66 Q182,66 182,96 Z",
            paint,
            extra=' class="handle"',
        ),
    ]


def _utensil_set(paint: str, fill: Fill) -> list[str]:
    """A pot in the record's color holding a ladle, a turner, a spoon and a whisk."""
    out = [_shadow(200, 344, 110)]
    for kind, x, top, tilt in (
        ("ladle", 156, 56, -10),
        ("turner", 200, 40, 0),
        ("whisk", 244, 70, 10),
        ("spoon", 222, 90, 5),
    ):
        head, start = _utensil_head(kind, 0, top, _shade(fill.base, 0.3))
        handle = _utensil_handle(0, start, 300, _shade(fill.base, 0.3))
        out.append(
            f'<g transform="translate({x} 0) rotate({tilt} 0 300)">{"".join(head + handle)}</g>'
        )
    out += [
        _path("M118,200 L282,200 L270,338 L130,338 Z", paint, extra=' class="pot"'),
        _ellipse(200, 200, 82, 14, _shade(fill.base, 0.35), LW),
        _dark("M248,214 L280,214 L270,338 L244,338 Z", 0.16),
    ]
    return out


def kitchen_utensil(paint: str, fill: Fill, label: str | None, kind: str = "spatula",
                    material: str = "silicone") -> list[str]:  # fmt: skip
    """One utensil standing up, its head in the record's color: a spatula, a slotted turner,
    a ladle, a slotted spoon, a balloon whisk, a pair of tongs, a masher, a Y peeler or a
    box grater; ``kind="set"`` draws a set standing in its pot. A wooden or stainless one
    draws its handle in that material."""
    if kind == "grater":
        return _grater(paint, fill)
    if kind == "set":
        return _utensil_set(paint, fill)
    mat = material.lower()
    handle = (
        WOOD
        if "wood" in mat or "bamboo" in mat
        else STEEL
        if "stainless" in mat
        else _shade(fill.base, 0.2)
    )
    top = 46.0
    head, start = _utensil_head(kind, 200, top, paint)
    out = [_shadow(200, 344, 60), *head]
    if start > 0:
        out = [_shadow(200, 344, 60), *_utensil_handle(200, start - 4, 336, handle), *head]
    return out


# --------------------------------------------------------------------------
# Boards and colanders
# --------------------------------------------------------------------------


def chopping_board(paint: str, fill: Fill, label: str | None, material: str = "wood") -> list[str]:
    """A board in three-quarter view with its edge showing and a hanging hole: wood has a
    flowing grain, bamboo its glued strips, plastic a juice groove, glass a shine and feet."""
    mat = material.lower()
    top = "M64,176 L272,106 L346,200 L136,284 Z"
    out = [
        '<ellipse cx="206" cy="304" rx="150" ry="14" fill="#000000" fill-opacity=".08"/>',
        _path("M64,176 L136,284 L136,302 L64,194 Z", _shade(fill.base, 0.25)),
        _path("M136,284 L346,200 L346,218 L136,302 Z", _shade(fill.base, 0.15)),
        _path(
            top, paint, extra=' class="board"' + (' fill-opacity=".6"' if mat == "glass" else "")
        ),
        _ellipse(98, 177, 10, 6, "#fbfaf6", LW_DETAIL),
    ]
    if "bamboo" in mat:
        out.append(
            _line(
                " ".join(
                    f"M{86 + i * 21:.1f},{168 - i * 7:.1f} L{158 + i * 21:.1f},{276 - i * 8.4:.1f}"
                    for i in range(1, 10)
                ),
                1.2,
                extra=' stroke-opacity=".6"',
            )
        )
    elif "wood" in mat:
        out.append(
            _line(
                "M118,190 Q170,160 220,170 T320,190 M140,226 Q200,196 250,206 T330,206 M110,160 Q160,132 230,138 T296,140",
                1.3,
                extra=' stroke-opacity=".55"',
            )
        )
    elif "glass" in mat:
        out += [
            _highlight("M120,186 L240,140", 8, 0.8),
            *[_ellipse(x, y, 7, 4, BLACK, 1.0) for x, y in ((84, 196), (140, 296), (330, 220))],
        ]
    else:
        out.append(
            _path(
                "M92,178 L270,118 L326,198 L142,268 Z", "none", 2.2, stroke=_shade(fill.base, 0.35)
            )
        )
    return out


def colander(
    paint: str, fill: Fill, label: str | None, material: str = "stainless steel"
) -> list[str]:
    """A colander: a perforated bowl on a foot ring with two handles. A collapsible silicone
    one shows its folding ribs, an enamel one a dark rim band, a plastic one slotted holes."""
    mat = material.lower()
    cx, top, w, h = 200.0, 140.0, 140.0, 130.0
    bottom = top + h
    body = f"M{cx - w:.1f},{top:.1f} C{cx - w:.1f},{top + h * 0.8:.1f} {cx - 90:.1f},{bottom:.1f} {cx - 64:.1f},{bottom:.1f} L{cx + 64:.1f},{bottom:.1f} C{cx + 90:.1f},{bottom:.1f} {cx + w:.1f},{top + h * 0.8:.1f} {cx + w:.1f},{top:.1f} Z"
    out = [
        _shadow(cx, bottom + 30, 110),
        _path(
            f"M{cx - 64:.1f},{bottom - 2:.1f} L{cx - 74:.1f},{bottom + 22:.1f} L{cx + 74:.1f},{bottom + 22:.1f} L{cx + 64:.1f},{bottom - 2:.1f} Z",
            _shade(fill.base, 0.25),
        ),
        _path(
            f"M{cx - w + 4:.1f},{top + 10:.1f} Q{cx - w - 40:.1f},{top + 8:.1f} {cx - w - 30:.1f},{top + 34:.1f} Q{cx - w - 10:.1f},{top + 40:.1f} {cx - w + 6:.1f},{top + 34:.1f}",
            "none",
            7,
        ),
        _path(
            f"M{cx + w - 4:.1f},{top + 10:.1f} Q{cx + w + 40:.1f},{top + 8:.1f} {cx + w + 30:.1f},{top + 34:.1f} Q{cx + w + 10:.1f},{top + 40:.1f} {cx + w - 6:.1f},{top + 34:.1f}",
            "none",
            7,
        ),
        _path(body, paint, extra=' class="colander"'),
        _ellipse(cx, top, w, 34, _tint(fill.base, 0.4)),
        _dark(
            f"M{cx - w + 6:.1f},{top:.1f} A{w - 6:.1f},30 0 0 1 {cx + w - 6:.1f},{top:.1f} A{w - 6:.1f},18 0 0 0 {cx - w + 6:.1f},{top:.1f} Z",
            0.14,
        ),
    ]
    if "collapsible" in mat or "silicone" in mat:
        out.append(
            _line(
                " ".join(
                    f"M{cx - w * f:.1f},{top + h * t:.1f} Q{cx:.1f},{top + h * t + 22:.1f} {cx + w * f:.1f},{top + h * t:.1f}"
                    for f, t in ((0.97, 0.3), (0.86, 0.58), (0.7, 0.84))
                ),
                2.2,
            )
        )
    if "enamel" in mat:
        out.append(_ellipse(cx, top, w, 34, "none", 6, extra=f' style="stroke:{BLACK}"'))
    hole = (
        (lambda x, y: _ellipse(x, y, 2.2, 6, "#fbfaf6", 0.9))
        if "plastic" in mat
        else (lambda x, y: _circle(x, y, 3.2, "#fbfaf6", 0.9))
    )
    for row, (y, half) in enumerate(((top + 52, 118), (top + 78, 106), (top + 104, 84))):
        n = int(2 * half / 20)
        out += [hole(cx - half + 10 + i * 20 + (row % 2) * 10, y) for i in range(n)]
    return out


def grill_press(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A cast-iron steak weight (grill press): a ribbed slab seen from above and in front,
    a wooden bar handle on two posts. The slab is the record's color."""
    face = "M64,236 L250,190 L340,240 L154,290 Z"
    edge_l = _path("M64,236 L154,290 L154,314 L64,260 Z", _shade(fill.base, 0.3))
    edge_r = _path("M154,290 L340,240 L340,264 L154,314 Z", _shade(fill.base, 0.2))
    ribs = " ".join(
        f"M{64 + (250 - 64) * t:.1f},{236 + (190 - 236) * t:.1f} L{154 + (340 - 154) * t:.1f},{290 + (240 - 290) * t:.1f}"
        for t in (i / 7 for i in range(1, 7))
    )
    return [
        _shadow(200, 330, 150),
        edge_l,
        edge_r,
        _path(face, paint, extra=' class="slab"'),
        _line(ribs, 2.2, ' stroke-opacity=".55"', _shade(fill.base, 0.5)),
        _path("M168,246 L168,186 L186,186 L186,242 Z", STEEL),
        _path("M232,234 L232,174 L250,174 L250,230 Z", STEEL),
        _path("M156,172 Q208,148 262,166 L262,184 Q208,168 156,190 Z", WOOD, extra=' class="handle"'),
        _highlight(f"M{110},{240} L{200},{214}", 4, 0.4),
    ]


register({
    "plate": plate,
    "bowl": bowl,
    "cutlery_piece": cutlery_piece,
    "kitchen_knife": kitchen_knife,
    "drinking_glass": drinking_glass,
    "kitchen_utensil": kitchen_utensil,
    "chopping_board": chopping_board,
    "colander": colander,
    "grill_press": grill_press,
})  # fmt: skip

#: The shapes this module adds, in its table's order.
SHAPES = ("plate", "bowl", "cutlery_piece", "kitchen_knife", "drinking_glass",
          "kitchen_utensil", "chopping_board", "colander", "grill_press")  # fmt: skip
