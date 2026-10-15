"""School uniform shapes for the retail drawing kit (gen#205): stubs, drawn in the next commit."""

from __future__ import annotations

from kit import Fill, register


def _nothing(paint: str, fill: Fill, label: str | None, **_: str) -> list[str]:
    return []


SHAPES = {
    "school_trousers": _nothing, "school_skirt": _nothing, "school_pinafore": _nothing,
    "school_shirt": _nothing,
}  # fmt: skip
register(SHAPES)
