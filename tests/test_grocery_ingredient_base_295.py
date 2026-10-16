"""The normalised base-ingredient list next to the raw label text (gen#295).

``facets.ingredients`` keeps the label text; ``facets.ingredient_base`` holds the head
ingredient of each label row, from the committed table ``grocery_ingredients.BASE`` (no
heuristic). One number form: the plural for a countable (peanuts, oranges), the mass noun
otherwise (salt, sugar). A label value with no row is reported, never guessed.
"""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import grocery  # noqa: E402
import grocery_ingredients as gi  # noqa: E402


@cache
def flat() -> tuple[dict, ...]:
    return tuple(grocery.flat(grocery.documents(grocery.build(grocery.TARGET))))


@cache
def label_values() -> frozenset[str]:
    return frozenset(v for r in flat() for v in r["facets"].get("ingredients", ()))


@cache
def base_values() -> frozenset[str]:
    return frozenset(v for r in flat() for v in r["facets"].get("ingredient_base", ()))


@pytest.mark.parametrize(
    ("label", "base"),
    [
        ("orange peel", "oranges"),
        ("sea salt", "salt"),
        ("salt", "salt"),
        ("emulsifier (soya lecithin)", "soya"),
        ("cocoa butter", "cocoa"),
        ("wheat flour", "wheat"),
        ("roasted peanut", "peanuts"),
        ("peanut paste", "peanuts"),
        ("toasted almond", "almonds"),
        ("candied lemon peel", "lemons"),
        ("pasteurised whole cows' milk", "milk"),
        ("cheddar cheese", "cheese"),
        ("sugar", "sugar"),
    ],
)
def test_a_label_maps_to_its_head_ingredient(label: str, base: str) -> None:
    assert gi.BASE.get(label) == base


def test_every_label_value_of_the_build_has_a_row() -> None:
    assert gi.unmapped(label_values()) == []


def test_no_row_names_a_label_the_build_never_writes() -> None:
    """Read over the scale build, which holds the grocery rows and the decoys (gen#294)."""
    import scale  # noqa: PLC0415

    rows = grocery.flat(grocery.documents(scale.build(10**6).records))
    written = {v for r in rows for v in r["facets"].get("ingredients", ())}
    assert sorted(set(gi.BASE) - label_values() - written) == []


def test_a_flat_row_carries_the_base_of_each_label_row_in_order() -> None:
    listed = [r for r in flat() if r.get("ingredients")]
    assert listed
    for r in listed:
        want = list(dict.fromkeys(gi.base_value(v) for v in r["facets"]["ingredients"]))
        assert r["facets"].get("ingredient_base") == want, r["sku"]


def test_a_row_without_a_label_list_has_no_base_list() -> None:
    bare = [r for r in flat() if not r.get("ingredients")]
    assert bare
    assert not [r["sku"] for r in bare if "ingredient_base" in r["facets"]]


def test_the_label_facet_is_kept_as_it_is() -> None:
    sample = next(r for r in flat() if r.get("ingredients"))
    assert sample["facets"]["ingredients"] == list(
        dict.fromkeys(gi.facet_value(i) for i in sample["ingredients"])
    )
    assert "roasted peanut" in label_values()


def test_the_plain_ingredient_is_in_the_base_list_whatever_its_preparation() -> None:
    assert {"peanuts", "almonds", "oranges", "salt", "sugar"} <= base_values()
    assert not {"roasted peanut", "orange peel", "sea salt", "peanut", "orange"} & base_values()


def test_the_base_list_is_shorter_than_the_label_list() -> None:
    assert 0 < len(base_values()) < len(label_values())


def test_a_countable_is_written_in_the_plural_and_a_mass_noun_in_the_singular() -> None:
    singular = {"almond", "peanut", "hazelnut", "cashew", "walnut", "orange", "lemon", "lime",
                "egg", "raisin", "strawberry", "raspberry", "tomato", "potato", "onion"}
    assert not singular & set(gi.BASE.values())
    assert {"salt", "sugar", "milk", "butter", "honey", "cocoa"} <= set(gi.BASE.values())


def test_a_value_with_no_row_is_reported_and_keeps_its_own_value() -> None:
    assert gi.unmapped({"salt", "dragon fruit"}) == ["dragon fruit"]
    assert gi.base_value("Dragon Fruit (12%)") == "dragon fruit"


def test_the_label_text_is_written_in_us_spelling() -> None:
    labels = {i for r in flat() for i in r.get("ingredients", ())}
    assert not [i for i in labels if "flavouring" in i]
    assert any("flavoring" in i for i in labels)


@cache
def scaled_unmapped() -> list[str]:
    """The label values the base table lacks, over the scale build with the decoys (gen#294)."""
    import scale  # noqa: PLC0415

    return grocery.ingredient_report(scale.build(10**6).records)["ingredients_unmapped"]


def test_the_scale_build_with_the_decoys_has_no_unmapped_label() -> None:
    assert scaled_unmapped() == []
