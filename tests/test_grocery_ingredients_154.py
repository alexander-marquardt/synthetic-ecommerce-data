"""Grocery ingredient lists (gen#154): invented, ordered, and never in conflict with the allergens.

Every food product and food SKU carries a top-level ``ingredients`` list of 5 to 20
strings, in descending-weight order as on a label. The lists are tested against the
allergen entries, nested and flat: an ingredient names an allergen source IFF the
allergen is in ``contains``; ``may_contain`` (traces) never appears in a list; a
free-from SKU lists no such source. Fresh whole fruit and vegetables and the two
non-food leaves carry no list. The word lists below are this module's own, not the
generator's, so a wrong list cannot pass by agreeing with itself.
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

#: Phrases that hold an allergen word without the allergen, removed before matching.
NOT_ALLERGEN = re.compile(
    r"cocoa butter|shea butter|coconut (?:milk|cream)|cream of tartar|"
    r"(?:rice|maize|corn|potato|tapioca|chickpea|coconut|buckwheat) (?:flour|starch)|buckwheat"
)
WORDS = {
    "Peanuts": r"\b(?:peanuts?|groundnuts?|arachis)\b",
    "Tree Nuts": (
        r"\b(?:almonds?|hazelnuts?|walnuts?|cashews?|pecans?|pistachios?|macadamias?|nuts?)\b"
    ),
    "Milk": (
        r"\b(?:milk|whey|butter|cream|cheese|cheddar|mozzarella|edam|emmental|yoghurt"
        r"|casein|lactose|ghee)\b"
    ),
    "Gluten": r"\b(?:wheat|barley|rye|oats?|spelt|semolina|malt|couscous|flour|rusk)\b",
    "Soy": r"\b(?:soy|soya|lecithin|tofu|edamame|miso)\b",
    "Egg": r"\b(?:eggs?|albumen|mayonnaise)\b",
}
ANIMAL = re.compile(
    r"\b(?:honey|beeswax|chicken|beef|pork|bacon|ham|pepperoni|tuna|salmon|cod|mackerel|haddock)\b"
)
MEAT = re.compile(r"\b(?:chicken|beef|pork|bacon|ham|pepperoni|tuna|salmon|cod|mackerel|haddock)\b")
NO_LIST = {"Fresh Fruit", "Fresh Vegetables", "Kitchen Cleaner", "Body Lotion"}


@cache
def records() -> list[dict]:
    return grocery.build(grocery.TARGET)


@cache
def docs() -> tuple[dict, ...]:
    return tuple(grocery.documents(list(records())))


@cache
def flat() -> tuple[dict, ...]:
    return tuple(grocery.flat(list(docs())))


def sources(ingredients: list[str]) -> set[str]:
    """The allergens an ingredient list names a source of."""
    found = set()
    for item in ingredients:
        if item.startswith("gluten free"):
            continue
        text = NOT_ALLERGEN.sub(" ", item.lower())
        found |= {a for a, pattern in WORDS.items() if re.search(pattern, text)}
    return found


def values(entries: list[dict], key: str) -> set[str]:
    return {e["value"] for e in entries if e["key"] == key}


def listed(doc: dict) -> bool:
    return doc["product_type"] not in NO_LIST


def test_a_food_product_and_each_of_its_skus_lists_five_to_twenty_ingredients() -> None:
    bad = []
    for d in docs():
        for where, item in [(d["product_id"], d), *((v["sku"], v) for v in d["variants"])]:
            lst = item.get("ingredients")
            if listed(d) != (lst is not None) or (lst and not 5 <= len(lst) <= 20):
                bad.append(where)
            if lst and (
                len(set(lst)) != len(lst) or not all(isinstance(i, str) and i for i in lst)
            ):
                bad.append(where)
    assert bad == []


def test_the_flat_file_carries_ingredients_top_level_and_not_as_an_attribute() -> None:
    rows = list(flat())
    food = [r for r in rows if "ingredients" in r]
    assert len(food) == sum(len(d["variants"]) for d in docs() if listed(d))
    assert food
    for r in rows:
        assert "ingredients" not in {e["key"] for e in r["attributes"]}
        assert "ingredients" not in r["facets"]
        assert "ingredients" not in r["attribute_names"]


@pytest.mark.parametrize("level", ["nested", "flat"])
def test_an_allergen_source_is_listed_iff_the_allergen_is_contained(level: str) -> None:
    if level == "nested":
        items = [(v["sku"], v) for d in docs() for v in d["variants"] if listed(d)]
        items += [(d["product_id"], d) for d in docs() if listed(d)]
    else:
        items = [(r["sku"], r) for r in flat() if "ingredients" in r]
    bad = []
    for name, item in items:
        has = values(item["attributes"], "contains")
        traces = values(item["attributes"], "may_contain")
        named = sources(item.get("ingredients", []))
        if named != has or named & traces:
            bad.append((name, sorted(named ^ has)))
    assert bad == []


def test_a_free_from_sku_lists_no_source_of_that_allergen() -> None:
    bad = [
        r["sku"]
        for r in flat()
        if "ingredients" in r
        and sources(r.get("ingredients", [])) & values(r["attributes"], "free_from")
    ]
    assert bad == []


def test_a_vegan_sku_lists_no_animal_ingredient_and_a_vegetarian_no_meat() -> None:
    bad = []
    for r in flat():
        if "ingredients" not in r:
            continue
        text = " ".join(r.get("ingredients", [])).lower()
        diet = values(r["attributes"], "dietary")
        if ("Vegan" in diet and ANIMAL.search(text)) or (
            "Vegetarian" in diet and MEAT.search(text)
        ):
            bad.append(r["sku"])
    assert bad == []


def test_a_product_lists_the_same_ingredients_in_every_variant_but_its_flavors() -> None:
    """Pack size never changes a list; a flavor adds its own items to the shared ones."""
    bad = []
    for d in docs():
        if not listed(d):
            continue
        by_flavor: dict[str, list] = {}
        for v in d["variants"]:
            flavor = tuple(values(v["attributes"], "flavor"))
            if by_flavor.setdefault(flavor, v.get("ingredients", [])) != v.get("ingredients", []):
                bad.append(v["sku"])
        for v in d["variants"]:
            if any(i not in d.get("ingredients", []) for i in v.get("ingredients", [])):
                bad.append(v["sku"])
    assert bad == []


def test_a_flat_sku_lists_what_its_variant_lists() -> None:
    nested = {
        v["sku"]: v.get("ingredients", []) for d in docs() if listed(d) for v in d["variants"]
    }
    assert {r["sku"]: r["ingredients"] for r in flat() if "ingredients" in r} == nested


def test_the_lists_are_invented_ordered_and_realistic() -> None:
    peanut = next(
        v for d in docs() for v in d["variants"]
        if d["category_leaf"] == "Chocolate Bars"
        and "Peanut Caramel" in values(v["attributes"], "flavor")
    )  # fmt: skip
    assert any(re.fullmatch(r"roasted peanuts \(\d+%\)", i) for i in peanut.get("ingredients", []))
    assert peanut.get("ingredients", [])[0] == "sugar"
    assert "sunflower oil" in {i for d in docs() if listed(d) for i in d.get("ingredients", [])}
    assert all(
        not re.search(r"[A-Z]", i) for d in docs() if listed(d) for i in d.get("ingredients", [])
    )


def test_chocolate_without_peanuts_still_has_both_sides() -> None:
    skus = [r for r in flat() if r["category_leaf"] == "Chocolate Bars"]
    free = [r for r in skus if "Peanuts" in values(r["attributes"], "free_from")]
    has = [r for r in skus if "Peanuts" in values(r["attributes"], "contains")]
    assert free
    assert has
    assert all(sources(r.get("ingredients", [])) & {"Peanuts"} == set() for r in free)
    assert all("Peanuts" in sources(r.get("ingredients", [])) for r in has)


def test_the_lists_are_deterministic_and_vary_by_product() -> None:
    def lists(seed: int) -> list:
        return [s.get("ingredients") for r in grocery.build(2000, seed) for s in r["skus"]]

    assert lists(3) == lists(3)
    assert lists(3) != lists(4)
    crisps = {
        tuple(v.get("ingredients", []))
        for d in docs()
        if d["category_leaf"] == "Crisps"
        for v in d["variants"]
    }
    assert len(crisps) > 6
