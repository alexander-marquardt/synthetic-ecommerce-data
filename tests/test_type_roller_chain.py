"""Per-type gates for ``roller_chain``, deepened from breadth (#53), and the
``Pitch`` key split it needs (#36).

The gates are the lock nuts' (:mod:`test_type_lock_nuts_nylon_insert` says
what each one catches) with this type's ``KEY`` and floor.

#36: a roller chain's ``Pitch`` is the spacing of its links, an inch length,
and a metric tap's ``Pitch`` is its thread pitch. Real catalogs print both as
``Pitch``, so the display name stays, but the machine key differs: the chain's
is ``chain_pitch``, the tap's stays ``pitch``. Without the split the facet
derivation measures one ``pitch`` over both types and buckets a chain's
``1/2"`` beside a tap's ``1.25 mm``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import type_gates
from published import published_attributes
from synthetic_industrial_products.catalog import emit, names, taxonomy, typespec
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate, generate_type
from synthetic_industrial_products.prism import derive
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "roller_chain"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: The default build makes 81 SKUs; a floor that catches a collapse back to a
#: breadth row's one or two, not a target.
DEFAULT_SKU_FLOOR = 50

#: The dimensional standard every line claims, and the dimensions read from it.
DIMENSIONAL = {"ASME B29.1"}
DIMENSIONS = ("Pitch", "Roller Dia.", "Inside Width")


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert same_product_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in published_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_published_dimension_came_from():
    problems, checked = type_gates.provenance_problems(_default_docs(), DIMENSIONAL, DIMENSIONS)
    assert problems == [], problems[:10]
    assert checked > 30, f"only {checked} dimensional claims were checked"


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_roller_chain.py``."""
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


# --- #36: a chain's Pitch is not a tap's Pitch --------------------------------


@pytest.fixture(scope="module")
def default_rows() -> list[dict]:
    return list(emit.iter_flat(generate(GeneratorConfig())))


def _pitch_entries(rows: list[dict], type_key: str) -> list[dict]:
    return [
        a
        for row in rows
        if row["product_type"] == type_key
        for a in row["attributes"]
        if a["name"] == "Pitch"
    ]


def test_a_chains_pitch_is_keyed_chain_pitch_in_inches(default_rows):
    entries = _pitch_entries(default_rows, KEY)
    chains = [row for row in default_rows if row["product_type"] == KEY]
    assert len(entries) == len(chains), (len(entries), len(chains))
    assert {a["key"] for a in entries} == {"chain_pitch"}
    assert {a["unit_code"] for a in entries} == {"INH"}
    assert all("chain_pitch" in row["facets"] for row in chains)
    assert not any("pitch" in row["facets"] for row in chains)


def test_a_taps_pitch_keeps_the_key_pitch(default_rows):
    entries = _pitch_entries(default_rows, "tap_spiral_point")
    assert entries, "no tap published a Pitch"
    assert {a["key"] for a in entries} == {"pitch"}
    assert {a["unit_code"] for a in entries} == {"MMT"}


def test_the_facet_derivation_measures_the_two_pitches_apart(default_rows):
    stats = derive.measure(default_rows)
    pitches = {key: s for key, s in stats.items() if s.name == "Pitch"}
    assert sorted(pitches) == ["chain_pitch", "pitch"]
    assert pitches["chain_pitch"].product_types == (KEY,)
    assert pitches["pitch"].product_types == ("tap_spiral_point",)
    decisions = [derive.decide(s) for s in pitches.values()]
    assert sorted(d.stats.key for d in decisions) == ["chain_pitch", "pitch"]


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
