"""``scripts/review_range_names.py`` counts the three classes of gen#623 (and the Line check).

The generator's own guard is in ``test_retail_scale.py`` (``range_review``); these tests hold the
script to small made-up rows, so a review that finds nothing cannot pass for a clean export.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import review_range_names as rr  # noqa: E402  (scripts/ is not a package)

RANGES = ["Larkrise", "Harrow"]
CLEAN = {"shared": 0, "foreign": 0, "phrase": 0, "unlabeled": 0}


def _row(pid: str, title: str, brand: str, line: str | None = None, **more: Any) -> dict[str, Any]:
    attrs = [{"key": "line", "name": "Line", "value": line}] if line else []
    return {"product_id": pid, "title": title, "brand": brand, "attributes": attrs, **more}


def test_a_range_word_under_two_brands_is_counted_once():
    rows = [
        _row("a", "Larkrise Chocolate Bar", "Pantry Mill", "Larkrise"),
        _row("b", "Larkrise Jam", "Copper Hill", "Larkrise"),
        _row("c", "Harrow Jeans", "Ottery Denim", "Harrow"),
    ]
    found = rr.review(rows, RANGES)
    assert found["shared"] == {"Larkrise": ["Copper Hill", "Pantry Mill"]}
    assert rr.counts(found) == CLEAN | {"shared": 1}


def test_a_the_prefix_and_a_second_sku_row_change_nothing():
    rows = [
        _row("a", "The Harrow Jeans", "Ottery Denim", "Harrow"),
        _row("a", "The Harrow Jeans", "Ottery Denim", "Harrow"),
    ]
    assert rr.counts(rr.review(rows, RANGES)) == CLEAN


def test_a_name_led_title_without_a_line_is_counted():
    rows = [
        _row("a", "Harrow Jeans", "Ottery Denim"),
        _row("b", "Harrow Skirt", "Ottery Denim", "Harrow"),
    ]
    assert rr.review(rows, RANGES)["unlabeled"] == [("Harrow Jeans", "Ottery Denim", "Harrow")]


def test_a_line_attribute_naming_another_word_does_not_label_the_title():
    rows = [_row("a", "Harrow Jeans", "Ottery Denim", "Larkrise")]
    assert len(rr.review(rows, RANGES)["unlabeled"]) == 1


def test_a_title_naming_another_brand_is_counted_but_not_its_own():
    rows = [
        _row("a", "Red Kite Lawn Mower", "Wrenfield"),
        _row("b", "Red Kite Hat", "Red Kite"),
        _row("c", "Wrenfield Hose", "Wrenfield"),
        _row("d", "Redkite Rope", "Wrenfield"),
    ]
    assert rr.review(rows, RANGES)["foreign"] == [("Red Kite Lawn Mower", "Wrenfield", "Red Kite")]


def test_a_brand_made_of_a_product_phrase_is_counted_but_a_single_word_is_not():
    rows = [
        _row("a", "Card Game Row Play Kitchen", "Card Game Row", category_leaf="Play kitchens"),
        _row("b", "Memory Card Game", "Little Fernby", category_leaf="Card games"),
        _row("c", "Cardigan", "Cardigan Finch", category_leaf="Cardigans"),
    ]
    assert rr.review(rows, RANGES)["phrase"] == {"Card Game Row": "card game"}


def test_a_dolls_house_brand_matches_the_apostrophe_label():
    rows = [_row("a", "House", "Dolls House Row", category_leaf="Dolls' houses")]
    assert rr.review(rows, RANGES)["phrase"] == {"Dolls House Row": "doll house"}


def test_a_line_the_data_names_counts_as_a_range_without_a_pool():
    rows = [
        _row("a", "Zorbik Sofa", "One", "Zorbik"),
        _row("b", "Zorbik Chair", "Two", "Zorbik"),
    ]
    assert list(rr.review(rows, [])["shared"]) == ["Zorbik"]


def test_a_range_stated_as_an_attribute_counts_when_the_title_does_not_lead_with_it():
    """The class 6 decoys lead with a department word ("Mens Kettle Hill Chinos")."""
    rows = [
        _row("a", "Mens Kettle Hill Chinos", "Larkmoor", "Kettle Hill"),
        _row("b", "Womens Kettle Hill Jumper", "Wrenfield", "Kettle Hill"),
        _row("c", "Mens Kettle Hill Polo Shirt", "Larkmoor", "Kettle Hill"),
    ]
    found = rr.review(rows, RANGES)
    assert found["shared"] == {"Kettle Hill": ["Larkmoor", "Wrenfield"]}
    assert rr.counts(found) == CLEAN | {"shared": 1}
