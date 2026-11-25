"""A chocolate bar, box, bag, hot chocolate or orange takes no pack factor (gen#1125).

A bar draws its weight and its multipack itself, so a 100g bar keeps half its product area; a
box, sharing bag, hot chocolate or chocolate orange draws by its weight.
"""

from __future__ import annotations

SELF_SIZED = (
    "chocolate_bar",
    "chocolate_box",
    "chocolate_bag",
    "hot_chocolate",
    "chocolate_orange",
)
