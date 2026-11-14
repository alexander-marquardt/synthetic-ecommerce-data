"""Bedding and food storage, slice 2 of gen#963: sheet sets, pillows and food storage containers.

``Home > Bedding`` sold no sheet set, one pillow style of 2 SKUs, and no food storage container,
so a search for ``sheets``, ``pillow`` or ``food storage`` found almost nothing. Slice 2 adds
three derivable types, each a spec of its own (``type_specs/bed_sheet.py``, ``pillow.py``,
``food_storage_container.py``); :mod:`kit_bedding_storage` draws the sheet set and the
containers, and the kit's ``pillow`` shape the pillows. These checks hold the slice's Done-when
(the gate comments of gen#963): the ceiling build has at least 20,400 SKUs under ``Home``; each
type's styles have unique ids, titles, twin keys and SKU ids; the rows and their drawings are the
same on every call; a material draws apart; and a golden slice pins each type's first derived
styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

ROOT = "Home"
#: Each type, its spec key and the category under ``Home`` it sits in.
TYPES = {
    "Sheet Set": ("bed_sheet", "Bedding"),
    "Pillow": ("pillow", "Bedding"),
    "Food Storage Container": ("food_storage_container", "Storage"),
}
#: The slice's floor at the ceiling build (the gate comment of gen#963; main held 14,059).
FLOOR = 20_400


@pytest.fixture(scope="module")
def home() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == ROOT]


def test_the_ceiling_build_holds_the_slice_floor_of_home_skus(home) -> None:
    skus = sum(r["sku_count"] for r in home)
    assert skus >= FLOOR, skus


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_is_derived_under_its_category(home, ptype) -> None:
    derived = set(ceiling_build().template_of)
    mine = [r for r in home if r["product_type"] == ptype]
    assert any(r["product_id"] in derived for r in mine)
    assert {r["category_path"][1] for r in mine} == {TYPES[ptype][1]}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(home, ptype) -> None:
    mine = [r for r in home if r["product_type"] == ptype]
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
    spec = type_registry.specs()[TYPES[ptype][0]]
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


@pytest.mark.parametrize("shape", ["sheet_set", "food_storage"])
def test_each_material_draws_apart(shape) -> None:
    rows = [r for s in type_registry.specs().values() for r in s.rows if r.shape == shape]
    fill = kit.Fill("solid", "#123456", "#654321")
    kinds = {dict(r.params)["kind"] for r in rows}
    assert len(kinds) >= 4
    drawn = {kit.render(shape, fill, params={"kind": k}) for k in kinds}
    assert len(drawn) == len(kinds)


def test_a_pillow_keeps_its_white_cover(home) -> None:
    colors = {s["color"] for r in home if r["product_type"] == "Pillow" for s in r["skus"]}
    assert colors == {"White"}


def _golden(home: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in home if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Sheet Set": [
        ("BRD-03493FD968A6",
         "Harbour & Pine Hush Extra Deep Pocket Microfiber Sheet Set", 24, 36.0),
        ("BRD-0504EEF40C88", "Alderwick Living Cloud Deep Pocket Bamboo Sheet Set", 24, 40.0),
        ("BRD-06938AB61FD2", "Brackenmere Home Nightcap Deep Pocket Flannel Sheet Set", 8, 76.0),
    ],
    "Pillow": [
        ("BRD-02444678A084", "Calderby & Lune Eiderdown Firm Cooling Gel Pillow", 2, 34.0),
        ("BRD-0308F0BA8C1F", "Brackenmere Home Nightcap Medium Feather Pillow", 2, 17.0),
        ("BRD-0375EA18ECDD", "Lanternby Slumber Plush Memory Foam Pillow", 2, 34.0),
    ],
    "Food Storage Container": [
        ("BRD-0405D7AD0731", "Cobble & Kiln Stash Leakproof Glass Food Storage Container", 6, 30.0),
        ("BRD-07FD859A8696",
         "Alderwick Living Haul Vented Silicone Food Storage Container", 18, 16.5),
        ("BRD-08883E193B9D",
         "Harbour & Pine Alcove Airtight Plastic Food Storage Container", 9, 33.0),
    ],
}  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(home, ptype) -> None:
    assert _golden(home, ptype) == GOLDEN[ptype]
