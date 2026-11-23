"""Cooking appliances (#1116, slice 1): range cookers, built-in ovens and hobs.

Home > Large Appliances held fridges, dishwashers and laundry only, so the query ``range`` met
baby monitors, water guns and jeans ("range" as a signal range or a product line) and
``range cooker 90cm`` met no cooker at all. Three types now sit in leaves of their own:
Range Cooker (dual fuel or induction, 90, 100 or 110 cm wide), Built-in Oven (single or
double) and Hob (induction, ceramic or gas). Each is a model with a series and a model number
in the scheme of gen#622, drawn by a shape of :mod:`kit_cooking` that shows its kind and its
width. The ranking checks run the no-policy baseline ranker over the templates.
"""

from __future__ import annotations

from collections import Counter

import pytest

from synthetic_ecommerce_data.domains.retail import appliance_model_numbers as amn
from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import kit, scale

ROOT = ["Home", "Large Appliances"]
#: product type -> (its leaf, its drawing shape, its kinds)
TYPES = {
    "Range Cooker": ("Range Cookers", "range_cooker",
                     {"Range Cooker (Dual Fuel)", "Range Cooker (Induction)"}),
    "Built-in Oven": ("Built-in Ovens", "built_in_oven", {"Single Oven", "Double Oven"}),
    "Hob": ("Hobs", "hob", {"Induction Hob", "Ceramic Hob", "Gas Hob"}),
}  # fmt: skip


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def index(templates) -> br.Index:
    return br.Index(templates)


def _attrs(record: dict) -> dict[str, str]:
    return {a["key"]: str(a["value"]) for a in record["attributes"]}


def _of(templates, ptype: str) -> list[dict]:
    return [r for r in templates if r["product_type"] == ptype]


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_each_cooking_type_has_its_own_leaf_its_own_shape_and_six_models_of_each_kind(
    templates, ptype
):
    leaf, shape, kinds = TYPES[ptype]
    rows = _of(templates, ptype)
    assert rows, ptype
    assert {tuple(r["category_path"]) for r in rows} == {(*ROOT, leaf)}
    assert {r["drawing"]["shape"] for r in rows} == {shape}
    count = Counter(_attrs(r)["appliance_type"] for r in rows)
    assert set(count) == kinds, count
    assert min(count.values()) >= 6, count
    assert len({r["brand"] for r in rows}) >= 2


@pytest.mark.parametrize("ptype", ["Range Cooker", "Hob"])
def test_a_range_cooker_or_hob_states_its_width_in_the_title_and_the_model_number(
    templates, ptype
):
    rows = _of(templates, ptype)
    assert rows, ptype
    for r in rows:
        width = _attrs(r)["item_width"]
        assert f" {width}cm " in r["title"], r["title"]
        assert amn.decode(_attrs(r)["model_number"])["capacity"] == int(width), r["title"]
        assert r["drawing"]["params"]["width"] == width, r["title"]


def test_an_oven_states_its_capacity_in_litres(templates):
    rows = _of(templates, "Built-in Oven")
    assert rows
    for r in rows:
        litres = _attrs(r)["capacity"]
        assert f" {litres}L " in r["title"], r["title"]
        assert amn.decode(_attrs(r)["model_number"])["capacity"] == int(litres), r["title"]


@pytest.mark.parametrize(
    ("shape", "param", "one", "other"),
    [
        ("range_cooker", "kind", "dual_fuel", "induction"),
        ("range_cooker", "width", "90", "110"),
        ("range_cooker", "ovens", "2", "3"),
        ("built_in_oven", "kind", "single", "double"),
        ("hob", "kind", "induction", "gas"),
        ("hob", "kind", "induction", "ceramic"),
        ("hob", "width", "60", "90"),
    ],
)
def test_a_param_changes_the_drawing(shape, param, one, other):
    assert shape in kit.shapes(), shape  # kit.shapes() imports every kit module first
    fill = kit.Fill("solid", "#c8312e")
    a = kit.render(shape, fill, params={param: one})
    b = kit.render(shape, fill, params={param: other})
    assert "<svg" in a and a != b


def test_range_cooker_90cm_finds_only_90cm_range_cookers(index):
    top = br.rank(index, "range cooker 90cm", 5, popular=False)
    got = [(r["product_type"], _attrs(r).get("item_width")) for r in top]
    assert got == [("Range Cooker", "90")] * 5, [r["title"] for r in top]


def test_range_meets_range_cookers_and_the_signal_range_products_without_a_policy(index):
    """Both families, as the issue's table asks: a policy, not the data, picks the intent."""
    types = Counter(r["product_type"] for r in br.rank(index, "range", 40, popular=False))
    assert types["Range Cooker"] >= 1, types
    assert set(types) - {"Range Cooker"}, types


@pytest.mark.parametrize(
    ("query", "ptype"),
    [("induction hob", "Hob"), ("gas hob", "Hob"), ("double oven", "Built-in Oven"),
     ("built-in single oven", "Built-in Oven"), ("dual fuel range cooker", "Range Cooker")],
)  # fmt: skip
def test_a_cooking_query_finds_its_own_type_first(index, query, ptype):
    top = br.rank(index, query, 5, popular=False)
    assert [r["product_type"] for r in top] == [ptype] * 5, [r["title"] for r in top]
