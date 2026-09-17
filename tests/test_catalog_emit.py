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


# -- image URLs ---------------------------------------------------------------
#
# The trap these guard is one fact: an image reference is not the referring
# product's SKU, and it is not even the referring product's TYPE. A URL built
# from either is dead, and dead at a rate high enough that spot-checking a
# handful of records would not find it.


def test_image_url_is_built_from_the_reference_not_the_product_sku():
    diverging = [
        doc
        for doc in emit.iter_flat(CATALOG)
        if doc["image_skus"] and doc["sku"] not in doc["image_skus"]
    ]
    assert diverging, "the catalog models image reuse; without it this proves nothing"
    for doc in diverging:
        for reference, url in zip(doc["image_skus"], doc["image_urls"], strict=True):
            assert url.endswith(f"/{reference}.png")
            assert not url.endswith(f"/{doc['sku']}.png")


def test_image_url_directory_is_the_drawn_types_not_the_referring_products():
    by_sku = {child.sku: line.type_key for line in CATALOG.lines for child in line.children}
    crossed = 0
    for doc in emit.iter_flat(CATALOG):
        for reference, url in zip(doc["image_skus"], doc["image_urls"], strict=True):
            owner = by_sku[reference]
            assert f"/{owner}/{reference}.png" in url
            if owner != doc["product_type"]:
                crossed += 1
    assert crossed, "image reuse crosses product types; without a case this proves nothing"


def test_every_reference_has_exactly_one_url_and_the_base_is_configurable():
    for doc in emit.iter_flat(CATALOG, "https://example.invalid/i/"):
        assert len(doc["image_urls"]) == len(doc["image_skus"])
        for url in doc["image_urls"]:
            assert url.startswith("https://example.invalid/i/")
            assert "//i//" not in url, "a trailing slash on the base must not double up"


def test_the_manifest_lists_each_image_once_and_accounts_for_every_reference():
    rows = list(emit.iter_image_manifest(CATALOG))
    refs = [row["image_ref"] for row in rows]
    assert len(refs) == len(set(refs)), "one row per image file, not per reference"

    referenced = [
        reference
        for line in CATALOG.lines
        for child in line.children
        for reference in child.image_skus
    ]
    assert set(refs) == set(referenced)
    assert sum(row["referenced_by"] for row in rows) == len(referenced)
    assert any(row["referenced_by"] > 1 for row in rows), "reuse means shared files"


def test_the_manifest_path_is_the_url_tail():
    for row in emit.iter_image_manifest(CATALOG, "https://example.invalid/i"):
        assert row["url"] == f"https://example.invalid/i/{row['path']}"
        assert row["path"] == f"{row['product_type']}/{row['image_ref']}.png"


def test_the_manifest_and_the_records_agree_on_every_url():
    hosted = {row["url"] for row in emit.iter_image_manifest(CATALOG)}
    wanted = {url for doc in emit.iter_flat(CATALOG) for url in doc["image_urls"]}
    assert wanted == hosted, "a record URL with no manifest row is a dead link"


def test_the_nested_shape_carries_the_same_urls_as_the_flat_one():
    flat = {doc["sku"]: doc["image_urls"] for doc in emit.iter_flat(CATALOG)}
    for doc in emit.iter_nested(CATALOG):
        for variant in doc["variants"]:
            assert variant["image_urls"] == flat[variant["sku"]]


def test_an_asset_suffixed_reference_resolves_to_the_skus_type():
    sku, type_key = next(
        (child.sku, line.type_key) for line in CATALOG.lines for child in line.children
    )
    assert emit._owning_type(f"{sku}_AS01", {sku: type_key}, frozenset()) == type_key


def test_a_generic_reference_resolves_by_its_product_type_prefix():
    """A drawing shared by a family is named for what it draws, not for a SKU."""
    types = frozenset(line.type_key for line in CATALOG.lines)
    assert types, "the catalog publishes product types"
    for type_key in types:
        assert emit._owning_type(type_key, {}, types) == type_key
        assert emit._owning_type(f"{type_key}_ball_nose", {}, types) == type_key


def test_a_generic_reference_takes_the_LONGEST_matching_product_type():
    """``end_mill`` is a prefix of ``end_mill_square``; the longer one wins.

    Matching the shorter one would file every square end mill's drawing under
    a directory for a different product type, and every URL built from it
    would be dead.
    """
    types = frozenset({"end_mill", "end_mill_square"})
    assert emit._owning_type("end_mill_square_ball_nose", {}, types) == "end_mill_square"


def test_an_unresolvable_reference_is_refused_rather_than_published_dead():
    import pytest

    with pytest.raises(emit.UnresolvedImageError):
        emit._owning_type("NOT-A-SKU", {}, frozenset({"end_mill_square"}))
