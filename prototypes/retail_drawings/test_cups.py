"""Class 15 of gen#125: "cups", one word with a sense in two departments.

A bare "cups" means drinkware in Home, and the cup of a bra (or a cup size)
in Lingerie. Bras whose titles say "Cup" outsell the drinkware, so without a
policy they win. The policy routes a bare cup(s) to the drinkware node and
switches off when a bra word is in the query ("d cup bra" stays with bras).

Run: ``uv run pytest prototypes/retail_drawings/test_cups.py``.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import real_classes as rc  # noqa: E402

CLASS_DOCS = rc.class_docs()
CORPUS = rc.corpus()
PROOF = json.loads((HERE / "real_classes_proof.json").read_text(encoding="utf-8"))
DRINKWARE = "Home/Kitchen & Dining/Drinkware"


def _cups() -> rc.ClassRow:
    rows = [r for r in rc.ROWS if r.query == "cups"]
    assert len(rows) == 1
    return rows[0]


def _doc(code: str) -> dict:
    return next(d for d in CLASS_DOCS if d["product_id"] == f"PLT-{code}")


def test_cups_is_class_15_with_drinkware_targets_and_a_bra_control() -> None:
    row = _cups()
    assert (row.n, len(row.targets), len(row.distractors)) == (15, 6, 7)
    assert [(c.query, c.intended) for c in row.controls] == [("d cup bra", "a bra")]


def test_the_targets_are_mugs_cups_a_travel_cup_and_a_set_and_only_some_say_cup() -> None:
    docs = [_doc(s.code) for s in _cups().targets]
    assert sorted(d["product_type"] for d in docs) == [
        "Cup", "Cup Set", "Mug", "Mug", "Travel Cup", "Tumbler"]  # fmt: skip
    for d in docs:
        assert d["department"] == ["Home"]
        assert "/".join(d["category_path"]).startswith(DRINKWARE + "/"), d["product_id"]
    says_cup = [d for d in docs if "cup" in f"{d['title']} {d['description']}".lower()]
    # Most drinkware says mug or tumbler: only the route recalls it.
    assert len(says_cup) == 3


def test_the_bras_say_cup_in_the_title_and_outsell_every_drinkware_target() -> None:
    row = _cups()
    bras = [_doc(s.code) for s, _ in row.distractors if s.product_type == "Bra"]
    assert len(bras) == 4
    assert sum("Cup" in d["title"] for d in bras) == 3
    assert {d["department"][0] for d in bras} == {"Lingerie & Nightwear"}
    best_cup = max(_doc(s.code)["sold_last_5_days"] for s in row.targets)
    assert min(d["sold_last_5_days"] for d in bras) > 5 * best_cup
    # Popular, yet below the bestseller badge: the old rows' top 15 is untouched.
    assert all(d["bestseller_rank"] > rc.BESTSELLER_TOP for d in bras)
    # A bra is sized band x cup: the cup letters its title states.
    demi = _doc("CUPDEM")
    assert {s["size"][-1] for s in demi["skus"]} == set("ABCDE")


def test_the_tail_holds_three_more_senses_outside_the_drinkware_node() -> None:
    tail = [_doc(s.code) for s, _ in _cups().distractors if s.product_type != "Bra"]
    assert sorted(d["product_type"] for d in tail) == ["Cup Holder", "Cupcake Cases", "Trophy"]
    for d in tail:
        assert not "/".join(d["category_path"]).startswith(DRINKWARE), d["product_id"]
        assert "cup" in f"{d['title']} {d['description']}".lower()


@pytest.mark.parametrize("query", ["d cup bra", "bra", "cup bras", "34dd cup", "demi cups",
                                   "balcony cups", "lace bra a-e", "a-e"])  # fmt: skip
def test_a_bra_word_switches_the_cups_policy_off(query: str) -> None:
    assert not _cups().policy.applies(query)


@pytest.mark.parametrize("query", ["cups", "cup", "travel cups", "a set of cups", "tea cup"])
def test_a_bare_cup_keeps_the_cups_policy_on(query: str) -> None:
    assert _cups().policy.applies(query)


def test_the_policy_routes_a_bare_cup_and_runs_a_bra_query_as_the_baseline() -> None:
    row = _cups()
    assert row.policy.route == DRINKWARE
    fs = rc.policy_body(row)["query"]["function_score"]
    assert fs["functions"][-1] == {"filter": {"term": {"category_path_joined": DRINKWARE}},
                                   "weight": rc.ROUTE_WEIGHT}  # fmt: skip
    assert rc.policy_body(row, query="d cup bra") == rc.baseline_body(row, query="d cup bra")
    assert "off when the query says" in row.policy.describe()


def test_the_control_is_a_bra_and_no_drinkware_is() -> None:
    (control,) = _cups().controls
    assert all(control.is_intended(_doc(s.code)) for s, _ in _cups().distractors
               if s.product_type == "Bra")  # fmt: skip
    assert not any(control.is_intended(_doc(s.code)) for s in _cups().targets)


def test_cup_is_in_the_collisions_table_with_both_meanings_and_their_personas() -> None:
    rows = [c for c in rc.COLLISIONS if c["word"] == "cup"]
    assert len(rows) == 1
    cup = rows[0]
    assert cup["query"] == "cups"
    assert cup["senses"] == [DRINKWARE, "Womens/Lingerie/Bras"]
    assert set(cup["meanings"]) == {"Home", "Lingerie & Nightwear"}
    assert set(cup["personas"].values()) == {"Home", "Lingerie & Nightwear"}


def test_the_committed_proof_runs_the_control_with_the_policy_on() -> None:
    assert [r["query"] for r in PROOF.get("controls", [])] == ["d cup bra"]
    (rec,) = PROOF["controls"]
    by_id = {d["product_id"]: d for d in CORPUS}
    (control,) = _cups().controls
    assert all(control.is_intended(by_id[h["product_id"]]) for h in rec["policy"][:3])


def test_a_control_whose_policy_top_3_leaves_its_sense_is_refused() -> None:
    assert PROOF.get("controls")
    bad = copy.deepcopy(PROOF)
    cups = next(r for r in bad["rows"] if r["query"] == "cups")
    bad["controls"][0]["policy"][1] = cups["policy"][0]
    assert rc.verdicts(bad, CORPUS) == ["'d cup bra' (control): the policy top 3 is not all a bra"]


def test_the_cups_claim_is_that_a_bra_leads_the_baseline_and_a_cup_may_too() -> None:
    assert getattr(_cups(), "baseline_holds", None) is not None
    by_id = {d["product_id"]: d for d in CORPUS}
    cups = next(r for r in PROOF["rows"] if r["query"] == "cups")
    top3 = [by_id[h["product_id"]] for h in cups["baseline"][:3]]
    assert any(_cups().baseline_holds.is_intended(d) for d in top3)


def test_a_cups_baseline_top_3_without_a_bra_is_refused() -> None:
    bad = copy.deepcopy(PROOF)
    cups = next(r for r in bad["rows"] if r["query"] == "cups")
    cups["baseline"][:3] = cups["policy"][:3]
    assert rc.verdicts(bad, CORPUS) == ["'cups': the baseline top 3 holds no a bra"]
