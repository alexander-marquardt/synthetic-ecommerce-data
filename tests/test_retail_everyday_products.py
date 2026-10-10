# ruff: noqa: E501
"""The retail build holds the everyday products a shopper types by name (champagne, wine, cider,
hand cream, eye cream, limes, strawberries) and their sibling families (spirits, fortified wine,
perry, mead, the other citrus and berries, foot and body cream), each with the attributes a shopper filters on.

Built at a small size: every depth family plants at least one style at any size.
"""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import grocery  # noqa: E402

DRINKS = ["Food & Drink", "Beer, Wine & Spirits"]
FRUIT = ["Food & Drink", "Fruit & Vegetables", "Fresh Fruit"]
SKIN = ["Beauty", "Skincare"]
SPIRITS = [*DRINKS, "Spirits"]
FORTIFIED = [*DRINKS, "Wine", "Fortified Wine"]
CITRUS = [*FRUIT, "Citrus Fruit"]
BERRIES = [*FRUIT, "Berries"]

#: leaf path -> (the title word, the attribute keys every style of the leaf states)
TYPES = {
    "champagne": (
        DRINKS + ["Wine", "Champagne"],
        "Champagne",
        ("grape", "country", "wine_style", "abv", "pack_size"),
    ),
    "red wine": (
        DRINKS + ["Wine", "Red Wine"],
        "Wine",
        ("grape", "country", "wine_style", "abv", "pack_size"),
    ),
    "white wine": (
        DRINKS + ["Wine", "White Wine"],
        "Wine",
        ("grape", "country", "wine_style", "abv", "pack_size"),
    ),
    "rose wine": (
        DRINKS + ["Wine", "Rosé Wine"],
        "Rosé",
        ("grape", "country", "wine_style", "abv", "pack_size"),
    ),
    "sparkling wine": (
        DRINKS + ["Wine", "Sparkling Wine"],
        "Sparkling",
        ("grape", "country", "wine_style", "abv", "pack_size"),
    ),
    "cider": (DRINKS + ["Cider"], "Cider", ("cider_style", "abv", "pack_size")),
    "hand cream": (SKIN + ["Hand Creams"], "Hand Cream", ("skin_concern", "pack_size")),
    "eye cream": (SKIN + ["Eye Creams"], "Eye Cream", ("skin_concern", "pack_size")),
    "limes": (FRUIT + ["Citrus Fruit", "Limes"], "Lime", ("variety", "origin", "pack_size")),
    "strawberries": (
        FRUIT + ["Berries", "Strawberries"],
        "Strawberr",
        ("variety", "origin", "pack_size"),
    ),
    "whisky": (SPIRITS + ["Whisky"], "Whisk", ("country", "spirit_style", "abv", "pack_size")),
    "gin": (SPIRITS + ["Gin"], "Gin", ("country", "spirit_style", "abv", "pack_size")),
    "vodka": (SPIRITS + ["Vodka"], "Vodka", ("country", "spirit_style", "abv", "pack_size")),
    "rum": (SPIRITS + ["Rum"], "Rum", ("country", "spirit_style", "abv", "pack_size")),
    "tequila": (SPIRITS + ["Tequila"], "Tequila", ("country", "spirit_style", "abv", "pack_size")),
    "port": (FORTIFIED + ["Port"], "Port", ("grape", "country", "wine_style", "abv", "pack_size")),
    "sherry": (FORTIFIED + ["Sherry"], "Sherry", ("grape", "country", "wine_style", "abv", "pack_size")),
    "vermouth": (FORTIFIED + ["Vermouth"], "Vermouth", ("grape", "country", "wine_style", "abv", "pack_size")),
    "perry": (DRINKS + ["Perry"], "Perry", ("cider_style", "abv", "pack_size")),
    "mead": (DRINKS + ["Mead"], "Mead", ("country", "spirit_style", "abv", "pack_size")),
    "grapefruit": (CITRUS + ["Grapefruit"], "Grapefruit", ("variety", "origin", "pack_size")),
    "mandarins": (CITRUS + ["Mandarins"], "Mandarin", ("variety", "origin", "pack_size")),
    "clementines": (CITRUS + ["Clementines"], "Clementine", ("variety", "origin", "pack_size")),
    "satsumas": (CITRUS + ["Satsumas"], "Satsuma", ("variety", "origin", "pack_size")),
    "raspberries": (BERRIES + ["Raspberries"], "Raspberr", ("variety", "origin", "pack_size")),
    "blueberries": (BERRIES + ["Blueberries"], "Blueberr", ("variety", "origin", "pack_size")),
    "blackberries": (BERRIES + ["Blackberries"], "Blackberr", ("variety", "origin", "pack_size")),
    "foot cream": (SKIN + ["Foot Creams"], "Foot Cream", ("skin_concern", "pack_size")),
    "body cream": (["Beauty", "Body Care", "Body Creams"], "Body Cream", ("scent", "pack_size")),
}


#: name -> (lowest, highest) plausible price of one variant, in pounds: what a shopper would find
#: on a shelf for the pack sizes generated (a 75cl bottle to a 1.5L one, a tube, a pack of fruit).
BANDS = {
    "champagne": (10.0, 150.0),
    "red wine": (3.0, 60.0),
    "white wine": (3.0, 60.0),
    "rose wine": (3.0, 60.0),
    "sparkling wine": (3.0, 60.0),
    "cider": (0.8, 20.0),
    "hand cream": (0.8, 30.0),
    "eye cream": (2.0, 60.0),
    "limes": (0.3, 12.0),
    "strawberries": (0.8, 12.0),
    "whisky": (12.0, 80.0),
    "gin": (10.0, 45.0),
    "vodka": (9.0, 40.0),
    "rum": (10.0, 50.0),
    "tequila": (14.0, 70.0),
    "port": (5.0, 60.0),
    "sherry": (4.0, 45.0),
    "vermouth": (4.0, 40.0),
    "perry": (0.8, 20.0),
    "mead": (5.0, 40.0),
    "grapefruit": (0.3, 12.0),
    "mandarins": (0.3, 12.0),
    "clementines": (0.3, 12.0),
    "satsumas": (0.3, 12.0),
    "raspberries": (0.8, 12.0),
    "blueberries": (0.8, 12.0),
    "blackberries": (0.8, 12.0),
    "foot cream": (0.8, 30.0),
    "body cream": (1.5, 40.0),
}


@cache
def docs() -> tuple[dict, ...]:
    return tuple(grocery.documents(grocery.build(600)))


@pytest.mark.parametrize("name", TYPES)
def test_the_type_is_generated_with_its_attributes(name: str) -> None:
    path, word, keys = TYPES[name]
    held = [d for d in docs() if d["category_path"] == path]
    assert held, f"no {name} at {'>'.join(path)}"
    for d in held:
        assert word in d["title"], d["title"]
        assert d["category_leaf"] == path[-1]
        have = {e["key"]: e["value"] for e in d["attributes"]}
        for key in keys:
            assert have.get(key), f"{d['title']}: {key} is empty"
        assert d["variants"]
        low, high = BANDS[name]
        for v in d["variants"]:
            assert low <= v["price"] <= high, f"{d['title']}: {v['price']} outside {low}-{high}"


def test_a_wine_states_a_volume_and_a_strength() -> None:
    wines = [d for d in docs() if d["category_path"][:3] == [*DRINKS, "Wine"]]
    assert wines
    for d in wines:
        assert any("net_volume" in {e["key"] for e in v["attributes"]} for v in d["variants"])
        assert float(next(e["value"] for e in d["attributes"] if e["key"] == "abv")) > 0


SIBLINGS = ("whisky", "gin", "vodka", "rum", "tequila", "port", "sherry", "vermouth", "perry", "mead")


@pytest.mark.parametrize("name", SIBLINGS)
def test_a_spirit_fortified_wine_perry_or_mead_states_a_volume_and_a_strength(name: str) -> None:
    held = [d for d in docs() if d["category_path"] == TYPES[name][0]]
    assert held
    for d in held:
        assert any("net_volume" in {e["key"] for e in v["attributes"]} for v in d["variants"])
        assert float(next(e["value"] for e in d["attributes"] if e["key"] == "abv")) > 0


def test_fortified_wine_sits_under_wine_and_spirits_beside_it() -> None:
    paths = {tuple(d["category_path"]) for d in docs()}
    assert (*FORTIFIED, "Port") in paths
    assert (*SPIRITS, "Whisky") in paths
