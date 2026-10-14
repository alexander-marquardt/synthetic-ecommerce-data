"""The people roots of the retail tree are Mens, Womens and Kids (gen#304).

The tree named its audiences inconsistently (``Men``, ``Women`` but ``Kids``). Shoppers say
"mens shoes" and "womens jumpers", and the downstream vocabularies are MENS / WOMENS / KIDS, so
the roots are ``Mens`` and ``Womens``. The store's department is the top level of the path, so
it moves with them. The guard fails if a whole node ``Men`` or ``Women`` comes back at any layer.
"""

from __future__ import annotations

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

OLD_NODES = frozenset({"Men", "Women"})
NEW_ROOTS = frozenset({"Mens", "Womens", "Kids"})


@pytest.fixture(scope="module")
def built() -> scale.Scaled:
    return scale.build(sum(t["sku_count"] for t in scale.templates()) + 3000)


@pytest.fixture(scope="module")
def nested(built: scale.Scaled) -> list[dict[str, Any]]:
    return scale.documents(built)


def _old_node_paths(paths: list[Any]) -> list[Any]:
    return [p for p in paths if OLD_NODES & set(p)]


def test_no_template_path_holds_a_men_or_women_node() -> None:
    assert _old_node_paths([t["category_path"] for t in scale.templates()]) == []


def test_no_build_record_path_holds_a_men_or_women_node(built: scale.Scaled) -> None:
    assert _old_node_paths([r["category_path"] for r in built.records]) == []


def test_no_nested_document_path_holds_a_men_or_women_node(nested: list[dict[str, Any]]) -> None:
    assert _old_node_paths([d["category_path"] for d in nested]) == []


def test_no_flat_document_path_holds_a_men_or_women_node(nested: list[dict[str, Any]]) -> None:
    assert _old_node_paths([r["category_path"] for r in scale.flat(nested)]) == []


def test_the_authored_export_holds_no_men_or_women_node() -> None:
    assert _old_node_paths([d["category_path"] for d in export.documents()]) == []


def test_the_people_roots_are_mens_womens_and_kids(nested: list[dict[str, Any]]) -> None:
    assert NEW_ROOTS.issubset({d["category_path"][0] for d in nested})


@pytest.mark.parametrize(
    ("root", "expected"), [("Mens", audience.MENS), ("Womens", audience.WOMENS)]
)
def test_a_people_root_implies_its_audience(root: str, expected: str) -> None:
    assert audience.audience_of_path([root, "Shoes"]) == expected
    assert set(audience.PEOPLE_ROOTS) == NEW_ROOTS


def test_the_old_roots_imply_no_audience() -> None:
    assert [audience.audience_of_path([r, "Shoes"]) for r in sorted(OLD_NODES)] == [None, None]
