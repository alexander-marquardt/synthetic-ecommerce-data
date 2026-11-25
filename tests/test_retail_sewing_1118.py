"""Sewing and knitting, cut 1 (gen#1118): sewing thread, yarn and fabric in Office & School.

The retail domain held no sewing machine, thread, fabric, yarn or needle, so a shopper's
``thread`` found only the industrial catalogue's threaded rods, taps and fasteners. This cut adds
the three types the issue's title names first, each a spec of its own (``type_specs/
sewing_thread.py``, ``yarn.py``, ``fabric.py``) drawn by :mod:`kit_sewing`, under ``Office &
School > Sewing & Knitting``. These checks hold the cut's Done-when: the ceiling build carries
each type in its leaf, derived as well as authored, with the six main colors, its measured or
named SKU axis, unique ids and titles, drawings that follow the stated values, and the decoys.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

ROOT = "Office & School"
NODE = "Sewing & Knitting"
#: Each type, its spec key and its leaf.
TYPES = {
    "Sewing Thread": ("sewing_thread", "Sewing Thread"),
    "Yarn": ("yarn", "Yarn"),
    "Fabric": ("fabric", "Fabric"),
}
MAIN = {"Red", "Blue", "Green", "Yellow", "Black", "White"}
#: The cut's floor at the ceiling build: about three eighths of the issue's +900, for three of
#: its eight types (the gate comment of gen#1118).
FLOOR = 340


@pytest.fixture(scope="module")
def sewing() -> list[dict]:
    # the node also holds cut 2's tools (tests/test_retail_sewing_cut2_1118.py)
    records = ceiling_build().records
    return [r for r in records if tuple(r["category_path"][:2]) == (ROOT, NODE)
            and r["product_type"] in TYPES]  # fmt: skip


def _spec(key: str) -> type_registry.TypeSpec:
    specs = type_registry.specs()
    assert key in specs, f"no spec {key}"
    return specs[key]


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_is_a_spec_in_its_sewing_leaf(ptype) -> None:
    key, leaf = TYPES[ptype]
    spec = _spec(key)
    assert spec.product_type == ptype
    assert spec.department == "Office & Stationery"
    assert spec.derivable
    assert {r.path for r in spec.rows} == {(ROOT, NODE, leaf)}


def test_the_ceiling_build_holds_the_cut_floor_of_sewing_skus(sewing) -> None:
    skus = sum(r["sku_count"] for r in sewing)
    assert skus >= FLOOR, skus
    assert {r["product_type"] for r in sewing} == set(TYPES)


def test_every_type_of_the_cut_is_derived_in_the_ceiling_build(sewing) -> None:
    derived = set(ceiling_build().template_of)
    assert {r["product_type"] for r in sewing if r["product_id"] in derived} == set(TYPES)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_offers_the_six_main_colors(sewing, ptype) -> None:
    colors = {s["color"] for r in sewing if r["product_type"] == ptype for s in r["skus"]}
    assert colors >= MAIN, MAIN - colors


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(sewing, ptype) -> None:
    mine = [r for r in sewing if r["product_type"] == ptype]
    assert mine
    for field in ("product_id", "title"):
        repeats = [v for v, n in collections.Counter(r[field] for r in mine).items() if n > 1]
        assert repeats == [], field
    twins = [k for k, n in collections.Counter(scale.twin_key(r) for r in mine).items() if n > 1]
    assert twins == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert len(skus) == len(set(skus))


def _attr(rec: dict, key: str) -> dict:
    return next(a for a in rec["attributes"] if a["key"] == key)


def test_a_thread_states_its_spool_length_in_meters_and_its_title_reads_it(sewing) -> None:
    threads = [r for r in sewing if r["product_type"] == "Sewing Thread"]
    assert threads
    for rec in threads:
        length = _attr(rec, "spool_length")
        assert length["unit_code"] == "MTR"
        assert length["value_canonical"] == float(length["value"]) * 1000
        assert f"{length['value']} m " in rec["title"], rec["title"]


def test_a_fabric_is_sold_by_the_cut_from_a_fat_quarter_to_meters(sewing) -> None:
    fabrics = [r for r in sewing if r["product_type"] == "Fabric"]
    assert fabrics
    for rec in fabrics:
        cuts = [s["fabric_cut"] for s in rec["skus"]]
        assert "Fat Quarter" in cuts and "1 Meter" in cuts, cuts
        hero = rec["skus"][0]["color"]
        price = {s["fabric_cut"]: s["price"] for s in rec["skus"] if s["color"] == hero}
        assert price["Fat Quarter"] < price["1 Meter"] < price["2 Meters"], price


def test_a_yarn_is_sold_by_the_ball_in_packs(sewing) -> None:
    yarns = [r for r in sewing if r["product_type"] == "Yarn"]
    assert yarns
    for rec in yarns:
        assert {s["pack_size"] for s in rec["skus"]} == {"Single", "5 pack", "10 pack"}
        assert _attr(rec, "yarn_weight")["value"] in {"4 Ply", "DK", "Aran", "Chunky"}


#: Two readings of one param that a shopper can tell apart, per type: the drawing follows each.
READINGS = {
    "sewing_thread": ("spool_length", "100", "1000"),
    "yarn": ("yarn_weight", "4 ply", "chunky"),
    "fabric": ("style", "poplin", "canvas"),
}


@pytest.mark.parametrize("key", READINGS)
def test_a_param_changes_the_drawing(key) -> None:
    spec = _spec(key)
    param, one, other = READINGS[key]
    row = spec.rows[0]
    fill = kit.Fill("solid", "#c8312e")
    base = dict(row.params)
    first = kit.render(row.shape, fill, params={**base, param: one})
    second = kit.render(row.shape, fill, params={**base, param: other})
    assert first != second


@pytest.mark.parametrize("key", READINGS)
def test_each_type_rows_and_drawings_are_deterministic(key) -> None:
    spec = _spec(key)
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


@pytest.mark.parametrize("key", READINGS)
def test_each_type_carries_a_part_color_and_a_range_name_decoy(key) -> None:
    spec = _spec(key)
    assert sorted(d.cls for d in spec.decoys) == [4, 6]
    for decoy in spec.decoys:
        (color,) = decoy.row.colors
        word = decoy.query.split()[0].capitalize()
        assert word in MAIN and word in decoy.row.title and color[0] != word, decoy.row.title


def test_the_red_thread_decoy_is_white_thread_on_a_red_spool() -> None:
    (decoy,) = [d for d in _spec("sewing_thread").decoys if d.cls == 4]
    assert decoy.query == "red sewing thread"
    assert decoy.row.colors[0][0] == "White"
    assert "Red Spool" in decoy.row.title
