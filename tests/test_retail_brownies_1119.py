"""Books, slice 3 (gen#1119): the brownie mix and tin set, and the demo query list.

'How to Make Brownies' had nothing to collide with: the catalogue sold no brownie mix and no
brownie tin. Slice 3 adds the two types (``type_specs/brownie_mix.py``, ``brownie_tin.py``, drawn
by :mod:`kit_baking`). These checks hold its Done-when: at least 50 brownie SKUs at the ceiling
build, each type in its leaf with the SKU axis a shopper picks from, a drawing per product, the
book's two collisions in the build, and the issue's eight queries in ``books-1119.md``, each with
the family it collides with and its expected results without and with a policy.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import books_rows, kit, type_registry

DOC = Path(__file__).resolve().parents[1] / "docs" / "retail-prototype" / "books-1119.md"
#: Each type: its spec key, its leaf, its department and its SKU axis.
TYPES = {
    "Brownie Mix": (
        "brownie_mix",
        ("Food & Drink", "Food Cupboard", "Baking", "Baking Mixes"),
        "Food & Drink",
        "net_weight_g",
    ),
    "Brownie Tin": (
        "brownie_tin",
        ("Home", "Kitchen & Dining", "Bakeware", "Brownie Tins"),
        "Home",
        "length_cm",
    ),
}
#: The gate's floor: the issue's "about 60 SKUs", less a margin.
FLOOR = 50
BOOK = "How to Make Brownies"
#: The issue's demo queries, in its order.
QUERIES = (
    "the book of chocolate",
    "chocolate",
    "how to make brownies",
    "brownie tin",
    "learn to sew",
    "barry plotter book 3",
    "barry plotter box set",
    "barry plotter",
)


def _spec(ptype: str) -> type_registry.TypeSpec:
    specs = type_registry.specs()
    key = TYPES[ptype][0]
    # An assertion, not a KeyError, so a build without the type fails as a red test.
    assert key in specs, f"no {key!r} type spec is registered"
    return specs[key]


def _records(ptype: str) -> list[dict]:
    return [r for r in ceiling_build().records if r["product_type"] == ptype]


def test_the_ceiling_build_holds_at_least_50_brownie_skus_across_both_types() -> None:
    counts = {t: sum(r["sku_count"] for r in _records(t)) for t in TYPES}
    assert all(counts.values()), counts
    assert sum(counts.values()) >= FLOOR, counts


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_is_a_spec_in_its_leaf_sold_by_its_axis(ptype) -> None:
    spec = _spec(ptype)
    _, path, department, axis = TYPES[ptype]
    assert (spec.product_type, spec.department) == (ptype, department)
    for row in spec.rows:
        assert row.path == path, row.code
        assert row.size_key == axis, row.code
        values = [float(s) for s, _ in row.sizes]
        prices = [p for _, p in row.sizes]
        assert values == sorted(set(values)) and len(values) >= 2, row.code
        assert prices == sorted(set(prices)), (row.code, prices)


@pytest.mark.parametrize("ptype", TYPES)
def test_every_product_of_a_type_has_its_own_title_and_drawing(ptype) -> None:
    rows = _spec(ptype).rows
    assert len({r.title for r in rows}) == len(rows)
    svgs = set()
    for row in rows:
        c = row.colors[0]
        svgs.add(kit.render(row.shape, kit.Fill(c[1], c[2], c[3]), params=dict(row.params)))
    assert len(svgs) == len(rows)


def test_how_to_make_brownies_collides_with_a_mix_and_a_tin_in_the_build() -> None:
    entries = {t: w for title, t, w in books_rows.COLLISIONS if title == BOOK}
    assert set(entries) == set(TYPES)
    assert all(title != BOOK for title, _, _ in books_rows.PENDING)
    for ptype, word in entries.items():
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        assert pattern.search(BOOK), word
        assert any(pattern.search(r["title"]) for r in _records(ptype)), (ptype, word)


def _table() -> dict[str, list[str]]:
    """The demo query table's rows: the query -> its other cells."""
    out = {}
    for line in DOC.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("| `") and len(cells) == 4:
            out[re.findall(r"`([^`]+)`", cells[0])[0]] = cells
    return out


@pytest.mark.parametrize("query", QUERIES)
def test_the_demo_query_list_gives_the_family_and_both_expected_results(query) -> None:
    table = _table()
    assert query in table, sorted(table)
    assert all(table[query]), table[query]


def test_the_demo_query_list_holds_every_query_once_in_the_issues_order() -> None:
    assert tuple(_table()) == QUERIES
