"""The Gifts department's party supplies (gen#966, slice 1): their path, colors, packs and rows.

Balloons, paper party plates and bunting each have a spec of their own (``type_specs/balloon.py``,
``party_plate.py``, ``party_bunting.py``) under ``Gifts > Party Supplies``. Balloons and bunting
are drawn by :mod:`kit_party`, plates by the tableware ``plate``. A balloon or plate SKU is a
color in a pack (``pack_size``), so a pack of ten is drawn as ten (:mod:`pack_copies`); a bunting
SKU is a color in a length in metres. The brands are the department's own invented ones.
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_party,  # noqa: F401 -- registers balloon, bunting
)
from synthetic_ecommerce_data.domains.retail.gifts_rows import (
    CALDERBY,
    DEPARTMENT,
    FERNBY,
    HEARTH,
    LANTERNBY,
    SIX_COLORS,
    THISTLE,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Row

__all__ = ["CALDERBY", "DEPARTMENT", "FERNBY", "HEARTH", "LANTERNBY", "THISTLE"]

ROOT = DEPARTMENT
BALLOONS = (ROOT, "Party Supplies", "Balloons")
PLATES = (ROOT, "Party Supplies", "Party Tableware")
BUNTING = (ROOT, "Party Supplies", "Party Decorations")

RED, BLUE, GREEN, YELLOW, BLACK, WHITE = SIX_COLORS


def packs(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A style's packs as its SKU sizes: ``<n> pack``, each at its price."""
    return tuple((f"{n} pack", p) for n, p in pairs)


def lengths(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    """A style's lengths in metres as its SKU sizes: a longer string costs more."""
    return tuple((f"{m:g}", p) for m, p in pairs)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...],
        params: tuple[tuple[str, str], ...], size_key: str = "pack_size") -> Row:  # fmt: skip
    """One party style: its six main colors times its packs (or lengths) are its SKUs."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, sizes[0][1], shape, description,
               SIX_COLORS, attrs, sizes, params=params, size_key=size_key)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, color: tuple) -> Row:
    """A text-match decoy cut from ``base``: one color, and a title or description that names
    a word its structured fields do not hold (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description, colors=(color,))
