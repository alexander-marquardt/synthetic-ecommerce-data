"""One attribute key per concept in the retail export (gen#227).

A height in centimetres was ``item_height`` on the furniture and ``height`` on a table lamp and an
olive tree; a footstool's storage was ``storage_compartment`` and a coffee table's
``storage_feature``. A range or facet filter on one key missed the other's products.
``key_guard`` names each concept, its one key and the keys that are another concept by design. The
first block feeds it catalogs broken on purpose (the mutants), the second runs it over the
authored styles, and the third pins the products the issue named.
"""

from __future__ import annotations

import json
import sys
from functools import cache
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import key_guard  # noqa: E402
import scale  # noqa: E402


def _entry(key: str, text: bool = False) -> dict[str, str]:
    """A measured entry (centimetres), or a text one (no ``unit_code``)."""
    entry = {"key": key, "name": key.title(), "value": "1"}
    return entry if text else {**entry, "unit_code": "CMT", "value_canonical": 10.0}


def _doc(*keys: str, variant: tuple[str, ...] = (), text: tuple[str, ...] = ()) -> dict[str, Any]:
    return {
        "product_id": "PLT-X",
        "attributes": [*(_entry(k) for k in keys), *(_entry(k, text=True) for k in text)],
        "variants": [{"attributes": [_entry(k) for k in variant]}],
    }


WHOLE = _doc("item_height", "storage_feature")


def test_a_catalog_with_each_concept_under_its_winner_has_no_finding() -> None:
    assert key_guard.concept_findings([WHOLE]) == []
    assert key_guard.stem_findings([WHOLE]) == []


def test_a_second_height_key_is_a_finding() -> None:
    found = key_guard.concept_findings([WHOLE, _doc("height")])
    assert found == ["item height: carried under ['height'] as well as 'item_height'"]


def test_a_second_height_key_on_a_variant_is_a_finding() -> None:
    found = key_guard.concept_findings([WHOLE, _doc("size", variant=("height_cm",))])
    assert found == ["item height: carried under ['height_cm'] as well as 'item_height'"]


def test_a_second_storage_key_is_a_finding() -> None:
    found = key_guard.concept_findings([WHOLE, _doc("storage_compartment")])
    assert found == [
        "furniture storage: carried under ['storage_compartment'] as well as 'storage_feature'"
    ]


def test_a_declared_exception_is_not_a_finding() -> None:
    other = _doc(
        "heel_height", "platform_height", "min_height", "max_height", "storage", "storage_type"
    )
    assert key_guard.concept_findings([WHOLE, other]) == []


def test_a_concept_no_document_carries_under_its_winner_is_a_finding() -> None:
    found = key_guard.concept_findings([_doc("storage_feature")])
    assert found == ["item height: no document carries 'item_height'"]


def test_two_keys_with_one_stem_are_a_finding() -> None:
    assert key_guard.stem_findings([_doc("item_height", "height")]) == [
        "'height' is ['height', 'item_height']"
    ]
    assert key_guard.stem_findings([_doc("weight", "weight_kg")]) == [
        "'weight' is ['weight', 'weight_kg']"
    ]


def test_a_text_key_that_shares_a_stem_with_a_measured_one_is_not_a_finding() -> None:
    """A garment's ``width`` is Standard or Wide, an ``item_width`` is a length."""
    assert key_guard.stem_findings([_doc("item_width", text=("width",))]) == []


def test_the_metric_counts_the_keys_of_each_concept() -> None:
    assert key_guard.keys_per_concept([WHOLE]) == {"item height": 1, "furniture storage": 1}
    two = [WHOLE, _doc("height", "storage_compartment", "heel_height")]
    assert key_guard.keys_per_concept(two) == {"item height": 2, "furniture storage": 2}


@cache
def _docs() -> tuple[dict[str, Any], ...]:
    return tuple(export.standard_document(rec) for rec in scale.templates())


def test_no_concept_of_the_authored_styles_is_carried_by_two_keys() -> None:
    assert key_guard.concept_findings(_docs()) == []


def test_the_metric_is_one_key_per_concept_over_the_authored_styles() -> None:
    assert key_guard.keys_per_concept(_docs()) == {"item height": 1, "furniture storage": 1}


def test_no_two_keys_of_the_authored_styles_share_a_stem() -> None:
    assert key_guard.stem_findings(_docs()) == []


def _entries(leaf: str) -> list[dict[str, Any]]:
    docs = [d for d in _docs() if d["category_leaf"] == leaf]
    assert docs, leaf
    return [e for d in docs for row in (d, *d["variants"]) for e in row["attributes"]]


@pytest.mark.parametrize(
    "leaf", ["Table Lamps", "Floor Lamps", "Gift Plants", "Dolls", "Real Christmas Trees"]
)
def test_a_measured_height_is_an_item_height(leaf: str) -> None:
    keys = {e["key"] for e in _entries(leaf)}
    assert "item_height" in keys, keys
    assert not keys & {"height", "height_cm"}, keys


@pytest.mark.parametrize("leaf", ["Table Lamps", "Floor Lamps", "Gift Plants", "Dolls"])
def test_an_item_height_in_centimetres_is_a_length_in_millimetres(leaf: str) -> None:
    heights = [e for e in _entries(leaf) if e["key"] == "item_height"]
    assert heights
    assert {e["unit_code"] for e in heights} == {"CMT"}
    assert all(e["value_canonical"] == float(e["value"]) * 10 for e in heights)


def test_a_tree_in_feet_keeps_its_unit_under_item_height() -> None:
    heights = [e for e in _entries("Real Christmas Trees") if e["key"] == "item_height"]
    assert {e["unit_code"] for e in heights} == {"FOT"}
    assert all(e["name"] == "Item height" for e in heights)


@pytest.mark.parametrize(
    ("leaf", "values"),
    [
        ("Coffee Tables", {"None", "Lift-Top", "Shelf", "Drawer"}),
        ("Footstools", {"None", "Lift-Top"}),
    ],
)
def test_storage_is_one_kind_where_none_means_no_storage(leaf: str, values: set[str]) -> None:
    entries = [e for e in _entries(leaf) if e["key"] in ("storage_feature", "storage_compartment")]
    assert {e["key"] for e in entries} == {"storage_feature"}
    assert {e["value"] for e in entries} == values
    assert {e["name"] for e in entries} == {"Storage feature"}


@pytest.mark.parametrize("name", ["samples.ndjson", "samples4.ndjson"])
def test_no_committed_sample_carries_a_second_key_for_a_concept(name: str) -> None:
    """The sneak-peek samples hold styles the templates do not (a round-2 table lamp)."""
    records = [json.loads(line) for line in (RETAIL / name).read_text().splitlines()]
    assert records
    found = key_guard.concept_findings(records)
    assert [f for f in found if "carried under" in f] == []
    assert key_guard.stem_findings(records) == []


@pytest.mark.parametrize("name", ["samples.ndjson", "samples4.ndjson"])
def test_a_committed_samples_item_height_in_centimetres_is_canonical_in_millimetres(
    name: str,
) -> None:
    """The table lamp of the round-2 samples carried its 46 cm as 46.0 mm."""
    records = [json.loads(line) for line in (RETAIL / name).read_text().splitlines()]
    heights = [
        e
        for r in records
        for e in r["attributes"]
        if e["key"] == "item_height" and e.get("unit_code") == "CMT"
    ]
    assert heights
    assert all(e["value_canonical"] == float(e["value"]) * 10 for e in heights), heights
