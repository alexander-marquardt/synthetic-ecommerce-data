"""Beach towel text-match decoys (gen#605): products that hold "beach towel" in the title and are
not a beach towel.

Every top result for ``beach towel`` was a real beach towel, so a search for it showed nothing
about how the engine tells a towel from a garment, a robe or a bag that is named for one. The rows
are class 8 of :mod:`decoy_product_words` (gen#326), in ``feature_decoys/beach_towel.py`` (gen#513):
a shopper's phrase on a product of another department, whose structured fields and drawing tell the
truth. Three classes: terry-towelling "beach towel stripe" clothes, kids' hooded towel ponchos and
robes, and a swim shorts and towel set with a tote for the towel. The department policy (Home, the
beach towel's department) drops all of them, so none is in the interpreted "Best" results.
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import decoy_product_words as dpw
from synthetic_ecommerce_data.domains.retail import scale
from synthetic_ecommerce_data.domains.retail.distractors import tokens

QUERY = "beach towel"
PTYPE = "Beach Towel"
PATH_LEAF = "Beach Towels"
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
    return [r for r in dpw.TABLE if r.query == QUERY]


def _docs(by_id: dict[str, dict]) -> list[dict]:
    rows = _rows()
    assert rows
    return [by_id[f"PLT-{r.code}"] for r in rows]


def test_beach_towel_has_eight_to_twelve_decoys_each_fixed_by_the_department() -> None:
    rows = _rows()
    assert 8 <= len(rows) <= 12, len(rows)
    assert all(r.decoy and r.noun == "towel" and r.policy == "department" for r in rows)
    assert len({r.code for r in rows}) == len(rows)


def test_each_decoy_title_holds_beach_and_towel_and_is_no_longer_than_a_towels(
    ceiling: list[dict], by_id: dict[str, dict]
) -> None:
    towels = [d for d in ceiling if d["product_type"] == PTYPE]
    assert towels
    longest = max(len(d["title"]) for d in towels)
    for doc in _docs(by_id):
        assert {"beach", "towel"} <= set(tokens(doc["title"])), doc["title"]
        assert 3 <= len(doc["title"].split()) <= 5, doc["title"]
        assert len(doc["title"]) <= longest, doc["title"]


def test_no_decoy_is_a_beach_towel_or_sits_in_the_homes_towel_aisle(
    by_id: dict[str, dict],
) -> None:
    for doc in _docs(by_id):
        assert doc["product_type"] != PTYPE, doc["product_id"]
        assert PATH_LEAF not in doc["category_path"], doc["product_id"]
        assert doc["category_path"][0] != "Home", doc["product_id"]


def test_the_three_classes_are_each_drawn_as_what_they_really_are(
    by_id: dict[str, dict],
) -> None:
    docs = _docs(by_id)
    stripe = [d for d in docs if "stripe" in tokens(d["title"])]
    assert {d["product_type"] for d in stripe} >= {"Shorts", "Shirt"}, stripe
    assert all(d["category_path"][0] == "Womens" for d in stripe)
    kids = [d for d in docs if d["audience"] == "kids"]
    assert len(kids) >= 2
    for d in kids:
        assert d["product_type"] == "Dressing Gown", d["title"]
        assert d["drawing"]["shape"] == "dressing_gown", d["title"]
        assert d["drawing"]["params"]["fabric"] == "towelling", d["title"]
        assert d["drawing"]["params"]["hood"] == "yes", d["title"]
    kids_titles = " ".join(d["title"] for d in kids)
    assert "Poncho" in kids_titles and "Robe" in kids_titles
    by_type = {d["product_type"]: d for d in docs}
    assert "Set" in by_type["Swim Shorts"]["title"]
    assert by_type["Swim Shorts"]["drawing"]["shape"] == "swim_shorts"
    assert "Bag" in by_type["Tote Bag"]["title"]
    assert by_type["Tote Bag"]["drawing"]["shape"] == "tote_bag"


def test_a_stripe_decoy_is_drawn_striped(
    by_id: dict[str, dict],
) -> None:
    """The Pattern facet is the pattern the drawing shows (scale.py), so it must be drawn."""
    docs = _docs(by_id)
    stripe = [d for d in docs if "stripe" in tokens(d["title"]) or d.get("pattern") == "stripe"]
    assert len(stripe) == 3, [d["title"] for d in stripe]
    for d in stripe:
        assert d["drawing"]["pattern"] == "stripe", (d["title"], d["drawing"])
        assert d["pattern"] == "stripe", d["title"]
        assert d["drawing"]["accent"] != d["drawing"]["base"], d["title"]


def test_the_towelling_shorts_state_towelling_as_their_fabric(by_id: dict[str, dict]) -> None:
    """A description of terry towelling over a jersey fabric attribute contradicts itself."""
    d = by_id["PLT-DY6050"]
    assert "towelling" in d["description"].lower()
    fabric = [a["value"] for a in d["attributes"] if a["key"] == "fabric"]
    assert fabric == ["Towelling"], fabric


def test_a_decoy_names_no_color_word_the_drawing_does_not_show(by_id: dict[str, dict]) -> None:
    for doc in _docs(by_id):
        words = set(re.findall(r"[a-z]+", f"{doc['title']} {doc['description']}".lower()))
        assert not words & COLOR_WORDS, (doc["product_id"], words & COLOR_WORDS)


def test_every_decoy_can_be_found_by_its_query(index: br.Index) -> None:
    rows = _rows()
    assert rows
    found = {d["product_id"] for d in br.rank(index, QUERY, 1000)}
    for row in rows:
        assert f"PLT-{row.code}" in found, row.code


def test_the_raw_top_12_for_beach_towel_holds_at_least_three_decoys(index: br.Index) -> None:
    mine = {f"PLT-{r.code}" for r in _rows()}
    top = br.rank(index, QUERY, 12)
    assert len([d for d in top if d["product_id"] in mine]) >= 3, [
        (d["product_id"], d["title"]) for d in top
    ]
    # the type itself is present: which real towels reach the top 12 is other PRs' ranking, not
    # this PR's claim
    assert any(d["product_type"] == PTYPE for d in br.rank(index, QUERY, 1000))


def test_the_department_policy_leaves_only_home_products_and_none_of_the_decoys(
    index: br.Index,
) -> None:
    """Interpreted as Home (the beach towel's department) the decoys are dropped: none of them is
    in the Home view at any rank; the Home view still holds the Beach Towel type."""
    mine = {f"PLT-{r.code}" for r in _rows()}
    view = [d for d in br.rank(index, QUERY, 1000) if d["category_path"][0] == "Home"]
    assert any(d["product_type"] == PTYPE for d in view), [d["title"] for d in view[:12]]
    assert not [d for d in view if d["product_id"] in mine], [d["title"] for d in view[:12]]
    assert mine, "the decoys exist"
