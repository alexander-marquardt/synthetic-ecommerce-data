"""Mens and Womens each have a Formal shoes node over their brogues and loafers (gen#606).

A shopper who asks for "dress shoes" or "smart shoes" means the brogues and the loafers, and no
node grouped them: the query matched the Dresses node and the "Dress Circle" wellies instead. The
tree now has ``Mens > Shoes > Formal shoes`` and ``Womens > Shoes > Formal shoes`` with ``Brogues``
and ``Loafers`` under each. Product ids, titles and drawings do not move.

The women's node holds the court shoes too, and they stay under ``Heels``: a retailer keeps Heels
as its own group and treats dress as an occasion across types. A court shoe is one document filed
at both paths through ``category_paths`` (gen#602, the mugs). Its second path ends in ``Court
shoes`` because a leaf is never a parent; a filter on ``Womens/Shoes/Formal shoes`` still finds it.
Block heels and kitten heels stay under Heels only.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core import standard
from synthetic_ecommerce_data.domains.retail import (
    export,
    multi_path,
    real_classes,
    scale,
    tree_guard,
)
from synthetic_ecommerce_data.domains.retail import footwear_rows as fw
from synthetic_ecommerce_data.prism import index

ROOTS = ("Mens", "Womens")
NODES = {root: (root, "Shoes", "Formal shoes") for root in ROOTS}
FORMAL_TYPES = ("Brogues", "Loafers")
COURT = "Court Shoes"
HEELS = ("Womens", "Shoes", "Heels")
COURT_HEELS = (*HEELS, "Court shoes")
COURT_FORMAL = (*NODES["Womens"], "Court shoes")


@pytest.fixture(scope="module")
def records() -> list[dict]:
    """The SHIPPED documents, as the 283 tree test reads them: decoys and derived styles too."""
    return scale.documents(ceiling_build())


def _of(records: list[dict], root: str, ptype: str) -> list[dict]:
    return [r for r in records if r["category_path"][0] == root and r["product_type"] == ptype]


def _filed(doc: dict) -> list[tuple[str, ...]]:
    """Every path ``doc`` is filed at, the primary first."""
    return [tuple(p) for p in doc.get("category_paths", [doc["category_path"]])]


@pytest.mark.parametrize("root", ROOTS)
@pytest.mark.parametrize("ptype", FORMAL_TYPES)
def test_every_brogue_and_loafer_sits_under_formal_shoes(
    records: list[dict], root: str, ptype: str
) -> None:
    docs = _of(records, root, ptype)
    assert docs, ptype
    outside = [d["product_id"] for d in docs if tuple(d["category_path"]) != (*NODES[root], ptype)]
    assert outside == []
    assert {d["category_leaf"] for d in docs} == {ptype}


@pytest.mark.parametrize("root", ROOTS)
def test_a_formal_node_is_the_primary_path_of_its_brogues_and_loafers_alone(
    records: list[dict], root: str
) -> None:
    held = collections.Counter(
        r["product_type"] for r in records if tuple(r["category_path"][:3]) == NODES[root]
    )
    assert set(held) == set(FORMAL_TYPES)
    paths = {tuple(r["category_path"]) for r in records}
    assert NODES[root] not in paths, "Formal shoes is a parent"


def test_every_court_shoe_keeps_the_heels_path_and_is_filed_under_formal_shoes(
    records: list[dict],
) -> None:
    courts = _of(records, "Womens", COURT)
    assert courts
    bad = {d["product_id"]: _filed(d) for d in courts if _filed(d) != [COURT_HEELS, COURT_FORMAL]}
    assert bad == {}
    assert all(tuple(d["category_path"]) == COURT_HEELS for d in courts)
    assert all(d["category_leaf"] == "Court shoes" for d in courts)


def test_no_court_shoe_is_listed_twice(records: list[dict]) -> None:
    ids = [d["product_id"] for d in _of(records, "Womens", COURT)]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("ptype", ["Block Heels", "Kitten Heels"])
def test_the_other_heels_stay_under_heels_alone(records: list[dict], ptype: str) -> None:
    docs = _of(records, "Womens", ptype)
    assert docs, ptype
    assert {tuple(d["category_path"]) for d in docs} == {(*HEELS, ptype.capitalize())}
    assert all("category_paths" not in d for d in docs)


@pytest.mark.parametrize("root", ROOTS)
def test_the_node_exists_in_the_category_tree(records: list[dict], root: str) -> None:
    paths = {path for r in records for path in _filed(r)}
    node = NODES[root]
    assert {node, (*node, "Brogues"), (*node, "Loafers")} <= tree_guard.nodes(paths)
    assert (root, "Shoes", "Brogues") not in paths
    assert (root, "Shoes", "Loafers") not in paths


def test_the_mens_node_has_no_court_shoes(records: list[dict]) -> None:
    paths = {path for r in records for path in _filed(r)}
    assert COURT_FORMAL in paths
    assert (*NODES["Mens"], "Court shoes") not in paths


def test_the_tree_rules_hold_on_every_filed_path(records: list[dict]) -> None:
    paths = {path for r in records for path in _filed(r)}
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    shoes = [r for r in records if r["category_path"][1:2] == ["Shoes"]]
    assert real_classes.check_category_paths(shoes) == []


def test_a_court_shoe_passes_the_standard(records: list[dict]) -> None:
    courts = _of(records, "Womens", COURT)
    assert [p for d in courts for p in standard.check_document(d)] == []


def _joined(docs: list[dict]) -> dict[str, set[str]]:
    """Each ``category_path_joined`` value, and the products a filter on it finds."""
    found: dict[str, set[str]] = collections.defaultdict(set)
    for doc in docs:
        for row in standard.flat_documents(doc, export.NUMERIC_FACTS):
            for value in index.project(row)[index.CATEGORY_PATH_FIELD]:
                found[value].add(doc["product_id"])
    return found


def test_a_filter_on_either_node_finds_the_court_shoes(records: list[dict]) -> None:
    shoes = [r for r in records if r["category_path"][:2] == ["Womens", "Shoes"]]
    found = _joined(shoes)
    courts = {d["product_id"] for d in _of(records, "Womens", COURT)}
    formal = index.PATH_SEPARATOR.join(NODES["Womens"])
    heels = index.PATH_SEPARATOR.join(HEELS)
    held = {
        d["product_id"]
        for d in shoes
        if d["product_type"] in (*FORMAL_TYPES, COURT)
    }
    assert found[formal] == held
    assert courts <= found[heels]
    assert not found[heels] & (held - courts), "a brogue or a loafer is under Heels"


@pytest.mark.parametrize(
    ("product_id", "path", "other"),
    [
        ("FTW-X", multi_path.COURT_HEELS, [multi_path.COURT_FORMAL]),
        ("FTW-X", multi_path.COURT_FORMAL, [multi_path.COURT_HEELS]),
        ("FTW-X", (*HEELS, "Block Heels"), []),
    ],
    ids=["heels-side", "formal-side", "block-heel"],
)
def test_other_paths_names_the_court_shoe_pair(
    product_id: str, path: tuple[str, ...], other: list[tuple[str, ...]]
) -> None:
    assert multi_path.other_paths({"product_id": product_id, "category_path": path}) == other


def test_a_court_shoe_is_searchable_by_both_of_its_paths(records: list[dict]) -> None:
    """Best takes the node as a filter and still needs the query's words in the text, so a court
    shoe whose ``text`` said only ``Heels`` was filtered in and never matched "formal shoes"."""
    courts = _of(records, "Womens", COURT)
    rows = [row for d in courts for row in standard.flat_documents(d, export.NUMERIC_FACTS)]
    assert rows
    assert [row["sku"] for row in rows if "Formal shoes" not in row["text"]] == []
    assert [row["sku"] for row in rows if "Heels" not in row["text"]] == []


def test_the_authored_styles_are_filed_by_the_same_rule() -> None:
    """The authored styles, before any derived style is added, agree with the built catalog."""
    for root in ROOTS:
        docs = [d for d in fw.docs() if d["category_path"][0] == root]
        formal = [d for d in docs if d["product_type"] in FORMAL_TYPES]
        assert formal, root
        # the authored rows spell nodes in Title Case: the build's casing step sentence-cases them
        want = (root, "Shoes", "Formal Shoes")
        assert all(tuple(d["category_path"][:3]) == want for d in formal), root
