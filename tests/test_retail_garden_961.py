"""Garden, slice 1 (gen#961): planters, outdoor lights and garden chairs.

The Garden department held 827 SKUs at the ceiling build, against the 9,000 the 500K mix plans
(``docs/catalogue-mix-837.md``), so a shopper's search for a planter or a solar path light found
nothing. Slice 1 adds three derivable types, each a spec of its own (``type_specs/planter.py``,
``outdoor_light.py``, ``garden_chair.py``) drawn by :mod:`kit_patio`. These checks hold the
slice's Done-when: the ceiling build has at least 3,400 SKUs under ``Garden``; each type's styles
have unique ids, titles, twin keys and SKU ids; the rows and their drawings are the same on every
call; and a golden slice pins each type's first derived styles, so a change that moves them shows
here. The decoy census of the department (three of each of five classes) is
``tests/test_retail_garden_203.py``, which reads these types from the registry.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, main_colors, scale, type_registry

TYPES = ("Planter", "Outdoor Light", "Garden Chair")
KEYS = {"Planter": "planter", "Outdoor Light": "outdoor_light", "Garden Chair": "garden_chair"}
#: The slice's floor at the ceiling build (the gate comment of gen#961): a third of the way from
#: 827 to the issue's 8,550.
FLOOR = 3_400


@pytest.fixture(scope="module")
def garden() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == "Garden"]


def test_the_ceiling_build_holds_the_slice_floor_of_garden_skus(garden) -> None:
    skus = sum(r["sku_count"] for r in garden)
    assert skus >= FLOOR, skus


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(garden) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in garden if r["product_id"] in derived}
    assert set(TYPES) <= kinds


def _golden(garden: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in garden if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Planter": [
        ("BRD-01D3D51BC153", "Rookery Garden Co. Sprout Round Concrete Planter", 12, 33.0),
        ("BRD-048027E684AD", "Fenwold Nursery Paddock Trough Ceramic Planter", 6, 51.0),
        ("BRD-06041DA4CDD7", "Harbour & Pine Copse Square Galvanized Steel Planter", 18, 53.0),
    ],
    "Outdoor Light": [
        ("BRD-012D10F91282", "Larkmoor Bloom Hardwired Cube Wall Light", 12, 15.0),
        ("BRD-0283E629D687", "Thistle & Wren Wildflower Battery Lantern Wall Light", 18, 28.0),
        ("BRD-02A965807B4F", "Rookery Garden Co. Sprout Solar Bulkhead Wall Light", 18, 27.0),
    ],
    "Garden Chair": [
        ("BRD-00224F280A77", "Fenwold Nursery Paddock Reclining Aluminum Garden Chair", 18, 70.0),
        ("BRD-07968A557327", "Thistle & Wren Wildflower Reclining Acacia Garden Chair", 12, 27.0),
        ("BRD-0ADE7569A567", "Larkmoor Bloom Stacking Plastic Garden Chair", 6, 27.0),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(garden, ptype) -> None:
    assert _golden(garden, ptype) == GOLDEN[ptype]


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(garden, ptype) -> None:
    mine = [r for r in garden if r["product_type"] == ptype]
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
    assert spec.derivable and spec.department == "Garden"
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_offers_the_six_main_colors_on_every_template(ptype) -> None:
    assert ptype not in main_colors.EXCEPTIONS
    for row in type_registry.specs()[KEYS[ptype]].rows:
        assert {c[0] for c in row.colors} >= set(main_colors.MAIN_COLORS), row.code


#: (shape, one reading, another): each param of the slice's shapes changes the drawing.
VARIANTS = [
    ("planter", {"form": "round"}, {"form": "trough"}),
    ("planter", {"material": "ceramic"}, {"material": "galvanized steel"}),
    ("outdoor_light", {"style": "lantern"}, {"style": "bollard"}),
    ("outdoor_light", {"power_source": "solar"}, {"power_source": "plug-in"}),
    ("garden_chair", {"style": "folding"}, {"style": "reclining"}),
    ("garden_chair", {"material": "acacia"}, {"material": "steel"}),
]


@pytest.mark.parametrize(("shape", "one", "other"), VARIANTS, ids=str)
def test_a_param_changes_the_drawing(shape: str, one: dict, other: dict) -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    assert kit.render(shape, fill, params=one) != kit.render(shape, fill, params=other)
    assert kit.render(shape, fill, params={}) == kit.render(shape, fill, params=one)
