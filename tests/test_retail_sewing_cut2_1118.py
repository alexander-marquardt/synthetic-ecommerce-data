"""Sewing and knitting, cut 2 (gen#1118): sewing machines, knitting needles and crochet hooks.

Cut 1 (``tests/test_retail_sewing_1118.py``) put thread, yarn and fabric under ``Office & School >
Sewing & Knitting``. A shopper who found the yarn still found nothing to knit it with, and the
range had no machine to sew the thread. This cut adds three types: ``type_specs/sewing_machine.py``,
``knitting_needles.py`` and ``crochet_hook.py``, drawn by :mod:`kit_sewing_tools`. The checks
hold the cut's Done-when. The ceiling build carries each type in its leaf, derived as well as
authored, with the six main colors. A needle or a hook is sold by its size in millimeters, a
measured axis whose rungs draw apart. Each type has unique ids and titles, drawings that follow
the stated values, and its decoys.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, size_ladder, type_registry

ROOT = "Office & School"
NODE = "Sewing & Knitting"
#: Each type, its spec key and its leaf.
TYPES = {
    "Sewing Machine": ("sewing_machine", "Sewing Machines"),
    "Knitting Needles": ("knitting_needles", "Knitting Needles"),
    "Crochet Hook": ("crochet_hook", "Crochet Hooks"),
}
#: The measured SKU axis of a needle and a hook: its key, the option's entry key and its sizes.
SIZED = {
    "Knitting Needles": ("needle_mm", "needle_size"),
    "Crochet Hook": ("hook_mm", "hook_size"),
}
MAIN = {"Red", "Blue", "Green", "Yellow", "Black", "White"}
#: The cut's floor at the ceiling build. Cut 1 made 591 SKUs of the issue's +900, and this cut is
#: three of the five types left (the gate comment of gen#1118, cut 2).
FLOOR = 150


@pytest.fixture(scope="module")
def cut() -> list[dict]:
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
    assert len({r.brand for r in spec.rows}) >= 2


def test_the_ceiling_build_holds_the_cut_floor_of_skus(cut) -> None:
    skus = sum(r["sku_count"] for r in cut)
    assert skus >= FLOOR, skus
    assert {r["product_type"] for r in cut} == set(TYPES)


def test_every_type_of_the_cut_is_derived_in_the_ceiling_build(cut) -> None:
    derived = set(ceiling_build().template_of)
    assert {r["product_type"] for r in cut if r["product_id"] in derived} == set(TYPES)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_offers_the_six_main_colors(cut, ptype) -> None:
    colors = {s["color"] for r in cut if r["product_type"] == ptype for s in r["skus"]}
    assert colors >= MAIN, MAIN - colors


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(cut, ptype) -> None:
    mine = [r for r in cut if r["product_type"] == ptype]
    assert mine
    for field in ("product_id", "title"):
        repeats = [v for v, n in collections.Counter(r[field] for r in mine).items() if n > 1]
        assert repeats == [], field
    twins = [k for k, n in collections.Counter(scale.twin_key(r) for r in mine).items() if n > 1]
    assert twins == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert len(skus) == len(set(skus))


@pytest.mark.parametrize("ptype", SIZED)
def test_a_needle_or_hook_is_sold_by_its_size_in_millimeters(cut, ptype) -> None:
    key, entry = SIZED[ptype]
    (option,) = [o for o in _spec(TYPES[ptype][0]).options if o.option == key]
    assert (option.key, option.unit) == (entry, "MMT")
    mine = [r for r in cut if r["product_type"] == ptype]
    assert mine
    for rec in mine:
        sizes = {float(s[key]) for s in rec["skus"]}
        assert len(sizes) >= 3, (rec["product_id"], sizes)
        assert all(2.0 <= mm <= 12.0 for mm in sizes), (rec["product_id"], sizes)
        hero = rec["skus"][0]["color"]
        scales = [
            size_ladder.size_scale(rec, s)
            for s in sorted(
                (s for s in rec["skus"] if s["color"] == hero), key=lambda s: float(s[key])
            )
        ]
        assert scales == sorted(scales) and scales[0] < scales[-1], (rec["product_id"], scales)


def test_a_sewing_machine_is_sold_singly_and_states_its_stitches(cut) -> None:
    machines = [r for r in cut if r["product_type"] == "Sewing Machine"]
    assert machines
    for rec in machines:
        assert {s["pack_size"] for s in rec["skus"]} == {"Single"}
        stitches = next(a for a in rec["attributes"] if a["key"] == "built_in_stitches")
        assert int(stitches["value"]) > 0


#: Two readings of one param that a shopper can tell apart, per type: the drawing follows each.
READINGS = {
    "sewing_machine": ("machine_type", "mechanical", "computerized"),
    "knitting_needles": ("needle_type", "straight", "circular"),
    "crochet_hook": ("handle", "inline", "soft grip"),
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
def test_each_param_is_the_lower_cased_value_of_an_attribute(key) -> None:
    for row in _spec(key).rows:
        values = {str(a[2]).lower() for a in row.attrs}
        assert {v for _, v in row.params} <= values, (row.code, row.params)


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
