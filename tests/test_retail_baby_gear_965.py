"""Baby gear, slice 1 (gen#965): diapers, baby wipes and baby bottles under Kids > Baby.

Kids > Baby sold clothing only, so a search for ``diapers``, ``baby wipes`` or ``baby bottle``
found nothing. Slice 1 adds its first three gear types, each a spec of its own
(``type_specs/diapers.py``, ``baby_wipes.py``, ``baby_bottle.py``) drawn by :mod:`kit_baby_gear`.
These checks hold the slice's Done-when: the ceiling build has at least 1,100 SKUs of the three
types under Kids > Baby; each type's styles have unique ids, titles and twin keys; the rows and
their drawings are the same on every call; and a golden slice pins each type's first derived
styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

TYPES = ("Diapers", "Baby Wipes", "Baby Bottle")
KEYS = {"Diapers": "diapers", "Baby Wipes": "baby_wipes", "Baby Bottle": "baby_bottle"}
#: The slice's floor at the ceiling build (the gate comment of gen#965).
FLOOR = 1_100


@pytest.fixture(scope="module")
def gear() -> list[dict]:
    return [
        r
        for r in ceiling_build().records
        if tuple(r["category_path"][:2]) == ("Kids", "Baby") and r["product_type"] in TYPES
    ]


def test_the_ceiling_build_holds_the_slice_floor_of_baby_gear_skus(gear) -> None:
    skus = sum(r["sku_count"] for r in gear)
    assert skus >= FLOOR, skus


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(gear) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in gear if r["product_id"] in derived}
    assert kinds == set(TYPES)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(gear, ptype) -> None:
    mine = [r for r in gear if r["product_type"] == ptype]
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


def _golden(gear: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in gear if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
# ruff: noqa: E501 -- a golden row reads better whole than wrapped.
GOLDEN: dict[str, list[tuple]] = {
    "Diapers": [
        ("BRD-025668103BD2", "Quillon Sleep Fluff Plant-Based Tape Diapers", 6, 12.5),
        ("BRD-09D32F707B12", "Fenwold Nursery Repose Overnight Pull-Up Diapers", 6, 12.5),
        ("BRD-0D8D0378F22C", "Quillon Sleep Fluff Leak Guard Tape Diapers", 6, 7.0),
    ],
    "Baby Wipes": [
        ("BRD-0017D8C55E8A", "Calderby & Lune Restful Cucumber Extra Soft Baby Wipes", 4, 1.3),
        ("BRD-012C19730161", "Little Fernby Slumber Cucumber Biodegradable Baby Wipes", 4, 1.85),
        ("BRD-01CF22249E7E", "Mirefield Naturals Doze Unscented Thick Cleansing Baby Wipes", 4, 2.15),
    ],
    "Baby Bottle": [
        ("BRD-03651A2BAAB4", "Larchwood Living Lull Easy Grip Silicone Baby Bottle", 6, 5.5),
        ("BRD-0423DFABAECE", "Fenwold Nursery Repose Fast Flow Silicone Baby Bottle", 4, 8.0),
        ("BRD-077995839159", "Fenwold Nursery Repose Anti-Colic Glass Baby Bottle", 12, 6.5),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(gear, ptype) -> None:
    assert _golden(gear, ptype) == GOLDEN[ptype]
