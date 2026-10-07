"""Per-type gates for ``retaining_rings_external``, deepened from breadth (#53).

Copied from ``tests/test_type_lock_nuts_nylon_insert.py`` (uniqueness, census
names, provenance, determinism, the golden slice, independence), plus the
gates particular to this type:

* every size the breadth row asked for is built at the default size;
* a metric SKU publishes the DIN 471 row of its Size, and an inch SKU
  publishes no dimension but its Size and claims no standard;
* both series and both stocked materials are built.

The type's module is imported inside the tests that read its tables, so a
build without the module fails them on an assertion, not at collection.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

import type_gates
from published import published_attributes
from synthetic_industrial_products.catalog import names, taxonomy, typespec
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate, generate_type
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "retaining_rings_external"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKU count, rounded down to a hundred: a
#: floor that catches a collapse back to breadth, not a target.
DEFAULT_SKU_FLOOR = 300

#: The dimensional standard this type's metric lines claim, and the
#: dimensions it publishes.
DIMENSIONAL = {"DIN 471"}
DIMENSIONS = ("Size", "Thickness", "Groove Dia.", "Inside Dia.")

#: The breadth row's ``size_values``: the reference queries they serve must
#: still find a ring of each size.
BREADTH_SIZES = ("1/4 in", "3/8 in", "1/2 in", "5/8 in", "3/4 in", "1 in")

MM = 25.4


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _values(doc: dict) -> dict[str, dict]:
    return {a["name"]: a for a in published_attributes(doc)}


def _mm(attribute: dict) -> float:
    """A published length in mm, read from its own string as the catalog does."""
    from synthetic_industrial_products.dimensions import parse_length

    return parse_length(attribute["value"]).inches * MM


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
    assert checked > 50, f"only {checked} dimensional claims were checked"


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_retaining_rings_external.py``."""
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


def test_every_breadth_size_is_built_at_the_default_size():
    sizes = Counter(_values(doc)["Size"]["value"] for doc in _default_docs())
    missing = [size for size in BREADTH_SIZES if sizes[size] == 0]
    assert missing == [], f"no SKU of {missing}"


def test_a_metric_sku_publishes_its_din_471_row():
    from synthetic_industrial_products.product_types.fasteners import (
        retaining_rings_external as ring,
    )

    rows = {f"{d:g} mm": (s, d2, d3) for d, s, d3, d2 in ring._DIN_471}
    metric = [doc for doc in _default_docs() if _values(doc)["Size"]["value"].endswith(" mm")]
    assert len(metric) > 100, f"only {len(metric)} metric SKUs"
    wrong = []
    for doc in metric:
        values = _values(doc)
        thickness, groove, inside = rows[values["Size"]["value"]]
        for name, expected in (
            ("Thickness", thickness),
            ("Groove Dia.", groove),
            ("Inside Dia.", inside),
        ):
            # Published in the brand's feed style: within its rounding.
            if name in values and abs(_mm(values[name]) - expected) > 0.01:
                wrong.append((doc["sku"], name, values[name]["value"], expected))
        standards = {a["value"] for a in published_attributes(doc) if a["name"] == "Standards"}
        if not standards <= DIMENSIONAL:
            wrong.append((doc["sku"], "Standards", sorted(standards), "DIN 471"))
    assert wrong == [], wrong[:10]


def test_an_inch_sku_publishes_only_its_size_and_claims_no_standard():
    inch = [doc for doc in _default_docs() if _values(doc)["Size"]["value"].endswith(" in")]
    assert len(inch) > 100, f"only {len(inch)} inch SKUs"
    unbacked = {*DIMENSIONS[1:], "Standards"}
    wrong = [(doc["sku"], sorted(set(_values(doc)) & unbacked)) for doc in inch]
    wrong = [(sku, found) for sku, found in wrong if found]
    assert wrong == [], wrong[:10]


def test_both_series_and_both_materials_are_built():
    seen = Counter(
        (_values(doc)["Size"]["value"].rsplit(" ", 1)[1], _values(doc)["Material"]["value"])
        for doc in _default_docs()
    )
    built = {pair for pair, count in seen.items() if count > 0}
    assert built == {
        ("mm", "Spring Steel"),
        ("mm", "Stainless Steel"),
        ("in", "Spring Steel"),
        ("in", "Stainless Steel"),
    }


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
