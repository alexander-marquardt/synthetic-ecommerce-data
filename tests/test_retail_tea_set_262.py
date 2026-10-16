"""RPLTEA, the wooden tea set (gen#262): the jug rests where the pot rests.

The first drawing hung the jug at mid-height with nothing under it, a pointed foot and no
shelf, so it read as a jug in the air. The pot and the jug now stand on one shelf line.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DRAWINGS = REPO / "prototypes" / "retail_drawings"
sys.path.insert(0, str(DRAWINGS))

import kit  # noqa: E402
import toys_rows  # noqa: E402

PAIR = re.compile(r"(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)")


def _svg() -> str:
    row = next(r for r in toys_rows.ROWS if r.code == "RPLTEA")
    return kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))


def _pieces(svg: str) -> list[str]:
    return re.findall(r'<g class="piece">(.*?)</g>', svg)


def _extent(piece: str) -> tuple[float, float, float]:
    """The piece's left, right and lowest drawn point, from its path points and ellipses."""
    xs: list[float] = []
    ys: list[float] = []
    for d in re.findall(r'<path d="([^"]*)"', piece):
        for x, y in PAIR.findall(d):
            xs.append(float(x))
            ys.append(float(y))
    for cx, cy, rx, ry in re.findall(
        r'<ellipse cx="([\d.]+)" cy="([\d.]+)" rx="([\d.]+)" ry="([\d.]+)"', piece
    ):
        xs += [float(cx) - float(rx), float(cx) + float(rx)]
        ys.append(float(cy) + float(ry))
    return min(xs), max(xs), max(ys)


def _jug_and_pot() -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    pieces = _pieces(_svg())
    assert len(pieces) == 1 + 1 + 4 + 4, "a jug, a pot, four saucers and four cups"
    return _extent(pieces[0]), _extent(pieces[1])


def test_the_jug_and_the_pot_end_on_the_same_line() -> None:
    jug, pot = _jug_and_pot()
    assert jug[2] == pot[2]


def test_a_shelf_lies_under_the_jug_and_the_pot_at_that_line() -> None:
    jug, pot = _jug_and_pot()
    shelves = re.findall(r'<rect [^>]*class="shelf"[^>]*>', _svg())
    assert len(shelves) == 1, "one shelf for the pot and the jug"
    x, y, w = (
        float(re.search(rf' {k}="([\d.]+)"', shelves[0]).group(1)) for k in ("x", "y", "width")
    )
    assert y == pot[2], "the pieces stand on the shelf's top edge"
    assert x <= jug[0] and x + w >= pot[1], "the shelf runs from the jug to the pot"
