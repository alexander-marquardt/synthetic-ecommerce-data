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
    """Stub of the red commit: a pack adds nothing to its drawing."""
    return {}
