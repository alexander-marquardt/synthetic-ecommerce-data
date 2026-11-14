"""The Electronics department's smart home rows (gen#956): smart plugs, bulbs, doorbell cameras.

The department is ``Electronics`` (``core/departments.RETAIL``), and these types sit under
``Electronics > Smart Home``. Each type is a spec of its own (``type_specs/smart_plug.py``,
``smart_bulb.py``, ``doorbell_camera.py``) drawn by :mod:`kit_smart_home`, and each is derivable:
the scaled build draws more styles from these rows by the values their titles show. Each type has
four title patterns, each authored twice by two brands, and few enough title-shown values that it
stays inside its share of the department (``tests/test_retail_electronics_smart_home_956.py``).
Every brand is an invented Electronics brand of :mod:`electronics_rows`.
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_smart_home,  # noqa: F401 -- registers smart_plug, smart_bulb, doorbell_camera
)
from synthetic_ecommerce_data.domains.retail.electronics_rows import DEPARTMENT
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

#: The top level of every path: the store's department.
ROOT = "Electronics"
PLUGS = (ROOT, "Smart Home", "Smart Plugs")
BULBS = (ROOT, "Smart Home", "Smart Bulbs")
DOORBELLS = (ROOT, "Smart Home", "Doorbell Cameras")

RED, BLUE, GREEN, YELLOW, BLACK, WHITE = (
    cw(name, hex_, "solid", "#2a2a2e" if name == "White" else "#ffffff")
    for name, hex_ in MAIN_COLORS.items()
)
#: The six main colors (gen#275), every one on every plug and doorbell template.
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        price: float, description: str, attrs: tuple[tuple, ...],
        params: tuple[tuple[str, str], ...], sizes: tuple[tuple[str, float], ...] = (),
        size_key: str = "size", colors: tuple = SIX) -> Row:  # fmt: skip
    """One smart home style: its colors (times its packs, when it has them) are its SKUs."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, price, shape, description,
               colors, attrs, sizes, params=params, size_key=size_key)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, color: tuple) -> Row:
    """A text-match decoy cut from ``base``: one color, and a title or description that names
    a color its structured fields do not hold (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description, colors=(color,))
