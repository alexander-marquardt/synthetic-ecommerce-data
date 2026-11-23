"""A beer takes no pack factor: it draws its own can, bottle or multipack (``kit_beer``, gen#1127).

A can fills the product area's full height, a bottle is drawn at its real proportions against its
line's largest, and a 4-pack draws its own count.
"""

from __future__ import annotations

SELF_SIZED = ("beer",)
