"""Drawings for the Sports & Outdoors types (gen#265): the stub the tests are written against.

Every shape is registered and draws nothing yet; the drawings come in the next commit.
"""

from __future__ import annotations

from kit import Fill, register


def _blank(paint: str, fill: Fill, label: str | None, **_: str) -> list[str]:
    return []


SHAPES = {
    name: _blank
    for name in (
        "tent",
        "sleeping_bag",
        "camp_chair",
        "yoga_mat",
        "dumbbell",
        "kettlebell",
        "foam_roller",
    )
}
BUMP_COLUMNS = 0
BUMP_ROWS = 0
register(SHAPES)
