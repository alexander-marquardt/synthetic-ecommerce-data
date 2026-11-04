"""Per-type gates for ``hand_files``, deepened from breadth (#836, slice 3).

The gates of ``test_type_lock_nuts_nylon_insert.py``, the template (#53 step 3):

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record says where its length came from;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed
  golden has it.

And this type's own: every length a record publishes is in the run its shape
stocks, its tooth type follows the maker's single or double cut rule, every
shape and cut is built, and the breadth row's lengths are still offered.
"""

from __future__ import annotations

import importlib
import json
from collections import Counter
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

KEY = "hand_files"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse back to the
#: breadth row's 2 SKUs, and is not a target.
DEFAULT_SKU_FLOOR = 40

#: The breadth row's ``size_values``, in inches: each must still be offered at the default size.
ROW_LENGTHS = (4.0, 6.0, 8.0, 10.0, 12.0)


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _module():
    """The type's module, read in the tests that need it: until it exists the
    first two gates red on their assertions, not on an import."""
    return importlib.import_module(
        "synthetic_ecommerce_data.domains.industrial.product_types.hand_tools." + KEY
    )


def _value(doc: dict, name: str) -> str:
    return next(a["value"] for a in authored_attributes(doc) if a["name"] == name)


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_the_type_keeps_the_breadth_rows_node():
    assert taxonomy.LEAVES[KEY] == (("Hand Tools", "Files & Rasps", "Hand Files"),)


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
    problems, checked = type_gates.provenance_problems(_default_docs(), (), ("Length",))
    assert problems == [], problems[:10]
    files = _module()
    assert {doc["dimension_provenance"] for doc in _default_docs()} == {files.PROVENANCE}


def test_every_length_is_in_the_run_its_shape_stocks():
    files = _module()
    shapes = {shape.name: shape for shape in files.SHAPES}
    for doc in _default_docs():
        shape = shapes[_value(doc, "Shape")]
        metric = "mm" in _value(doc, "Length")
        length = parse_length(_value(doc, "Length")).inches
        offered = files.lengths_in(shape, metric)
        assert any(abs(length - s) < 0.0006 for s in offered), (doc["sku"], shape.name, length)


def test_the_tooth_type_follows_the_makers_single_or_double_cut_rule():
    """All 4 in, 6 in and smooth files are single cut; bastard and second cut
    files longer than 6 in are double cut; a mill file is single cut."""
    docs = _default_docs()
    seen = Counter()
    for doc in docs:
        shape, cut = _value(doc, "Shape"), _value(doc, "Cut Type")
        length = parse_length(_value(doc, "Length")).inches
        single = shape == "Mill" or cut == "Smooth" or length < 6.5
        expected = "Single Cut" if single else "Double Cut"
        assert _value(doc, "Tooth Type") == expected, (doc["sku"], shape, cut, length)
        seen[expected] += 1
    assert seen["Single Cut"] and seen["Double Cut"], seen
    # The cases the default build may not reach: a long mill file, a long smooth one.
    tooth_type = _module().tooth_type
    assert tooth_type("Mill", "Bastard", 10.0) == "Single Cut"
    assert tooth_type("Flat", "Smooth", 12.0) == "Single Cut"
    assert tooth_type("Half Round", "Second", 6.0) == "Single Cut"
    assert tooth_type("Half Round", "Second", 8.0) == "Double Cut"
    assert tooth_type("Round", "Bastard", 300 / 25.4) == "Double Cut"


def test_every_shape_and_cut_is_built():
    docs = _default_docs()
    assert {_value(d, "Shape") for d in docs} == set(RUNS)
    assert {_value(d, "Cut Type") for d in docs} == {"Bastard", "Second", "Smooth"}
    assert {"mm" in _value(d, "Length") for d in docs} == {True, False}


#: Each shape's stocked lengths, inch (in) then metric (mm); the mill file is inch only.
RUNS = {
    "Flat": ((4, 6, 8, 10, 12, 14), (100, 150, 200, 250, 300)),
    "Hand": ((6, 8, 10, 12), (150, 200, 250, 300)),
    "Mill": ((4, 6, 8, 10, 12, 14), ()),
    "Half Round": ((4, 6, 8, 10, 12, 14), (100, 150, 200, 250, 300)),
    "Round": ((4, 6, 8, 10, 12), (100, 150, 200, 250)),
    "Square": ((4, 6, 8, 10, 12), (100, 150, 200, 250)),
    "Three Square": ((4, 6, 8, 10), (100, 150, 200)),
}


def test_each_shape_stocks_its_own_run_of_lengths():
    files = _module()
    built = {}
    for shape in files.SHAPES:
        inch = tuple(round(length) for length in files.lengths_in(shape, False))
        mm = () if shape.mm is None else tuple(
            round(length * 25.4) for length in files.lengths_in(shape, True)
        )
        built[shape.name] = (inch, mm)
    assert built == RUNS
    assert not any(system == "mm" and shape.name == "Mill" for shape, _, system in files.COMBOS)


def test_the_breadth_rows_lengths_are_still_offered():
    counts = Counter(
        round(parse_length(_value(doc, "Length")).inches, 3)
        for doc in _default_docs()
        if "mm" not in _value(doc, "Length")
    )
    assert [length for length in ROW_LENGTHS if not counts[length]] == []


def test_every_title_names_the_lines_own_shape():
    """"Hand" is a shape: a flat file titled "Hand File" names the wrong one (#846)."""
    wrong = [
        (doc["product_id"], doc[field])
        for doc in _default_docs()
        for field in ("title", "parent_title")
        if f"{_value(doc, 'Shape')} File" not in doc[field]
    ]
    assert wrong == []


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_hand_files.py``."""
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
