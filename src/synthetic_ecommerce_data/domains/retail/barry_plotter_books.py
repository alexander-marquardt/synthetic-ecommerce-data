"""The Barry Plotter book series (gen#1119, slice 2): data only."""

from __future__ import annotations

PUBLISHER = ""
AUTHOR = ""
BOX_MOTIF = ""
ROWS: tuple = ()


def ids() -> frozenset[str]:
    """Every product id of the series."""
    return frozenset(r.product_id for r in ROWS)
