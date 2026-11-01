"""The beauty lines of the ceiling build keep their packs apart (gen#748).

Apart from ``test_retail_pack_looks_748.py`` because the build costs minutes: the tests there read
a line's look from its name, and these read the lines the catalog holds.
"""

from __future__ import annotations

import pytest

from retail_ceiling import ceiling_build
from test_retail_pack_looks_748 import KINDS, _outline, _spec


def _products(kind: str) -> list[dict]:
    return [r for r in ceiling_build().records if r["product_type"] == kind]


def _lines(kind: str) -> dict[str, dict]:
    return {r.get("product_line") or r["title"]: r for r in _products(kind)}


@pytest.mark.parametrize(
    ("kind", "most"),
    [("Foundation", 50), ("Face Cream", 20), ("Moisturiser", 5), ("Bath Salts", 3), ("Perfume", 2)],
)
def test_every_line_of_a_kind_draws_its_own_outline(kind: str, most: int) -> None:
    lines = _lines(kind)
    assert len(lines) > most
    assert len({_outline(r, r["skus"][0]) for r in lines.values()}) == len(lines)


@pytest.mark.parametrize("kind", KINDS)
def test_no_two_lines_of_a_brand_share_a_form_and_a_top(kind: str) -> None:
    """A brand's products fill a page together. A new line that lands on a taken form and top needs
    a new ``pack_looks.BASES`` entry."""
    by_brand: dict[str, list[tuple[str, str]]] = {}
    for rec in _lines(kind).values():
        look = _spec(rec)
        by_brand.setdefault(rec["brand"], []).append((look.get("form"), look.get("top")))
    for brand, looks in by_brand.items():
        assert len(set(looks)) == len(looks), brand


@pytest.mark.parametrize("kind", KINDS)
def test_the_skus_of_a_product_share_one_pack(kind: str) -> None:
    products = _products(kind)
    assert products
    for rec in products:
        assert len({_outline(rec, sku) for sku in rec["skus"]}) == 1, rec["product_id"]
