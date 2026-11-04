"""Per-type gates for ``er_collets``, deepened from breadth (#831).

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

And this type's own: every collet a record publishes is a row of the ER collet
table for its series and unit system, with that row's clamping range, its
series' outside diameter and length, and its class's runout.
"""

from __future__ import annotations

import collections
import importlib
import json
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

KEY = "er_collets"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's 62 SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse back to the
#: breadth row's 2 SKUs, and is not a target.
DEFAULT_SKU_FLOOR = 40

#: The breadth row's ``size_values``: each must still be built at the default size.
BREADTH_SIZES = ('1/8"', '3/16"', '1/4"', '3/8"', '1/2"')


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
    er = _module()
    problems, checked = type_gates.provenance_problems(_default_docs(), er.STANDARDS, er.DIMENSIONS)
    assert problems == [], problems[:10]
    assert checked, "no record claims ISO 15488 or DIN 6499"


#: How far a published dimension may sit from its row's: the 0.005 mm a
#: unit-mixing defect's 2-place mm spelling rounds an inch value by.
TOLERANCE_IN = 0.0002


def test_every_collet_is_a_row_of_its_series_table():
    """The size, clamping range, outside diameter, length and runout a record
    publishes are the table's for its series, unit system and class. A
    dimension is compared by its magnitude: a unit-mixing defect re-spells one
    in the other unit (``defects.py``)."""
    er = _module()
    docs = _default_docs()
    for doc in docs:
        values = _values(doc)
        size = parse_length(values["Size"]).inches
        row = er.row_of(values["Type"], True, size) or er.row_of(values["Type"], False, size)
        assert row is not None, (doc["sku"], values["Type"], values["Size"])
        expected = er.published(row, values["Class"])
        if "Grip Range" in values:
            assert values["Grip Range"] == expected["Grip Range"], doc["sku"]
        d1_mm, _ = er.SERIES[row[0]]
        lengths = {
            "Concentricity Tolerance": parse_length(expected["Concentricity Tolerance"]).inches,
            "Outside Diameter": d1_mm / 25.4,
            "Overall Length": er.length_mm(row) / 25.4,
        }
        for name, inches in lengths.items():
            if name in values:
                published = parse_length(values[name]).inches
                assert abs(published - inches) <= TOLERANCE_IN, (doc["sku"], name, values[name])


def test_every_series_and_class_is_built_and_the_breadth_sizes_survive():
    docs = _default_docs()
    er = _module()
    built = {(_values(doc)["Type"], _values(doc)["Class"]) for doc in docs}
    assert {series for series, _ in built} == {er.published_series(s) for s in er.SERIES}
    assert {cls for _, cls in built} == set(er.CLASSES)
    sizes = collections.Counter(_values(doc)["Size"] for doc in docs)
    assert all(sizes[size] for size in BREADTH_SIZES), {s: sizes[s] for s in BREADTH_SIZES}


def test_a_collet_grips_one_collapse_below_its_nominal():
    """ER 8 and ER 11 collapse 0.5 mm, as do the 1 and 1.5 mm collets of ER 16
    to ER 25; the rest of ER 16 to ER 40 collapse 1 mm, and ER 50 2 mm."""
    er = _module()
    collapse = {"ER 8": 0.5, "ER 11": 0.5, "ER 50": 2.0}
    for row in er.TABLE.rows:
        series, _, system, max_mm, min_mm, *_ = row
        if system == "mm":
            expected = 0.5 if max_mm < 2.0 else collapse.get(series, 1.0)
            assert max_mm - min_mm == pytest.approx(expected), row


def test_the_runout_rows_cover_every_collet_and_never_tighten_with_size():
    er = _module()
    bores = [row[3] for row in er.TABLE.rows]
    assert er.din_runout_mm(min(bores)) == 0.015
    assert er.din_runout_mm(max(bores)) == 0.025
    ordered = sorted(bores)
    assert [er.din_runout_mm(b) for b in ordered] == sorted(er.din_runout_mm(b) for b in ordered)


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_er_collets.py``."""
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
