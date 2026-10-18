"""Shared pieces of the seven luggage and travel types (gen#209): colors, brands, row builder.

Luggage sits in **Womens > Accessories > Travel** beside the travel cases (gen#248: an accessory
is one product in one place, and its audience is the ``audience`` attribute, here Unisex). Every
type is its own spec under ``type_specs/`` and its own drawing in :mod:`kit_luggage`. A style is
an :class:`~accessory_rows.ARow`: its SKUs are the colors times the type's own axis, and
``extra`` states the other fields a size carries (a suitcase's size name and its weight), so a
size, a capacity and a weight are all structured entries on the variant. Every brand is invented.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_luggage  # noqa: F401 -- registers suitcase, cabin_case, holdall, ...
from accessory_rows import ARow, _a, _count, _num, _who
from audience import UNISEX
from breadth_rows import OWNERS
from variants import cw

PATH = ("Womens", "Accessories", "Travel")
DEPARTMENT = "Clothing"
EXEMPT = "luggage, not a garment: the type carries its own text-match decoys (gen#209)"

TARNWICK, FENMOOR, SKERRY, MARROWGATE, PELLBROOK, WRENFIELD = (
    "Tarnwick", "Fenmoor & Co", "Skerry Travel", "Marrowgate", "Pellbrook", "Wrenfield",
)  # fmt: skip
#: The brands this module states: the other three are in ``accessory_rows`` already.
OWNED = ((TARNWICK, "third_party"), (FENMOOR, "third_party"), (SKERRY, "own"))

OWNERS.update(dict(OWNED))

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
NAVY = cw("Navy", "#26365c")
GREY = cw("Grey", "#9a9ca0")
SILVER = cw("Silver", "#cfd5da", "solid", "#8f989f")
TEAL = cw("Teal", "#1c7c7d")
KHAKI = cw("Khaki", "#a8a070")
BURGUNDY = cw("Burgundy", "#6e2233")
PINK = cw("Pink", "#e8a5b5")
TAN = cw("Tan", "#b8864f")

a = _a
count = _count
num = _num


def litres(key: str, name: str, n: float) -> tuple[str, str, str, str]:
    """A capacity in litres on the style (a weekend bag has one size)."""
    return (key, name, f"{n:g}", "LTR")


def luggage_row(code, title, brand, price, desc, colors, ptype, leaf, shape, attrs, sizes=(), params=(), size_key="capacity_l", extra=()) -> ARow:  # fmt: skip
    """One luggage style: its colors times ``sizes``, with Unisex as its audience."""
    return ARow(code, title, brand, DEPARTMENT, (*PATH, leaf), ptype, price, shape, desc, colors, _who(attrs, UNISEX),
                sizes, params=params, size_key=size_key, extra=extra)  # fmt: skip


def sized(*rows: tuple[int, str, float, float]) -> tuple[tuple[tuple[str, float], ...], tuple]:
    """``(litres, size name, kg, price)`` rows as the SKU axis and the fields each litre carries."""
    sizes = num(*((lt, p) for lt, _, _, p in rows))
    extra = tuple((f"{lt:g}", (("luggage_size", n), ("weight_kg", f"{kg:g}"))) for lt, n, kg, _ in rows)
    return sizes, extra
