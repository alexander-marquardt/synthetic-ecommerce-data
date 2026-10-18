"""Clothing and shoe seed queries meet decoys that hold EVERY word of the phrase (gen#460).

The homepage seed queries are two or three words ("leather boots", "skinny jeans", "tea dress")
and the Best tier requires every term, so a decoy with the bare noun ("Boot Hill Dress") never
meets them. A seed-serving decoy is a class-8 row (:mod:`decoy_product_words`) whose title or
text holds every word of the phrase and whose true type is not the seed's: a jeans belt, a
doll's denim jacket outfit, a leather boot care kit. Its structured fields tell the truth, so a
department or category policy drops it. The measure is the prototype's no-policy ranking with
every query word required (the Best tier's ``minimum_should_match`` of 100%), over the ceiling
build; the live number is read on the next loaded index.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_apparel  # noqa: E402
import decoy_product_words as dpw  # noqa: E402
import decoy_rows  # noqa: E402
import scale  # noqa: E402
from distractors import tokens  # noqa: E402

#: seed phrase -> the product types the shopper means by it (a decoy is never one of them).
SEEDS = {
    "high rise jeans": {"Jeans"},
    "skinny jeans": {"Jeans"},
    "jeans": {"Jeans"},
    "barrel trousers": {"Trousers", "Mens Trousers"},
    "tea dress": {"Tea Dress", "Dress"},
    "denim jacket": {"Denim Jacket", "Jacket"},
    "womens boat neck top": {"Top", "Knitted Top", "Blouse", "Tee", "T-Shirt"},
    "pyjamas": {"Pyjamas", "Pyjama Shorts"},
    "leather boots": {"Ankle Boots", "Chelsea Boots", "Chukka Boots", "Knee High Boots",
                      "Safety Boots", "Walking Boots", "Wellies"},
    "running shoes": {"Running Shoes", "Trainers", "Plimsolls"},
    "brogues": {"Brogues"},
    "navy dresses": {"Dress", "Tea Dress"},
    "large dresses": {"Dress", "Tea Dress"},
}  # fmt: skip
FIRST = 12
POLICIES = ("category", "department")
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


def _rows(seed: str) -> list[dpw.Row]:
    return [r for r in dpw.TABLE if seed in r.seeds]


def _first(index: br.Index, seed: str) -> list[dict]:
    """The first documents for the seed with policies off and every query word required."""
    words = set(tokens(seed))
    hits = br.rank(index, seed, len(index.catalog))
    keep = [d for d in hits if words <= set(tokens(d["title"] + " " + d.get("description", "")))]
    return keep[:FIRST]


def test_the_seed_pool_is_the_one_the_rows_name() -> None:
    """A row naming a seed outside the pool, or a pool seed no row serves, reds here."""
    named = {s for r in dpw.TABLE for s in r.seeds}
    assert named == set(SEEDS), named ^ set(SEEDS)


def test_the_bare_noun_seed_boot_keeps_its_class_8_rows() -> None:
    """'boot' was already served (Black Boot Polish, Boot Hill Dress): the rows stay."""
    assert sum(r.noun == "boot" for r in dpw.TABLE) >= 2


@pytest.mark.parametrize("seed", sorted(SEEDS))
def test_a_seed_has_at_least_two_decoy_products(seed: str) -> None:
    rows = _rows(seed)
    assert len(rows) >= 2, (seed, len(rows))
    assert len({r.title for r in rows}) == len(rows), seed
    assert all(r.decoy and r.query and r.policy.split(":")[0] in POLICIES for r in rows), seed


@pytest.mark.parametrize("seed", sorted(SEEDS))
def test_a_seed_meets_two_decoy_products_in_the_first_12(index: br.Index, seed: str) -> None:
    mine = {f"PLT-{r.code}" for r in _rows(seed)}
    met = {d["product_id"] for d in _first(index, seed)} & mine
    assert len(met) >= 2, (seed, sorted(met), [d["title"] for d in _first(index, seed)])


@pytest.mark.parametrize("seed", sorted(SEEDS))
def test_each_decoy_holds_every_word_of_its_seed_and_is_another_type(
    by_id: dict[str, dict], seed: str
) -> None:
    rows = _rows(seed)
    assert rows, seed
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        text = set(tokens(doc["title"] + " " + doc["description"]))
        assert set(tokens(seed)) <= text, (row.code, seed, doc["title"])
        assert doc["product_type"] not in SEEDS[seed], (row.code, doc["product_type"])
        assert len(doc["title"].split()) <= 5, doc["title"]


@pytest.mark.parametrize("seed", sorted(SEEDS))
def test_a_decoy_names_only_the_color_it_shows(by_id: dict[str, dict], seed: str) -> None:
    """A color word in a title or text is the product's own color (#444): never a stray one."""
    rows = _rows(seed)
    assert rows, seed
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        words = set(re.findall(r"[a-z]+", f"{doc['title']} {doc['description']}".lower()))
        assert words & COLOR_WORDS <= {row.color.lower()}, (row.code, words & COLOR_WORDS)


def test_no_real_class_of_the_seed_pool_is_planted() -> None:
    """The planted ids stay out of the derivation (they are templates) like every class-8 row."""
    mine = {f"PLT-{r.code}" for r in dpw.TABLE if r.seeds}
    assert mine <= dpw.IDS
    assert not mine & (decoy_rows.IDS | decoy_apparel.IDS)
