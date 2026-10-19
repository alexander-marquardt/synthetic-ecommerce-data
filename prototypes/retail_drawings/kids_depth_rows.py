"""Kids clothing depth (gen#310, the Kids slice): data only.

Stub: no rows yet.
"""

from __future__ import annotations

ROWS: tuple = ()


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset(f"BRD-{r.code}" for r in ROWS)
