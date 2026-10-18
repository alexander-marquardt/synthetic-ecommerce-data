"""Clocks (gen#217, a spec by gen#351): Home > Home Accessories > Clocks.

Seven styles from five brands in three leaves (wall, mantel and alarm), drawn by
:func:`kit_decor.clock`: the clock type (wall, mantel or alarm) changes the drawing. The type, the
finish, the silent movement and the dial diameter are structured entries; a style is a color times
a diameter. Every name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

import kit_decor  # noqa: F401 -- registers the shapes
from decor_rows import (
    ALARM,
    BLACK,
    BLUE,
    BRACKENMERE,
    BROWN,
    CALDERBY,
    COBBLE,
    COPPER,
    EMBERLY,
    GOLD,
    GREEN,
    HARBOUR,
    LANTERNBY,
    MANTEL,
    NATURAL,
    RED,
    SILVER,
    WALL,
    WHITE,
    YELLOW,
    axis,
    row,
    yes,
)
from type_registry import TypeSpec, a

SILENT = yes("silent_movement", "Silent movement")
TICKING = a("silent_movement", "Silent movement", "No")

ROWS = (
    row("CLKWBR", "Brushed Brass Wall Clock", BRACKENMERE, WALL, "Clock", 24.0, "clock",
         "A round wall clock in a brushed brass frame with a sweep movement that does not tick.",
         (GOLD, BLACK, WHITE),
         (a("clock_type", "Clock type", "Wall"), a("finish", "Finish", "Brushed Brass"), SILENT),
         axis((30, 24.0), (40, 32.0), (50, 44.0)), "diameter_cm", (("type", "wall"),)),
    row("CLKWWN", "Walnut Wall Clock", LANTERNBY, WALL, "Clock", 29.0, "clock",
         "A wall clock in a walnut frame with a plain dial and a quiet quartz sweep movement.",
         (BROWN, RED, BLUE),
         (a("clock_type", "Clock type", "Wall"), a("finish", "Finish", "Walnut"), SILENT),
         axis((30, 29.0), (40, 38.0)), "diameter_cm", (("type", "wall"),)),
    row("CLKWPT", "Painted Metal Wall Clock", COBBLE, WALL, "Clock", 19.0, "clock",
         "A metal wall clock in a gloss painted frame, with a ticking quartz movement.",
         (RED, YELLOW, GREEN, BLUE),
         (a("clock_type", "Clock type", "Wall"), a("finish", "Finish", "Gloss Painted"), TICKING),
         axis((25, 19.0), (35, 25.0)), "diameter_cm", (("type", "wall"),)),
    row("CLKMOK", "Oak Mantel Clock", CALDERBY, MANTEL, "Clock", 39.0, "clock",
         "An arched mantel clock in a solid oak case on four small feet, with a silent sweep movement.",
         (NATURAL, BLACK, WHITE),
         (a("clock_type", "Clock type", "Mantel"), a("finish", "Finish", "Oak"), SILENT),
         axis((12, 39.0), (16, 49.0)), "diameter_cm", (("type", "mantel"),)),
    row("CLKMBZ", "Antique Bronze Mantel Clock", EMBERLY, MANTEL, "Clock", 45.0, "clock",
         "A mantel clock in an arched case with an antique bronze finish and a ticking movement.",
         (COPPER, GREEN, BLUE),
         (a("clock_type", "Clock type", "Mantel"), a("finish", "Finish", "Antique Bronze"), TICKING),
         axis((12, 45.0), (16, 55.0)), "diameter_cm", (("type", "mantel"),)),
    row("CLKABL", "Twin Bell Alarm Clock", HARBOUR, ALARM, "Clock", 12.0, "clock",
         "A twin bell alarm clock with a loud hammer alarm and a ticking movement, in a gloss painted case.",
         (RED, YELLOW, BLACK, WHITE),
         (a("clock_type", "Clock type", "Alarm"), a("finish", "Finish", "Gloss Painted"), TICKING),
         axis((10, 12.0), (12, 15.0)), "diameter_cm", (("type", "alarm"),)),
    row("CLKASL", "Silent Sweep Alarm Clock", LANTERNBY, ALARM, "Clock", 16.0, "clock",
         "A bedside alarm clock with a silent sweep movement and a gentle rising alarm tone, in a chrome case.",
         (SILVER, BLUE, GREEN),
         (a("clock_type", "Clock type", "Alarm"), a("finish", "Finish", "Chrome"), SILENT),
         axis((10, 16.0), (12, 19.0)), "diameter_cm", (("type", "alarm"),)),
)


SPEC = TypeSpec(
    key="clock",
    department="Home",
    product_type="Clock",
    rows=ROWS,
)
