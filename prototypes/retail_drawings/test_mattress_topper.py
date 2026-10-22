"""A mattress topper is a thin layer on a mattress, not a mattress (#581).

Run: ``uv run pytest prototypes/retail_drawings/test_mattress_topper.py``.

The maintainer asked whether the toppers "look like a mattress" or "should be thinner".
A real double topper is about 27:1 (135 cm wide, 5 cm deep) and a mattress is about 5x
deeper than a topper, so the drawing keeps one scale for both: its thickness follows the
stated ``depth``, and a faint mattress outline lies under it.

The drawing marks its parts with ``data-part`` (``topper-left``, ``mattress-left``: the
left side face of each slab, whose four corners are top-left, top-front, bottom-front,
bottom-left), so a test measures the drawing and not the code that drew it.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_preview4  # noqa: E402,F401 -- registers every shape the build draws
from kit import SIZE, Fill, render  # noqa: E402

SVG = "{http://www.w3.org/2000/svg}"
#: A mattress is drawn at this depth beside the topper (the stated depth of ``mattress()``).
MATTRESS_CM = 25


def _svg(depth: str | None, shape: str = "mattress_topper") -> ET.Element:
    params = None if depth is None else {"depth": depth}
    return ET.fromstring(render(shape, Fill("solid", "#f4f2ec"), params=params))


def _part(root: ET.Element, part: str) -> ET.Element:
    found = [e for e in root.iter() if e.get("data-part") == part]
    assert len(found) == 1, f"{part!r}: expected one drawn element, found {len(found)}"
    return found[0]


def _corners(path: ET.Element) -> list[tuple[float, float]]:
    nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", path.get("d") or "")]
    return list(zip(nums[0::2], nums[1::2], strict=True))


def _thickness(root: ET.Element, part: str) -> float:
    """A slab's drawn thickness: the left edge of its left face, top-left to bottom-left."""
    corners = _corners(_part(root, f"{part}-left"))
    assert len(corners) == 4, f"{part}-left is not a four-corner face: {corners}"
    return corners[3][1] - corners[0][1]


@pytest.mark.parametrize("depth", ["3cm", "5cm", "5 cm", "7cm", "10cm"])
def test_the_topper_depth_is_drawn_at_the_mattress_scale(depth: str) -> None:
    root = _svg(depth)
    cm = float(re.match(r"\d+(?:\.\d+)?", depth).group())  # type: ignore[union-attr]
    topper, mattress = _thickness(root, "topper"), _thickness(root, "mattress")
    assert topper / mattress == pytest.approx(cm / MATTRESS_CM, rel=0.02)


def test_a_5_cm_and_a_10_cm_topper_differ_visibly() -> None:
    five, ten = _thickness(_svg("5cm"), "topper"), _thickness(_svg("10cm"), "topper")
    assert ten == pytest.approx(2 * five, rel=0.02)
    assert ten - five >= 8, "the two drawings differ by under 8 px"


def test_a_topper_is_thin_not_a_mattress() -> None:
    """The old drawing was 38 px for 5 cm, about 8:1 against its 300 px width."""
    root = _svg("5cm")
    assert _thickness(root, "topper") <= 20


def test_a_topper_without_a_depth_is_drawn_as_5_cm() -> None:
    assert _thickness(_svg(None), "topper") == pytest.approx(_thickness(_svg("5cm"), "topper"))


def test_the_topper_lies_on_a_faint_mattress() -> None:
    root = _svg("5cm")
    mattress = _part(root, "mattress")
    assert float(mattress.get("opacity", "1")) <= 0.5, "the mattress outline is not faint"
    # The topper's bottom-front corner is the mattress's top-front corner: it lies on it.
    top_front = _corners(_part(root, "mattress-left"))[1]
    bottom_front = _corners(_part(root, "topper-left"))[2]
    assert bottom_front == pytest.approx(top_front, abs=0.1)


def test_the_mattress_is_drawn_under_the_topper() -> None:
    order = [e.get("data-part") for e in _svg("5cm").iter() if e.get("data-part")]
    assert "mattress" in order and "topper" in order, order
    assert order.index("mattress") < order.index("topper")


@pytest.mark.parametrize("depth", ["3cm", "10cm"])
def test_the_canvas_is_unchanged_and_the_drawing_fits_it(depth: str) -> None:
    root = _svg(depth)
    assert (root.get("width"), root.get("height"), root.get("viewBox")) == (
        str(SIZE), str(SIZE), f"0 0 {SIZE} {SIZE}",
    )  # fmt: skip
    assert SIZE == 400
    for path in root.iter(f"{SVG}path"):
        for x, y in _corners(path):
            assert 0 <= x <= SIZE and 0 <= y <= SIZE, f"{path.get('d')[:40]} leaves the canvas"


def test_the_depth_is_still_dimensioned() -> None:
    texts = ["".join(t.itertext()) for t in _svg("10cm").iter(f"{SVG}text")]
    assert "10cm" in texts


def test_the_protector_is_left_as_it_was() -> None:
    """Its deep mattress with a fitted cover is right for a protector (issue note)."""
    root = _svg(None, "mattress_protector")
    assert not [e for e in root.iter() if e.get("data-part")]
