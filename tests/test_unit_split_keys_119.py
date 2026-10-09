"""One unit per key for the diameter keys the label ruling split (#118, review of #119)."""

from __future__ import annotations

import json
from dataclasses import replace

import type_gates
from synthetic_ecommerce_data.core.model import Attribute, length_attribute
from synthetic_ecommerce_data.domains.industrial.generate import _unit_key


def test_dowel_pins_publish_each_unit_under_its_own_key():
    units: dict[str, set[str]] = {}
    for line in type_gates.default_records("dowel_pins"):
        for a in json.loads(line)["attributes"]:
            if a["key"].startswith("dowel_dia"):
                units.setdefault(a["key"], set()).add(a["unit_code"])
    assert units == {"dowel_dia": {"INH"}, "dowel_dia_mm": {"MMT"}}


def test_a_restated_diameter_takes_the_key_of_its_unit():
    inches = length_attribute("Diameter", '4-1/2"')
    assert _unit_key(inches, "mm") == "diameter_mm"
    assert _unit_key(replace(inches, key="diameter_mm"), "in") == "diameter"
    dowel = length_attribute("Dowel Dia.", '1/4"')
    assert _unit_key(dowel, "mm") == "dowel_dia_mm"


def test_any_other_key_travels_with_the_value():
    assert _unit_key(length_attribute("Length", '2"'), "mm") is None
    assert _unit_key(Attribute(name="Size", value="1", key="size"), "mm") == "size"
