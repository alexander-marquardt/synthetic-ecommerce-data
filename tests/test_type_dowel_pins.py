"""Per-type gates for ``dowel_pins``, deepened from breadth (#53).

The template is ``tests/test_type_lock_nuts_nylon_insert.py``: uniqueness,
census conformance, provenance, byte-determinism under two hash seeds, a golden
slice, and independence from every other type. On top of it, each value the
type publishes is held to the standards' tables, restated here from the
sources rather than read from the module, so a table typed wrong in the
module goes red:

* ISO 2338 and ISO 8734 Table 1 (FreeCAD_FastenersWB ``iso2338def.csv`` and
  ``iso8734def.csv`` at ``fddd07af``) and Table 2 (the 1997 preview PDFs);
* ASME B18.8.2 hardened ground machine dowel pins, as the Engineers Edge
  reproduction of its table gives them.

Every byte comparison goes through :mod:`type_gates`, which compares digests
and then names the first differing SKU, so a red reports in seconds.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import type_gates
from published import published_attributes
from synthetic_industrial_products.catalog import emit, names, taxonomy, typespec
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate, generate_type
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "dowel_pins"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to ten (a hundred
#: would be 0 at this type's share): a floor that catches a collapse back to
#: the breadth row's two SKUs, not a target.
DEFAULT_SKU_FLOOR = 40

#: The dimensional standards this type's lines claim, and the dimensions it publishes.
DIMENSIONAL = {"ISO 2338", "ISO 8734", "ASME B18.8.2"}
DIMENSIONS = ("Dowel Dia.", "Length", "Dia. Tolerance")

#: A build large enough to reach every diameter of every table.
LARGE_LINES = 39000

MM = 25.4

# --- the standards' tables, restated from the sources, not from the module ---

#: ISO 2338 Table 1: d -> (shortest l, longest l), mm. 30, 40 and 50 mm are
#: left out of the catalog.
ISO_2338_RANGE = {
    0.6: (2, 6), 0.8: (2, 8), 1: (4, 10), 1.2: (4, 12), 1.5: (4, 16), 2: (6, 20),
    2.5: (6, 24), 3: (8, 30), 4: (8, 40), 5: (10, 50), 6: (12, 60), 8: (14, 80),
    10: (18, 95), 12: (22, 140), 16: (26, 180), 20: (35, 200), 25: (50, 200),
}  # fmt: skip
#: ISO 8734 Table 1: the same, mm.
ISO_8734_RANGE = {
    1: (3, 10), 1.5: (4, 16), 2: (5, 20), 2.5: (6, 24), 3: (8, 30), 4: (10, 40),
    5: (12, 50), 6: (14, 60), 8: (18, 80), 10: (22, 100), 12: (26, 100), 16: (40, 100),
    20: (50, 100),
}  # fmt: skip
#: Both tables' nominal lengths, mm (ISO 8734's stops at 100).
ISO_LENGTHS = {
    2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 35, 40, 45, 50,
    55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 120, 140, 160, 180, 200,
}  # fmt: skip
#: Table 2, per standard: (Type, Material) -> (Hardness, the finishes allowed).
ISO_GRADES = {
    "ISO 2338": {
        ("Unhardened", "Steel"): ("125-245 HV30", {"Plain", "Black Oxide", "Zinc Plated"}),
        ("Unhardened", "18-8 Stainless Steel"): ("210-280 HV30", {"Plain"}),
    },
    "ISO 8734": {
        ("Through Hardened", "Steel"): ("550-650 HV30", {"Plain"}),
        ("Case Hardened", "Steel"): ("600-700 HV1 (surface)", {"Plain"}),
        ("Hardened", "Stainless Steel"): ("460-560 HV30", {"Plain"}),
    },
}
#: ASME B18.8.2: each offered size's preferred lengths, inches, every step listed.
B18_8_2_LENGTHS = {
    size: {Fraction(v) for v in lengths.split()}
    for size, lengths in {
        "1/16": "3/16 1/4 5/16 3/8 1/2 5/8 3/4",
        "3/32": "5/16 3/8 1/2 5/8 3/4 7/8 1",
        "1/8": "3/8 1/2 5/8 3/4 7/8 1 5/4 3/2 7/4 2",
        "3/16": "1/2 5/8 3/4 7/8 1 5/4 3/2 7/4 2",
        "1/4": "1/2 5/8 3/4 7/8 1 5/4 3/2 7/4 2 9/4 5/2",
        "5/16": "1/2 5/8 3/4 7/8 1 5/4 3/2 7/4 2 9/4 5/2",
        "3/8": "1/2 5/8 3/4 7/8 1 5/4 3/2 7/4 2 9/4 5/2 3",
        "7/16": "7/8 1 5/4 3/2 7/4 2 9/4 5/2 3",
        "1/2": "3/4 1 5/4 3/2 7/4 2 9/4 5/2 3 7/2 4",
        "5/8": "5/4 3/2 7/4 2 9/4 5/2 3 7/2 4 9/2 5",
        "3/4": "3/2 7/4 2 9/4 5/2 3 7/2 4 9/2 5 11/2 6",
        "7/8": "2 5/2 3 7/2 4 9/2 5 11/2 6",
        "1": "2 5/2 3 7/2 4 9/2 5 6",
    }.items()
}
#: B18.8.2's pin diameter A over the nominal size, min to max, per series.
B18_8_2_TOLERANCES = {'+0.0001" to +0.0003"', '+0.0009" to +0.0011"'}
#: The sizes the breadth row offered, which the default build must still reach.
BREADTH_SIZES = ("1/8", "3/16", "1/4", "3/8", "1/2")


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _clean_docs(lines: int | None = None) -> list[dict]:
    """The type's documents with no injected defect, so each value is the builder's."""
    config = GeneratorConfig(defect_scale=0.0, **({"lines": lines} if lines else {}))
    catalog = generate(config, types=[KEY])
    return [doc for line in catalog.lines for doc in emit.flat_documents(catalog, line)]


def _values(doc: dict) -> dict[str, dict]:
    return {a["name"]: a for a in doc["attributes"]}


def _mm(attribute: dict) -> float:
    """``value_canonical`` is millimetres whatever unit the value is written in."""
    return float(attribute["value_canonical"])


def _inch_size(doc: dict) -> str:
    """The B18.8.2 nominal size a record's diameter is, as the table writes it."""
    inches = Fraction(_mm(_values(doc)["Dowel Dia."]) / MM).limit_denominator(64)
    return str(inches)


def _standard(doc: dict) -> str:
    """The table a record's dimensions were read from, as its provenance names it."""
    (standard,) = [
        s for s in sorted(DIMENSIONAL) if f"the {s} table" in doc["dimension_provenance"]
    ]
    return standard


@pytest.fixture(scope="module")
def clean_docs() -> list[dict]:
    return _clean_docs()


@pytest.fixture(scope="module")
def large_docs() -> list[dict]:
    return _clean_docs(LARGE_LINES)


# --- the template's gates ---------------------------------------------------------


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert same_product_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in published_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_published_dimension_came_from():
    problems, checked = type_gates.provenance_problems(_default_docs(), DIMENSIONAL, DIMENSIONS)
    assert problems == [], problems[:10]
    assert checked > 20, f"only {checked} dimensional claims were checked"


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_dowel_pins.py``."""
    assert SLICE.is_file(), f"no golden slice at {SLICE}"
    committed = SLICE.read_text(encoding="utf-8").splitlines()
    report = type_gates.difference(committed, type_gates.default_records(KEY))
    if report:
        pytest.fail(f"{SLICE.name} is not a fresh build: {report}")


def test_every_other_type_is_byte_identical_with_this_type_left_out():
    moved = _moved_by_removing(KEY)
    assert not moved, f"building {KEY} changed {moved[:8]}"


def test_every_other_type_builds_as_the_committed_golden_has_it():
    report = type_gates.others_moved_from_the_golden(KEY)
    if report:
        pytest.fail(report)


def test_the_whole_build_carries_exactly_this_types_own_build():
    whole = _by_type(generate().lines)
    alone = _by_type(generate_type(GeneratorConfig(), KEY))
    assert whole[KEY] == alone[KEY]


# --- the type's values against the standards' tables -------------------------------


def test_every_standard_is_built_and_the_breadth_rows_sizes_survive(clean_docs):
    assert {_standard(doc) for doc in clean_docs} == DIMENSIONAL
    inch = {_inch_size(doc) for doc in clean_docs if _standard(doc) == "ASME B18.8.2"}
    assert sorted(set(BREADTH_SIZES) - inch) == []


def test_every_diameter_of_every_table_reaches_a_document(large_docs):
    built: dict[str, set] = {standard: set() for standard in DIMENSIONAL}
    for doc in large_docs:
        standard = _standard(doc)
        if standard == "ASME B18.8.2":
            built[standard].add(_inch_size(doc))
        else:
            built[standard].add(round(_mm(_values(doc)["Dowel Dia."]), 3))
    assert built["ISO 2338"] == {float(d) for d in ISO_2338_RANGE}
    assert built["ISO 8734"] == {float(d) for d in ISO_8734_RANGE}
    assert built["ASME B18.8.2"] == set(B18_8_2_LENGTHS)


def test_every_metric_length_is_a_nominal_length_inside_its_tables_range(large_docs):
    outside = []
    checked = 0
    for doc in large_docs:
        standard = _standard(doc)
        if standard == "ASME B18.8.2":
            continue
        values = _values(doc)
        d = round(_mm(values["Dowel Dia."]), 3)
        length = round(_mm(values["Length"]), 3)
        low, high = (ISO_2338_RANGE if standard == "ISO 2338" else ISO_8734_RANGE)[d]
        checked += 1
        if length not in ISO_LENGTHS or not low <= length <= high:
            outside.append(f"{standard} {d:g} x {length:g}mm")
    assert checked > 300, f"only {checked} metric SKUs were checked"
    assert outside == [], f"{len(outside)} SKUs outside Table 1, e.g. {sorted(set(outside))[:6]}"


def test_every_inch_length_is_one_of_its_sizes_preferred_lengths(large_docs):
    outside = []
    checked = 0
    for doc in large_docs:
        if _standard(doc) != "ASME B18.8.2":
            continue
        size = _inch_size(doc)
        length = Fraction(_mm(_values(doc)["Length"]) / MM).limit_denominator(64)
        checked += 1
        if length not in B18_8_2_LENGTHS[size]:
            outside.append(f"{size} x {length}")
    assert checked > 300, f"only {checked} inch SKUs were checked"
    assert outside == [], f"{len(outside)} SKUs off the table, e.g. {sorted(set(outside))[:6]}"


def test_each_lines_grade_tolerance_and_finish_are_its_standards(large_docs):
    wrong = []
    for doc in large_docs:
        standard = _standard(doc)
        values = {name: a["value"] for name, a in _values(doc).items()}
        if standard == "ASME B18.8.2":
            got = (values["Type"], values["Material"], values["Dia. Tolerance"])
            ok = got[:2] == ("Hardened Ground", "Steel") and got[2] in B18_8_2_TOLERANCES
            ok = ok and "Finish" not in values and "Hardness" not in values
            ok = ok and values.get("Rockwell Hardness", "Rockwell C60 min. (surface)") == (
                "Rockwell C60 min. (surface)"
            )
        else:
            grade = ISO_GRADES[standard].get((values["Type"], values["Material"]))
            allowed = {"ISO 2338": {"m6", "h8"}, "ISO 8734": {"m6"}}[standard]
            hardness, finishes = grade or ("", set())
            ok = grade is not None and values["Dia. Tolerance"] in allowed
            # Hardness and Finish are sparse: absent is not wrong, a wrong value is.
            ok = ok and values.get("Hardness", hardness) == hardness
            ok = ok and values.get("Finish", "Plain") in finishes
            ok = ok and "Rockwell Hardness" not in values
        if not ok:
            wrong.append(f"{standard}: {values}")
    assert wrong == [], f"{len(wrong)} wrong, e.g. {wrong[:3]}"


def test_no_pack_quantity_is_published(clean_docs):
    names_published = {a["name"] for doc in clean_docs for a in doc["attributes"]}
    assert {n for n in names_published if "Quantity" in n or "Pack" in n} == set()


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
