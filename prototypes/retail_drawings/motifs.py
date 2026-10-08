"""Motif prints: any kit drawing repeated on a printable surface (gen#125).

The **registry** (:func:`registry`) is every shape the kit can draw, read
from :data:`kit.SHAPES` at call time, so the motif pool grows as product
types are added. A shape's category comes from :data:`kit_motifs.CATEGORY`
(fruit, vegetables, animals, flowers, stars, seasonal, food treats, ...); any
other kit shape is a ``product`` motif, which, like ``tools``, only a novelty
or gift range may print (:func:`allowed`).

A print is a :class:`kit.Fill` with ``pattern="print"``: ``base`` is the
ground color, ``accent`` the motif's color, and ``motif``, ``placement``,
``scale`` and ``spacing`` say what is printed and how. Every value comes
from the record, never from a random draw:

* ``all-over``: the motif scaled into an SVG ``<pattern>`` tile of edge
  ``spacing``, twice, as a half-drop repeat (:func:`print_defs`);
* ``scatter``: a sparser tile holding the motif three times at the fixed
  sizes and turns of :data:`SCATTER`;
* ``placement``: one motif centred in the surface's print area
  (:data:`PRINT_BOX`, :func:`overlay`), the graphic-tee look. Here ``scale``
  is the share of the print area the motif's drawn box covers
  (:func:`drawn_box`), so a thin hammer and a round orange at the same scale
  look the same size; a large graphic is :data:`LARGE_SCALE`.
"""

# ruff: noqa: E501 -- SVG literals and data rows read better whole (prototype only).

from __future__ import annotations

import math
import re
from dataclasses import dataclass

import kit_garments  # noqa: F401 -- registers the parametric garments
import kit_home  # noqa: F401 -- registers home and beauty shapes
import kit_motifs
import kit_produce  # noqa: F401 -- registers produce_pile
import kit_round4  # noqa: F401 -- registers belt, hanger, gift bag, ...
import kit_surfaces  # noqa: F401 -- registers sweatshirt, mug, apron, ...
from kit import INK, OFFSET_Y, PLACEMENTS, SHAPES, SIZE, Fill, _shade

#: Printable categories, then the two only novelty and gift ranges may print.
PRINTABLE = ("fruit", "vegetables", "animals", "dinosaurs and vehicles", "flowers", "stars",
             "seasonal", "food treats")  # fmt: skip
NOVELTY_ONLY = ("tools", "product")
CATEGORIES = (*PRINTABLE, *NOVELTY_ONLY)
RANGES = ("core", "novelty", "gift")
NOVELTY_RANGES = ("novelty", "gift")


@dataclass(frozen=True)
class Motif:
    name: str  # the kit shape that draws it
    category: str

    @property
    def label(self) -> str:
        """The motif as a shopper says it: ``christmas_tree`` -> ``Christmas Tree``."""
        return self.name.replace("_", " ").title()


def registry() -> dict[str, Motif]:
    """Every kit shape as a motif, in :data:`kit.SHAPES` order."""
    return {n: Motif(n, kit_motifs.CATEGORY.get(n, "product")) for n in SHAPES}


def motif(name: str) -> Motif:
    found = registry().get(name)
    if found is None:
        raise ValueError(f"unknown motif {name!r}: no kit shape draws it")
    return found


def _body(name: str, color: str) -> str:
    return "".join(SHAPES[name](color, Fill("solid", color, _shade(color, 0.3)), None))


def motif_svg(
    name: str, color: str, cx: float, cy: float, size: float, turn: float = 0,
    origin: tuple[float, float] | None = None,
) -> str:  # fmt: skip
    """The motif's 400-unit sheet drawn ``size`` units across, its ``origin`` (default the
    sheet's centre) on (cx, cy), turned ``turn`` degrees."""
    motif(name)
    ox, oy = origin or (200, 200 - OFFSET_Y.get(name, 0))
    return (
        f'<g class="motif" data-motif="{name}" transform="translate({cx:g} {cy:g}) '
        f'rotate({turn:g}) scale({size / SIZE:.6g}) translate({-ox:g} {-oy:g})">'
        f"{_body(name, color)}</g>"
    )


# --------------------------------------------------------------------------
# A drawing's extent: what a placement print scales, so a thin hammer and a
# round orange both fill the print area the record asks for
# --------------------------------------------------------------------------

_NUM = r"-?\d*\.?\d+(?:e-?\d+)?"
_ARGS = {"M": 2, "L": 2, "T": 2, "H": 1, "V": 1, "Q": 4, "S": 4, "C": 6, "A": 7, "Z": 0}
Affine = tuple[float, float, float, float, float, float]  # x' = a x + c y + e, y' = b x + d y + f
_ID: Affine = (1, 0, 0, 1, 0, 0)


def _mul(m: Affine, n: Affine) -> Affine:
    a, b, c, d, e, f = m
    p, q, r, s, t, u = n
    return (a * p + c * q, b * p + d * q, a * r + c * s, b * r + d * s, a * t + c * u + e, b * t + d * u + f)


def _transform(text: str) -> Affine:
    """An SVG ``transform`` (translate, rotate, scale) as one affine map."""
    m = _ID
    for op, args in re.findall(r"(translate|rotate|scale)\(([^)]*)\)", text):
        v = [float(x) for x in re.findall(_NUM, args)]
        if op == "translate":
            m = _mul(m, (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0))
        elif op == "scale":
            m = _mul(m, (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0))
        else:
            r = math.radians(v[0])
            cx, cy = (v[1], v[2]) if len(v) == 3 else (0, 0)
            m = _mul(m, (1, 0, 0, 1, cx, cy))
            m = _mul(m, (math.cos(r), math.sin(r), -math.sin(r), math.cos(r), 0, 0))
            m = _mul(m, (1, 0, 0, 1, -cx, -cy))
    return m


def _path_points(d: str) -> list[tuple[float, float]]:
    """Every end and control point of path ``d`` (a hull of what it draws); an arc adds
    the box its radii span around its chord's midpoint."""
    out: list[tuple[float, float]] = []
    x = y = sx = sy = 0.0
    tokens = re.findall(rf"[A-Za-z]|{_NUM}", d)
    i, cmd = 0, "M"
    while i < len(tokens):
        if tokens[i].isalpha():
            cmd, i = tokens[i], i + 1
            if cmd in "Zz":
                x, y = sx, sy
                continue
        n = _ARGS[cmd.upper()]
        v = [float(t) for t in tokens[i : i + n]]
        i += n
        rel = cmd.islower()
        up = cmd.upper()
        if up == "H":
            x = v[0] + (x if rel else 0)
        elif up == "V":
            y = v[0] + (y if rel else 0)
        elif up == "A":
            nx, ny = v[5] + (x if rel else 0), v[6] + (y if rel else 0)
            mx, my = (x + nx) / 2, (y + ny) / 2
            out += [(mx - v[0], my - v[1]), (mx + v[0], my + v[1])]
            x, y = nx, ny
        else:
            for k in range(0, n, 2):
                out.append((v[k] + (x if rel else 0), v[k + 1] + (y if rel else 0)))
            x, y = out[-1]
        if up == "M":
            sx, sy = x, y
            cmd = "l" if rel else "L"
        out.append((x, y))
    return out


def _element_points(tag: str, at: dict[str, str]) -> list[tuple[float, float]]:
    g = {k: float(v) for k, v in at.items() if re.fullmatch(_NUM, v or "")}
    if tag == "path":
        return _path_points(at.get("d", ""))
    if tag == "rect":
        x, y = g.get("x", 0), g.get("y", 0)
        return [(x, y), (x + g["width"], y + g["height"])]
    if tag in ("circle", "ellipse"):
        rx, ry = g.get("rx", g.get("r", 0)), g.get("ry", g.get("r", 0))
        return [(g["cx"] - rx, g["cy"] - ry), (g["cx"] + rx, g["cy"] + ry)]
    if tag == "line":
        return [(g["x1"], g["y1"]), (g["x2"], g["y2"])]
    if tag in ("polygon", "polyline"):
        v = [float(t) for t in re.findall(_NUM, at.get("points", ""))]
        return list(zip(v[::2], v[1::2], strict=False))
    return []


def drawn_box(name: str) -> tuple[float, float, float, float]:
    """(x0, y0, x1, y1) of what shape ``name`` draws on its 400-unit sheet (clip paths,
    patterns and definitions aside), through every group's transform."""
    motif(name)
    stack, pts = [_ID], []
    skip = 0
    for close, tag, attrs, selfclose in re.findall(r"<(/?)(\w+)([^>]*?)(/?)>", _body(name, INK)):
        if tag in ("clipPath", "defs", "pattern", "mask", "linearGradient", "radialGradient"):
            skip += -1 if close else (0 if selfclose else 1)
            continue
        if close:
            if tag == "g":
                stack.pop()
            continue
        at = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))
        m = _mul(stack[-1], _transform(at.get("transform", "")))
        if tag == "g" and not selfclose:
            stack.append(m)
            continue
        if skip:
            continue
        a, b, c, d, e, f = m
        corners = _element_points(tag, at)
        if tag in ("rect", "circle", "ellipse") and len(corners) == 2:
            (x0, y0), (x1, y1) = corners
            corners = [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
        pts += [(a * x + c * y + e, b * x + d * y + f) for x, y in corners]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


#: A scatter tile's motifs: (x, y) as a share of the tile, size factor, turn.
SCATTER = ((0.2, 0.25, 1.0, -14), (0.7, 0.45, 0.7, 18), (0.35, 0.8, 0.55, 0))
#: An all-over tile's half-drop: the same motif twice, upright.
HALF_DROP = ((0.25, 0.25, 1.0, 0), (0.75, 0.75, 1.0, 0))


def tile_spots(fill: Fill) -> list[tuple[float, float, float, float]]:
    """Each motif of one repeat tile as (x, y, size, turn), including the copies
    that wrap in from a neighbouring tile, so no motif is cut at the tile's edge."""
    s, size = fill.spacing, fill.scale * SIZE
    layout = HALF_DROP if fill.placement == "all-over" else SCATTER
    out = []
    for fx, fy, k, turn in layout:
        r = size * k / 2
        for dx in (-s, 0, s):
            for dy in (-s, 0, s):
                x, y = fx * s + dx, fy * s + dy
                if -r < x < s + r and -r < y < s + r:
                    out.append((x, y, size * k, turn))
    return out


def print_defs(fill: Fill, pid: str) -> str:
    """The ``<pattern>`` tile of an all-over or scatter print (empty for a placement print)."""
    if fill.placement == "placement":
        return ""
    s = fill.spacing
    body = "".join(motif_svg(fill.motif or "", fill.accent, *spot) for spot in tile_spots(fill))
    return (
        f'<pattern id="{pid}" class="print" data-motif="{fill.motif}" data-placement="{fill.placement}" '
        f'width="{s:g}" height="{s:g}" patternUnits="userSpaceOnUse">'
        f'<rect width="{s:g}" height="{s:g}" fill="{fill.base}"/>{body}</pattern>'
    )


#: Printable surface -> its placements and the print area (cx, cy, width, height) a
#: placement print is centred in. A tee's is the chest between the armholes, from
#: below the neckband to above the hem.
SURFACES: dict[str, tuple[tuple[str, ...], tuple[float, float, float, float] | None]] = {
    "tshirt": (PLACEMENTS, (200, 222, 156, 196)),
    "top": (PLACEMENTS, (200, 206, 140, 170)),
    "sweatshirt": (PLACEMENTS, (200, 214, 150, 170)),
    "pyjamas": (("all-over", "scatter", "placement"), (110, 196, 72, 72)),
    "dress": (("all-over", "scatter"), None),
    "blouse": (("all-over", "scatter"), None),
    "skirt": (("all-over", "scatter"), None),
    "sheet": (("all-over", "scatter"), None),
    "pillow": (PLACEMENTS, (200, 216, 170, 120)),
    "duvet": (PLACEMENTS, (200, 210, 180, 180)),
    "cushion": (PLACEMENTS, (200, 206, 180, 180)),
    "tea_towel": (PLACEMENTS, (200, 204, 150, 220)),
    "apron": (PLACEMENTS, (200, 196, 100, 100)),
    "mug": (PLACEMENTS, (185, 232, 140, 170)),
    "beach_towel": (("all-over", "scatter"), None),
    "gift_bag": (("all-over", "scatter"), None),
    "wrapping_paper": (("all-over", "scatter"), None),
}
#: Each placement surface's print area, from :data:`SURFACES`.
PRINT_BOX = {s: box for s, (_, box) in SURFACES.items() if box is not None}
#: A large placement graphic's drawn box covers this share of the print area
#: (maintainer ruling on the preview: a tee graphic fills 55-65% of the chest);
#: :data:`LARGE_SCALE` is the scale the range records for one.
LARGE = (0.55, 0.65)
LARGE_SCALE = 0.6


def check_surface(shape: str, placement: str) -> None:
    """ValueError unless ``shape`` takes a print laid out as ``placement``."""
    if shape not in SURFACES:
        raise ValueError(f"{shape!r} is not a printable surface")
    if placement not in SURFACES[shape][0]:
        raise ValueError(f"{shape!r} takes no {placement!r} print")


def overlay(shape: str, fill: Fill) -> str:
    """A placement print's one motif, centred in ``shape``'s print area."""
    check_surface(shape, "placement")
    k, (x0, y0, x1, y1) = placement_scale(shape, fill)
    cx, cy, _, _ = PRINT_BOX[shape]
    return motif_svg(fill.motif or "", fill.accent, cx, cy, k * SIZE, origin=((x0 + x1) / 2, (y0 + y1) / 2))


def placement_scale(shape: str, fill: Fill) -> tuple[float, tuple[float, float, float, float]]:
    """(the factor the motif's sheet is drawn at, its drawn box) so that the box covers
    ``fill.scale`` of ``shape``'s print area, or, for a motif too long or too tall to
    cover that much, spans the area's width or height: a print never overflows its area."""
    _, _, w, h = PRINT_BOX[shape]
    box = x0, y0, x1, y1 = drawn_box(fill.motif or "")
    k = math.sqrt(fill.scale * w * h / ((x1 - x0) * (y1 - y0)))
    return min(k, w / (x1 - x0), h / (y1 - y0)), box


# --------------------------------------------------------------------------
# What may be printed where
# --------------------------------------------------------------------------

_KIDS = frozenset({"dinosaurs and vehicles", "animals", "fruit", "stars", "food treats", "seasonal"})
#: (product group, audience) -> the printable categories its range may carry.
ALLOW: dict[tuple[str, str], frozenset[str]] = {
    ("tops", "women"): frozenset({"fruit", "flowers", "stars", "seasonal", "animals"}),
    ("tops", "men"): frozenset({"stars", "seasonal", "animals"}),
    ("tops", "kids"): _KIDS,
    ("sweatshirts", "women"): frozenset({"fruit", "flowers", "stars", "seasonal", "animals"}),
    ("sweatshirts", "kids"): _KIDS,
    ("nightwear", "women"): frozenset({"fruit", "flowers", "stars", "animals", "food treats"}),
    ("nightwear", "kids"): _KIDS,
    ("dresses", "women"): frozenset({"fruit", "flowers"}),
    ("bedding", "adult"): frozenset({"fruit", "flowers", "stars", "animals"}),
    ("bedding", "kids"): frozenset({"dinosaurs and vehicles", "animals", "stars"}),
    ("cushions", "adult"): frozenset({"fruit", "flowers", "animals", "stars", "seasonal"}),
    ("kitchen textiles", "adult"): frozenset({"fruit", "vegetables", "flowers", "food treats"}),
    ("mugs", "adult"): frozenset({"fruit", "flowers", "animals", "stars", "food treats", "seasonal"}),
    ("gift wrap", "adult"): frozenset({"stars", "seasonal", "flowers", "animals", "food treats", "fruit"}),
}
#: Groups whose novelty or gift range may print tools and product drawings.
NOVELTY_GROUPS = ("tops", "sweatshirts", "kitchen textiles", "mugs", "gift wrap")


def allowed(group: str, audience: str, range_: str, name: str) -> bool:
    """Whether a ``range_`` style of ``group`` for ``audience`` may print motif ``name``."""
    if range_ not in RANGES:
        raise ValueError(f"unknown range {range_!r}; one of {RANGES}")
    category = motif(name).category
    if category in NOVELTY_ONLY:
        return range_ in NOVELTY_RANGES and group in NOVELTY_GROUPS
    return category in ALLOW.get((group, audience), frozenset())
