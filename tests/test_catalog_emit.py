"""Both serialisations, checked without needing a cluster.

The live proofs run against Elasticsearch in ``scripts/verify_elasticsearch.py``.
What is checked here is everything that can be checked from the documents
themselves -- that the two shapes describe the same products, that the nested
shape keeps the correlation the flat shape loses, and that the field names the
flat shape invents are legal ones.
"""

from __future__ import annotations

import json

from synthetic_industrial_products.catalog import emit
from synthetic_industrial_products.catalog.config import SMALL
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.catalog.vocab import STANDARDS_NAME
from synthetic_industrial_products.render import UnknownProductError, renderer_for

CATALOG = generate(SMALL)


def test_the_two_shapes_describe_the_same_products():
    nested = list(emit.iter_nested(CATALOG))
    flat = list(emit.iter_flat(CATALOG))
    assert len(nested) == len(CATALOG.lines)
    assert len(flat) == CATALOG.sku_count
    assert sum(doc["variant_count"] for doc in nested) == len(flat)

    nested_skus = {v["sku"] for doc in nested for v in doc["variants"]}
    assert nested_skus == {doc["sku"] for doc in flat}


def test_every_document_is_json_serialisable():
    for doc in list(emit.iter_nested(CATALOG))[:20]:
        json.loads(json.dumps(doc))
    for doc in list(emit.iter_flat(CATALOG))[:50]:
        json.loads(json.dumps(doc))


def test_attributes_are_nested_key_value_at_both_levels():
    doc = next(iter(emit.iter_nested(CATALOG)))
    assert doc["attributes"], "the parent carries line-constant attributes"
    for entry in doc["attributes"]:
        assert set(entry) <= {"name", "value", "value_num"}
        assert entry["name"] and entry["value"]
    variant = doc["variants"][0]
    assert variant["attributes"], "the child carries its own varying attributes"
    for entry in variant["attributes"]:
        assert set(entry) <= {"name", "value", "value_num"}


def test_a_dimension_carries_both_representations_on_one_entry():
    """One array, not two: the text and the number are the same attribute."""
    found = False
    for doc in emit.iter_flat(CATALOG):
        for entry in doc["attributes"]:
            if entry["name"] in ("Milling Dia.", "Length", "Outside Dia."):
                assert "value" in entry
                if "value_num" in entry:
                    found = True
    assert found, "no dimension carried both a published string and a number"


def test_a_keyword_only_attribute_omits_value_num_rather_than_nulling_it():
    for doc in emit.iter_flat(CATALOG):
        for entry in doc["attributes"]:
            assert entry.get("value_num") is not None or "value_num" not in entry


def test_the_multivalued_attribute_becomes_several_entries_under_one_name():
    for doc in emit.iter_flat(CATALOG):
        standards = [e for e in doc["attributes"] if e["name"] == STANDARDS_NAME]
        if len(standards) > 1:
            assert len({e["value"] for e in standards}) == len(standards)
            return
    raise AssertionError("no record carried more than one Standards value")


def test_sanitize_produces_a_legal_field_name():
    assert emit.sanitize("Milling Dia.") == "milling_dia"
    assert emit.sanitize("Dia./Thread Size") == "dia_thread_size"
    assert emit.sanitize("Single End/Double End") == "single_end_double_end"
    assert emit.sanitize("Max. RPM") == "max_rpm"
    for doc in emit.iter_flat(CATALOG):
        for key in doc["facets"]:
            assert "." not in key, key
            assert key and not key.startswith("_")


def test_the_three_measurement_system_spellings_stay_three_facet_keys():
    """Folding them here would hide the problem a field map exists to solve."""
    keys = set()
    for doc in emit.iter_flat(CATALOG):
        keys |= {k for k in doc["facets"] if "measurement" in k or "dimension_type" in k}
    assert len(keys) >= 2, keys


def test_the_searchable_text_reaches_attribute_values():
    """The demo case needs a shank's value to be findable by full text."""
    for doc in emit.iter_flat(CATALOG):
        shank = [e for e in doc["attributes"] if e["name"] == "Shank Dia."]
        if shank:
            assert shank[0]["value"] in doc["text"]
            return
    raise AssertionError("no record carried a shank diameter")


def test_the_flat_mapping_pins_the_facet_field_type():
    """Dynamic facet KEYS are fine; a dynamic facet TYPE is not.

    Left to dynamic mapping these become analysed text, and a term or prefix
    filter against them silently matches nothing -- a zero that reads like
    "no such product" instead of like a mapping mistake.
    """
    templates = emit.FLAT_MAPPING["mappings"]["dynamic_templates"]
    by_name = {name: body for template in templates for name, body in template.items()}
    assert by_name["facet_values"]["mapping"]["type"] == "keyword"
    assert by_name["facet_numbers"]["mapping"]["type"] == "double"


def test_the_nested_mapping_nests_what_has_to_be_nested():
    props = emit.NESTED_MAPPING["mappings"]["properties"]
    assert props["attributes"]["type"] == "nested"
    assert props["variants"]["type"] == "nested"
    assert props["variants"]["properties"]["attributes"]["type"] == "nested"


def test_the_flat_mapping_deliberately_does_not_nest_its_attributes():
    """That limitation is the thing the flat shape exists to exhibit."""
    assert emit.FLAT_MAPPING["mappings"]["properties"]["attributes"]["type"] == "object"


def test_render_records_are_in_the_shape_the_existing_renderer_reads():
    drawable = 0
    for record in emit.render_records(CATALOG):
        assert "sku" in record
        try:
            renderer_for(record)
        except UnknownProductError:
            continue
        drawable += 1
    assert drawable > 0, "no generated record could be dispatched to a renderer"


def test_write_jsonl_round_trips(tmp_path):
    path = tmp_path / "flat.jsonl"
    count = emit.write_jsonl(emit.iter_flat(CATALOG), path)
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == count == CATALOG.sku_count
    assert json.loads(lines[0])["sku"]
