# ruff: noqa: E501
"""The retail build holds the everyday products a shopper types by name (champagne, wine, cider,
hand cream, eye cream, limes, strawberries), each with the attributes a shopper filters on.

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

#: leaf path -> (the title word, the attribute keys every style of the leaf states)
TYPES = {
    "champagne": (DRINKS + ["Wine", "Champagne"], "Champagne", ("grape", "country", "wine_style", "abv", "pack_size")),
    "red wine": (DRINKS + ["Wine", "Red Wine"], "Wine", ("grape", "country", "wine_style", "abv", "pack_size")),
    "white wine": (DRINKS + ["Wine", "White Wine"], "Wine", ("grape", "country", "wine_style", "abv", "pack_size")),
    "rose wine": (DRINKS + ["Wine", "Rosé Wine"], "Rosé", ("grape", "country", "wine_style", "abv", "pack_size")),
    "sparkling wine": (DRINKS + ["Wine", "Sparkling Wine"], "Sparkling", ("grape", "country", "wine_style", "abv", "pack_size")),
    "cider": (DRINKS + ["Cider"], "Cider", ("cider_style", "abv", "pack_size")),
    "hand cream": (SKIN + ["Hand Creams"], "Hand Cream", ("skin_concern", "pack_size")),
    "eye cream": (SKIN + ["Eye Creams"], "Eye Cream", ("skin_concern", "pack_size")),
    "limes": (FRUIT + ["Citrus Fruit", "Limes"], "Lime", ("variety", "origin", "pack_size")),
    "strawberries": (FRUIT + ["Berries", "Strawberries"], "Strawberr", ("variety", "origin", "pack_size")),
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
        assert d["variants"] and all(v["price"] > 0 for v in d["variants"])


def test_a_wine_states_a_volume_and_a_strength() -> None:
    wines = [d for d in docs() if d["category_path"][:3] == [*DRINKS, "Wine"]]
    assert wines
    for d in wines:
        assert any("net_volume" in {e["key"] for e in v["attributes"]} for v in d["variants"])
        assert float(next(e["value"] for e in d["attributes"] if e["key"] == "abv")) > 0
