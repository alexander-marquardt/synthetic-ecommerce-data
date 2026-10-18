"""Both serialisations, checked without needing a cluster.

The live proofs run against Elasticsearch in ``scripts/verify_elasticsearch.py``.
What is checked here is everything that can be checked from the documents
themselves -- that the two shapes describe the same products, that the nested
shape keeps the correlation the flat shape loses, and that the field names the
flat shape invents are legal ones.
"""

from __future__ import annotations

import json

import pytest

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.render import UnknownProductError, renderer_for
from synthetic_ecommerce_data.domains.industrial.taxonomy import product_type_for_image
from synthetic_ecommerce_data.domains.industrial.vocab import STANDARDS_NAME

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


ENTRY_FIELDS = {"key", "name", "value", "unit_code", "value_canonical"}


def test_attributes_are_nested_key_value_at_both_levels():
    doc = next(iter(emit.iter_nested(CATALOG)))
    assert doc["attributes"], "the parent carries line-constant attributes"
    for entry in doc["attributes"]:
        assert set(entry) <= ENTRY_FIELDS
        assert entry["key"] and entry["name"] and entry["value"]
    variant = doc["variants"][0]
    assert variant["attributes"], "the child carries its own varying attributes"
    for entry in variant["attributes"]:
        assert set(entry) <= ENTRY_FIELDS


def test_a_dimension_carries_its_split_parts_on_one_entry():
    """One array, not two: the magnitude, its unit and the number are one attribute."""
    found = False
    for doc in emit.iter_flat(CATALOG):
        for entry in doc["attributes"]:
            if entry["name"] in ("Milling Dia.", "Length", "Outside Dia.") and "unit_code" in entry:
                assert "value" in entry and "value_canonical" in entry
                found = True
    assert found, "no dimension carried a magnitude, a unit code and a canonical number"


def test_an_unmeasured_attribute_omits_the_unit_parts_rather_than_nulling_them():
    for doc in emit.iter_flat(CATALOG):
        for entry in doc["attributes"]:
            for part in ("unit_code", "value_canonical"):
                assert entry.get(part) is not None or part not in entry
            assert ("unit_code" in entry) == ("value_canonical" in entry), entry


def test_a_metric_tap_publishes_pitch_in_mm_and_an_inch_tap_threads_per_inch_in_tpi():
    """Two quantities under two keys, as real catalogs publish them (#42).

    The published string is a bare number either way; only the generator knows
    which it is. A metric tap's ``Pitch`` is millimetres, an inch tap's
    ``Threads per Inch`` is ``TPI``, and neither tap carries the other's key.
    """
    seen = set()
    for doc in emit.iter_nested(CATALOG):
        for variant in doc["variants"]:
            entries = {e["name"]: e for e in variant["attributes"]}
            if "Thread Size" not in entries or doc["product_type"] != "tap_spiral_point":
                continue
            metric = entries["Thread Size"]["value"].startswith("M")
            names = ("Thread Pitch", "Threads per Inch")
            ours, theirs = names if metric else names[::-1]
            assert theirs not in entries, entries
            if ours in entries:
                assert entries[ours]["unit_code"] == ("MMT" if metric else "TPI"), entries
                assert entries[ours]["key"] == ("thread_pitch" if metric else "threads_per_inch")
                seen.add(metric)
    assert seen == {True, False}, "the sample needs both a metric and an inch tap"


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


def test_the_measurement_system_is_one_facet_key():
    """#497 merged the three spellings into ``Measurement System``: one key, and no other."""
    keys = set()
    for doc in emit.iter_flat(CATALOG):
        keys |= {k for k in doc["facets"] if "measurement" in k or "dimension_type" in k}
    assert keys == {"measurement_system"}, keys


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
# One drawing per SKU, drawn from that SKU's own values, served from the image
# bundle's folder (elastic/prism-industrial-products#103). The traps these
# guard: a SKU showing a sibling's drawing, a URL that no manifest row backs,
# and a URL pointing at a third-party host.


def test_every_sku_names_its_own_drawing():
    for doc in emit.iter_flat(CATALOG):
        assert doc["image_id"] == f"{doc['product_type']}/{doc['product_id']}/{doc['sku']}"
        assert doc["image_url"] == f"{emit.DEFAULT_IMAGE_BASE_URL}/{doc['image_id']}.svg"
        assert doc["image_detail_url"] == doc["image_url"], "one SVG serves both views"


def test_the_default_base_is_the_bundle_folder_not_a_third_party_host():
    """Images are served from the pinned bundle, never from a personal site."""
    assert emit.DEFAULT_IMAGE_BASE_URL.startswith("/")
    assert "://" not in emit.DEFAULT_IMAGE_BASE_URL


def test_the_base_url_is_configurable_and_a_trailing_slash_does_not_double_up():
    for doc in emit.iter_flat(CATALOG, "https://example.invalid/i/"):
        assert doc["image_url"].startswith("https://example.invalid/i/")
        assert "//i//" not in doc["image_url"]


def test_a_product_shows_its_first_variants_drawing():
    for doc in emit.iter_nested(CATALOG):
        assert doc["image_id"] == doc["variants"][0]["image_id"]
        for variant in doc["variants"]:
            assert variant["image_id"].endswith("/" + variant["sku"])


def test_the_manifest_has_one_row_per_sku_with_its_digest():
    rows = list(emit.iter_image_manifest(CATALOG))
    assert len(rows) == CATALOG.sku_count
    assert {row["image_id"] for row in rows} == {c.image_id for _, c in CATALOG.all_skus()}
    for row in rows:
        assert row["path"] == f"{row['image_id']}.svg"
        assert row["url"] == f"{emit.DEFAULT_IMAGE_BASE_URL}/{row['path']}"
        assert len(row["sha256"]) == 64
        assert row["bytes"] > 0
        assert row["geometry"] in ("record", "partial", "nominal")
        assert row["product_type"] == product_type_for_image(row["image_id"])


def test_the_manifest_and_the_records_agree_on_every_url():
    hosted = {row["url"] for row in emit.iter_image_manifest(CATALOG)}
    wanted = {doc["image_url"] for doc in emit.iter_flat(CATALOG)}
    assert wanted == hosted, "a record URL with no manifest row is a dead link"


def test_the_nested_shape_carries_the_same_urls_as_the_flat_one():
    flat = {doc["sku"]: doc["image_url"] for doc in emit.iter_flat(CATALOG)}
    for doc in emit.iter_nested(CATALOG):
        for variant in doc["variants"]:
            assert variant["image_url"] == flat[variant["sku"]]


def test_a_malformed_image_id_is_refused():
    from synthetic_ecommerce_data.domains.industrial import taxonomy

    for bad in ("end_mill_square", "", "/", "end_mill_square/X", "a/b/c", "x/y/z/w"):
        with pytest.raises(taxonomy.ImageIdError):
            emit.image_path(bad)


def test_a_sku_pointing_at_another_skus_drawing_is_refused():
    import dataclasses

    line = next(line for line in CATALOG.lines if len(line.children) >= 2)
    first, second, *rest = line.children
    swapped = dataclasses.replace(first, image_id=second.image_id)
    broken = dataclasses.replace(
        CATALOG, lines=(dataclasses.replace(line, children=(swapped, second, *rest)),)
    )
    with pytest.raises(emit.UnresolvedImageError):
        list(emit.iter_flat(broken))
    with pytest.raises(emit.UnresolvedImageError):
        list(emit.iter_image_manifest(broken))
