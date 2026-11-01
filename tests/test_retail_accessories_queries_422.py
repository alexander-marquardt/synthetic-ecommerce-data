"""Retail accessories as a whole (gen#422): the query shapes the issue lists, over the export.

Each type's own file (``tests/test_retail_belt_422.py`` and its five neighbors) holds that type.
This file holds the issue's three "Done when" lines that no single type can: every listed query
shape returns its type first on the built catalogue, the words a non-accessory shares ("belt" on a
tool kit, "cap" on a bottle or a pen) never beat the accessory, and the department grew by at
least 150 SKUs.

A query is ranked by text score alone (``popular=False``), because a seeded sales draw must not
decide which TYPE a query's words find (#432). A text-match decoy is planted to outrank the type on
purpose (gen#294), so the first hit that counts is the first that is no decoy.
"""

from __future__ import annotations

from collections import Counter

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import type_registry

#: Every query shape of the issue, and the product type it must find first.
QUERIES = {
    "black leather belt": "Belt",
    "mens belt 34 inch": "Belt",
    "red beanie": "Hat",
    "white baseball cap": "Hat",
    "silk scarf": "Scarf",
    "touchscreen gloves": "Gloves",
    "polarised sunglasses": "Sunglasses",
    "aviator sunglasses": "Sunglasses",
    "rfid wallet": "Wallet",
    "card holder": "Wallet",
}
#: The issue's six product types: the department's growth, and the 161 SKUs it started from.
TYPES = ("Belt", "Hat", "Scarf", "Gloves", "Sunglasses", "Wallet")
GROWTH = 150
#: Query -> the accessory it must find, and the non-accessories that share its word.
WORD_DECOYS = {
    "leather belt": ("Belt", {"PLT-DY4220"}),
    "white baseball cap": ("Hat", {"PLT-DY4221", "PLT-DY4222"}),
    "silk scarf": ("Scarf", {"PLT-DY4223", "PLT-DY4224"}),
}


def _is_decoy(doc: dict, decoys: frozenset[str]) -> bool:
    return doc["product_id"].startswith("PLT-D") or doc["product_id"] in decoys


@pytest.fixture(scope="module")
def index() -> br.Index:
    return br.Index(ceiling_build().records)


@pytest.mark.parametrize("query", QUERIES)
def test_the_listed_query_returns_its_type_first(index: br.Index, query: str) -> None:
    decoys = type_registry.text_match_decoy_ids()
    top = br.rank(index, query, size=200, popular=False)
    first = next((d for d in top if not _is_decoy(d, decoys)), None)
    assert first and first["product_type"] == QUERIES[query], [d["title"] for d in top[:12]]


@pytest.mark.parametrize("query", WORD_DECOYS)
def test_a_non_accessory_that_shares_the_word_never_beats_the_accessory(
    index: br.Index, query: str
) -> None:
    wanted, ids = WORD_DECOYS[query]
    assert ids <= {d["product_id"] for d in index.catalog}, sorted(ids)
    order = br.rank(index, query, size=2000, popular=False)
    place = {d["product_id"]: n for n, d in enumerate(order)}
    decoys = type_registry.text_match_decoy_ids()
    accessory = next(
        n for n, d in enumerate(order) if d["product_type"] == wanted and not _is_decoy(d, decoys)
    )
    assert all(place.get(i, len(order)) > accessory for i in ids), [d["title"] for d in order[:12]]


def test_the_department_grew_by_at_least_150_skus_across_all_six_types() -> None:
    styles = {i for s in type_registry.specs().values() for i in type_registry.ids_of(s)}
    skus: Counter[str] = Counter()
    for doc in ceiling_build().records:
        if doc["product_id"] in styles and doc["product_type"] in TYPES:
            skus[doc["product_type"]] += doc["sku_count"]
    assert all(skus[t] for t in TYPES), skus
    assert sum(skus.values()) >= GROWTH, skus
