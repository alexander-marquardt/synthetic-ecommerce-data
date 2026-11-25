"""A loaf is drawn at no less than 0.9 of its line's largest (``kit_bread``, gen#1126).

A loaf is drawn to fill its picture, and its 400g at the cube root (0.79) covered under half the
product area: it is drawn at 0.9 of its 800g, still the smaller loaf, so every size holds the
fill floor.
"""

from __future__ import annotations

FLOORS = {"loaf": 0.9}
