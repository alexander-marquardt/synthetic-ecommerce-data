"""Facts a record states are real, and a brand lists a type one way.

The review of the 100K catalog found invented facts: bearing load ratings a
formula made up, standards drawn from a pool for other parts, finishes and
hardnesses that no maker sells on that material, end mills whose shank is
thinner than their flutes, and titles that dropped the part's key size.
Each rule is checked against tables written out HERE, independently of the
generator's own.
"""

from __future__ import annotations

import collections
import json
import re
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog import emit
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.dimensions import DimensionParseError, parse_length

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"
LBF_PER_KN = 224.809

#: Deep groove ball bearing ratings: (dynamic C kN, static C0 kN, open grease
#: limiting speed rpm) -- SKF's published tables for 60/62/63, distributor
#: listings for the inch R series.
RATINGS = {
    "6000": (4.75, 1.96, 38000), "6001": (5.40, 2.36, 32000), "6002": (5.85, 2.85, 28000),
    "6003": (6.37, 3.25, 24000), "6004": (9.95, 5.00, 20000), "6005": (11.9, 6.55, 18000),
    "6006": (13.8, 8.30, 14000), "6200": (5.40, 2.36, 34000), "6201": (7.28, 3.10, 32000),
    "6202": (8.06, 3.75, 28000), "6203": (9.95, 4.75, 24000), "6204": (13.5, 6.55, 20000),
    "6205": (14.8, 7.80, 18000), "6206": (20.3, 11.2, 15000), "6207": (27.0, 15.3, 13000),
    "6208": (32.5, 19.0, 11000), "6300": (8.52, 3.40, 28000), "6301": (9.95, 4.15, 26000),
    "6302": (11.9, 5.40, 22000), "6303": (14.3, 6.55, 20000), "6304": (16.8, 7.80, 18000),
    "6305": (23.4, 11.6, 16000), "R4": (1.14, 0.46, 48000), "R6": (3.30, 1.40, 36000),
    "R8": (5.07, 2.37, 28000), "R10": (6.23, 3.30, 24000), "R12": (9.36, 4.80, 20000),
}  # fmt: skip
#: A contact seal limits speed to about 70% of the open bearing; a shield does not.
CLOSURE_SPEED = {"Open": 1.0, "Double Shield": 1.0, "Double Seal": 0.70}

#: The standards a record of each type may claim.
MAY_CLAIM = {
    "screw_socket_head": {"ISO 4762", "DIN 912", "ASME B18.3", "ASTM A574", "ASTM F837",
                          "ISO 898-1", "ISO 3506-1"},
    "screw_flat_head": {"ISO 10642", "ASME B18.3", "ISO 898-1", "ISO 3506-1"},
    "screw_button_head": {"ISO 7380-1", "ASME B18.3", "ISO 898-1", "ISO 3506-1"},
    "screw_low_head": {"DIN 7984", "ASME B18.3", "ISO 898-1", "ISO 3506-1"},
    "bolt_hex": {"ASME B18.2.1", "ISO 4014", "ISO 4017", "DIN 933", "ISO 8765", "ISO 8676",
                 "DIN 961", "SAE J429", "ISO 898-1"},
    "nut_hex": {"ISO 4032", "ISO 4035", "ASME B18.2.2", "SAE J995", "ISO 898-2"},
    "washer_flat": {"ISO 7089", "DIN 125-A"},
    "end_mill_square": {"ISO 1641", "DIN 6527", "ANSI B94.19"},
    "end_mill_ball": {"ISO 1641", "DIN 6527", "ANSI B94.19"},
    "drill_jobber": {"DIN 338", "ASME B94.11M"},
    "tap_spiral_point": {"ISO 529", "ASME B94.9"},
    "hex_key": {"ISO 2936", "ASME B18.3"},
    "hammer_ball_pein": {"ASME B107.400"},
    "abrasive_flap_disc": {"EN 13743", "oSa Certified"},
    "wheel_depressed_center": {"ANSI B7.1", "EN 12413", "oSa Certified"},
    "bearing_radial_ball": {"ISO 15", "ISO 492", "ABMA 20"},
    "kit_assortment": set(),
}  # fmt: skip

#: Finishes no maker sells on the material, and hardness scales that cannot be.
NEVER_ON_STAINLESS = {"Zinc Plated", "Zinc Yellow", "Hot Dip Galvanized", "Black Oxide"}
CARBIDE_ONLY_COATINGS = {"nACo"}
NOT_ON_CARBIDE = {"Black Oxide", "Bronze Oxide", "Steam Oxide"}

#: The key dimension every title names, per type.
KEY = {
    "end_mill_square": ("Milling Dia.",), "end_mill_ball": ("Milling Dia.",),
    "drill_jobber": ("Size",), "tap_spiral_point": ("Thread Size",),
    "screw_socket_head": ("Dia./Thread Size",), "screw_flat_head": ("Dia./Thread Size",),
    "screw_button_head": ("Dia./Thread Size",), "screw_low_head": ("Dia./Thread Size",),
    "bolt_hex": ("Dia./Thread Size",), "washer_flat": ("Size",), "nut_hex": ("Thread Size",),
    "hex_key": ("Size",), "bearing_radial_ball": ("Bearing Number", "Bore"),
    "wheel_depressed_center": ("Diameter",), "abrasive_flap_disc": ("Diameter",),
    "hammer_ball_pein": ("Head Weight",), "kit_assortment": ("Number of Pieces",),
}  # fmt: skip


@pytest.fixture(scope="module")
def golden() -> list[dict]:
    return [json.loads(line) for line in (GOLDEN / "flat.jsonl").read_text("utf-8").splitlines()]


@pytest.fixture(scope="module")
def fresh() -> list[dict]:
    return list(emit.iter_flat(generate(GeneratorConfig())))


@pytest.fixture(scope="module", params=["golden", "fresh"])
def docs(request) -> list[dict]:
    return request.getfixturevalue(request.param)


def _values(doc: dict) -> dict[str, str]:
    return {a["name"]: a["value"] for a in doc["attributes"]}


def _inches(value: str) -> float | None:
    try:
        return parse_length(value).inches
    except DimensionParseError:
        return None


def test_every_bearing_is_rated_by_its_table(docs):
    checked = 0
    for doc in docs:
        if doc["product_type"] != "bearing_radial_ball":
            continue
        v = _values(doc)
        dynamic, static, speed = RATINGS[v["Bearing Number"]]
        if "Dynamic Load Capacity" in v:
            assert v["Dynamic Load Capacity"] == f"{round(dynamic * LBF_PER_KN, -1):,.0f} lbf"
        if "Static Load Capacity" in v:
            assert v["Static Load Capacity"] == f"{round(static * LBF_PER_KN, -1):,.0f} lbf"
        if "Max. RPM" in v:
            expected = round(speed * CLOSURE_SPEED[v["Closure Type"]], -2)
            assert v["Max. RPM"] == f"{expected:,.0f}", (doc["sku"], v)
        checked += 1
    assert checked > 500


def test_every_claimed_standard_applies_to_the_part(docs):
    wrong = [
        (doc["sku"], doc["product_type"], a["value"])
        for doc in docs
        for a in doc["attributes"]
        if a["name"] == "Standards" and a["value"] not in MAY_CLAIM[doc["product_type"]]
    ]
    assert wrong == [], wrong[:10]
    assert sum(1 for d in docs for a in d["attributes"] if a["name"] == "Standards") > 1000


def test_no_finish_or_hardness_the_material_cannot_have(docs):
    wrong = []
    for doc in docs:
        v = _values(doc)
        material, finish = v.get("Material", ""), v.get("Finish", "")
        hardness, grade = v.get("Rockwell Hardness", ""), v.get("Grade", "")
        if "Stainless" in material and finish in NEVER_ON_STAINLESS:
            wrong.append((doc["sku"], material, finish))
        if "Stainless" in material and hardness.startswith("C"):
            wrong.append((doc["sku"], material, hardness))
        if "Alloy" in material and hardness.startswith("B"):
            wrong.append((doc["sku"], material, hardness))
        if material != "Solid Carbide" and finish in CARBIDE_ONLY_COATINGS:
            wrong.append((doc["sku"], material, finish))
        if material == "Solid Carbide" and finish in NOT_ON_CARBIDE:
            wrong.append((doc["sku"], material, finish))
        if finish == "Hot Dip Galvanized" and grade in ("Grade 8", "Class 10.9"):
            wrong.append((doc["sku"], grade, finish))
        if grade and "Stainless" in material:
            wrong.append((doc["sku"], material, grade))
        if re.search(r"\(not plated\)", doc["description"]) and finish not in ("", "Plain"):
            wrong.append((doc["sku"], "not plated", finish))
    assert wrong == [], wrong[:10]


def test_no_end_mill_shank_is_thinner_than_its_cutter(docs):
    """Excused only where a modelled unit-mixing defect rounded one of the two."""
    thin = []
    for doc in docs:
        v = _values(doc)
        cut, shank = _inches(v.get("Milling Dia.", "")), _inches(v.get("Shank Dia.", ""))
        if cut is None or shank is None:
            continue
        mixed = v["Milling Dia."].endswith("mm") != v["Shank Dia."].endswith("mm")
        if shank < cut - (0.002 if mixed else 1e-6):
            thin.append((doc["sku"], v["Milling Dia."], v["Shank Dia."]))
    assert thin == [], thin[:10]


def _in_title(value: str, title: str) -> bool:
    if value in title:
        return True
    # A unit-mixing defect republished the value in the other system after
    # the title was composed: the same quantity, once, in the other unit.
    size = _inches(value)
    if size is None:
        return False
    for token in re.findall(r"[\d./-]+\s?(?:mm|\"|in\.?)", title):
        other = _inches(token.replace(" ", ""))
        if other is not None and abs(other - size) <= max(0.0005, 0.002 * size):
            return True
    return False


def test_every_title_names_its_key_dimension(docs):
    missing = []
    for doc in docs:
        v = _values(doc)
        for name in KEY[doc["product_type"]]:
            if name in v and not _in_title(v[name], doc["title"]):
                missing.append((doc["sku"], name, v[name], doc["title"]))
    assert missing == [], missing[:10]


#: A bare dimension: digits, a fraction, a thread designation, and a unit.
_BARE = re.compile(r'^[\d./\-#Mx ]+(?:mm| mm|"| in\.?)?$')


def test_a_brand_titles_a_type_one_way(docs):
    """The first dimension segment is labelled on every title of a (brand,
    type), or on none: one maker lists one type one way. (Bearings, wheels and
    flap discs lead with a key dimension that is never labelled.)"""
    styles: dict[tuple[str, str], set[bool]] = collections.defaultdict(set)
    for doc in docs:
        if doc["product_type"] in (
            "bearing_radial_ball",
            "wheel_depressed_center",
            "abrasive_flap_disc",
        ):
            continue
        parts = doc["title"].split(",")
        if len(parts) < 2:
            continue
        first = parts[1].strip()
        styles[(doc["brand"], doc["product_type"])].add(not _BARE.match(first))
    mixed = {k: v for k, v in styles.items() if len(v) > 1}
    assert mixed == {}, sorted(mixed)[:10]
    assert len(styles) > 150


def test_kit_titles_say_what_the_kit_is(docs):
    kits = [d for d in docs if d["product_type"] == "kit_assortment"]
    assert kits
    for doc in kits:
        kind = _values(doc)["Type"]
        assert kind in doc["title"], (doc["sku"], doc["title"])


def test_only_a_size_is_called_a_size(docs):
    """ "Also available in Double Shield / Open sizes" named a closure a size."""
    for doc in docs:
        match = re.search(r"Also available in (.+?) sizes\.", doc["description"])
        if match:
            for value in match.group(1).split(" / "):
                assert _inches(value) is not None or re.match(r"^(M|#)?[\d/]", value), (
                    doc["sku"],
                    value,
                )
