"""A breadth product's sizes, ranked on the one ladder retail reads (gen#719).

A breadth row's drawing is one fixed shape (:mod:`.breadth_shapes`), so its sizes used to share one
picture. :func:`ratios` puts each SKU on the product's own ladder (:mod:`...core.size_rungs`) and
says at what share of the type's scale it is drawn. Every other industrial figure is drawn from
the SKU's own dimensions at one true scale per type, so its sizes already differ and a rank on top
would shrink them twice: they stay at 1.

The ladder needs the values in order, not their measure: :func:`measure` puts a row's sizes, which
mix inch fractions, metric threads and gauge numbers, on one scale. :data:`NOT_SIZES` names the
row attributes that are no bigger or smaller, which share one picture as before.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from synthetic_ecommerce_data.core.size_rungs import ratio_at

#: A row's size attributes that are no size of the part: a kind, a count or a rating.
NOT_SIZES = frozenset({"Color", "Type", "Piece Count", "Rated Load", "Maximum Workpiece Weight"})
#: Sizes sold by a word.
WORDS = {"Small": 0.0, "Medium": 1.0, "Large": 2.0, "X-Large": 3.0}
#: A unit's factor to the row's one scale: millimeters, grams, or the count of what it holds.
UNITS = {"in": 25.4, "mm": 1.0, "g": 1.0, "kg": 1000.0, "oz": 28.35, "ml": 1.0, "Slots": 1.0}
INCH = UNITS["in"]
#: "1/4 in", "1-1/2 in", "10 mm", "M8x1.25", "#8-32", "1/4-20".
_SIZE = re.compile(
    r"(?P<mark>[M#]?)(?:(?P<whole>\d+)-(?=\d+/))?(?P<top>\d+(?:\.\d+)?)(?:/(?P<bottom>\d+))?"
    r"(?:[-x][\d.]+)?\s*(?P<unit>[A-Za-z]*)"
)


def measure(value: str) -> float:
    """``value``'s place among its row's sizes: an inch or a metric thread in millimeters, a gauge
    number by the diameter it stands for, a word by its index."""
    if value in WORDS:
        return WORDS[value]
    found = _SIZE.match(value.split(" to ")[0])  # a range ranks by its lower end
    if found is None:
        raise ValueError(f"size {value!r} has no place on a size ladder")
    number = float(found["top"]) / float(found["bottom"] or 1) + float(found["whole"] or 0)
    if found["mark"] == "#":
        return (0.06 + 0.013 * number) * INCH  # the screw-gauge rule
    if not found["unit"]:  # a metric thread is in millimeters, a thread's fraction in inches
        return number * INCH if found["bottom"] else number
    if found["unit"] not in UNITS:
        raise ValueError(f"size {value!r} has no place on a size ladder")
    return number * UNITS[found["unit"]]


def _size_of(record: Mapping[str, str], attr: str) -> str:
    """``record``'s value of ``attr``, in either case: a bundle with no authored-name map rebuilds
    its records under the published sentence-case names."""
    return {name.casefold(): value for name, value in record.items()}[attr.casefold()]


def ratios(product_type: str, records: Sequence[Mapping[str, str]]) -> list[float]:
    """The share of the type's scale each record is drawn at: 1 unless a breadth product's sizes
    form a ladder."""
    from synthetic_ecommerce_data.domains.industrial import (
        breadth,  # noqa: PLC0415 -- it registers this
    )

    unscaled = [1.0] * len(records)
    row = next((r for r in breadth.rows() if r.key == product_type), None)
    if row is None or row.size_attr in NOT_SIZES or len(records) < 2:  # noqa: PLR2004
        return unscaled
    sizes = [measure(_size_of(record, row.size_attr)) for record in records]
    ladder = sorted(set(sizes))
    if len(ladder) < 2:  # noqa: PLR2004
        return unscaled
    return [ratio_at(ladder.index(size), len(ladder)) for size in sizes]
