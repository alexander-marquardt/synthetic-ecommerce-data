"""A milk jug, a milk carton and a yoghurt take no pack factor (``kit_dairy``, gen#1128).

Each pint or litre size of a jug or carton is drawn in its own proportions and fills half its
picture, where a factor drew a 1 pint at 0.63 and a fifth of its product area. A yoghurt draws
its 4 x 125g as 4 pots and its 500g as one tub, each filling half its picture.
"""

from __future__ import annotations

SELF_SIZED = ("milk_jug", "milk_carton", "yogurt")
