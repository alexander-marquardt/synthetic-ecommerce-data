"""Electronics gaming, slice 2b (gen#956): game controllers and gaming headsets.

At the ceiling build the Electronics department held 1,166 SKUs. The 500K mix plans 14,000
(``docs/catalogue-mix-837.md``). A shopper who searched for a game controller found nothing, and
a search for a gaming headset found one ``Earbuds`` row. Slice 2b adds two derivable types under
``Electronics > Gaming``. Each is a spec of its own (``type_specs/game_controller.py``,
``gaming_headset.py``), drawn by :mod:`kit_gaming`.

These checks hold the slice's Done-when, from the gate comment of gen#956:

- On their own, the two types add at least 700 SKUs to the ceiling build, so the slice holds
  whether or not slices 1 and 2a are merged first.
- Each type holds between 350 and 600 SKUs. Slices 2a, 2b and 3 share the department's last
  4,500 SKUs, so a type that grows past the band takes slice 3's share.
- Each type's styles have unique ids, titles, SKUs and twin keys.
- The rows and their drawings are the same on every call.
- A golden slice pins each type's first derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

ROOT = "Electronics"
TYPES = ("Game Controller", "Gaming Headset")
KEYS = {"Game Controller": "game_controller", "Gaming Headset": "gaming_headset"}
#: What the slice adds at the ceiling build on its own (the gate comment of gen#956).
FLOOR = 700
#: Each type's share of the department's remaining SKUs: low, high.
BAND = (350, 600)


@pytest.fixture(scope="module")
def electronics() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == ROOT]


def _skus(electronics: list[dict], ptype: str) -> int:
    return sum(r["sku_count"] for r in electronics if r["product_type"] == ptype)


def test_the_slice_adds_its_floor_of_electronics_skus(electronics) -> None:
    added = sum(_skus(electronics, t) for t in TYPES)
    assert added >= FLOOR, added


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_holds_its_share_of_the_department(electronics, ptype) -> None:
    low, high = BAND
    assert low <= _skus(electronics, ptype) <= high, _skus(electronics, ptype)


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(electronics) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in electronics if r["product_id"] in derived}
    assert kinds >= set(TYPES)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_sits_under_gaming(electronics, ptype) -> None:
    mine = [r for r in electronics if r["product_type"] == ptype]
    assert mine
    assert {tuple(r["category_path"][:2]) for r in mine} == {(ROOT, "Gaming")}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(electronics, ptype) -> None:
    mine = [r for r in electronics if r["product_type"] == ptype]
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
    ("shape", "params", "other"),
    [
        ("game_controller", {"controller_form": "classic"}, {"controller_form": "pro"}),
        ("game_controller", {"controller_form": "classic"}, {"controller_form": "mobile"}),
        ("game_controller", {"connection": "wireless"}, {"connection": "wired"}),
        ("gaming_headset", {"connection": "wireless"}, {"connection": "wired"}),
    ],
)
def test_a_param_changes_the_drawing(shape, params, other) -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    assert kit.render(shape, fill, params=params) != kit.render(shape, fill, params=other)


def _golden(electronics: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in electronics
                   if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {  # fmt: skip
    "Game Controller": [
        ("BRD-04F2FEFA22A6", "Burnbury Pro Wireless Game Controller", 4, 33.0),
        ("BRD-05693091192E", "Holwell Wireless Game Controller", 6, 50.0),
        ("BRD-061FF7AC2190", "Beling Pro Wireless Game Controller", 6, 28.0),
    ],
    "Gaming Headset": [
        ("BRD-013A5149F0E8", "Thorncliffe Wireless Gaming Headset", 6, 100.0),
        ("BRD-0856DD2BE3A9", "Elleringham Wireless Stereo Gaming Headset", 6, 130.0),
        ("BRD-094AD4605794", "Walholme Wired Stereo Gaming Headset", 6, 41.0),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(electronics, ptype) -> None:
    assert _golden(electronics, ptype) == GOLDEN[ptype]
