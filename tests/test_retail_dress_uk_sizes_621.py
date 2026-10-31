"""Womens dresses come in UK numeric sizes 6 to 20 as well as letter sizes (gen#621).

"size 20 dress" must find size-20 dresses by ``facets.size_uk: 20``. The dresses sized by number
stored a bare ``size``, so no dress carried ``size_uk``; a share now stores the three size
systems the way the jeans do, each size a variant.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from retail_ceiling import ceiling_build

ROOT = Path(__file__).resolve().parents[1]



@pytest.fixture(scope="module")
def dresses() -> list[dict]:
    recs = ceiling_build().records
    return [r for r in recs if r["category_path"][:2] == ["Womens", "Dresses"]]


def _uk_dresses(dresses: list[dict]) -> list[dict]:
    return [r for r in dresses if any("size_uk" in s for s in r["skus"])]


def test_at_least_one_dress_style_offers_uk_numeric_sizes(dresses: list[dict]) -> None:
    assert len(_uk_dresses(dresses)) >= 10


def test_the_uk_20_variant_carries_us_16_and_eu_48(dresses: list[dict]) -> None:
    twenty = [s for r in _uk_dresses(dresses) for s in r["skus"] if s.get("size_uk") == "20"]
    assert twenty, "no dress SKU carries size_uk 20"
    assert {(s["size_eu"], s["size_us"]) for s in twenty} == {("48", "16")}


def test_a_uk_dress_runs_from_6_to_20_one_variant_per_size_and_color(dresses: list[dict]) -> None:
    runs = _uk_dresses(dresses)
    assert runs, "no dress offers UK numeric sizes"
    for r in runs:
        run = [str(n) for n in range(6, 21, 2)]
        assert r["size_options"]["size_uk"][:8] == run, r["product_id"]
        assert "size" not in r["size_options"], r["product_id"]
        pairs = [(s["color"], s["size_uk"]) for s in r["skus"]]
        assert len(set(pairs)) == len(pairs) == r["sku_count"], r["product_id"]
        assert all({"size_eu", "size_us"} <= set(s) and "size" not in s for s in r["skus"])
