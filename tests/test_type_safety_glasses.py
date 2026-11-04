"""Per-type gates for ``safety_glasses``, deepened from breadth (#834).

The lock nut's gates (``tests/test_type_lock_nuts_nylon_insert.py``), plus
the ones this type adds: every published pair is one of the maker's model
lines in one of that line's lens colors, and every lens color the breadth row
offered is still offered.

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

KEY = "safety_glasses"
MODULE = "synthetic_ecommerce_data.domains.industrial.product_types.safety.safety_glasses"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's 52 SKUs, rounded down to ten: a floor that
#: catches a collapse back to breadth, not a target.
DEFAULT_SKU_FLOOR = 30

#: The lens colors the breadth row offered (``size_values``): each is still offered.
BREADTH_COLORS = ("Clear", "Gray", "Amber")


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


def test_every_published_pair_is_one_of_the_makers_model_lines():
    """Frame style, coating and frame color are a row of the feed, and the
    lens color is one that row is sold in; a product's lens colors are one row's."""
    lines = _module().MODEL_LINES
    by_product = collections.defaultdict(set)
    for doc in _default_docs():
        values = _values(doc)
        rows = [
            row
            for row in lines
            if (row.style, row.coating, row.frame_color)
            == (values["Style"], values["Coating"], values.get("Frame Color"))
        ]
        assert rows, doc["sku"]
        assert values["Lens Color"] in {tint for row in rows for tint in row.tints}, doc["sku"]
        by_product[doc["product_id"]].add(values["Lens Color"])
    for product, tints in by_product.items():
        assert any(tints <= set(row.tints) for row in lines), product
    assert len(by_product) > 1


def test_the_model_lines_are_distinct_and_sold_in_named_tints():
    module = _module()
    lines = module.MODEL_LINES
    assert len(lines) == len(set(lines)) == 44
    assert {tint for row in lines for tint in row.tints} == set(module.LENS_COLORS)
    assert {row.coating for row in lines} == {"Anti-Fog", "No Anti-Fog"}


def test_every_lens_color_the_breadth_row_offered_is_still_offered():
    counts = collections.Counter(_values(doc)["Lens Color"] for doc in _default_docs())
    assert {tint: counts[tint] > 0 for tint in BREADTH_COLORS} == dict.fromkeys(
        BREADTH_COLORS, True
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
    """Regenerate with ``uv run python tests/test_type_safety_glasses.py``."""
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
