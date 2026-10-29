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

from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import (
    decoy_apparel,
    decoy_rows,
    scale,
)
from synthetic_ecommerce_data.domains.retail import decoy_product_words as dpw
from synthetic_ecommerce_data.domains.retail.distractors import tokens

ROOT = Path(__file__).resolve().parents[1]


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


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


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
def test_a_seed_meets_two_decoy_products_in_the_first_12(index: br.Index, seed: str) -> None:
    mine = {f"PLT-{r.code}" for r in _rows(seed)}
    met = {d["product_id"] for d in _first(index, seed)} & mine
    assert len(met) >= 2, (seed, sorted(met), [d["title"] for d in _first(index, seed)])


def test_no_real_class_of_the_seed_pool_is_planted() -> None:
    """The planted ids stay out of the derivation (they are templates) like every class-8 row."""
    mine = {f"PLT-{r.code}" for r in dpw.TABLE if r.seeds}
    assert mine <= dpw.IDS
    assert not mine & (decoy_rows.IDS | decoy_apparel.IDS)
