"""Every product carries a readable ``product_type_label`` (gen#331).

The industrial ``product_type`` is a snake_case id the catalogue repo keys on
(``hammer_ball_pein``); a shopper reads it as a field name. The id stays; the label beside
it is plain English from one table, and a retail product's label is its ``product_type``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import emit, standard
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.taxonomy import LEAVES
from synthetic_ecommerce_data.domains.industrial.type_labels import PRODUCT_TYPE_LABELS, label_for

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
CATALOG = generate(SMALL)


def test_every_emitted_type_has_a_label():
    assert sorted(set(LEAVES) - set(PRODUCT_TYPE_LABELS)) == []


def test_the_table_names_no_type_that_does_not_exist():
    assert PRODUCT_TYPE_LABELS, "the table is empty"
    assert sorted(set(PRODUCT_TYPE_LABELS) - set(LEAVES)) == []


def test_no_label_is_an_id():
    assert PRODUCT_TYPE_LABELS, "the table is empty"
    assert [k for k, v in PRODUCT_TYPE_LABELS.items() if "_" in v or v == k] == []


def test_every_label_starts_with_a_capital_letter():
    assert PRODUCT_TYPE_LABELS, "the table is empty"
    assert [k for k, v in PRODUCT_TYPE_LABELS.items() if not v[:1].isupper()] == []


def test_a_label_names_one_type():
    assert PRODUCT_TYPE_LABELS, "the table is empty"
    labels = list(PRODUCT_TYPE_LABELS.values())
    assert sorted({v for v in labels if labels.count(v) > 1}) == []


@pytest.mark.parametrize(
    ("type_key", "label"),
    [
        ("hammer_ball_pein", "Ball Pein Hammer"),
        ("hammer_claw", "Claw Hammer"),
        ("end_mill_square", "Square End Mill"),
        ("nut_hex", "Hex Nut"),
    ],
)
def test_plain_shopper_english(type_key, label):
    assert label_for(type_key) == label


def test_industrial_documents_carry_the_label_beside_the_unchanged_id():
    for doc in [*emit.iter_nested(CATALOG), *emit.iter_flat(CATALOG)]:
        assert doc["product_type"] in LEAVES
        assert doc.get("product_type_label") == label_for(doc["product_type"]), doc["product_id"]
        assert doc["product_type_label"], doc["product_id"]


def test_the_mappings_type_the_label_a_keyword():
    for mapping in (emit.NESTED_MAPPING, emit.FLAT_MAPPING):
        assert mapping["mappings"]["properties"].get("product_type_label") == {"type": "keyword"}


def test_the_standard_requires_the_label():
    doc = next(iter(emit.iter_nested(CATALOG)))
    assert standard.check_document(doc) == []
    bare = {k: v for k, v in doc.items() if k != "product_type_label"}
    assert any("product_type_label" in problem for problem in standard.check_document(bare))


def test_a_retail_product_is_labelled_by_its_type():
    if str(RETAIL) not in sys.path:
        sys.path.insert(0, str(RETAIL))
    import export  # noqa: PLC0415 -- the prototype's own directory is its import root

    docs = export.documents()
    assert [d["product_id"] for d in docs if d.get("product_type_label") != d["product_type"]] == []
    flat = export.flat_documents()[:200]
    assert [d["sku"] for d in flat if d.get("product_type_label") != d["product_type"]] == []
