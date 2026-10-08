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
* ``placement``: one large motif centred in the surface's print area
  (:data:`PRINT_BOX`, :func:`overlay`), the graphic-tee look.
"""

# ruff: noqa: E501 -- SVG literals and data rows read better whole (prototype only).

from __future__ import annotations

from dataclasses import dataclass

import kit_garments  # noqa: F401 -- registers the parametric garments
import kit_home  # noqa: F401 -- registers home and beauty shapes
import kit_motifs
import kit_produce  # noqa: F401 -- registers produce_pile
import kit_round4  # noqa: F401 -- registers belt, hanger, gift bag, ...
import kit_surfaces  # noqa: F401 -- registers sweatshirt, mug, apron, ...
from kit import OFFSET_Y, PLACEMENTS, SHAPES, SIZE, Fill, _shade

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


def motif_svg(name: str, color: str, cx: float, cy: float, size: float, turn: float = 0) -> str:
    """The motif drawn ``size`` units across, centred on (cx, cy), turned ``turn`` degrees."""
    motif(name)
    body = "".join(SHAPES[name](color, Fill("solid", color, _shade(color, 0.3)), None))
    return (
        f'<g class="motif" data-motif="{name}" transform="translate({cx:g} {cy:g}) '
        f'rotate({turn:g}) scale({size / SIZE:.4g}) translate(-200 {OFFSET_Y.get(name, 0) - 200:g})">'
        f"{body}</g>"
    )


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


#: Printable surface -> its placements and the print area (cx, cy, largest motif) a
#: placement print is centred in.
SURFACES: dict[str, tuple[tuple[str, ...], tuple[float, float, float] | None]] = {
    "tshirt": (PLACEMENTS, (200, 220, 140)),
    "top": (PLACEMENTS, (200, 200, 130)),
    "sweatshirt": (PLACEMENTS, (200, 200, 130)),
    "pyjamas": (("all-over", "scatter", "placement"), (110, 196, 72)),
    "dress": (("all-over", "scatter"), None),
    "blouse": (("all-over", "scatter"), None),
    "skirt": (("all-over", "scatter"), None),
    "sheet": (("all-over", "scatter"), None),
    "pillow": (PLACEMENTS, (200, 216, 150)),
    "duvet": (PLACEMENTS, (200, 210, 160)),
    "cushion": (PLACEMENTS, (200, 206, 180)),
    "tea_towel": (PLACEMENTS, (200, 186, 150)),
    "apron": (PLACEMENTS, (200, 196, 90)),
    "mug": (PLACEMENTS, (185, 235, 140)),
    "beach_towel": (("all-over", "scatter"), None),
    "gift_bag": (("all-over", "scatter"), None),
    "wrapping_paper": (("all-over", "scatter"), None),
}


def check_surface(shape: str, placement: str) -> None:
    """ValueError unless ``shape`` takes a print laid out as ``placement``."""
    if shape not in SURFACES:
        raise ValueError(f"{shape!r} is not a printable surface")
    if placement not in SURFACES[shape][0]:
        raise ValueError(f"{shape!r} takes no {placement!r} print")


def overlay(shape: str, fill: Fill) -> str:
    """A placement print's one motif, centred in ``shape``'s print area."""
    check_surface(shape, "placement")
    cx, cy, most = SURFACES[shape][1] or (0, 0, 0)
    size = fill.scale * SIZE
    if size > most:
        raise ValueError(f"a {size:g}-unit motif overflows {shape!r}'s {most:g}-unit print area")
    return motif_svg(fill.motif or "", fill.accent, cx, cy, size)


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
