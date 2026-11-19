"""Baby gear (gen#965): diapers, wipes, bottles, strollers, car seats, high chairs, cribs and
baby monitors.

Kids > Baby sold clothing only, so a search for ``diapers``, ``baby wipes``, ``baby bottle`` or
``stroller`` found nothing. Slice 1 adds its first three gear types (``type_specs/diapers.py``,
``baby_wipes.py``, ``baby_bottle.py``); slice 2 adds strollers, car seats and high chairs
(``type_specs/stroller.py``, ``car_seat.py``, ``high_chair.py``); slice 3 adds cribs and baby
monitors (``type_specs/crib.py``, ``baby_monitor.py``). Each is a spec of its own, drawn by
:mod:`kit_baby_gear`. These checks hold each slice's Done-when: the ceiling build has at least
the slice's floor of SKUs of its types under Kids > Baby (1,100 for the three types of slices 1
and 2, 600 for the two of slice 3), and all of them with the rest of Kids meet the issue's own
counts; each type's styles have unique ids, titles and twin keys; the
rows and their drawings are the same on every call; a param of each slice 2 and 3 shape changes
its drawing; and a golden slice pins each type's first derived styles, so a change that moves
them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

SLICE_1 = ("Diapers", "Baby Wipes", "Baby Bottle")
SLICE_2 = ("Stroller", "Car Seat", "High Chair")
SLICE_3 = ("Crib", "Baby Monitor")
TYPES = SLICE_1 + SLICE_2 + SLICE_3
KEYS = {
    "Diapers": "diapers", "Baby Wipes": "baby_wipes", "Baby Bottle": "baby_bottle",
    "Stroller": "stroller", "Car Seat": "car_seat", "High Chair": "high_chair",
    "Crib": "crib", "Baby Monitor": "baby_monitor",
}  # fmt: skip
#: Each slice's floor at the ceiling build (the gate comments of gen#965).
FLOORS = {SLICE_1: 1_100, SLICE_2: 1_100, SLICE_3: 600}


@pytest.fixture(scope="module")
def gear() -> list[dict]:
    return [
        r
        for r in ceiling_build().records
        if tuple(r["category_path"][:2]) == ("Kids", "Baby") and r["product_type"] in TYPES
    ]


@pytest.mark.parametrize("types", list(FLOORS), ids=["slice_1", "slice_2", "slice_3"])
def test_the_ceiling_build_holds_the_slice_floor_of_baby_gear_skus(gear, types) -> None:
    skus = sum(r["sku_count"] for r in gear if r["product_type"] in types)
    assert skus >= FLOORS[types], skus


#: gen#965's Done-when: Kids SKUs (95% of the 19,000 target) and baby gear SKUs under Kids > Baby.
KIDS_FLOOR = 18_050
GEAR_FLOOR = 3_261


def test_the_ceiling_build_meets_the_issue_done_when(gear) -> None:
    kids = sum(r["sku_count"] for r in ceiling_build().records if r["category_path"][0] == "Kids")
    assert kids >= KIDS_FLOOR, kids
    assert sum(r["sku_count"] for r in gear) >= GEAR_FLOOR


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


#: Each slice 2 and 3 shape, its param and two readings that must draw differently (gen#512).
PARAMS = {
    "stroller": ("stroller_style", "full-size", "jogging"),
    "car_seat": ("seat_type", "infant carrier", "high-back booster"),
    "high_chair": ("frame", "wooden", "folding"),
    "crib": ("crib_style", "standard", "convertible"),
    "baby_monitor": ("monitor_type", "audio", "video"),
}


@pytest.mark.parametrize("shape", PARAMS)
def test_a_param_changes_the_drawing(shape) -> None:
    assert shape in kit.SHAPES, f"no {shape} shape is registered"
    key, one, other = PARAMS[shape]
    fill = kit.Fill("solid", "#3f6fb5", "#f4f1ea")
    assert kit.render(shape, fill, params={key: one}) != kit.render(shape, fill, params={key: other})


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
    "Stroller": [
        ("BRD-00B0FC30CD7A", "Little Fernby Acorn Reversible Seat Full-Size Stroller", 2, 180.0),
        ("BRD-0558EE92E904", "Little Fernby Acorn One-Hand Fold Jogging Stroller", 3, 450.0),
        ("BRD-05602DD61254", "Larchwood Living Bud Lightweight Compact Stroller", 3, 315.0),
    ],
    "Car Seat": [
        ("BRD-014566DE43C0", "Mirefield Naturals Sail Easy Clean High-Back Booster Car Seat", 2, 130.0),
        ("BRD-0318851BA458", "Emberly Home Saunter Side Impact Convertible Car Seat", 2, 73.0),
        ("BRD-043710479D3B", "Cobble & Kiln Pathway Padded Convertible Car Seat", 4, 74.0),
    ],
    "High Chair": [
        ("BRD-026CA93CB5DD", "Mirefield Naturals Sail Easy Clean Wooden High Chair", 2, 225.0),
        ("BRD-043C204F8B10", "Thistle & Wren Rover Space-Saving Folding High Chair", 2, 145.0),
        ("BRD-050A2E09CB73", "Fenwold Nursery Perch Adjustable Height Folding High Chair", 3, 210.0),
    ],
    "Crib": [
        ("BRD-0022CA803780", "Larchwood Living Harebell Teething Rail Convertible Crib", 2, 360.0),
        ("BRD-00C883D56F95", "Cobble & Kiln Starling Wipe-Clean Standard Crib", 2, 200.0),
        ("BRD-01A4D62AE89F", "Larchwood Living Harebell Solid Wood Mini Crib", 2, 155.0),
    ],
    "Baby Monitor": [
        ("BRD-0015F68114F1", "Mirefield Naturals Firefly Sound-Activated Video Baby Monitor", 3, 220.0),
        ("BRD-00389B9778F7", "Mirefield Naturals Firefly Room Temperature Audio Baby Monitor", 3, 170.0),
        ("BRD-02DAB1B9EDF1", "Little Fernby Thimble Room Temperature Video Baby Monitor", 2, 190.0),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(gear, ptype) -> None:
    got = _golden(gear, ptype)
    assert got, ptype
    assert got == GOLDEN[ptype]
