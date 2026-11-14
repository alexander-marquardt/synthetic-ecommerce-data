"""Food & Drink pantry staples, slice 1 (gen#964): Coffee Pods, Granola and Flour.

The ceiling build held 12,265 Food & Drink SKUs against the 17,000 of the 500K mix (gen#837), and
no coffee pod, granola or bag of flour. Slice 1 adds the three types, each a derivable spec of its
own (``type_specs/coffee_pods.py``, ``granola.py``, ``flour.py``) drawn by kit shapes the
department already uses. These checks hold the slice's Done-when (the gate comment of gen#964)
and the issue's: the ceiling build holds at least 1,300 SKUs of the three types and at least
16,150 under Food & Drink; each type's styles have unique ids, titles, twin keys and SKU ids; the
rows and their drawings are the same on every call; each type carries its text-match decoys;
and a golden slice pins each type's first derived styles, so a change that moves them shows here.
"""

# ruff: noqa: E501 -- the golden rows read better whole than wrapped.

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

ROOT = "Food & Drink"
KEYS = {"Coffee Pods": "coffee_pods", "Granola": "granola", "Flour": "flour"}
TYPES = tuple(KEYS)
PATHS = {
    "Coffee Pods": [ROOT, "Drinks", "Coffee Pods"],
    "Granola": [ROOT, "Breakfast", "Granola"],
    "Flour": [ROOT, "Food Cupboard", "Baking", "Flour"],
}
#: The slice's floor at the ceiling build (the gate comment of gen#964).
SLICE_FLOOR = 1_300
#: The issue's Done-when: 95% of the 17,000 the 500K mix plans for the department.
DEPARTMENT_FLOOR = 16_150


@pytest.fixture(scope="module")
def food() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == ROOT]


def test_the_ceiling_build_holds_the_slice_floor_of_the_three_types(food) -> None:
    skus = sum(r["sku_count"] for r in food if r["product_type"] in TYPES)
    assert skus >= SLICE_FLOOR, skus


def test_the_ceiling_build_holds_the_issue_floor_of_food_and_drink(food) -> None:
    skus = sum(r["sku_count"] for r in food)
    assert skus >= DEPARTMENT_FLOOR, skus


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_sits_on_its_own_leaf_and_is_derived(food, ptype) -> None:
    mine = [r for r in food if r["product_type"] == ptype]
    assert {tuple(r["category_path"]) for r in mine} == {tuple(PATHS[ptype])}
    derived = set(ceiling_build().template_of)
    assert any(r["product_id"] in derived for r in mine)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(food, ptype) -> None:
    mine = [r for r in food if r["product_type"] == ptype]
    assert mine
    for field in ("product_id", "title"):
        repeats = [v for v, n in collections.Counter(r[field] for r in mine).items() if n > 1]
        assert repeats == [], field
    twins = [k for k, n in collections.Counter(scale.twin_key(r) for r in mine).items() if n > 1]
    assert twins == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert len(skus) == len(set(skus))


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_rows_and_drawings_are_deterministic(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_carries_text_match_decoys_whose_fields_tell_the_truth(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert len(spec.decoys) >= 2
    for d in spec.decoys:
        word = d.query.split()[0]
        doc = d.row.doc()
        assert word.lower() in doc["title"].lower(), d.row.code
        values = " ".join(str(a["value"]) for a in doc["attributes"]).lower()
        assert word.lower() not in values, d.row.code


def _golden(food: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in food if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Coffee Pods": [
        ("BRD-001C88E1EE69", "Lunchtime Hand Roasted Sumatran Dark Roast Espresso Coffee Pods", 3, 3.05),
        ("BRD-00BD2AD56CE1", "Bubbly Roastery Style Colombian Light Roast Espresso Coffee Pods", 3, 3.45),
        ("BRD-00E40C5C57D0", "Bubbly Costa Rican Medium Roast Espresso Coffee Pods", 4, 3.15),
    ],
    "Granola": [
        ("BRD-00A5603347BE", "Kindly Bowl Ready Crunchy Oat Granola with Apple & Cinnamon", 3, 3.8),
        ("BRD-01CB10F6A181", "Goldfield Farms Proper Hand Baked Clustered Spelt Granola with Honey & Almond", 3, 3.25),
        ("BRD-0209B1668DAE", "Trusty Hand Baked Crunchy Oat Granola with Apple & Cinnamon", 3, 2.7),
    ],
    "Flour": [
        ("BRD-0160FB66CA1A", "Crofter's Bakehouse Fair Kitchen Staple Fine Milled Plain Flour", 3, 2.15),
        ("BRD-026F386294B0", "Wheatsheaf Lane Unfussy Roller Milled Plain Flour", 3, 2.05),
        ("BRD-029B2DF151BA", "Trusty Fine Sifted Fine Milled Self-Raising Flour", 3, 2.05),
    ],
}  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(food, ptype) -> None:
    assert _golden(food, ptype) == GOLDEN[ptype]
