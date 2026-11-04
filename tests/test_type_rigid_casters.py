"""Per-type gates for ``rigid_casters``, deepened from breadth (#835).

Copied from the threaded rod's gate file; each gate is about this type alone:

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record names the chart its dimensions were read from, and
  every published dimension and load is that chart's own row;
* the breadth row's sizes: every wheel the row offered is still built;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed golden
  has it.
"""

from __future__ import annotations

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

KEY = "rigid_casters"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: A deep type, not a breadth row's two SKUs. A floor that catches a collapse
#: back to breadth, not a target.
DEFAULT_SKU_FLOOR = 40

#: No dimensional standard exists for a caster, so none is claimed.
DIMENSIONAL: set[str] = set()
DIMENSIONS = ("Wheel Dia.", "Tread Width", "Overall Height")

#: The wheel diameters the breadth row offered (``size_values``, in inches).
BREADTH_SIZES = (2.0, 3.0, 4.0, 5.0, 6.0)


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _attrs(doc: dict) -> dict[str, str]:
    return {a["name"]: a["value"] for a in authored_attributes(doc)}


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
    unread = [d["sku"] for d in docs if "caster chart" not in d["dimension_provenance"]]
    assert not unread, f"{len(unread)} records name no caster chart, e.g. {unread[:3]}"


def test_every_published_dimension_and_load_is_its_charts_row():
    """A record's tread, height and load are the chart row of its series,
    wheel diameter and wheel material, never scaled from a neighbour."""
    from synthetic_ecommerce_data.domains.industrial.product_types.material_handling import (
        rigid_casters,
    )

    rows = rigid_casters.chart_rows()
    wrong = []
    for doc in _default_docs():
        attrs = _attrs(doc)
        key = (
            parse_length(attrs["Wheel Dia."]).inches,
            parse_length(attrs["Tread Width"]).inches,
            attrs["Wheel Material"],
            attrs["Bearing Type"],
        )
        row = rows.get(key)
        published = (
            parse_length(attrs["Overall Height"]).inches,
            float(attrs["Load Capacity"].split()[0].replace(",", "")),
        )
        if row is None or abs(row[0] - published[0]) > 1e-3 or row[1] != published[1]:
            wrong.append((doc["sku"], key, published, row))
    assert not wrong, f"{len(wrong)} records are not a chart row, e.g. {wrong[:3]}"


def test_every_wheel_the_breadth_row_offered_is_built():
    built = {parse_length(_attrs(doc)["Wheel Dia."]).inches for doc in _default_docs()}
    missing = [size for size in BREADTH_SIZES if size not in built]
    assert not missing, f"no {KEY} SKU has a wheel of {missing} in"


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_rigid_casters.py``."""
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
