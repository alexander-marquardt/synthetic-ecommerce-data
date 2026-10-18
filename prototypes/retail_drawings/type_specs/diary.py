"""Diaries (gen#217, a spec by gen#351): Gifts > Stationery > Diaries.

Three styles from three brands, drawn by :func:`kit_decor.diary`: an elastic band (or none)
changes the drawing. The year, the page layout and the paper size are structured entries; a style
is a color. Every name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

import kit_decor  # noqa: F401 -- registers the shapes
from decor_rows import (
    BLACK,
    BLUE,
    BRACKENMERE,
    CALDERBY,
    DIARIES,
    GREEN,
    HARBOUR,
    RED,
    WHITE,
    YELLOW,
    row,
)
from type_registry import TypeSpec, a

ROWS = (
    row("DRYWTV", "Week to View Diary", CALDERBY, DIARIES, "Diary", 9.0, "diary",
         "A hardback diary with a week on every spread and a ribbon marker.",
         (RED, BLUE, GREEN, YELLOW, BLACK, WHITE),
         (a("diary_year", "Year", "2027"), a("page_layout", "Page layout", "Week to View"),
          a("paper_size", "Paper size", "A5")),
         params=(("band", "no"),)),
    row("DRYDPG", "Day a Page Diary with Elastic Band", HARBOUR, DIARIES, "Diary", 12.0, "diary",
         "A hardback diary with a full page for every day, an elastic band to keep it closed and a ribbon marker.",
         (BLACK, BLUE, RED),
         (a("diary_year", "Year", "2027"), a("page_layout", "Page layout", "Day a Page"),
          a("paper_size", "Paper size", "A5")),
         params=(("band", "yes"),)),
    row("DRYPKT", "Pocket Diary", BRACKENMERE, DIARIES, "Diary", 6.0, "diary",
         "A small diary with a week to view that fits in a coat pocket.",
         (GREEN, WHITE, YELLOW),
         (a("diary_year", "Year", "2027"), a("page_layout", "Page layout", "Week to View"),
          a("paper_size", "Paper size", "A6")),
         params=(("band", "no"),)),
)


SPEC = TypeSpec(
    key="diary",
    department="Gifts",
    product_type="Diary",
    rows=ROWS,
)
