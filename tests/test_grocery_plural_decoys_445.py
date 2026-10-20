"""Grocery decoys on the plural: a raw search for "oranges" is not too clean (gen#445).

With interpretation off, a search for a fresh fruit or vegetable in the plural must meet products
of other categories whose title names the plural as an ingredient or source (a juice pressed from
oranges, sun-dried tomatoes in oil), and the fresh products must have titles as long as the
decoys', so the title field's length normalisation does not put every fresh product above them.
The rows are class 9 of :mod:`decoy_rows`; each is a believable retail title (gen#444).
"""

from __future__ import annotations

import math
import re
import statistics
import sys
from collections import Counter
from functools import cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_rows as dr  # noqa: E402
import grocery  # noqa: E402
import scale  # noqa: E402

PLURALS = ("oranges", "lemons", "limes", "apples", "strawberries", "raspberries", "tomatoes",
           "onions", "potatoes", "carrots", "bananas", "cherries")
#: The stem a decoy's ingredient list must hold: the product is made of the fruit, whatever it says.
STEM = {"oranges": "orange", "lemons": "lemon", "limes": "lime", "apples": "apple",
        "strawberries": "strawberr", "raspberries": "raspberr", "tomatoes": "tomato",
        "onions": "onion", "potatoes": "potato", "carrots": "carrot", "bananas": "banana",
        "cherries": "cherr"}
FRESH = ("Fruit & Vegetables", "Fresh Fruit", "Fresh Vegetables")
MAX_TITLE_TOKENS = 6


def _tokens(title: str) -> list[str]:
    return re.findall(r"[a-z][a-z-]*", title.lower())


@cache
def _docs() -> dict[str, dict]:
    return {f"PLT-D{d.code}": doc for d, doc in zip(dr.TABLE, dr.docs(), strict=True)}


def _rows(plural: str) -> list[dr.Decoy]:
    """The FOOD class 9 rows of a plural; the non-food ones (a brand, a scent) have their own
    test, ``tests/test_grocery_plural_nonfood_decoys_445.py``."""
    return [d for d in dr.TABLE if d.cls == 9 and d.query == plural
            and _docs()[f"PLT-D{d.code}"]["category_path"][0] == "Food & Drink"]


@cache
def _fresh_records() -> tuple[dict, ...]:
    return tuple(grocery.build(grocery.TARGET))


@pytest.mark.parametrize("plural", PLURALS)
def test_each_plural_has_three_decoys_from_two_categories(plural: str) -> None:
    rows = _rows(plural)
    assert len(rows) >= 3, plural
    for d in rows:
        assert plural in _tokens(d.title), d.title
        assert len(d.title.split()) <= MAX_TITLE_TOKENS, d.title
    paths = {tuple(_docs()[f"PLT-D{d.code}"]["category_path"][:3]) for d in rows}
    assert len(paths) >= 2, (plural, paths)


@pytest.mark.parametrize("plural", PLURALS)
def test_a_decoy_is_a_real_product_that_never_claims_to_be_fresh(plural: str) -> None:
    assert _rows(plural), plural
    for d in _rows(plural):
        doc = _docs()[f"PLT-D{d.code}"]
        assert not set(FRESH) & set(doc["category_path"]), d.title
        assert "fresh" not in _tokens(d.title), d.title
        assert d.ingredients and any(STEM[plural] in i for i in d.ingredients), d.title


@pytest.mark.parametrize("plural", PLURALS)
def test_the_fresh_products_are_as_long_as_the_decoys(plural: str) -> None:
    leaf = plural.title()
    fresh = [r for r in _fresh_records()
             if r["category_path"][-1].endswith(leaf) and plural in _tokens(r["title"])]
    assert len(fresh) >= 5 and len(_rows(plural)) >= 3, (plural, len(fresh))
    fresh_len = statistics.median(len(r["title"].split()) for r in fresh)
    decoy_len = statistics.median(len(d.title.split()) for d in _rows(plural))
    assert abs(fresh_len - decoy_len) <= 2, (plural, fresh_len, decoy_len)


@cache
def _million() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def index() -> br.Index:
    return br.Index(_million())


@pytest.mark.parametrize("plural", PLURALS)
def test_a_raw_search_shows_three_decoys_in_the_first_twelve(index: br.Index, plural: str) -> None:
    ids = {f"PLT-D{d.code}" for d in _rows(plural)}
    top = [d["product_id"] for d in br.rank(index, plural, 12)]
    assert len([i for i in top if i in ids]) >= 3, (plural, top)


def _title_scores(plural: str) -> dict[str, float]:
    """The title-only BM25 of ``plural`` over the million-product build: exact spelling, no
    stemming, no description and no popularity, Elasticsearch's defaults (k1 1.2, b 0.75). This is
    the raw match a search with interpretation off makes, which :mod:`baseline_rank` hides (it
    strips the plural, reads the description and weighs the sales)."""
    counts = [Counter(re.findall(r"[a-z0-9]+", r["title"].lower())) for r in _million()]
    mean = sum(sum(c.values()) for c in counts) / len(counts)
    df = sum(1 for c in counts if c[plural])
    idf = math.log(1 + (len(counts) - df + 0.5) / (df + 0.5))
    return {
        r["product_id"]: idf * c[plural] * 2.2
        / (c[plural] + 1.2 * (0.25 + 0.75 * sum(c.values()) / mean))
        for r, c in zip(_million(), counts, strict=True) if c[plural]
    }


@pytest.mark.parametrize("plural", PLURALS)
def test_a_title_only_raw_match_shows_three_decoys_in_the_first_twelve(plural: str) -> None:
    """Short titles score higher, so a decoy is surely in the first twelve only when no more than
    twelve products (itself and every tie with it included) score as high."""
    scores = _title_scores(plural)
    ids = {f"PLT-D{d.code}" for d in _rows(plural)}
    sure = [i for i in ids if sum(1 for v in scores.values() if v >= scores[i] - 1e-9) <= 12]
    assert len(sure) >= 3, (plural, len(scores), sorted(
        sum(1 for v in scores.values() if v >= scores[i] - 1e-9) for i in ids))


def test_the_class_9_docstring_examples_are_titles_of_the_rows() -> None:
    """The examples the class 9 docstring quotes are real rows, not stale titles."""
    titles = {d.title for d in dr.TABLE}
    section = (dr.__doc__ or "").split("9. **plural**", 1)[1].split("or, in a non-food", 1)[0]
    quoted = re.findall(r'"([^"]+)"', section)
    assert quoted
    assert all(any(t.startswith(q) for t in titles) for q in quoted), quoted


def test_the_apple_oat_bar_title_joins_its_words_with_an_ampersand() -> None:
    """A retailer prints "Apples & Cinnamon Oat Bars", never the bare compound."""
    titles = {d.title for d in dr.TABLE}
    assert "Apples & Cinnamon Oat Bars" in titles
    assert "Apples Cinnamon Oat Bars" not in titles
