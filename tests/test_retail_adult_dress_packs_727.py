"""Adult dress multipacks (gen#727): "2 red dresses for the price of one, or whatever".

The Kids packs (``tests/test_retail_kids_dress_packs_727.py``) gave "red dresses" plural titles, and
the maintainer then asked for adult packs too. The range is a pack of 2 and a pack of 3 of two
styles, in the title form the socks use. One style sells in Red among other colors and the other
only in Red, so its title can say so. A pack is what a style is sold as, so each count is its own
product. It uses the one ``pack_size`` vocabulary (gen#246), the multibuy factors of
``underwear_rows`` and the one pack drawing (``pack_copies``, gen#728), and the description says the
count (gen#449).
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    image_release,
    scale,
    underwear_rows,
    womens_depth_rows,
)

TITLE = re.compile(r"^Womens .+ Dresses, Pack of ([23])$")
WORD = {2: "two", 3: "three"}


@pytest.fixture(scope="module")
def dresses() -> list[dict]:
    return [
        r
        for r in scale.templates()
        if r["product_type"] == "Dress" and r["category_path"][0] == "Womens"
    ]


@pytest.fixture(scope="module")
def packs(dresses: list[dict]) -> list[dict]:
    return [r for r in dresses if " Pack of " in r["title"]]


def _count(rec: dict) -> int:
    return int(rec["title"].rsplit(" ", 1)[1])


def _attr(rec: dict, key: str) -> str:
    return next((str(a["value"]) for a in rec["attributes"] if a["key"] == key), "")


def _colors(rec: dict) -> set[str]:
    return {o["color"] for o in rec["color_options"]}


def test_the_range_is_two_womens_styles_each_in_a_pack_of_2_and_3(packs: list[dict]) -> None:
    assert sorted(_count(r) for r in packs) == [2, 2, 3, 3]
    assert [r["title"] for r in packs if not TITLE.match(r["title"])] == []
    assert {tuple(r["category_path"][:2]) for r in packs} == {("Womens", "Dresses")}
    assert {r["audience"] for r in packs} == {"adult"}
    assert len({r["title"].rsplit(",", 1)[0] for r in packs}) == 2


def test_every_pack_sells_in_red_so_red_dresses_finds_it(packs: list[dict]) -> None:
    assert packs
    for rec in packs:
        assert "Red" in _colors(rec), rec["title"]
        assert "Red" in {s["color"] for s in rec["skus"]}, rec["title"]


def test_a_title_says_red_only_where_the_pack_sells_only_in_red(packs: list[dict]) -> None:
    named = [r for r in packs if " Red " in r["title"]]
    assert len(named) == 2
    assert all(_colors(r) == {"Red"} for r in named)
    assert all(len(_colors(r)) > 1 for r in packs if r not in named)


def test_a_pack_states_its_count_in_the_one_pack_vocabulary(packs: list[dict]) -> None:
    assert packs
    for rec in packs:
        n = _count(rec)
        assert _attr(rec, "pack_size") == f"{n} pack", rec["title"]
        assert {s["pack_size"] for s in rec["skus"]} == {f"{n} pack"}, rec["title"]
        assert {s["units_per_pack"] for s in rec["skus"]} == {n}, rec["title"]


def test_a_pack_states_the_neckline_of_its_style(packs: list[dict]) -> None:
    assert packs
    for rec in packs:
        assert rec["neckline"] == ("v-neck" if "Midi" in rec["title"] else "crew"), rec["title"]


def test_a_pack_is_priced_by_the_underwear_multibuy_factor() -> None:
    rows = [r for r in womens_depth_rows.ROWS if " Pack of " in r.title]
    assert rows
    for row in rows:
        n = int(row.title.rsplit(" ", 1)[1])
        ((_, factor),) = underwear_rows._packs(n)
        prices = dict(row.sizes)
        for sku in row.skus():
            assert sku["price"] == round(prices[sku["size"]] * factor, 2), row.title


def test_a_pack_costs_less_than_that_many_single_dresses(
    dresses: list[dict], packs: list[dict]
) -> None:
    """Against the cheapest full-price single of the same size, so no single beats the pack."""
    assert packs
    singles: dict[str, float] = {}
    for rec in dresses:
        if rec in packs or rec.get("was_price"):
            continue
        for sku in rec["skus"]:
            if "size" in sku:
                singles[sku["size"]] = min(sku["price"], singles.get(sku["size"], sku["price"]))
    for rec in packs:
        for sku in rec["skus"]:
            assert sku["price"] < _count(rec) * singles[sku["size"]], (rec["title"], sku)


def test_a_pack_is_drawn_as_that_many_dresses(packs: list[dict]) -> None:
    assert packs
    for rec in packs:
        for sku in rec["skus"][:5]:
            assert image_release.render(rec, sku).count(b'class="pack-copy"') == _count(rec)


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


def test_no_single_dress_carries_a_pack_size(dresses: list[dict], packs: list[dict]) -> None:
    """A decoy cloned from a pack would carry its count under a single's title."""
    assert packs
    assert [r["title"] for r in dresses if _attr(r, "pack_size") and r not in packs] == []


def test_the_packs_stay_out_of_the_derivation(packs: list[dict]) -> None:
    """A derived style would swap a value of a pack and keep its count."""
    assert packs
    derived_from = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert derived_from & {r["product_id"] for r in packs} == set()
