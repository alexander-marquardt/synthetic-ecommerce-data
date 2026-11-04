"""Per-type gates for ``cut_resistant_gloves``, deepened from breadth (#834).

The lock nut's gates (``tests/test_type_lock_nuts_nylon_insert.py``), plus
the ones this type adds: every published glove is one of the guide's model
lines, every size is an EN ISO 21420 hand size, a product's sizes are
neighbours, and every size the breadth row offered is still offered.

Every byte comparison goes through :mod:`type_gates`, which compares digests
and then names the first differing SKU, so a red reports in seconds.
"""

from __future__ import annotations

import collections
import importlib
import json
from pathlib import Path

import pytest

import type_gates
from published import authored_attributes, authored_entries
from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import names, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "cut_resistant_gloves"
MODULE = "synthetic_ecommerce_data.domains.industrial.product_types.safety.cut_resistant_gloves"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's 68 SKUs, rounded down to ten: a floor that
#: catches a collapse back to breadth, not a target.
DEFAULT_SKU_FLOOR = 40

#: The sizes the breadth row offered (``size_values``): each is still offered.
BREADTH_SIZES = ("Small", "Medium", "Large", "X-Large")


def _module():
    return importlib.import_module(MODULE)


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _values(doc: dict) -> dict[str, str]:
    return {a["name"]: a["value"] for a in authored_entries(doc)}


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_every_published_glove_is_one_of_the_guides_model_lines():
    """Cut level, shell and coating are a row of the guide; a gauge, when
    published, is that row's."""
    lines = _module().MODEL_LINES
    checked = 0
    for doc in _default_docs():
        values = _values(doc)
        rows = [
            row
            for row in lines
            if (row.cut_level, row.material, row.coating)
            == (values["ANSI Cut Level"], values["Material"], values["Coating"])
        ]
        assert rows, doc["sku"]
        if "Knit Gauge" in values:
            assert values["Knit Gauge"] in {f"{row.gauge} Gauge" for row in rows}, doc["sku"]
        checked += 1
    assert checked >= DEFAULT_SKU_FLOOR


def test_the_model_lines_are_distinct_and_rated_by_the_standard():
    lines = _module().MODEL_LINES
    assert len(lines) == len(set(lines)) == 29
    assert {row.cut_level for row in lines} <= {f"A{n}" for n in range(1, 10)}


def test_a_products_sizes_are_neighbouring_hand_sizes():
    order = [size.name for size in _module().HAND_SIZES]
    by_product = collections.defaultdict(list)
    for doc in _default_docs():
        size = _values(doc)["Size"]
        assert size in order, doc["sku"]
        by_product[doc["product_id"]].append(order.index(size))
    for product, indexes in by_product.items():
        assert sorted(indexes) == list(range(min(indexes), max(indexes) + 1)), product


def test_every_size_the_breadth_row_offered_is_still_offered():
    counts = collections.Counter(_values(doc)["Size"] for doc in _default_docs())
    assert {size: counts[size] > 0 for size in BREADTH_SIZES} == dict.fromkeys(
        BREADTH_SIZES, True
    ), counts


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert same_product_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in authored_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_cut_resistant_gloves.py``."""
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
