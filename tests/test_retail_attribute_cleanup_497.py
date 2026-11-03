"""The retail attribute clean-up of #497, first slice: no published attribute restates the
product type.

``attribute_cleanup.clean`` runs inside ``export._product_attributes`` and ``export._variant``,
so the guards read the documents the scaler builds (every template: ``build(10**6)`` is
past the ceiling), not the helper alone.
"""

from __future__ import annotations

import inspect
import re
from functools import cache
from typing import Any

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    attribute_cleanup,
    name_guard,
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
        ("style", "Underbed"),
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
        if e["key"] in {"style", "type"}
        and str(e["value"]).casefold() == doc["product_type"].casefold()
    }
    assert restating == set()


def test_the_real_sub_kinds_of_a_removed_key_stay_published() -> None:
    """A storage box's Underbed and a nursery storage's Basket say something the type does
    not, so they stay (as its ``style``, the 10-18 fold); the Fitness Band's ``tracker_type``
    is dropped whole."""
    seen: dict[str, set[str]] = {}
    for doc in _docs():
        seen.setdefault(doc["product_type"], set()).update(_published_of(doc, "style"))
    assert "Underbed" in seen["Storage Box"]
    assert {"Basket", "Cube", "Hanging Organizer"} <= seen["Nursery Storage"]
    assert "Fitness band" not in seen.get("Fitness Band", set())


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


# Fifth slice: an authored key that holds two kinds of value is split, one kind per key (the
# 10-18 ruling, "Split"; review #6, #28, #29).

STRAP_MATERIALS = {"Leather", "Fabric", "Stainless Steel Mesh", "Silicone"}
STRAP_FORMS = {"Adjustable", "Thin", "Chain", "Back strap", "None"}
NECKS = {"Crew Neck", "V Neck", "Roll Neck", "Boat Neck", "Cowl Neck", "Turtle Neck"}
NECKLINES = {
    "Crew", "V-neck", "Round", "Boat", "Slash", "Square", "High", "Collared", "Cowl", "Halter",
    "Tie-neck",
}  # fmt: skip


def _published_of(doc: dict[str, Any], key: str) -> list[Any]:
    return [e["value"] for e in _entries(doc) if e["key"] == key]


def test_a_strap_is_published_as_its_material_or_its_form_by_type() -> None:
    watch = attribute_cleanup.clean([_e("strap", "Leather")], "Analog Watch")
    slip = attribute_cleanup.clean([_e("strap", "Adjustable")], "Slip")
    assert [(e["key"], e["name"]) for e in watch] == [("strap_material", "Strap material")]
    assert [(e["key"], e["name"]) for e in slip] == [("strap_style", "Strap style")]
    assert attribute_cleanup.published("strap", "Fitness Band") == "strap_material"
    assert attribute_cleanup.published("strap", "Handbag") == "strap_style"


def test_no_published_strap_mixes_a_material_with_a_form() -> None:
    material = {v for doc in _docs() for v in _published_of(doc, "strap_material")}
    style = {v for doc in _docs() for v in _published_of(doc, "strap_style")}
    assert not any(_published_of(doc, "strap") for doc in _docs())
    assert material == STRAP_MATERIALS
    assert style and style <= STRAP_FORMS


def test_a_lampshade_and_a_soft_toy_carry_a_material_not_a_fabric() -> None:
    shade = attribute_cleanup.clean([_e("fabric", "Velvet")], "Lampshade")
    toy = attribute_cleanup.clean([_e("fabric", "Plush")], "Soft Toy")
    coat = attribute_cleanup.clean([_e("fabric", "Wool")], "Coat")
    assert [(e["key"], e["name"]) for e in shade] == [("shade_material", "Shade material")]
    assert [(e["key"], e["name"]) for e in toy] == [("material", "Material")]
    assert [e["key"] for e in coat] == ["fabric"]
    left = {
        doc["product_type"]
        for doc in _docs()
        if doc["product_type"] in ("Lampshade", "Soft Toy") and _published_of(doc, "fabric")
    }
    assert left == set()


def test_a_neck_is_a_neckline_and_a_knit_style_keeps_its_construction() -> None:
    got = attribute_cleanup.clean(
        [_e("knit_style", "Crew Neck"), _e("knit_style", "Cable Knit")], "Jumper"
    )
    assert [(e["key"], e["name"], e["value"]) for e in got] == [
        ("neckline", "Neckline", "Crew"),
        ("knit_style", "Knit_Style", "Cable Knit"),
    ]
    roll = attribute_cleanup.clean([_e("knit_style", "Roll Neck")], "Jumper")
    assert [(e["key"], e["value"]) for e in roll] == [("neckline", "High")]


def test_a_neck_in_the_knit_style_gives_way_to_the_authored_neckline() -> None:
    polo = [_e("knit_style", "Crew Neck"), _e("neckline", "collared")]
    for entries in (polo, polo[::-1]):
        got = attribute_cleanup.clean(entries, "Polo Jumper")
        assert [(e["key"], e["value"]) for e in got] == [("neckline", "Collared")]


def test_no_entry_list_carries_two_necklines() -> None:
    lists = [doc["attributes"] for doc in _docs()]
    lists += [variant["attributes"] for doc in _docs() for variant in doc["variants"]]
    twice = [
        [e["value"] for e in entries if e["key"] == "neckline"]
        for entries in lists
        if sum(e["key"] == "neckline" for e in entries) > 1
    ]
    assert twice == []


def test_no_knit_style_names_a_neck_and_every_neckline_is_in_one_casing() -> None:
    knits = {v for doc in _docs() for v in _published_of(doc, "knit_style")}
    assert knits and knits & NECKS == set()
    necks = [e for doc in _docs() for e in _entries(doc) if e["key"] == "neckline"]
    assert {e["name"] for e in necks} == {"Neckline"}
    assert {e["value"] for e in necks} <= NECKLINES
    jumpers = {
        v for doc in _docs() if doc["product_type"] == "Jumper"
        for v in _published_of(doc, "neckline")
    }  # fmt: skip
    assert {"Crew", "V-neck", "High", "Boat", "Cowl"} <= jumpers


def test_a_count_of_items_is_a_piece_count() -> None:
    got = attribute_cleanup.clean(
        [
            _e("contents", "3 items"),
            {"key": "items", "name": "Items", "value": "4", "unit_code": "C62",
             "value_canonical": 4.0},
            _e("contents", "4 Plates, 4 Bowls"),
        ],
        "Gift Set",
    )  # fmt: skip
    assert [(e["key"], e["name"], e["value"], e.get("unit_code")) for e in got] == [
        ("piece_count", "Piece count", "3", "C62"),
        ("piece_count", "Piece count", "4", "C62"),
        ("contents", "Contents", "4 Plates, 4 Bowls", None),
    ]


def test_no_document_carries_items_or_a_counted_contents_and_every_piece_count_is_whole() -> None:
    assert not any(_published_of(doc, "items") for doc in _docs())
    contents = {v for doc in _docs() for v in _published_of(doc, "contents")}
    assert contents and not {v for v in contents if attribute_cleanup.COUNTED.fullmatch(v)}
    pieces = [e for doc in _docs() for e in _entries(doc) if e["key"] == "piece_count"]
    assert {e["name"] for e in pieces} == {"Piece count"}
    assert {(e["unit_code"], e["value"].isdigit()) for e in pieces} == {("C62", True)}
    counted = {doc["product_type"] for doc in _docs() if _published_of(doc, "piece_count")}
    assert {"Gift Hamper", "Gift Set", "Hospital Bag", "Travel Set"} <= counted


#: Review merge #30's one-type sub-kind keys, and the Jelly Shoes' ``jelly_style`` (also shown
#: as "Style"): one concept, published as ``style`` "Style" (the 10-18 ruling, "Style").
SUB_KINDS = {
    "accessory_type", "airer_type", "bag_shape", "bag_style", "band_type", "bbq_kind",
    "bin_type", "bolero_style", "bookcase_style", "bowl_type", "bracelet_type", "chair_style",
    "chest_style", "cutlery_type", "earring_style", "fixture_type", "furniture_kind",
    "glass_type", "heater_type", "jelly_style", "kettle_type", "knife_type", "ladder_kind",
    "laundry_basket_type", "lid_type", "mattress_type", "mirror_type", "module_type", "mop_type",
    "necklace_type", "pan_type",
    "parasol_kind", "pinafore_style", "plate_type", "pump_type", "purse_type", "ring_type",
    "shapewear_type", "shorts_style", "skirt_shape", "skirt_style", "spirit_style",
    "storage_type", "table_type", "tent_type", "toy_type", "tracker_type", "umbrella_type",
    "utensil_type", "watch_type",
}  # fmt: skip


def test_a_sub_kind_key_is_published_as_style() -> None:
    got = attribute_cleanup.clean(
        [_e("bbq_kind", "Kamado"), {"key": "skirt_shape", "name": "Shape", "value": "A-Line"}],
        "BBQ",
    )
    assert [(e["key"], e["name"], e["value"]) for e in got] == [
        ("style", "Style", "Kamado"),
        ("style", "Style", "A-Line"),
    ]
    assert {attribute_cleanup.published(k) for k in SUB_KINDS} == {"style"}


def test_a_sub_kind_that_names_the_product_type_is_dropped() -> None:
    got = attribute_cleanup.clean(
        [_e("toy_type", "Marble Run"), _e("pan_type", "Wok")], "Marble Run"
    )
    assert [(e["key"], e["value"]) for e in got] == [("style", "Wok")]


def test_no_published_document_carries_a_sub_kind_key_and_style_has_one_name() -> None:
    left = {e["key"] for doc in _docs() for e in _entries(doc)} & SUB_KINDS
    assert left == set()
    names = {e["name"] for doc in _docs() for e in _entries(doc) if e["key"] == "style"}
    assert names == {"Style"}


def test_a_folded_sub_kind_is_a_style_value_and_the_named_facets_stay() -> None:
    styles: dict[str, set[str]] = {}
    for doc in _docs():
        styles.setdefault(doc["product_type"], set()).update(_published_of(doc, "style"))
    assert "Kamado" in styles["BBQ"]
    assert "A-Line" in styles["Skirt"]
    assert "Underbed" in styles["Storage Box"]
    assert {"Single Malt", "Blended"} <= styles["Whisky"]
    for kept in ("bra_shape", "knit_style", "back_style"):
        assert any(_published_of(doc, kept) for doc in _docs()), kept


def test_no_style_restates_its_product_type() -> None:
    restating = {
        (doc["product_type"], value)
        for doc in _docs()
        for value in _published_of(doc, "style")
        if str(value).casefold() == doc["product_type"].casefold()
    }
    assert restating == set()
    houses = {v for doc in _docs() if doc["product_type"] == "Dolls' House"
              for v in _published_of(doc, "style")}  # fmt: skip
    assert houses and "Dolls' House" not in houses


def test_a_boolean_is_published_only_when_true_and_always_as_yes() -> None:
    got = attribute_cleanup.clean(
        [_e("waterproof", "No"), _e("online_only", "no"), _e("pet_friendly", "yes"),
         _e("belt", "Yes"), _e("ring_size_uk", "N")],
        "Raincoat",
    )  # fmt: skip
    assert [(e["key"], e["value"]) for e in got] == [
        ("pet_friendly", "Yes"),
        ("belt", "Yes"),
        ("ring_size_uk", "N"),
    ]
    authored = [_e("pocket", "No"), _e("hood", "No"), _e("hood", "Yes"), _e("lined", "false")]
    assert attribute_cleanup.withheld(authored) == {"pockets", "lined"}
    plain = [_e("bolero_style", "Bolero"), _e("hood", "No")]
    assert attribute_cleanup.withheld(plain, "Bolero") == {"style", "hood"}
    values ={e["value"] for doc in _docs() for e in _entries(doc) if isinstance(e["value"], str)}
    assert {v for v in values if v.casefold() in ("no", "false", "yes", "true")} == {"Yes"}


#: A number with a unit written into its text: the unit belongs in the unit field. A ``size``
#: is a SKU option's label ("60 cm" on a Plant), kept as the shopper picks it.
NUMBER_AND_UNIT = re.compile(r"\d[\d,.]*\s*(cm|mm)")


def test_a_unit_written_into_a_value_goes_to_the_unit_field() -> None:
    boots = [e for doc in _docs() if doc["product_type"] == "Knee High Boots"
             for e in _entries(doc) if e["key"] == "calf"]  # fmt: skip
    assert boots and {(e["value"], e.get("unit_code")) for e in boots} == {("36", "CMT")}
    rated = [e for doc in _docs() for e in _entries(doc) if e["key"] == "waterproof_rating"]
    assert rated and {e.get("unit_code") for e in rated} == {"MMT"}
    assert all(e["value"].isdigit() for e in rated)
    written = {
        (e["key"], e["value"])
        for doc in _docs()
        for e in _entries(doc)
        if e["key"] != "size"
        and isinstance(e["value"], str)
        and NUMBER_AND_UNIT.fullmatch(e["value"])
    }
    assert written == set()


def test_a_value_has_one_spelling() -> None:
    fillings = {v for doc in _docs() for v in _published_of(doc, "filling")}
    assert "Hollowfibre" in fillings and "Hollow Fibre" not in fillings
    lines = {v for doc in _docs() for v in _published_of(doc, "line")}
    assert not {v for v in lines if "Stone Ground" in v}


def test_the_catalogue_guard_finds_a_name_on_two_keys_and_a_key_under_two_names() -> None:
    docs = [
        {"product_id": "a", "attributes": [_e("rug_shape", "Round") | {"name": "Shape"}],
         "variants": []},
        {"product_id": "b", "attributes": [_e("shape", "Oval") | {"name": "Shape"}],
         "variants": [{"attributes": [_e("shape", "Oval") | {"name": "Outline"}]}]},
    ]  # fmt: skip
    assert name_guard.catalogue_name_findings(docs) == [
        "key 'shape' is shown as ['Outline', 'Shape']",
        "name 'Shape' names ['rug_shape', 'shape']",
    ]


def test_one_display_name_is_one_key_and_one_key_one_name_catalogue_wide() -> None:
    assert name_guard.catalogue_name_findings(_docs()) == []
    styles: dict[str, set[str]] = {"Bolero": set(), "Step Ladder": set()}
    for doc in _docs():
        if doc["product_type"] in styles:
            styles[doc["product_type"]].update(_published_of(doc, "style"))
    assert "Shrug" in styles["Bolero"] and "Step stool" in styles["Step Ladder"]
    assert "Bolero" not in styles["Bolero"] and "Step ladder" not in styles["Step Ladder"]
