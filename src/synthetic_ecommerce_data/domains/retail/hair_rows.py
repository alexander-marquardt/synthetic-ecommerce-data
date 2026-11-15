"""The hair styling tools' shared pieces (gen#957): their paths, colors, rows and decoys.

The Beauty department had shampoo and conditioner under ``Hair Care`` and no tool, so a search
for ``hair dryer``, ``straightener`` or ``paddle brush`` found nothing. Three types fix that,
each a spec of its own (``type_specs/hair_dryer.py``, ``hair_straightener.py``,
``hairbrush.py``) drawn by :mod:`kit_hair`. Every style is sold in the six main colors (gen#275);
a SKU is a color times the type's own option (a dryer's attachments, a straightener's plate width,
a brush's size). The brands are the department's invented brands; every name here is invented.
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_hair,  # noqa: F401 -- registers hair_dryer, hair_straightener, hairbrush
)
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

DEPARTMENT = "Beauty"
DRYERS = (DEPARTMENT, "Hair Care", "Hair Dryers")
STRAIGHTENERS = (DEPARTMENT, "Hair Care", "Hair Straighteners")
BRUSHES = (DEPARTMENT, "Hair Care", "Hairbrushes")

RED, BLUE, GREEN, YELLOW, BLACK, WHITE = (
    cw(name, hex_, "solid", "#2a2a2e" if name == "White" else "#ffffff")
    for name, hex_ in MAIN_COLORS.items()
)
#: The six main colors (gen#275), every one on every template.
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...],
        params: tuple[tuple[str, str], ...], size_key: str) -> Row:  # fmt: skip
    """One hair tool style: its six colors times its ``size_key`` options are its SKUs."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, sizes[0][1], shape,
               description, SIX, attrs, sizes, params=params, size_key=size_key)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, color: tuple) -> Row:
    """A text-match decoy cut from ``base``: one color, and a title or description that names
    a color its structured fields do not hold (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description, colors=(color,))
