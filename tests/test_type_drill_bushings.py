"""Per-type gates for ``drill_bushings``, deepened from breadth (#831).

The gates of ``test_type_lock_nuts_nylon_insert.py``, the template (#53 step 3):

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record says which table its dimensions were read from;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed
  golden has it.

And this type's own: every bushing a record publishes is a row of the ASME
B94.33 table for its type and body, at one of that row's lengths, and a drill
bushing's hole is a drill size inside the row's bore range.
"""

from __future__ import annotations

import collections
import importlib
import json
from fractions import Fraction
from pathlib import Path

import pytest

import type_gates
from published import authored_attributes
from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.dimensions import parse_length
from synthetic_ecommerce_data.domains.industrial import names, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import unexplained_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "drill_bushings"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's 72 SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse back to the
#: breadth row's 2 SKUs, and is not a target.
DEFAULT_SKU_FLOOR = 40

#: The breadth row's ``size_values``: each must still be built at the default size.
BREADTH_SIZES = ('1/8"', '3/16"', '1/4"', '3/8"', '1/2"')

#: How far a published length may sit from its row's: the 0.005 mm a
#: unit-mixing defect's 2-place mm spelling rounds an inch value by.
TOLERANCE_IN = 0.0002


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _module():
    """The type's module, read in the tests that need it: until it exists the
    first two gates red on their assertions, not on an import."""
    return importlib.import_module(
        "synthetic_ecommerce_data.domains.industrial.product_types.cutting_tools." + KEY
    )


def _values(doc: dict) -> dict[str, str]:
    return {a["name"]: a["value"] for a in authored_attributes(doc)}


def _inches(text: str) -> float:
    return float(sum(Fraction(part) for part in text.split()))


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert unexplained_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in authored_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_published_dimension_came_from():
    bushings = _module()
    problems, checked = type_gates.provenance_problems(
        _default_docs(), bushings.STANDARDS, bushings.DIMENSIONS
    )
    assert problems == [], problems[:10]
    assert checked, "no record claims ASME B94.33"


def test_every_bushing_is_a_row_of_its_type_table():
    """The ANSI number a record publishes names a row of its type's table at
    one of the row's lengths, and its outside diameter, length, head and size
    are that row's. A drill bushing's size is a drill size inside the row's
    bore range; a liner's is the row's inside diameter. A dimension is
    compared by its magnitude: a unit-mixing defect re-spells one in the other
    unit (``defects.py``)."""
    bushings = _module()
    for doc in _default_docs():
        values = _values(doc)
        size = parse_length(values["Size"]).inches
        row, length = bushings.row_of(values["ANSI Number"], size)
        assert row is not None, (doc["sku"], values["ANSI Number"], values["Size"])
        assert (values["Type"], values["Head Type"]) == bushings.TYPES[row["type"]]
        expected = {
            "Outside Dia.": _inches(row["od_nominal"]),
            bushings.length_name(row): length / 16,
        }
        if "head_dia" in row:
            expected["Head Dia."] = _inches(row["head_dia"])
            expected["Head Height"] = _inches(row["head_thickness"])
        if bushings.is_liner(row):
            expected["Size"] = _inches(row["id_nominal"])
        else:
            assert row["bore_min_in"] - 0.0001 <= size <= row["bore_max_in"] + 0.0001, doc["sku"]
            drill, inches = bushings.hole_of(values["Drill Size"])
            assert abs(inches - size) <= TOLERANCE_IN, (doc["sku"], values["Drill Size"])
        for name, inches in expected.items():
            if name in values:
                published = parse_length(values[name]).inches
                assert abs(published - inches) <= TOLERANCE_IN, (doc["sku"], name, values[name])


def test_every_type_is_built_and_the_breadth_sizes_survive():
    docs = _default_docs()
    bushings = _module()
    built = {(_values(doc)["Type"], _values(doc)["Head Type"]) for doc in docs}
    assert built == set(bushings.TYPES.values())
    sizes = collections.Counter(_values(doc)["Size"] for doc in docs)
    assert all(sizes[size] for size in BREADTH_SIZES), {s: sizes[s] for s in BREADTH_SIZES}


def test_the_bore_ranges_of_one_body_never_overlap():
    """A body's rows split its bore range by counterbore class; two rows of
    one type and body share no hole, so a hole has one row."""
    bushings = _module()
    ranges = collections.defaultdict(list)
    for row in bushings.ROWS:
        if not bushings.is_liner(row):
            ranges[(row["type"], row["body"])].append((row["bore_min_in"], row["bore_max_in"]))
    for key, spans in ranges.items():
        spans.sort()
        for (_, high), (low, _) in zip(spans, spans[1:], strict=False):
            assert high < low, key


def test_a_press_fit_body_is_ground_over_its_nominal_and_a_slip_fit_under_it():
    """A press-fit and a liner body are ground over nominal to press into the
    plate; a renewable body is ground under nominal to slip into its liner.
    The one printed exception is the catalogue's SF-88 minimum, kept as
    printed and never published (``OD_AS_PRINTED``)."""
    bushings = _module()
    for row in bushings.ROWS:
        nominal = _inches(row["od_nominal"])
        label = f"{row['type']}-{row['body']}"
        if label in bushings.OD_AS_PRINTED:
            continue
        assert row["od_min_in"] < row["od_max_in"], label
        if row["type"] == "SF":
            assert row["od_max_in"] <= nominal, label
        else:
            assert row["od_min_in"] > nominal, label


def test_a_body_number_is_its_outside_diameter_in_sixty_fourths():
    """B94.33 numbers a bushing by its body: ``P-48`` is 48/64 = 3/4", and
    ``HL-176`` is 2-3/4". A row whose number and diameter disagree was misread."""
    bushings = _module()
    for row in bushings.ROWS:
        assert row["body"] == round(_inches(row["od_nominal"]) * 64), row


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_drill_bushings.py``."""
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


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
