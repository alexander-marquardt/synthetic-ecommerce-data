"""Mens > Shoes > Formal shoes holds the men's brogues and loafers (gen#606).

A shopper who asks for "dress shoes" or "smart shoes" means the brogues and the loafers, and no
node grouped them: the query matched the Dresses node and the "Dress Circle" wellies instead. The
tree now has ``Mens > Shoes > Formal shoes`` with ``Brogues`` and ``Loafers`` under it. Product
ids, titles and drawings do not move, and the Womens tree is left as it was until the maintainer
names which women's shoe types it groups.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import footwear_rows as fw  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402

CEILING = 10_000_000  # more SKUs than the templates reach, so ``scale.build`` runs to its ceiling

NODE = ("Mens", "Shoes", "Formal shoes")
FORMAL_TYPES = ("Brogues", "Loafers")


@pytest.fixture(scope="module")
def records() -> list[dict]:
    """The SHIPPED documents, as the 283 tree test reads them: decoys and derived styles too."""
    return scale.documents(scale.build(CEILING))


def _of(records: list[dict], root: str, ptype: str) -> list[dict]:
    return [r for r in records if r["category_path"][0] == root and r["product_type"] == ptype]


@pytest.mark.parametrize("ptype", FORMAL_TYPES)
def test_every_mens_brogue_and_loafer_sits_under_formal_shoes(
    records: list[dict], ptype: str
) -> None:
    docs = _of(records, "Mens", ptype)
    assert docs, ptype
    outside = [d["product_id"] for d in docs if tuple(d["category_path"]) != (*NODE, ptype)]
    assert outside == []
    assert {d["category_leaf"] for d in docs} == {ptype}


def test_formal_shoes_holds_only_the_mens_brogues_and_loafers(records: list[dict]) -> None:
    held = collections.Counter(
        r["product_type"] for r in records if tuple(r["category_path"][:3]) == NODE
    )
    assert set(held) == set(FORMAL_TYPES)
    assert all(tuple(r["category_path"]) != NODE for r in records), "Formal shoes is a parent"


def test_the_node_exists_in_the_category_tree(records: list[dict]) -> None:
    paths = {tuple(r["category_path"]) for r in records}
    assert {NODE, (*NODE, "Brogues"), (*NODE, "Loafers")} <= tree_guard.nodes(paths)
    assert ("Mens", "Shoes", "Brogues") not in paths
    assert ("Mens", "Shoes", "Loafers") not in paths


@pytest.mark.parametrize("ptype", FORMAL_TYPES)
def test_the_womens_tree_is_unchanged(records: list[dict], ptype: str) -> None:
    docs = _of(records, "Womens", ptype)
    assert docs, ptype
    assert {tuple(d["category_path"]) for d in docs} == {("Womens", "Shoes", ptype)}


def test_the_tree_rules_of_283_hold_with_the_new_node(records: list[dict]) -> None:
    paths = {tuple(r["category_path"]) for r in records}
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []


def test_the_authored_styles_are_filed_by_the_same_rule() -> None:
    """The authored styles, before any derived style is added, agree with the built catalogue."""
    docs = [d for d in fw.docs() if d["category_path"][0] == "Mens"]
    mens = [d for d in docs if d["product_type"] in FORMAL_TYPES]
    assert mens
    # the authored rows spell nodes in Title Case: the build's casing step sentence-cases them
    assert all(tuple(d["category_path"][:3]) == ("Mens", "Shoes", "Formal Shoes") for d in mens)
