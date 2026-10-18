"""Pricing unit and order multiple are two plain published fields on every SKU (gen#14).

They are not variants: a SKU states how its shown price is quoted (``pricing_unit``) and the
multiple it is ordered in (``order_multiple``), beside ``price_usd`` and ``stock``. A SKU that
publishes a ``Package Quantity`` above 1 is priced per pack; every other SKU is priced each.
The fields are in the standard, both Elasticsearch mappings and the PRISM field map, so a
query can see them.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.core import emit, standard
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.prism import field_map

FIELDS = ("pricing_unit", "order_multiple")


@pytest.fixture(scope="module")
def catalog():
    return generate(SMALL)


@pytest.fixture(scope="module")
def flat(catalog):
    return list(emit.iter_flat(catalog))


@pytest.fixture(scope="module")
def nested(catalog):
    return list(emit.iter_nested(catalog))


def _pack(doc) -> float | None:
    """The pack the document's own attribute entry states, as a number."""
    return next(
        (a["value_canonical"] for a in doc["attributes"] if a["key"] == "units_per_pack"), None
    )


@pytest.mark.parametrize("field", FIELDS)
def test_every_flat_sku_publishes_the_field(flat, field):
    assert flat
    assert [d["sku"] for d in flat if d.get(field) is None] == []


@pytest.mark.parametrize("field", FIELDS)
def test_every_nested_variant_publishes_the_field(nested, field):
    variants = [v for doc in nested for v in doc["variants"]]
    assert variants
    assert [v["sku"] for v in variants if v.get(field) is None] == []


def test_the_order_multiple_is_a_positive_whole_number(flat):
    values = {d.get("order_multiple") for d in flat}
    assert values
    assert all(isinstance(v, int) and not isinstance(v, bool) and v >= 1 for v in values)


def test_a_pack_above_one_is_priced_per_pack_and_every_other_sku_each(flat):
    packed = [d for d in flat if (_pack(d) or 1) > 1]
    assert packed, "the small build holds no pack-sold SKU, so the rule is not exercised"
    assert {d.get("pricing_unit") for d in packed} == {"Per Pack"}
    single = [d for d in flat if (_pack(d) or 1) <= 1]
    assert single, "the small build holds no single-unit SKU"
    assert {d.get("pricing_unit") for d in single} == {"Each"}


def test_the_nested_variant_states_what_the_flat_document_states(flat, nested):
    by_sku = {d["sku"]: d for d in flat}
    for doc in nested:
        for variant in doc["variants"]:
            twin = by_sku[variant["sku"]]
            assert (variant.get("pricing_unit"), variant.get("order_multiple")) == (
                twin.get("pricing_unit"),
                twin.get("order_multiple"),
            )


@pytest.mark.parametrize("field", FIELDS)
def test_the_standard_names_the_field(field):
    assert field in standard.VARIANT_FIELDS
    assert field in standard._FLAT_VARIANT_FIELDS


@pytest.mark.parametrize("field", FIELDS)
def test_both_mappings_declare_the_field(field):
    nested = emit.NESTED_MAPPING["mappings"]["properties"]["variants"]["properties"]
    assert field in nested
    assert field in emit.FLAT_MAPPING["mappings"]["properties"]


@pytest.mark.parametrize("field", FIELDS)
def test_the_prism_field_map_carries_the_field(field):
    assert f"source: {field}" in "\n".join(field_map._structural_fields())
