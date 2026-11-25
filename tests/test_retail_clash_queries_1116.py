"""The ten search-demo clash queries, without and with a policy (#1116, the last slice).

A query's families must be in the build without a policy, and its policy must do what the issue's
Expected column says: a boost puts its family first and drops no other family, a filter leaves only
the family it names. The exact counts and places are in ``docs/retail-prototype/
clash-queries-1116.md``, measured once, because a product added elsewhere moves them.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from synthetic_ecommerce_data import clash_queries as cq
from synthetic_ecommerce_data.domains.retail import baseline_rank as br

DOC = Path(__file__).parents[1] / "docs" / "retail-prototype" / "clash-queries-1116.md"
BY_QUERY = {clash.query: clash for clash in cq.CLASHES}
QUERIES = sorted(BY_QUERY)
BOOSTED = [c.query for c in cq.CLASHES if c.boost]
FILTERED = [c.query for c in cq.CLASHES if c.filter]


@pytest.fixture(scope="module")
def index() -> br.Index:
    return br.Index(cq.catalog())


def test_the_ten_queries_of_the_issue_each_have_one_policy():
    assert sorted(
        ["washer", "washer 8kg", "m8 washer", "dryer", "heat pump dryer", "range",
         "range cooker 90cm", "iron", "steam iron", "freezer"]
    ) == QUERIES  # fmt: skip
    assert all(bool(c.filter) != bool(c.boost) for c in cq.CLASHES)
    assert sorted(BOOSTED + FILTERED) == QUERIES


@pytest.mark.parametrize("query", QUERIES)
def test_every_family_is_in_the_build_without_a_policy(index, query):
    clash = BY_QUERY[query]
    found = cq.hits(index, clash, policy=False)
    missing = [name for name, (n, _) in cq.families(found, clash).items() if not n]
    assert not missing, (query, missing)


@pytest.mark.parametrize("query", BOOSTED)
def test_a_boost_puts_its_family_first_and_drops_no_other(index, query):
    clash = BY_QUERY[query]
    off = cq.hits(index, clash, policy=False)
    on = cq.hits(index, clash, policy=True)
    first = next(iter(clash.families))
    wanted = sum(cq.meets(r, clash.boost) for r in off)
    assert wanted and len(on) == len(off)
    assert all(cq.meets(r, clash.boost) for r in on[: min(wanted, cq.SIZE)]), query
    assert cq.families(on, clash)[first][1] == 1
    assert {n: c for n, (c, _) in cq.families(on, clash).items()} == {
        n: c for n, (c, _) in cq.families(off, clash).items()
    }


@pytest.mark.parametrize("query", FILTERED)
def test_a_filter_leaves_only_its_family(index, query):
    clash = BY_QUERY[query]
    on = cq.hits(index, clash, policy=True)
    (family,) = clash.families.values()
    assert on and all(cq.meets(r, clash.filter) for r in on), query
    assert all(cq.meets(r, family) for r in on), query


@pytest.mark.parametrize("query", ["washer 8kg", "heat pump dryer", "range cooker 90cm"])
def test_an_unambiguous_appliance_query_finds_its_family_without_a_policy(index, query):
    """The issue's table asks for laundry only or cookers only, before any policy."""
    clash = BY_QUERY[query]
    (family,) = clash.families.values()
    top = cq.hits(index, clash, policy=False)[: cq.SIZE]
    assert all(cq.meets(r, family) for r in top), [r["title"] for r in top]


def test_m8_washer_finds_fasteners_only_without_a_policy(index):
    top = cq.hits(index, BY_QUERY["m8 washer"], policy=False)[: cq.SIZE]
    assert {r["product_type"] for r in top} <= {"washer_flat", "serrated_flange_nuts"}


def test_the_washer_top_ten_turns_from_flat_washers_to_machines(index):
    """The case the ruling asks to record: the bare word is a fastener until a policy says
    otherwise."""
    clash = BY_QUERY["washer"]
    off = cq.hits(index, clash, policy=False)[: cq.SIZE]
    on = cq.hits(index, clash, policy=True)[: cq.SIZE]
    assert {r["product_type"] for r in off} == {"washer_flat"}
    assert all(cq.meets(r, cq.WASHERS) for r in on)


def test_the_docs_table_states_the_queries_policies_of_the_code():
    rows = [
        [cell.strip() for cell in line.strip("|\n").split("|")]
        for line in DOC.read_text("utf-8").splitlines()
        if line.startswith("| `")
    ]
    got = [(r[0].strip("`"), r[1], r[4]) for r in rows]
    assert got == [(c.query, c.expected, c.policy()) for c in cq.CLASHES]
    assert len(rows[0]) == 7
