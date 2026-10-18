"""One concept, one attribute: the retail document's clean-up (gen#497).

The first block feeds :func:`attribute_cleanup.clean` and the cross-type name guard documents
broken on purpose; the second reads the shipped retail build (every template, nested and flat).
"""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path
from typing import Any

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import attribute_cleanup  # noqa: E402
import name_guard  # noqa: E402
import scale  # noqa: E402

CEILING = 10_000_000  # more SKUs than the templates reach, so ``scale.build`` runs to its ceiling

#: Keys the published retail document does not carry: they repeat another field or are
#: back-office (``brand_owner`` is a document field, ``pack_size`` is restated by the net content).
REMOVED = {"storage_type", "tracker_type", "brand_owner", "pack_size"}
#: Keys merged into another (old key -> the key that holds the concept now).
MERGED_AWAY = {
    "fill": "filling", "seats": "seat_count", "max_weight_kg": "max_load_kg",
    "voltage_v": "battery_voltage", "power": "power_source", "fragrance": "scent",
    "range": "line", "suit_set": "line", "pocket": "pockets", "arm": "arm_style",
    "blade_size": "blade_span", "finished_size": "dimensions", "charms": "charm_count",
    "drop": "heel_drop", "number_of_pieces": "piece_count", "items": "piece_count",
    "contents": "piece_count", "skirt_length": "garment_length", "inside_leg": "leg_length",
    "fit_length": "leg_length", "country": "origin", "strap": "strap_material",
}  # fmt: skip


def _e(key: str, name: str, value: Any) -> dict[str, Any]:
    return {"key": key, "name": name, "value": value}


def _clean(entries: list[dict[str, Any]], product_type: str = "Thing") -> list[tuple[str, Any]]:
    return [(e["key"], e["value"]) for e in attribute_cleanup.clean(entries, product_type)]


def test_a_removed_key_is_dropped() -> None:
    kept = _clean([_e("storage_type", "Storage type", "Storage Box"), _e("color", "Color", "Red")])
    assert kept == [("color", "Red")]


def test_a_sub_kind_key_folds_into_style_and_a_named_exception_does_not() -> None:
    got = _clean([_e("kettle_type", "Kettle type", "Travel"), _e("bra_shape", "Bra shape", "Plunge")])
    assert got == [("style", "Travel"), ("bra_shape", "Plunge")]


def test_a_petite_leg_is_a_short_leg_and_the_key_is_one() -> None:
    got = _clean([_e("inside_leg", "Inside leg", "Short/Petite")], "Trousers")
    assert got == [("leg_length", "Short")]
    assert _clean([_e("length", "Length", "Petite")], "Jeans") == [("leg_length", "Short")]
    assert _clean([_e("length", "Length", "Knee")], "Slip") == [("garment_length", "Knee")]


def test_strap_splits_into_material_and_form() -> None:
    assert _clean([_e("strap", "Strap", "Leather")]) == [("strap_material", "Leather")]
    assert _clean([_e("strap", "Strap", "Adjustable")]) == [("strap_style", "Adjustable")]


def test_a_lampshade_and_a_toy_state_material_not_fabric() -> None:
    assert _clean([_e("fabric", "Fabric", "Silk")], "Lampshade") == [("shade_material", "Silk")]
    assert _clean([_e("fabric", "Fabric", "Plush")], "Soft Toy") == [("material", "Plush")]
    assert _clean([_e("fabric", "Fabric", "Cotton")], "Shirt") == [("fabric", "Cotton")]


def test_origin_is_one_key_with_place_names_most_specific_first() -> None:
    got = _clean([_e("origin", "Origin", "Rioja"), _e("country", "Country", "Spain")])
    assert got == [("origin", "Rioja"), ("origin", "Spain")]
    assert _clean([_e("origin", "Origin", "Croatian")]) == [("origin", "Croatia")]
    assert _clean([_e("origin", "Origin", "Sicilian")]) == [("origin", "Sicily"), ("origin", "Italy")]


def test_a_boolean_is_emitted_only_when_true_and_as_yes() -> None:
    got = _clean([_e("pockets", "Pockets", "No"), _e("extending", "Extending", "yes")])
    assert got == [("extending", "Yes")]


def test_a_unit_leaves_the_value() -> None:
    (entry,) = attribute_cleanup.clean([_e("drop", "Heel drop", "8mm")], "Running Shoes")
    assert (entry["key"], entry["name"]) == ("heel_drop", "Heel drop")
    assert entry["value"] != "8mm"
    assert entry.get("unit_code") == "MMT"


def test_one_spelling_per_value() -> None:
    assert _clean([_e("fill", "Fill", "Hollow Fibre")]) == [("filling", "Hollowfibre")]
    assert _clean([_e("power", "Power", "Battery")]) == [("power_source", "Battery-powered")]


def test_a_key_with_two_names_and_a_name_on_two_keys_are_findings() -> None:
    docs = [
        {"attributes": [_e("a", "Alpha", 1)], "variants": [{"attributes": [_e("a", "Other", 1)]}]},
        {"attributes": [_e("b", "Beta", 1), _e("c", "Beta", 2)], "variants": []},
    ]
    assert name_guard.catalogue_name_findings(docs) == [
        "key 'a' has names ['Alpha', 'Other']",
        "name 'Beta' is held by keys ['b', 'c']",
    ]


@cache
def _docs() -> tuple[dict[str, Any], ...]:
    return tuple(scale.documents(scale.build(CEILING)))


def _keys(docs: Any) -> set[str]:
    return {
        e["key"]
        for d in docs
        for e in [*d["attributes"], *(a for v in d["variants"] for a in v["attributes"])]
    }


def test_the_shipped_build_has_no_removed_or_merged_away_key() -> None:
    present = _keys(_docs())
    assert present & REMOVED == set()
    assert present & set(MERGED_AWAY) == set()
    assert present & attribute_cleanup.STYLE_KEYS == set()


def test_one_key_has_one_name_and_one_name_one_key_catalogue_wide() -> None:
    assert name_guard.catalogue_name_findings(_docs()) == []
    assert name_guard.catalogue_name_findings(scale.flat(list(_docs()))) == []


def test_brand_owner_is_a_document_field_for_ranking() -> None:
    assert {d["brand_owner"] for d in _docs() if "brand_owner" in d} == {"own", "third_party"}


def _values(key: str) -> set[Any]:
    return {
        e["value"]
        for d in _docs()
        for e in [*d["attributes"], *(a for v in d["variants"] for a in v["attributes"])]
        if e["key"] == key
    }


def test_no_leg_or_garment_length_says_petite() -> None:
    assert not {"Petite", "Short/Petite"} & (_values("leg_length") | _values("garment_length"))
    assert _values("size_range") == {"Petite", "Regular", "Tall"}


def test_a_wine_names_its_region_before_its_country() -> None:
    riojas = [d for d in _docs() if "Rioja" in d["title"]]
    assert riojas
    for d in riojas:
        assert [e["value"] for e in d["attributes"] if e["key"] == "origin"] == ["Rioja", "Spain"]
    assert not {"Croatian", "Italian", "Spanish", "Greek"} & _values("origin")


def test_booleans_are_true_and_yes_everywhere() -> None:
    bad = {"No", "no", "yes", "true", "false"} & {
        v for d in _docs()
        for v in [e["value"] for e in [*d["attributes"], *(a for x in d["variants"] for a in x["attributes"])]]
        if isinstance(v, str)
    }
    assert bad == set()
