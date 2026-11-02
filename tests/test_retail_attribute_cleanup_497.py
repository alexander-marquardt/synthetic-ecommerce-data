"""The retail attribute clean-up of #497, first slice: no published attribute restates the
product type.

``attribute_cleanup.clean`` runs inside ``export._product_attributes`` and ``export._variant``,
so the guards read the documents the scaler builds (every template: ``build(10**6)`` is
past the ceiling), not the helper alone.
"""

from __future__ import annotations

from functools import cache
from typing import Any

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    attribute_cleanup,
    scale,
)


def _e(key: str, value: Any) -> dict[str, Any]:
    return {"key": key, "name": key.title(), "value": value}


@cache
def _docs() -> tuple[dict[str, Any], ...]:
    return tuple(scale.documents(ceiling_build()))


def _entries(doc: dict[str, Any]):
    yield from doc["attributes"]
    for variant in doc["variants"]:
        yield from variant["attributes"]


def test_a_key_that_restates_the_type_is_dropped_and_a_real_sub_kind_stays() -> None:
    got = attribute_cleanup.clean(
        [
            _e("storage_type", "Storage Box"),
            _e("type", "Set Screw"),
            _e("storage_type", "Underbed"),
            _e("type", "Deep Groove"),
            _e("color", "Storage Box"),
        ],
        "Storage Box",
    )
    assert [(e["key"], e["value"]) for e in got] == [
        ("type", "Set Screw"),
        ("storage_type", "Underbed"),
        ("type", "Deep Groove"),
        ("color", "Storage Box"),
    ]
    band = attribute_cleanup.clean([_e("tracker_type", "Fitness band")], "Fitness Band")
    assert band == []


def test_a_type_equal_to_the_product_type_is_dropped_whatever_its_case() -> None:
    kept = attribute_cleanup.clean([_e("type", "set screw"), _e("type", "Socket")], "Set Screw")
    assert [e["value"] for e in kept] == ["Socket"]


def test_no_published_attribute_restates_its_product_type() -> None:
    restating = {
        (doc["product_type"], e["key"], e["value"])
        for doc in _docs()
        for e in _entries(doc)
        if e["key"] in {"storage_type", "tracker_type", "type"}
        and str(e["value"]).casefold() == doc["product_type"].casefold()
    }
    assert restating == set()


def test_the_real_sub_kinds_of_a_removed_key_stay_published() -> None:
    """A storage box's Underbed and a nursery storage's Basket say something the type does
    not, so their ``storage_type`` stays; the Fitness Band loses its ``tracker_type`` whole."""
    seen: dict[tuple[str, str], set[str]] = {}
    for doc in _docs():
        for e in _entries(doc):
            if e["key"] in {"storage_type", "tracker_type"}:
                seen.setdefault((doc["product_type"], e["key"]), set()).add(e["value"])
    assert "Underbed" in seen[("Storage Box", "storage_type")]
    assert {"Basket", "Cube", "Hanging Organizer"} <= seen[("Nursery Storage", "storage_type")]
    assert ("Fitness Band", "tracker_type") not in seen
    assert all(
        value.casefold() != ptype.casefold()
        for (ptype, _), values in seen.items()
        for value in values
    )


#: Second slice: an authored key -> the (key, display name) it is published under.
MERGED = {
    "fill": ("filling", "Filling"),
    "seats": ("seat_count", "Seat count"),
    "max_weight_kg": ("max_load_kg", "Maximum load"),
    "voltage_v": ("battery_voltage", "Battery voltage"),
    "power": ("power_source", "Power source"),
    "range": ("line", "Range"),
    "suit_set": ("line", "Range"),
    "pocket": ("pockets", "Pockets"),
    "arm": ("arm_style", "Arm style"),
    "blade_size": ("blade_span", "Blade span"),
    "finished_size": ("dimensions", "Dimensions"),
    "charms": ("charm_count", "Charm count"),
    "drop": ("heel_drop", "Heel drop"),
}


def test_a_same_concept_key_is_published_under_its_one_key_and_name() -> None:
    got = attribute_cleanup.clean([_e(old, "1") for old in MERGED], "Thing")
    assert [(e["key"], e["name"]) for e in got] == list(dict.fromkeys(MERGED.values()))


def test_a_test_reads_an_authored_key_under_the_key_it_is_published_as() -> None:
    assert {old: attribute_cleanup.published(old) for old in MERGED} == {
        old: key for old, (key, _) in MERGED.items()
    }
    assert attribute_cleanup.published("color") == "color"


def test_a_merged_entry_that_repeats_its_target_is_published_once() -> None:
    got = attribute_cleanup.clean(
        [_e("seat_count", "4"), _e("seats", "4"), _e("seats", "6")], "Garden Furniture Set"
    )
    assert [(e["key"], e["value"]) for e in got] == [("seat_count", "4"), ("seat_count", "6")]


def test_no_published_document_carries_a_merged_away_key() -> None:
    left = {e["key"] for doc in _docs() for e in _entries(doc)} & set(MERGED)
    assert left == set()


def test_each_merged_key_has_one_display_name_on_every_document() -> None:
    want = {key: name for key, name in MERGED.values()}
    names: dict[str, set[str]] = {}
    for doc in _docs():
        for e in _entries(doc):
            if e["key"] in want:
                names.setdefault(e["key"], set()).add(e["name"])
    assert {k: v for k, v in names.items() if v != {want[k]}} == {}
    assert set(names) == set(want)


def test_battery_powered_has_one_spelling() -> None:
    spelt = {e["value"] for doc in _docs() for e in _entries(doc) if e["key"] == "power_source"}
    assert "Battery-Powered" in spelt
    assert "Battery" not in spelt


def test_a_heel_drop_holds_its_millimetres_in_the_unit_field() -> None:
    drops = [e for doc in _docs() for e in _entries(doc) if e["key"] == "heel_drop"]
    assert drops
    assert {(e["value"], e.get("unit_code")) for e in drops} <= {("0", "MMT"), ("8", "MMT")}
