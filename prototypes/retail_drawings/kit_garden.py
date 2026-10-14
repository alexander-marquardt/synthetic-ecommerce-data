"""Drawings of the garden products (gen#292).

Stub: the hose draws nothing yet.
"""

from __future__ import annotations

from kit import Fill, register


def garden_hose(paint: str, fill: Fill, label: str | None, style: str = "coiled") -> list[str]:
    """A garden hose."""
    return []


SHAPES = {"garden_hose": garden_hose}
register(SHAPES)
