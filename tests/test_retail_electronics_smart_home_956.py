"""Electronics smart home, slice 2a (gen#956): smart plugs, smart bulbs and doorbell cameras.

The Electronics department held 1,166 SKUs at the ceiling build, against the 14,000 the 500K mix
plans (``docs/catalogue-mix-837.md``), and a shopper searching for a smart plug, a smart bulb or a
video doorbell found nothing. Slice 2a adds three derivable types under
``Electronics > Smart Home``, each a spec of its own (``type_specs/smart_plug.py``,
``smart_bulb.py``, ``doorbell_camera.py``) drawn by :mod:`kit_smart_home`.

These checks hold the slice's Done-when (the gate comment of gen#956). The three types add at
least 1,200 SKUs to the ceiling build on their own, so the slice holds whether or not slice 1
(audio) is merged first. Each type is sized between 350 and 900 SKUs: slices 2a, 2b and 3 share
the department's last 4,500 SKUs, so a type that grows past the band takes another type's share.
Each type's styles have unique ids, titles, SKUs and twin keys. The rows and their drawings are
the same on every call. A golden slice pins each type's first derived styles, so a change that
moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, smart_home_rows, type_registry

TYPES = ("Smart Plug", "Smart Bulb", "Doorbell Camera")
KEYS = {
    "Smart Plug": "smart_plug",
    "Smart Bulb": "smart_bulb",
    "Doorbell Camera": "doorbell_camera",
}
#: What the slice adds at the ceiling build on its own (the gate comment of gen#956).
FLOOR = 1_200
#: Each type's share of the department's remaining SKUs: low, high.
BAND = (350, 900)


@pytest.fixture(scope="module")
def electronics() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == smart_home_rows.ROOT]


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
def test_each_type_sits_under_smart_home(electronics, ptype) -> None:
    mine = [r for r in electronics if r["product_type"] == ptype]
    assert mine
    assert {tuple(r["category_path"][:2]) for r in mine} == {(smart_home_rows.ROOT, "Smart Home")}


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
    ("shape", "param", "one", "other"),
    [
        ("smart_plug", "plug_form", "mini", "dual outlet"),
        ("smart_plug", "plug_form", "mini", "outdoor"),
        ("smart_bulb", "bulb_fitting", "e27", "gu10"),
        ("smart_bulb", "bulb_fitting", "e27", "b22"),
        ("doorbell_camera", "doorbell_power", "battery", "wired"),
    ],
)
def test_a_param_changes_the_drawing(shape, param, one, other) -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    assert kit.render(shape, fill, params={param: one}) != kit.render(
        shape, fill, params={param: other}
    )


def _golden(electronics: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in electronics
                   if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {  # fmt: skip
    "Smart Plug": [
        ("BRD-01793710EC8B", "Brockgate Mini Zigbee Smart Plug", 2, 31.0),
        ("BRD-02062D564652", "Woldsside Mini Zigbee Smart Plug", 6, 16.5),
        ("BRD-065868823F3B", "Presbank Mini Zigbee Smart Plug", 6, 37.0),
    ],
    "Smart Bulb": [
        ("BRD-022943A5D604", "Horbrook Wi-Fi Smart Bulb, GU10 Fitting", 4, 10.5),
        ("BRD-02A9A32D1BF5", "Langstead GU10 Warm White Zigbee Smart Bulb", 4, 10.5),
        ("BRD-033371888FD4", "Ellerdale E14 Color Changing Wi-Fi Smart Bulb", 4, 16.0),
    ],
    "Doorbell Camera": [
        ("BRD-0284498502E6", "Copbank Video Doorbell Camera with Package Detection", 2, 140.0),
        ("BRD-066BF8907A5A", "Wigbank Video Doorbell Camera with Night Vision", 6, 130.0),
        ("BRD-072A1FF1DEDA", "Foxmoor Wired Doorbell Camera with App Alerts", 6, 61.0),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(electronics, ptype) -> None:
    assert _golden(electronics, ptype) == GOLDEN[ptype]
