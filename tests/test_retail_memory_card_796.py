"""The memory card of Electronics and its "card" word decoys (gen#796).

gen#437 planted the gift card's decoys and left the memory card open: no Electronics type was a
memory card, so a `memory card` search had no true answer and the toys' "Memory Card Game" was the
only row with the words. The type now lives at Electronics > Accessories > Memory Cards, and
"memory card" sits in the title of products whose true type is something else (class 8, gen#326).
A greeting card and the Memory Card Game were already cross-department decoys; they are asserted
here, not added again.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from decoy_true_nodes import TRUE_NODE
from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import decoy_product_words as dpw
from synthetic_ecommerce_data.domains.retail import image_release, kit
from synthetic_ecommerce_data.domains.retail.distractors import tokens

PTYPE = "Memory Card"
PATH = ["Electronics", "Accessories", "Memory Cards"]
QUERY = "memory card"
COLOR_WORDS = {c.lower() for c in dpw.COLORS} - {"clear"}
DOCS = Path(__file__).resolve().parents[1] / "docs"


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return ceiling_build().records


@pytest.fixture(scope="module")
def by_id(ceiling: list[dict]) -> dict[str, dict]:
    return {r["product_id"]: r for r in ceiling}


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def _cards(ceiling: list[dict]) -> list[dict]:
    return [d for d in ceiling if d["product_type"] == PTYPE and d["product_id"] not in dpw.BY_ID]


def _attrs(doc: dict) -> dict[str, str]:
    return {a["key"]: str(a["value"]) for a in doc["attributes"]}


def _rows() -> list[dpw.Row]:
    return [r for r in dpw.TABLE if r.device_type == PTYPE]


def test_electronics_carries_a_memory_card_type_sold_by_capacity(ceiling: list[dict]) -> None:
    cards = _cards(ceiling)
    assert len(cards) >= 4, [d["title"] for d in cards]
    for doc in cards:
        assert doc["category_path"] == PATH, doc["product_id"]
        attrs = _attrs(doc)
        assert attrs.get("card_format") in {"microSD", "SD"}, (doc["product_id"], attrs)
        assert attrs["card_format"].lower() in tokens(doc["title"]), (doc["title"], attrs)
        assert attrs.get("speed_class"), (doc["product_id"], attrs)
        capacities = {s.get("storage_gb") for s in doc["skus"]}
        assert None not in capacities and len(capacities) >= 2, (doc["product_id"], capacities)
    assert {_attrs(d)["card_format"] for d in cards} == {"microSD", "SD"}


def test_the_memory_card_has_a_drawing_of_its_own(ceiling: list[dict]) -> None:
    assert "memory_card" in kit.SHAPES
    cards = _cards(ceiling)
    assert cards
    for doc in cards:
        assert doc["drawing"]["shape"] == "memory_card", doc["product_id"]
        image_release.render(doc, doc["skus"][0])


def test_the_memory_card_has_at_least_two_word_decoys() -> None:
    rows = _rows()
    assert len(rows) >= 2, len(rows)
    assert all(r.decoy and r.policy and r.query == QUERY and r.noun == "memory" for r in rows)
    assert len({r.kind for r in rows}) == len(rows)
    assert TRUE_NODE.get("memory") == PATH[-1]


def test_each_decoy_holds_the_words_and_is_another_product(by_id: dict[str, dict]) -> None:
    rows = _rows()
    assert rows
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        assert {"memory", "card"} <= set(tokens(doc["title"])), (row.code, doc["title"])
        assert doc["product_type"] != PTYPE, row.code
        assert PATH[-1] not in doc["category_path"], row.code
        # a decoy of another department is dropped by the department policy; one that sits in
        # Electronics by the category policy
        assert (doc["category_path"][0] == "Electronics") == (row.policy == "category"), row.code
        words = set(re.findall(r"[a-z]+", f"{doc['title']} {doc['description']}".lower()))
        assert not words & COLOR_WORDS, (row.code, words & COLOR_WORDS)


def test_the_card_game_and_the_greeting_card_are_cross_department_card_words(
    ceiling: list[dict],
) -> None:
    games = [d for d in ceiling if "Memory Card Game" in d["title"]]
    assert games
    assert all(d["product_type"] == "Board Game" and d["category_path"][0] == "Toys" for d in games)
    greetings = [d for d in ceiling if d["product_type"] == "Greeting Card"]
    assert greetings
    assert all(d["category_path"][0] == "Gifts" for d in greetings)


def _shopper_view(index: br.Index, query: str, department: str) -> list[dict]:
    """The results after the policies that fix the class-8 decoys: the department kept, the decoy
    rows of :data:`dpw.BY_ID` dropped."""
    return [
        d
        for d in br.rank(index, query, 1000)
        if d["category_path"][0] == department and d["product_id"] not in dpw.BY_ID
    ]


def test_a_memory_card_search_ranks_a_memory_card_first(index: br.Index) -> None:
    view = _shopper_view(index, QUERY, "Electronics")[:5]
    assert view and view[0]["product_type"] == PTYPE, [(d["product_id"], d["title"]) for d in view]
    # without a policy, too, a memory card outranks every greeting card and the card game
    types = [d["product_type"] for d in br.rank(index, QUERY, 1000)]
    assert PTYPE in types, types[:10]
    first = types.index(PTYPE)
    assert "Greeting Card" not in types[:first] and "Board Game" not in types[:first], types[:10]


def test_a_greeting_card_search_ranks_no_memory_card_above_a_greeting_card(
    index: br.Index,
) -> None:
    types = [d["product_type"] for d in br.rank(index, "greeting card", 1000)]
    assert types and types[0] == "Greeting Card", types[:10]
    view = [d["product_type"] for d in _shopper_view(index, "greeting card", "Gifts")]
    assert PTYPE not in view, view[:10]


def test_the_docs_state_the_rule() -> None:
    page = DOCS / "retail-product-word-decoys" / "memory-card-796.md"
    assert page.is_file(), page
    text = page.read_text(encoding="utf-8")
    assert "Memory Cards" in text and "memory card" in text
    assert "Memory Cards" in (DOCS / "retail-electronics.md").read_text(encoding="utf-8")
