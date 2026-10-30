"""A pack of N is drawn as N items, and a pack above 24 as its outer box (gen#728).

Most packs drew one item, so a six-pack looked like a single can. This is the one layout every
family uses: a new family needs no drawing of its own to show its pack.

- THE COUNT is :func:`count`: the SKU's ``units_per_pack``, its ``pack_size`` (``4 x 125g``,
  ``3 pack``, ``40 bags``), the product's one pack attribute, a sock row's ``pairs``, or the title
  ("Fruit Yogurt, 4 Pack", "Pack of 10", "Set of 2", "Twin Pack", "..., Pair").
- ONE DRAWING, MANY USES. The product's own drawing goes once into a ``<defs>`` and each copy is a
  ``<use>`` of it, so ids (a pattern, a clip, a mask) stay unique, the file stays small and every
  copy is the same product in the same swatch. Rear copies are drawn first, so the front one is on
  top.
- UP TO :data:`FILE_MOST`, a file: each copy behind the last, smaller and offset up and to the
  right. ABOVE IT, rows (:func:`rows`): the front row is full size and each row behind is smaller
  and higher, so a six-pack is two in front with two more rows behind.
- THE STACK FITS. Measured with the front copy full size, a stack past the product's area
  (:data:`AREA`) is scaled down as a whole and centered on it.
- ABOVE :data:`MOST_DRAWN` the outer box stands in for the items (:func:`outer_box`): the count
  large on its front, three loose items before it, and a box that grows a little with the count.
- A DRAWING THAT ALREADY DRAWS ITS COUNT is left as it is (:func:`self_drawn`): a pile of fruit
  (told the SKU's count by :func:`pile_count`), a nest of tables, a shape with its own ``count``,
  ``pieces`` or ``units`` of that number. ``tub`` drew its own pots and moved onto this layout, as
  did socks and the school shirt.

A pack takes no pack factor (``pack_scale.factor``): its copies show its size. The count goes
through ``export.drawing_spec``, so each count is its own drawing.
"""

from __future__ import annotations

import math
import re
from html import escape
from typing import Any

from synthetic_ecommerce_data.domains.retail import sheet_extent
from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW_DETAIL,
    _path,
    _word,
)

#: The largest pack drawn item by item; above it the outer box stands in.
MOST_DRAWN = 24
#: The largest pack drawn as a file; above it, rows.
FILE_MOST = 3
#: Each copy of a file against the one before it, and how far it steps, as shares of the item.
FILE_SHRINK = 0.95
FILE_STEP_X = 0.2
FILE_STEP_Y = 0.1
#: Each row against the one before it, and the smallest a rear row is drawn.
ROW_SHRINK = 0.9
ROW_FLOOR = 0.6
#: A row's rise as a share of the item's height, and the column pitch as a share of its width.
ROW_RISE = 0.5
COLUMN_PITCH = 0.94
#: The area a product stands in on the sheet: ``x0, y0, x1, y1`` (see ``house_styles``).
AREA = (24.0, 28.0, 376.0, 362.0)
#: The loose items before an outer box, and the box the first of them fits.
LOOSE = 3
LOOSE_BOX = 116.0
#: The outer box's share of its largest size at the smallest and largest count it has to tell.
BOX_SMALLEST = 0.74
BOX_LARGEST_COUNT = 240

#: The params a shape draws its own count from, and the shapes that always draw their own.
OWN_COUNT = ("count", "pieces", "units")
SELF_DRAWN_SHAPES = frozenset({"anti_vibration_mat", "produce_pile", "side_table"})
#: What a shape that draws several in one drawing is told, so that a copy is one item.
ONE_ITEM = {
    "bath_towel": {"folded": "1"},
    "hangers": {"nested": "1"},
    "travel_organizer": {"cubes": "1"},
}

_PACK_SIZE = re.compile(r"(\d+)\s*(?:x|pack|bags)\b", re.IGNORECASE)
_TITLE = (
    re.compile(r"\b(?:pack|set) of (\d+)\b", re.IGNORECASE),
    re.compile(r"\b(\d+)[ -]?(?:pack|pk)\b", re.IGNORECASE),
)
_TWO = re.compile(r"\btwin pack\b|\bpair$", re.IGNORECASE)
_SHEET = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{}</svg>'

#: One copy: its center x, its baseline y and its scale, with the front copy at ``(0, 0, 1)``.
Place = tuple[float, float, float]


def _attribute(rec: dict[str, Any]) -> int | None:
    """The count of the product's one pack attribute; ``None`` when it has none, or several."""
    values = {a["value"] for a in rec.get("attributes", ()) if a["key"] == "units_per_pack"}
    sizes = {a["value"] for a in rec.get("attributes", ()) if a["key"] == "pack_size"}
    if len(values) == 1:
        return int(next(iter(values)))
    sized = _PACK_SIZE.match(next(iter(sizes))) if len(sizes) == 1 else None
    return int(sized[1]) if sized else None


def _titled(title: str) -> int:
    """The count the title names, or 1."""
    for pattern in _TITLE:
        named = pattern.search(title)
        if named:
            return int(named[1])
    return 2 if _TWO.search(title) else 1


def count(rec: dict[str, Any], sku: dict[str, Any]) -> int:
    """How many items the SKU's pack holds."""
    if "units_per_pack" in sku:
        return int(sku["units_per_pack"])
    sized = _PACK_SIZE.match(str(sku.get("pack_size", "")))
    if sized:
        return int(sized[1])
    attribute = _attribute(rec)
    if attribute is not None:
        return attribute
    pairs = (rec["drawing"].get("params") or {}).get("pairs")
    return int(pairs) if pairs else _titled(rec["title"])


def self_drawn(rec: dict[str, Any], n: int) -> bool:
    """Whether the product's own drawing already shows ``n`` items."""
    drawing = rec["drawing"]
    params = drawing.get("params") or {}
    return drawing["shape"] in SELF_DRAWN_SHAPES or any(
        str(params.get(key)) == str(n) for key in OWN_COUNT
    )


def copies(rec: dict[str, Any], sku: dict[str, Any]) -> int:
    """How many copies of its drawing the SKU's image is laid out from: 1 for a single item and
    for a drawing that shows its own count."""
    n = count(rec, sku)
    return 1 if self_drawn(rec, n) else n


def spec(rec: dict[str, Any], sku: dict[str, Any]) -> dict[str, int]:
    """What a pack adds to its SKU's drawing spec (so to its drawing id): nothing for one item."""
    n = copies(rec, sku)
    return {"pack_count": n} if n > 1 else {}


def pile_count(rec: dict[str, Any], sku: dict[str, Any]) -> dict[str, int]:
    """The ``count`` a pack of fruit draws when it is not the one its line's drawing was made for:
    the drawing holds the line's first pack, so a line that starts at a single would draw its
    4 pack as that single's pile."""
    drawing = rec["drawing"]
    n = count(rec, sku)
    if drawing["shape"] != "produce_pile" or n == 1:
        return {}
    return {} if str((drawing.get("params") or {}).get("count")) == str(n) else {"count": n}


def one_item(shape: str, params: dict | None) -> dict | None:
    """``params``, told to draw one item where the shape draws several by default."""
    return (params or {}) | ONE_ITEM[shape] if shape in ONE_ITEM else params


def rows(n: int, width: float, height: float) -> list[int]:
    """The copies of each row of a pack of ``n`` items of this size, front row first.

    A wide item takes fewer columns, because its rows stack in less height, but never so few that
    the pack becomes a tower. A tall one takes no more than a square would, so that a six-pack
    keeps its two columns. Copies that do not divide evenly go to the rows nearest the front.
    """
    fewest = max(2, math.ceil(math.sqrt(n)) - 1)
    columns = min(round(math.sqrt(n)), max(fewest, round(math.sqrt(n * ROW_RISE * height / width))))
    depth = math.ceil(n / columns)
    each, extra = divmod(n, depth)
    return [each + 1 if row < extra else each for row in range(depth)]


def _file(n: int, width: float, height: float) -> list[Place]:
    """A file of ``n`` copies, front first: each behind the last, smaller, up and to the right."""
    return [
        (i * FILE_STEP_X * width, -i * FILE_STEP_Y * height, FILE_SHRINK**i) for i in range(n)
    ]


def _rows(n: int, width: float, height: float) -> list[Place]:
    """``n`` copies in rows, front row first: each row smaller, and raised over the one before."""
    counts = rows(n, width, height)
    deepest = len(counts) - 1
    shrink = max(ROW_SHRINK, ROW_FLOOR ** (1 / deepest)) if deepest else ROW_SHRINK
    out: list[Place] = []
    base = 0.0
    for depth, across in enumerate(counts):
        size = shrink**depth
        pitch = COLUMN_PITCH * width * size
        out += [(pitch * (c - (across - 1) / 2), base, size) for c in range(across)]
        base -= ROW_RISE * height * size
    return out


def places(n: int, width: float, height: float) -> list[Place]:
    """Where each of ``n`` copies of an item of this size stands, front first, unfitted."""
    return _file(n, width, height) if n <= FILE_MOST else _rows(n, width, height)


def fitted(placed: list[Place], width: float, height: float) -> list[Place]:
    """``placed`` in the sheet's coordinates: scaled down as a whole if it overflows
    :data:`AREA`, and centered on it."""
    left = min(x - s * width / 2 for x, _, s in placed)
    right = max(x + s * width / 2 for x, _, s in placed)
    top = min(y - s * height for _, y, s in placed)
    bottom = max(y for _, y, _ in placed)
    x0, y0, x1, y1 = AREA
    fit = min(1.0, (x1 - x0) / (right - left), (y1 - y0) / (bottom - top))
    return [
        (
            (x0 + x1) / 2 + fit * (x - (left + right) / 2),
            (y0 + y1) / 2 + fit * (y - (top + bottom) / 2),
            fit * s,
        )
        for x, y, s in placed
    ]


def _use(item: str, box: sheet_extent.Box, place: Place) -> str:
    """One copy: the item's bottom center moved onto the place's center and baseline."""
    x, y, size = place
    dx = x - size * (box[0] + box[2]) / 2
    dy = y - size * box[3]
    return (
        f'<use class="pack-copy" href="#{item}" '
        f'transform="translate({dx:.2f} {dy:.2f}) scale({size:.4f})"/>'
    )


def growth(n: int) -> float:
    """The outer box's share of its largest size: it grows with the logarithm of the count, so
    40, 80 and 240 tell apart without a large pack leaving the sheet."""
    span = math.log(n / (MOST_DRAWN + 1)) / math.log(BOX_LARGEST_COUNT / (MOST_DRAWN + 1))
    return min(1.0, BOX_SMALLEST + (1 - BOX_SMALLEST) * span)


def outer_box(n: int, paint: str) -> str:
    """The outer box of a pack of ``n``, in the product's own paint, with the count large on it."""
    grown = growth(n)
    width, height, depth, rise = 250 * grown, 268 * grown, 40 * grown, 30 * grown
    left, bottom = 200 - (width + depth) / 2, 336.0
    top, right = bottom - height, left + width
    panel_x, panel_y = left + width * 0.1, top + height * 0.08
    panel_w, panel_h = width * 0.8, height * 0.52
    middle, word_w = left + width / 2, panel_w - 20
    nw, ne = f"{left:.1f},{top:.1f}", f"{right:.1f},{top:.1f}"
    sw, se = f"{left:.1f},{bottom:.1f}", f"{right:.1f},{bottom:.1f}"
    back_nw = f"{left + depth:.1f},{top - rise:.1f}"
    back_ne = f"{right + depth:.1f},{top - rise:.1f}"
    back_se = f"{right + depth:.1f},{bottom - rise:.1f}"
    return "".join(
        (
            f'<g class="pack-box" data-count="{n}">',
            _path(f"M{nw} L{ne} L{se} L{sw} Z", paint),
            _path(f"M{nw} L{back_nw} L{back_ne} L{ne} Z", paint),
            _path(f"M{ne} L{back_ne} L{back_se} L{se} Z", paint),
            _path(
                f"M{nw} L{back_nw} L{back_ne} L{back_se} L{se} L{ne} Z",
                "#000000",
                1,
                ' fill-opacity=".12"',
            ),
            f'<rect x="{panel_x:.1f}" y="{panel_y:.1f}" width="{panel_w:.1f}" '
            f'height="{panel_h:.1f}" rx="8" fill="#ffffff" stroke="{INK}" '
            f'stroke-width="{LW_DETAIL}"/>',
            _word(escape(str(n)), middle, panel_y + panel_h * 0.42, word_w, panel_h * 0.66),
            _word("pack", middle, panel_y + panel_h * 0.84, word_w, panel_h * 0.17),
            "</g>",
        )
    )


def _loose(width: float, height: float) -> list[Place]:
    """Where the loose items stand before an outer box, front first."""
    size = min(1.0, LOOSE_BOX / width, LOOSE_BOX / height)
    x0, _, x1, y1 = AREA
    middle, across = (x0 + x1) / 2, (x1 - x0) / 2 - size * width / 2
    return [(middle, y1, size), (middle - across, y1, size), (middle + across, y1, size)]


def layout(body: str, parts: list[str], n: int, paint: str, uid: str) -> str:
    """``body`` (the product's drawing on the sheet) drawn as a pack of ``n``: copies of it, or
    the outer box and loose items above :data:`MOST_DRAWN`. ``parts`` are the shape's own elements,
    the box a copy is measured by."""
    box = sheet_extent.reach(_SHEET.format("".join(parts)))
    if box is None:
        return body
    width, height = box[2] - box[0], box[3] - box[1]
    item = f"pack-item-{uid}"
    if n > MOST_DRAWN:
        front = _loose(width, height)
        before = outer_box(n, paint)
    else:
        front = fitted(places(n, width, height), width, height)
        before = ""
    uses = "".join(_use(item, box, place) for place in reversed(front))
    return (
        f'<g class="pack" data-count="{n}"><defs><g id="{item}">{body}</g></defs>{before}{uses}</g>'
    )
