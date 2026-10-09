"""The retail breadth tier (gen#34, first increment): plain products in new leaves.

Each row of ``breadth_rows.BREADTH_34`` is one or two products in a category no other
template uses, so a shopper query for cutlery, a claw hammer or cherries finds a category
at all. These checks hold what makes a row breadth and not depth.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import breadth_rows  # noqa: E402
import kit  # noqa: E402
import scale  # noqa: E402

ROWS = breadth_rows.BREADTH_34


def _leaves() -> dict[tuple[str, ...], list[breadth_rows.Row]]:
    out: dict[tuple[str, ...], list[breadth_rows.Row]] = collections.defaultdict(list)
    for row in ROWS:
        out[row.path].append(row)
    return out


def test_every_leaf_holds_one_or_two_products_and_there_are_at_least_twenty_leaves() -> None:
    leaves = _leaves()
    assert len(leaves) >= 20
    assert {p: len(r) for p, r in leaves.items() if not 1 <= len(r) <= 2} == {}


def test_no_other_template_uses_a_breadth_leaf() -> None:
    mine = {r.code for r in ROWS}
    other = {
        tuple(d["category_path"])
        for d in scale.templates()
        if d["product_id"].removeprefix("BRD-") not in mine
    }
    assert sorted(set(_leaves()) & other) == []


#: Branches this tier adds on purpose, each under a node the catalog already has.
NEW_BRANCHES = frozenset({
    ("Beauty", "Fragrance"),
    ("Beauty", "Make-Up", "Eyes"),
    ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Berries"),
    ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Stone Fruit"),
    ("Garden", "Seeds"),
    ("Home", "DIY & Tools"),
})


def _existing_nodes() -> set[tuple[str, ...]]:
    """Every node (every prefix of a path) used by a template that is not a breadth row."""
    mine = {r.code for r in ROWS}
    nodes: set[tuple[str, ...]] = set()
    for d in scale.templates():
        if d["product_id"].removeprefix("BRD-") in mine:
            continue
        path = tuple(d["category_path"])
        nodes.update(path[:i] for i in range(1, len(path) + 1))
    return nodes


def test_a_new_leaf_sits_inside_the_existing_tree_not_beside_it() -> None:
    """A leaf's parent is an existing node or a listed new branch (whose own parent exists),
    and the leaf is not placed beside a node named for its own product type (a Cherries leaf
    under Fruit & Vegetables, next to Fresh Fruit, belongs inside Fresh Fruit)."""
    nodes = _existing_nodes()
    unknown_parent = sorted(
        r.path for r in ROWS if r.path[:-1] not in nodes | NEW_BRANCHES
    )
    orphan_branch = sorted(b for b in NEW_BRANCHES if b[:-1] not in nodes)
    beside = sorted(
        (r.path, r.product_type)
        for r in ROWS
        if (*r.path[:-1], r.product_type) in nodes
    )
    assert unknown_parent == []
    assert orphan_branch == []
    assert beside == []


def test_no_node_sits_directly_under_a_parent_of_the_same_name() -> None:
    pairs = {p: zip(p, p[1:], strict=False) for p in _leaves()}
    same = [p for p, z in pairs.items() if any(a.lower() == b.lower() for a, b in z)]
    assert same == []


def test_titles_and_codes_are_unique_and_every_row_builds_a_valid_document() -> None:
    titles = [r.title for r in ROWS]
    codes = [r.code for r in ROWS]
    assert len(set(titles)) == len(titles)
    assert len(set(codes)) == len(codes)
    for row in ROWS:
        doc = row.doc()
        assert doc["skus"], row.code
        assert doc["attributes"], row.code
        assert doc["drawing"]["shape"] in kit.SHAPES, row.code
        assert doc["drawing"].get("label") is None, row.code


def test_a_unit_free_key_names_no_unit_and_a_unit_key_ends_in_its_unit() -> None:
    """A material or a variety has no unit in its key; a measured figure ends in it
    (``head_weight_oz``, unit code ONZ); a size is a SKU field."""
    units = {"ONZ": "oz"}
    tokens = ("mm", "cm", "ml", "kg", "g", "l", "in", "ft", "oz")
    bad = []
    for r in ROWS:
        for a in r.attrs:
            key, code = a[0], (a[3] if len(a) > 3 else None)
            if code is None and any(u in key.split("_") for u in tokens):
                bad.append((r.code, key))
            if code is not None and not key.endswith("_" + units[code]):
                bad.append((r.code, key))
    assert bad == []
