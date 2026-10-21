"""The real beach towels (gen#624): stub."""

from __future__ import annotations

from breadth_rows import Row

ROWS: tuple[Row, ...] = ()


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]
