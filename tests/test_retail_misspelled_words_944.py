"""The retail build sells products whose text holds a common misspelling (gen#944, gen#1130).

The R&I demo offers "You may also consider searching for <common spelling>" only when a search has
3 or fewer Best results and the common spelling is at least 5 times more common. Three words are
on 3 products each (the hits and the suggestion show) and two on 7 to 10 (hits only).

gen#1130: a planted misspelling is a deliberate brand or product name, a pun a real company might
choose (Bannana Bros gummy sweets, the Pliars bluffing card game), never a misspelled generic word
in an ordinary product's title or description ("Big Bannana Bunch" read as a data error). All
five words follow it: ``Leggins & Co`` is a fashion label and ``Cardigen`` a deck-building trading
card game, far from knitwear. No category, type or attribute holds any of the five.

These tests read the ceiling build, the one a release ships (docs/releasing.md).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import house_styles, kit, kit_toys_play, scale
from synthetic_ecommerce_data.domains.retail.class_model import BRAND_OWNER
from synthetic_ecommerce_data.domains.retail.feature_decoys import misspelled_words_944 as ms

#: misspelling -> (common spelling, how many products carry it).
WORDS = {
    "choocolate": ("chocolate", range(3, 4)),
    "bannana": ("banana", range(3, 4)),
    "pliars": ("pliers", range(3, 4)),
    "leggins": ("leggings", range(7, 11)),
    "cardigen": ("cardigan", range(7, 11)),
}
#: gen#1130: each word -> the brand or product names that may carry it, and the (category leaf,
#: product type) pairs its products sit in, every one of them used.
NAMED = {
    "choocolate": (
        ("Choo-Choocolate Express",),
        {("Chocolate Boxes", "Chocolate Box"), ("Wooden Toys", "Wooden Toy")},
    ),
    "bannana": (
        ("Bannana Bros", "Bannana Brothers"),
        {("Sweets", "Sweets"), ("Board Games", "Board Game")},
    ),
    "pliars": (("Pliars",), {("Card Games", "Card Game")}),
    "leggins": (("Leggins & Co",), {("Leggings", "Leggings")}),
    "cardigen": (("Cardigen",), {("Card Games", "Card Game")}),
}
#: gen#1130: the drawings of a word's products, each in its own kit (no reused banana, and
#: Cardigen is not drawn as the Pliars tuck box).
SHAPES = {
    "choocolate": {"box", "wooden_toy"},
    "bannana": {"bag", "board_game"},
    "pliars": {"card_game"},
    "leggins": {"leggings"},
    "cardigen": {"trading_cards"},
}
#: The Engine's head-hit threshold and the floor the common spelling must clear (issue text).
THRESHOLD, RATIO = 3, 5
#: The invented brands that carry a misspelling.
BRANDS = ("Choo-Choocolate Express", "Bannana Bros", "Leggins & Co", "Cardigen")
#: The industrial catalogue the R&I demo serves beside retail: its pliers count for `pliars`.
INDUSTRIAL = Path(__file__).resolve().parent.parent / "golden-catalog" / "flat.jsonl"


@pytest.fixture(scope="module")
def records() -> list[dict]:
    return ceiling_build().records


def _has(word: str, text: str) -> bool:
    return re.search(rf"\b{re.escape(word)}s?\b", text.lower()) is not None


def _text(r: dict) -> str:
    return " ".join((r["brand"], r["title"], r.get("description", "")))


def _carrying(records: list[dict], word: str) -> list[dict]:
    return [r for r in records if _has(word, _text(r))]


@pytest.mark.parametrize("word", WORDS)
def test_each_misspelling_is_on_its_number_of_products(records, word) -> None:
    _, count = WORDS[word]
    assert len(_carrying(records, word)) in count, [r["title"] for r in _carrying(records, word)]


def test_three_words_show_the_suggestion_and_two_do_not() -> None:
    under = {w for w, (_, n) in WORDS.items() if max(n) <= THRESHOLD}
    over = {w for w, (_, n) in WORDS.items() if min(n) > THRESHOLD}
    assert (under, over) == ({"choocolate", "bannana", "pliars"}, {"leggins", "cardigen"})


@pytest.mark.parametrize("word", [w for w, (_, n) in WORDS.items() if max(n) <= THRESHOLD])
def test_the_common_spelling_is_five_times_more_common(records, word) -> None:
    """Counted over the Combined catalogue: retail and the industrial golden catalogue."""
    common = WORDS[word][0]
    industrial = [json.loads(raw) for raw in INDUSTRIAL.read_text().splitlines()]
    searched = ("title", "parent_title", "brand", "description", "text")
    commons = len(_carrying(records, common))
    commons += sum(
        1 for r in industrial if _has(common, " ".join(str(r.get(f, "")) for f in searched))
    )
    assert commons >= RATIO * len(_carrying(records, word)) > 0


@pytest.mark.parametrize("word", NAMED)
def test_the_misspelling_is_only_ever_a_brand_or_product_name(records, word) -> None:
    """With its brand and product names taken out, no product's text holds the word, and every
    product carrying it names one in its brand or title."""
    names, _ = NAMED[word]
    strip = re.compile("|".join(rf"\b{re.escape(n)}\b" for n in names), re.IGNORECASE)
    for r in _carrying(records, word):
        assert not _has(word, strip.sub(" ", _text(r))), (r["product_id"], _text(r))
        assert strip.search(f"{r['brand']} {r['title']}"), (r["product_id"], r["title"])


@pytest.mark.parametrize("word", NAMED)
def test_each_named_product_is_of_the_specs_type_and_category(records, word) -> None:
    _, places = NAMED[word]
    found = {(r["category_path"][-1], r["product_type"]) for r in _carrying(records, word)}
    assert found == places


@pytest.mark.parametrize(
    ("word", "common"), [("bannana", "banana"), ("pliars", "pliers"), ("cardigen", "cardigan")]
)
def test_no_named_product_sits_in_its_common_words_own_category(records, word, common) -> None:
    """The shopper who types the word is after the brand: no Bananas, Pliers or Cardigans leaf,
    and no Cardigen product in clothing."""
    for r in _carrying(records, word):
        assert not any(_has(common, node) for node in r["category_path"]), r["category_path"]
        assert r["category_path"][:3] != ["Food & Drink", "Fruit & Vegetables", "Fresh Fruit"]
        assert "Knitwear" not in r["category_path"] and r["department"] != "Clothing"


@pytest.mark.parametrize("word", NAMED)
def test_each_named_product_is_drawn_by_its_own_kit(word) -> None:
    shapes = {ms.KINDS[kind].shape for _, kind, *_, w, _ in ms._ROWS if w == word}
    assert shapes == SHAPES[word]


def test_each_cardigen_product_draws_its_own_picture() -> None:
    """Eight products, eight pictures: no two Cardigen products draw the same trading card
    form (a pack, an expansion pack per theme, a display box, a deck, a battle set, sleeves, a
    deck box)."""
    fill = kit.Fill("solid", "#4a3a8a")
    kinds = [kind for _, kind, *_, w, _ in ms._ROWS if w == "cardigen"]
    drawn = {"".join(kit_toys_play.trading_cards(fill.base, fill, None, **dict(ms.KINDS[k].params)))
             for k in kinds}  # fmt: skip
    assert len(kinds) == len(set(kinds)) == len(drawn) == 8


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


@pytest.mark.parametrize("brand", BRANDS)
def test_each_invented_brand_is_third_party_and_draws_its_own_mark(records, brand) -> None:
    assert any(r["brand"] == brand for r in records), brand
    assert BRAND_OWNER.get(brand) == "third_party"
    assert brand in house_styles.HOUSE_STYLES


def test_no_derived_style_is_drawn_from_a_misspelled_product(records) -> None:
    """The rows are templates only. In the pool a derived style is drawn from, they would move
    the seeded derivation, and about a hundred other products of the build would change."""
    ours = {r["product_id"] for w in WORDS for r in _carrying(records, w)}
    assert ours
    pool = {d["product_id"] for d in scale.derivable(scale.templates())}
    assert sorted(ours & pool) == []
    assert sorted(i for i, t in ceiling_build().template_of.items() if t in ours) == []
