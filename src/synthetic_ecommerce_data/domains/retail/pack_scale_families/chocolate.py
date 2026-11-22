"""A chocolate bar, box or sharing bag takes no pack factor (``kit_chocolate``, gen#1125).

A bar draws its weight and its multipack itself, so a 100g bar keeps half its product area; a
box or sharing bag draws by its weight.
"""

from __future__ import annotations

SELF_SIZED = ("chocolate_bar", "chocolate_box", "chocolate_bag")
