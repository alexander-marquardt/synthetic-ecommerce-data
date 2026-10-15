"""Nike is the second real-brand exception: text only, found by ``nike air max`` (gen#341).

The maintainer's ruling (2026-10-15): Nike joins Apple, iPhone and iPad as a real brand. Every other
brand stays invented. The name is text (title, brand, description); no drawing carries a logo, a
swoosh, a wordmark or a trade dress.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
sys.path.insert(0, str(RETAIL))

import build_preview  # noqa: E402
import house_styles as hs  # noqa: E402
import real_brands  # noqa: E402
import scale  # noqa: E402

MAIN = {"Red", "Blue", "Green", "Yellow", "Black", "White"}


@pytest.fixture(scope="module")
def catalog() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def nike(catalog) -> list[dict]:
    return [d for d in catalog if d["brand"] == "Nike"]


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def test_nike_air_max_matches_at_least_five_products_by_title(nike) -> None:
    hits = [d for d in nike if {"nike", "air", "max"} <= set(_words(d["title"]))]
    assert len(hits) >= 5, [d["title"] for d in hits]


def test_air_max_is_sold_to_men_women_and_kids(nike) -> None:
    roots = {d["category_path"][0] for d in nike if "air max" in d["title"].lower()}
    assert roots == {"Mens", "Womens", "Kids"}


def test_nike_trainers_running_shoes_and_kids_sports_shoes_are_in_the_existing_leaves(nike) -> None:
    leaves = {tuple(d["category_path"]) for d in nike}
    for root in ("Mens", "Womens", "Kids"):
        assert (root, "Shoes", "Trainers") in leaves
        assert (root, "Shoes", "Sports Shoes", "Running Shoes") in leaves


def test_nike_sportswear_is_joggers_sweatshirts_tees_and_sports_bras(nike) -> None:
    leaves = {d["category_leaf"] for d in nike}
    assert {"Joggers", "Sweatshirts", "T-Shirts", "Sports Bras"} <= leaves


def test_a_nike_style_offers_at_least_three_main_colors(nike) -> None:
    have = {d["product_id"]: {o["color"] for o in d["color_options"]} for d in nike}
    short = {pid: sorted(MAIN & c) for pid, c in have.items() if len(MAIN & c) < 3}
    assert short == {}


def test_nike_is_a_third_party_brand_and_every_nike_title_names_it(nike) -> None:
    assert nike, "no Nike product"
    assert {d["brand_owner"] for d in nike} == {"third_party"}
    assert [d["title"] for d in nike if "nike" not in d["title"].lower()] == []


def test_nike_ids_are_unique_and_leave_the_derivation(catalog) -> None:
    ids = [d["product_id"] for d in catalog]
    assert len(ids) == len(set(ids))
    derived = {d["product_id"] for d in scale.derivable(catalog)}
    assert scale.NIKE_IDS and not (scale.NIKE_IDS & derived)


def test_nike_is_named_by_decoys_of_other_brands_and_types(catalog, nike) -> None:
    decoys = [d for d in catalog if d["brand"] != "Nike" and "nike" in d["description"].lower()
              and d["product_id"] in scale.NIKE_IDS]
    assert len(decoys) >= 8
    assert len({d["product_type"] for d in decoys}) >= 6
    # none of them is a pair of trainers or running shoes, and none carries "nike" in its title
    assert not [d for d in decoys if d["product_type"] in ("Trainers", "Running Shoes")]
    assert not [d for d in decoys if "nike" in d["title"].lower()]


def test_a_nike_query_has_close_calls_the_nike_products_do_not_hold(catalog, nike) -> None:
    mentions = [d for d in catalog if "nike" in (d["title"] + " " + d["description"]).lower()]
    by_type = Counter(d["brand"] == "Nike" for d in mentions)
    assert by_type[True] >= 20 and by_type[False] >= 8


# -- the brand guard: Nike passes, every other real brand fails ------------------------------------


def _doc(brand: str = "Wrenfield", title: str = "Plain Tee", description: str = "A tee.") -> dict:
    return {"product_id": "X", "brand": brand, "title": title, "description": description}


def test_the_guard_allows_nike_in_the_brand_title_and_description() -> None:
    doc = _doc("Nike", "Nike Air Max 90 Trainers", "Cushioned trainers from Nike.")
    assert real_brands.check([doc]) == []
    assert "Nike" in real_brands.ALLOWED


@pytest.mark.parametrize("name", ["Adidas", "Puma", "New Balance", "Samsung", "Levi's", "Dyson"])
def test_the_guard_refuses_any_other_real_brand(name: str) -> None:
    assert len(real_brands.check([_doc(brand=name)])) == 1
    assert len(real_brands.check([_doc(title=f"{name} Style Tee")])) == 1
    assert len(real_brands.check([_doc(description=f"Fits {name} and Nike trainers.")])) == 1


def test_the_guard_does_not_flag_a_word_inside_an_invented_name() -> None:
    assert real_brands.check([_doc(brand="Pumaleigh Mill", title="Nextdoor Tee")]) == []


def test_the_allow_list_and_the_refused_list_do_not_overlap() -> None:
    allowed = {a.lower() for a in real_brands.ALLOWED}
    assert not allowed & {k.lower() for k in real_brands.KNOWN_REAL}


def test_the_whole_catalogue_names_only_invented_brands_and_the_allowed_ones(catalog) -> None:
    assert real_brands.check(catalog) == []


# -- drawings carry no logo ----------------------------------------------------------------------


def test_a_nike_drawing_carries_no_logo_mark_or_name(nike) -> None:
    assert nike, "no Nike product"
    for d in nike[:40]:
        svg = build_preview.drawing_svg(d)
        brand_layer = svg.split('<g class="brand">', 1)[1]
        assert 'class="mark"' not in brand_layer, d["product_id"]
        assert "<text" not in brand_layer, d["product_id"]
        assert "nike" not in svg.lower(), d["product_id"]


def test_the_nike_style_row_has_no_mark_and_no_other_brand_has_none() -> None:
    assert "Nike" in hs.HOUSE_STYLES
    assert hs.HOUSE_STYLES["Nike"].mark == "none"
    others = [b for b, s in hs.HOUSE_STYLES.items() if s.mark == "none" and b != "Nike"]
    assert others == []
    assert hs.logo(hs.HOUSE_STYLES["Nike"], "Nike") == []


def test_an_invented_brand_still_draws_its_logo(catalog) -> None:
    doc = next(d for d in catalog if d["brand"] == "Stridewell")
    svg = build_preview.drawing_svg(doc)
    assert 'class="mark"' in svg.split('<g class="brand">', 1)[1]
