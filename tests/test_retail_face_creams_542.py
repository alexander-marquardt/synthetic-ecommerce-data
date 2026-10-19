"""Face creams (gen#542): one brand held the type; five or more invented brands now sell it, each
in day, night and SPF lines of 30, 50 and 100 ml.

The checks hold what the issue asked for: five or more brands and twenty or more products, a price
per ml that falls with the volume in every line of the type, and brand names that are invented and
carry a house style of their own.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import house_styles  # noqa: E402
import real_brands  # noqa: E402
import scale  # noqa: E402

TYPE = "Face Cream"
#: The line names the issue lists, as words of a title: every new brand sells day, night and SPF.
LINES = {"day": "Day", "night": "Night", "spf": "SPF"}
SIZES = {30.0, 50.0, 100.0}
#: What a SKU states besides its volume: the keys that do not split a line into its own series.
NOT_A_SERIES_KEY = {"sku", "price", "in_stock", "net_volume_ml"}


@pytest.fixture(scope="module")
def creams() -> list[dict]:
    docs = [d for d in scale.templates(baseline=False) if d["product_type"] == TYPE]
    assert docs, "no Face Cream template in the build"
    return docs


def series(doc: dict) -> dict[tuple, list[tuple[float, float]]]:
    """A product's SKUs as (volume ml, price) per series: the SKUs that differ only by volume."""
    out: dict[tuple, list[tuple[float, float]]] = defaultdict(list)
    for sku in doc["skus"]:
        if "net_volume_ml" not in sku:  # a product sold in one size states none
            continue
        key = tuple(sorted((k, str(v)) for k, v in sku.items() if k not in NOT_A_SERIES_KEY))
        out[key].append((float(sku["net_volume_ml"]), float(sku["price"])))
    return out


def per_ml_falls(points: list[tuple[float, float]]) -> bool:
    """True when each bigger volume costs less per ml than the one below it."""
    ordered = sorted(points)
    rates = [price / ml for ml, price in ordered]
    return all(later < earlier for earlier, later in zip(rates, rates[1:], strict=False))


def test_the_type_has_five_or_more_brands_and_twenty_or_more_products(creams) -> None:
    assert len({d["brand"] for d in creams}) >= 5
    assert len(creams) >= 20


def test_price_per_ml_falls_as_volume_rises_in_every_line(creams) -> None:
    """Every series of every product of the type: a bigger pot is cheaper per ml."""
    multi = 0
    rises = []
    for doc in creams:
        for key, points in series(doc).items():
            if len(points) < 2:
                continue
            multi += 1
            if not per_ml_falls(points):
                rises.append((doc["product_id"], key, sorted(points)))
    assert rises == []
    assert multi >= 20, "the guard must see the multi-size lines, or it holds nothing"


def test_the_guard_reds_a_line_whose_price_per_ml_does_not_fall() -> None:
    assert per_ml_falls([(30.0, 9.0), (50.0, 13.0), (100.0, 20.0)])
    assert not per_ml_falls([(30.0, 9.0), (50.0, 15.0), (100.0, 30.0)])  # linear: same per ml
    assert not per_ml_falls([(30.0, 9.0), (50.0, 16.0), (100.0, 20.0)])  # 50 ml dearer per ml


def test_each_new_brand_sells_a_day_a_night_and_an_spf_line_in_30_50_and_100_ml(creams) -> None:
    by_brand: dict[str, list[dict]] = defaultdict(list)
    for d in creams:
        by_brand[d["brand"]].append(d)
    full = {
        b: docs
        for b, docs in by_brand.items()
        if all(any(word in d["title"] for d in docs) for word in LINES.values())
    }
    assert len(full) >= 5, sorted(full)
    for brand, docs in full.items():
        sized = {float(s["net_volume_ml"]) for d in docs for s in d["skus"] if "net_volume_ml" in s}
        assert sized >= SIZES, (brand, sorted(sized))


def test_a_brand_of_the_type_names_no_real_brand(creams) -> None:
    assert real_brands.check(creams) == []


def test_every_brand_of_the_type_has_a_house_style_and_a_mark_of_its_own(creams) -> None:
    brands = {d["brand"] for d in creams}
    assert sorted(brands - set(house_styles.HOUSE_STYLES)) == []
    marks = [house_styles.HOUSE_STYLES[b].mark for b in brands]
    assert len(set(marks)) == len(marks)
