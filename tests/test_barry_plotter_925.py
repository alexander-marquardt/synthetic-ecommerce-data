"""Barry Plotter, an invented franchise range named only in the product text (gen#925).

The invented films sell about 30 SKUs each from one brand at one price per type, so a film phrase
with a filter leaves one product or none. These tests pin, on the ceiling build, that the range is
large enough to filter: 500 or more SKUs in its six groups from 8 or more brands, about 60% under
£30 and a quarter on sale, and dozens of hits for the filters a demo puts on it. They pin that the
name is in no structured field, that only the range's products name it, and that the doc page
states the counts the build makes.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import barry_plotter

DOC = Path(__file__).resolve().parents[1] / "docs" / "retail-prototype" / "barry-plotter-925.md"
NAME = re.compile(r"\bbarry plotter\b", re.IGNORECASE)
#: The share of the range's SKUs under £30 and of its products on sale the issue asks for, and
#: how far the build may stand from each.
UNDER_30, ON_SALE, NEAR = 0.60, 0.25, 0.05


@pytest.fixture(scope="module")
def catalog() -> list[dict]:
    return ceiling_build().records


@pytest.fixture(scope="module")
def products(catalog) -> list[dict]:
    return [d for d in catalog if d["product_id"] in barry_plotter.ids()]


@pytest.fixture(scope="module")
def skus(products) -> list[tuple[dict, dict]]:
    return [(d, s) for d in products for s in d["skus"]]


def _group(doc: dict) -> str:
    return barry_plotter.group_of(_ROWS[doc["product_id"]])


_ROWS = {r.product_id: r for r in barry_plotter.ROWS}


def test_the_ceiling_build_holds_every_row_and_500_skus_in_six_groups(products, skus) -> None:
    assert {d["product_id"] for d in products} == barry_plotter.ids()
    assert len(skus) >= 500, len(skus)
    assert {_group(d) for d in products} == set(barry_plotter.GROUPS)


def test_the_range_is_made_by_8_brands_or_more(products) -> None:
    brands = {d["brand"] for d in products}
    assert len(brands) >= 8, sorted(brands)


#: Each filter a demo puts on the range, and the fewest SKUs it must still return.
FILTERS = {
    "under £30": (lambda d, s: s["price"] < 30, 150),
    "on sale": (lambda d, s: d.get("was_price", 0) > s["price"], 80),
    "hoodie": (lambda d, s: d["product_type"] == "Hoodie", 15),
    "kids' pyjamas in 7-8 Yrs": (
        lambda d, s: d["product_type"] == "Pyjamas" and s.get("size") == "7-8 Yrs",
        10,
    ),
    "building set under £50": (
        lambda d, s: d["product_type"] == "Building Set" and s["price"] < 50,
        15,
    ),
}


@pytest.mark.parametrize("name", FILTERS)
def test_a_filter_on_the_range_still_returns_dozens(skus, name) -> None:
    keep, fewest = FILTERS[name]
    assert sum(keep(d, s) for d, s in skus) >= fewest, name


def test_hoodies_come_from_three_brands_or_more(products) -> None:
    brands = {d["brand"] for d in products if d["product_type"] == "Hoodie"}
    assert len(brands) >= 3, sorted(brands)


def test_the_shares_under_30_and_on_sale_are_near_the_targets(products, skus) -> None:
    assert products and skus
    under = sum(s["price"] < 30 for _, s in skus) / len(skus)
    sale = sum("was_price" in d for d in products) / len(products)
    assert abs(under - UNDER_30) <= NEAR, under
    assert abs(sale - ON_SALE) <= NEAR, sale
    assert any(s["price"] > 100 for _, s in skus)


def test_the_name_is_in_no_structured_field(catalog) -> None:
    named = {d["product_id"]: barry_plotter.structured_names(d) for d in catalog}
    assert {p: n for p, n in named.items() if n} == {}


def test_structured_names_finds_the_name_in_each_field() -> None:
    """The guard above can fail: the name in a brand, a series, the path, the leaf or an
    attribute is found."""
    plain = {"brand": "Little Fernby", "category_path": ["Kids", "Tops"], "category_leaf": "Tops"}
    assert barry_plotter.structured_names(plain) == []
    assert barry_plotter.structured_names({**plain, "brand": "Barry Plotter"}) == ["brand"]
    line = {**plain, "product_line": "Barry Plotter"}
    assert barry_plotter.structured_names(line) == ["product_line"]
    path = {**plain, "category_path": ["Kids", "Barry Plotter"]}
    assert barry_plotter.structured_names(path) == ["category_path[1]"]
    attr = {**plain, "attributes": [{"key": "theme", "value": "Barry Plotter"}]}
    assert barry_plotter.structured_names(attr) == ["attribute theme"]


def test_only_the_range_names_the_range(catalog) -> None:
    named = {d["product_id"] for d in catalog if NAME.search(f"{d['title']} {d['description']}")}
    assert named == barry_plotter.ids()


def test_every_description_says_it_is_from_the_films_and_a_few_titles_do_not(products) -> None:
    for d in products:
        assert barry_plotter.FROM in d["description"], d["product_id"]
    only = {d["product_id"] for d in products if not NAME.search(d["title"])}
    assert only == barry_plotter.DESCRIPTION_ONLY
    assert 3 <= len(only) <= len(products) // 10, sorted(only)


def test_the_shared_words_are_where_the_doc_says(catalog) -> None:
    """The shared words the doc lists: ``barry`` and ``plotter`` start no word of any other
    product's text; ``plot`` starts only Fenwold Nursery's "Plot" garden series, and
    ``berry`` (one letter from ``barry``) a few products."""
    others = [d for d in catalog if d["product_id"] not in barry_plotter.ids()]

    def holding(word: str) -> list[dict]:
        return [
            d
            for d in others
            if re.search(rf"\b{word}", f"{d['title']} {d['description']}", re.IGNORECASE)
        ]

    assert holding("barry") == [] and holding("plotter") == []
    assert {d["brand"] for d in holding("plot")} == {"Fenwold Nursery"}
    assert holding("berry\\b")


def test_the_doc_states_the_counts_the_build_makes(products, skus) -> None:
    text = DOC.read_text()
    for group in barry_plotter.GROUPS:
        n = sum(_group(d) == group for d in products)
        k = sum(_group(d) == group for d, _ in skus)
        row = next((line for line in text.splitlines() if line.startswith(f"| {group} |")), "")
        assert row.endswith(f"| {n} | {k} |"), (group, n, k, row)
    assert f"| **Total** | | | {len(products)} | {len(skus)} |" in text
    for motif in barry_plotter.MOTIFS:
        assert motif in text, motif
