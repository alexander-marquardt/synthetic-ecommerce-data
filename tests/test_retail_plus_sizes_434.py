"""Womens clothing carries UK sizes above 16 (gen#434, gap 1).

The UK ladder stopped at 16 (some styles at 18 or 20), so "dress size 22" read the size,
filtered the dresses and found none that carried it. A share of the Womens dresses, tops,
trousers, jeans and knitwear now runs on to UK 24, in the chart's own EU and US sizes
(:mod:`plus_sizes`).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import plus_sizes  # noqa: E402
import scale  # noqa: E402


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


def _womens(recs: list[dict], leaf: str) -> list[dict]:
    return [r for r in recs if r["category_path"][:2] == ["Womens", leaf]]


def _carrying(recs: list[dict], uk: str) -> list[dict]:
    return [r for r in recs if any(uk in (s.get("size_uk"), s.get("size")) for s in r["skus"])]


def test_at_least_thirty_womens_dresses_carry_uk_22(ceiling: list[dict]) -> None:
    assert len(_carrying(_womens(ceiling, "Dresses"), "22")) >= 30


@pytest.mark.parametrize("leaf", ["Dresses", "Tops"])
@pytest.mark.parametrize("uk", ["18", "20", "22", "24"])
def test_each_leaf_carries_each_larger_size(ceiling: list[dict], leaf: str, uk: str) -> None:
    assert _carrying(_womens(ceiling, leaf), uk), f"no Womens/{leaf} style carries UK {uk}"


def test_a_larger_size_is_a_row_of_the_womens_chart(ceiling: list[dict]) -> None:
    for r in _womens(ceiling, "Dresses"):
        for s in r["skus"]:
            if "size_uk" in s:
                uk = int(s["size_uk"])
                assert (s["size_eu"], s["size_us"]) == (str(uk + 28), str(uk - 4)), r["product_id"]


def test_the_options_and_the_sku_count_follow_the_larger_skus(ceiling: list[dict]) -> None:
    for r in _carrying(_womens(ceiling, "Dresses"), "22"):
        ids = [s["sku"] for s in r["skus"]]
        assert len(set(ids)) == len(ids) == r["sku_count"], r["product_id"]
        seen: list[str] = []
        for s in r["skus"]:
            if s["size"] not in seen:
                seen.append(s["size"])
        assert r["size_options"]["size"] == seen, r["product_id"]


def test_extend_appends_the_chart_rows_per_color_and_leaves_ids_alone() -> None:
    skus = [{"sku": f"X-1-00{n}", "color": c, "size_uk": uk, "size_eu": str(int(uk) + 28),
             "size_us": str(int(uk) - 4), "price": 20.0, "in_stock": True}
            for n, (c, uk) in enumerate([("Red", "14"), ("Red", "16"), ("Blue", "14"),
                                          ("Blue", "16")], 1)]
    rec = {"product_id": "X-1", "category_path": ["Womens", "Dresses"], "sku_count": 4,
           "skus": skus, "size_options": {"size_uk": ["14", "16"]}}
    out = plus_sizes.extend(rec)
    assert [s["sku"] for s in out["skus"][:4]] == [s["sku"] for s in skus]
    assert [(s["color"], s["size_uk"]) for s in out["skus"][4:]] == [
        (c, uk) for c in ("Red", "Blue") for uk in ("18", "20", "22", "24")]
    assert out["sku_count"] == 12
    assert out["size_options"]["size_uk"] == ["14", "16", "18", "20", "22", "24"]


def test_a_mens_style_is_not_chosen() -> None:
    assert not plus_sizes.chosen({"product_id": "X-1", "category_path": ["Mens", "Dresses"]})


def test_extend_carries_a_bare_number_size_as_the_size_alone() -> None:
    skus = [{"sku": f"X-2-00{n}", "color": "Red", "size": uk, "price": 20.0, "in_stock": True}
            for n, uk in enumerate(["16", "18"], 1)]
    rec = {"product_id": "X-2", "category_path": ["Womens", "Tops"], "sku_count": 2, "skus": skus,
           "size_options": {"size": ["16", "18"]}}
    out = plus_sizes.extend(rec)
    assert [s["size"] for s in out["skus"]] == ["16", "18", "20", "22", "24"]
    assert all(set(s) == {"sku", "color", "size", "price", "in_stock"} for s in out["skus"])
    assert out["size_options"] == {"size": ["16", "18", "20", "22", "24"]}
