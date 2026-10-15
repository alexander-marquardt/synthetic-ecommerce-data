"""No retail document carries ``new_in`` (gen#277).

The flag added nothing a shopper could use: on the served catalogue 337 of 9,337 retail
products were ``yes``, so the top results all read ``no`` and the sidebar showed a "New in"
facet with one value. It was no ranking signal either. ``promotion`` stays (gen#189 replaced
``offer`` with it).

Checked at every layer a document passes through, as gen#186 does for ``color_family``: the
build records, the nested standard documents, the flat per-SKU documents, the authored export
and the exported field list (:data:`export.FACTS`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402 -- the prototype's own directory is its import root
import real_classes as rc  # noqa: E402
import scale  # noqa: E402

#: Every spelling the flag took: its key, its display name and its badge label.
GONE = ("new_in", "New in", "New In")


@pytest.fixture(scope="module")
def built() -> scale.Scaled:
    """Every template, then a few thousand SKUs of derived styles."""
    return scale.build(sum(t["sku_count"] for t in scale.templates()) + 3000)


@pytest.fixture(scope="module")
def nested(built: scale.Scaled) -> list[dict[str, Any]]:
    return scale.documents(built)


def _carriers(docs: list[dict[str, Any]]) -> list[str]:
    """The product ids of the documents whose JSON names any spelling anywhere."""
    out = []
    for d in docs:
        blob = json.dumps(d, ensure_ascii=False)
        if any(word in blob for word in GONE):
            out.append(d["product_id"])
    return out


def test_no_build_record_carries_new_in(built: scale.Scaled) -> None:
    assert len(built.records) > len(scale.templates())  # derived styles are in it
    assert _carriers(built.records) == []


def test_no_nested_document_carries_new_in(nested: list[dict[str, Any]]) -> None:
    assert _carriers(nested) == []


def test_no_flat_document_carries_new_in(nested: list[dict[str, Any]]) -> None:
    assert _carriers(scale.flat(nested)) == []


def test_the_authored_export_carries_no_new_in() -> None:
    docs = export.documents()
    assert docs
    assert _carriers(docs) == []


def test_the_exported_field_list_has_no_new_in_entry() -> None:
    specs = {**export.OPTIONS, **export.FACTS}
    assert [f for f, (key, name, _) in specs.items() if {f, key, name} & set(GONE)] == []


def test_the_authored_class_docs_carry_no_new_in_flag_or_badge() -> None:
    docs = rc.class_docs()
    assert docs
    assert _carriers(docs) == []
    assert "new_in" not in rc.BOOLEANS


def test_promotion_is_kept() -> None:
    assert "promotion" in export.FACTS
    assert any("promotion" in d for d in rc.class_docs())
