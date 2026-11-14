"""Electronics gadgets, slice 3a (gen#956): power banks, webcams and smartwatches.

At the ceiling build the Electronics department held 1,166 SKUs. The 500K mix plans 14,000
(``docs/catalogue-mix-837.md``). A shopper who searched for a webcam or a smartwatch found
nothing, and a power bank search found four ``Charger`` rows. Slice 3a adds three derivable
types: ``Electronics > Accessories > Power Banks``, ``Computers > Webcams`` and
``Wearables > Smartwatches``. Each is a spec of its own (``type_specs/power_bank.py``,
``webcam.py``, ``smartwatch.py``), drawn by :mod:`kit_gadgets`.

These checks hold the slice's Done-when, from the gate comment of gen#956:

- On their own, the three types add at least 1,000 SKUs to the ceiling build, so the slice holds
  whether or not slices 1, 2a and 2b are merged first. With them, the department passes the
  issue's 13,300 floor.
- Each type holds between 350 and 600 SKUs, so slice 3b (printers and ink) keeps its share.
- Each type's styles have unique ids, titles, SKUs and twin keys.
- The rows and their drawings are the same on every call, and each param changes the drawing.
- A golden slice pins each type's first derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

ROOT = "Electronics"
#: Each type, its spec key and the node under ``Electronics`` it sits in.
TYPES = {
    "Power Bank": ("power_bank", ("Accessories", "Power Banks")),
    "Webcam": ("webcam", ("Computers", "Webcams")),
    "Smartwatch": ("smartwatch", ("Wearables", "Smartwatches")),
}
#: What the slice adds at the ceiling build on its own (the gate comment of gen#956).
FLOOR = 1_000
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
def test_each_type_sits_under_its_node(electronics, ptype) -> None:
    mine = [r for r in electronics if r["product_type"] == ptype]
    assert mine
    assert {tuple(r["category_path"][1:]) for r in mine} == {TYPES[ptype][1]}


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


def test_a_derived_webcam_title_keeps_the_case_of_4k(electronics) -> None:
    titles = [r["title"] for r in electronics if r["product_type"] == "Webcam"]
    assert any("4K" in t for t in titles)
    assert not [t for t in titles if "4k" in t or "full hd" in t.lower() and "Full HD" not in t]


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_rows_and_drawings_are_deterministic(ptype) -> None:
    spec = type_registry.specs()[TYPES[ptype][0]]
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


@pytest.mark.parametrize(
    ("shape", "params", "other"),
    [
        ("power_bank", {"power_bank_form": "slim"}, {"power_bank_form": "rugged"}),
        ("power_bank", {"power_bank_form": "slim"}, {"power_bank_form": "magnetic"}),
        ("power_bank", {"power_bank_charging": "usb-c"}, {"power_bank_charging": "wireless"}),
        ("webcam", {"webcam_use": "streaming"}, {"webcam_use": "conference"}),
        ("webcam", {"webcam_feature": "privacy shutter"}, {"webcam_feature": "ring light"}),
        ("smartwatch", {"smartwatch_face": "round"}, {"smartwatch_face": "square"}),
        ("smartwatch", {"smartwatch_network": "gps"}, {"smartwatch_network": "cellular"}),
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
    "Power Bank": [
        ("BRD-006DDB4B6F2A", "Yarington Rugged Power Bank", 6, 43.0),
        ("BRD-02166BB08EC2", "Sandbeck Power Bank with Built-in Cable", 6, 36.0),
        ("BRD-049E59BD4EDB", "Gosham Power Bank with Built-in Cable", 6, 50.0),
    ],
    "Webcam": [
        ("BRD-028A1F52DDA5", "Shelby Full HD Streaming Webcam", 6, 95.0),
        ("BRD-03A5CF4A742C", "Walhill Webcam with Ring Light", 6, 40.0),
        ("BRD-05F0E6B1F561", "Sutfell 4K Conference Webcam", 6, 88.0),
    ],
    "Smartwatch": [
        ("BRD-09047AA2CAC1", "Winmoor Round Cellular Smartwatch", 6, 350.0),
        ("BRD-0995A2837ADD", "Wykebury Cellular Smartwatch", 6, 245.0),
        ("BRD-11E912504086", "Holhill Square Cellular Smartwatch", 2, 240.0),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(electronics, ptype) -> None:
    assert _golden(electronics, ptype) == GOLDEN[ptype]
