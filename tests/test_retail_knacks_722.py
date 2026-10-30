"""The sportswear brand is invented: Knacks and Breeze Max, not a real name (gen#722).

The maintainer's ruling (2026-10-30) replaces the 2026-10-15 one (gen#341): the 22 products that
sold under a real sportswear brand keep their ids, types, prices, colors and sizes under an
invented brand and invented line names, and the guard refuses the old names.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import build_preview, real_brands, scale
from synthetic_ecommerce_data.domains.retail import house_styles as hs

#: Each former product by id, recorded from main before the rename: what gen#722 keeps.
PIN = json.loads((Path(__file__).parent / "data" / "knacks_722_products.json").read_text("utf-8"))
FORMER = ("Nike", "Air Max", "Pegasus", "Dri-FIT")
MAIN = {"Red", "Blue", "Green", "Yellow", "Black", "White"}
FORMER_WORD = re.compile(rf"(?<![a-z0-9])(?:{'|'.join(map(re.escape, FORMER))})(?![a-z0-9])", re.I)


@pytest.fixture(scope="module")
def catalog() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def knacks(catalog) -> list[dict]:
    return [d for d in catalog if d["brand"] == "Knacks"]


def _kept(doc: dict) -> dict:
    """What a former product keeps: the digest holds every SKU's id, color, size and price."""
    skus = sorted(doc["skus"], key=lambda s: s["sku"])
    return {
        "product_type": doc["product_type"],
        "category_path": doc["category_path"],
        "price": doc["price"],
        "colors": sorted({s["color"] for s in skus}),
        "skus": len(skus),
        "sku_digest": hashlib.sha256(json.dumps(skus, sort_keys=True).encode()).hexdigest(),
    }


def test_no_document_names_a_former_name_in_any_field(catalog) -> None:
    found = {d["product_id"]: FORMER_WORD.findall(json.dumps(d)) for d in catalog}
    assert {pid: names for pid, names in found.items() if names} == {}


def test_a_generated_catalogue_names_no_former_name() -> None:
    records = ceiling_build().records
    assert [r["product_id"] for r in records if FORMER_WORD.search(json.dumps(r))] == []


@pytest.mark.parametrize("name", FORMER)
@pytest.mark.parametrize("field", ["brand", "title", "description"])
def test_the_guard_refuses_a_former_name(name: str, field: str) -> None:
    doc = {"product_id": "X", "brand": "Wrenfield", "title": "Tee", "description": "A tee."}
    assert len(real_brands.check([{**doc, field: f"Fits {name} trainers"}])) == 1


def test_each_former_product_is_a_knacks_product_with_what_it_had(catalog) -> None:
    by_id = {d["product_id"]: d for d in catalog}
    assert {pid: by_id[pid]["brand"] for pid in PIN} == dict.fromkeys(PIN, "Knacks")
    assert {pid: _kept(by_id[pid]) for pid in PIN} == PIN


def test_no_other_product_is_a_knacks_product(catalog) -> None:
    assert {d["product_id"] for d in catalog if d["brand"] == "Knacks"} == set(PIN)


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def test_knacks_breeze_max_matches_at_least_five_products_by_title(knacks) -> None:
    hits = [d for d in knacks if {"knacks", "breeze", "max"} <= set(_words(d["title"]))]
    assert len(hits) >= 5, [d["title"] for d in hits]


def test_breeze_max_is_sold_to_men_women_and_kids(knacks) -> None:
    roots = {d["category_path"][0] for d in knacks if "breeze max" in d["title"].lower()}
    assert roots == {"Mens", "Womens", "Kids"}


def test_knacks_shoes_are_in_the_existing_leaves(knacks) -> None:
    leaves = {tuple(d["category_path"]) for d in knacks}
    for root in ("Mens", "Womens", "Kids"):
        assert (root, "Shoes", "Trainers") in leaves
        assert (root, "Shoes", "Sports Shoes", "Running Shoes") in leaves


def test_knacks_sportswear_is_joggers_sweatshirts_tees_and_sports_bras(knacks) -> None:
    leaves = {d["category_leaf"] for d in knacks}
    assert {"Joggers", "Sweatshirts", "T-Shirts", "Sports Bras"} <= leaves


def test_a_knacks_style_offers_at_least_three_main_colors(knacks) -> None:
    have = {d["product_id"]: {o["color"] for o in d["color_options"]} for d in knacks}
    short = {pid: sorted(MAIN & c) for pid, c in have.items() if len(MAIN & c) < 3}
    assert short == {}


def test_knacks_is_a_third_party_brand_and_every_knacks_title_names_it(knacks) -> None:
    assert knacks, "no Knacks product"
    assert {d["brand_owner"] for d in knacks} == {"third_party"}
    assert [d["title"] for d in knacks if "knacks" not in d["title"].lower()] == []


def test_knacks_ids_are_unique_and_leave_the_derivation(catalog) -> None:
    ids = [d["product_id"] for d in catalog]
    assert len(ids) == len(set(ids))
    derived = {d["product_id"] for d in scale.derivable(catalog)}
    assert scale.source_ids("knacks_rows") and not (scale.source_ids("knacks_rows") & derived)


def test_knacks_is_named_by_decoys_of_other_brands_and_types(catalog, knacks) -> None:
    decoys = [d for d in catalog if d["brand"] != "Knacks" and "knacks" in d["description"].lower()
              and d["product_id"] in scale.source_ids("knacks_rows")]
    assert len(decoys) >= 8
    assert len({d["product_type"] for d in decoys}) >= 6
    # none of them is a pair of trainers or running shoes, and none carries "knacks" in its title
    assert not [d for d in decoys if d["product_type"] in ("Trainers", "Running Shoes")]
    assert not [d for d in decoys if "knacks" in d["title"].lower()]


def test_a_knacks_query_has_close_calls_the_knacks_products_do_not_hold(catalog, knacks) -> None:
    mentions = [d for d in catalog if "knacks" in (d["title"] + " " + d["description"]).lower()]
    by_type = Counter(d["brand"] == "Knacks" for d in mentions)
    assert by_type[True] >= 20 and by_type[False] >= 8


# -- the brand guard ----------------------------------------------------------------------------


def _doc(brand: str = "Wrenfield", title: str = "Plain Tee", description: str = "A tee.") -> dict:
    return {"product_id": "X", "brand": brand, "title": title, "description": description}


@pytest.mark.parametrize("name", ["Adidas", "Puma", "New Balance", "Samsung", "Levi's", "Dyson"])
def test_the_guard_refuses_any_other_real_brand(name: str) -> None:
    assert len(real_brands.check([_doc(brand=name)])) == 1
    assert len(real_brands.check([_doc(title=f"{name} Style Tee")])) == 1
    assert len(real_brands.check([_doc(description=f"Fits {name} and Knacks trainers.")])) == 1


def test_the_guard_does_not_flag_a_word_inside_an_invented_name() -> None:
    assert real_brands.check([_doc(brand="Pumaleigh Mill", title="Nextdoor Tee")]) == []


def test_the_allow_list_and_the_refused_list_do_not_overlap() -> None:
    allowed = {a.lower() for a in real_brands.ALLOWED}
    assert not allowed & {k.lower() for k in real_brands.KNOWN_REAL}


def test_the_whole_catalogue_names_only_invented_brands_and_the_allowed_ones(catalog) -> None:
    assert real_brands.check(catalog) == []


# -- Knacks draws its own mark ---------------------------------------------------------------------


def test_a_knacks_drawing_carries_its_own_mark(knacks) -> None:
    for d in knacks[:40]:
        assert 'class="mark"' in build_preview.drawing_svg(d).split('<g class="brand">', 1)[1]


def test_the_knacks_mark_is_its_own_and_is_drawn_in_straight_strokes() -> None:
    mark = hs.HOUSE_STYLES["Knacks"].mark
    assert mark == "laced_eyelets"
    assert not re.search(r' d="[^"]*[QqCcSsAa]', hs.mark_svg(mark, 0, 0, 50, "#111111"))


def test_no_brand_has_no_mark() -> None:
    none = {b for b, s in hs.HOUSE_STYLES.items() if s.mark == hs.NO_MARK}
    assert none == set()


def test_an_invented_brand_still_draws_its_logo(catalog) -> None:
    doc = next(d for d in catalog if d["brand"] == "Stridewell")
    svg = build_preview.drawing_svg(doc)
    assert 'class="mark"' in svg.split('<g class="brand">', 1)[1]
