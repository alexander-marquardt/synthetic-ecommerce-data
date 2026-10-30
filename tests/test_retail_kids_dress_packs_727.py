"""Kids dress multipacks (gen#727): a few plural dress titles for "red dresses" to prefer.

No dress title in the catalogue was plural, so the exact-spelling preference had nothing to show
on "red dress" against "red dresses". The range is a pack of 2 and a pack of 3 of three girls'
styles, in the title form the socks use ("Bamboo Socks, Pack of 5"), and no Womens dress pack.
A pack is what a style is sold as, so each count is its own product. It uses the one ``pack_size``
vocabulary (gen#246), the multibuy factors of ``underwear_rows`` and the one pack drawing
(``pack_copies``, gen#728), and the description says the count (gen#449).
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    image_release,
    kids_depth_rows,
    scale,
    underwear_rows,
)

TITLE = re.compile(r"^Girls .+ Dresses, Pack of ([23])$")
WORD = {2: "two", 3: "three"}


@pytest.fixture(scope="module")
def dresses() -> list[dict]:
    return [r for r in scale.templates() if r["product_type"] == "Dress"]


@pytest.fixture(scope="module")
def packs(dresses: list[dict]) -> list[dict]:
    return [r for r in dresses if " Pack of " in r["title"]]


def _count(rec: dict) -> int:
    return int(rec["title"].rsplit(" ", 1)[1])


def _attr(rec: dict, key: str) -> str:
    return next((str(a["value"]) for a in rec["attributes"] if a["key"] == key), "")


def test_the_range_is_three_girls_styles_each_in_a_pack_of_2_and_3(packs: list[dict]) -> None:
    assert sorted(_count(r) for r in packs) == [2, 2, 2, 3, 3, 3]
    assert [r["title"] for r in packs if not TITLE.match(r["title"])] == []
    assert {tuple(r["category_path"]) for r in packs} == {("Kids", "Girls", "Dresses")}
    assert {r["audience"] for r in packs} == {"kids"}
    assert len({r["title"].rsplit(",", 1)[0] for r in packs}) == 3


def test_every_pack_sells_in_red_so_red_dresses_finds_it(packs: list[dict]) -> None:
    assert packs
    for rec in packs:
        assert "Red" in {o["color"] for o in rec["color_options"]}, rec["title"]
        assert "Red" in {s["color"] for s in rec["skus"]}, rec["title"]


def test_a_pack_states_its_count_in_the_one_pack_vocabulary(packs: list[dict]) -> None:
    assert packs
    for rec in packs:
        n = _count(rec)
        assert _attr(rec, "pack_size") == f"{n} pack", rec["title"]
        assert {s["pack_size"] for s in rec["skus"]} == {f"{n} pack"}, rec["title"]
        assert {s["units_per_pack"] for s in rec["skus"]} == {n}, rec["title"]


def test_a_pack_is_priced_by_the_underwear_multibuy_factor() -> None:
    rows = [r for r in kids_depth_rows.ROWS if " Pack of " in r.title]
    assert rows
    for row in rows:
        n = int(row.title.rsplit(" ", 1)[1])
        ((_, factor),) = underwear_rows._packs(n)
        prices = {size: price for size, price in row.sizes}
        for sku in row.skus():
            assert sku["price"] == round(prices[sku["size"]] * factor, 2), row.title


def test_a_pack_costs_less_than_that_many_single_dresses(
    dresses: list[dict], packs: list[dict]
) -> None:
    """Against the cheapest full-price single of the same age, so no single beats the pack."""
    singles: dict[str, float] = {}
    for rec in dresses:
        if rec in packs or rec["product_id"] not in kids_depth_rows.product_ids():
            continue
        if rec.get("was_price"):
            continue
        for sku in rec["skus"]:
            singles[sku["size"]] = min(sku["price"], singles.get(sku["size"], sku["price"]))
    assert packs and singles
    for rec in packs:
        for sku in rec["skus"]:
            assert sku["price"] < _count(rec) * singles[sku["size"]], (rec["title"], sku)


def test_a_pack_is_drawn_as_that_many_dresses_and_a_single_as_one_dress(
    dresses: list[dict], packs: list[dict]
) -> None:
    assert packs
    for rec in packs:
        for sku in rec["skus"][:7]:
            assert image_release.render(rec, sku).count(b'class="pack-copy"') == _count(rec)
    single = next(r for r in dresses if r not in packs)
    assert b'class="pack-copy"' not in image_release.render(single, single["skus"][0])


def test_a_pack_description_says_the_count_and_the_same_color(packs: list[dict]) -> None:
    assert packs
    for rec in packs:
        assert rec["description"].startswith(f"A pack of {WORD[_count(rec)]} "), rec["title"]
        assert ", all in the same color," in rec["description"], rec["title"]


def test_each_pack_sku_has_its_own_image_file(packs: list[dict]) -> None:
    assert packs
    for rec in packs:
        assert len({export.image_id(rec, s) for s in rec["skus"]}) == len(rec["skus"])
        assert len(image_release.image_files([rec])) == len(rec["skus"])


def test_no_womens_dress_is_sold_as_a_pack(dresses: list[dict], packs: list[dict]) -> None:
    assert packs
    packed = [r["title"] for r in dresses if _attr(r, "pack_size") and r not in packs]
    womens = [r["title"] for r in dresses if r["category_path"][0] == "Womens" and r in packs]
    assert packed == []
    assert womens == []
