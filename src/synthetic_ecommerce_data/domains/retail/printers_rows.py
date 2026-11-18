"""The Electronics department's printer rows (gen#956, slice 3b): printers and ink cartridges.

The department is ``Electronics`` (``core/departments.RETAIL``). Both types sit under
``Electronics > Printers``. Each is a spec of its own (``type_specs/printer.py``,
``ink_cartridge.py``), drawn by :mod:`kit_printers`. Each is derivable: the scaled build draws
more styles from these rows by the values their titles show. Each type has four title patterns,
each authored twice by two brands. Its titles show few enough values that it stays inside its
share of the department (``tests/test_retail_electronics_printers_956.py``). Every brand is an
invented Electronics brand of :mod:`electronics_rows`.
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_printers,  # noqa: F401 -- registers printer, ink_cartridge
)
from synthetic_ecommerce_data.domains.retail.electronics_rows import DEPARTMENT
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

#: The top level of every path: the store's department.
ROOT = "Electronics"
PRINTERS = (ROOT, "Printers", "Printers")
INK_CARTRIDGES = (ROOT, "Printers", "Ink Cartridges")

RED, BLUE, GREEN, YELLOW, BLACK, WHITE = (
    cw(name, hex_, "solid", "#2a2a2e" if name == "White" else "#ffffff")
    for name, hex_ in MAIN_COLORS.items()
)
#: The six main colors (gen#275), every one on every template. A printer's color is its case;
#: an ink cartridge's is its ink.
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        price: float, description: str, attrs: tuple[tuple, ...],
        params: tuple[tuple[str, str], ...]) -> Row:  # fmt: skip
    """One printer or ink style: its six colors are its SKUs."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, price, shape, description,
               SIX, attrs, (), params=params)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, color: tuple) -> Row:
    """A text-match decoy cut from ``base``. It has one color, and its title or description names
    a color its structured fields do not hold (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description, colors=(color,))
