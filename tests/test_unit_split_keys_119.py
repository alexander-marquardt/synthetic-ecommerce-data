"""One unit per key for the diameter keys the label ruling split (#118, review of #119)."""

from __future__ import annotations

import json

import type_gates
from synthetic_ecommerce_data.domains.industrial.generate import UNIT_SPLIT_KEYS


def test_dowel_pins_publish_each_unit_under_its_own_label_and_key():
    units: dict[tuple[str, str], set[str]] = {}
    for line in type_gates.default_records("dowel_pins"):
        for a in json.loads(line)["attributes"]:
            if a["key"].startswith("dowel_dia"):
                units.setdefault((a["name"], a["key"]), set()).add(a["unit_code"])
    assert units == {
        ("Dowel dia. (in)", "dowel_dia_in"): {"INH"},
        ("Dowel dia. (mm)", "dowel_dia_mm"): {"MMT"},
    }


def test_the_unit_mixing_defect_leaves_the_unit_split_keys_alone():
    assert {"diameter", "dowel_dia_in", "dowel_dia_mm"} <= UNIT_SPLIT_KEYS
