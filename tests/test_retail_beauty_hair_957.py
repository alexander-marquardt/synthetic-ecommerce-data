"""Beauty, slice 1 (gen#957): hair care in depth, with dryers, straighteners and hairbrushes.

Main's ceiling build held 2,589 Beauty SKUs against the 500K mix's 14,000, with 24 shampoos, 24
conditioners and no hair tool, so a search for ``hair dryer`` or ``paddle brush`` found nothing.
Slice 1 adds three types, each a spec of its own (``type_specs/hair_dryer.py``,
``hair_straightener.py``, ``hairbrush.py``) drawn by :mod:`kit_hair`, and widens Shampoo and
Conditioner to six hair types and six ingredients each. These checks hold the slice's Done-when:
the ceiling build has at least 5,000 Beauty SKUs; each new type's styles have unique ids,
titles, twin keys and SKU ids; the rows and their drawings are the same on every call; and a
golden slice pins each new type's first derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import hair_rows, kit, scale, type_registry

TYPES = ("Hair Dryer", "Hair Straightener", "Hairbrush")
KEYS = {
    "Hair Dryer": "hair_dryer",
    "Hair Straightener": "hair_straightener",
    "Hairbrush": "hairbrush",
}
#: The slice's floor at the ceiling build (the gate comment of gen#957).
FLOOR = 5_000
#: Shampoo and Conditioner each held 24 SKUs; the wider pools must lift each well past that.
WASH_FLOOR = 400


@pytest.fixture(scope="module")
def beauty() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == hair_rows.DEPARTMENT]


def test_the_ceiling_build_holds_the_slice_floor_of_beauty_skus(beauty) -> None:
    skus = sum(r["sku_count"] for r in beauty)
    assert skus >= FLOOR, skus


def test_every_new_type_is_derived_under_hair_care(beauty) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in beauty if r["product_id"] in derived}
    assert set(TYPES) <= kinds
    paths = {r["product_type"]: tuple(r["category_path"][:2]) for r in beauty}
    assert {paths[t] for t in TYPES} == {("Beauty", "Hair Care")}


@pytest.mark.parametrize("ptype", ("Shampoo", "Conditioner"))
def test_shampoo_and_conditioner_derive_from_six_hair_types_and_ingredients(beauty, ptype) -> None:
    mine = [r for r in beauty if r["product_type"] == ptype]
    hair = {a["value"] for r in mine for a in r["attributes"] if a["key"] == "hair_type"}
    ingredient = {a["value"] for r in mine for a in r["attributes"] if a["key"] == "ingredient"}
    assert len(hair) >= 6 and len(ingredient) >= 6, (hair, ingredient)
    assert sum(r["sku_count"] for r in mine) >= WASH_FLOOR


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(beauty, ptype) -> None:
    mine = [r for r in beauty if r["product_type"] == ptype]
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


@pytest.mark.parametrize(
    ("shape", "key", "values"),
    [
        ("hair_dryer", "technology", ("ionic", "ceramic", "tourmaline", "infrared")),
        ("hair_dryer", "form", ("compact", "salon", "travel", "folding")),
        ("hair_straightener", "plate", ("ceramic", "titanium", "tourmaline")),
        ("hair_straightener", "kind", ("mini", "salon", "cordless", "travel")),
        ("hairbrush", "head", ("paddle", "round", "vent", "detangling")),
        ("hairbrush", "bristle", ("boar", "nylon", "mixed")),
    ],
)
def test_each_param_value_draws_its_own_figure(shape, key, values) -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    drawn = {kit.render(shape, fill, params={key: v}) for v in values}
    assert len(drawn) == len(values)


def _golden(beauty: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in beauty if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each new type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Hair Dryer": [
        ("BRD-0077A410FA13", "Rosfield Ceramic Travel Hair Dryer", 18, 47.0),
        ("BRD-01D56FB601F9", "Bradridge Infrared Travel Hair Dryer", 6, 38.0),
        ("BRD-0609FB2D7E62", "Dunstead Infrared Folding Hair Dryer", 15, 30.0),
    ],
    "Hair Straightener": [
        ("BRD-027568501F10", "Fairmoor Ceramic Salon Hair Straightener", 6, 17.0),
        ("BRD-051B2818F4E3", "Rosley Tourmaline Mini Hair Straightener", 12, 51.0),
        ("BRD-107E2D20C55F", "Cleveside Titanium Salon Hair Straightener", 6, 62.0),
    ],
    "Hairbrush": [
        ("BRD-0160A1505BAC", "Elleringham Nylon Paddle Hairbrush", 9, 7.5),
        ("BRD-03DDB4C39E3D", "Falmouth Mixed Bristle Vent Hairbrush", 18, 12.0),
        ("BRD-03F99A7428C0", "Cresswick Mixed Vent Hairbrush", 12, 9.5),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(beauty, ptype) -> None:
    assert _golden(beauty, ptype) == GOLDEN[ptype]
