"""The pack is drawn smaller when its line sells a smaller size of it (gen#543).

A 30 ml jar and a 100 ml jar of one line used to be one drawing. Now a SKU's pack is scaled by
about the cube root of its content against the line's largest size, which is how real packs
grow: half the content is a pack about 0.79 as tall.

- THE REFERENCE is the largest size the line sells. It is drawn at the shape's natural size
  (the cap, 1.0), so a line of one size, and the largest size of any line, draw exactly as
  before and keep their image ids.
- THE FLOOR is :data:`FLOOR`: a size below about a fifth of the largest still draws at 0.6, so it
  stays legible. A shape drawn to fill its picture has its own, higher floor
  (:data:`SHAPE_FLOORS`).
- THE CONTENT is the SKU's ``net_volume_ml`` or ``net_weight_g`` (a multipack's is its total). A
  count (``units_per_pack``) stands in only where there is no content and only in
  :data:`COUNT_DEPARTMENTS`: a pack of six cans is bigger than a single can, but a pack of three
  bodysuits holds the same bodysuit, so a garment is never scaled by its count.
- A PACK OF ITEMS takes no factor: its copies show its size (:mod:`pack_copies`, gen#728), and a
  factor on top would shrink the items twice.
- A SHAPE THAT DRAWS ITS OWN SIZE takes no factor (:data:`SELF_SIZED`). Each family of such
  shapes, and each shape with its own floor, is a module of :mod:`pack_scale_families` that says
  why (#1151): both tables are built by walking that package, so a family adds or edits its own
  module there and this file gains no line.
- THE CANVAS is unchanged: :func:`wrap` scales the pack about the bottom center of its bounding
  box, so every size of a line stands on one baseline and one center line of the same 400 x 400
  sheet.

Each size is its own image (``export.drawing_spec`` carries the factor), as a lamp's finish is.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.domains.retail import pack_copies, pack_scale_families

#: The smallest factor: a tiny size still draws at this share of the largest.
FLOOR = 0.6
#: The content keys, in the order they are read: a total content beats a count.
CONTENT_KEYS = ("net_volume_ml", "net_weight_g")
#: The shapes whose drawing shows its own size, which take no factor, and shape -> its own
#: smallest factor over :data:`FLOOR`: one module of :mod:`pack_scale_families` per family.
SELF_SIZED, SHAPE_FLOORS = pack_scale_families.tables()
#: The count key, and the departments whose pack it sizes.
COUNT_KEY = "units_per_pack"
COUNT_DEPARTMENTS = frozenset({"Food & Drink", "Beauty"})

_SHEET = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{}</svg>'


def quantity(rec: dict[str, Any], sku: dict[str, Any]) -> float | None:
    """The SKU's content (or its count, where a count sizes the pack), or ``None``."""
    for key in CONTENT_KEYS:
        if key in sku:
            return float(sku[key])
    if COUNT_KEY in sku and rec["category_path"][0] in COUNT_DEPARTMENTS:
        return float(sku[COUNT_KEY])
    return None


def factor(rec: dict[str, Any], sku: dict[str, Any]) -> float | None:
    """The factor the SKU's pack is drawn at, or ``None`` for the natural size (the line's
    largest size, a line of one size, or a SKU with no content to size by)."""
    if (rec.get("drawing") or {}).get("shape") in SELF_SIZED:  # it draws its own size
        return None
    own = quantity(rec, sku)
    if not own or own <= 0 or pack_copies.copies(rec, sku) > 1:
        return None
    largest = max(q for q in (quantity(rec, s) for s in rec["skus"]) if q)
    if own >= largest:
        return None
    floor = SHAPE_FLOORS.get((rec.get("drawing") or {}).get("shape"), FLOOR)
    return round(max(floor, (own / largest) ** (1 / 3)), 3)


def wrap(pack: str, parts: list[str], shrink: float) -> str:
    """``pack`` (the SVG elements of the drawing) in a group that scales it by ``shrink`` about
    the bottom center of the box ``parts`` (the shape's own elements) cover."""
    from synthetic_ecommerce_data.domains.retail import (
        sheet_extent,  # noqa: PLC0415 -- deferred: it is the guard's measure
    )

    box = sheet_extent.reach(_SHEET.format("".join(parts)))
    if box is None:
        return pack
    x = (box[0] + box[2]) / 2 * (1 - shrink)
    y = box[3] * (1 - shrink)
    return f'<g class="pack" transform="translate({x:.2f} {y:.2f}) scale({shrink:g})">{pack}</g>'
