"""Per-type gates for ``hex_pipe_nipples``, deepened from breadth (#832).

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

And this type's own: every hex nipple is a row of the maker's hex chart, every
close and barrel nipple a size and length of the ASTM A733 table in its
schedule, and every kind is built.
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

KEY = "hex_pipe_nipples"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse back to the
#: breadth row's 2 SKUs, and is not a target.
DEFAULT_SKU_FLOOR = 50


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _module():
    """The type's module, read in the tests that need it: until it exists the
    first two gates red on their assertions, not on an import."""
    return importlib.import_module(
        "synthetic_ecommerce_data.domains.industrial.product_types.motion." + KEY
    )


def _attrs(doc: dict) -> dict[str, str]:
    return {a["name"]: a["value"] for a in authored_attributes(doc)}


def _inches(value: str) -> float:
    return parse_length(value).inches


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
    module = _module()
    docs = _default_docs()
    problems, _ = type_gates.provenance_problems(docs, (), ("Length",))
    assert problems == [], problems[:10]
    for doc in docs:
        hex_kind = _attrs(doc)["Type"] in module.HEX_KINDS
        source = module.HEX_CHART if hex_kind else module.A733
        assert source in doc["dimension_provenance"], (doc["sku"], doc["dimension_provenance"])


def test_every_hex_nipple_is_a_row_of_the_hex_chart():
    """Pipe size, length, hex and pressure rating are one chart row, the
    rating the one the chart gives the record's material."""
    module = _module()
    hexes = [d for d in _default_docs() if _attrs(d)["Type"] in module.HEX_KINDS]
    assert hexes, "no hex nipple was built"
    rows = module.hex_rows()
    for doc in hexes:
        a = _attrs(doc)
        row = rows.get((a["Type"], a["Pipe Size"], round(_inches(a["Length"]), 3)))
        assert row is not None, (doc["sku"], a["Type"], a["Pipe Size"], a["Length"])
        assert _inches(a["Hex Size"]) == pytest.approx(row.hex, abs=1e-3), doc["sku"]
        psi = row.brass_psi if a["Material"] == "Brass" else row.psi
        assert a["Pressure Rating (psi)"] == f"{psi:,}", doc["sku"]


def test_every_close_and_barrel_nipple_is_an_a733_size_and_length_in_its_schedule():
    """A close nipple is the table's close length for its size; a barrel
    nipple a length the table offers the size in, in the line's schedule; the
    outside diameter is the size's."""
    module = _module()
    pipes = [d for d in _default_docs() if _attrs(d)["Type"] not in module.HEX_KINDS]
    assert pipes, "no close or barrel nipple was built"
    table = {row["size"]: row for row in module.A733_TABLE.rows}
    for doc in pipes:
        a = _attrs(doc)
        row = table[a["Pipe Size"].removesuffix(" in")]
        schedule = a["Schedule"].removeprefix("Schedule ")
        length = _inches(a["Length"])
        if a["Type"] == "Close":
            assert length == pytest.approx(_inches(row["close"] + " in"), abs=1e-3), doc["sku"]
        else:
            offered = [_inches(x + " in") for x in row["lengths"][schedule]]
            assert any(abs(length - x) < 1e-3 for x in offered), (doc["sku"], schedule, length)
        assert _inches(a["Outside Dia."]) == pytest.approx(row["od"], abs=1e-3), doc["sku"]


def test_every_kind_is_built_and_the_breadth_rows_sizes_are_offered():
    module = _module()
    docs = _default_docs()
    assert {_attrs(d)["Type"] for d in docs} == set(module.KINDS)
    sizes = {_attrs(d)["Pipe Size"] for d in docs}
    assert {"1/4 in", "3/8 in", "1/2 in", "3/4 in", "1 in"} <= sizes


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_hex_pipe_nipples.py``."""
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
