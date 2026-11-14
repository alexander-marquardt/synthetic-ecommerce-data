"""Office & school, slices 1 and 3 (gen#969): the department, with pens, pencils, spiral
notebooks, school backpacks, colored pencils and desk organizers.

The retail catalogue had no office or school department, so a search for ``gel pens`` or ``A4
notebook`` found nothing. Slice 1 adds the department (``core/departments.RETAIL``) and its first
three types, each a spec of its own (``type_specs/pen.py``, ``pencil.py``, ``spiral_notebook.py``)
drawn by :mod:`kit_office`. Slice 3 adds the bag, art and desk types
(``type_specs/school_backpack.py``, ``colored_pencils.py``, ``desk_organizer.py``). These checks
hold the slices' Done-when: the ceiling build has each slice's share of SKUs under the department;
each type's styles have unique ids, titles and twin keys; the rows and their drawings are the same
on every call; and a golden slice pins each type's first derived styles, so a change that moves
them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core import departments
from synthetic_ecommerce_data.domains.retail import kit, office_rows, scale, type_registry

SLICE_3 = ("School Backpack", "Colored Pencils", "Desk Organizer")
TYPES = ("Pen", "Pencil", "Spiral Notebook", *SLICE_3)
KEYS = {
    "Pen": "pen",
    "Pencil": "pencil",
    "Spiral Notebook": "spiral_notebook",
    "School Backpack": "school_backpack",
    "Colored Pencils": "colored_pencils",
    "Desk Organizer": "desk_organizer",
}
#: Slice 3's share of the department at the ceiling build: the issue's 4,275 less slice 2's
#: floor of 2,850 (the gate comments of gen#969).
SLICE_3_SHARE = 1_425
#: The department's floor at the ceiling build: slice 1's 1,400 plus slice 3's share. With
#: slice 2's 1,450 it is the issue's 4,275.
FLOOR = 1_400 + SLICE_3_SHARE


@pytest.fixture(scope="module")
def office() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == office_rows.ROOT]


def test_the_department_is_on_the_closed_list() -> None:
    assert "Office & school" in departments.RETAIL
    assert office_rows.ROOT.lower() == "office & school"


def test_the_ceiling_build_holds_the_slice_floor_of_office_skus(office) -> None:
    skus = sum(r["sku_count"] for r in office)
    assert skus >= FLOOR, skus


def test_the_slice_3_types_hold_their_share_of_office_skus(office) -> None:
    skus = sum(r["sku_count"] for r in office if r["product_type"] in SLICE_3)
    assert skus >= SLICE_3_SHARE, skus


def test_the_school_backpack_is_its_own_type_apart_from_clothing_backpacks() -> None:
    specs = type_registry.specs()
    assert specs["school_backpack"].product_type == "School Backpack"
    assert specs["backpack"].department == "Clothing"


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(office) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in office if r["product_id"] in derived}
    assert kinds == set(TYPES)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(office, ptype) -> None:
    mine = [r for r in office if r["product_type"] == ptype]
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


def _golden(office: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in office if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Pen": [
        ("BRD-02FD05FA1851", "Kelfell Bold Ballpoint Pens", 9, 4.65),
        ("BRD-0AEED8938A93", "Wesbury Bold Rollerball Pens", 18, 5.5),
        ("BRD-1154563F036E", "Glenbank Fine Rollerball Pens", 18, 5.5),
    ],
    "Pencil": [
        ("BRD-00177A9CA748", "Birkhaugh 2B Pencils with Eraser", 15, 1.9),
        ("BRD-14C1085C8C1C", "Hamgarth 2H Pencils with Eraser", 18, 2.05),
        ("BRD-16AF6C00FB2D", "Foxgarth 4B Drawing Pencils", 18, 2.9),
    ],
    "Spiral Notebook": [
        ("BRD-082994CBD41A", "Brackbank A5 Dotted Spiral Notebook", 6, 2.9),
        ("BRD-15F48D958E7F", "Edenworth A5 Lined Spiral Notebook", 6, 3.95),
        ("BRD-29026ABE797F", "Sandlow B5 Squared Spiral Notebook", 9, 3.4),
    ],
    "School Backpack": [
        ("BRD-01411C4BDEDE", "Duning 25 L Laptop School Backpack", 6, 29.0),
        ("BRD-049244973B0D", "Eskcombe 20 L Laptop School Backpack", 2, 33.0),
        ("BRD-063E22A16FA7", "Whitwick 15 L Laptop School Backpack", 5, 14.0),
    ],
    "Colored Pencils": [
        ("BRD-0134D243DE3D", "Ravscar 48 Classic Colored Pencils", 12, 25.0),
        ("BRD-0705C812EEC2", "Irebridge 36 Erasable Colored Pencils", 6, 6.5),
        ("BRD-0C433A3C151E", "Kencombe 48 Soft Core Colored Pencils", 6, 23.0),
    ],
    "Desk Organizer": [
        ("BRD-02B2BA130207", "Stokemouth 5 Compartment Metal Desk Organizer", 18, 8.5),
        ("BRD-045FA7902BD2", "Rambeck 3 Compartment Plastic Desk Organizer", 18, 11.5),
        ("BRD-07CCBFCDDC17", "Readale 6 Compartment Mesh Desk Organizer", 15, 9.0),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(office, ptype) -> None:
    assert _golden(office, ptype) == GOLDEN[ptype]
