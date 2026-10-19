"""Footwear offers Orange: "orange trainers" finds products in Mens, Womens and Kids (gen#420).

The 8,564 shoe SKUs of the Iowa load carried the six main colors and others, but no Orange, so
a shopper's ``orange trainers`` or ``orange nike`` found nothing. Trainers and running shoes,
the Nike rows (gen#341) among them, offer Orange as a plain color word on at least three styles
in each audience, and the drawing colors the upper orange. Deleting the color fails this file.
"""

from __future__ import annotations

import colorsys
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402

#: The product types "trainers" names in a shopper's query: trainers and running shoes.
TRAINER_TYPES = ("Trainers", "Running Shoes")
AUDIENCES = ("Mens", "Womens", "Kids")


@pytest.fixture(scope="module")
def tpls() -> list[dict]:
    return scale.templates()


def _orange(tpls: list[dict]) -> list[dict]:
    """The trainer and running-shoe styles that offer the color word Orange."""
    return [
        d for d in tpls
        if d["product_type"] in TRAINER_TYPES
        and any(o["color"] == "Orange" for o in d["color_options"])
    ]  # fmt: skip


@pytest.mark.parametrize("audience", AUDIENCES)
def test_orange_trainers_finds_at_least_three_products_per_audience(tpls, audience):
    found = [d["product_id"] for d in _orange(tpls) if d["category_path"][0] == audience]
    assert len(found) >= 3, found


def test_orange_trainers_finds_at_least_nine_products(tpls):
    assert len(_orange(tpls)) >= 9


def test_the_nike_trainers_and_running_shoes_offer_orange(tpls):
    nike = [d for d in _orange(tpls) if d["brand"] == "Nike"]
    assert {d["product_type"] for d in nike} == set(TRAINER_TYPES), [d["title"] for d in nike]
    assert {d["category_path"][0] for d in nike} == set(AUDIENCES)


def test_orange_is_a_plain_solid_orange_color_the_drawing_can_fill(tpls):
    """The option is the plain word "Orange", family orange, and its hex is an orange hue."""
    seen = 0
    for d in _orange(tpls):
        for o in d["color_options"]:
            if o["color"] != "Orange":
                continue
            seen += 1
            assert o["family"] == "orange", (d["product_id"], o)
            assert o["pattern"] == "solid", (d["product_id"], o)
            r, g, b = (int(o["hex"][i : i + 2], 16) / 255 for i in (1, 3, 5))
            hue, sat, val = colorsys.rgb_to_hsv(r, g, b)
            assert 15 <= hue * 360 <= 35 and sat >= 0.7 and val >= 0.8, (d["product_id"], o["hex"])
    assert seen >= 9


def test_an_orange_sku_exists_in_stock_for_every_orange_style(tpls):
    styles = _orange(tpls)
    assert len(styles) >= 9
    for d in styles:
        skus = [s for s in d["skus"] if s["color"] == "Orange"]
        assert skus, d["product_id"]
        assert any(s["in_stock"] for s in skus), d["product_id"]
