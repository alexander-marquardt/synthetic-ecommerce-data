"""Garden hose templates for the scaled retail catalog (gen#292): data only.

Stub: no rows yet.
"""

from __future__ import annotations

import kit_garden  # noqa: F401 -- registers garden_hose
from breadth_rows import Row

ROWS: tuple[Row, ...] = ()


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]
