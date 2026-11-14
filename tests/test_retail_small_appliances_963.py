"""Small kitchen appliances, slice 1 of gen#963: coffee makers, air fryers and blenders.

``Home > Small Appliances`` held only kettles and toasters, so a search for ``air fryer`` or
``coffee maker`` found nothing. Slice 1 adds three derivable types, each a spec of its own
(``type_specs/coffee_maker.py``, ``air_fryer.py``, ``blender.py``) drawn by
:mod:`kit_kitchen_appliances`. These checks hold the slice's Done-when (the gate comment of
gen#963): the ceiling build has at least 17,000 SKUs under ``Home``; each type's styles have
unique ids, titles, twin keys and SKU ids; the rows and their drawings are the same on every
call; and a golden slice pins each type's first derived styles, so a change that moves them
shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

#: The department, the top level of every path the slice adds to.
ROOT = "Home"
CATEGORY = "Small Appliances"
TYPES = ("Coffee Maker", "Air Fryer", "Blender")
KEYS = {"Coffee Maker": "coffee_maker", "Air Fryer": "air_fryer", "Blender": "blender"}
#: The slice's floor at the ceiling build (the gate comment of gen#963; main held 14,059).
FLOOR = 17_000


@pytest.fixture(scope="module")
def home() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == ROOT]


def test_the_ceiling_build_holds_the_slice_floor_of_home_skus(home) -> None:
    skus = sum(r["sku_count"] for r in home)
    assert skus >= FLOOR, skus


def test_every_type_of_the_slice_is_derived_under_small_appliances(home) -> None:
    derived = set(ceiling_build().template_of)
    mine = [r for r in home if r["product_type"] in TYPES]
    assert {r["product_type"] for r in mine if r["product_id"] in derived} == set(TYPES)
    assert {r["category_path"][1] for r in mine} == {CATEGORY}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(home, ptype) -> None:
    mine = [r for r in home if r["product_type"] == ptype]
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


def _golden(home: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in home if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Coffee Maker": [
        ("BRD-003968530EB3", "Townbank Retro Cold Brew Coffee Maker", 3, 34.0),
        ("BRD-00941E85B153", "Winington Slimline Drip Coffee Maker", 5, 140.0),
        ("BRD-022D78E8F869", "Woldsthorpe Digital Espresso Coffee Maker", 6, 62.0),
    ],
    "Air Fryer": [
        ("BRD-00435F8172B1", "Halscar Smart Dual Basket Air Fryer", 6, 55.0),
        ("BRD-008C1EA0682C", "Daling Digital Rotisserie Air Fryer", 12, 77.0),
        ("BRD-02E1A3B5630A", "Horlow Touchscreen Rotisserie Air Fryer", 12, 70.0),
    ],
    "Blender": [
        ("BRD-018897B20052", "Chelington Classic Personal Blender", 2, 26.0),
        ("BRD-03C59B49EA36", "Chaplow Retro Personal Blender", 6, 50.0),
        ("BRD-0495FA35F2D6", "Chelshaw Digital Jug Blender", 3, 25.0),
    ],
}  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(home, ptype) -> None:
    assert _golden(home, ptype) == GOLDEN[ptype]
