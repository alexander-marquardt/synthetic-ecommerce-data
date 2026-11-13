"""Per-type gates for ``flange_nuts``, deepened from breadth (#829).

Copied from the carriage bolt's gate file; each gate is about this type alone:

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record says which table its dimensions were read from, and
  never that no standard fixes a value it claims a standard for;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed golden
  has it.

And this type's own: a metric nut's thread, width across flats, flange
diameter and height are a row of the ISO 4161 table; an inch nut's are a row
of the ASME B18.2.2 hex flange nut table; each table's own pitch is the thread
table's; both tables and both flanges (serrated and plain) are built, and the
breadth row's sizes are all offered.
"""

from __future__ import annotations

import importlib
import json
import re
from pathlib import Path

import pytest

import type_gates
from published import authored_attributes
from synthetic_ecommerce_data.core import price, typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.dimensions import parse_length, parse_thread
from synthetic_ecommerce_data.domains.industrial import names, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import unexplained_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "flange_nuts"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse back to the
#: breadth row's 1 SKU, and is not a target.
DEFAULT_SKU_FLOOR = 30

#: The dimensional standards a line claims, and the dimensions it publishes.
ASME = "ASME B18.2.2"
ISO = "ISO 4161"
DIMENSIONAL = {ASME, ISO}
NUT = ("Width Across Flats", "Flange Dia.", "Height")
DIMENSIONS = ("Thread Size", *NUT)

#: The breadth row's size_values: each must be offered at the default build.
BREADTH_SIZES = ("1/4-20", "5/16-18", "3/8-16", "M8x1.25", "M10x1.5")

#: Both flanges a distributor stocks a flange nut with.
STYLES = {"Serrated Flange", "Plain Flange"}

MM = 25.4

_TABLE = re.compile(r"Width Across Flats[^;]*read from the (ASME B18\.2\.2|ISO 4161) table")


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _module():
    """The type's module, read in the tests that need it: until it exists the
    first two gates red on their assertions, not on an import."""
    return importlib.import_module(
        "synthetic_ecommerce_data.domains.industrial.product_types.fasteners." + KEY
    )


def _value(doc: dict, name: str) -> str:
    return next(a["value"] for a in authored_attributes(doc) if a["name"] == name)


def _table(doc: dict) -> str:
    found = _TABLE.search(doc["dimension_provenance"])
    assert found, f"{doc['sku']} names no nut table: {doc['dimension_provenance']!r}"
    return found.group(1)


def _inches(doc: dict, name: str) -> float:
    return parse_length(_value(doc, name)).inches


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert unexplained_duplicates(docs, share=0.02) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in authored_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_published_dimension_came_from():
    docs = _default_docs()
    problems, _ = type_gates.provenance_problems(docs, DIMENSIONAL, DIMENSIONS)
    assert problems == [], problems[:10]
    # The table named is the thread's own: a metric thread is ISO 4161's.
    wrong = [
        doc["sku"]
        for doc in docs
        if (_table(doc) == ISO) != _value(doc, "Thread Size").startswith("M")
    ]
    assert wrong == [], wrong[:5]


def test_each_nut_tables_pitch_is_the_thread_tables():
    """The thread is read from ASME B1.1 and ISO 262 (#73); the nut tables
    carry their own pitch, and the two agree on every row."""
    module = _module()
    for row in module.ASME_ROWS:
        assert parse_thread(module.inch_thread(row)).tpi == pytest.approx(row.tpi), row
    for row in module.ISO_4161_ROWS:
        assert parse_thread(module.metric_thread(row)).pitch_in * MM == pytest.approx(row.p), row


def test_every_metric_nut_is_a_row_of_the_iso_table():
    module = _module()
    rows = {row.d: row for row in module.ISO_4161_ROWS}
    stray = []
    for doc in _default_docs():
        if _table(doc) != ISO:
            continue
        thread = parse_thread(_value(doc, "Thread Size"))
        # To the table's own precision: a feed that writes a metric nut in
        # decimal inches reads back a hair off the millimetre.
        d = round(thread.major.inches * MM)
        nut = tuple(round(_inches(doc, name) * MM, 1) for name in NUT)
        row = rows.get(d)
        if (
            row is None
            or round(thread.pitch_in * MM, 2) != row.p
            or nut != (row.s, row.dc, row.m)
        ):
            stray.append((doc["sku"], d, nut))
    assert not stray, stray[:5]


def test_every_inch_nut_is_a_row_of_the_asme_table():
    module = _module()
    rows = {module.inch_thread(row): row for row in module.ASME_ROWS}
    stray = []
    for doc in _default_docs():
        if _table(doc) != ASME:
            continue
        row = rows.get(_value(doc, "Thread Size"))
        nut = [_inches(doc, name) for name in NUT]
        if row is None or any(
            abs(got - want) > 1e-3 for got, want in zip(nut, (row.f, row.b, row.h), strict=True)
        ):
            stray.append((doc["sku"], _value(doc, "Thread Size"), nut))
    assert not stray, stray[:5]


def test_every_breadth_size_is_offered_at_the_default_build():
    built = {_value(d, "Thread Size") for d in _default_docs()}
    assert set(BREADTH_SIZES) <= built, sorted(set(BREADTH_SIZES) - built)


def test_both_tables_are_built_at_the_default_build():
    assert {_table(d) for d in _default_docs()} == DIMENSIONAL


def test_both_flanges_are_built_in_each_table():
    built = {(_table(d), _value(d, "Nut Style")) for d in _default_docs()}
    assert built == {(table, style) for table in DIMENSIONAL for style in STYLES}, sorted(built)


def test_the_price_is_marked_generated():
    """The census has no flange nuts (neither ``deep_types`` nor
    ``breadth_categories``), so no row may score the hand-set model."""
    assert KEY not in price.DEEPENED_CENSUS
    assert not price.model_for(KEY).measured


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_flange_nuts.py``."""
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
