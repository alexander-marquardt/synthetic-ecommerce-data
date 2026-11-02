"""Juice has a child per flavour, and no node label needs its breadcrumb to be read (gen#299).

Every juice sat in one leaf, ``Food & Drink > Drinks > Juice``, so no category named "orange
juice" and a category policy could not route it. A grocer's ``Juice > Orange`` is the wrong fix
here: the category vocabulary reads a label on its own, so a bare ``Orange`` would capture the
shopper's "oranges" (the fruit) and "orange" (the color). The children name the product
(``Orange Juice``), and rule (d) of ``tree_guard.py`` keeps the class out of the whole tree.

The first block holds the grocery build to the issue: each JUI and GJU flavour in its child,
nothing left on Juice itself, the orange decoys and the fresh oranges where they were. The second
runs over the shipped tree (the ceiling build's documents): the two queries name their nodes, the
guard passes, and the planted bare ``Orange`` leaf fails it.
"""

from __future__ import annotations

from functools import cache

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import grocery, scale, tree_guard

JUICE = ("Food & Drink", "Drinks", "Juice")
#: Each juice flavour the JUI and GJU families draw -> the Juice child it sits in.
CHILD = {
    "Smooth Orange": "Orange Juice",
    "Orange with Bits": "Orange Juice",
    "Apple": "Apple Juice",
    "Pineapple": "Pineapple Juice",
    "Coconut Water": "Coconut Water",
    "Red Grape Juice": "Grape Juice",
    "White Grape Juice": "Grape Juice",
}
ORANGES = ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Citrus Fruit", "Oranges")


@cache
def _recs() -> tuple[dict, ...]:
    return tuple(grocery.build(grocery.TARGET))


def _flavor(rec: dict) -> str:
    return next(a["value"] for a in rec["attributes"] if a["key"] == "flavor")


def test_juice_is_a_parent_with_one_child_per_flavour() -> None:
    under = [r for r in _recs() if tuple(r["category_path"][:3]) == JUICE]
    assert {r["category_path"][3] for r in under if len(r["category_path"]) > 3} == set(
        CHILD.values()
    )
    assert [r["title"] for r in under if len(r["category_path"]) == 3] == []


@pytest.mark.parametrize("code", ["JUI", "GJU"])
def test_every_juice_sits_in_the_child_for_its_flavour(code: str) -> None:
    juices = [r for r in _recs() if r["product_id"].startswith(f"GRC-{code}-")]
    assert juices
    wrong = {r["title"]: r["category_path"] for r in juices
             if r["category_path"] != [*JUICE, CHILD[_flavor(r)]]}  # fmt: skip
    assert wrong == {}


def test_orange_flavoured_products_that_are_not_juice_stay_out_of_juice() -> None:
    orange = [r for r in _recs() if "orange" in r["title"].lower() and r["product_type"] != "Juice"]
    assert {r["category_path"][1] for r in orange} >= {"Drinks", "Chocolate & Sweets"}
    assert [r["title"] for r in orange if tuple(r["category_path"][:3]) == JUICE] == []


def test_fresh_oranges_stay_under_fruit() -> None:
    assert any(tuple(r["category_path"]) == ORANGES for r in _recs())


@pytest.fixture(scope="module")
def docs() -> list[dict]:
    """The shipped documents: their labels are the ones the category vocabulary reads."""
    return scale.documents(ceiling_build())


def _rows(docs: list[dict]) -> list[tuple[str, str, str, tuple[str, ...]]]:
    return [(d["product_id"], d["title"], d["product_type"], tuple(d["category_path"]))
            for d in docs]  # fmt: skip


def _colors(docs: list[dict]) -> set[str]:
    attrs = (a for d in docs for v in (d, *d["variants"]) for a in v["attributes"])
    return {a["value"] for a in attrs if a["key"] == "color"}


def test_nothing_sits_on_juice_itself_in_the_shipped_tree(docs: list[dict]) -> None:
    shipped = ["Food & drink", "Drinks", "Juice"]
    assert [d["title"] for d in docs if d["category_path"] == shipped] == []


def test_orange_juice_names_the_orange_juice_node(docs: list[dict]) -> None:
    paths = [p for *_, p in _rows(docs)]
    assert tree_guard.named_nodes(paths, "orange juice") == {
        ("Food & drink", "Drinks", "Juice", "Orange juice")
    }


def test_oranges_still_names_only_the_fruit_node(docs: list[dict]) -> None:
    paths = [p for *_, p in _rows(docs)]
    assert tree_guard.named_nodes(paths, "oranges") == {
        ("Food & drink", "Fruit & vegetables", "Fresh fruit", "Citrus fruit", "Oranges")
    }


def test_no_label_in_the_shipped_tree_reads_wrongly_without_its_breadcrumb(docs) -> None:
    assert tree_guard.bare_label_findings(_rows(docs), _colors(docs)) == []


def test_a_planted_bare_orange_leaf_under_juice_fails_the_guard(docs: list[dict]) -> None:
    """The mutant the issue asks for: the orange juices moved to a leaf called ``Orange``."""
    planted = [(pid, title, kind, (*path[:3], "Orange") if path[3:] == ("Orange juice",) else path)
               for pid, title, kind, path in _rows(docs)]  # fmt: skip
    found = tree_guard.bare_label_findings(planted, _colors(docs))
    assert [f for f in found if f.startswith("Food & drink > Drinks > Juice > Orange:")], found


def test_each_declared_label_exception_still_fires_and_has_a_reason(docs: list[dict]) -> None:
    undeclared = tree_guard.bare_label_findings(_rows(docs), _colors(docs), exceptions={})
    for path, reason in tree_guard.LABEL_EXCEPTIONS.items():
        assert reason.strip(), path
        assert any(f.startswith(f"{' > '.join(path)}:") for f in undeclared), (path, undeclared)
