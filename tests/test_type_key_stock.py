"""Per-type gates for ``key_stock`` (#108).

The template is ``tests/test_type_lock_nuts_nylon_insert.py``: uniqueness,
census conformance, provenance, byte-determinism under two hash seeds, a golden
slice, and independence from every other type. On top of it, each value the
type publishes is held to the spec space, restated here rather than read from
the module, so a size typed wrong in the module goes red.

Every byte comparison goes through :mod:`type_gates`, which compares digests
and then names the first differing SKU, so a red reports in seconds.
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import pytest

import type_gates
from published import published_attributes
from synthetic_industrial_products.catalog import emit, names, taxonomy, typespec
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate, generate_type
from synthetic_industrial_products.drawing.figures import FIGURES
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "key_stock"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's 70 SKUs, rounded down to ten: a floor
#: that catches a collapse to a breadth row's one or two SKUs, not a target.
DEFAULT_SKU_FLOOR = 40

#: The dimensions the type publishes; it claims no dimensional standard.
DIMENSIONS = ("Width", "Height", "Length")

#: A build large enough to reach every section in every combination.
LARGE_LINES = 39000

MM = 25.4

# --- the spec space, restated from the issue, not from the module ------------------

#: (width, height), inches: eleven square sizes and three rectangular ones.
SQUARE = ("1/8", "3/16", "1/4", "5/16", "3/8", "7/16", "1/2", "5/8", "3/4", "7/8", "1")
RECTANGULAR = (("1/4", "3/16"), ("3/8", "1/4"), ("1/2", "3/8"))
SECTIONS = {(Fraction(w), Fraction(h)) for w, h in [*((s, s) for s in SQUARE), *RECTANGULAR]}
#: (Fit, Material, Finish, Length in inches).
COMBOS = {
    (fit, material, finish, length)
    for fit in ("Oversized", "Undersized")
    for material, finish in (
        ("Steel", "Plain"),
        ("Steel", "Zinc Plated"),
        ("18-8 Stainless Steel", "Plain"),
    )
    for length in (12, 36)
}
#: Every attribute name a record may publish of its own.
NAMES = {"Item", "Fit", "Material", "Finish", "Length", "Width", "Height"}
#: The names every type's records may carry for the unit system they are in.
MEASUREMENT_NAMES = {"Measurement System", "System of Measurement", "Dimension Type"}


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _clean_docs(lines: int | None = None) -> list[dict]:
    """The type's documents with no injected defect, so each value is the builder's."""
    config = GeneratorConfig(defect_scale=0.0, **({"lines": lines} if lines else {}))
    catalog = generate(config, types=[KEY])
    return [doc for line in catalog.lines for doc in emit.flat_documents(catalog, line)]


def _values(doc: dict) -> dict[str, dict]:
    return {a["name"]: a for a in doc["attributes"]}


def _inches(attribute: dict) -> Fraction:
    """``value_canonical`` is millimetres whatever unit the value is written in."""
    return Fraction(float(attribute["value_canonical"]) / MM).limit_denominator(64)


def _section(doc: dict) -> tuple[Fraction, Fraction]:
    values = _values(doc)
    return _inches(values["Width"]), _inches(values["Height"])


def _combo(doc: dict) -> tuple[str, str, str, int]:
    values = _values(doc)
    return (
        values["Fit"]["value"],
        values["Material"]["value"],
        values["Finish"]["value"],
        int(_inches(values["Length"])),
    )


@pytest.fixture(scope="module")
def clean_docs() -> list[dict]:
    return _clean_docs()


@pytest.fixture(scope="module")
def large_docs() -> list[dict]:
    return _clean_docs(LARGE_LINES)


# --- the template's gates ---------------------------------------------------------


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is not a modelled type"


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


def test_the_provenance_names_each_published_dimension_and_no_standard():
    docs = _default_docs()
    problems, claims = type_gates.provenance_problems(docs, set(), DIMENSIONS)
    assert problems == [], problems[:10]
    assert claims == 0
    assert {doc["dimension_provenance"] for doc in docs} == {
        "Width, Height and Length are conventional stocked sizes; no standard fixes these values"
    }


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_key_stock.py``."""
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


# --- the type's values against the spec space ---------------------------------------


def test_the_default_build_reaches_every_section_and_every_combination(clean_docs):
    assert {_section(doc) for doc in clean_docs} == SECTIONS
    assert {_combo(doc) for doc in clean_docs} == COMBOS


def test_the_large_build_offers_every_section_in_every_combination(large_docs):
    built = {(_combo(doc), _section(doc)) for doc in large_docs}
    assert built == {(combo, section) for combo in COMBOS for section in SECTIONS}


def test_a_record_publishes_the_fits_name_and_no_tolerance_or_standard(large_docs):
    published = {a["name"] for doc in large_docs for a in doc["attributes"]}
    assert published - MEASUREMENT_NAMES == NAMES
    assert {_values(doc)["Item"]["value"] for doc in large_docs} == {"Key Stock"}
    assert typespec.modelled()[KEY].may_claim == frozenset()


def test_a_drawing_says_how_much_of_it_was_read_from_the_record():
    figure, _ = FIGURES[KEY]
    full = {"Width": '1/4"', "Height": '3/16"', "Length": '12"'}
    assert figure(full).source == "record"
    assert figure({"Width": '1/4"'}).source == "partial"
    assert figure({}).source == "nominal"


def test_a_wider_section_is_drawn_wider_and_a_longer_bar_longer():
    figure, _ = FIGURES[KEY]

    def size(width: str, height: str, length: str) -> tuple[float, float]:
        x0, y0, x1, y1 = figure(
            {"Width": width, "Height": height, "Length": length}
        ).figure.bounds()
        return x1 - x0, y1 - y0

    narrow, wide = size('1/4"', '1/4"', '12"'), size('1/2"', '1/2"', '12"')
    assert wide[0] > narrow[0]
    assert size('1/4"', '1/4"', '36"')[1] > narrow[1]


def test_stainless_costs_several_times_steel_and_a_long_bar_under_three_short(large_docs):
    """The price is generated; these are the two ratios its model states."""
    by_spec: dict[tuple, list[float]] = defaultdict(list)
    for doc in large_docs:
        _, material, _, length = _combo(doc)
        by_spec[(material, length, _section(doc)[0])].append(doc["price_usd"])
    median = {spec: statistics.median(prices) for spec, prices in by_spec.items()}
    widths = sorted({width for _, _, width in median})
    assert len(widths) == 11
    stainless = [median[("18-8 Stainless Steel", 12, w)] / median[("Steel", 12, w)] for w in widths]
    longer = [median[("Steel", 36, w)] / median[("Steel", 12, w)] for w in widths]
    assert 3.0 < statistics.median(stainless) < 9.0, stainless
    assert 2.0 < statistics.median(longer) < 3.0, longer


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
