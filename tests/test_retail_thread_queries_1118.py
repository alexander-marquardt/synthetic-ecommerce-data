"""The 'thread' search-demo queries, without and with a policy (#1118, the last cut).

Sewing thread shares its word with the industrial catalogue's thread sizes: a bare ``thread``
finds threaded rods first, ``sewing thread white`` finds sewing notions and machines beside the
thread, and ``m6 thread`` also finds the Mervane M6 phone. Each query's policy must do what its
Expected cell says. The exact counts and places are in
``docs/retail-prototype/sewing-knitting-1118.md``, measured once on the ceiling build and once on
the served index, because a product added elsewhere moves them.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from synthetic_ecommerce_data import clash_queries as cq
from synthetic_ecommerce_data.domains.retail import baseline_rank as br

DOC = Path(__file__).parents[1] / "docs" / "retail-prototype" / "sewing-knitting-1118.md"
BY_QUERY = {clash.query: clash for clash in cq.THREADS}


@pytest.fixture(scope="module")
def index() -> br.Index:
    return br.Index(cq.catalog())


def _top(index: br.Index, query: str, *, policy: bool) -> list[dict]:
    return cq.hits(index, BY_QUERY[query], policy=policy)[: cq.SIZE]


def test_the_issue_names_three_thread_queries_each_with_one_policy():
    assert sorted(BY_QUERY) == ["m6 thread", "sewing thread white", "thread"]
    assert all(bool(c.filter) != bool(c.boost) for c in cq.THREADS)


@pytest.mark.parametrize("query", sorted(BY_QUERY))
def test_every_family_is_in_the_build_without_a_policy(index, query):
    clash = BY_QUERY[query]
    found = cq.hits(index, clash, policy=False)
    missing = [name for name, (n, _) in cq.families(found, clash).items() if not n]
    assert not missing, (query, missing)


def test_a_bare_thread_finds_industrial_thread_first_until_the_boost(index):
    """The clash the issue names: 10,000+ industrial thread hits bury the spool."""
    clash = BY_QUERY["thread"]
    off = cq.hits(index, clash, policy=False)
    on = cq.hits(index, clash, policy=True)
    assert not any(cq.meets(r, cq.SEWING) for r in off[: cq.SIZE])
    sewing = sum(cq.meets(r, cq.SEWING) for r in off)
    assert all(cq.meets(r, cq.SEWING) for r in on[:sewing])
    assert {n: c for n, (c, _) in cq.families(on, clash).items()} == {
        n: c for n, (c, _) in cq.families(off, clash).items()
    }


def test_sewing_thread_white_puts_thread_first_and_its_filter_keeps_white_thread_only(index):
    off = _top(index, "sewing thread white", policy=False)
    on = cq.hits(index, BY_QUERY["sewing thread white"], policy=True)
    assert cq.meets(off[0], cq.SEWING)
    assert any(not cq.meets(r, cq.SEWING) for r in off), "the notions and machines beside it"
    assert on and all(cq.meets(r, {**cq.SEWING, "color": ("White",)}) for r in on)


def test_a_color_is_met_by_any_sku_of_the_record():
    record = {"product_type": "Sewing Thread", "attributes": [],
              "skus": [{"color": "Red"}, {"color": "White"}]}  # fmt: skip
    assert cq.meets(record, {"color": ("White",)})
    assert not cq.meets(record, {"color": ("Black",)})
    assert not cq.meets({**record, "skus": []}, {"color": ("White",)})


def test_m6_thread_meets_the_m6_phone_until_the_filter(index):
    off = _top(index, "m6 thread", policy=False)
    on = cq.hits(index, BY_QUERY["m6 thread"], policy=True)
    assert any(r["product_type"] in {"Smartphone", "Phone Case"} for r in off)
    assert on and all(r.get("industrial") for r in on)
    assert not any(cq.meets(r, cq.SEWING) for r in on)


def test_the_docs_table_states_the_queries_and_policies_of_the_code():
    rows = [
        [cell.strip() for cell in line.strip("|\n").split("|")]
        for line in DOC.read_text("utf-8").splitlines()
        if line.startswith("| `") and len(line.split("|")) == 9
    ]
    assert [(r[0].strip("`"), r[1], r[4]) for r in rows] == [
        (c.query, c.expected, c.policy()) for c in cq.THREADS
    ]
