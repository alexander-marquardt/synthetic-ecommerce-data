"""The one rank rule of a size ladder, retail's and industrial's (gen#339, gen#719).

A size's scale is its rank in its product's own ladder, stepped evenly from :data:`BOTTOM` (the
smallest) to :data:`TOP` (the largest). The scale is symbolic, not true to dimension: the point is
that a demo shows a different picture per size. The largest rung keeps the drawing as it was, so
a smaller rung draws at ``scale / TOP`` of it (:func:`ratio_at`).
"""

from __future__ import annotations

#: The scale factors of the largest and the smallest rung; a smaller rung draws at
#: ``scale / TOP`` of the full-size drawing (a ratio, not a share of the sheet).
TOP = 0.90
BOTTOM = 0.55


def scale_at(rank: int, rungs: int) -> float:
    """The scale rung ``rank`` (0 = smallest) of ``rungs`` stands for, ``BOTTOM`` to ``TOP``."""
    return round(BOTTOM + (TOP - BOTTOM) * rank / (rungs - 1), 4)


def ratio_at(rank: int, rungs: int) -> float:
    """The share of the full-size drawing rung ``rank`` of ``rungs`` draws at (the largest: 1)."""
    return scale_at(rank, rungs) / TOP
