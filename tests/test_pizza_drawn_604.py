"""A chilled pizza is drawn as a pizza (gen#604), not as the kit's upright cereal-style carton.

The PIZ family draws the ``pizza`` pack shape: a round pie on a card base under film, seen at a
slight angle. The flavour attribute picks the toppings and the size attribute ("10 inch",
"12 inch") the diameter, both as per-SKU drawing params. The range name and the flavour-color
band (the brand band) stay.
"""

from __future__ import annotations

import itertools
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

PIZ = next(f for f in grocery.FAMILIES if f.code == "PIZ")
FLAVOURS = [f.name for f in PIZ.flavors]
FILL = kit.Fill("solid", "#c8312e", "#ffffff")


def render(flavor: str, size: str, **marks: str) -> str:
    return kit.render("pizza", FILL, "Pizza", params={"flavor": flavor, "pack_size": size, **marks})


def layer(svg: str, name: str) -> str:
    """The SVG group of one named layer of the drawing."""
    found = re.search(rf'<g class="{name}">(.*?)</g>', svg, re.S)
    assert found, f"no {name} layer"
    return found.group(1)


def crust_rx(svg: str) -> float:
    found = re.search(r'<ellipse class="crust"[^>]*? rx="([\d.]+)"', svg)
    assert found, "no crust"
    return float(found.group(1))


def test_the_pizza_family_has_its_own_container() -> None:
    assert PIZ.shape == "pizza"
    assert "pizza" in kit.SHAPES


def test_the_pizza_is_round_on_a_card_under_film() -> None:
    svg = render("Margherita", "12 inch")
    assert "<ellipse" in svg and 'class="film"' in svg and 'class="card"' in svg
    left, top, right, bottom = sheet_extent.reach(svg)
    assert (right - left) > (bottom - top) * 0.9  # wider than tall, as a pie on a card is


@pytest.mark.parametrize(("a", "b"), list(itertools.combinations(FLAVOURS, 2)))
def test_two_flavours_render_different_topping_layers(a: str, b: str) -> None:
    assert layer(render(a, "12 inch"), "toppings") != layer(render(b, "12 inch"), "toppings")


def test_an_unknown_flavour_is_refused() -> None:
    with pytest.raises(ValueError, match="Mystery"):
        render("Mystery", "12 inch")


def test_a_12_inch_pizza_is_larger_than_a_10_inch_one() -> None:
    small = crust_rx(render("Margherita", "10 inch"))
    big = crust_rx(render("Margherita", "12 inch"))
    assert big > small
    assert big / small == pytest.approx(1.2, abs=0.02)


def test_the_brand_band_and_label_stay() -> None:
    svg = render("Margherita", "12 inch", line="Fresh Hearth", chips="#c8312e,#8c3b2a")
    assert "Pizza" in svg and "Fresh Hearth" in svg
    assert "#8c3b2a" in svg


def test_the_style_carries_flavour_and_size_as_drawing_params() -> None:
    rec = next(r for r in grocery.build(grocery.TARGET) if r["product_id"].startswith("GRC-PIZ-"))
    assert rec["drawing"]["shape"] == "pizza"
    assert set(rec["drawing"]["params"]) >= {"flavor", "pack_size"}
    images = {export.image_id(rec, s) for s in rec["skus"]}
    assert len(images) == len(rec["skus"])  # every flavour x size is its own picture
