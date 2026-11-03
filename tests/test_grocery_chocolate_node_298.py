"""Chocolate & Sweets has a Chocolate node, and every chocolate sits under it (gen#298).

The grocery tree had no chocolate node: ``Chocolate & Sweets > {Chocolate Bars, Chocolate Boxes,
Sweets}``. So a shopper's bare "chocolate" named no category, and a category policy such as
"chocolate without peanuts" could not route to one. The maintainer's shape (2026-10-14, from a UK
grocer's tree) is::

    Chocolate & Sweets > Chocolate > Chocolate Bars > Dark / Milk / White Chocolate Bars
                                   > Chocolate Multipacks
                                   > Sharing Bags
                                   > Chocolate Boxes
                       > Sweets

The first block holds the grocery build to it. Each bar style sits in the child for its chocolate
type, the #294 peanut decoys too, and nothing sits on Chocolate or Chocolate Bars itself. The second
block runs over the shipped tree (the ceiling build's documents). Every chocolate is under the node
and nothing else is. Hot chocolate stays in Drinks, and the query "chocolate" names the node.
"""

from __future__ import annotations

from functools import cache

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import grocery, grocery_rows, scale, tree_guard
from synthetic_ecommerce_data.domains.retail.grocery_families import _bars
from synthetic_ecommerce_data.domains.retail.grocery_model import F, Family

CHOCOLATE = ("Food & Drink", "Chocolate & Sweets", "Chocolate")
BARS = (*CHOCOLATE, "Chocolate Bars")
#: Each bar flavor the bar families draw -> the Chocolate Bars child for its chocolate.
TYPE = {
    # CHB
    "Milk": "Milk", "Hazelnut Milk": "Milk", "Peanut Caramel": "Milk",
    "Salted Caramel Milk": "Milk",
    "Dark 70%": "Dark", "Mint Dark": "Dark", "Orange Dark": "Dark", "Coconut Dark": "Dark",
    "Almond Dark": "Dark", "Raspberry Dark": "Dark", "White": "White", "Lemon White": "White",
    # CHO, the chocolate oranges
    "Milk Chocolate Orange": "Milk", "Dark Chocolate Orange": "Dark",
    # PNT, PNH and PNF, the "chocolate without peanuts" class (gen#294)
    "Chocolate Peanut Butter Cups": "Milk", "Milk Chocolate with Crunchy Peanuts": "Milk",
    "Chocolate Coated Peanuts": "Milk", "Peanut Caramel Chocolate Bar": "Milk",
    "Dark Chocolate Peanut Clusters": "Dark", "Chocolate Peanut Brittle": "Milk",
    "Milk Chocolate Praline Bar": "Milk", "Triple Chocolate Biscuit Bar": "Milk",
    "Dark Chocolate Crunch Bar": "Dark", "Peanut-Free Milk Chocolate Bar": "Milk",
    "Peanut-Free Dark Chocolate Bar": "Dark", "No Peanuts Hazelnut Milk Chocolate Bar": "Milk",
    "No Peanuts Orange Dark Chocolate Bar": "Dark",
    "Peanut-Free Salted Caramel Chocolate Bar": "Milk",
}  # fmt: skip
#: Each family under Chocolate that is not a bar family -> its leaf.
LEAF = {"CHX": "Chocolate Boxes", "CMP": "Chocolate Multipacks", "CSB": "Sharing Bags"}
CHOCOLATE_TYPES = {"Chocolate Bar", "Chocolate Box"}


@cache
def _recs() -> tuple[dict, ...]:
    return tuple(grocery.build(grocery.TARGET))


def _flavors(rec: dict) -> list[str]:
    return [a["value"] for a in rec["attributes"] if a["key"] == "flavor"]


def _family(rec: dict) -> str:
    return rec["product_id"].split("-")[1]


def test_chocolate_is_a_parent_of_bars_multipacks_sharing_bags_and_boxes() -> None:
    paths = (tuple(r["category_path"]) for r in _recs())
    under = [p for p in paths if p[:3] == CHOCOLATE]
    assert {p[3] for p in under} == {"Chocolate Bars", "Chocolate Multipacks", "Sharing Bags",
                                     "Chocolate Boxes"}  # fmt: skip
    assert {p[4] for p in under if p[:4] == BARS} == {
        "Dark Chocolate Bars",
        "Milk Chocolate Bars",
        "White Chocolate Bars",
    }
    assert [p for p in under if p in (CHOCOLATE, BARS)] == []


@pytest.mark.parametrize("code", ["CHB", "CHO", "PNT", "PNH", "PNF"])
def test_every_bar_sits_in_the_child_for_its_chocolate_type(code: str) -> None:
    bars = [r for r in _recs() if _family(r) == code]
    assert bars
    wrong = {r["title"]: (r["category_path"], _flavors(r)) for r in bars
             if any(r["category_path"] != [*BARS, f"{TYPE[f]} Chocolate Bars"]
                    for f in _flavors(r))}  # fmt: skip
    assert wrong == {}


def test_the_peanut_decoys_sit_in_a_bar_child_by_their_chocolate() -> None:
    """The planted decoys (gen#294): "chocolate without peanuts" routes to Chocolate over them."""
    planted = {f for code, names, *_ in grocery_rows.DECOY_ANCHORS for f in names}
    decoys = [r for r in _recs() if set(_flavors(r)) & planted]
    assert {_family(r) for r in decoys} == {"PNT", "PNH", "PNF"}
    leaves = {r["category_path"][-1] for r in decoys}
    assert leaves == {"Milk Chocolate Bars", "Dark Chocolate Bars"}


@pytest.mark.parametrize("code", sorted(LEAF))
def test_each_box_multipack_and_sharing_bag_family_is_a_real_leaf(code: str) -> None:
    styles = [r for r in _recs() if _family(r) == code]
    assert len(styles) >= 8, len(styles)
    assert {tuple(r["category_path"]) for r in styles} == {(*CHOCOLATE, LEAF[code])}


def test_a_bar_flavor_of_no_chocolate_type_stops_the_build() -> None:
    """A flavor that names no white or dark and holds no milk has no child: refused, not filed."""
    carob = (F("Plain Carob", "#3b2416"),)
    fam = Family("XXX", BARS, "{line} {flavor}", "Chocolate Bar", "bar", "Chocolate", "ambient",
                 "D", 1.0, ("100g",), carob, ("Pantry Mill",), 0.001)  # fmt: skip
    with pytest.raises(ValueError, match="Plain Carob"):
        _bars(fam)


@pytest.fixture(scope="module")
def docs() -> list[dict]:
    """The shipped documents: the seasonal, decoy and scaled rows as well as the grocery build."""
    return scale.documents(ceiling_build())


SHIPPED = ["Food & drink", "Chocolate & sweets", "Chocolate"]


def test_every_shipped_chocolate_sits_under_chocolate_and_nothing_else_does(docs) -> None:
    outside = {d["title"]: d["category_path"] for d in docs
               if d["product_type"] in CHOCOLATE_TYPES
               and d["category_path"][:3] != SHIPPED}  # fmt: skip
    inside = {d["title"]: d["product_type"] for d in docs
              if d["category_path"][:3] == SHIPPED
              and d["product_type"] not in CHOCOLATE_TYPES}  # fmt: skip
    assert (outside, inside) == ({}, {})


def test_the_bar_decoys_sit_in_the_child_for_their_chocolate(docs) -> None:
    """The class 9 plural decoys (gen#445) of the kinds dark_chocolate and white_chocolate."""
    named = ("Chocolate & Candied Oranges", "White Chocolate Raspberries Bar")
    assert {d["title"]: d["category_path"][3:] for d in docs if d["title"] in named} == {
        "Chocolate & Candied Oranges": ["Chocolate bars", "Dark chocolate bars"],
        "White Chocolate Raspberries Bar": ["Chocolate bars", "White chocolate bars"],
    }


def test_nothing_sits_on_chocolate_or_chocolate_bars_itself(docs) -> None:
    parents = (SHIPPED, [*SHIPPED, "Chocolate bars"])
    assert [d["title"] for d in docs if d["category_path"] in parents] == []


def test_sweets_and_hot_chocolate_stay_where_they_were(docs) -> None:
    sweets = {d["category_path"][2] for d in docs if d["product_type"] == "Sweets"
              and d["category_path"][:2] == SHIPPED[:2]}  # fmt: skip
    hot = {tuple(d["category_path"]) for d in docs if d["product_type"] == "Hot Chocolate"}
    assert (sweets, hot) == ({"Sweets"}, {("Food & drink", "Drinks", "Hot chocolate")})


def test_chocolate_names_the_chocolate_node_and_hot_chocolate_its_own(docs) -> None:
    paths = [tuple(d["category_path"]) for d in docs]
    assert tree_guard.named_nodes(paths, "chocolate") == {tuple(SHIPPED)}
    assert tree_guard.named_nodes(paths, "hot chocolate") == {
        ("Food & drink", "Drinks", "Hot chocolate")
    }
