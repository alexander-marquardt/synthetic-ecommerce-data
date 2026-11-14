"""The Electronics department's gadget rows (gen#956, slice 3a): power banks, webcams, smartwatches.

The department is ``Electronics`` (``core/departments.RETAIL``). Power banks sit under
``Electronics > Accessories``, webcams under ``Electronics > Computers`` and smartwatches under
``Electronics > Wearables``. Each type is a spec of its own (``type_specs/power_bank.py``,
``webcam.py``, ``smartwatch.py``), drawn by :mod:`kit_gadgets`. Each is derivable: the scaled
build draws more styles from these rows by the values their titles show. Each type has four title
patterns, each authored twice by two brands. Its titles show few enough values that it stays
inside its share of the department (``tests/test_retail_electronics_gadgets_956.py``). Every
brand is an invented Electronics brand of :mod:`electronics_rows`.
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_gadgets,  # noqa: F401 -- registers power_bank, webcam, smartwatch
)
from synthetic_ecommerce_data.domains.retail.electronics_rows import DEPARTMENT
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

#: The top level of every path: the store's department.
ROOT = "Electronics"
POWER_BANKS = (ROOT, "Accessories", "Power Banks")
WEBCAMS = (ROOT, "Computers", "Webcams")
SMARTWATCHES = (ROOT, "Wearables", "Smartwatches")

RED, BLUE, GREEN, YELLOW, BLACK, WHITE = (
    cw(name, hex_, "solid", "#2a2a2e" if name == "White" else "#ffffff")
    for name, hex_ in MAIN_COLORS.items()
)
#: The six main colors (gen#275), every one on every template.
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        price: float, description: str, attrs: tuple[tuple, ...],
        params: tuple[tuple[str, str], ...]) -> Row:  # fmt: skip
    """One gadget style: its six colors are its SKUs."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, price, shape, description,
               SIX, attrs, (), params=params)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, color: tuple) -> Row:
    """A text-match decoy cut from ``base``. It has one color, and its title or description names
    a color its structured fields do not hold (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description, colors=(color,))
