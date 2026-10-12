"""No retail document carries ``color_family`` (gen#186).

``color_family`` was each SKU's shade lowercased through a fixed table ("Navy Stripe" ->
"navy"). PRISM showed it beside ``color`` as a second color facet, listing the
same products twice. Grouping shades into a family is a PRISM vocabulary group, which a
merchandiser can see and change, so the generator does not bake one in.

Checked at every layer a document passes through: the build records' SKUs, the nested
standard documents (product and variant attribute entries), the flat per-SKU documents,
and the exported field list (:data:`export.OPTIONS`, :data:`export.FACTS`).
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
import scale  # noqa: E402

#: Both spellings the field took: its key and its display name.
GONE = ("color_family", "Color family")


@pytest.fixture(scope="module")
def built() -> scale.Scaled:
    """Every template, then a few thousand SKUs of derived styles."""
    return scale.build(sum(t["sku_count"] for t in scale.templates()) + 3000)


@pytest.fixture(scope="module")
def nested(built: scale.Scaled) -> list[dict[str, Any]]:
    return scale.documents(built)


def _carriers(docs: list[dict[str, Any]]) -> list[str]:
    """The product ids of the documents whose JSON names either spelling anywhere."""
    out = []
    for d in docs:
        blob = json.dumps(d, ensure_ascii=False)
        if any(word in blob for word in GONE):
            out.append(d["product_id"])
    return out


def test_no_build_record_sku_carries_color_family(built: scale.Scaled) -> None:
    assert len(built.records) > len(scale.templates())  # derived styles are in it
    bad = [r["product_id"] for r in built.records if any("color_family" in s for s in r["skus"])]
    assert bad == []


def test_no_nested_document_carries_color_family(nested: list[dict[str, Any]]) -> None:
    assert _carriers(nested) == []


def test_no_flat_document_carries_color_family(nested: list[dict[str, Any]]) -> None:
    assert _carriers(scale.flat(nested)) == []


def test_the_authored_export_carries_no_color_family() -> None:
    assert _carriers(export.documents()) == []


def test_the_exported_field_list_has_no_color_family_entry() -> None:
    specs = {**export.OPTIONS, **export.FACTS}
    assert [f for f, (key, name, _) in specs.items() if {f, key, name} & set(GONE)] == []
