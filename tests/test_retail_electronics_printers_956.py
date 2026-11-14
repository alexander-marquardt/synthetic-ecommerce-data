"""Electronics printers and ink, slice 3b (gen#956): printers and ink cartridges.

At the ceiling build the Electronics department held 1,166 SKUs. The 500K mix plans 14,000
(``docs/catalogue-mix-837.md``). A shopper who searched for a printer or for ink found nothing.
Slice 3b adds two derivable types: ``Electronics > Printers > Printers`` and
``Printers > Ink Cartridges``. Each is a spec of its own (``type_specs/printer.py``,
``ink_cartridge.py``), drawn by :mod:`kit_printers`.

These checks hold the slice's Done-when, from the gate comments of gen#956:

- On their own, the two types add at least 230 SKUs to the ceiling build, so the slice holds
  whether or not slices 1, 2a, 2b and 3a are merged first. With them, the department reaches the
  issue's 14,000 target.
- Each type holds between 350 and 600 SKUs.
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
    "Printer": ("printer", ("Printers", "Printers")),
    "Ink Cartridge": ("ink_cartridge", ("Printers", "Ink Cartridges")),
}
#: What the slice adds at the ceiling build on its own (the gate comment of gen#956).
FLOOR = 230
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


def test_a_derived_ink_title_keeps_the_case_of_xl(electronics) -> None:
    titles = [r["title"] for r in electronics if r["product_type"] == "Ink Cartridge"]
    assert any("XL" in t.split() for t in titles)
    assert not [t for t in titles if "xl" in t.lower().split() and "XL" not in t.split()]


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
        ("printer", {"printer_type": "inkjet"}, {"printer_type": "laser"}),
        ("printer", {"printer_function": "multifunction"}, {"printer_function": "photo"}),
        ("ink_cartridge", {"ink_yield": "standard"}, {"ink_yield": "xl"}),
        ("ink_cartridge", {"ink_formula": "dye"}, {"ink_formula": "pigment"}),
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
    "Printer": [
        ("BRD-0206A3C29992", "Thornside Laser Photo Printer", 2, 270.0),
        ("BRD-0230D119E7A4", "Tanridge Laser Multifunction Printer", 6, 220.0),
        ("BRD-024FA5CEDC39", "Easshaw Inkjet Photo Printer", 6, 135.0),
    ],
    "Ink Cartridge": [
        ("BRD-033A01D781CE", "Ludwyke Standard Dye Ink Cartridge", 6, 41.0),
        ("BRD-043A22B65182", "Rambridge XL Ink Cartridge", 6, 17.0),
        ("BRD-0529840C833B", "Whitlow Standard Ink Cartridge", 6, 34.0),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(electronics, ptype) -> None:
    assert _golden(electronics, ptype) == GOLDEN[ptype]
