"""Decoys whose titles hold every word of "mens black jeans" and "white minimiser bras" (gen#711).

The live head tier keeps only products that hold every query word. A decoy that lacks one of
the three words never reaches the first page with interpretation off, so that page led with the
real product both with interpretation off and with it on. These rows are class 8 of
:mod:`decoy_product_words` (``feature_decoys/all_words_jeans_bras.py``): an accessory or a
companion that a shop names after the product. The checks hold that each title has every query
word, that each row is an ordinary product of a type the build already sells (its leaf and its
price band), that none sits in the queried category, and that the no-policy baseline puts one in
the top 10.
"""

from __future__ import annotations

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

#: query -> the category node of the product it names: no decoy of the query sits in it.
QUERIES = {"mens black jeans": "Jeans", "white minimiser bras": "Bras"}

#: query -> how many all-words decoys it holds: the jeans query has the two belts, the hangers
#: and the denim shirt; the bras query has the wash bag, the travel case and the briefs.
FLOOR = {"mens black jeans": 4, "white minimiser bras": 3}


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def by_id(ceiling: list[dict]) -> dict[str, dict]:
    return {r["product_id"]: r for r in ceiling}


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def _rows(query: str) -> list[dpw.Row]:
    return [r for r in dpw.TABLE if r.query == query]


def _decoy_ids() -> set[str]:
    return {pid for pid, row in dpw.BY_ID.items() if row.decoy}


@pytest.mark.parametrize("query", sorted(QUERIES))
def test_each_query_has_three_decoys_whose_title_holds_every_word(query: str) -> None:
    """The guard: a query that loses its all-words decoys fails here."""
    rows = _rows(query)
    assert len(rows) >= FLOOR[query], (query, [r.title for r in rows])
    for row in rows:
        assert set(tokens(query)) <= set(tokens(row.title)), (row.code, row.title)
        assert row.decoy and row.policy == "category", row.code


@pytest.mark.parametrize("query", sorted(QUERIES))
def test_no_decoy_sits_in_the_category_the_query_names(
    query: str, by_id: dict[str, dict]
) -> None:
    node = QUERIES[query]
    rows = _rows(query)
    assert rows, query
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        assert node not in doc["category_path"], (row.code, doc["category_path"])
        assert tokens(doc["product_type"]) != tokens(node), row.code


@pytest.mark.parametrize("query", sorted(QUERIES))
def test_each_decoy_is_a_type_the_build_sells_in_its_leaf_and_price_band(
    query: str, ceiling: list[dict], by_id: dict[str, dict]
) -> None:
    """No made-up type: two or more ordinary products share the type and the leaf, and the
    decoy's price sits between their cheapest and their dearest."""
    decoys = _decoy_ids()
    rows = _rows(query)
    assert rows, query
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        peers = [
            d["price"]
            for d in ceiling
            if d["product_type"] == doc["product_type"]
            and d["category_path"] == doc["category_path"]
            and d["product_id"] not in decoys
        ]
        assert len(peers) >= 2, (row.code, doc["product_type"], doc["category_path"])
        assert min(peers) <= doc["price"] <= max(peers), (row.code, doc["price"], peers)
        assert doc["drawing"]["shape"] == row.shape, row.code


@pytest.mark.parametrize("query", sorted(QUERIES))
def test_a_title_is_short_and_names_each_word_once(query: str) -> None:
    for row in _rows(query):
        words = tokens(row.title)
        assert 4 <= len(row.title.split()) <= 5, row.title
        assert len(words) == len(set(words)), row.title


@pytest.mark.parametrize("query", sorted(QUERIES))
def test_the_baseline_top_10_holds_one_of_the_new_decoys(query: str, index: br.Index) -> None:
    mine = {f"PLT-{r.code}" for r in _rows(query)}
    assert mine, query
    top = [d["product_id"] for d in br.rank(index, query, 10)]
    assert mine & set(top), (query, top)
