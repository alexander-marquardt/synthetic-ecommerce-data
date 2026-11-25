"""A wine bottle takes no pack factor: it draws its own size (``kit_drinks``, gen#1127).

It draws each size against its line's largest, at the bottle's real proportions and never below
0.8 of the largest's height. A factor drew a half bottle at 0.63 of the magnum, in a mostly empty
frame.
"""

from __future__ import annotations

SELF_SIZED = ("wine_bottle",)
