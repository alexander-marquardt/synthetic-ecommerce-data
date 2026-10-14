"""Knitwear depth: products per style and material, near-white shades and decoys (gen#309).

Knitwear held 16 products. A knitwear query ("ladies white jumper", "mens navy v neck jumper",
"cashmere cardigan") had a handful to choose between. This slice adds distinct PRODUCTS (a style
is a product; its colors times its sizes are its SKUs), not sizes. The floors and the expected
decoy words are written out here, not read from the rows module, so dropping rows or a decoy
class from the module fails this file.

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
import knitwear_rows  # noqa: E402
import scale  # noqa: E402

#: root -> (floor of distinct knitwear products, floor without decoys), from the issue.
FLOORS = {"Women": (150, 120), "Men": (100, 80)}
#: The styles a root's knitwear carries (the `knit_style` attribute) and the materials.
STYLES = {
    "Women": ("Crew Neck", "V Neck", "Roll Neck", "Turtle Neck", "Cable Knit", "Half Zip",
              "Boat Neck", "Button Front", "Longline", "Cropped", "Tank Top", "Slipover"),
    "Men": ("Crew Neck", "V Neck", "Roll Neck", "Cable Knit", "Half Zip", "Quarter Zip",
            "Button Front", "Zip Through", "Shawl Collar", "Slipover"),
}
MATERIALS = ("cashmere", "merino", "lambswool", "cotton", "wool blend", "recycled", "acrylic")
TYPES = ("Jumper", "Cardigan", "Knitted Top")
CLASSES = (1, 2, 3, 4, 5, 6, 7)
MAIN = ("Red", "Blue", "Green", "Yellow", "Black", "White")
NEAR_WHITE = ("cream", "ivory", "off white", "ecru")
BRANDS = ("White Heron", "Red Kite", "Cardigan Finch")
CATEGORY_NOUNS = ("dress", "coat", "trouser", "shirt", "sock", "blazer", "skirt", "boot")
AUDIENCE_WORDS = ("women", "men", "boyfriend", "kids", "boys", "girls", "mini-me")
#: Necklines the knitwear carries (the existing facet's words, plus v-neck).
NECKLINES = {"crew", "v-neck", "high", "boat", "collared", "round"}


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def knit(templates) -> list[dict]:
    return [r for r in templates if r["category_path"][1:2] == ["Knitwear"]]


@pytest.fixture(scope="module")
def decoys(templates) -> list[tuple]:
    """Each decoy with its SHIPPED template: ``scale.templates()`` has already run
    ``main_colors.complete``, which is what the catalogue ships (not the module's raw docs)."""
    by_id = {r["product_id"]: r for r in templates}
    return [(d, by_id[f"BRD-{d.code}"]) for d in knitwear_rows.TABLE]


def _attr(rec: dict, key: str) -> str:
    return " ".join(a["value"] for a in rec["attributes"] if a["key"] == key)


def _real(rec: dict) -> bool:
    return rec["product_id"] not in {f"BRD-{d.code}" for d in knitwear_rows.TABLE}


@pytest.mark.parametrize("root", FLOORS)
def test_knitwear_meets_its_product_floor(knit, root):
    """The floor counts DECOYS too: a decoy is a real product with SKUs and a leaf."""
    n = len({r["product_id"] for r in knit if r["category_path"][0] == root})
    assert n >= FLOORS[root][0], f"{root}: {n} knitwear products"


@pytest.mark.parametrize("root", FLOORS)
def test_knitwear_meets_a_floor_without_its_decoys(knit, root):
    n = len({r["product_id"] for r in knit if r["category_path"][0] == root and _real(r)})
    assert n >= FLOORS[root][1], f"{root}: {n} non-decoy knitwear products"


@pytest.mark.parametrize("root", FLOORS)
def test_every_style_meets_every_material(knit, root):
    """The coverage grid: each style exists in each of the seven materials."""
    cells = {(_attr(r, "knit_style"), m) for r in knit
             if r["category_path"][0] == root and _real(r)
             for m in MATERIALS if m in _attr(r, "material").lower()}
    missing = [(s, m) for s in STYLES[root] for m in MATERIALS if (s, m) not in cells]
    assert not missing, missing


@pytest.mark.parametrize("root", FLOORS)
def test_at_least_eight_styles_and_five_materials(knit, root):
    rows = [r for r in knit if r["category_path"][0] == root and _real(r)]
    assert len({_attr(r, "knit_style") for r in rows}) >= 8
    assert len({_attr(r, "material") for r in rows}) >= 5


@pytest.mark.parametrize("root", FLOORS)
def test_every_knitwear_product_has_a_neckline_and_a_style(knit, root):
    for r in knit:
        if r["category_path"][0] == root and r["product_id"] in knitwear_rows.product_ids():
            assert r.get("neckline") in NECKLINES, (r["product_id"], r.get("neckline"))
            assert _attr(r, "knit_style"), r["product_id"]


def test_the_sizes_stay_realistic(knit):
    mine = knitwear_rows.product_ids()
    for r in knit:
        if r["product_id"] in mine:
            assert len(r["size_options"]) <= 6, r["product_id"]


@pytest.mark.parametrize("shade", ("Cream", "Ivory", "Off White", "Ecru"))
@pytest.mark.parametrize("root", FLOORS)
def test_each_near_white_shade_is_a_color_on_jumpers(knit, root, shade):
    n = len({r["product_id"] for r in knit
             if r["category_path"][0] == root and r["product_type"] == "Jumper"
             and shade in {s["color"] for s in r["skus"]}})
    assert n >= 5, f"{root} {shade} jumpers: {n}"


@pytest.mark.parametrize("root", FLOORS)
def test_white_jumpers_are_plentiful(knit, root):
    n = len({r["product_id"] for r in knit
             if r["category_path"][0] == root and r["product_type"] == "Jumper"
             and "White" in {s["color"] for s in r["skus"]}})
    assert n >= 15, f"{root} white jumpers: {n}"


def test_every_row_is_unique_and_a_template(templates):
    docs = knitwear_rows.docs()
    assert docs
    assert {r["category_path"][0] for r in docs} == {"Women", "Men"}
    assert {r["category_path"][1] for r in docs} == {"Knitwear"}
    assert len({r["product_id"] for r in docs}) == len(docs)
    assert len({r["title"] for r in docs}) == len(docs)
    assert {r["product_id"] for r in docs} <= {r["product_id"] for r in templates}
    assert {r["product_id"] for r in docs} == set(knitwear_rows.product_ids())


@pytest.mark.parametrize("root", ("Women", "Men"))
@pytest.mark.parametrize("ptype", TYPES)
@pytest.mark.parametrize("klass", CLASSES)
def test_each_type_has_three_decoys_of_each_class_per_audience(root, ptype, klass):
    n = sum(1 for d in knitwear_rows.TABLE
            if d.ptype == ptype and d.klass == klass and d.root == root)
    assert n >= 3


def test_a_decoy_is_a_product_of_its_type_and_true_in_its_fields(decoys):
    assert decoys
    for d, rec in decoys:
        assert rec["product_type"] == d.ptype, d.code
        colors = {s["color"] for s in rec["skus"]}
        assert colors == {d.color}, (d.code, colors)
        assert rec["category_path"][0] == d.root, d.code


def test_class_1_names_a_trim_color_that_is_not_the_color(decoys):
    assert decoys
    for d, rec in decoys:
        if d.klass == 1:
            assert d.word in MAIN and d.word != d.color, d.code
            assert d.word.lower() in rec["title"].lower(), d.code
            assert d.color.lower() in rec["title"].lower(), d.code


def test_class_2_borrows_another_categorys_noun_and_class_3_an_audience_word(decoys):
    assert decoys
    for d, rec in decoys:
        t = rec["title"].lower()
        if d.klass == 2:
            assert d.word in CATEGORY_NOUNS and d.word in t, d.code
        if d.klass == 3:
            assert any(w in t for w in AUDIENCE_WORDS), d.code


def test_class_4_names_a_feature_the_material_lacks(decoys):
    assert decoys
    for d, rec in decoys:
        if d.klass == 4:
            stem = d.word.split("-")[0].lower()
            assert stem in rec["title"].lower(), d.code
            assert stem not in _attr(rec, "material").lower(), (d.code, _attr(rec, "material"))


def test_class_5_spells_the_shade_only_in_the_description(decoys):
    assert decoys
    for d, rec in decoys:
        if d.klass == 5:
            assert d.color.lower() in NEAR_WHITE
            assert d.color.lower() not in rec["title"].lower(), d.code
            assert d.color.lower() in rec["description"].lower(), d.code


def test_class_6_is_an_incidental_word_in_a_short_title(decoys):
    assert decoys
    for d, rec in decoys:
        if d.klass == 6:
            assert d.word.lower() in rec["title"].lower(), d.code
            assert d.word.lower() != d.color.lower(), d.code
            assert len(rec["title"].split()) <= 5, rec["title"]


def test_class_7_brand_is_in_the_brand_field_and_the_short_title(decoys):
    assert decoys
    seen = set()
    for d, rec in decoys:
        if d.klass == 7:
            assert rec["brand"] == d.word and d.word in BRANDS, d.code
            assert d.word in rec["title"] and len(rec["title"].split()) <= 5, d.code
            seen.add(d.word)
    assert seen == set(BRANDS)


@pytest.mark.parametrize("brand", BRANDS)
def test_each_new_brand_has_its_own_house_style_and_lockup_text(brand):
    style = house_styles.HOUSE_STYLES.get(brand)
    assert style is not None
    assert style.layout != "mark_only"  # the lockup carries the brand's name
    others = [s for b, s in house_styles.HOUSE_STYLES.items() if b != brand]
    assert style.mark not in {s.mark for s in others}
    assert house_styles.lockup_key(style) not in {house_styles.lockup_key(s) for s in others}


def test_the_table_lists_every_decoy_once(decoys):
    codes = [d.code for d in knitwear_rows.TABLE]
    assert len(codes) == len(set(codes))
    assert all(d.query and d.policy for d in knitwear_rows.TABLE)
