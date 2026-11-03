"""The retail attribute clean-up of #497, first slice: no published attribute restates the
product type.

``attribute_cleanup.clean`` runs inside ``export._product_attributes`` and ``export._variant``,
so the guards read the documents the scaler builds (every template: ``build(10**6)`` is
past the ceiling), not the helper alone.
"""

from __future__ import annotations

import inspect
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


# Third slice: where a product comes from is one multi-valued key, every level that applies,
# most specific first, each value a place name (the 10-18 ruling, "Origin").


def _origins(doc: dict[str, Any]) -> list[Any]:
    return [e["value"] for e in _entries(doc) if e["key"] == "origin"]


def _clean(entries: list[dict[str, Any]], product_type: str, title: str) -> list[dict[str, Any]]:
    # The origin rule reads the product's title (a region it names goes first), so clean takes it.
    assert "title" in inspect.signature(attribute_cleanup.clean).parameters
    return attribute_cleanup.clean(entries, product_type, title=title)


def test_country_and_origin_are_published_as_one_origin_key() -> None:
    got = _clean([_e("country", "Spain"), _e("origin", "Croatian")], "Thing", "A Thing")
    assert [(e["key"], e["name"], e["value"]) for e in got] == [
        ("origin", "Origin", "Spain"),
        ("origin", "Origin", "Croatia"),
    ]
    assert attribute_cleanup.published("country") == "origin"


def test_a_place_within_a_country_is_published_with_its_country_after_it() -> None:
    got = _clean([_e("origin", "Sicilian")], "Olive Oil", "Olive Oil")
    assert [e["value"] for e in got] == ["Sicily", "Italy"]
    got = _clean([_e("country", "Scotland")], "Whisky", "Scotch Whisky")
    assert [e["value"] for e in got] == ["Scotland", "United Kingdom"]


def test_a_region_the_title_names_goes_first_only_when_it_lies_in_the_country() -> None:
    rioja = _clean([_e("country", "Spain")], "Wine", "Rioja Reserva")
    assert [e["value"] for e in rioja] == ["Rioja", "Spain"]
    elsewhere = _clean([_e("country", "Chile")], "Wine", "Rioja Style Red")
    assert [e["value"] for e in elsewhere] == ["Chile"]


def test_no_published_document_carries_country() -> None:
    assert not any(e["key"] == "country" for doc in _docs() for e in _entries(doc))


def test_every_origin_is_a_place_name_under_one_display_name() -> None:
    entries = [e for doc in _docs() for e in _entries(doc) if e["key"] == "origin"]
    assert {e["name"] for e in entries} == {"Origin"}
    assert {"Croatian", "Sicilian", "Sumatran", "Italian"} & {e["value"] for e in entries} == set()
    assert {e["value"] for e in entries} - attribute_cleanup.PLACES == set()


def test_a_drink_carries_its_region_before_its_country() -> None:
    by_title = {doc["title"]: _origins(doc) for doc in _docs() if _origins(doc)}
    assert by_title.get("Yellow Skerry Rioja Reserva") == ["Rioja", "Spain"]
    champagnes = [_origins(doc) for doc in _docs() if doc["product_type"] == "Champagne"]
    assert champagnes and all(o == ["Champagne", "France"] for o in champagnes)
    scotch = [o for t, o in by_title.items() if "Scotch" in t]
    assert scotch and all(o == ["Scotland", "United Kingdom"] for o in scotch)


# Fourth slice: a trouser's leg option is one key, a style length another, and "Petite" is a
# size range, never a length (the 10-18 ruling, "Size range and leg length"; review merge #3).

LEG_LENGTHS = {"Extra Short", "Short", "Regular", "Long", "Extra Long"}


def _clean_on(entries: list[dict[str, Any]], product_type: str) -> list[dict[str, Any]]:
    # A Petite leg puts Petite in the product's size range, so clean knows the product's list.
    assert "on_product" in inspect.signature(attribute_cleanup.clean).parameters
    return attribute_cleanup.clean(entries, product_type, on_product=True)


def test_a_leg_option_is_published_as_one_leg_length_and_petite_is_its_size_range() -> None:
    got = _clean_on([_e("length", "Petite"), _e("length", "Long")], "Jeans")
    assert [(e["key"], e["name"], e["value"]) for e in got] == [
        ("leg_length", "Leg length", "Short"),
        ("size_range", "Size range", "Petite"),
        ("leg_length", "Leg length", "Long"),
    ]
    legs = attribute_cleanup.clean([_e("inside_leg", "Short/Petite")], "Trousers")
    assert [(e["key"], e["value"]) for e in legs] == [("leg_length", "Short")]
    assert attribute_cleanup.published("inside_leg") == "leg_length"
    assert attribute_cleanup.published("length", "Jeans") == "leg_length"


def test_a_style_length_is_published_as_one_garment_length_in_one_spelling() -> None:
    got = attribute_cleanup.clean(
        [_e("length", "Knee"), _e("garment_length", "Knee Length"), _e("length", "Crop")], "Dress"
    )
    assert [(e["key"], e["name"], e["value"]) for e in got] == [
        ("garment_length", "Garment length", "Knee"),
        ("garment_length", "Garment length", "Cropped"),
    ]
    shorts = attribute_cleanup.clean([_e("leg_length", "Mid")], "PE Shorts")
    assert [(e["key"], e["value"]) for e in shorts] == [("garment_length", "Mid Length")]
    assert attribute_cleanup.published("skirt_length") == "garment_length"
    assert attribute_cleanup.published("length", "Dress") == "garment_length"


def test_no_published_document_carries_an_authored_length_key() -> None:
    left = {
        (e["key"], doc["product_type"])
        for doc in _docs()
        for e in _entries(doc)
        if e["key"] in ("inside_leg", "skirt_length")
        or (e["key"] == "length" and doc["product_type"] != "Suit Jacket")
    }
    assert left == set()


def test_every_leg_length_is_a_leg_option_and_petite_is_never_a_length() -> None:
    legs = {e["value"] for doc in _docs() for e in _entries(doc) if e["key"] == "leg_length"}
    assert legs == LEG_LENGTHS
    # A Skirt's ``fit_length`` (Short/Petite, Regular, Long) awaits the maintainer's ruling.
    lengths = {
        e["value"]
        for doc in _docs()
        for e in _entries(doc)
        if e["key"].endswith("length") and e["key"] != "fit_length"
    }
    assert {"Petite", "Short/Petite"} & lengths == set()


def test_a_jeans_style_sold_in_a_petite_leg_is_in_the_petite_size_range() -> None:
    jeans = [doc for doc in _docs() if doc["product_type"] == "Jeans"]
    petite = [doc for doc in jeans if any(e["key"] == "size_range" and e["value"] == "Petite"
                                          for e in doc["attributes"])]  # fmt: skip
    assert len(petite) >= 300
    for doc in jeans:
        for variant in doc["variants"]:
            assert not any(e["key"] == "size_range" for e in variant["attributes"])


def test_every_style_length_is_one_garment_length_under_one_name_and_spelling() -> None:
    entries = [e for doc in _docs() for e in _entries(doc) if e["key"] == "garment_length"]
    assert {e["name"] for e in entries} == {"Garment length"}
    values = {e["value"] for e in entries}
    assert {"Mini", "Midi", "Maxi", "Knee", "Cropped", "Mid Length", "Full Length"} <= values
    assert {"Knee Length", "Mid", "Full", "Crop", "Petite", "Short/Petite"} & values == set()


def test_every_size_range_is_in_one_casing() -> None:
    ranges = {e["value"] for doc in _docs() for e in _entries(doc) if e["key"] == "size_range"}
    assert ranges and ranges <= {"Petite", "Regular", "Tall", "Plus"}
