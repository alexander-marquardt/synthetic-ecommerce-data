"""Per-type gates for ``shaft_collars``, deepened from breadth (#833).

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

And this type's own: every collar a record publishes is a row of the table
its line reads, in a material that row is stocked in, and every catalogue row
is the bore its catalogue number says.
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
from synthetic_ecommerce_data.core.dimensions import parse_length
from synthetic_ecommerce_data.domains.industrial import names, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import unexplained_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "shaft_collars"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse back to the
#: breadth row's 2 SKUs, and is not a target.
DEFAULT_SKU_FLOOR = 40

DIMENSIONS = ("Bore Dia.", "Outside Dia.", "Width")

#: The breadth row's size_values: every one is built at the default size.
BREADTH_BORES = ('1/4"', '3/8"', '1/2"', '5/8"', '3/4"', '1"')


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _module():
    """The type's module, read in the tests that need it: until it exists the
    first two gates red on their assertions, not on an import."""
    return importlib.import_module(
        "synthetic_ecommerce_data.domains.industrial.product_types.motion." + KEY
    )


def _values(doc: dict) -> dict[str, str]:
    return {a["name"]: a["value"] for a in authored_attributes(doc)}


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_every_breadth_bore_is_built_by_default():
    bores = {_values(doc).get("Bore Dia.") for doc in _default_docs()}
    assert set(BREADTH_BORES) <= bores, sorted(set(BREADTH_BORES) - bores)


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
    problems, _ = type_gates.provenance_problems(_default_docs(), (), DIMENSIONS)
    assert problems == [], problems[:10]


def test_a_collar_claims_no_standard():
    collars = _module()
    assert list(collars.SPEC.claims({}, metric=True, provenance="", standard="")) == []
    assert collars.SPEC.may_claim == frozenset()


def test_every_collar_is_a_row_of_its_lines_table():
    """The bore, outside diameter, width and screw a record publishes are one
    row of the table its type, material, finish and unit system name."""
    collars = _module()
    seen = set()
    for doc in _default_docs():
        v = _values(doc)
        metric = v["Bore Dia."].endswith("mm")
        line = (v["Type"], v["Material"], v.get("Finish", ""), "mm" if metric else "in")
        rows = [r for t in collars.series() if t.line == line for r in t.rows]
        assert rows, (doc["sku"], line)
        got = tuple(parse_length(v[name]).inches for name in DIMENSIONS)
        assert any(
            all(abs(a - b) < 0.006 for a, b in zip(got, (r.bore, r.outside, r.width), strict=True))
            and v["Screw Size"] == r.screw
            for r in rows
        ), (doc["sku"], got)
        seen.add(line)
    assert len(seen) >= 4, seen


def test_every_row_is_its_catalogue_number():
    """C-106 is a 1-1/16" bore: the number is the bore in hundredths of an
    inch, cut short (millimetres on a metric row); the outside diameter is
    larger than the bore; and a table rises by bore."""
    collars = _module()
    for name, text in collars.TABLES.items():
        rows = collars.parse_table(text, metric=name == "metric")
        assert rows, name
        for row in rows:
            digits = row.number.split("-")[1]
            if name == "metric":
                assert float(digits) == pytest.approx(row.bore * 25.4), row.number
            else:
                assert int(digits) == int(row.bore * 100 + 1e-9), row.number
            assert row.bore < row.outside, row.number
            assert row.materials, row.number
        assert [r.bore for r in rows] == sorted({r.bore for r in rows}), name


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_shaft_collars.py``."""
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
