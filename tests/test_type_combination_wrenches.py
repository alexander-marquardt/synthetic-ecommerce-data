"""Per-type gates for ``combination_wrenches``, deepened from breadth (#836, slice 2).

The gates of ``test_type_lock_nuts_nylon_insert.py``, the template (#53 step 3):

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record says which table its size was read from;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed
  golden has it.

And this type's own: every size a record publishes is the width across flats
of a hex nut or hex screw table, inside the run its kind stocks, and the
breadth row's sizes are still offered.
"""

from __future__ import annotations

import importlib
import json
from collections import Counter
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

KEY = "combination_wrenches"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse back to the
#: breadth row's 2 SKUs, and is not a target.
DEFAULT_SKU_FLOOR = 50

#: The breadth row's ``size_values``: each must still be offered at the default size.
ROW_SIZES = ("1/4", "5/16", "3/8", "7/16", "1/2", "9/16", "5/8", "3/4")


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


def test_the_type_keeps_the_node_675_moved_its_row_under():
    assert taxonomy.LEAVES[KEY] == (("Hand Tools", "Wrenches & Keys", "Combination Wrenches"),)


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
    problems, checked = type_gates.provenance_problems(_default_docs(), (), ("Size",))
    assert problems == [], problems[:10]
    wrenches = _module()
    for doc in _default_docs():
        metric = "mm" in _value(doc, "Size")
        size = parse_length(_value(doc, "Size")).inches
        standard = wrenches.flats_standard(size, metric)
        assert f"the {standard} table" in doc["dimension_provenance"], doc["sku"]


def test_every_size_is_a_hex_width_across_flats_its_kind_stocks():
    """A size is a hex nut's or hex screw's width across flats, in the run
    the line's kind (its Type, points and finish) stocks."""
    wrenches = _module()
    docs = _default_docs()
    kinds = {(k.type, k.points, k.finish): k for k in wrenches.KINDS}
    for doc in docs:
        kind = kinds[(_value(doc, "Type"), _value(doc, "Number of Points"), _value(doc, "Finish"))]
        metric = "mm" in _value(doc, "Size")
        size = parse_length(_value(doc, "Size")).inches
        offered = wrenches.sizes_in(kind, metric)
        assert any(abs(size - s) < 0.0006 for s in offered), (doc["sku"], kind.type, size)
    built = {(_value(d, "Type"), _value(d, "Number of Points"), _value(d, "Finish")) for d in docs}
    assert built == set(kinds)


def test_the_sizes_are_read_from_the_across_flats_tables():
    wrenches = _module()
    assert wrenches.INCH_FLATS and wrenches.MM_FLATS
    assert set(wrenches.INCH_FLATS.values()) == {"ASME B18.2.2", "ASME B18.2.1"}
    assert set(wrenches.MM_FLATS.values()) == {"ISO 4017", "DIN 933"}
    # A width the nut or ISO table carries is read from it; the other table fills its gaps.
    assert wrenches.INCH_FLATS[Fraction(1, 2)] == "ASME B18.2.2"
    assert wrenches.INCH_FLATS[Fraction(5, 8)] == "ASME B18.2.1"
    assert wrenches.MM_FLATS[10.0] == "ISO 4017"
    assert wrenches.MM_FLATS[17.0] == "DIN 933"
    for kind in wrenches.KINDS:
        assert wrenches.sizes_in(kind, False) and wrenches.sizes_in(kind, True), kind.type


def _missing_row_sizes(docs: list[dict]) -> list[str]:
    counts = Counter(
        Fraction(parse_length(_value(doc, "Size")).inches).limit_denominator(64)
        for doc in docs
        if "mm" not in _value(doc, "Size")
    )
    return [size for size in ROW_SIZES if not counts[Fraction(size)]]


def test_the_breadth_rows_sizes_are_still_offered():
    assert _missing_row_sizes(_default_docs()) == []


#: Twelve seeds from the default on: before #50's fix, 9 of them built no 3/4" wrench.
SEEDS = range(GeneratorConfig().seed, GeneratorConfig().seed + 12)


def test_the_breadth_rows_sizes_are_offered_whatever_the_seed():
    """The sizes are a rotation over the type's lines, not a variant count's luck (#50)."""
    missing = {}
    for seed in SEEDS:
        built = generate_type(GeneratorConfig(seed=seed), KEY)
        docs = [json.loads(line) for line in type_gates.records(built)]
        if gaps := _missing_row_sizes(docs):
            missing[seed] = gaps
    assert missing == {}


class _Rotations:
    """A generator's two rotations, for ``_run`` alone: the pool's rotation always at 0."""

    def __init__(self, step: int):
        self.step = step

    def _rotation_step(self, key: str) -> int:
        return self.step

    def _offered_run(self, key: str, lengths: list[float], count: int) -> list[float]:
        return sorted(lengths)[:count]


def test_a_line_anchored_on_a_breadth_size_keeps_its_drawn_count_and_the_size():
    """A run anchored near the pool's long end is moved back, never cut short."""
    wrenches = _module()
    for kind in wrenches.KINDS:
        pool = sorted(wrenches.sizes_in(kind, False))
        for step, anchor in enumerate(wrenches.BREADTH_SIZES):
            for count in range(1, len(pool) + 1):
                run = wrenches._run(_Rotations(step), KEY, kind, "in", count)
                assert len(run) == count, (kind.type, anchor, count)
                start = pool.index(run[0])
                assert run == pool[start : start + count], (kind.type, anchor, count)
                if float(anchor) in pool:
                    assert float(anchor) in run, (kind.type, anchor, count)


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_combination_wrenches.py``."""
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
