"""Gifts party supplies, slice 1 (gen#966): balloons, party plates and bunting.

The Gifts department held 1,003 SKUs at the ceiling build and nothing for a party, so a search
for ``balloons`` or ``bunting`` found no product of the kind. Slice 1 adds three types under
``Gifts > Party Supplies``, each a spec of its own (``type_specs/balloon.py``, ``party_plate.py``,
``party_bunting.py``); balloons and bunting are drawn by :mod:`kit_party`, plates by the tableware
``plate``. These checks hold the slice's Done-when: the ceiling build has at least 1,650 Gifts
SKUs; each type is derived; each type's styles have unique ids, titles, twin keys and SKUs; the
rows and their drawings are the same on every call; and a golden slice pins each type's first
derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

ROOT = "Gifts"
PARTY = (ROOT, "Party Supplies")
KEYS = {"Balloon": "balloon", "Party Plate": "party_plate", "Bunting": "party_bunting"}
TYPES = tuple(KEYS)
#: The slice's floor at the ceiling build (the gate comment of gen#966); main held 1,003.
FLOOR = 1_650


@pytest.fixture(scope="module")
def gifts() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == ROOT]


@pytest.fixture(scope="module")
def party(gifts) -> list[dict]:
    return [r for r in gifts if tuple(r["category_path"][:2]) == PARTY]


def test_the_ceiling_build_holds_the_slice_floor_of_gifts_skus(gifts) -> None:
    skus = sum(r["sku_count"] for r in gifts)
    assert skus >= FLOOR, skus


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(party) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in party if r["product_id"] in derived}
    assert kinds == set(TYPES)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(party, ptype) -> None:
    mine = [r for r in party if r["product_type"] == ptype]
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
    ("shape", "param", "values"),
    [
        ("balloon", "style", ("latex", "foil", "confetti")),
        ("balloon", "finish", ("matte", "pearl", "metallic")),
        ("bunting", "flag", ("pennant", "square", "scalloped")),
        ("bunting", "material", ("paper", "fabric", "felt")),
    ],
)
def test_each_drawn_param_changes_the_drawing(shape, param, values) -> None:
    kit.register_all()
    fill = kit.Fill("solid", "#c8312e", "#ffffff")
    drawings = {kit.render(shape, fill, params={param: v}) for v in values}
    assert len(drawings) == len(values)


def _golden(party: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in party if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Balloon": [
        ("BRD-03577D8FD6A0", "Cressgate Matte Foil Balloons", 18, 4.5),
        ("BRD-0ACEACD6977D", "Dewthorpe Matte Latex Balloons", 18, 5.5),
        ("BRD-0B0AFA8BF2B1", "Stokemoor Metallic Foil Balloons", 18, 6.5),
    ],
    "Party Plate": [
        ("BRD-08603C539371", "Kelby Card Side Plates", 18, 4.05),
        ("BRD-0AA9CB10EA26", "Darham Bamboo Side Plates", 12, 2.2),
        ("BRD-139B51C33C33", "Torthwaite Card Dinner Plates", 18, 2.05),
    ],
    "Bunting": [
        ("BRD-087FF7CAE62D", "Wathfield Paper Pennant Bunting", 9, 7.5),
        ("BRD-1135CE7E367D", "Wenmere Fabric Square Bunting", 15, 7.0),
        ("BRD-1A2DA76E4A30", "Bolthill Fabric Scalloped Bunting", 6, 6.5),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(party, ptype) -> None:
    assert _golden(party, ptype) == GOLDEN[ptype]
