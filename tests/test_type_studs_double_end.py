"""Per-type gates for ``studs_double_end``, deepened from breadth (#829).

Copied from the threaded rod's gate file; each gate is about this type alone:

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record says which table its thread was read from, and
  never that no standard fixes a value it claims a standard for;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed golden
  has it.

And this type's own: every thread a record publishes is a row of the thread
table its line reads, on a stud at least :data:`LENGTH_OVER_DIAMETER` times
its diameter long, both kinds (equal threads and tap end) are built, and the
breadth row's sizes are all offered.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

import type_gates
from published import authored_attributes
from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.dimensions import parse_length, parse_thread
from synthetic_ecommerce_data.domains.industrial import names, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import unexplained_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "studs_double_end"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's 71 SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse back to the
#: breadth row's 2 SKUs, and is not a target.
DEFAULT_SKU_FLOOR = 40

#: The dimensional standards this type's lines claim (none: ASME B18.31.2 was
#: not read) and the dimensions it publishes.
DIMENSIONAL: set[str] = set()
DIMENSIONS = ("Length",)
#: The tables a record's Thread Size is read from: ASME B1.1 (inch) or ISO 262 (metric).
THREAD_TABLES = ("ASME B1.1", "ISO 262")

#: The breadth row's size_values: each must be offered at the default build.
BREADTH_SIZES = ("1/4-20", "5/16-18", "3/8-16", "7/16-14", "M8x1.25", "M10x1.5")

#: The shortest stud a diameter is stocked on, in diameters.
LENGTH_OVER_DIAMETER = 4


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
    unread = [
        d["sku"] for d in docs if not any(t in d["dimension_provenance"] for t in THREAD_TABLES)
    ]
    assert not unread, f"{len(unread)} records name no thread table, e.g. {unread[:3]}"


def test_every_thread_is_a_row_of_its_series_table():
    module = _module()
    offered = {thread for series, _ in module.SERIES for rows in series.ranges for thread in rows}
    docs = _default_docs()
    stray = sorted({_value(d, "Thread Size") for d in docs} - offered)
    assert not stray, f"threads no series table offers: {stray}"


def test_no_stud_is_shorter_than_four_diameters():
    short = []
    for doc in _default_docs():
        major = parse_thread(_value(doc, "Thread Size")).major.inches
        length = parse_length(_value(doc, "Length")).inches
        if length < LENGTH_OVER_DIAMETER * major - 1e-9:
            short.append((doc["sku"], _value(doc, "Thread Size"), _value(doc, "Length")))
    assert not short, short[:5]


def test_every_breadth_size_is_offered_at_the_default_build():
    built = {_value(d, "Thread Size") for d in _default_docs()}
    assert set(BREADTH_SIZES) <= built, sorted(set(BREADTH_SIZES) - built)


def test_both_kinds_are_built_at_the_default_build():
    """``Type`` is sparse (``VOCAB``), so only the records that publish it are read."""
    published = (a for d in _default_docs() for a in authored_attributes(d))
    built = {a["value"] for a in published if a["name"] == "Type"}
    assert built == set(_module().KINDS), sorted(built)


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_studs_double_end.py``."""
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
