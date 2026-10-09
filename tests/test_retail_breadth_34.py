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


def test_a_unit_free_attribute_key_names_no_unit() -> None:
    """A unit-free value (a material, a variety) has no unit in its key; a size is a SKU field."""
    bad = [
        (r.code, k)
        for r in ROWS
        for k, _, _ in r.attrs
        if any(u in k.split("_") for u in ("mm", "cm", "ml", "kg", "g", "l", "in", "ft"))
    ]
    assert bad == []
