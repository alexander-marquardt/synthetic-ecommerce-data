"""A row with peanuts or a tree nut also carries the allergen and ingredient value ``nuts`` (#909).

"Nuts is an ingredient and allergen .. so is peanuts .. and any product that has peanuts, also
has an allergen that is nuts" (the maintainer, 2026-11-08, elastic/prism-retail-and-industrial#832).
Without a ``nuts`` value in the three facets the ALLERGEN and INGREDIENT vocabularies have none, so
``bread without nuts`` excludes nothing. Read over the default build's flat rows, the ones served.
The word lists are this module's own: a wrong generator table cannot pass by agreeing with itself.
"""

from __future__ import annotations

from functools import cache

from synthetic_ecommerce_data.domains.retail import grocery

NUTS = "nuts"
#: The allergen values that are nuts.
NUT_ALLERGENS = frozenset({"peanuts", "tree nuts"})
#: The base ingredients that are a tree nut.
TREE_NUT_BASES = frozenset(
    {"almonds", "brazil nuts", "cashews", "hazelnuts", "walnuts", "pine nuts", "pecans",
     "pistachios", "macadamias"}
)
FACETS = ("contains", "may_contain", "ingredient_base")


@cache
def rows() -> tuple[dict, ...]:
    return tuple(grocery.flat(grocery.documents(grocery.build(grocery.TARGET))))


def facet(row: dict, key: str) -> set[str]:
    return set(row["facets"].get(key, ()))


def test_a_row_that_contains_peanuts_or_tree_nuts_contains_nuts() -> None:
    nutty = [r for r in rows() if facet(r, "contains") & NUT_ALLERGENS]
    assert len(nutty) > 100
    assert [r["sku"] for r in nutty if NUTS not in facet(r, "contains")] == []


def test_a_row_that_may_contain_peanuts_or_tree_nuts_may_contain_or_contains_nuts() -> None:
    traced = [r for r in rows() if facet(r, "may_contain") & NUT_ALLERGENS]
    assert len(traced) > 100
    missing = [r["sku"] for r in traced
               if NUTS not in facet(r, "may_contain") | facet(r, "contains")]
    assert missing == []
    # As for any value, a trace the row already contains is not stated again.
    assert [r["sku"] for r in rows()
            if NUTS in facet(r, "may_contain") & facet(r, "contains")] == []
    assert any(NUTS in facet(r, "may_contain") for r in traced)


def test_a_row_whose_ingredients_hold_peanuts_or_a_tree_nut_holds_nuts() -> None:
    nutty = [r for r in rows() if facet(r, "ingredient_base") & (TREE_NUT_BASES | {"peanuts"})]
    assert len(nutty) > 100
    assert {b for r in nutty for b in facet(r, "ingredient_base")} >= {"peanuts", "hazelnuts"}
    assert [r["sku"] for r in nutty if NUTS not in facet(r, "ingredient_base")] == []


def test_a_row_with_no_nut_carries_no_nuts() -> None:
    nut_values = NUT_ALLERGENS | TREE_NUT_BASES
    clean = [r for r in rows() if not any(facet(r, k) & nut_values for k in FACETS)]
    assert len(clean) > 1000
    assert [(r["sku"], k) for r in clean for k in FACETS if NUTS in facet(r, k)] == []
