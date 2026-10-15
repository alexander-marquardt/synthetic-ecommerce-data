"""School uniform for Kids (gen#205): stubs, the rows follow in the next commit."""

from __future__ import annotations

import kit_school  # noqa: F401 -- registers school_trousers, school_skirt, ...

ROWS: tuple = ()


def docs() -> list[dict]:
    return [r.doc() for r in ROWS]
