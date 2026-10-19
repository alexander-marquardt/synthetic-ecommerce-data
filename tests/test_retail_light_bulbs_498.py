"""Light bulbs and one color temperature key across lighting (gen#498).

A search for *soft white* has to find 3000K bulbs, *warm white* 2700K, *cool white* 4000K and
*daylight* 6500K: the names printed on a bulb box. So the catalog holds LED bulbs in every
fitting (E27, E14, GU10, B22), each sold in all four temperatures with the box name in the
title, and one fact has one key: ``color_temperature``, name "Color temperature", unit KEL, on
every light that states it. A tunable lamp carries its range as the entries of its two ends
under that one key, not as a second "Minimum color temperature" key.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decoy_rows  # noqa: E402
import export  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402

from synthetic_ecommerce_data.core.letter_case import sentence_case  # noqa: E402
from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

#: kelvin -> the name printed on a bulb box for it.
BOX = {2700: "Warm White", 3000: "Soft White", 4000: "Cool White", 6500: "Daylight"}
FITTINGS = ("E27", "E14", "GU10", "B22")
KEY = "color_temperature"


@pytest.fixture(scope="module")
def lighting() -> list[dict]:
    """Every Home > Lighting template as the standard document a consumer reads."""
    recs = [r for r in scale.templates() if list(r["category_path"][:2]) == ["Home", "Lighting"]]
    return [export.standard_document(r) for r in recs]


@pytest.fixture(scope="module")
def bulbs(lighting: list[dict]) -> list[dict]:
    return [d for d in lighting if d["product_type"] == "Light Bulb"]


def _entries(doc: dict, key: str) -> list[dict]:
    return [e for e in doc["attributes"] if e["key"] == key]


def _value(doc: dict, key: str) -> str:
    (entry,) = _entries(doc, key)
    return entry["value"]


def test_a_light_bulb_type_is_registered_under_home_lighting(bulbs: list[dict]) -> None:
    assert "light_bulb" in type_registry.specs()
    assert bulbs
    published = [sentence_case(n) for n in ("Home", "Lighting", "Light Bulbs")]  # gen#499
    assert all(d["category_path"] == published for d in bulbs)


def test_bulbs_exist_in_every_fitting_at_every_temperature(bulbs: list[dict]) -> None:
    held = {(_value(d, "bulb_fitting"), _value(d, KEY)) for d in bulbs}
    want = {(f, str(k)) for f in FITTINGS for k in BOX}
    assert want <= held, sorted(want - held)


def test_each_fitting_is_sold_in_a_few_wattage_equivalents(bulbs: list[dict]) -> None:
    for fitting in FITTINGS:
        of_fitting = [d for d in bulbs if _value(d, "bulb_fitting") == fitting]
        watts = {_value(d, "equivalent_wattage") for d in of_fitting}
        assert len(watts) >= 2, (fitting, watts)


def test_a_bulb_title_carries_the_box_name_and_the_kelvin_it_states(bulbs: list[dict]) -> None:
    assert bulbs
    for d in bulbs:
        kelvin = int(_value(d, KEY))
        assert kelvin in BOX, d["product_id"]
        assert f"{BOX[kelvin]} {kelvin}K" in d["title"], d["title"]
        assert _value(d, "bulb_fitting") in d["title"], d["title"]
        for other, name in BOX.items():
            if other != kelvin:
                assert name not in d["title"], (d["title"], name)


def test_every_lighting_temperature_is_the_one_kelvin_key(lighting: list[dict]) -> None:
    seen = 0
    for d in lighting:
        assert check_catalog([d]) == [], d["product_id"]
        for entry in d["attributes"]:
            if "color temperature" in entry["name"].lower() or entry["key"].startswith(KEY):
                seen += 1
                assert (entry["key"], entry["name"]) == (KEY, "Color temperature"), entry
                assert entry["unit_code"] == "KEL", (d["product_id"], entry)
                assert entry["value"].isdigit(), (d["product_id"], entry)
                assert entry["value_canonical"] == float(entry["value"]), entry
    assert seen


def test_a_tunable_lamp_states_its_range_as_its_two_ends_under_the_one_key(
    lighting: list[dict],
) -> None:
    ends = {}
    for d in lighting:
        values = sorted(int(e["value"]) for e in _entries(d, KEY))
        if d["product_type"] == "Desk Lamp":
            ends[d["product_id"]] = values
    assert ends["BRD-LTDADJ"] == [2700, 6500]
    assert ends["BRD-LTDWCP"] == [2700, 6500]
    assert ends["BRD-LTDGNK"] == [3000]
    assert ends["BRD-LTDCLP"] == [5000]


def test_lighting_adds_no_second_temperature_key_anywhere_in_the_catalog() -> None:
    names = {
        e["key"]
        for r in scale.templates()
        for e in export.standard_document(r)["attributes"]
        if "color" in e["key"] and "temperature" in e["key"]
    }
    assert names == {KEY}, names


def test_a_light_states_a_temperature_only_where_the_light_source_comes_with_it(
    lighting: list[dict],
) -> None:
    """Maintainer rule (10-18): a bulb or an Integrated LED lamp carries color_temperature; a
    fitting that takes a replaceable bulb (E27, E14, GU10, B22) does not."""
    integrated = 0
    for d in lighting:
        has_temp = bool(_entries(d, KEY))
        fitting = [e["value"] for e in _entries(d, "bulb_fitting")]
        if d["product_type"] == "Light Bulb":
            assert has_temp, d["product_id"]
        elif fitting and fitting != ["Integrated LED"]:
            assert not has_temp, (d["product_id"], fitting)
        elif fitting:
            integrated += 1
            assert has_temp, d["product_id"]
    assert integrated


def _decoys(box: str) -> list:
    return [d for d in decoy_rows.TABLE if d.query == box.lower() and not d.true_hit]


@pytest.mark.parametrize("box", sorted(BOX.values()))
def test_each_box_name_has_at_least_three_decoys_that_are_not_lighting(box: str) -> None:
    rows = _decoys(box)
    assert len(rows) >= 3, (box, len(rows))
    by_id = {r["product_id"]: r for r in scale.templates()}
    for d in rows:
        doc = by_id[f"PLT-D{d.code}"]
        assert box.lower() in d.title.lower(), d.title
        assert list(doc["category_path"][:2]) != ["Home", "Lighting"], d.title
        assert doc["product_type"] != "Light Bulb", d.title
        assert not any(e["key"] == KEY for e in doc["attributes"]), d.title
