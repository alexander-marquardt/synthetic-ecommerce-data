"""Retail cups (gen#620): realistic cup titles, a drawing of its own per cup kind, Cup-named bras.

A shopper's ``cup`` meets drinkware (gen#125 class 15 routes it) and, in the bare baseline, the
cup of a bra. Before this change the real cups were short ("Leakproof Travel Cup") and all drawn
with ``mug()``, and no bra was named for its cup in a short, believable title. Now:

* every real cup carries a realistic title of 6 to 10 words (material, size, use), so a short decoy
  outscores it on a bare ``cup`` and the policy has something to fix;
* every cup kind has a drawing function of its own (a mug keeps ``mug``);
* the Cup-named bras are class-8 decoys in the bra category (gen#326, the #444 believability rule:
  the fields tell the truth, only the title misleads), their titles short and holding ``cup``.

Builds on gen#165 (bra styles are facets, so a "Full Cup Bra" sits under its leaf) and relates to
gen#520 and gen#508 (the plural-cups bras).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import kit  # noqa: E402
import scale  # noqa: E402
from distractors import tokens  # noqa: E402

#: The product type of each cup kind that is not a mug, and the drawing it must have.
CUP_KINDS = {
    "Party Cup": "party_cup",
    "Paper Cup": "paper_cup",
    "Travel Cup": "travel_cup",
    "Tumbler": "tumbler",
    "Sippy Cup": "sippy_cup",
    "Measuring Cup": "measuring_cup",
    "Cup": "tea_cup",
    "Cup Set": "espresso_cup",
}
BRA_PREFIX = ("Womens", "Lingerie", "Bras")
MIN_DECOYS = 3


@pytest.fixture(scope="module")
def docs() -> list[dict]:
    return scale.templates()


def _of(docs: list[dict], product_type: str) -> list[dict]:
    return [d for d in docs if d["product_type"] == product_type]


def _decoys(docs: list[dict]) -> list[dict]:
    """The Cup-named bras: a bra by path and type, with ``cup`` in a title of at most 5 words."""
    return [
        d
        for d in docs
        if tuple(d["category_path"][:3]) == BRA_PREFIX
        and "cup" in tokens(d["title"])
        and len(d["title"].split()) <= 5
    ]


@pytest.mark.parametrize("product_type", sorted(CUP_KINDS))
def test_real_cup_titles_are_realistic_six_to_ten_words(
    docs: list[dict], product_type: str
) -> None:
    cups = _of(docs, product_type)
    assert cups, f"no {product_type} in the catalogue"
    for d in cups:
        n = len(d["title"].split())
        assert 6 <= n <= 10, f"{d['product_id']} {d['title']!r} has {n} words"


@pytest.mark.parametrize("product_type", sorted(CUP_KINDS))
def test_every_cup_kind_has_a_drawing_of_its_own(docs: list[dict], product_type: str) -> None:
    shapes = {d["drawing"]["shape"] for d in _of(docs, product_type)}
    assert shapes == {CUP_KINDS[product_type]}, product_type
    assert CUP_KINDS[product_type] in kit.SHAPES


def test_the_cup_kinds_do_not_share_a_drawing_and_none_is_the_mug(docs: list[dict]) -> None:
    assert len(set(CUP_KINDS.values())) == len(CUP_KINDS)
    assert "mug" not in CUP_KINDS.values()
    mugs = _of(docs, "Mug")
    shapes = {d["drawing"]["shape"] for d in mugs}
    assert "mug" in shapes and shapes <= {"mug", "gift_mug"}, shapes
    assert not shapes & set(CUP_KINDS.values())


def test_cup_named_bras_are_bras_with_cup_in_a_short_title(docs: list[dict]) -> None:
    ids = {d["product_id"] for d in _decoys(docs) if d["product_id"].startswith("PLT-DY")}
    assert len(ids) >= MIN_DECOYS, sorted(ids)
    for d in _decoys(docs):
        if not d["product_id"].startswith("PLT-DY"):
            continue
        assert d["product_type"] == "Bra", d["product_id"]
        assert "cup" in tokens(d["title"]), d["title"]


def test_a_bare_cup_ranks_the_decoys_above_every_real_cup(docs: list[dict]) -> None:
    top = br.rank(br.Index(docs), "cup", 12)
    decoy_ids = {d["product_id"] for d in _decoys(docs) if d["product_id"].startswith("PLT-DY")}
    assert len([d for d in top if d["product_id"] in decoy_ids]) >= MIN_DECOYS
    real = {d["product_id"] for pt in CUP_KINDS for d in _of(docs, pt)}
    assert not [d["product_id"] for d in top if d["product_id"] in real]
