"""Wallpaper (gen#217, a spec by gen#351): Home > Decorating > Wallpaper.

Four styles from four brands, drawn by :func:`kit_decor.wallpaper`: the finish (matt or metallic)
changes the drawing, and a pattern is painted in the fill. The pattern, the finish and the roll
width are structured entries; a style is a color times a roll length. Every name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

import kit_decor  # noqa: F401 -- registers the shapes
from decor_rows import (
    BLACK,
    BLUE,
    BRACKENMERE,
    EMBERLY,
    GREEN,
    GREY,
    LARCHWOOD,
    RED,
    THISTLE,
    WALLPAPER,
    WHITE,
    YELLOW,
    axis,
    cm,
    row,
)
from type_registry import TypeSpec, a
from variants import cw

STRIPE = cw("Blue", "#f4f1ea", "stripe", "#3f6fb5")
SPOT = cw("Yellow", "#f4f1ea", "polka", "#f2c230")
CHECK = cw("Green", "#f4f1ea", "gingham", "#4f8a3a")

ROWS = (
    row("WLPPLN", "Plain Matt Wallpaper", LARCHWOOD, WALLPAPER, "Wallpaper", 16.0, "wallpaper",
         "A plain matt wallpaper that is easy to paste and hides a lightly uneven wall.",
         (WHITE, GREY, GREEN, BLACK, RED, BLUE, YELLOW),
         (a("pattern", "Pattern", "Plain"), a("finish", "Finish", "Matt"), cm("roll_width", "Roll width", 53)),
         axis((5, 16.0), (10, 28.0)), "roll_length_m", (("finish", "matt"),)),
    row("WLPSTR", "Striped Wallpaper", EMBERLY, WALLPAPER, "Wallpaper", 18.0, "wallpaper",
         "A wallpaper with a wide stripe running down the roll, matched across the join.",
         (STRIPE, cw("Red", "#f4f1ea", "stripe", "#c8312e")),
         (a("pattern", "Pattern", "Striped"), a("finish", "Finish", "Matt"), cm("roll_width", "Roll width", 53)),
         axis((10, 18.0), (15, 26.0)), "roll_length_m", (("finish", "matt"),)),
    row("WLPSPT", "Spotted Metallic Wallpaper", BRACKENMERE, WALLPAPER, "Wallpaper", 24.0, "wallpaper",
         "A spotted wallpaper with a metallic sheen that catches the light.",
         (SPOT, cw("Black", "#f4f1ea", "polka", "#2d2d33")),
         (a("pattern", "Pattern", "Spotted"), a("finish", "Finish", "Metallic"), cm("roll_width", "Roll width", 53)),
         axis((10, 24.0), (15, 34.0)), "roll_length_m", (("finish", "metallic"),)),
    row("WLPCHK", "Checked Wallpaper", THISTLE, WALLPAPER, "Wallpaper", 20.0, "wallpaper",
         "A checked wallpaper with a soft gingham weave look, for a kitchen or a hall.",
         (CHECK, cw("Blue", "#f4f1ea", "gingham", "#3f6fb5")),
         (a("pattern", "Pattern", "Checked"), a("finish", "Finish", "Matt"), cm("roll_width", "Roll width", 53)),
         axis((10, 20.0),), "roll_length_m", (("finish", "matt"),)),
)


SPEC = TypeSpec(
    key="wallpaper",
    department="Home",
    product_type="Wallpaper",
    rows=ROWS,
)

