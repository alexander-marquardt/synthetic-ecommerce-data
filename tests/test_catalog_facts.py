"""Facts a record states are real, and a brand lists a type one way.

The review of the 100K catalog found invented facts: bearing load ratings a
formula made up, standards drawn from a pool for other parts, finishes and
hardnesses that no maker sells on that material, end mills whose shank is
thinner than their flutes, and titles that dropped the part's key size.
Each rule is checked against tables written out apart from the generator's
own rules: here, or, for the per-type facts (the standards a type may claim
and its title key), in ``type_facts``, which reads them from each type's
``TypeSpec`` so that a new type edits no table here (#61).
"""

from __future__ import annotations

import collections
import itertools
import json
import re
from pathlib import Path

import pytest

import type_facts
import type_gates
from published import published_attributes
from synthetic_industrial_products.catalog import emit, newtypes
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import Generator, generate
from synthetic_industrial_products.dimensions import DimensionParseError, parse_length

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"
LBF_PER_KN = 224.809

#: Deep groove ball bearing ratings: (dynamic C kN, static C0 kN, limiting
#: speed rpm of the open bearing). Every metric row is one maker's on one
#: basis: SKF's deep groove ball bearing product pages,
#: https://www.skf.com/group/products/rolling-bearings/ball-bearings/deep-groove-ball-bearings/productid-<number>,
#: retrieved 2026-10-07. Two makers' rows side by side break the series' order
#: at the seam, since their speed ratings are not on one basis. The inch R
#: rows are distributor listings.
RATINGS = {
    "607": (2.34, 0.95, 53000), "608": (3.45, 1.37, 48000), "609": (3.90, 1.66, 43000),
    "625": (1.14, 0.38, 60000), "626": (2.34, 0.95, 50000), "627": (3.45, 1.37, 45000),
    "629": (4.75, 1.96, 38000), "6000": (4.75, 1.96, 40000), "6001": (5.40, 2.36, 38000),
    "6002": (5.85, 2.85, 32000), "6003": (6.37, 3.25, 28000), "6004": (9.95, 5.00, 24000),
    "6005": (11.9, 6.55, 20000), "6006": (13.8, 8.30, 17000), "6007": (16.8, 10.2, 15000),
    "6008": (17.8, 11.0, 14000), "6009": (22.1, 14.6, 12000), "6010": (22.9, 16.0, 11000),
    "6011": (29.6, 21.2, 10000), "6012": (30.7, 23.2, 9500), "6013": (31.9, 25.0, 9000),
    "6014": (39.7, 31.0, 8000), "6015": (41.6, 33.5, 7500), "6016": (49.4, 40.0, 7000),
    "6017": (52.0, 43.0, 6700), "6018": (60.5, 50.0, 6300), "6019": (63.7, 54.0, 6000),
    "6020": (63.7, 54.0, 5600), "6200": (5.40, 2.36, 36000), "6201": (7.28, 3.10, 32000),
    "6202": (8.06, 3.75, 28000), "6203": (9.95, 4.75, 24000), "6204": (13.5, 6.55, 20000),
    "6205": (14.8, 7.80, 18000), "6206": (20.3, 11.2, 15000), "6207": (27.0, 15.3, 13000),
    "6208": (32.5, 19.0, 11000), "6209": (35.1, 21.6, 11000), "6210": (37.1, 23.2, 10000),
    "6211": (46.2, 29.0, 9000), "6212": (55.3, 36.0, 8000), "6213": (58.5, 40.5, 7500),
    "6214": (63.7, 45.0, 7000), "6215": (68.9, 49.0, 6700), "6216": (72.8, 55.0, 6000),
    "6217": (87.1, 64.0, 5600), "6218": (101.0, 73.5, 5300), "6219": (114.0, 81.5, 5000),
    "6220": (127.0, 93.0, 4800), "6300": (8.52, 3.40, 32000), "6301": (10.1, 4.15, 28000),
    "6302": (11.9, 5.40, 24000), "6303": (14.3, 6.55, 22000), "6304": (16.8, 7.80, 19000),
    "6305": (23.4, 11.6, 16000), "6306": (29.6, 16.0, 13000), "6307": (35.1, 19.0, 12000),
    "6308": (42.3, 24.0, 11000), "6309": (55.3, 31.5, 9500), "6310": (65.0, 38.0, 8500),
    "6311": (74.1, 45.0, 8000), "6312": (85.2, 52.0, 7000), "6313": (97.5, 60.0, 6700),
    "6314": (111.0, 68.0, 6300), "6315": (119.0, 76.5, 5600), "6316": (130.0, 86.5, 5300),
    "6317": (140.0, 96.5, 5000), "6318": (151.0, 108.0, 4800), "6319": (159.0, 118.0, 4500),
    "6320": (174.0, 140.0, 4300), "R4": (1.14, 0.46, 48000), "R6": (3.30, 1.40, 36000),
    "R8": (5.07, 2.37, 28000), "R10": (6.23, 3.30, 24000), "R12": (9.36, 4.80, 20000),
}  # fmt: skip
#: ISO 15 boundary dimensions of a radial bearing, (outside dia, width) mm by
#: bore mm, for the three diameter series the catalog stocks: 0 (6000-6020,
#: 607-609), 2 (6200-6220, 625-629) and 3 (6300-6320).
ISO15_SERIES = {
    "0": {7: (19, 6), 8: (22, 7), 9: (24, 7), 10: (26, 8), 12: (28, 8), 15: (32, 9),
          17: (35, 10), 20: (42, 12), 25: (47, 12), 30: (55, 13), 35: (62, 14), 40: (68, 15),
          45: (75, 16), 50: (80, 16), 55: (90, 18), 60: (95, 18), 65: (100, 18),
          70: (110, 20), 75: (115, 20), 80: (125, 22), 85: (130, 22), 90: (140, 24),
          95: (145, 24), 100: (150, 24)},
    "2": {5: (16, 5), 6: (19, 6), 7: (22, 7), 8: (24, 8), 9: (26, 8), 10: (30, 9),
          12: (32, 10), 15: (35, 11), 17: (40, 12), 20: (47, 14), 25: (52, 15), 30: (62, 16),
          35: (72, 17), 40: (80, 18), 45: (85, 19), 50: (90, 20), 55: (100, 21),
          60: (110, 22), 65: (120, 23), 70: (125, 24), 75: (130, 25), 80: (140, 26),
          85: (150, 28), 90: (160, 30), 95: (170, 32), 100: (180, 34)},
    "3": {10: (35, 11), 12: (37, 12), 15: (42, 13), 17: (47, 14), 20: (52, 15),
          25: (62, 17), 30: (72, 19), 35: (80, 21), 40: (90, 23), 45: (100, 25),
          50: (110, 27), 55: (120, 29), 60: (130, 31), 65: (140, 33), 70: (150, 35),
          75: (160, 37), 80: (170, 39), 85: (180, 41), 90: (190, 43), 95: (200, 45),
          100: (215, 47)},
}  # fmt: skip


def iso15_bore(number: str) -> int:
    """The bore a metric deep groove designation's bore code names, per ISO 15:
    a single digit is the bore in mm; 00-03 are 10, 12, 15 and 17; 04 and up
    are five times the code."""
    code = number[2:]
    if len(code) == 1:
        return int(code)
    return {"00": 10, "01": 12, "02": 15, "03": 17}.get(code, 5 * int(code))


#: A contact seal limits speed to about 70% of the open bearing; a shield does not.
CLOSURE_SPEED = {"Open": 1.0, "Double Shield": 1.0, "Double Seal": 0.70}

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
#: three times its cutter -- 43 of the 46 differing records in
#: reference-statistics/04 are at or under 3.0, the 2.667 and 3.0 ratios
#: included -- or the smallest stocked shank above the cutter when that is
#: more. A metric cutter below 6 mm may also sit on the 6 mm DIN 6535 shank:
#: a catalog convention the #33 review proposed, not yet confirmed against a
#: standard's diameter table (#87).
SHANKS_IN = (1 / 8, 3 / 16, 1 / 4, 5 / 16, 3 / 8, 1 / 2, 5 / 8, 3 / 4, 1.0)
SHANKS_MM = (3.0, 3.175, 4.0, 6.0, 6.35, 8.0, 10.0, 12.0, 12.7, 16.0, 20.0, 25.0)
MAX_SHANK_RATIO = 3.0
SMALL_METRIC_SHANK_MM = 6.0
#: Standards that describe METRIC radial bearings only (ABMA 20 is "... --
#: Metric Design"). A bearing number with a letter is the inch R series.
METRIC_BEARING_ONLY = {"ISO 15", "ISO 492", "ABMA 20"}

#: Finishes no maker sells on the material, and hardness scales that cannot be.
NEVER_ON_STAINLESS = {"Zinc Plated", "Zinc Yellow", "Hot Dip Galvanized", "Black Oxide"}
CARBIDE_ONLY_COATINGS = {"nACo"}
NOT_ON_CARBIDE = {"Black Oxide", "Bronze Oxide", "Steam Oxide"}


def may_claim(type_key: str) -> frozenset[str]:
    """The standards ``type_key`` may claim. A type declared nowhere, or in
    both its module and a shared row, is refused (``type_facts``)."""
    return type_facts.may_claim()[type_key]


def title_key(type_key: str) -> tuple[str, ...]:
    """The key dimension a title of ``type_key`` names, refused as :func:`may_claim` is."""
    return type_facts.title_key()[type_key]


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


def test_each_metric_series_is_in_rating_order_by_bore():
    """Within one ISO 15 diameter series a larger bore never carries a lower
    load rating or a higher limiting speed. A table that mixes two makers'
    rows breaks that at the seam, and a shopper sees it on the published Max.
    RPM: a 609 (9x24 mm) rated slower than a 6000 (10x26 mm). Read on the
    generator's own table, the one every published rating comes from."""
    by_series: dict[str, list[tuple[int, str]]] = collections.defaultdict(list)
    for number, bore, _od, _width in newtypes._BEARINGS_METRIC:
        by_series[number[1]].append((bore, number))
    breaks = []
    for series, rows in sorted(by_series.items()):
        rows.sort()
        for (_, small), (_, large) in itertools.pairwise(rows):
            c1, c01, rpm1 = newtypes.BEARING_RATINGS[small]
            c2, c02, rpm2 = newtypes.BEARING_RATINGS[large]
            if c2 < c1 or c02 < c01 or rpm2 > rpm1:
                breaks.append((series, small, large))
    assert breaks == []
    assert {s: len(r) for s, r in by_series.items()} == {"0": 24, "2": 25, "3": 21}


def test_the_metric_numbers_are_every_one_the_maker_rates():
    """The generator stocks every 60/62/63 number from 5 mm to 100 mm bore
    that the table's maker publishes, so no common size is a silent hole, and
    nothing it does not publish. SKF lists 628 only with seals or shields, so
    the open bearing's rating is not published and 628 is not stocked; 605,
    606 and the 61x numbers are outside the ladder."""
    unpublished = {"628"}
    ladder = {f"6{s}{i:02d}" for s in "023" for i in range(21)}
    ladder |= {"607", "608", "609", "625", "626", "627", "628", "629"}
    stocked = {number for number, *_ in newtypes._BEARINGS_METRIC}
    assert stocked == ladder - unpublished
    assert stocked == {n for n in RATINGS if n.isdigit()}
    assert {n for n, *_ in newtypes._BEARINGS_METRIC + newtypes._BEARINGS_INCH} == set(
        newtypes.BEARING_RATINGS
    )


def test_every_metric_bearing_has_its_iso_15_boundary_dimensions(docs):
    """A metric bearing number names its bore by its bore code and its outside
    diameter and width by ISO 15's table for its diameter series, the second
    digit of 60/62/63. Held against the table written out above, not the
    generator's, so a widened size range cannot carry an invented size."""
    bores: set[int] = set()
    wrong = []
    for doc in docs:
        if doc["product_type"] != "bearing_radial_ball":
            continue
        v = _values(doc)
        number = v["Bearing Number"]
        if not number.isdigit():
            continue
        bore = iso15_bore(number)
        od, width = ISO15_SERIES[number[1]][bore]
        for name, mm in (("Bore Dia.", bore), ("Outside Dia.", od), ("Width", width)):
            if name not in v:
                continue
            inches = _inches(v[name])
            if inches is None or abs(inches - mm / 25.4) >= 0.002:
                wrong.append((doc["sku"], number, name, v[name], mm))
        bores.add(bore)
    assert not wrong, wrong[:5]
    assert (min(bores), max(bores)) == (5, 100), sorted(bores)


def test_every_claimed_standard_applies_to_the_part(docs):
    wrong = wrong_claims(docs)
    assert wrong == [], wrong[:10]
    assert sum(1 for d in docs for a in d["attributes"] if a["name"] == "Standards") > 1000


def wrong_claims(docs: list[dict]) -> list[tuple[str, str, str]]:
    """(SKU, type, standard) for each published claim outside the type's
    declared ``may_claim`` (``type_facts``)."""
    may_claim = type_facts.may_claim()
    return [
        (doc["sku"], doc["product_type"], a["value"])
        for doc in docs
        for a in published_attributes(doc)
        if a["name"] == "Standards" and a["value"] not in may_claim[doc["product_type"]]
    ]


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


def test_a_nut_says_which_table_each_dimension_came_from(docs):
    """A nut claiming ISO 4032 must not say no standard fixes its values, which
    every hex nut said until the review of PR #60."""
    nuts = [doc for doc in docs if doc["product_type"] == "nut_hex"]
    problems, checked = type_gates.provenance_problems(
        nuts, NUT_DIMENSIONS, ("Width Across Flats", "Height")
    )
    assert problems == [], problems[:10]
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
    """A 5/32" cutter on a 5/8" shank (4x) is not an end mill a maker sells:
    an oversize shank is at most three times the cutter, unless nothing
    smaller than that is stocked above the cutter, or the cutter is a metric
    one below 6 mm on the 6 mm shank."""
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
        metric = v["Shank Dia."].endswith("mm")
        stocked = [s / 25.4 for s in SHANKS_MM] if metric else list(SHANKS_IN)
        above = [s for s in stocked if s > cut + 1e-6]
        ceiling = max(MAX_SHANK_RATIO * cut, min(above)) if above else cut
        if metric and cut < SMALL_METRIC_SHANK_MM / 25.4 - 1e-6:
            ceiling = max(ceiling, SMALL_METRIC_SHANK_MM / 25.4)
        if shank > ceiling + 0.002:
            fat.append((doc["sku"], v["Milling Dia."], v["Shank Dia."]))
    return fat, checked


def _oversize_pairs(docs: list[dict], unit: str) -> list[tuple[str, float, float]]:
    """(sku, cutter, shank) in inches for end mills whose shank differs from
    the cutter, both published in ``unit`` (``mm`` or ``"``)."""
    pairs = []
    for doc in docs:
        v = _values(doc)
        cut_text, shank_text = v.get("Milling Dia.", ""), v.get("Shank Dia.", "")
        if not (cut_text.endswith(unit) and shank_text.endswith(unit)):
            continue
        cut, shank = _inches(cut_text), _inches(shank_text)
        if cut is None or shank is None or abs(shank - cut) < 1e-4:
            continue
        pairs.append((doc["sku"], cut, shank))
    return pairs


def test_a_small_metric_cutter_on_an_oversize_shank_sits_on_6mm(docs):
    """The catalog puts a 1-5 mm cutter on the 6 mm DIN 6535 shank, a
    convention the #33 review proposed and no standard's table has yet
    confirmed (#87). A cap that turned a 1-2.5 mm cutter's
    oversize shank into a 3 mm one made the common metric product the rare
    one (31 SKUs on 29f's golden)."""
    small = [p for p in _oversize_pairs(docs, "mm") if p[1] < SMALL_METRIC_SHANK_MM / 25.4 - 1e-6]
    off = [p for p in small if abs(p[2] * 25.4 - SMALL_METRIC_SHANK_MM) > 1e-3]
    assert off == [], f"{len(off)} of {len(small)} not on 6 mm: {off[:10]}"
    assert len(small) > 20


def test_the_census_wide_shank_ratios_still_occur(docs):
    """The cap is not tighter than the census: 4 of its 46 differing records
    sit at 2.667x or 3.0x, so some inch end mills carry a shank in that band.
    The band is the census's own, not 2x-3x: a cap of 2.5x still draws the
    2.29x, 2.4x and 2.5x pairs, and would pass a wider window."""
    band = [p for p in _oversize_pairs(docs, '"') if 2.6 < p[2] / p[1] <= 3.0 + 1e-6]
    assert len(band) > 5, band


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
    missing = untitled_keys(docs)
    assert missing == [], missing[:10]


def untitled_keys(docs: list[dict]) -> list[tuple[str, str, str, str]]:
    """(SKU, attribute, value, title) for each declared title key attribute
    (``type_facts``) a record publishes and its title does not name."""
    keys = type_facts.title_key()
    missing = []
    for doc in docs:
        v = _values(doc)
        for name in keys[doc["product_type"]]:
            if name in v and not _in_title(v[name], doc["title"]):
                missing.append((doc["sku"], name, v[name], doc["title"]))
    return missing


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
