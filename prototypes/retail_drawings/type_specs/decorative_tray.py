"""Decorative and trinket trays (gen#217, a spec by gen#351): Home > Home Accessories > Decorative
Trays.

Four styles from four brands, drawn by :func:`kit_decor.trinket_tray`: the outline (round or
rectangular) changes the drawing. The material and the tray shape are structured entries; a style
is a color times a size. Every name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

import kit_decor  # noqa: F401 -- registers the shapes
from decor_rows import (
    BLACK,
    BLUE,
    BRACKENMERE,
    BROWN,
    CALDERBY,
    EMBERLY,
    GOLD,
    GREEN,
    LANTERNBY,
    RED,
    SILVER,
    TRAYS,
    WHITE,
    YELLOW,
    axis,
    row,
)
from type_registry import TypeSpec, a

ROWS = (
    row("TRYMBL", "Marble Effect Trinket Tray", CALDERBY, TRAYS, "Decorative Tray", 14.0, "trinket_tray",
         "A round trinket tray with a marble effect finish, for rings, keys and small things.",
         (WHITE, BLACK, GREEN),
         (a("material", "Material", "Marble Effect"), a("tray_shape", "Tray shape", "Round")),
         axis((15, 14.0), (20, 18.0)), "diameter_cm", (("outline", "round"),)),
    row("TRYWDR", "Wooden Rectangular Decorative Tray", LANTERNBY, TRAYS, "Decorative Tray", 22.0, "trinket_tray",
         "A rectangular tray made of acacia wood with two cut-out handles, for the coffee table.",
         (BROWN, BLACK, WHITE),
         (a("material", "Material", "Wood"), a("tray_shape", "Tray shape", "Rectangular")),
         axis((30, 22.0), (40, 28.0), (50, 36.0)), "length_cm", (("outline", "rectangular"),)),
    row("TRYMTL", "Gold Metal Trinket Tray", EMBERLY, TRAYS, "Decorative Tray", 16.0, "trinket_tray",
         "A round metal trinket tray with a raised rim and a gold finish.",
         (GOLD, RED, BLUE, YELLOW),
         (a("material", "Material", "Metal"), a("tray_shape", "Tray shape", "Round")),
         axis((15, 16.0), (20, 21.0)), "diameter_cm", (("outline", "round"),)),
    row("TRYMRT", "Mirrored Rectangular Decorative Tray", BRACKENMERE, TRAYS, "Decorative Tray", 26.0, "trinket_tray",
         "A rectangular tray with a mirrored base and a metal rim, for perfume and candles.",
         (SILVER, BLACK, GREEN),
         (a("material", "Material", "Metal"), a("tray_shape", "Tray shape", "Rectangular")),
         axis((25, 26.0), (35, 34.0)), "length_cm", (("outline", "rectangular"),)),
)


SPEC = TypeSpec(
    key="decorative_tray",
    department="Home",
    product_type="Decorative Tray",
    rows=ROWS,
)

