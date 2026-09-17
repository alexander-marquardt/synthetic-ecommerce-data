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
# The trap these guard is one fact: a product's image is NOT a drawing of that
# product. A family shares one generic drawing, so a URL assembled from the
# product's own SKU is dead for every record in the catalog -- and dead in a
# way that spot-checking a handful of records will not reveal, because every
# record looks equally plausible.


def test_the_image_url_is_built_from_the_image_id_never_from_the_product_sku():
    docs = list(emit.iter_flat(CATALOG))
    assert docs
    for doc in docs:
        assert doc["image_id"], "every variant carries an image"
        assert doc["image_url"].endswith(f"/{doc['image_id']}.png")
        assert doc["sku"] not in doc["image_url"]


def test_the_image_id_is_never_the_products_own_sku():
    """Which is what makes building the URL from the SKU a dead link every time.

    Without this the test above could pass on a catalog where the two agreed,
    and would then be proving nothing about the rule it is named for.
    """
    for doc in emit.iter_flat(CATALOG):
        assert doc["image_id"] != doc["sku"]


def test_the_card_and_detail_urls_are_different_files():
    for doc in emit.iter_flat(CATALOG):
        assert doc["image_url"] != doc["image_detail_url"]
        assert "/card/" in doc["image_url"]
        assert "/detail/" in doc["image_detail_url"]


def test_the_base_url_is_configurable_and_a_trailing_slash_does_not_double_up():
    for doc in emit.iter_flat(CATALOG, "https://example.invalid/i/"):
        assert doc["image_url"].startswith("https://example.invalid/i/")
        assert "//i//" not in doc["image_url"]


def test_a_product_line_carries_the_same_image_as_its_variants():
    """A family page and its variants show one drawing; that is what a family is."""
    for doc in emit.iter_nested(CATALOG):
        assert doc["image_id"]
        assert doc["image_url"].endswith(f"/{doc['image_id']}.png")
        for variant in doc["variants"]:
            assert variant["image_id"] == doc["image_id"]


def test_the_manifest_lists_each_image_once_and_accounts_for_every_reference():
    rows = list(emit.iter_image_manifest(CATALOG))
    ids = [row["image_id"] for row in rows]
    assert len(ids) == len(set(ids)), "one row per image file, not per reference"

    referenced = [line.image_id for line in CATALOG.lines]
    referenced += [child.image_id for _, child in CATALOG.all_skus()]
    assert set(ids) == set(referenced)
    assert sum(row["referenced_by"] for row in rows) == len(referenced)
    assert all(row["referenced_by"] > 1 for row in rows), "ten drawings, thousands of products"


def test_the_manifest_is_far_smaller_than_the_catalog():
    """Ten files behind four thousand products is the point of the change.

    A manifest that grew with the catalog would mean per-SKU images had come
    back without anyone noticing.
    """
    rows = list(emit.iter_image_manifest(CATALOG))
    assert len(rows) == 10
    # This fixture is a SMALL catalog; the shipped one is 4,600-odd variants
    # behind the same ten files.
    assert CATALOG.sku_count > 20 * len(rows)


def test_the_manifest_path_is_the_url_tail():
    for row in emit.iter_image_manifest(CATALOG, "https://example.invalid/i"):
        assert row["url"] == f"https://example.invalid/i/{row['path']}"
        assert row["detail_url"] == f"https://example.invalid/i/{row['detail_path']}"
        assert row["path"] == f"card/{row['image_id']}.png"
        assert row["detail_path"] == f"detail/{row['image_id']}.png"


def test_the_manifest_and_the_records_agree_on_every_url():
    hosted = {row["url"] for row in emit.iter_image_manifest(CATALOG)}
    hosted |= {row["detail_url"] for row in emit.iter_image_manifest(CATALOG)}
    wanted = {doc["image_url"] for doc in emit.iter_flat(CATALOG)}
    wanted |= {doc["image_detail_url"] for doc in emit.iter_flat(CATALOG)}
    assert wanted == hosted, "a record URL with no manifest row is a dead link"


def test_the_nested_shape_carries_the_same_urls_as_the_flat_one():
    flat = {doc["sku"]: doc["image_url"] for doc in emit.iter_flat(CATALOG)}
    for doc in emit.iter_nested(CATALOG):
        for variant in doc["variants"]:
            assert variant["image_url"] == flat[variant["sku"]]


def test_every_image_id_names_a_drawing_that_exists():
    from synthetic_industrial_products.render.generic import IMAGE_IDS

    assert {row["image_id"] for row in emit.iter_image_manifest(CATALOG)} == set(IMAGE_IDS)


def test_an_image_id_with_no_drawing_is_refused_rather_than_published_dead():
    """A URL for a drawing nobody renders is worse than no URL at all.

    The bare id does not claim to resolve; the URL does.
    """
    import dataclasses

    import pytest

    line = CATALOG.lines[0]
    broken = dataclasses.replace(
        CATALOG, lines=(dataclasses.replace(line, image_id="no_such_drawing"),)
    )
    with pytest.raises(emit.UnresolvedImageError):
        list(emit.iter_flat(broken))
    with pytest.raises(emit.UnresolvedImageError):
        list(emit.iter_image_manifest(broken))
