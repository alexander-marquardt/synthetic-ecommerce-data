"""Mens clothing depth: product floors per leaf and text-match decoys per type (gen#310).

The Mens tree held no trousers, polo shirts, coats, jackets or tailoring, three products per
shirt leaf and a handful of underwear and socks. This slice adds them. The floors and the
expected decoy words are written out here, not read from the rows module, so dropping rows or
a decoy class from the module fails this file.

The counts are taken over :func:`scale.templates`: every row is a template, and a derived style
only adds to them, so a floor met here is met by the ceiling build.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import house_styles  # noqa: E402
import mens_depth_rows  # noqa: E402
import scale  # noqa: E402

#: group -> (category path prefixes, the floor of distinct products), from the issue.
FLOORS = {
    "trousers and chinos": ((("Men", "Trousers"),), 80),
    "shirts": ((("Men", "Tops", "Shirts"),), 120),
    "polo shirts": ((("Men", "Tops", "Polo Shirts"),), 50),
    "coats and jackets": ((("Men", "Coats & Jackets"),), 80),
    "suits, blazers and tailoring": ((("Men", "Suits & Tailoring"),), 60),
    "underwear and socks": ((("Men", "Underwear"), ("Men", "Socks")), 60),
}
#: The product types that carry decoys, and the five-plus-two classes each carries.
TYPES = ("Trousers", "Shirt", "Polo Shirt", "Coat", "Jacket", "Suit Jacket", "Boxers", "Socks")
CLASSES = (1, 2, 3, 4, 5, 6, 7)
MAIN = ("Red", "Blue", "Green", "Yellow", "Black", "White")
#: The invented brands of class 7: each holds a color or category word.
BRANDS = ("Black Curlew", "Yellow Plover", "Jacket Wren")
#: Other categories' nouns a class-2 title may borrow.
CATEGORY_NOUNS = ("dress", "jumper", "coat", "blazer", "shirt", "trouser", "sock", "boot", "boxer")
AUDIENCE_WORDS = ("women", "boyfriend", "kids", "boys", "girls", "mini-me")
NEAR_WHITE = ("ivory", "cream", "off white")


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def decoys() -> list[tuple]:
    return [(d, next(r for r in mens_depth_rows.docs() if r["product_id"] == f"BRD-{d.code}"))
            for d in mens_depth_rows.TABLE]


def _under(rec: dict, prefixes) -> bool:
    return any(tuple(rec["category_path"][: len(p)]) == p for p in prefixes)


@pytest.mark.parametrize("group", FLOORS)
def test_every_group_meets_its_product_floor(templates, group):
    prefixes, floor = FLOORS[group]
    n = len({r["product_id"] for r in templates if _under(r, prefixes)})
    assert n >= floor, f"{group}: {n} products, floor {floor}"


def test_no_mens_knitwear_is_added_here(templates):
    """Knitwear is gen#309's, a sibling slice."""
    mine = {r["product_id"] for r in mens_depth_rows.docs()}
    assert mine
    knit = [r for r in templates if r["product_id"] in mine and "Knitwear" in r["category_path"]]
    assert not knit


def test_every_row_is_mens_and_unique(templates):
    docs = mens_depth_rows.docs()
    assert docs
    assert {r["category_path"][0] for r in docs} == {"Men"}
    assert len({r["product_id"] for r in docs}) == len(docs)
    assert len({r["title"] for r in docs}) == len(docs)
    assert {r["product_id"] for r in docs} <= scale.MENS_DEPTH_IDS


def test_every_row_is_a_template_no_derived_style_copies(templates):
    ids = {r["product_id"] for r in mens_depth_rows.docs()}
    assert ids <= {r["product_id"] for r in templates}


@pytest.mark.parametrize("ptype", TYPES)
@pytest.mark.parametrize("klass", CLASSES)
def test_each_type_has_three_decoys_of_each_class(ptype, klass):
    n = sum(1 for d in mens_depth_rows.TABLE if d.ptype == ptype and d.klass == klass)
    assert n >= 3


def test_a_decoy_is_a_product_of_its_type_and_true_in_its_fields(decoys):
    assert decoys
    for d, rec in decoys:
        assert rec["product_type"] == d.ptype, d.code
        colors = {s["color"] for s in rec["skus"]}
        assert colors == {d.color}, (d.code, colors)
        assert rec["category_path"][0] == "Men", d.code


def test_class_1_and_6_name_a_main_color_that_is_not_the_products(decoys):
    for d, rec in decoys:
        if d.klass in (1, 6):
            assert d.word in MAIN and d.word != d.color, d.code
            assert d.word.lower() in rec["title"].lower(), d.code
        if d.klass == 1:
            assert d.color.lower() in rec["title"].lower(), d.code
        if d.klass == 6:
            assert d.color.lower() not in rec["title"].lower(), d.code


def test_class_6_sits_in_a_short_title_and_names_its_range(decoys):
    for d, rec in decoys:
        if d.klass == 6:
            assert len(rec["title"].split()) <= 5, rec["title"]
            assert "range" in rec["description"].lower(), d.code


def test_class_2_borrows_another_categorys_noun_and_class_3_an_audience_word(decoys):
    own = {"Trousers": "chinos", "Shirt": "shirt", "Polo Shirt": "polo", "Coat": "coat",
           "Jacket": "jacket", "Suit Jacket": "blazer", "Boxers": "boxers", "Socks": "socks"}
    for d, rec in decoys:
        t = rec["title"].lower()
        if d.klass == 2:
            assert d.word in CATEGORY_NOUNS and d.word in t, d.code
            assert d.word not in own[d.ptype], d.code
        if d.klass == 3:
            assert any(w in t for w in AUDIENCE_WORDS), d.code
            assert rec["category_path"][0] == "Men", d.code


def test_class_4_names_a_feature_the_material_lacks(decoys):
    for d, rec in decoys:
        if d.klass == 4:
            stem = d.word.split("-")[0].lower()
            assert stem in rec["title"].lower(), d.code
            material = " ".join(
                a["value"].lower() for a in rec["attributes"] if a["key"] == "material"
            )
            assert material and stem not in material, (d.code, material)


def test_class_5_spells_the_shade_only_in_the_description(decoys):
    for d, rec in decoys:
        if d.klass == 5:
            assert d.color.lower() in NEAR_WHITE
            assert d.color.lower() not in rec["title"].lower(), d.code
            assert d.color.lower() in rec["description"].lower(), d.code


def test_class_7_brand_is_in_the_brand_field_and_the_short_title(decoys):
    seen = set()
    for d, rec in decoys:
        if d.klass == 7:
            assert rec["brand"] == d.word and d.word in BRANDS, d.code
            assert d.word in rec["title"] and len(rec["title"].split()) <= 5, d.code
            seen.add(d.word)
    assert seen == set(BRANDS)


@pytest.mark.parametrize("brand", BRANDS)
def test_each_new_brand_has_its_own_house_style_and_logo_name(brand):
    style = house_styles.HOUSE_STYLES.get(brand)
    assert style is not None
    others = [s for b, s in house_styles.HOUSE_STYLES.items() if b != brand]
    assert style.mark not in {s.mark for s in others}
    assert house_styles.lockup_key(style) not in {house_styles.lockup_key(s) for s in others}
    assert style.color


def test_the_table_lists_every_decoy_once(decoys):
    codes = [d.code for d in mens_depth_rows.TABLE]
    assert len(codes) == len(set(codes))
    assert all(d.query and d.policy for d in mens_depth_rows.TABLE)
