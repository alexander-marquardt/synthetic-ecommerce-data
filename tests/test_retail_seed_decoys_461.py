"""Home, beauty, food, garden and toy seed queries meet decoys (gen#461).

The two-word seed queries ("duvet cover", "lipstick", "lemon drizzle cake") need every term in
the Best tier, so the bare-noun decoys of gen#326 never met them. Each seed here has at least two
decoy products in the first twelve hits, with policies off: a real product of its own type whose
name holds the whole seed phrase. The first twelve are measured on the prototype's plain text
ranking (:mod:`baseline_rank`) narrowed to the documents that hold every seed word, the shape of
the live cross_fields query with minimum_should_match 100%.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import decoy_product_words as dpw
from synthetic_ecommerce_data.domains.retail.distractors import tokens

ROOT = Path(__file__).resolve().parents[1]


FIRST = 12
#: seed query -> the category leaves of the product the seed really names.
SEEDS = {
    "duvet cover": {"Duvet Covers"},
    "mattress topper": {"Mattress Toppers"},
    "bed frame": {"Beds"},
    "tea towels": {"Tea Towels"},
    "lipstick": {"Lipstick"},
    "foundation": {"Foundation"},
    "lemon drizzle cake": {"Cakes"},
    "gift hamper": {"Hampers"},
    "olive tree": {"Olive Trees", "Gift Plants"},
}
#: Mattress topper is served by the protectors of gen#155 (distractor_rows): no new row.
SERVED_BY_EXISTING = {"mattress topper": "Mattress Protectors"}
_ID = lambda s: s.replace(" ", "_")  # noqa: E731 -- a space would split a Red-Test id


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return ceiling_build().records


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


@pytest.fixture(scope="module")
def by_id(ceiling: list[dict]) -> dict[str, dict]:
    return {r["product_id"]: r for r in ceiling}


def first_hits(index: br.Index, query: str, n: int = FIRST) -> list[dict]:
    """The first ``n`` documents that hold every query word, in the plain text ranking."""
    words = tokens(query)
    out = []
    for doc in br.rank(index, query, 10**6):
        text = set(tokens(doc["title"])) | set(tokens(doc.get("description", "")))
        if all(w in text for w in words):
            out.append(doc)
        if len(out) == n:
            break
    return out


def _seed_rows(seed: str) -> list[dpw.Row]:
    return [r for r in dpw.TABLE if r.seed == seed]


@pytest.mark.parametrize("seed", SEEDS, ids=_ID)
def test_a_seed_query_meets_two_decoy_products_in_its_first_12(
    index: br.Index, seed: str
) -> None:
    ids = {f"PLT-{r.code}" for r in _seed_rows(seed)}
    leaf = SERVED_BY_EXISTING.get(seed)
    decoys = [
        d["product_id"]
        for d in first_hits(index, seed)
        if d["product_id"] in ids or (leaf and d["category_path"][-1] == leaf)
    ]
    assert len(decoys) >= 2, (seed, decoys)


def test_the_olive_tree_is_a_product_and_ranks_in_the_first_12(index: br.Index) -> None:
    top = first_hits(index, "olive tree")
    assert any(d["category_path"][-1] == "Olive Trees" for d in top), [d["title"] for d in top]


def test_dinosaur_toys_titled_dinosaur_first_outrank_the_tees(index: br.Index) -> None:
    top = first_hits(index, "dinosaur")
    toys = [d for d in top if d["category_path"][0] == "Toys" and d["title"].startswith("Dinosaur")]
    assert len(toys) >= 2, [d["title"] for d in top]
    assert all(top.index(t) < 3 for t in toys[:2]), [d["title"] for d in top]


def test_a_seed_decoy_title_that_names_a_pack_count_matches_its_pack_size(
    by_id: dict[str, dict],
) -> None:
    """No deliberately wrong data: "4 Pack" in a title is a pack_size of "4 pack"."""
    named = 0
    for row in dpw.TABLE:
        if not row.seed:
            continue
        doc = by_id[f"PLT-{row.code}"]
        m = re.search(r"\b(\d+)\s*pack\b", doc["title"], re.IGNORECASE)
        if not m:
            continue
        named += 1
        sizes = [a["value"] for a in doc["attributes"] if a["key"] == "pack_size"]
        assert sizes == [f"{m[1]} pack"], (row.code, doc["title"], sizes)
    assert named, "no seed decoy names a pack count: the check is vacuous"
