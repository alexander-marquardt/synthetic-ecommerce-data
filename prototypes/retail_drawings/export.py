"""The retail catalog in the output standard (stub: the build's own records)."""

from __future__ import annotations

from build_preview4 import samples


def documents() -> list[dict]:
    return [d for recs in samples().values() for d in recs]
