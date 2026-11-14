"""Per-type gates for ``bar_stock_square`` (#830, slice 3).

The template is ``tests/test_type_bar_stock_round.py``: uniqueness, census conformance,
provenance, byte-determinism under two hash seeds, a golden slice, and independence
from every other type. On top of it, each value the type publishes is held to the spec
space, restated here rather than read from the module, so a size typed wrong in the
module goes red, and the type's brands are held to the ``material`` pool.

Every byte comparison goes through :mod:`type_gates`, which compares digests and then
names the first differing SKU, so a red reports in seconds.
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import pytest

import type_gates
from published import authored_attributes, authored_entries
from synthetic_ecommerce_data.core import brands, emit, typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import breadth, names, taxonomy
from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from synthetic_ecommerce_data.domains.industrial.title_attributes import TITLE_ATTRIBUTES
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "bar_stock_square"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to ten: a floor that catches a
#: collapse to the breadth row's one SKU, not a target.
DEFAULT_SKU_FLOOR = 50

#: The size a square bar is sold by, its side: the name square key stock publishes for it.
SIZE = "Width"

#: The dimensions the type publishes; it claims no dimensional standard.
DIMENSIONS = (SIZE, "Length")

#: A build large enough to reach every size in every combination.
LARGE_LINES = 39000

MM = 25.4

# --- the spec space, restated from the issue, not from the module ------------------

#: Widths, inches: 1/8" to 1" by sixteenths, to 2" by eighths, to 3" by quarters, then
#: 3-1/2" and 4".
SIZES = {
    *(Fraction(n, 16) for n in range(2, 17)),
    *(Fraction(n, 8) for n in range(9, 17)),
    *(Fraction(n, 4) for n in range(9, 13)),
    Fraction(7, 2),
    Fraction(4),
}
#: (Material, Material Grade): the nine alloys square bar is stocked in.
ALLOYS = {
    ("Steel", "1018"),
    ("Steel", "1045"),
    ("Steel", "12L14"),
    ("Alloy Steel", "4140"),
    ("Stainless Steel", "303"),
    ("Stainless Steel", "304"),
    ("Stainless Steel", "316"),
    ("Aluminum", "6061-T6"),
    ("Brass", "C360"),
}
#: (Material, Material Grade, Length in inches).
COMBOS = {(material, grade, length) for material, grade in ALLOYS for length in (12, 36, 72, 144)}
#: The ten makers of the ``material`` family, the brand pool decided on #830.
MATERIAL_POOL = {
    "Dravenholt",
    "Kessingmoor",
    "Tervasko",
    "Varnstrom",
    "Iron Heron",
    "Vellinhorst",
    "Crennick Works",
    "Ashcombe Forge",
    "Quennick",
    "Salt Meadow Works",
}
#: Every attribute name a record may publish of its own: a square bar is drawn, never ground,
#: so it publishes no Finish.
NAMES = {"Material", "Material Grade", "Length", SIZE}
#: The name every type's records carry for the unit system they are in.
MEASUREMENT_NAMES = {"Measurement System"}
#: The breadth row's sizes and materials, which the reference queries need.
ROW_SIZES = {Fraction(1, 4), Fraction(3, 8), Fraction(1, 2), Fraction(3, 4)}
ROW_MATERIALS = {"Steel", "Aluminum"}


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _clean_docs(lines: int | None = None) -> list[dict]:
    """The type's documents with no injected defect, so each value is the builder's."""
    config = GeneratorConfig(defect_scale=0.0, **({"lines": lines} if lines else {}))
    catalog = generate(config, types=[KEY])
    return [doc for line in catalog.lines for doc in emit.flat_documents(catalog, line)]


def _values(doc: dict) -> dict[str, dict]:
    return {a["name"]: a for a in authored_entries(doc)}


def _inches(attribute: dict) -> Fraction:
    """``value_canonical`` is millimetres whatever unit the value is written in."""
    return Fraction(float(attribute["value_canonical"]) / MM).limit_denominator(64)


def _size(doc: dict) -> Fraction:
    return _inches(_values(doc)[SIZE])


def _combo(doc: dict) -> tuple[str, str, int]:
    values = _values(doc)
    return (
        values["Material"]["value"],
        values["Material Grade"]["value"],
        int(_inches(values["Length"])),
    )


@pytest.fixture(scope="module")
def clean_docs() -> list[dict]:
    return _clean_docs()


@pytest.fixture(scope="module")
def large_docs() -> list[dict]:
    return _clean_docs(LARGE_LINES)


# --- the template's gates ---------------------------------------------------------


def test_the_type_is_modelled_in_its_own_module_and_its_breadth_row_is_gone():
    assert KEY in typespec.modelled(), f"{KEY} is not a modelled type"
    assert KEY not in {row.key for row in breadth.load_rows()}


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert same_product_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in authored_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_each_published_dimension_and_no_standard():
    docs = _default_docs()
    problems, claims = type_gates.provenance_problems(docs, set(), DIMENSIONS)
    assert problems == [], problems[:10]
    assert claims == 0
    assert {doc["dimension_provenance"] for doc in docs} == {
        "Width and Length are conventional stocked sizes; "
        "no standard fixes these values"
    }


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_bar_stock_square.py``."""
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


def test_the_title_names_the_width():
    assert TITLE_ATTRIBUTES[KEY] == ((SIZE, "W"),)


# --- the brand pool -----------------------------------------------------------------


def test_the_type_draws_from_the_material_pool_and_no_fastener_specialist():
    assert {b.name for b in brands.brands_for(KEY)} == MATERIAL_POOL
    fastener_only = {b.name for b in brands.BRAND_BOOK if b.families == {"fastener"}}
    assert not fastener_only & MATERIAL_POOL
    assert {doc["brand"] for doc in _default_docs()} <= MATERIAL_POOL


def test_the_pools_tiers_price_in_order_on_the_specs_its_brands_share(large_docs):
    """``test_price``'s tier order, for the material family at ``--lines 39000``: at the
    default size its lines share almost no spec across brands (#830)."""
    by_spec: dict[tuple, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for doc in large_docs:
        tier = brands.tier_of(doc["brand"], KEY)
        by_spec[(_combo(doc), _size(doc))][tier].append(doc["price_usd"])
    economy, premium = [], []
    for tiers in by_spec.values():
        if "standard" not in tiers:
            continue
        standard = statistics.median(tiers["standard"])
        if "economy" in tiers:
            economy.append(statistics.median(tiers["economy"]) / standard)
        if "premium" in tiers:
            premium.append(statistics.median(tiers["premium"]) / standard)
    assert len(economy) >= 20 and len(premium) >= 20, (len(economy), len(premium))
    assert statistics.median(economy) < 1.0 < statistics.median(premium)


# --- the type's values against the spec space ---------------------------------------


def test_the_default_build_offers_the_breadth_rows_sizes_and_materials(clean_docs):
    assert {_size(doc) for doc in clean_docs} >= ROW_SIZES
    assert {_combo(doc)[0] for doc in clean_docs} >= ROW_MATERIALS
    half_inch_square = [doc for doc in clean_docs if _size(doc) == Fraction(1, 2)]
    assert half_inch_square


def test_the_default_build_stays_in_the_spec_space(clean_docs):
    assert {_size(doc) for doc in clean_docs} <= SIZES
    assert {_combo(doc) for doc in clean_docs} <= COMBOS


def test_the_large_build_offers_every_combination_and_every_size(large_docs):
    assert {_combo(doc) for doc in large_docs} == COMBOS
    assert {_size(doc) for doc in large_docs} == SIZES


def test_a_record_publishes_its_alloy_and_no_tolerance_or_standard(large_docs):
    published = {a["name"] for doc in large_docs for a in authored_entries(doc)}
    assert published - MEASUREMENT_NAMES == NAMES
    assert typespec.modelled()[KEY].may_claim == frozenset()


def test_a_drawing_says_how_much_of_it_was_read_from_the_record():
    figure, _ = FIGURES[KEY]
    assert figure({SIZE: '1/2"', "Length": '12"'}).source == "record"
    assert figure({SIZE: '1/2"'}).source == "partial"
    assert figure({}).source == "nominal"


def test_a_wider_bar_is_drawn_wider_and_a_longer_bar_longer():
    figure, _ = FIGURES[KEY]

    def size(width: str, length: str) -> tuple[float, float]:
        x0, y0, x1, y1 = figure({SIZE: width, "Length": length}).figure.bounds()
        return x1 - x0, y1 - y0

    thin, thick = size('1/4"', '12"'), size('1"', '12"')
    assert thick[0] > thin[0]
    assert size('1/4"', '36"')[1] > thin[1]
    assert size('1/4"', '144"')[1] > size('1/4"', '72"')[1]


def test_stainless_costs_several_times_steel_and_a_long_bar_under_its_short_bars(large_docs):
    """The price is generated; these are the ratios its model states."""
    by_spec: dict[tuple, list[float]] = defaultdict(list)
    for doc in large_docs:
        material, _, length = _combo(doc)
        by_spec[(material, length, _size(doc))].append(doc["price_usd"])
    median = {spec: statistics.median(prices) for spec, prices in by_spec.items()}

    def ratio(top: tuple, bottom: tuple) -> float:
        shared = [s for s in SIZES if (*top, s) in median and (*bottom, s) in median]
        assert len(shared) >= 5, (top, bottom, shared)
        return statistics.median(median[(*top, s)] / median[(*bottom, s)] for s in shared)

    assert 2.0 < ratio(("Stainless Steel", 12), ("Steel", 12)) < 5.0
    assert 2.0 < ratio(("Brass", 12), ("Steel", 12)) < 4.5
    assert 2.0 < ratio(("Steel", 36), ("Steel", 12)) < 3.0
    assert 8.0 < ratio(("Steel", 144), ("Steel", 12)) < 12.0


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
