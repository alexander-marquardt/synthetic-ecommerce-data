"""Per-type gates for ``pillow_block_bearings``, a table-driven type (#101).

The template's gates (uniqueness, census names, provenance, byte-determinism
under two hash seeds, a golden slice, independence from every other type), and
on top of them what a table type promises (:mod:`table_gates`): every size it
builds is a row of its table, its declared prices keep their orders, and every
row has a drawing scaled from that row.

The table is restated here, not read from the module, so a row typed wrong in
the module goes red. The housing dimensions are the UCP200 chart at
http://www.queensbearing.com/products/51-Pillow-Block-Bearings-UCP200-series.html
as the module's author read it on 2026-10-07, in inches; the module's
docstring says where the bores are from.

No price LEVEL is asserted beyond a wide sanity band: the prices are declared
estimates, and ``tests/test_price.py`` reads the type as not measured.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import table_gates
import type_gates
from published import published_attributes
from synthetic_ecommerce_data.catalog import names, taxonomy, typespec
from synthetic_ecommerce_data.catalog.config import GeneratorConfig
from synthetic_ecommerce_data.catalog.generate import generate, generate_type
from synthetic_ecommerce_data.drawing import svg_problems
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "pillow_block_bearings"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

DIMENSIONAL = {"JIS B 1557"}
#: The bore, then the chart's ``h``, ``a``, ``e`` and ``w`` under the names
#: they are published as.
COLUMNS = (
    "Bore Dia.",
    "Base to Center Height",
    "Overall Length",
    "Bolt Hole Center-to-Center",
    "Overall Height",
)
#: ``(bore, h, a, e, w)`` in inches: housings 204, 205 (two bores), 206
#: (three), 208, 210 and 212.
TABLE = (
    (0.75, 1.3125, 5.00, 3.74, 2.56),
    (0.875, 1.4375, 5.51, 4.13, 2.80),
    (1.0, 1.4375, 5.51, 4.13, 2.80),
    (1.125, 1.6875, 6.50, 4.76, 3.27),
    (1.1875, 1.6875, 6.50, 4.76, 3.27),
    (1.25, 1.6875, 6.50, 4.76, 3.27),
    (1.5, 1.9375, 7.24, 5.39, 3.86),
    (2.0, 2.25, 8.11, 6.26, 4.49),
    (2.25, 2.75, 9.49, 7.24, 5.43),
)
MM = table_gates.MM


def _inches(row: tuple[float, ...]) -> tuple[float, ...]:
    """A row ``table_gates`` read back in millimetres, in inches to four
    places: the table is stated in inches, and 1-7/16 in is 36.5125 mm, which
    a third place rounds either way."""
    return tuple(round(value / MM, 4) for value in row)


ROWS = set(TABLE)
MATERIALS = ("Cast Iron",)
PACKS = {1, 2, 4}

#: A build large enough to reach every row in every pack.
LARGE_LINES = 39000
#: What the default build holds: a move is a change to the table or its share.
DEFAULT_PRODUCTS = 43
DEFAULT_SKUS = 90
#: What ``LARGE_LINES`` builds: the table's 27 size-and-pack cells over the
#: brands that sell the type.
LARGE_PRODUCTS = 174
LARGE_SKUS = 270
#: USD for one pack, any size, pack and brand tier. Not a fit: a price outside
#: it is a broken ladder (a mounted bearing for a few dollars, or four of them
#: for many thousands), not a wrong estimate.
SANITY_BAND = (15.0, 2500.0)


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


@pytest.fixture(scope="module")
def large():
    return table_gates.catalog(KEY, LARGE_LINES)


@pytest.fixture(scope="module")
def large_docs(large) -> list[dict]:
    return table_gates.docs(large)


@pytest.fixture(scope="module")
def drawn(large):
    return table_gates.drawings(large, KEY, COLUMNS)


# --- the template's gates ---------------------------------------------------------


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is not a modelled type"


def test_the_type_does_not_also_exist_as_a_breadth_row():
    from synthetic_ecommerce_data.catalog import breadth

    assert [row.key for row in breadth.rows() if row.key == KEY] == []


def test_the_default_build_holds_the_declared_count():
    docs = _default_docs()
    assert len(docs) == DEFAULT_SKUS
    assert len({doc["product_id"] for doc in docs}) == DEFAULT_PRODUCTS


def test_the_large_build_holds_every_cell(large, large_docs):
    assert len(large.lines) == LARGE_PRODUCTS
    assert len(large_docs) == LARGE_SKUS


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert len(docs) == DEFAULT_SKUS
    assert same_product_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in published_attributes(doc)}
    assert set(COLUMNS) <= emitted
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_published_dimension_came_from(large_docs):
    problems, checked = type_gates.provenance_problems(large_docs, DIMENSIONAL, COLUMNS)
    assert problems == [], problems[:10]
    assert checked > 20, f"only {checked} dimensional claims were checked"


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert len(first) == DEFAULT_SKUS
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_pillow_block_bearings.py``."""
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


# --- the table ----------------------------------------------------------------------


def test_every_row_of_the_table_is_built_and_nothing_else(large_docs):
    assert len(ROWS) == 9
    assert {_inches(table_gates.row(doc, COLUMNS)) for doc in large_docs} == ROWS


def test_the_one_material_and_every_pack_is_built_and_nothing_else(large_docs):
    published = [table_gates.values(doc) for doc in large_docs]
    assert {v["Material"]["value"] for v in published} == set(MATERIALS)
    assert {int(v[table_gates.PACK]["value_canonical"]) for v in published} == PACKS


def test_no_load_capacity_is_published(large_docs):
    """A capacity is a force and the table states lengths: none is published,
    and one that appears must come with the source it was read from."""
    published = {a["name"] for doc in large_docs for a in doc["attributes"]}
    assert sorted(name for name in published if "Load" in name) == []


def test_one_product_publishes_exactly_these_attributes():
    """The default build's first record, whole."""
    doc = _default_docs()[0]
    assert doc["title"] == 'Replacement Pillow Block Bearing, 3/4" Bore Dia.'
    assert doc["price_usd"] == 24.94
    assert {a["name"]: a["value"] for a in doc["attributes"]} == {
        "Item": "Pillow Block Bearing",
        "Material": "Cast Iron",
        "Finish": "Painted",
        "Package Quantity": "1",
        "Standards": "JIS B 1557",
        "Bore Dia.": "3/4",
        "Base to Center Height": "1-5/16",
        "Overall Length": "5",
        "Bolt Hole Center-to-Center": "3.7400",
        "Overall Height": "2.5600",
        "Measurement System": "Fractional Inch",
    }


# --- the declared price keeps its orders --------------------------------------------


def test_larger_and_bigger_pack_each_cost_more(large_docs):
    """One material, so no material order to keep: 72 size pairs and 54 pack
    pairs are every neighbouring pair of 9 sizes and 3 packs at 3 brand tiers."""
    wrong, compared = table_gates.price_order(large_docs, KEY, "Bore Dia.", MATERIALS)
    assert wrong == [], f"{len(wrong)} wrong, e.g. {wrong[:4]}"
    assert compared == {"size": 72, "material": 0, "pack": 54}


def test_every_price_is_inside_the_sanity_band(large_docs):
    low, high = SANITY_BAND
    outside = [
        (doc["sku"], doc["price_usd"]) for doc in large_docs if not low <= doc["price_usd"] <= high
    ]
    assert outside == [], outside[:5]


# --- the drawing ---------------------------------------------------------------------


def test_every_row_has_a_drawing_and_no_two_rows_share_one(drawn):
    assert {_inches(size) for size in drawn} == ROWS
    assert len({svg for _, svg in drawn.values()}) == len(ROWS)


def test_each_drawing_is_scaled_from_its_row(drawn):
    """The foot is the row's ``Overall Length`` wide; the housing's crown is
    its ``Overall Height`` above the mounting face, which is y = 0."""
    for size, (figure, _) in drawn.items():
        bore, _, length, _, height = _inches(size)
        assert figure.source == "record", (bore, figure.source)
        x0, y0, x1, y1 = figure.figure.bounds()
        assert x1 - x0 == pytest.approx(length, abs=1e-4), bore
        assert y0 == pytest.approx(-height, abs=1e-4), bore
        assert y1 == 0.0, bore


def test_no_drawing_carries_text_and_the_largest_is_small(drawn):
    assert [problem for _, svg in drawn.values() for problem in svg_problems(svg)] == []
    assert max(len(svg) for _, svg in drawn.values()) < 8000


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
