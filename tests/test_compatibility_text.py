"""Every cross-reference sentence is a fact, and the near-miss threads are real.

The copy says which screws a key drives, which drill a tap wants, which bolts
a nut fits (:mod:`synthetic_ecommerce_data.catalog.compat`). Each claim is
checked here against tables written out FROM THE STANDARDS in this file --
not against the generator's own tables, which the first tests check in turn --
and against the record's own published values.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

import pytest

from compat_text import compatibility_sentences, without_compatibility
from published import published_attributes
from synthetic_ecommerce_data.catalog import compat, emit, typespec
from synthetic_ecommerce_data.catalog.config import GeneratorConfig
from synthetic_ecommerce_data.catalog.generate import generate
from synthetic_ecommerce_data.dimensions import parse_length

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"
MM = 25.4

#: ISO 4762 socket (s, nominal) by diameter, and ASME B18.3's key by diameter.
ISO_4762_KEY_MM = {
    "M3": 2.5, "M4": 3, "M5": 4, "M6": 5, "M8": 6, "M10": 8, "M12": 10, "M16": 14, "M20": 17,
}  # fmt: skip
ASME_B18_3_KEY_IN = {
    "#6": 7 / 64, "#8": 9 / 64, "#10": 5 / 32, "1/4": 3 / 16, "5/16": 1 / 4,
    "3/8": 5 / 16, "7/16": 3 / 8, "1/2": 3 / 8, "5/8": 1 / 2,
}  # fmt: skip
#: Every pitch below, coarse, fine, UNC and UNF, was checked row by row against
#: one table: FreeCAD's hole thread tables ("ISO metric regular", "ISO metric
#: fine", "UNC", "UNF" in src/Mod/PartDesign/App/FeatureHole.cpp, FreeCAD
#: commit 3424c410627263394f701aeec5b61d7bab7bb3a1, LGPL-2.1), which list the
#: ISO 261 diameter-pitch pairs and the ASME B1.1 pitches (an inch pitch there
#: is in mm: 25.4 / TPI). All rows agree with it, M36x2 included.
#:
#: ISO 261 coarse pitches, and ISO 262's selected fine ones.
METRIC_COARSE = {
    "M3": 0.5, "M4": 0.7, "M5": 0.8, "M6": 1.0, "M8": 1.25, "M10": 1.5, "M12": 1.75,
    "M14": 2.0, "M16": 2.0, "M18": 2.5, "M20": 2.5, "M22": 2.5, "M24": 3.0, "M27": 3.0,
    "M30": 3.5, "M33": 3.5, "M36": 4.0,
}  # fmt: skip
METRIC_FINE = {"M8": {1.0}, "M10": {1.25, 1.0}, "M12": {1.5, 1.25}, "M16": {1.5}, "M20": {1.5, 2.0}}
#: ASME B1.1 threads per inch.
UNC = {
    "#4": 40, "#6": 32, "#8": 32, "#10": 24, "1/4": 20, "5/16": 18, "3/8": 16, "7/16": 14,
    "1/2": 13, "9/16": 12, "5/8": 11, "3/4": 10, "7/8": 9, "1": 8,
}  # fmt: skip
UNF = {
    "#6": 40,
    "#8": 36,
    "#10": 32,
    "1/4": 28,
    "5/16": 24,
    "3/8": 24,
    "7/16": 20,
    "1/2": 20,
    "5/8": 18,
}  # noqa: E501
#: Fine pitches a threaded type sells that the near-miss sentences do not
#: offer (``compat.fine_threads``, held to the two tables above): ISO 261's
#: metric fine pitches and ASME B1.1's UNF, for the lock nut's larger sizes.
SOLD_FINE = {
    "M14": {1.5}, "M24": {2.0}, "M30": {2.0}, "M36": {2.0},
    "9/16": {18}, "3/4": {16}, "7/8": {14}, "1": {12},
}  # fmt: skip
#: Number and letter drill sizes (ASME B94.11M), inches.
LETTER_NUMBER_DRILLS = {
    "#36": 0.1065, "#29": 0.1360, "#25": 0.1495, "#21": 0.1590, "#7": 0.2010, "#3": 0.2130,
    "F": 0.2570, "I": 0.2720, "Q": 0.3320, "U": 0.3680,
}  # fmt: skip


def _major_in(diameter: str) -> float:
    if diameter.startswith("M"):
        return float(diameter[1:]) / MM
    if diameter.startswith("#"):
        return 0.060 + 0.013 * int(diameter[1:])
    return float(Fraction(diameter))


def _split(thread: str) -> tuple[str, float]:
    """``M12x1.5`` -> (``M12``, 1.5); ``1/4-28`` -> (``1/4``, 28)."""
    if thread.startswith("M"):
        dia, pitch = thread.split("x")
        return dia, float(pitch)
    dia, tpi = thread.split("-")
    return dia, float(tpi)


def _drill_in(named: str) -> float:
    return LETTER_NUMBER_DRILLS.get(named) or parse_length(named).inches


@pytest.fixture(scope="module")
def golden() -> list[dict]:
    return [json.loads(line) for line in (GOLDEN / "flat.jsonl").read_text("utf-8").splitlines()]


@pytest.fixture(scope="module")
def fresh() -> list[dict]:
    """The default build, emitted in memory (a few seconds): so a generator
    change reds here before a regeneration hides it in the golden."""
    return list(emit.iter_flat(generate(GeneratorConfig())))


@pytest.fixture(scope="module", params=["golden", "fresh"])
def docs(request) -> list[dict]:
    return request.getfixturevalue(request.param)


# --- the generator's tables, against the standards ----------------------------


def test_every_metric_tap_drill_is_the_diameter_less_the_pitch():
    """To the stocked tenth: a chart drills M8x1.25's 6.75 at 6.8."""
    for thread, drill_mm in compat.TAP_DRILLS_METRIC.items():
        dia, pitch = _split(thread)
        assert abs(drill_mm - (float(dia[1:]) - pitch)) <= 0.05 + 1e-9, thread
        assert round(drill_mm * 10) == pytest.approx(drill_mm * 10), thread


def test_every_inch_tap_drill_is_the_named_drill_and_cuts_a_usable_thread():
    """75%-thread chart entries: the drill cuts 60-85% of a full thread depth."""
    for thread, (named, decimal) in compat.TAP_DRILLS_INCH.items():
        assert _drill_in(named) == pytest.approx(decimal, abs=5e-5), thread
        dia, tpi = _split(thread)
        percent = tpi * (_major_in(dia) - decimal) / 0.01299
        assert 60 <= percent <= 85, (thread, round(percent, 1))


def test_the_key_to_screw_table_is_the_standards():
    table = compat.socket_head_keys()
    for size, key_mm in ISO_4762_KEY_MM.items():
        assert table[size] == (pytest.approx(key_mm / MM), "ISO 4762"), size
    for size, key_in in ASME_B18_3_KEY_IN.items():
        assert table[size] == (pytest.approx(key_in), "ASME B18.3"), size


def test_the_fine_pitches_are_iso_262s_and_the_unified_fine_series():
    for dia, pitches in METRIC_FINE.items():
        assert set(compat.fine_threads(dia, metric=True)) == {f"{dia}x{p:g}" for p in pitches}
    for dia, tpi in UNF.items():
        assert compat.fine_threads(dia, metric=False) == (f"{dia}-{tpi}",)


# --- every sentence in the catalog --------------------------------------------


def _published(doc: dict) -> dict[str, str]:
    """Name to published spelling, from flat ``facets`` (a nested entry carries none, #42)."""
    return {a["name"]: a["value"] for a in published_attributes(doc)}


def _same_length(a: str, b: str) -> bool:
    return abs(parse_length(a).inches - parse_length(b).inches) < 1e-4


def sentence_errors(docs: list[dict]) -> list[tuple[str, str]]:
    """Every (sku, sentence) whose claim the standards or the record contradict."""
    bad: list[tuple[str, str]] = []
    for doc in docs:
        values = _published(doc)
        for match in compatibility_sentences(doc["description"]):
            ok = _sentence_holds(match, doc["product_type"], values)
            if not ok or match.group(0) not in doc.get("text", match.group(0)):
                bad.append((doc["sku"], match.group(0)))
    return bad


def _sentence_holds(match: re.Match[str], type_key: str, values: dict[str, str]) -> bool:
    g = match.groupdict()
    if g["screws"] is not None:
        if type_key != "hex_key":
            return False
        key_in = parse_length(values["Size"]).inches
        metric = g["standard"] == "ISO 4762"
        table = {s: k / MM for s, k in ISO_4762_KEY_MM.items()} if metric else ASME_B18_3_KEY_IN
        fits = {s for s, k in table.items() if abs(k - key_in) < 1e-4}
        named = {s.strip().rstrip('"') for s in re.split(r",| and ", g["screws"])}
        return bool(fits) and named == fits and values["Size"].endswith("mm") == metric
    if g["key"] is not None:
        drive = values.get("Drive Size")
        if drive is None or not _same_length(g["key"], drive):
            return False
        if type_key == "screw_socket_head":
            dia = _split(values["Dia./Thread Size"])[0]
            known = (
                ISO_4762_KEY_MM.get(dia, 0) / MM if dia.startswith("M") else ASME_B18_3_KEY_IN[dia]
            )
            return abs(parse_length(drive).inches - known) < 1e-4
        return True
    if g["tapped"] is not None:
        if type_key != "tap_spiral_point" or values.get("Thread Size") != g["tapped"]:
            return False
        if g["tap_drill"] is None:
            return g["tapped"] not in compat.TAP_DRILLS_METRIC | compat.TAP_DRILLS_INCH
        dia, pitch = _split(g["tapped"])
        if dia.startswith("M"):
            drill_mm = parse_length(g["tap_drill"]).inches * MM
            return abs(drill_mm - (float(dia[1:]) - pitch)) <= 0.05 + 1e-6
        percent = pitch * (_major_in(dia) - _drill_in(g["tap_drill"])) / 0.01299
        return 60 <= percent <= 85
    if g["drilled"] is not None:
        if type_key != "drill_jobber":
            return False
        size_in = parse_length(values["Size"]).inches
        for thread in re.split(r",| and ", g["drilled"]):
            dia, pitch = _split(thread.strip())
            if dia.startswith("M"):
                if abs(size_in * MM - (float(dia[1:]) - pitch)) > 0.05 + 1e-6:
                    return False
            elif not 60 <= pitch * (_major_in(dia) - size_in) / 0.01299 <= 85:
                return False
        return True
    if g["nut"] is not None:
        return type_key == "nut_hex" and values.get("Thread Size") == g["nut"]
    return type_key == "washer_flat" and values.get("Size") == g["washer"]


def test_every_compatibility_sentence_holds(docs):
    assert sentence_errors(docs) == []
    kinds = {
        next(
            k
            for k, v in m.groupdict().items()
            if v is not None and k not in ("standard", "tap_drill")
        )
        for doc in docs
        for m in compatibility_sentences(doc["description"])
    }
    assert kinds == {"screws", "key", "tapped", "drilled", "nut", "washer"}, kinds


def test_a_planted_false_sentence_is_caught(golden):
    key = next(d for d in golden if "For M12 socket head cap screws" in d["description"])
    planted = dict(key, description=key["description"].replace("For M12 ", "For M10 "))
    assert sentence_errors([planted]) == [
        (key["sku"], "For M10 socket head cap screws (ISO 4762).")
    ]
    drill = next(d for d in golden if "Tap drill for M12x1.75 threads (" in d["description"])
    planted = dict(drill, description=drill["description"].replace("M12x1.75", "M12x1.5"))
    assert sentence_errors([planted]) == [
        (drill["sku"], "Tap drill for M12x1.5 threads (M12 thread, 1.75 mm pitch).")
    ]


def test_no_record_carries_another_products_attributes(docs):
    """The cross-reference is text: a key never publishes a thread size."""
    for doc in docs:
        if doc["product_type"] in ("hex_key", "drill_jobber", "washer_flat"):
            assert not {"Thread Size", "Dia./Thread Size"} & set(_published(doc)), doc["sku"]


def test_a_size_query_reaches_more_than_one_product_type(docs):
    """What the sentences are for: ``M12`` is in the searchable text of screws,
    bolts, nuts, taps, washers and keys, and ``10.2mm``'s drill names M12x1.75."""
    types = {d["product_type"] for d in docs if re.search(r"\bM12\b|M12x", d["text"])}
    assert {
        "screw_socket_head",
        "bolt_hex",
        "nut_hex",
        "tap_spiral_point",
        "washer_flat",
        "hex_key",
    } <= types  # noqa: E501
    assert any("Tap drill for M12x1.75" in d["text"] for d in docs)


def test_a_metric_designation_is_searchable_by_its_diameter(docs):
    """``M12x1.75`` is one token to the standard analyzer, so the record's
    searchable text also names ``M12`` -- or ``m12 socket cap screws`` reaches
    the keys whose copy mentions M12 screws and not one screw."""
    checked = 0
    for doc in docs:
        for value in _published(doc).values():
            match = re.fullmatch(r"M(\d+(?:\.\d+)?)x\d+(?:\.\d+)?", value)
            if match:
                assert re.search(rf"(?<!\S)M{match.group(1)}(?!\S)", doc["text"]), doc["sku"]
                checked += 1
    assert checked > 100, checked


def test_the_description_is_the_template_plus_at_most_one_sentence(docs):
    for doc in docs:
        found = compatibility_sentences(doc["description"])
        assert len(found) <= 1, doc["sku"]
        assert "  " not in without_compatibility(doc["description"]), doc["sku"]


# --- near-miss threads ---------------------------------------------------------

#: The thread attribute of each type still declared in the shared tables. A
#: type with its own module declares it on its TypeSpec (``threaded``).
SHARED_THREADED = {
    "screw_flat_head": "Dia./Thread Size",
    "screw_button_head": "Dia./Thread Size",
    "screw_low_head": "Dia./Thread Size",
    "bolt_hex": "Dia./Thread Size",
    "nut_hex": "Thread Size",
    "tap_spiral_point": "Thread Size",
}
THREADED = SHARED_THREADED | {
    key: spec.threaded for key, spec in typespec.modelled().items() if spec.threaded
}


def test_no_threaded_row_names_a_type_with_its_own_module():
    """A row left behind would be overridden by the spec unseen. This file
    names the socket screw in tests of its own behaviour, so it is checked
    here rather than by ``test_type_registration``'s quoted-key scan."""
    assert sorted(SHARED_THREADED.keys() & typespec.modelled().keys()) == []


def _series(thread: str) -> str | None:
    dia, pitch = _split(thread)
    if dia.startswith("M"):
        if METRIC_COARSE.get(dia) == pitch:
            return "Metric Coarse"
        fine = METRIC_FINE.get(dia, set()) | SOLD_FINE.get(dia, set())
        return "Metric Fine" if pitch in fine else None
    if UNC.get(dia) == pitch:
        return "UNC"
    return "UNF" if UNF.get(dia) == pitch or pitch in SOLD_FINE.get(dia, ()) else None


def test_every_thread_is_a_real_designation_and_its_thread_type_says_which(docs):
    for doc in docs:
        name = THREADED.get(doc["product_type"])
        values = _published(doc)
        if name is None or name not in values:
            continue
        series = _series(values[name])
        assert series is not None, (doc["sku"], values[name])
        if "Thread Type" in values:
            assert values["Thread Type"] == series, (
                doc["sku"],
                values[name],
                values["Thread Type"],
            )


def test_a_diameter_query_has_a_pitch_to_choose(docs):
    """``m12 socket cap screws`` finds M12x1.75 AND a fine pitch, and so on for
    every threaded type -- the near-miss the pitch facet exists to separate."""
    for type_key, name in THREADED.items():
        series = {
            _series(_published(d)[name])
            for d in docs
            if d["product_type"] == type_key and name in _published(d)
        }  # noqa: E501
        assert {"Metric Coarse", "Metric Fine", "UNC", "UNF"} <= series, (type_key, series)
    m12 = {
        _published(d)["Dia./Thread Size"]
        for d in docs
        if d["product_type"] == "screw_socket_head"
        and _published(d).get("Dia./Thread Size", "").startswith("M12x")
    }
    assert m12 == {"M12x1.75", "M12x1.5", "M12x1.25"}, m12


def test_a_fine_pitch_metric_screw_claims_no_coarse_thread_standard(docs):
    for doc in docs:
        values = _published(doc)
        if doc["product_type"].startswith("screw_") and values.get("Thread Type") == "Metric Fine":
            assert "Meets/Exceeds" not in values, doc["sku"]
            assert "fine-pitch" in doc["dimension_provenance"], doc["sku"]


# --- lengths and drives are catalog values -------------------------------------


def test_a_countersunk_screw_publishes_no_length_under_head(docs):
    flat = [d for d in docs if d["product_type"] == "screw_flat_head"]
    assert flat
    assert all("Length under Head" not in _published(d) for d in flat)


def test_every_drive_size_is_a_nominal_key(docs):
    """A distributor prints the key, 10mm -- never the socket's toleranced 10.07mm."""
    keys_mm = set(compat.KEY_SERIES_MM)
    keys_in = set(compat.KEY_SERIES_IN)
    off = []
    for doc in docs:
        drive = _published(doc).get("Drive Size")
        if drive is None:
            continue
        inches = parse_length(drive).inches
        if drive.endswith("mm"):
            ok = any(abs(inches * MM - k) < 1e-3 for k in keys_mm)
        else:
            ok = any(abs(inches - k) < 1e-3 for k in keys_in)
        # The unit-mixing defect republishes a value in the other system
        # (5mm as 0.1969"); that is a modelled defect, not a nominal size.
        metric_thread = _published(doc).get("Dia./Thread Size", "").startswith("M")
        if not ok and drive.endswith("mm") == metric_thread:
            off.append((doc["sku"], drive))
    assert off == []
