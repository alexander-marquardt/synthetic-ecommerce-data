"""Per-type gates for ``roll_pins``, deepened from breadth (#829).

Copied from the double-end stud's gate file; each gate is about this type alone:

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record says which table its diameter was read from, and
  never that no standard fixes a value it claims a standard for;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed golden
  has it.

And this type's own: a metric pin's diameter is a row of its ISO table and its
length a nominal length inside that row's range; an inch pin's diameter is a
row of the ASME B18.8.2 table and its length a stocked one between
:data:`MIN_OVER_DIAMETER` and :data:`MAX_OVER_DIAMETER` diameters; both kinds
(slotted and coiled) are built, and the breadth row's sizes are all offered.
"""

from __future__ import annotations

import importlib
import json
import re
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

KEY = "roll_pins"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse back to the
#: breadth row's 2 SKUs, and is not a target.
DEFAULT_SKU_FLOOR = 40

#: The dimensional standards a line claims, and the dimensions it publishes.
DIMENSIONAL = {"ASME B18.8.2", "ISO 8752", "ISO 13337", "ISO 8750", "ISO 8748"}
DIMENSIONS = ("Pin Dia.", "Length")

#: The breadth row's size_values: each must be offered at the default build.
BREADTH_SIZES = ("1/8", "3/16", "1/4", "3/8")

#: An inch pin's stocked length, in diameters of the pin.
MIN_OVER_DIAMETER = 2
MAX_OVER_DIAMETER = 20

MM = 25.4

_TABLE = re.compile(r"Pin Dia\.(?: and Length)? read from the (ASME B18\.8\.2|ISO \d+) table")


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
    assert found, f"{doc['sku']} names no diameter table: {doc['dimension_provenance']!r}"
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
    for doc in docs:
        _table(doc)


def test_every_metric_pin_is_a_row_and_a_length_of_its_iso_table():
    module = _module()
    stray = []
    for doc in _default_docs():
        standard = _table(doc)
        if standard == module.B18_8_2:
            continue
        rows = {row.d: row for row in module.METRIC_TABLES[standard]}
        d = round(_inches(doc, "Pin Dia.") * MM, 3)
        length = round(_inches(doc, "Length") * MM, 3)
        row = rows.get(d)
        if row is None or length not in module.ISO_LENGTHS or not row.min_l <= length <= row.max_l:
            stray.append((doc["sku"], standard, d, length))
    assert not stray, stray[:5]


def test_every_inch_pin_is_a_row_of_the_asme_table_on_a_stocked_length():
    module = _module()
    sizes = {float(Fraction(row.size)) for row in module.B18_8_2_ROWS}
    stocked = {float(v) for v in module.INCH_LENGTHS}
    stray = []
    for doc in _default_docs():
        if _table(doc) != module.B18_8_2:
            continue
        d, length = _inches(doc, "Pin Dia."), _inches(doc, "Length")
        within = MIN_OVER_DIAMETER * d - 1e-9 <= length <= MAX_OVER_DIAMETER * d + 1e-9
        if d not in sizes or length not in stocked or not within:
            stray.append((doc["sku"], _value(doc, "Pin Dia."), _value(doc, "Length")))
    assert not stray, stray[:5]


def test_every_breadth_size_is_offered_at_the_default_build():
    built = {
        str(Fraction(_inches(d, "Pin Dia.")).limit_denominator(64))
        for d in _default_docs()
        if _table(d) == _module().B18_8_2
    }
    assert set(BREADTH_SIZES) <= built, sorted(set(BREADTH_SIZES) - built)


def test_every_table_and_both_kinds_are_built_at_the_default_build():
    module = _module()
    docs = _default_docs()
    assert {_table(d) for d in docs} == set(module.SERIES), sorted({_table(d) for d in docs})
    published = (a for d in docs for a in authored_attributes(d))
    built = {a["value"] for a in published if a["name"] == "Type"}
    assert built == set(module.KINDS), sorted(built)


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_roll_pins.py``."""
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
