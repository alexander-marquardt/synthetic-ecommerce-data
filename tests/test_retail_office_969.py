"""Office & school, slices 1 and 2 (gen#969): the department, with pens, pencils, spiral
notebooks, ring binders, document folders and calculators.

The retail catalogue had no office or school department, so a search for ``gel pens`` or ``A4
notebook`` found nothing. Slice 1 adds the department (``core/departments.RETAIL``) and its first
three types, each a spec of its own (``type_specs/pen.py``, ``pencil.py``, ``spiral_notebook.py``)
drawn by :mod:`kit_office`. Slice 2 adds the filing and desk types (``type_specs/ring_binder.py``,
``document_folder.py``, ``calculator.py``). These checks hold the slices' Done-when: the ceiling
build has at least 2,850 SKUs under the department; each type's styles have unique ids, titles
and twin keys; the rows and their drawings are the same on every call; and a golden slice pins
each type's first derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core import departments
from synthetic_ecommerce_data.domains.retail import kit, office_rows, scale, type_registry

TYPES = ("Pen", "Pencil", "Spiral Notebook", "Ring Binder", "Document Folder", "Calculator")
KEYS = {
    "Pen": "pen", "Pencil": "pencil", "Spiral Notebook": "spiral_notebook",
    "Ring Binder": "ring_binder", "Document Folder": "document_folder", "Calculator": "calculator",
}  # fmt: skip
#: Slice 2's floor at the ceiling build (the gate comment of gen#969): 1,400 for slice 1, plus
#: 1,450 for ring binders, document folders and calculators.
FLOOR = 2_850


@pytest.fixture(scope="module")
def office() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == office_rows.ROOT]


def test_the_department_is_on_the_closed_list() -> None:
    assert "Office & school" in departments.RETAIL
    assert office_rows.ROOT.lower() == "office & school"


def test_the_ceiling_build_holds_the_slice_floor_of_office_skus(office) -> None:
    skus = sum(r["sku_count"] for r in office)
    assert skus >= FLOOR, skus


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
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(office, ptype) -> None:
    assert _golden(office, ptype) == GOLDEN[ptype]
