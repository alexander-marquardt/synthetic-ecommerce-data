"""Pets, slice 1 (gen#967): the department, with dog food, cat food and cat litter.

The retail catalogue had no pets department, so a search for ``dry dog food`` or ``cat litter``
found nothing. Slice 1 adds the department (``core/departments.RETAIL``) and its first three
types, each a spec of its own (``type_specs/dog_food.py``, ``cat_food.py``, ``cat_litter.py``)
drawn by :mod:`kit_pets`. These checks hold the slice's Done-when: the ceiling build has at least
2,000 SKUs under the department; each type's styles have unique ids, titles and twin keys; the
rows and their drawings are the same on every call; and a golden slice pins each type's first
derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core import departments
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

#: The department, the top level of every pets path.
ROOT = "Pets"
TYPES = ("Dog Food", "Cat Food", "Cat Litter")
KEYS = {"Dog Food": "dog_food", "Cat Food": "cat_food", "Cat Litter": "cat_litter"}
#: The slice's floor at the ceiling build (the gate comment of gen#967).
FLOOR = 2_000


@pytest.fixture(scope="module")
def pets() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == ROOT]


def test_the_department_is_on_the_closed_list() -> None:
    assert ROOT in departments.RETAIL


def test_the_ceiling_build_holds_the_slice_floor_of_pets_skus(pets) -> None:
    skus = sum(r["sku_count"] for r in pets)
    assert skus >= FLOOR, skus


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(pets) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in pets if r["product_id"] in derived}
    assert kinds == set(TYPES)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(pets, ptype) -> None:
    mine = [r for r in pets if r["product_type"] == ptype]
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


def _golden(pets: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in pets if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Dog Food": [
        ("BRD-00E89FE10BED", "Fenstone Adult Large Breed Dry Dog Food with Chicken & Rice", 4, 8.5),
        ("BRD-0139F80E655E", "Glenby Puppy Small Breed Dry Dog Food with Beef & Vegetable", 3, 8.5),
        ("BRD-015EB9FD793C", "Merhill Senior Medium Breed Dry Dog Food with Turkey & Sweet Potato", 3, 8.5),  # noqa: E501
    ],
    "Cat Food": [
        ("BRD-006AF6BEB0E4", "Hepgate Senior Wet Cat Food with Tuna Pate, Tins", 4, 2.55),
        ("BRD-01B4E9895FF8", "Walwyke Adult Hairball Control Dry Cat Food with Chicken", 3, 3.85),
        ("BRD-02FDA95F49AE", "Fenbank Senior Wet Cat Food with Chicken in Jelly, Pouches", 3, 4.45),
    ],
    "Cat Litter": [
        ("BRD-00112B468C03", "Baringham Baby Powder Wood Pellet Cat Litter", 3, 6.5),
        ("BRD-03E57A1B6D5A", "Sandcroft Lavender Clumping Clay Cat Litter", 3, 3.2),
        ("BRD-06F75E8C843B", "Holness Citrus Clumping Clay Cat Litter", 3, 5.5),
    ],
}  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(pets, ptype) -> None:
    assert _golden(pets, ptype) == GOLDEN[ptype]
