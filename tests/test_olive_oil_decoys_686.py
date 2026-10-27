"""A plain "olive oil" search meets short-titled foods that are not olive oil (gen#686).

On public grocery sites a search for ``olive oil`` returns pesto, tinned fish and fries cooked
in olive oil near the top: the title holds both words and is as short as an olive oil's. The
module ``feature_decoys/olive_oil.py`` plants those foods (class 10 of :mod:`decoy_rows`: the
phrase names an ingredient of another food). Each is filed, typed and drawn as what it is, never
under Olive Oil, and its codes sit in a DY block of their own.
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
import decoy_product_words as dpw  # noqa: E402
import decoy_rows as dr  # noqa: E402
import scale  # noqa: E402
from feature_decoys import olive_oil  # noqa: E402

QUERY = "olive oil"
OLIVE_OIL = ["Food & Drink", "Food Cupboard", "Olive Oil"]
BLOCK = re.compile(r"PLT-DY686\d")

#: title -> (category path, product type, drawing shape): what each decoy really is.
TRUTH = {
    "Pesto with Olive Oil": (
        ["Food & Drink", "Food Cupboard", "Sauces & Condiments"], "Sauce", "jar"),
    "Fries Cooked in Olive Oil": (
        ["Food & Drink", "Frozen", "Frozen Vegetables"], "Frozen Vegetables", "bag"),
    "Sardines in Olive Oil": (["Food & Drink", "Food Cupboard", "Tinned"], "Tinned Food", "tin"),
    "Tuna in Olive Oil": (["Food & Drink", "Food Cupboard", "Tinned"], "Tinned Food", "tin"),
    "Sun-Dried Tomatoes in Olive Oil": (
        ["Food & Drink", "Food Cupboard", "Sauces & Condiments"], "Pickle", "jar"),
    "Olive Oil Spread": (
        ["Food & Drink", "Dairy & Alternatives", "Butter & Spreads"], "Butter & Spreads", "jar"),
    "Crisps Cooked in Olive Oil": (
        ["Food & Drink", "Biscuits & Snacks", "Crisps"], "Crisps", "crisps_bag"),
}


@cache
def _codes() -> frozenset[str]:
    return frozenset(olive_oil.decoy_rows(lambda code, *_a, **_k: code))


@cache
def _docs() -> tuple[dict, ...]:
    ids = {f"PLT-D{c}" for c in _codes()}
    return tuple(d for d in dr.docs() if d["product_id"] in ids)


def _by_title() -> dict[str, dict]:
    return {d["title"]: d for d in _docs()}


@pytest.mark.parametrize("title", sorted(TRUTH))
def test_each_decoy_is_filed_typed_and_drawn_as_what_it_is(title: str) -> None:
    doc = _by_title().get(title)
    assert doc is not None, title
    path, product_type, shape = TRUTH[title]
    assert doc["category_path"] == path
    assert doc["department"] == ["Food & Drink"]
    assert doc["product_type"] == product_type
    assert doc["drawing"]["shape"] == shape


def test_every_title_holds_olive_oil_and_none_is_an_olive_oil() -> None:
    docs = _docs()
    assert len(docs) == len(TRUTH)
    for d in docs:
        assert QUERY in d["title"].lower(), d["title"]
        assert d["category_path"] != OLIVE_OIL, d["title"]
        assert "Olive Oil" not in d["category_path"], d["title"]
        assert d["product_type"] != "Olive Oil", d["title"]


def test_titles_and_descriptions_are_short() -> None:
    docs = _docs()
    assert docs
    for d in docs:
        assert len(d["title"].split()) <= 6, d["title"]
        assert len(d["description"].split()) <= 12, d["description"]


def test_every_row_is_a_class_10_decoy_of_the_olive_oil_query() -> None:
    rows = [r for r in dr.TABLE if r.code in _codes()]
    assert len(rows) == len(TRUTH)
    assert all(r.cls == 10 and r.query == QUERY and not r.true_hit for r in rows)


def test_the_codes_are_a_dy_block_of_their_own() -> None:
    ids = {f"PLT-D{c}" for c in _codes()}
    assert len(ids) == len(TRUTH)
    assert all(BLOCK.fullmatch(i) for i in ids), sorted(ids)
    others = (set(dr.BY_ID) - ids) | {f"PLT-{r.code}" for r in dpw.TABLE}
    assert not {i for i in others if i.startswith("PLT-DY686")}


def test_a_plain_olive_oil_search_ranks_decoys_in_the_top_10() -> None:
    index = br.Index(scale.build(10**6).records)
    top = [d["title"] for d in br.rank(index, QUERY, 10)]
    assert len([t for t in top if t in TRUTH]) >= 3, top
