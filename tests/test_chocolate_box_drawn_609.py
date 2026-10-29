"""A chocolate selection box is drawn as a flat selection box (gen#609), not as the kit's carton.

The CHX family draws the ``chocolate_box`` pack shape: a wide, shallow lidded box seen at a slight
angle, a ribbon across the lid. The pack scale (gen#543) still draws a 150g box smaller than a 400g
one on the same sheet, and the range name and the flavour-color band (the brand band) stay.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.retail import (
    grocery,
    image_release,
    kit,
    sheet_extent,
)

ROOT = Path(__file__).resolve().parents[1]


CHX = next(f for f in grocery.FAMILIES if f.code == "CHX")
FILL = kit.Fill("solid", "#8a5a3c", "#ffffff")


def records() -> list[dict]:
    return [r for r in grocery.build(grocery.TARGET) if r["product_id"].startswith("GRC-CHX-")]


def size(parts: list[str]) -> tuple[float, float]:
    """The width and height the pack's own elements cover (not the sheet's paper and frame)."""
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{"".join(parts)}</svg>'
    left, top, right, bottom = sheet_extent.reach(svg)
    return right - left, bottom - top


def drawn_scale(svg: str) -> float:
    """The factor the pack is drawn at on the sheet (1 when it is at its natural size)."""
    found = re.search(r'<g class="pack" transform="translate\([^)]*\) scale\(([\d.]+)\)"', svg)
    return float(found.group(1)) if found else 1.0


def test_the_chocolate_box_family_has_its_own_container() -> None:
    assert CHX.shape == "chocolate_box"
    assert CHX.shape != "box"
    assert "chocolate_box" in kit.SHAPES


def test_no_chocolate_selection_style_is_drawn_with_the_generic_box() -> None:
    recs = records()
    assert recs
    assert {r["drawing"]["shape"] for r in recs} == {"chocolate_box"}


def test_the_chocolate_box_is_wide_and_shallow() -> None:
    width, height = size(kit.SHAPES["chocolate_box"]("#8a5a3c", FILL, "Chocolates"))
    assert width >= 2 * height  # the carton it replaces is taller than wide


def test_the_lid_carries_a_ribbon() -> None:
    svg = kit.render("chocolate_box", FILL, "Chocolates")
    assert 'class="lid"' in svg and 'class="ribbon"' in svg


def test_a_400g_box_is_visibly_larger_than_a_150g_one() -> None:
    rec = next(r for r in records() if {"150g", "400g"} <= {s["pack_size"] for s in r["skus"]})
    by_size = {s["pack_size"]: s for s in rec["skus"]}
    small = drawn_scale(image_release.render(rec, by_size["150g"], styled=False).decode())
    big = drawn_scale(image_release.render(rec, by_size["400g"], styled=False).decode())
    width, height = size(kit.SHAPES["chocolate_box"]("#8a5a3c", FILL, "Chocolates"))
    assert big == 1.0  # the line's largest size is drawn at the shape's natural size
    assert small < 0.8 * big  # so a 150g box is drawn well under a 400g one
    assert width <= 400 and height <= 400  # on the one sheet, whatever the scale


@pytest.mark.parametrize("line", ["Ingleby Organic", "Fresh Hearth"])
def test_the_range_name_and_flavour_band_stay(line: str) -> None:
    marks = {"line": line, "chips": "#8a5a3c,#3b2416"}
    svg = kit.render("chocolate_box", FILL, "Chocolates", params=marks)
    assert "Chocolates" in svg and line in svg
    assert "#3b2416" in svg
