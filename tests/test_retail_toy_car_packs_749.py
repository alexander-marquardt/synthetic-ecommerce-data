"""Toy car packs (gen#749): a few plural car titles for "toy cars" to prefer.

No title in the catalogue said "cars", so the exact-spelling preference had nothing to show on
"toy cars" against "toy car". The range is a pack of 3 and a pack of 5 of two kinds of car, in the
title form the socks use ("Bamboo Socks, Pack of 5"). A pack is what a style is sold as, so each
count is its own product. It uses the one ``pack_size`` vocabulary (gen#246), the multibuy factors
of ``underwear_rows`` and the one pack drawing (``pack_copies``, gen#728), and the description says
the count (gen#449). Each color is a SKU (gen#271), so every car of a pack is that color.
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    image_release,
    scale,
    underwear_rows,
)
from synthetic_ecommerce_data.domains.retail.type_specs import toy_vehicle

TITLE = re.compile(r"^(?:Die-Cast Cars|Wooden Racing Cars), Pack of ([35])$")
WORD = {3: "three", 5: "five"}


@pytest.fixture(scope="module")
def vehicles() -> list[dict]:
    return [r for r in scale.templates() if r["product_type"] == "Toy Vehicle"]


@pytest.fixture(scope="module")
def packs(vehicles: list[dict]) -> list[dict]:
    return [r for r in vehicles if " Pack of " in r["title"]]


def _count(rec: dict) -> int:
    return int(rec["title"].rsplit(" ", 1)[1])


def _attr(rec: dict, key: str) -> str:
    return next((str(a["value"]) for a in rec["attributes"] if a["key"] == key), "")


def test_the_range_is_two_kinds_of_car_each_in_a_pack_of_3_and_5(packs: list[dict]) -> None:
    assert sorted(_count(r) for r in packs) == [3, 3, 5, 5]
    assert [r["title"] for r in packs if not TITLE.match(r["title"])] == []
    assert {tuple(r["category_path"]) for r in packs} == {("Toys", "Vehicles", "Toy Vehicles")}
    assert {r["audience"] for r in packs} == {"kids"}
    assert len({r["title"].rsplit(",", 1)[0] for r in packs}) == 2


def test_a_pack_title_says_cars_and_leaves_toy_to_the_category(packs: list[dict]) -> None:
    """With "toy" beside "cars" a pack would match "toy car" as a stemmed phrase, which no single
    title does, and lead the singular page the issue wants a single to lead."""
    assert packs
    for rec in packs:
        assert re.search(r"\bCars\b", rec["title"]), rec["title"]
        assert not re.search(r"\btoy\b", rec["title"], re.IGNORECASE), rec["title"]


def test_the_single_cars_keep_their_singular_titles(vehicles: list[dict]) -> None:
    single = [r["title"] for r in vehicles if re.search(r"\bCar\b", r["title"])]
    assert len(single) >= 3
    assert [t for t in single if "Pack of" in t] == []


def test_a_pack_states_its_count_in_the_one_pack_vocabulary(packs: list[dict]) -> None:
    assert packs
    for rec in packs:
        n = _count(rec)
        assert _attr(rec, "pack_size") == f"{n} pack", rec["title"]
        assert {s["pack_size"] for s in rec["skus"]} == {f"{n} pack"}, rec["title"]
        assert {s["units_per_pack"] for s in rec["skus"]} == {n}, rec["title"]


def test_a_pack_is_priced_by_the_underwear_multibuy_factor() -> None:
    assert toy_vehicle.SPEC.rows
    for row in toy_vehicle.SPEC.rows:
        n = int(row.title.rsplit(" ", 1)[1])
        ((_, factor),) = underwear_rows._packs(n)
        assert {s["price"] for s in row.skus()} == {round(row.price * factor, 2)}, row.title


def test_a_pack_costs_less_than_that_many_of_the_cheapest_single(
    vehicles: list[dict], packs: list[dict]
) -> None:
    """Against the cheapest single of the same material, so no single beats the pack."""
    singles: dict[str, float] = {}
    for rec in vehicles:
        if rec in packs:
            continue
        price = min(s["price"] for s in rec["skus"])
        singles[_attr(rec, "material")] = min(price, singles.get(_attr(rec, "material"), price))
    assert packs
    for rec in packs:
        for sku in rec["skus"]:
            assert sku["price"] < _count(rec) * singles[_attr(rec, "material")], rec["title"]


def test_a_pack_is_drawn_as_that_many_cars_and_a_single_as_one_car(
    vehicles: list[dict], packs: list[dict]
) -> None:
    assert packs
    for rec in packs:
        for sku in rec["skus"]:
            assert image_release.render(rec, sku).count(b'class="pack-copy"') == _count(rec)
    single = next(r for r in vehicles if r not in packs)
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


def test_the_packs_stay_out_of_the_derivation(packs: list[dict]) -> None:
    """A derived style would swap a value of a pack and keep its count, and would move the seeded
    draws of the styles the derivation has."""
    assert packs
    assert {r["product_id"] for r in packs} <= scale.left_out()
    derived_from = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert derived_from & {r["product_id"] for r in packs} == set()
    assert "BRD-CARPOL" in derived_from
