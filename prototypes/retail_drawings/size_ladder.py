"""Size-scaled drawings: one image per rung of a product's size ladder (gen#339).

STUB: the bounds are fixed here and nothing is scaled yet.
"""

from __future__ import annotations

#: The fraction of the sheet the largest and the smallest rung fill.
TOP = 0.90
BOTTOM = 0.55


def size_scale(rec: dict, sku: dict) -> float | None:
    """The fraction of the sheet the SKU's drawing fills, or ``None`` when it is not scaled."""
    return None


def stand(body: str, defs: str, size_scale: float | None) -> str:
    """``body`` scaled to ``size_scale`` about its own bottom centre."""
    return body
