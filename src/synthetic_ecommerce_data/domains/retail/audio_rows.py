"""The Electronics department's audio rows (gen#956): headphones, portable speakers, soundbars.

The department is ``Electronics`` (``core/departments.RETAIL``), and these types sit under
``Electronics > Audio``. Each type is a spec of its own (``type_specs/headphones.py``,
``portable_speaker.py``, ``soundbar.py``) drawn by :mod:`kit_audio`, and each is derivable: the
scaled build draws more styles from these rows by the values their titles show. A type yields at
most (title-shown value combinations x brands) styles per title pattern, so each type has four
title patterns, each authored twice by two brands. Every brand is an invented Electronics brand
of :mod:`electronics_rows` (owners ``ELECTRONICS_OWNERS``).
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_audio,  # noqa: F401 -- registers headphones, portable_speaker, soundbar
)
from synthetic_ecommerce_data.domains.retail.electronics_rows import DEPARTMENT
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

#: The top level of every path: the store's department.
ROOT = "Electronics"
HEADPHONES = (ROOT, "Audio", "Headphones")
SPEAKERS = (ROOT, "Audio", "Portable Speakers")
SOUNDBARS = (ROOT, "Audio", "Soundbars")

RED, BLUE, GREEN, YELLOW, BLACK, WHITE = (
    cw(name, hex_, "solid", "#2a2a2e" if name == "White" else "#ffffff")
    for name, hex_ in MAIN_COLORS.items()
)
#: The six main colors (gen#275), every one on every template.
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        price: float, description: str, attrs: tuple[tuple, ...],
        params: tuple[tuple[str, str], ...], sizes: tuple[tuple[str, float], ...] = (),
        size_key: str = "size", colors: tuple = SIX) -> Row:  # fmt: skip
    """One audio style: its colors (times its packs, when it has them) are its SKUs."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, price, shape, description,
               colors, attrs, sizes, params=params, size_key=size_key)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, color: tuple) -> Row:
    """A text-match decoy cut from ``base``: one color, and a title or description that names
    a color its structured fields do not hold (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description, colors=(color,))
