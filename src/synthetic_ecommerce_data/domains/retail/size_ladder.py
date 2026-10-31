"""Size-scaled drawings: one image per rung of a product's size ladder (gen#339, gen#719).

Every size of a color used to share one drawing, so a product's sizes showed the same image
repeated. A product with more than one size now draws each size at its own scale: symbolic, not
true to dimension, so S is visibly smaller than M, and a 50 cm frame than a 58 cm one.

- THE SCALE is the size's rank in the product's OWN ladder (the distinct primary sizes of its
  SKUs, smallest first), stepped evenly from :data:`BOTTOM` (the smallest) to :data:`TOP` (the
  largest), the scale the full-size drawing stands for (the largest keeps the style's size, the
  smallest draws at ``BOTTOM / TOP`` of it). A product with one size has no ladder
  and is not scaled (:func:`size_scale` is ``None``).
- THE PRIMARY SIZE is the one dimension that is bigger or smaller (:func:`primary`): the first key
  of the type's declared axis (:data:`size_axes.AXES`) that varies within the product. That is a
  footwear chart row (its UK, EU and US sizes are one rung), a letter size, a kids' age size, a
  garment number or a measure, and for a two-dimensional size its first dimension only (a bra's
  band, a trouser's waist). A fit that is not bigger or smaller (petite, regular, tall, a bra's
  cup, a jean's inside leg) is not read, so it shares its rung's image.
- WHAT IS NOT SCALED is what no type declares (:data:`size_axes.NOT_SIZES`): a fit, a rating, a
  count, and a pack, which keeps :mod:`pack_scale`.
- ANCHORING. The drawing is scaled about its own bottom center (:func:`stand`), so a ladder reads
  as items standing on one floor. The largest rung is the drawing as it was (``TOP`` is the
  scale the full-size drawing stands for, not a measured share of the sheet), and a smaller
  rung is that drawing times ``scale / TOP``.
"""

from __future__ import annotations

import re
from typing import Any

from synthetic_ecommerce_data.core.size_rungs import BOTTOM, TOP, scale_at
from synthetic_ecommerce_data.domains.retail import size_axes

__all__ = ["BOTTOM", "TOP", "primary", "scale_at", "size_scale", "spec", "stand"]

#: Letter sizes, smallest first; "2XL" is the same rung as "XXL".
LETTERS = ("XXXS", "XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL", "XXXXL")
_ALIASES = {"2XS": "XXS", "3XS": "XXXS", "2XL": "XXL", "3XL": "XXXL", "4XL": "XXXXL"}
#: A size sold by a word, on its own ladder; only the words of one product are ever compared.
WORDS = {
    **{word: float(rank) for rank, word in enumerate(("Small", "Medium", "Large"))},
    **{word: float(rank) for rank, word in enumerate(
        ("Single", "Small Double", "Double", "King Size", "Super King Size"))},  # fmt: skip
    **{word: float(rank) for rank, word in enumerate(("Hand Towel", "Bath Towel", "Bath Sheet"))},
}
_LEADING = re.compile(r"\d+(?:\.\d+)?")
#: A baby's or child's age size, in months or years: "0-3 Mths", "2-3 Yrs", "6 Yrs".
_AGE = re.compile(r"(\d+(?:\.\d+)?)(?:-\d+(?:\.\d+)?)?\s*(Mths?|Yrs?)$", re.IGNORECASE)
#: Two dimensions, which rank by their area: "140 x 200 cm", "5 x 7 in".
_AREA = re.compile(r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)")
#: A height in meters, beside the same plant's in centimeters: "1.2 m".
_METERS = re.compile(r"(\d+(?:\.\d+)?)\s*m$")


def _letter(text: str) -> int | None:
    word = text.strip().upper()
    word = _ALIASES.get(word, word)
    return LETTERS.index(word) if word in LETTERS else None


def _value_order(text: str) -> float:
    """A size's place on its ladder: a word's or a letter's index, else what it measures (a
    bed's "King Size (5 ft)", an age "3-4 Yrs" or "0-3 Mths", a rug's "120 x 170 cm"), else the
    number it opens with (a waist "28", a bra "32B" is band 32)."""
    word = WORDS.get(text.split(" (")[0].strip())
    if word is not None:
        return word
    letter = _letter(text.split("/")[0])  # a pair ("S/M": socks, tights) ranks by its first size
    if letter is not None:
        return float(letter)
    if text.strip().lower() == "newborn":
        return -1.0
    age = _AGE.match(text.strip())
    if age is not None:  # months and years on one scale, as a baby's range runs into a child's
        return float(age.group(1)) * (12 if age.group(2).lower().startswith("y") else 1)
    area = _AREA.match(text.strip())
    if area is not None:
        return float(area.group(1)) * float(area.group(2))
    meters = _METERS.match(text.strip())
    if meters is not None:
        return float(meters.group(1)) * 100
    found = _LEADING.match(text.strip())
    if found is None:
        raise ValueError(f"size {text!r} has no place on a size ladder")
    return float(found.group())


def primary(rec: dict, sku: dict) -> tuple[str, str] | None:
    """``(key, value)``: the SKU's primary size, or ``None`` when its sizes do not scale: the
    first key of its type's axis that varies within the product and that the SKU carries."""
    for key in size_axes.AXES.get(rec["product_type"], ()):
        if key in sku and len({str(s[key]) for s in rec["skus"] if key in s}) > 1:
            return key, str(sku[key])
    return None


def _order(rec: dict, key: str, value: str) -> float:
    """Where a primary size sits on the ladder: its footwear chart row, else its value's order.
    Sizes with one order (a bra's cups of one band) are one rung."""
    if "Footwear" in rec["department"]:  # the chart's row order: "10 Infant" is not a number
        chart = [str(v) for v in rec.get("size_options", {}).get(key, ())]
        if value not in chart:
            raise ValueError(f"{rec['product_id']}: size {value!r} is on no row of its chart")
        return float(chart.index(value))
    return _value_order(value)


def size_scale(rec: dict, sku: dict) -> float | None:
    """The scale the SKU's drawing stands for on its ladder, or ``None`` when it is not scaled."""
    own = primary(rec, sku)
    if own is None:
        return None
    key, value = own
    ladder = sorted({_order(rec, key, str(s[key])) for s in rec["skus"] if key in s})
    if len(ladder) < 2:
        return None
    return scale_at(ladder.index(_order(rec, key, value)), len(ladder))


def stand(body: str, defs: str, size_scale: float | None) -> str:
    """``body`` scaled to ``size_scale`` about its own bottom center.

    The largest rung (and a drawing with no ladder) comes back as it is. ``defs`` holds what the
    body refers to (a pattern, a clip), so the body can be measured.
    """
    if size_scale is None or size_scale >= TOP:
        return body
    from synthetic_ecommerce_data.domains.retail import (
        sheet_extent,  # noqa: PLC0415 -- the measure is needed only for a scaled rung
    )

    svg = f'<svg xmlns="http://www.w3.org/2000/svg"><defs>{defs}</defs>{body}</svg>'
    box = sheet_extent.reach(svg)
    if box is None:
        return body
    x, y = (box[0] + box[2]) / 2, box[3]
    ratio = size_scale / TOP
    return (
        f'<g class="size" transform="translate({x:g} {y:g}) scale({ratio:.4f}) '
        f'translate({-x:g} {-y:g})">{body}</g>'
    )


def spec(rec: dict, sku: dict) -> dict[str, Any]:
    """What a scaled SKU adds to its drawing spec (so to its image id); nothing when unscaled."""
    scale = size_scale(rec, sku)
    return {} if scale is None else {"size_scale": scale}
