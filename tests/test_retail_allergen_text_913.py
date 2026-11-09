"""A grocery SKU's description names no allergen the SKU does not hold (#913).

A grocery description is written once for the style, and each SKU states its own ``contains``
and ``may_contain``. ``attribute_text.allergen_lines`` reads a record's "Contains:" and "May
contain:" lines and names each SKU they overstate. Its count is held at zero on the ceiling
build, and the check is held against hand-made rows so it cannot go quiet.
"""

from __future__ import annotations

from typing import Any

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import attribute_text

#: The food SKUs under a description with an allergen line: the ceiling build holds about 10,000,
#: so a check that reads none of them cannot pass.
MIN_FOOD_SKUS = 5_000


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return ceiling_build().records


def _rec(description: str, *skus: dict[str, Any]) -> dict[str, Any]:
    return {
        "product_id": "GRC-T-1",
        "title": "A Bar",
        "description": description,
        "skus": list(skus),
    }


def _sku(sku: str, contains: tuple[str, ...] = (), may: tuple[str, ...] = ()) -> dict[str, Any]:
    out: dict[str, Any] = {"sku": sku}
    if contains:
        out["contains"] = list(contains)
    if may:
        out["may_contain"] = list(may)
    return out


def test_no_food_sku_of_the_ceiling_build_is_described_with_an_allergen_it_does_not_hold(ceiling):
    bad = [
        f"{r['product_id']}: {line}" for r in ceiling for line in attribute_text.allergen_lines(r)
    ]
    assert not bad, f"{len(bad)} SKUs disagree: {bad[:20]}"


def test_the_nut_free_milk_bar_of_the_issue_says_no_peanuts(ceiling):
    rec = next(r for r in ceiling if r["product_id"] == "GRC-CHB-0001")
    milk = [s for s in rec["skus"] if s["flavor"] == "Milk"]
    assert milk and all("Nut Free" in s["dietary"] for s in milk)
    assert "Peanut" not in rec["description"].split("Contains:")[-1], rec["description"]


def test_the_check_reads_enough_food_skus_to_mean_something(ceiling):
    described = [
        s
        for r in ceiling
        if "Contains:" in r.get("description", "") or "May contain:" in r.get("description", "")
        for s in r.get("skus", ())
    ]
    assert len(described) >= MIN_FOOD_SKUS, len(described)


# ---- the check against hand-made rows ------------------------------------------------------


def test_a_contains_line_naming_another_flavors_allergen_disagrees():
    rec = _rec(
        "Chocolate bars. Contains: Peanuts, Milk, Soy.",
        _sku("A", ("Peanuts", "Milk", "Soy")),
        _sku("B", ("Milk", "Soy")),
    )
    assert attribute_text.allergen_lines(rec) == [
        "SKU B does not hold ['Peanuts'] but the text says Contains"
    ]


def test_a_contains_line_naming_an_allergen_a_sku_only_traces_disagrees():
    rec = _rec("Biscuits. Contains: Egg.", _sku("A", ("Egg",)), _sku("B", may=("Egg",)))
    assert attribute_text.allergen_lines(rec) == [
        "SKU B does not hold ['Egg'] but the text says Contains"
    ]


def test_a_contains_line_every_sku_holds_agrees():
    rec = _rec(
        "Chocolate bars. Contains: Milk, Soy.",
        _sku("A", ("Peanuts", "Milk", "Soy")),
        _sku("B", ("Milk", "Soy")),
    )
    assert attribute_text.allergen_lines(rec) == []


def test_a_may_contain_line_agrees_with_a_sku_that_contains_the_allergen():
    rec = _rec(
        "Chocolate bars. May contain: Peanuts, Tree Nuts.",
        _sku("A", ("Peanuts",), ("Tree Nuts",)),
        _sku("B", may=("Peanuts", "Tree Nuts")),
    )
    assert attribute_text.allergen_lines(rec) == []


def test_a_may_contain_line_naming_a_trace_a_sku_lacks_disagrees():
    rec = _rec("Fruit gums. May contain: Milk.", _sku("A", may=("Milk",)), _sku("B"))
    assert attribute_text.allergen_lines(rec) == [
        "SKU B does not hold ['Milk'] but the text says May contain"
    ]


def test_a_description_with_no_allergen_line_agrees():
    rec = _rec("A multi-surface spray. Contains 750ml.", _sku("A"))
    assert attribute_text.allergen_lines(rec) == []


def test_disagreements_counts_the_allergen_rows():
    rec = _rec("Bars. Contains: Gluten.", _sku("A", ("Gluten",)), _sku("B"))
    assert attribute_text.disagreements([rec]) == [
        "GRC-T-1: SKU B does not hold ['Gluten'] but the text says Contains"
    ]
