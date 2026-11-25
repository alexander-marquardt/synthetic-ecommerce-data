"""Sewing and knitting, cut 3 (gen#1118): sewing needles, sewing pins and embroidery kits.

Cuts 1 and 2 (``tests/test_retail_sewing_1118.py``, ``tests/test_retail_sewing_cut2_1118.py``) put
thread, yarn, fabric, sewing machines, knitting needles and crochet hooks under ``Office & School
> Sewing & Knitting``. A shopper with thread still found no needle to sew it by hand, no pin to
hold a hem and no embroidery kit. This cut adds the last three types the issue names:
``type_specs/sewing_needles.py``, ``sewing_pins.py`` and ``embroidery_kit.py``, drawn by
:mod:`kit_sewing_notions`. The checks hold the cut's Done-when. The ceiling build carries each
type in its leaf, derived as well as authored, with the six main colors. Each type has unique ids
and titles, drawings that follow the stated values, and its decoys.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, line_grammar, scale, type_registry

ROOT = "Office & School"
NODE = "Sewing & Knitting"
#: Each type, its spec key and its leaf.
TYPES = {
    "Sewing Needles": ("sewing_needles", "Sewing Needles"),
    "Sewing Pins": ("sewing_pins", "Sewing Pins"),
    "Embroidery Kit": ("embroidery_kit", "Embroidery Kits"),
}
MAIN = {"Red", "Blue", "Green", "Yellow", "Black", "White"}
#: The cut's floor at the ceiling build. Cuts 1 and 2 passed the issue's +900, and this cut is the
#: last three types it names (the gate comment of gen#1118, cut 3).
FLOOR = 120


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


#: The attribute that states how many items one SKU holds, kept out of the title.
COUNTS = {"Sewing Needles": "needle_count", "Sewing Pins": "pin_count"}


@pytest.mark.parametrize("ptype", COUNTS)
def test_a_needle_book_or_pin_card_states_its_count_outside_its_title(cut, ptype) -> None:
    """The count of needles in a book, or of pins on a card, is an attribute, so the title's
    pack (``Single``, ``3 pack``) is the only count a pack drawing reads."""
    mine = [r for r in cut if r["product_type"] == ptype]
    assert mine
    for rec in mine:
        count = next(a for a in rec["attributes"] if a["key"] == COUNTS[ptype])
        assert int(count["value"]) > 0
        assert count["value"] not in rec["title"], rec["title"]


#: Two readings of one param that a shopper can tell apart, per type: the drawing follows each.
READINGS = {
    "sewing_needles": [("needle_kind", "sharps", "embroidery"),
                       ("needle_kind", "tapestry", "quilting")],  # fmt: skip
    "sewing_pins": [("head", "ball head", "glass head"), ("head", "ball head", "flat head")],
    "embroidery_kit": [("kit_type", "cross stitch", "stamped"), ("motif", "floral", "heart")],
}


@pytest.mark.parametrize("key", READINGS)
def test_a_param_changes_the_drawing(key) -> None:
    spec = _spec(key)
    row = spec.rows[0]
    fill = kit.Fill("solid", "#c8312e")
    base = dict(row.params)
    for param, one, other in READINGS[key]:
        first = kit.render(row.shape, fill, params={**base, param: one})
        second = kit.render(row.shape, fill, params={**base, param: other})
        assert first != second, (param, one, other)


def test_a_stamped_kit_draws_both_motifs_apart() -> None:
    fill = kit.Fill("solid", "#2f6fb3")
    heart = kit.render("embroidery_kit", fill, params={"kit_type": "stamped", "motif": "heart"})
    floral = kit.render("embroidery_kit", fill, params={"kit_type": "stamped", "motif": "floral"})
    assert heart != floral


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


def test_the_cut_takes_no_lead_word_from_another_family() -> None:
    """A lead word any template's text uses leaves its family's deal (#851), and the rest are
    dealt again, which moves other departments' goldens (cut 2's first build did)."""
    tpls = scale.templates()
    mine = [r for r in tpls if r["product_type"] in TYPES]
    rest = [r for r in tpls if r["product_type"] not in TYPES]
    leads = {
        w.lower()
        for fam in line_grammar._NUMBERED.values()
        for w in (*fam.leads, *fam.grocery_leads)
    }  # fmt: skip
    new = line_grammar.text_words(mine) - line_grammar.text_words(rest)
    assert mine and not new & leads, sorted(new & leads)
