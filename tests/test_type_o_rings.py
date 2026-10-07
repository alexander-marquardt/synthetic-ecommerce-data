"""Per-type gates for ``o_rings``, deepened from breadth (#53).

The lock nut's gates (``tests/test_type_lock_nuts_nylon_insert.py``), plus
the two this type adds: every size is a row of the AS568 table, and the
borrowed flat-washer price model is never read beyond the key span it was
fitted over (the washer's slope run out to a 25.94" ring priced it near
1,000 USD).

Every byte comparison goes through :mod:`type_gates`, which compares digests
and then names the first differing SKU, so a red reports in seconds.
"""

from __future__ import annotations

import dataclasses
import importlib
import json
from pathlib import Path

import pytest

import type_gates
from published import published_attributes
from synthetic_industrial_products.catalog import names, price, standards, taxonomy, typespec
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate, generate_type
from synthetic_industrial_products.catalog.model import length_attribute
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "o_rings"
MODULE = "synthetic_industrial_products.product_types.motion.o_rings"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's 66 SKUs, rounded down to ten: a floor
#: that catches a collapse back to breadth, not a target.
DEFAULT_SKU_FLOOR = 40

DIMENSIONAL = {"SAE AS568"}
DIMENSIONS = ("Inside Dia.", "Width", "Inside Dia. Tolerance", "Width Tolerance")

#: The AS568 rows the type offers: 349 dash numbers less none, by series.
SERIES_ROWS = {"0": 50, "1": 77, "2": 84, "3": 87, "4": 51}

#: A shown price an elastomer seal sold one per SKU does not reach.
SEAL_PRICE_CEILING = 50.0


def _module():
    return importlib.import_module(MODULE)


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_every_as568_series_is_offered_whole():
    by_series = _module().series()
    assert {name: len(rows) for name, rows in by_series.items()} == SERIES_ROWS
    dashes = [row.dash for row in _module().rows()]
    assert len(dashes) == len(set(dashes)) == 349
    # Within a series a nominal inside diameter names one ring.
    for rows in by_series.values():
        assert len({row.nominal for row in rows}) == len(rows)


def test_every_published_ring_is_its_dash_numbers_row():
    """Size, inside diameter and width agree with the table row the dash names."""
    by_dash = {row.dash: row for row in _module().rows()}
    checked = 0
    for doc in _default_docs():
        values = {a["name"]: a["value"] for a in doc["attributes"]}
        if "Dash Number" not in values:
            continue
        row = by_dash[values["Dash Number"].removeprefix("AS568-")]
        assert length_attribute("Inside Dia.", values["Inside Dia."]).value_num == pytest.approx(
            row.inside * 25.4
        ), doc["sku"]
        assert length_attribute("Width", values["Width"]).value_num == pytest.approx(
            row.width * 25.4
        ), doc["sku"]
        checked += 1
    assert checked > 30, checked


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
    assert checked > 5, f"only {checked} dimensional claims were checked"


def test_the_borrowed_price_model_is_the_flat_washers():
    typespec.ensure_registered()
    assert price.BORROWS.get(KEY) == "washer_flat"
    assert price.model_for(KEY) is price.MODELS["washer_flat"]


def test_the_washer_span_is_the_washer_builders_own_rows():
    sizes = standards.available_sizes("ISO 7089")
    inside = [standards.washer("ISO 7089", size).inside_dia_in for size in sizes]
    assert price.MEASURED_SPANS.get("washer_flat") == pytest.approx((min(inside), max(inside)))


def test_a_borrowed_key_is_held_to_the_span_its_model_was_fitted_over():
    """The key of every AS568 row lies inside the washer's span: none extrapolates."""
    typespec.ensure_registered()
    low, high = price.MEASURED_SPANS["washer_flat"]
    read = price.KEYS[KEY]
    keys = {
        row.dash: read({"Width": length_attribute("Width", f'{row.width:.3f}"')})
        for row in _module().rows()
    }
    assert all(low <= k <= high for k in keys.values()), keys
    # An -001's 0.040" is below the span and reads as its floor; a -475's
    # 0.275" is inside it and reads as itself.
    assert keys["001"] == pytest.approx(low)
    assert keys["475"] == pytest.approx(0.275)
    # A key above the span reads as its ceiling.
    assert read({"Width": length_attribute("Width", '2.000"')}) == pytest.approx(high)


def test_a_type_that_borrows_declares_no_model_of_its_own():
    spec = dataclasses.replace(_module().SPEC, price=price.MODELS["washer_flat"], module=MODULE)
    with pytest.raises(typespec.TypeModuleError, match="both a price model and borrows"):
        typespec.register(spec)


def test_no_ring_is_priced_like_a_part_an_elastomer_seal_is_not():
    prices = [doc["price_usd"] for doc in _default_docs()]
    assert max(prices) < SEAL_PRICE_CEILING, max(prices)


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_o_rings.py``."""
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
