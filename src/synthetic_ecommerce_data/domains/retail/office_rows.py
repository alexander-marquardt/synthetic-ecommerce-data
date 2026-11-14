"""The Office & school department's shared pieces (gen#969): its paths, colors, packs and rows.

The store's department is the top level of ``category_path`` (``Office & school``, on
``core/departments.RETAIL``); the build record's ``department`` is the closed list's
``Office & Stationery`` (:mod:`departments`), which keys the department's brand pools. Each type
is a spec of its own (``type_specs/pen.py``, ``pencil.py``, ``spiral_notebook.py``) drawn by
:mod:`kit_office`. A SKU is a color in a pack (``pack_size``), so a pack of ten is drawn as ten
pens (:mod:`pack_copies`). The brands are the invented stationery brands of the Gifts notebooks
and diaries; every name here is invented.
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_office,  # noqa: F401 -- registers pen, pencil, spiral_notebook
)
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

#: The build record's department, from the closed list of :mod:`departments`.
DEPARTMENT = "Office & Stationery"
#: The top level of every path: the store's department (``core/departments.RETAIL``).
ROOT = "Office & School"
PENS = (ROOT, "Pens & Pencils", "Pens")
PENCILS = (ROOT, "Pens & Pencils", "Pencils")
NOTEBOOKS = (ROOT, "Paper & Notebooks", "Spiral Notebooks")

CALDERBY = "Calderby & Lune"
LANTERNBY = "Lanternby"
THISTLE = "Thistle & Wren"

RED, BLUE, GREEN, YELLOW, BLACK, WHITE = (
    cw(name, hex_, "solid", "#2a2a2e" if name == "White" else "#ffffff")
    for name, hex_ in MAIN_COLORS.items()
)
#: The six main colors (gen#275), every one on every template.
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def packs(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A style's packs as its SKU sizes: ``Single`` or ``<n> pack``, each at its price."""
    return tuple(("Single" if n == 1 else f"{n} pack", p) for n, p in pairs)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...],
        params: tuple[tuple[str, str], ...], colors: tuple = SIX) -> Row:  # fmt: skip
    """One office style: its colors times its packs are its SKUs."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, sizes[0][1], shape, description,
               colors, attrs, sizes, params=params, size_key="pack_size")  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, color: tuple) -> Row:
    """A text-match decoy cut from ``base``: one color, and a title or description that names
    a color its structured fields do not hold (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description, colors=(color,))
