"""Mens elasticated-waist trousers: a leaf, a floor and the text-match decoys (gen#329).

The probe of 2026-10-15 found no trouser that states an elasticated waist, so the "garment
attribute treated as keyword" class had no data. This slice adds the leaf
``Mens/Trousers/Elasticated Waist Trousers`` and, for the same type, three decoys of each of the
seven gen#294 classes. The floors and the expected decoy words are written out here, not read
from the rows module, so dropping rows or a decoy class from the module fails this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import needs_rows  # noqa: E402
import scale  # noqa: E402

LEAF = ("Mens", "Trousers", "Elasticated Waist Trousers")
#: Distinct products in the leaf that are not decoys: the ranking needs real ones to choose from.
REAL_FLOOR = 12
MAIN = ("Red", "Blue", "Green", "Yellow", "Black", "White")
CLASSES = (1, 2, 3, 4, 5, 6, 7)
#: The words a class-4 decoy names: an elastic that is NOT at the waist.
NOT_AT_THE_WAIST = ("elasticated cuff", "elasticated hem", "elasticated ankle")


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def decoys(templates) -> list[tuple]:
    """Each decoy with its SHIPPED template (after ``main_colors.complete``)."""
    by_id = {r["product_id"]: r for r in templates}
    return [(d, by_id[f"BRD-{d.code}"]) for d in needs_rows.TABLE]


def _attr(rec: dict, key: str) -> list[str]:
    return [a["value"] for a in rec["attributes"] if a["key"] == key]


def _real_in_leaf(templates) -> list[dict]:
    decoy_ids = {f"BRD-{d.code}" for d in needs_rows.TABLE}
    return [r for r in templates
            if tuple(r["category_path"]) == LEAF and r["product_id"] not in decoy_ids]


def test_the_leaf_holds_a_floor_of_real_products(templates):
    ids = {r["product_id"] for r in _real_in_leaf(templates)}
    assert len(ids) >= REAL_FLOOR, len(ids)


def test_every_product_in_the_leaf_states_an_elastic_waist(templates):
    leaf = [r for r in templates if tuple(r["category_path"]) == LEAF]
    assert leaf
    for r in leaf:
        assert _attr(r, "waist_type") == ["Elastic"], r["product_id"]
        assert "elasticated waist" in r["title"].lower(), r["title"]


def test_the_leaf_products_are_drawn_with_an_elasticated_waist(templates):
    real = _real_in_leaf(templates)
    assert real
    for r in real:
        assert r["drawing"]["params"].get("waist") == "elasticated", r["product_id"]


def test_the_leaf_offers_the_main_colors(templates):
    colors = {s["color"] for r in _real_in_leaf(templates) for s in r["skus"]}
    assert set(MAIN) <= colors, sorted(set(MAIN) - colors)


def test_the_real_products_are_mens_trousers_with_unique_titles(templates):
    real = _real_in_leaf(templates)
    assert real
    assert {r["product_type"] for r in real} == {"Mens Trousers"}
    titles = [r["title"] for r in real]
    assert len(set(titles)) == len(titles)


@pytest.mark.parametrize("klass", CLASSES)
def test_there_are_three_decoys_of_each_class(klass):
    n = sum(1 for d in needs_rows.TABLE if d.klass == klass)
    assert n >= 3, n


def test_a_decoy_is_a_mens_trouser_true_in_its_fields(decoys):
    assert decoys
    for d, rec in decoys:
        assert rec["product_type"] == "Mens Trousers", d.code
        assert rec["category_path"][0] == "Mens", d.code
        assert {s["color"] for s in rec["skus"]} == {d.color}, d.code


def test_class_4_names_an_elastic_that_is_not_the_waist_and_sits_elsewhere(decoys):
    assert decoys
    seen = set()
    for d, rec in decoys:
        if d.klass == 4:
            title = rec["title"].lower()
            hit = [w for w in NOT_AT_THE_WAIST if w in title]
            assert hit, rec["title"]
            seen.update(hit)
            assert tuple(rec["category_path"]) != LEAF, d.code
            assert "elastic" not in _attr(rec, "waist_type"), d.code
            assert "elasticated waist" not in title, d.code
    assert seen == set(NOT_AT_THE_WAIST)


def test_class_1_and_6_name_a_main_color_that_is_not_the_products(decoys):
    assert decoys
    for d, rec in decoys:
        if d.klass in (1, 6):
            assert d.word in MAIN and d.word != d.color, d.code
            assert d.word.lower() in rec["title"].lower(), d.code
        if d.klass == 6:
            assert d.color.lower() not in rec["title"].lower(), d.code
            assert len(rec["title"].split()) <= 5, rec["title"]


def test_class_5_spells_the_shade_only_in_the_description(decoys):
    assert decoys
    for d, rec in decoys:
        if d.klass == 5:
            assert d.color.lower() in ("ivory", "cream", "off white")
            assert d.color.lower() not in rec["title"].lower(), d.code
            assert d.color.lower() in rec["description"].lower(), d.code


def test_class_7_brand_is_the_brand_field_and_in_the_short_title(decoys):
    assert decoys
    for d, rec in decoys:
        if d.klass == 7:
            assert rec["brand"] == d.word, d.code
            assert d.word in rec["title"] and len(rec["title"].split()) <= 5, d.code


def test_the_table_lists_every_decoy_once_with_a_query_and_a_policy():
    assert needs_rows.TABLE
    codes = [d.code for d in needs_rows.TABLE]
    assert len(codes) == len(set(codes))
    assert all(d.query and d.policy for d in needs_rows.TABLE)


def test_every_row_is_a_template_no_derived_style_copies(templates):
    ids = {r["product_id"] for r in needs_rows.docs()}
    assert ids
    assert ids <= {r["product_id"] for r in templates}
    assert ids <= scale.NEEDS_IDS
