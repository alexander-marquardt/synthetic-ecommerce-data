"""Gift card text-match decoys (gen#437): the "card" that is a gift card, planted next to the Gifts
decoys of gen#425.

gen#425 left two "card" meanings unplanted. The gift card has a home since gen#424 (the
``gift_card`` spec: Gifts > Cards > Gift Cards), so its decoys are planted here: rows of the
class-8 table of :mod:`decoy_product_words` whose title holds "gift card" and whose true type is
another product (a card holder case, a wrapping sheet). The memory card needs the Electronics
department (gen#332) and stays open on gen#437.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_product_words as dpw  # noqa: E402
import scale  # noqa: E402
from distractors import tokens  # noqa: E402

PTYPE = "Gift Card"
PATH_LEAF = "Gift Cards"
COLOR_WORDS = {c.lower() for c in dpw.COLORS} - {"clear"}


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def by_id(ceiling: list[dict]) -> dict[str, dict]:
    return {r["product_id"]: r for r in ceiling}


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def _rows() -> list[dpw.Row]:
    return [r for r in dpw.TABLE if r.gift_type == PTYPE]


def test_the_gift_card_has_at_least_two_decoys() -> None:
    rows = _rows()
    assert len(rows) >= 2, len(rows)
    assert all(r.decoy and r.policy and r.query == "gift card" and r.noun == "card" for r in rows)
    assert len({r.kind for r in rows}) == len(rows)


def test_each_gift_card_decoy_holds_the_shoppers_word_and_is_another_product(
    by_id: dict[str, dict],
) -> None:
    rows = _rows()
    assert rows
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        assert {"gift", "card"} <= set(tokens(doc["title"])), (row.code, doc["title"])
        assert doc["product_type"] != PTYPE, row.code
        assert PATH_LEAF not in doc["category_path"], row.code
        assert len(doc["title"].split()) <= 5, doc["title"]
        # the department policy drops a decoy of another department; the one that sits in Gifts
        # is fixed by the category policy
        assert (doc["category_path"][0] == "Gifts") == (row.policy == "category"), row.code


def test_a_gift_card_decoy_names_no_color_word_the_drawing_does_not_show(
    by_id: dict[str, dict],
) -> None:
    rows = _rows()
    assert rows
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        words = set(re.findall(r"[a-z]+", f"{doc['title']} {doc['description']}".lower()))
        assert not words & COLOR_WORDS, (row.code, words & COLOR_WORDS)


def test_every_gift_card_decoy_can_be_found_by_its_query(
    index: br.Index,
) -> None:
    rows = _rows()
    assert rows
    for row in rows:
        found = {d["product_id"] for d in br.rank(index, row.query, 1000)}
        assert f"PLT-{row.code}" in found, row.code


def _shopper_view(index: br.Index, query: str) -> list[dict]:
    """The results after the policies that fix the class-8 decoys (department Gifts kept, the
    decoy rows of :data:`dpw.BY_ID` dropped)."""
    return [
        d
        for d in br.rank(index, query, 1000)
        if d["category_path"][0] == "Gifts" and d["product_id"] not in dpw.BY_ID
    ]


def test_a_gift_card_search_ranks_a_gift_card_first(index: br.Index) -> None:
    top = _shopper_view(index, "gift card")[:5]
    assert top
    assert top[0]["product_type"] == PTYPE, [(d["product_id"], d["title"]) for d in top]


def test_a_greeting_card_search_ranks_no_gift_card_above_a_greeting_card(
    index: br.Index,
) -> None:
    view = _shopper_view(index, "greeting card")[:10]
    types = [d["product_type"] for d in view]
    assert types and types[0] == "Greeting Card", types
    assert PTYPE not in types[: types.index("Greeting Card") + 1], types
