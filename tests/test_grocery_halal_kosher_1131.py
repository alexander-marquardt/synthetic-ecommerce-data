"""Halal and Kosher on food products, by category share and by rule (gen#1131).

They are certifications of a product line, so each one is drawn once per product, from its
id, at its category's ``CERTIFICATION`` share. A variant keeps one only when it passes the
rules: never Halal on pork or alcohol, never Kosher on pork, shellfish or meat with milk.
Each rule is pinned over every SKU of a build (the #913 class), as the Vegan rule is.
"""

from __future__ import annotations

from functools import cache

from synthetic_ecommerce_data.domains.retail import grocery, grocery_rows
from synthetic_ecommerce_data.domains.retail.grocery_model import CERTIFICATION, F

FAMS = {f.code: f for f in grocery_rows.FAMILIES}
PORK = {"Pork Sausages", "Smoked Bacon", "Pepperoni", "Ham & Pineapple"}


@cache
def _recs() -> tuple[dict, ...]:
    return tuple(grocery.build(grocery.TARGET))


def _skus():
    """Every food SKU with its family and flavor: (record, family, flavor, sku)."""
    for r in _recs():
        fam = FAMS[r["product_id"].split("-")[1]]
        if not fam.food:
            continue
        by_name = {f.name: f for f in fam.flavors}
        for sku in r["skus"]:
            yield r, fam, by_name[sku[fam.axis]], sku


def _labels(sku: dict) -> set[str]:
    return set(sku.get("dietary", ()))


def test_the_dietary_list_ends_with_halal_and_kosher() -> None:
    assert grocery_rows.DIETARY[-2:] == ("Halal", "Kosher")


def test_pork_and_shellfish_flags_each_imply_meat_and_pork_is_the_named_flavors() -> None:
    flagged = {fl.name for f in grocery_rows.FAMILIES for fl in f.flavors if "p" in fl.codes}
    assert flagged == PORK
    for fam in grocery_rows.FAMILIES:
        for fl in fam.flavors:
            if {"p", "s"} & set(fl.codes):
                assert "x" in fl.codes, (fam.code, fl.name)


def test_no_sku_is_halal_on_pork_or_alcohol() -> None:
    halal = 0
    for r, fam, fl, sku in _skus():
        if "Halal" in _labels(sku):
            halal += 1
            assert "p" not in fl.codes, (r["product_id"], fl.name)
            drink = grocery.alcoholic(fam, fl, sku.get("ingredients"))
            assert not drink, (r["product_id"], fl.name)
    assert halal > 0


def test_no_sku_is_kosher_on_pork_shellfish_or_meat_with_milk() -> None:
    kosher = 0
    for r, _fam, fl, sku in _skus():
        if "Kosher" in _labels(sku):
            kosher += 1
            contains = set(sku.get("contains", ()))
            assert not {"p", "s"} & set(fl.codes), (r["product_id"], fl.name)
            meat = "x" in fl.codes and "Fish" not in contains
            assert not (meat and "Milk" in contains), (r["product_id"], fl.name)
    assert kosher > 0


def test_no_sku_is_vegan_on_milk_egg_meat_fish_or_honey() -> None:
    vegan = 0
    for r, _fam, fl, sku in _skus():
        if "Vegan" in _labels(sku):
            vegan += 1
            assert not {"Milk", "Egg", "Fish"} & set(sku.get("contains", ())), r["product_id"]
            assert not {"x", "h"} & set(fl.codes), (r["product_id"], fl.name)
    assert vegan > 0


def test_a_certification_is_the_products_own_draw_and_only_in_its_categories() -> None:
    for r, fam, _fl, sku in _skus():
        held = _labels(sku) & {"Halal", "Kosher"}
        assert held <= grocery.certified(fam, r["product_id"]), (r["product_id"], held)
        if held:
            assert tuple(fam.path[1:3]) in CERTIFICATION, (r["product_id"], fam.path)


def test_every_certified_category_holds_both_values_and_others_hold_none() -> None:
    seen: dict[tuple[str, ...], set[str]] = {}
    for _r, fam, _fl, sku in _skus():
        seen.setdefault(tuple(fam.path[1:3]), set()).update(_labels(sku) & {"Halal", "Kosher"})
    for cat in CERTIFICATION:
        assert seen.get(cat) == {"Halal", "Kosher"}, cat
    assert all(not v for k, v in seen.items() if k not in CERTIFICATION)


def test_the_draw_depends_on_the_product_id_alone() -> None:
    fam = FAMS["CHB"]
    pids = [f"GRC-CHB-{n:04d}" for n in range(1, 401)]
    first = [grocery.certified(fam, p) for p in pids]
    assert first == [grocery.certified(fam, p) for p in pids]
    halal = sum("Halal" in c for c in first) / len(pids)
    kosher = sum("Kosher" in c for c in first) / len(pids)
    assert abs(halal - 0.25) < 0.07 and abs(kosher - 0.30) < 0.07
    assert grocery.certified(FAMS["HON"], "GRC-HON-0001") == frozenset()


def test_the_rules_on_planted_flavors() -> None:
    both = frozenset({"Halal", "Kosher"})
    plain = {"contains": [], "may_contain": []}
    milk = {"contains": ["Milk"], "may_contain": []}
    fish = {"contains": ["Fish", "Milk"], "may_contain": []}
    labels = lambda fl, facts, alcohol=False: grocery.dietary(fl, facts, False, both, alcohol)  # noqa: E731
    assert {"Halal", "Kosher"} <= set(labels(F("Chicken", "#ffffff", "x"), plain))
    assert set(labels(F("Prawns", "#ffffff", "xs"), plain)) & both == {"Halal"}
    assert set(labels(F("Ham", "#ffffff", "xp"), plain)) & both == set()
    assert set(labels(F("Chicken Alfredo", "#ffffff", "Mx"), milk)) & both == {"Halal"}
    assert set(labels(F("Fish Pie", "#ffffff", "xF"), fish)) & both == both
    assert set(labels(F("Rum Truffle", "#ffffff", "M"), milk, True)) & both == {"Kosher"}
    assert set(grocery.dietary(F("Chicken", "#ffffff", "x"), plain, False)) & both == set()


def test_an_alcohol_in_the_ingredients_is_found_and_a_vinegar_is_not() -> None:
    fam, fl = FAMS["CHB"], FAMS["CHB"].flavors[0]
    assert grocery.alcoholic(fam, fl, ["sugar", "dark rum (4%)"])
    assert grocery.alcoholic(fam, fl, ["cream", "irish whiskey"])
    assert not grocery.alcoholic(fam, fl, ["sugar", "white wine vinegar", "ginger"])
    assert not grocery.alcoholic(fam, fl, None)
