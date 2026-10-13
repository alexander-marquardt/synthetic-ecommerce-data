"""The retail tree has one root per department, and no document states a ``department`` (gen#281).

The store's department is the top level of ``category_path``, read downstream. The build had
two roots for food (``Food & Drink`` and ``Food``), a ``Baby`` root beside ``Kids`` and an
``Electricals`` root beside ``Home``, and every document also carried a ``department`` attribute
that mixed audience (Clothing) and product kind (Footwear): two departments for one product.

The guard is the closed list of top levels (:data:`DEPARTMENTS`): a root in none of them, or a
listed one no style sits under, fails here, at every layer a document passes through (the build
records, the nested documents, the flat per-SKU documents and the authored export).
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import audience  # noqa: E402
import export  # noqa: E402
import scale  # noqa: E402

#: The store's departments, and the only values the top level of a retail ``category_path`` takes.
DEPARTMENTS = frozenset(
    {
        "Women",
        "Men",
        "Kids",
        "Food & Drink",
        "Home",
        "Beauty",
        "Cleaning",
        "Toys",
        "Gifts",
        "Garden",
        "Accessories",
    }
)
#: The roots the build once had -> the first two nodes their subtree now starts with.
FOLDED_ROOTS = {
    "Food": ["Food & Drink", "Fresh Produce"],
    "Baby": ["Kids", "Baby"],
    "Electricals": ["Home", "Electricals"],
}


@pytest.fixture(scope="module")
def built() -> scale.Scaled:
    """Every template, then a few thousand SKUs of derived styles."""
    return scale.build(sum(t["sku_count"] for t in scale.templates()) + 3000)


@pytest.fixture(scope="module")
def nested(built: scale.Scaled) -> list[dict[str, Any]]:
    return scale.documents(built)


def _top_levels(docs: list[dict[str, Any]]) -> collections.Counter[str]:
    return collections.Counter(d["category_path"][0] for d in docs)


def test_the_build_records_sit_under_exactly_the_declared_departments(built: scale.Scaled) -> None:
    assert len(built.records) > len(scale.templates())  # derived styles are in it
    assert set(_top_levels(built.records)) == DEPARTMENTS


def test_the_templates_sit_under_exactly_the_declared_departments() -> None:
    assert set(_top_levels(scale.templates())) == DEPARTMENTS


def test_the_nested_documents_sit_under_exactly_the_declared_departments(
    nested: list[dict[str, Any]],
) -> None:
    assert set(_top_levels(nested)) == DEPARTMENTS


def test_the_flat_documents_sit_under_exactly_the_declared_departments(
    nested: list[dict[str, Any]],
) -> None:
    assert {r["category_path"][0] for r in scale.flat(nested)} == DEPARTMENTS


def test_the_authored_export_sits_under_declared_departments() -> None:
    assert set(_top_levels(export.documents())) <= DEPARTMENTS


@pytest.mark.parametrize(("old", "prefix"), sorted(FOLDED_ROOTS.items()), ids=sorted(FOLDED_ROOTS))
def test_a_folded_root_keeps_its_subtree_under_its_new_parent(
    old: str, prefix: list[str], built: scale.Scaled
) -> None:
    paths = [r["category_path"] for r in built.records]
    assert [p for p in paths if p[0] == old] == []
    assert any(p[:2] == prefix for p in paths)


def test_a_baby_style_is_still_sold_to_babies() -> None:
    assert audience.audience_of_path(["Kids", "Baby", "Coats & Jackets"]) == audience.BABY


def test_no_nested_document_carries_a_department_attribute(nested: list[dict[str, Any]]) -> None:
    assert [d["product_id"] for d in nested if _has_department(d)] == []


def test_no_flat_document_carries_a_department_column_or_facet(
    nested: list[dict[str, Any]],
) -> None:
    flat = scale.flat(nested)
    assert flat
    assert [
        r["sku"] for r in flat if "department" in r or "department" in r.get("facets", {})
    ] == []


def test_the_authored_export_carries_no_department_attribute() -> None:
    docs = export.documents()
    assert docs
    assert [d["product_id"] for d in docs if _has_department(d)] == []


def test_the_exported_field_list_has_no_department_entry() -> None:
    assert "department" not in {key for key, _, _ in export.FACTS.values()}


def _has_department(doc: dict[str, Any]) -> bool:
    entries = doc["attributes"] + [e for v in doc["variants"] for e in v["attributes"]]
    return any(e["key"] == "department" for e in entries)
