"""Biscuits are drawn as a wrapped sleeve (gen#608), not as the kit's upright cereal-style carton.

The BIS and ORB families draw the ``sleeve`` pack shape: a flow-wrapped packet lying on its
side, wider than tall, with crimped ends. The range name and the flavor-color band (the
brand band) stay, and so does the pack's product word.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import grocery  # noqa: E402
import kit  # noqa: E402
import sheet_extent  # noqa: E402

CODES = ("BIS", "ORB")
FILL = kit.Fill("solid", "#c48a3a", "#ffffff")


def render(shape: str = "sleeve", **marks: str) -> str:
    return kit.render(shape, FILL, "Biscuits", params=marks or None)


def family(code: str) -> grocery.Family:
    return next(f for f in grocery.FAMILIES if f.code == code)


def aspect(shape: str) -> float:
    """Width over height of the pack's own drawn elements (the sheet frame left out)."""
    parts = kit.SHAPES[shape](FILL.base, FILL, "Biscuits")
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{"".join(parts)}</svg>'
    left, top, right, bottom = sheet_extent.reach(svg)
    return (right - left) / (bottom - top)


@pytest.mark.parametrize("code", CODES)
def test_a_biscuit_family_no_longer_uses_the_box(code: str) -> None:
    assert family(code).shape == "sleeve"
    assert family(code).shape != "box"


def test_the_cereal_family_keeps_the_box() -> None:
    assert family("CER").shape == "box"
    assert aspect("box") < 1.0  # the carton is taller than wide


def test_the_sleeve_is_wider_than_tall_and_not_the_carton() -> None:
    assert "sleeve" in kit.SHAPES
    assert aspect("sleeve") > 1.3
    assert render() != render("box")


def test_the_sleeve_has_crimped_ends() -> None:
    svg = render()
    assert svg.count('class="crimp"') == 2
    paths = re.findall(r'<path d="([^"]+)"[^>]*class="crimp"', svg)
    left, right = ([float(x) for x in re.findall(r"[ML](-?[\d.]+),", d)] for d in paths)
    assert min(left) < 64  # the teeth reach past the body edge at x=72
    assert max(right) > 336  # and past the body edge at x=328


def test_the_pack_label_range_name_and_flavor_band_stay() -> None:
    svg = render(line="Fresh Hearth", chips="#c8312e,#8c3b2a")
    assert "Biscuits" in svg and "Fresh Hearth" in svg
    assert "#c8312e" in svg and "#8c3b2a" in svg


@pytest.mark.parametrize("code", CODES)
def test_the_built_style_draws_a_sleeve_with_the_label(code: str) -> None:
    prefix = f"GRC-{code}-"
    rec = next(r for r in grocery.build(grocery.TARGET) if r["product_id"].startswith(prefix))
    assert rec["drawing"]["shape"] == "sleeve"
    # the pack's product word, drawn on the label panel
    word = {"BIS": "Biscuits", "ORB": "Shortbread"}[code]
    assert rec["drawing"]["label"] == word
    assert export.image_id(rec, rec["skus"][0])
