"""Grocery holds the two real failure classes "beer" and "oranges" (gen#154, refs #154).

A query that names a category ("oranges", "beer") should boost that category. The
policy can only be shown with and without when the data holds both sides: products
whose CATEGORY PATH is the query's noun (blood oranges, easy peelers that never say
"orange", a lager that never says "beer") and products that only share the WORD
(a chocolate orange, a beer battered haddock, a ginger beer). These tests hold both
sides of both classes in the 10K build, in the nested and the flat output, and hold
the rule that a product has exactly one category path.
"""

from __future__ import annotations

import re
import sys
from functools import cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import grocery  # noqa: E402

ORANGES = ["Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Citrus Fruit", "Oranges"]
BEER = ["Food & Drink", "Beer, Wine & Spirits", "Beer"]
BEER_LEAVES = ("Lager", "Pale Ale", "Sour Beer", "Fruit Beer", "Alcohol Free")


@cache
def docs() -> tuple[dict, ...]:
    return tuple(grocery.documents(grocery.build(grocery.TARGET)))


@cache
def flat() -> tuple[dict, ...]:
    return tuple(grocery.flat(list(docs())))


def values(entries: list[dict], key: str) -> set[str]:
    return {e["value"] for e in entries if e["key"] == key}


def under(prefix: list[str]) -> list[dict]:
    return [d for d in docs() if d["category_path"][: len(prefix)] == prefix]


def titled(word: str, outside: list[str]) -> list[dict]:
    pat = re.compile(rf"\b{word}", re.I)
    return [
        d
        for d in docs()
        if pat.search(d["title"]) and d["category_path"][: len(outside)] != outside
    ]


# --------------------------------------------------------------------------
# Oranges: the category holds the fruit, the word is everywhere else.
# --------------------------------------------------------------------------


def test_the_oranges_leaf_holds_oranges_blood_oranges_segments_and_easy_peelers() -> None:
    leaf = under(ORANGES)
    assert all(d["category_path"] == ORANGES and d["category_leaf"] == "Oranges" for d in leaf)
    varieties = {v for d in leaf for x in d["variants"] for v in values(x["attributes"], "variety")}
    assert varieties == {"Oranges", "Blood Oranges", "Orange Segments", "Easy Peelers"}


def test_easy_peelers_are_a_type_match_with_no_orange_word_in_the_title() -> None:
    peelers = [d for d in under(ORANGES) if "Easy Peelers" in d["title"]]
    assert peelers
    assert not [d for d in peelers if "orange" in f"{d['title']} {d['description']}".lower()]


@pytest.mark.parametrize(
    "phrase",
    [
        "Chocolate Orange",
        "Cranberry & Orange Panettone",
        "Orange Shortbread",
        "Orange Drinking Chocolate",
        "Chocolate & Orange Cookies",
        "Seville Orange Marmalade",
        "Smooth Orange Juice",
    ],
)
def test_a_flavour_use_of_orange_sits_outside_the_oranges_leaf(phrase: str) -> None:
    hits = [d for d in docs() if phrase in d["title"]]
    assert hits, phrase
    assert not [d for d in hits if d["category_path"][: len(ORANGES)] == ORANGES]


def test_the_word_orange_names_more_products_outside_the_leaf_than_inside_it() -> None:
    inside = [d for d in under(ORANGES) if "orange" in d["title"].lower()]
    assert inside
    assert len(titled("orange", ORANGES)) >= 3 * len(inside)


@pytest.mark.parametrize(
    ("leaf", "variety"),
    [("Lemons", "Unwaxed Lemons"), ("Apples", "Gala Apples"), ("Apples", "Bramley Apples")],
)
def test_other_fresh_produce_has_a_bare_noun_leaf_too(leaf: str, variety: str) -> None:
    held = [d for d in docs() if d["category_leaf"] == leaf]
    assert held
    assert all(d["category_path"][:3] == ["Food & Drink", "Fruit & Vegetables", "Fresh Fruit"] for d in held)
    assert any(variety in values(v["attributes"], "variety") for d in held for v in d["variants"])


# --------------------------------------------------------------------------
# Beer: five leaves, an abv attribute on every beer, in some titles only.
# --------------------------------------------------------------------------


def beers() -> list[dict]:
    return under(BEER)


def test_beer_has_its_five_leaves_under_one_beer_node() -> None:
    assert {d["category_path"][3:] and d["category_path"][3] for d in beers()} == set(BEER_LEAVES)
    assert all(len(d["category_path"]) == 4 and d["product_type"] == "Beer" for d in beers())


def test_every_beer_carries_an_abv_attribute_and_only_some_titles_state_it() -> None:
    held = beers()
    assert held
    stated = 0
    for d in held:
        abv = values(d["attributes"], "abv")
        assert len(abv) == 1, d["product_id"]
        number = float(next(iter(abv)))
        assert 0 <= number <= 9
        stated += f"{number:g}%" in d["title"]
    assert 0 < stated < len(held)


def test_a_beer_abv_is_a_flat_number_and_the_volume_is_in_ml() -> None:
    rows = [r for r in flat() if r["category_path"][:3] == BEER]
    assert rows
    for r in rows:
        assert "abv" in r["facets_num"], r["sku"]
        assert r["facets_num"]["net_volume"] > 0 or values(r["attributes"], "net_volume")
        assert any(e["key"] == "net_volume" and e["unit"] == "MLT" for e in r["attributes"])


def test_a_beer_contains_gluten_and_a_lager_need_not_say_beer() -> None:
    for d in beers():
        for v in d["variants"]:
            assert "Gluten" in values(v["attributes"], "contains"), v["sku"]
            assert "Gluten Free" not in values(v["attributes"], "dietary")
    assert [d for d in beers() if "beer" not in d["title"].lower()]
    assert [d for d in beers() if "beer" in d["title"].lower()]


def test_the_alcohol_free_leaf_holds_beers_at_half_a_percent_or_less() -> None:
    free = [d for d in beers() if d["category_path"][3] == "Alcohol Free"]
    assert free
    assert all(float(next(iter(values(d["attributes"], "abv")))) <= 0.5 for d in free)


@pytest.mark.parametrize(
    ("phrase", "path"),
    [
        ("Ginger Beer", ["Food & Drink", "Drinks", "Soft Drinks"]),
        ("Beer Battered Scottish Haddock", ["Food & Drink", "Frozen", "Battered Fish"]),
        ("Beer Battered Cod", ["Food & Drink", "Frozen", "Battered Fish"]),
        ("Cider Vinegar", ["Food & Drink", "Food Cupboard", "Vinegar"]),
        ("Wine Gums", ["Food & Drink", "Chocolate & Sweets", "Sweets"]),
    ],
)
def test_a_modifier_or_compound_use_sits_in_its_own_category(phrase: str, path: list[str]) -> None:
    hits = [d for d in docs() if phrase in d["title"]]
    assert hits, phrase
    assert all(d["category_path"] == path for d in hits)


def test_beer_battered_fish_contains_gluten_and_is_not_vegetarian() -> None:
    fish = [d for d in docs() if "Beer Battered" in d["title"]]
    assert fish
    for d in fish:
        for v in d["variants"]:
            assert "Gluten" in values(v["attributes"], "contains")
            assert not {"Vegan", "Vegetarian"} & values(v["attributes"], "dietary")


def test_the_word_beer_names_products_outside_the_beer_category() -> None:
    outside = titled("beer", BEER)
    assert {d["category_path"][-1] for d in outside} >= {"Soft Drinks", "Battered Fish"}


# --------------------------------------------------------------------------
# One category path per product, in both outputs.
# --------------------------------------------------------------------------


def test_a_product_has_exactly_one_category_path_in_both_outputs() -> None:
    ids = [d["product_id"] for d in docs()]
    assert len(ids) == len(set(ids))
    for d in docs():
        assert isinstance(d["category_path"], list) and d["category_leaf"] == d["category_path"][-1]
    for r in flat():
        assert r["category_path"][-1] == r["category_leaf"]
    reached = {r["category_leaf"] for r in flat() if r["category_path"][:3] == BEER}
    assert reached == set(BEER_LEAVES)
    assert {r["category_leaf"] for r in flat() if r["category_path"][:5] == ORANGES} == {"Oranges"}
