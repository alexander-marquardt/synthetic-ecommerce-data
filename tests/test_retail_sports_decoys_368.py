"""Every Sports & Outdoors type carries text-match decoys (gen#368; the rule of #294, #311).

A sports decoy is a product of another department whose title holds the shopper's word for a
sports product: a block-heel shoe for "yoga block", a lantern-sleeve blouse for "camping lantern",
a tennis bracelet for "tennis racket". The structured fields tell the truth (department, category
path, product type, drawing), so a department or category policy drops it. The rows live in the
class-8 table of :mod:`decoy_product_words` (gen#326) and carry the sports type they mislead in
``target``. This file walks the live catalog's Sports & Outdoors types, so a new type reds here
until it carries at least two decoys or is exempted with a reason.
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
import decoy_product_words as dpw  # noqa: E402
import scale  # noqa: E402
from distractors import tokens  # noqa: E402

ROOT_NAME = "Sports & Outdoors"
#: The seventeen types of the second increment (gen#368), each with its decoys in this PR.
SECOND_INCREMENT = (
    "Yoga Block", "Yoga Strap", "Resistance Band", "Camping Lantern", "Roll Mat", "Bike Pump",
    "Baseball Bat", "Baseball Glove", "Baseball", "Batting Helmet", "Swim Goggles", "Swim Cap",
    "Kickboard", "Swim Armbands", "Football", "Tennis Racket", "Badminton Set",
)  # fmt: skip
#: The seven first-increment types that carry no decoys yet (gen#375 adds them).
FIRST_INCREMENT = {
    "Tent", "Sleeping Bag", "Camping Chair", "Yoga Mat", "Dumbbell", "Kettlebell", "Foam Roller",
}
COLOR_WORDS = {c.lower() for c in dpw.COLORS} - {"clear"}  # glass is clear, not a colour


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def by_id(ceiling: list[dict]) -> dict[str, dict]:
    return {r["product_id"]: r for r in ceiling}


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def _rows(ptype: str) -> list[dpw.Row]:
    return [r for r in dpw.TABLE if r.target == ptype]


def test_every_sports_type_is_planned_or_exempt(ceiling: list[dict]) -> None:
    """A census over the live catalog, not over a list: a new Sports & Outdoors type reds here
    until it carries decoys (or is exempted with a reason that names its follow-up issue)."""
    live = {r["product_type"] for r in ceiling if r["category_path"][0] == ROOT_NAME}
    planned = {r.target for r in dpw.TABLE if r.target}
    assert set(SECOND_INCREMENT) <= live, set(SECOND_INCREMENT) - live
    assert planned, "no sports type is planned"
    assert live - set(dpw.SPORTS_EXEMPT) == planned, (live - set(dpw.SPORTS_EXEMPT)) ^ planned
    assert set(dpw.SPORTS_EXEMPT) <= live
    assert all("#" in reason for reason in dpw.SPORTS_EXEMPT.values())


def test_the_exempt_set_is_the_seven_first_increment_types() -> None:
    """The hatch is pinned: a later type cannot delete its decoys and add its name to the exempt
    dict. Adding a name reds here, so its author edits this set on purpose (gen#375 empties it)."""
    assert set(dpw.SPORTS_EXEMPT) == FIRST_INCREMENT, set(dpw.SPORTS_EXEMPT) ^ FIRST_INCREMENT
    assert set(dpw.SPORTS_EXEMPT.values()) == {"decoys are tracked in #375"}


def test_every_live_non_exempt_sports_type_has_at_least_two_decoys(ceiling: list[dict]) -> None:
    """The two-decoy floor comes from the live catalog, not from the hand-written tuple."""
    live = {r["product_type"] for r in ceiling if r["category_path"][0] == ROOT_NAME}
    short = {t: len(_rows(t)) for t in live - set(dpw.SPORTS_EXEMPT) if len(_rows(t)) < 2}
    assert not short, short


@pytest.mark.parametrize("ptype", SECOND_INCREMENT)
def test_a_second_increment_type_has_at_least_two_decoys(ptype: str) -> None:
    rows = _rows(ptype)
    assert len(rows) >= 2, (ptype, len(rows))
    assert all(r.decoy and r.policy and r.query for r in rows), ptype


@pytest.mark.parametrize("ptype", SECOND_INCREMENT)
def test_each_decoy_holds_the_shoppers_word_and_is_another_product(
    by_id: dict[str, dict], ptype: str
) -> None:
    rows = _rows(ptype)
    assert rows, ptype
    own = set(tokens(ptype))
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        assert row.noun in tokens(doc["title"]), (row.code, doc["title"])
        assert row.noun in own, (row.code, row.noun, ptype)
        assert set(tokens(row.query)) <= set(tokens(doc['title'] + ' ' + doc['description']))
        assert doc["category_path"][0] != ROOT_NAME, row.code
        assert doc["product_type"] != ptype, row.code
        assert ptype not in doc["category_path"], row.code
        assert len(doc["title"].split()) <= 5, doc["title"]


@pytest.mark.parametrize("ptype", SECOND_INCREMENT)
def test_a_decoy_names_no_color_word_the_drawing_does_not_show(
    by_id: dict[str, dict], ptype: str
) -> None:
    """A sports decoy names no misleading color: its title and description carry none at all,
    so the title and the drawing cannot disagree (the rule of the #311 color test)."""
    rows = _rows(ptype)
    assert rows, ptype
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        words = set(re.findall(r"[a-z]+", f"{doc['title']} {doc['description']}".lower()))
        assert not words & COLOR_WORDS, (row.code, words & COLOR_WORDS)


def test_every_sports_decoy_can_be_found_by_its_query_word(
    index: br.Index, by_id: dict[str, dict]
) -> None:
    """Text match is the point: the plain text search meets each decoy on the word it holds."""
    rows = [r for r in dpw.TABLE if r.target]
    assert len(rows) >= 2 * len(SECOND_INCREMENT)
    missing = []
    for row in rows:
        found = {d["product_id"] for d in br.rank(index, row.query, 1000)}
        if f"PLT-{row.code}" not in found:
            missing.append((row.code, row.query))
    assert not missing, missing
