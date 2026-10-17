"""What the five Gifts type specs of gen#425 share: the six main colors, the brands and the path.

A mug, a greeting card, a notebook, a money box and a pamper hamper each have a spec module of
their own under ``type_specs/``. They all offer the same six main colors (gen#275), so no
``main_colors.EXCEPTIONS`` entry is needed, and they all sit in the Gifts department with the
brands the department already has (Lanternby, Calderby & Lune, Thistle & Wren, Little Fernby,
Hearth & Table, Pipwick Toys). Every name is invented.
"""

from __future__ import annotations

from variants import cw

DEPARTMENT = "Gifts"

#: The six main colors with the same hexes as the other six-color types (garden hose).
SIX_COLORS = (
    cw("Red", "#c8312e"),
    cw("Blue", "#3f6fb5"),
    cw("Green", "#4f8a3a"),
    cw("Yellow", "#f2c230"),
    cw("Black", "#2d2d33"),
    cw("White", "#f4f1ea", "solid", "#9a9ca0"),
)

LANTERNBY = "Lanternby"
CALDERBY = "Calderby & Lune"
THISTLE = "Thistle & Wren"
FERNBY = "Little Fernby"
HEARTH = "Hearth & Table"
PIPWICK = "Pipwick Toys"

#: The path of each type (the tree guard's rules; one path per leaf).
MUG_PATH = (DEPARTMENT, "Mugs & Drinkware")
CARD_PATH = (DEPARTMENT, "Cards", "Greeting Cards")
NOTEBOOK_PATH = (DEPARTMENT, "Stationery", "Notebooks")
MONEY_BOX_PATH = (DEPARTMENT, "Kids' Gifts", "Money Boxes")
HAMPER_PATH = (DEPARTMENT, "Gift Sets", "Pamper Hampers")
