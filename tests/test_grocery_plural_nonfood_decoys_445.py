"""Non-food decoys on the fresh plural: "lemons" is not only food (gen#445, the 10-17 follow-up).

With interpretation off, a raw search for a fresh fruit or vegetable in the plural must meet
products of a NON-food department whose title carries the exact plural: a fruit-word brand shown
on the product ("Lucky Lemons" kidswear) or a product scented with the fruit (a lemons hand wash,
an oranges and cloves candle). These are class 9 rows of :mod:`decoy_rows`, next to the food
rows of ``tests/test_grocery_plural_decoys_445.py``. Every one is a believable retail product
(gen#444): the brand or the scent is what the plural names, and nothing claims it is fresh fruit.
"""

from __future__ import annotations

import re
import sys
from functools import cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_rows as dr  # noqa: E402
import real_brands  # noqa: E402
import scale  # noqa: E402

PLURALS = ("oranges", "lemons", "limes", "apples", "strawberries", "raspberries", "tomatoes",
           "onions", "potatoes", "carrots", "bananas", "cherries")
#: The plurals the maintainer named: each shows at least two non-food decoys in the first 12.
TWO = ("oranges", "lemons", "limes")
STEM = {"oranges": "orange", "lemons": "lemon", "limes": "lime", "apples": "apple",
        "strawberries": "strawberr", "raspberries": "raspberr", "tomatoes": "tomato",
        "onions": "onion", "potatoes": "potato", "carrots": "carrot", "bananas": "banana",
        "cherries": "cherr"}
MAX_TITLE_TOKENS = 6


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z][a-z-]*", text.lower())


@cache
def _docs() -> dict[str, dict]:
    return {f"PLT-D{d.code}": doc for d, doc in zip(dr.TABLE, dr.docs(), strict=True)}


def _nonfood(plural: str) -> list[dr.Decoy]:
    return [d for d in dr.TABLE if d.cls == 9 and d.query == plural
            and _docs()[f"PLT-D{d.code}"]["category_path"][0] != "Food & Drink"]


def _attr(doc: dict, key: str) -> str:
    return " ".join(a["value"] for a in doc.get("attributes", []) if a["key"] == key)


@pytest.mark.parametrize("plural", PLURALS)
def test_each_plural_has_a_non_food_decoy(plural: str) -> None:
    rows = _nonfood(plural)
    assert len(rows) >= (2 if plural in TWO else 1), (plural, [d.title for d in rows])
    for d in rows:
        assert plural in _tokens(d.title), d.title
        assert len(d.title.split()) <= MAX_TITLE_TOKENS, d.title


@pytest.mark.parametrize("plural", PLURALS)
def test_a_non_food_decoy_is_a_brand_or_a_scent_and_never_fresh(plural: str) -> None:
    rows = _nonfood(plural)
    assert rows, plural
    for d in rows:
        doc = _docs()[f"PLT-D{d.code}"]
        assert "fresh" not in _tokens(d.title + " " + doc["description"]), d.title
        branded = plural in _tokens(doc["brand"]) and doc["brand"].lower() in d.title.lower()
        scented = STEM[plural] in _attr(doc, "fragrance").lower()
        assert branded != scented, (d.title, doc["brand"], _attr(doc, "fragrance"))
        # A brand row carries no fruit motif: the word is the label, not the picture.
        assert not branded or _attr(doc, "motif") == "", d.title
        assert not real_brands.check([doc]), d.title


@pytest.fixture(scope="module")
def index() -> br.Index:
    return br.Index(scale.build(10**6).records)


@pytest.mark.parametrize("plural", TWO)
def test_a_raw_search_shows_two_non_food_decoys_in_the_first_twelve(index: br.Index,
                                                                     plural: str) -> None:
    ids = {f"PLT-D{d.code}" for d in _nonfood(plural)}
    top = [d["product_id"] for d in br.rank(index, plural, 12)]
    assert len([i for i in top if i in ids]) >= 2, (plural, top)
