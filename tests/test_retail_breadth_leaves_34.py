"""Three plain leaves of the breadth tier (gen#34): picture hooks, plant pots, batteries.

Each word already reaches many leaves, so a plain query for it gains a new category and that
category's facets. A leaf holds one or two products, because breadth is not depth.
"""

from __future__ import annotations

import collections

import pytest

from synthetic_ecommerce_data.domains.retail import kit, scale

LEAVES = {
    ("Home", "DIY & Tools", "Picture Hooks"): "Picture Hook",
    ("Home", "Home Accessories", "Plant Pots"): "Plant Pot",
    ("Electronics", "Accessories", "Batteries"): "Battery",
}
_IDS = [leaf[-1] for leaf in LEAVES]


def _docs(path: tuple[str, ...]) -> list[dict]:
    return [d for d in scale.templates() if tuple(d["category_path"]) == path]


@pytest.mark.parametrize("path", LEAVES, ids=_IDS)
def test_a_leaf_holds_one_or_two_products_of_its_own_type(path: tuple[str, ...]) -> None:
    docs = _docs(path)
    assert 1 <= len(docs) <= 2
    assert {d["product_type"] for d in docs} == {LEAVES[path]}


@pytest.mark.parametrize("path", LEAVES, ids=_IDS)
def test_a_leaf_states_at_least_two_attributes_a_facet_can_show(path: tuple[str, ...]) -> None:
    per_doc = collections.Counter(len(d["attributes"]) for d in _docs(path))
    assert per_doc and min(per_doc) >= 2


@pytest.mark.parametrize(
    "path, word",
    [
        (("Home", "DIY & Tools", "Picture Hooks"), "hooks"),
        (("Home", "Home Accessories", "Plant Pots"), "pot"),
        (("Electronics", "Accessories", "Batteries"), "batteries"),
    ],
    ids=_IDS,
)
def test_each_title_holds_the_plain_word_that_reaches_the_leaf(
    path: tuple[str, ...], word: str
) -> None:
    docs = _docs(path)
    assert docs and all(word in d["title"].lower().replace(",", "").split() for d in docs)


@pytest.mark.parametrize(
    "shape, a, b",
    [
        ("picture_hook", {"pins": "1"}, {"pins": "2"}),
        ("plant_pot", {"finish": "plain"}, {"finish": "glazed"}),
        ("battery", {"cell": "AA"}, {"cell": "AAA"}),
    ],
)
def test_a_param_changes_the_drawing(shape: str, a: dict, b: dict) -> None:
    fill = kit.Fill("solid", "#b5623a")
    assert kit.render(shape, fill, params=a) != kit.render(shape, fill, params=b)


def test_every_new_shape_is_text_free() -> None:
    for shape in ("picture_hook", "plant_pot", "battery"):
        assert "<text" not in kit.render(shape, kit.Fill("solid", "#b5623a"))


def test_a_battery_cell_is_the_size_its_row_says_it_is() -> None:
    """The drawing reads the cell the attribute states, so an AAA is the thinner cell."""
    docs = _docs(("Electronics", "Accessories", "Batteries"))
    assert docs
    for doc in docs:
        cell = next(a["value"] for a in doc["attributes"] if a["key"] == "battery_size")
        assert doc["drawing"]["params"]["cell"] == cell
