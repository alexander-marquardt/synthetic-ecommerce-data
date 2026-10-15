"""Retail beauty depth (gen#214): stub, filled in the next commit."""

from __future__ import annotations

import kit_beauty  # noqa: F401 -- registers the beauty shapes

BRANDS: tuple = ()
ROWS: tuple = ()
DECOYS: tuple = ()


def docs() -> list[dict]:
    return [r.doc() for r in (*ROWS, *DECOYS)]
