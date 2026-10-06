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

from published import published_attributes
from synthetic_industrial_products.catalog import emit
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import Generator, generate
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
    "nut_hex": {"ISO 4032", "ISO 4035", "ISO 8673", "ISO 8675", "ASME B18.2.2", "SAE J995",
                "ISO 898-2"},
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

#: A nut's DIMENSIONAL standards: thread -> (width across flats, height), in
#: mm for the ISO tables and inches for ASME. Transcribed from
#: FreeCAD_FastenersWB (``iso4032def.csv``, ``iso4035def.csv``,
#: ``iso8673def.csv``, ``iso8675def.csv``, ``asmeb18.2.2.1def.csv`` and
#: ``asmeb18.2.2.4def.csv``), with the ASME widths at their nominal
#: fractions. B18.2.2 lists a hex nut AND a jam nut per size, so a B18.2.2
#: claim may be either row. A heavy hex nut is none of these.
_ISO_4032 = {
    "M3x0.5": (5.5, 2.4),
    "M4x0.7": (7.0, 3.2),
    "M5x0.8": (8.0, 4.7),
    "M6x1": (10.0, 5.2),
    "M8x1.25": (13.0, 6.8),
    "M10x1.5": (16.0, 8.4),
    "M12x1.75": (18.0, 10.8),
    "M16x2": (24.0, 14.8),
    "M20x2.5": (30.0, 18.0),
    "M24x3": (36.0, 21.5),
}
_ISO_4035 = {
    "M3x0.5": (5.5, 1.8),
    "M4x0.7": (7.0, 2.2),
    "M5x0.8": (8.0, 2.7),
    "M6x1": (10.0, 3.2),
    "M8x1.25": (13.0, 4.0),
    "M10x1.5": (16.0, 5.0),
    "M12x1.75": (18.0, 6.0),
    "M16x2": (24.0, 8.0),
    "M20x2.5": (30.0, 10.0),
    "M24x3": (36.0, 12.0),
}
_ISO_8673 = {
    "M8x1": (13.0, 6.8),
    "M10x1": (16.0, 8.4),
    "M10x1.25": (16.0, 8.4),
    "M12x1.25": (18.0, 10.8),
    "M12x1.5": (18.0, 10.8),
    "M16x1.5": (24.0, 14.8),
    "M20x1.5": (30.0, 18.0),
    "M20x2": (30.0, 18.0),
}
_ISO_8675 = {
    "M8x1": (13.0, 4.0),
    "M10x1": (16.0, 5.0),
    "M10x1.25": (16.0, 5.0),
    "M12x1.25": (18.0, 6.0),
    "M12x1.5": (18.0, 6.0),
    "M16x1.5": (24.0, 8.0),
    "M20x1.5": (30.0, 10.0),
    "M20x2": (30.0, 10.0),
}
_B18_2_2_HEX = {
    "#6": (5 / 16, 7 / 64),
    "#8": (11 / 32, 1 / 8),
    "#10": (3 / 8, 1 / 8),
    "1/4": (7 / 16, 7 / 32),
    "5/16": (1 / 2, 17 / 64),
    "3/8": (9 / 16, 21 / 64),
    "7/16": (11 / 16, 3 / 8),
    "1/2": (3 / 4, 7 / 16),
    "5/8": (15 / 16, 35 / 64),
    "3/4": (9 / 8, 41 / 64),
    "1": (3 / 2, 55 / 64),
}
_B18_2_2_JAM = {
    "1/4": (7 / 16, 5 / 32),
    "5/16": (1 / 2, 3 / 16),
    "3/8": (9 / 16, 7 / 32),
    "7/16": (11 / 16, 1 / 4),
    "1/2": (3 / 4, 5 / 16),
    "5/8": (15 / 16, 3 / 8),
    "3/4": (9 / 8, 27 / 64),
    "1": (3 / 2, 35 / 64),
}
#: standard -> the tables a record claiming it must be a row of.
NUT_DIMENSIONS = {
    "ISO 4032": (_ISO_4032,), "ISO 4035": (_ISO_4035,), "ISO 8673": (_ISO_8673,),
    "ISO 8675": (_ISO_8675,), "ASME B18.2.2": (_B18_2_2_HEX, _B18_2_2_JAM),
}  # fmt: skip

#: The stocked shank ladders (inches), and the most an oversize shank may be:
#: twice its cutter, or the smallest stocked shank above the cutter when that
#: is more (a 1mm cutter sits on a 3mm shank; nothing thinner is stocked).
SHANKS_IN = (1 / 8, 3 / 16, 1 / 4, 5 / 16, 3 / 8, 1 / 2, 5 / 8, 3 / 4, 1.0)
SHANKS_MM = (3.0, 3.175, 4.0, 6.0, 6.35, 8.0, 10.0, 12.0, 12.7, 16.0, 20.0, 25.0)
#: Standards that describe METRIC radial bearings only (ABMA 20 is "... --
#: Metric Design"). A bearing number with a letter is the inch R series.
METRIC_BEARING_ONLY = {"ISO 15", "ISO 492", "ABMA 20"}

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


#: Every rule in this file is a truth table written for the census-modelled
#: types. The breadth categories (:mod:`.catalog.breadth`,
#: alexander-marquardt/synthetic-industrial-products#34) are cheap filler --
#: their materials, finishes and titles are drawn from a short, plausible
#: list, not measured against a reference table -- so they are EXEMPT here,
#: by the maintainer's own ruling (2026-09-30 refinement on #34).
def _realistic_only(docs: list[dict]) -> list[dict]:
    return [doc for doc in docs if doc.get("spec_quality") != "fast_and_cheap"]


@pytest.fixture(scope="module")
def golden() -> list[dict]:
    docs = [json.loads(line) for line in (GOLDEN / "flat.jsonl").read_text("utf-8").splitlines()]
    return _realistic_only(docs)


@pytest.fixture(scope="module")
def fresh() -> list[dict]:
    return _realistic_only(list(emit.iter_flat(generate(GeneratorConfig()))))


@pytest.fixture(scope="module", params=["golden", "fresh"])
def docs(request) -> list[dict]:
    return request.getfixturevalue(request.param)


def _values(doc: dict) -> dict[str, str]:
    """Name to PUBLISHED spelling, from flat ``facets``: the tables are checked as published."""
    return {a["name"]: a["value"] for a in published_attributes(doc)}


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
        for a in published_attributes(doc)
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


def _published_tolerance(value: str) -> float:
    """Half the precision the value is written to, in inches: a feed that
    writes whole millimetres states 2.4mm as ``2mm``."""
    if value.endswith("mm"):
        number = value[:-2].strip()
        places = len(number.split(".")[1]) if "." in number else 0
        return 0.5 * 10**-places / 25.4 + 1e-6
    return 0.004


def _is_row(published: dict, row: tuple[float, float], unit: float) -> bool:
    """Whether every published (inches, tolerance) is ``row``'s value."""
    return all(
        abs(published[name][0] - want * unit) <= published[name][1]
        for name, want in zip(("Width Across Flats", "Height"), row, strict=True)
        if name in published and published[name][0] is not None
    )


def test_a_nut_claims_only_the_standard_its_dimensions_are(docs):
    """A nut claiming a dimensional standard publishes THAT standard's width
    across flats and height for its thread. A heavy hex nut claiming ISO 4032
    (the regular nut), or an M10x1.25 nut claiming a coarse-thread standard,
    is an invented fact -- the review of 7dac659 found 29 and 53 of them."""
    wrong, checked = wrong_nut_standards(docs)
    assert wrong == [], wrong[:10]
    assert checked > 200


def wrong_nut_standards(docs: list[dict]) -> tuple[list, int]:
    """The nut records whose dimensional claim is not their row, and how many
    claims were checked."""
    wrong, checked = [], 0
    for doc in docs:
        if doc["product_type"] != "nut_hex":
            continue
        values = _values(doc)
        claimed = [
            a["value"]
            for a in published_attributes(doc)
            if a["name"] == "Standards" and a["value"] in NUT_DIMENSIONS
        ]
        thread = values["Thread Size"]
        key = thread if thread.startswith("M") else thread.split("-")[0]
        for standard in claimed:
            checked += 1
            unit = 1 / 25.4 if standard.startswith("ISO") else 1.0
            rows = [t[key] for t in NUT_DIMENSIONS[standard] if key in t]
            if not rows:
                wrong.append((doc["sku"], standard, thread, "no such row"))
                continue
            published = {
                name: (_inches(values[name]), _published_tolerance(values[name]))
                for name in ("Width Across Flats", "Height")
                if name in values
            }
            if not any(_is_row(published, row, unit) for row in rows):
                wrong.append((doc["sku"], standard, values.get("Type"), thread, published))
    return wrong, checked


def test_an_inch_bearing_claims_no_metric_bearing_standard(docs):
    wrong, metric = [], 0
    for doc in docs:
        if doc["product_type"] != "bearing_radial_ball":
            continue
        claimed = {a["value"] for a in published_attributes(doc) if a["name"] == "Standards"}
        if _values(doc)["Bearing Number"].isdigit():
            metric += bool(claimed)
        elif claimed & METRIC_BEARING_ONLY:
            wrong.append((doc["sku"], _values(doc)["Bearing Number"], sorted(claimed)))
    assert wrong == [], wrong[:10]
    assert metric > 100


def test_a_title_names_the_mills_own_end_shape(docs):
    """``SGL Sq End`` on a ball nose end mill states a shape it does not have
    (168 of 568 ball end mills on 7dac659's golden)."""
    wrong, named = [], collections.Counter()
    for doc in docs:
        if not doc["product_type"].startswith("end_mill"):
            continue
        shape = _values(doc)["End Mill Style"]
        for word, style in (("Sq End", "Square"), ("Ball End", "Ball Nose")):
            if re.search(rf"\b(?:SGL|DBL) {word}\b", doc["title"]):
                named[style] += 1
                if style != shape:
                    wrong.append((doc["sku"], shape, doc["title"]))
    assert wrong == [], wrong[:10]
    assert named["Square"] > 50 and named["Ball Nose"] > 20, named


def test_no_end_mill_shank_is_oversize(docs):
    """A 5/32" cutter on a 5/8" shank is not an end mill a maker sells: an
    oversize shank is at most twice the cutter, unless nothing smaller than
    that is stocked above the cutter."""
    fat, checked = oversize_shanks(docs)
    assert fat == [], fat[:10]
    assert checked > 1000


def oversize_shanks(docs: list[dict]) -> tuple[list, int]:
    fat, checked = [], 0
    for doc in docs:
        v = _values(doc)
        cut, shank = _inches(v.get("Milling Dia.", "")), _inches(v.get("Shank Dia.", ""))
        if cut is None or shank is None:
            continue
        checked += 1
        ladder = SHANKS_MM if v["Shank Dia."].endswith("mm") else None
        stocked = [s / 25.4 for s in ladder] if ladder else list(SHANKS_IN)
        above = [s for s in stocked if s > cut + 1e-6]
        ceiling = max(2 * cut, min(above)) if above else cut
        if shank > ceiling + 0.002:
            fat.append((doc["sku"], v["Milling Dia."], v["Shank Dia."]))
    return fat, checked


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


def test_a_brand_names_a_secondary_dimension_on_every_title_or_none(monkeypatch):
    """Labelled and secondary are two styles, and a pair has ONE of them.

    :func:`test_a_brand_titles_a_type_one_way` reads the title string, so it
    tells a labelled key size from a bare one -- but a labelled title with a
    second labelled dimension (``5/16" Milling Dia., 1-1/4" Cut L``) and one
    without look alike to it: a per-SKU choice between the two stayed green.
    This test reads the segments the generator composes (a title's
    ``Segment`` keeps the attribute it names for exactly this), on a fresh
    build: within a (brand, type), either no title names a secondary
    dimension, or every title whose record publishes one names one.
    """
    calls: list[tuple[tuple[str, str], str]] = []
    original = Generator._dimension_segments

    def spy(self, draft, child):
        segments = original(self, draft, child)
        if segments:
            primary = child.primary.name
            could = any(
                a.name in self._published and a.name != primary for a in child.secondary.values()
            )
            if segments[0].label is None:
                kind = "unlabelled"
            elif len(segments) > 1:
                kind = "secondary"
            else:
                kind = "labelled" if could else ""
            if kind:
                calls.append(((draft.brand, draft.type_key), kind))
        return segments

    monkeypatch.setattr(Generator, "_dimension_segments", spy)
    generate(GeneratorConfig())
    kinds: dict[tuple[str, str], collections.Counter] = collections.defaultdict(collections.Counter)
    for pair, kind in calls:
        kinds[pair][kind] += 1
    mixed = {pair: dict(k) for pair, k in kinds.items() if len(k) > 1}
    assert mixed == {}, sorted(mixed.items())[:10]
    styles = collections.Counter(next(iter(k)) for k in kinds.values())
    assert styles["secondary"] > 10 and styles["labelled"] > 10, styles


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
