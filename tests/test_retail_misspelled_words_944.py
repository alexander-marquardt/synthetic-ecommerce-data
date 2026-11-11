"""The retail build sells products whose text holds a common misspelling (gen#944).

The R&I demo offers "You may also consider searching for <common spelling>" only when a search has
3 or fewer Best results and the common spelling is at least 5 times more common. Two words are on
3 products each (the hits and the suggestion show) and two on 7 to 10 (hits only). Each product is
an ordinary product of its word's own type and category; the misspelling sits in an invented
brand, in the title, or in the description alone, and never in a category, type or attribute.

These tests read the ceiling build, the one a release ships (docs/releasing.md).
"""

from __future__ import annotations

import re

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import house_styles
from synthetic_ecommerce_data.domains.retail.class_model import BRAND_OWNER

#: misspelling -> (common spelling, the category node and type its products sit in, products).
WORDS = {
    "choocolate": ("chocolate", "Milk Chocolate Bars", "Chocolate Bar", range(3, 4)),
    "bannana": ("banana", "Bananas", "Fresh Fruit", range(3, 4)),
    "leggins": ("leggings", "Leggings", "Leggings", range(7, 11)),
    "cardigen": ("cardigan", "Cardigans", "Cardigan", range(7, 11)),
}
#: The Engine's head-hit threshold and the floor the common spelling must clear (issue text).
THRESHOLD, RATIO = 3, 5
#: The invented brands that carry a misspelling.
BRANDS = ("Choocolate Factory", "Bannana Bros", "Leggins Lab", "Cardigen & Co")


@pytest.fixture(scope="module")
def records() -> list[dict]:
    return ceiling_build().records


def _has(word: str, text: str) -> bool:
    return re.search(rf"\b{re.escape(word)}s?\b", text.lower()) is not None


def _carrying(records: list[dict], word: str) -> list[dict]:
    return [r for r in records if _has(word, " ".join((r["brand"], r["title"], r["description"])))]


@pytest.mark.parametrize("word", WORDS)
def test_each_misspelling_is_on_its_number_of_products(records, word) -> None:
    *_, count = WORDS[word]
    assert len(_carrying(records, word)) in count, [r["title"] for r in _carrying(records, word)]


def test_two_words_show_the_suggestion_and_two_do_not() -> None:
    """Half the words sit at or under the threshold, half above it."""
    under = [w for w, (*_, n) in WORDS.items() if max(n) <= THRESHOLD]
    over = [w for w, (*_, n) in WORDS.items() if min(n) > THRESHOLD]
    assert len(under) == len(over) == 2


@pytest.mark.parametrize("word", [w for w, (*_, n) in WORDS.items() if max(n) <= THRESHOLD])
def test_the_common_spelling_is_five_times_more_common(records, word) -> None:
    common = WORDS[word][0]
    assert len(_carrying(records, common)) >= RATIO * len(_carrying(records, word)) > 0


@pytest.mark.parametrize("word", WORDS)
def test_each_product_is_of_its_words_own_type_and_category(records, word) -> None:
    _, node, ptype, _ = WORDS[word]
    found = _carrying(records, word)
    assert found
    wrong = {r["product_id"]: (r["category_path"], r["product_type"]) for r in found
             if r["category_path"][-1] != node or r["product_type"] != ptype}  # fmt: skip
    assert wrong == {}


@pytest.mark.parametrize("word", WORDS)
def test_the_misspelling_is_product_text_only(records, word) -> None:
    """No category node, product type or attribute of any product holds the word."""
    leaks = []
    for r in records:
        fields = [*r["category_path"], r["product_type"]]
        fields += [f"{a['name']} {a['value']}" for a in r["attributes"]]
        if any(_has(word, str(f)) for f in fields):
            leaks.append(r["product_id"])
    assert leaks == []


@pytest.mark.parametrize("word", WORDS)
def test_the_placements_mix_brand_and_title(records, word) -> None:
    found = _carrying(records, word)
    assert any(_has(word, r["brand"]) for r in found), word
    assert any(_has(word, r["title"]) and not _has(word, r["brand"]) for r in found), word


def test_some_products_hold_the_misspelling_in_the_description_only(records) -> None:
    only = [r["product_id"] for w in WORDS for r in _carrying(records, w)
            if not _has(w, f"{r['brand']} {r['title']}")]  # fmt: skip
    assert 1 <= len(only) <= 2, only


@pytest.mark.parametrize("brand", BRANDS)
def test_each_invented_brand_is_third_party_and_draws_its_own_mark(records, brand) -> None:
    assert any(r["brand"] == brand for r in records), brand
    assert BRAND_OWNER.get(brand) == "third_party"
    assert brand in house_styles.HOUSE_STYLES
