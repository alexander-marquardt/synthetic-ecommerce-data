"""Per-type gates for ``retaining_rings_external``, a table-driven type (#101).

The template's gates (uniqueness, census names, provenance, byte-determinism
under two hash seeds, a golden slice, independence from every other type), and
on top of them what a table type promises (:mod:`table_gates`): every size it
builds is a row of its table, its declared prices keep their three orders, and
every row has a drawing scaled from that row.

The table is restated here, not read from the module, so a row typed wrong in
the module goes red. It is the chart at
https://www.fasteners.eu/standards/DIN/471/ as the module's author read it on
2026-10-07; the page presents it as DIN 471 and the standard was not read.

No price LEVEL is asserted beyond a wide sanity band: the prices are declared
estimates, and ``tests/test_price.py`` lists the type as not measured.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import table_gates
import type_gates
from published import published_attributes
from synthetic_industrial_products.catalog import names, taxonomy, typespec
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate, generate_type
from synthetic_industrial_products.drawing import svg_problems
from synthetic_industrial_products.drawing.model import Lines, Poly
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "retaining_rings_external"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

DIMENSIONAL = {"DIN 471"}
#: The chart's ``d1``, ``d3``, ``s``, ``d2`` and ``m`` under the names they
#: are published as.
COLUMNS = (
    "For Shaft Diameter",
    "Inside Diameter",
    "Thickness",
    "Groove Diameter",
    "Groove Width",
)
#: ``(d1, d3, s, d2, m)`` in millimetres: twelve of the chart's sizes.
ROWS = {
    (6.0, 5.6, 0.7, 5.7, 0.8), (8.0, 7.4, 0.8, 7.6, 0.9), (10.0, 9.3, 1.0, 9.6, 1.1),
    (12.0, 11.0, 1.0, 11.5, 1.1), (15.0, 13.8, 1.0, 14.3, 1.1), (16.0, 14.7, 1.0, 15.2, 1.1),
    (20.0, 18.5, 1.2, 19.0, 1.3), (25.0, 23.2, 1.2, 23.9, 1.3), (30.0, 27.9, 1.5, 28.6, 1.6),
    (35.0, 32.2, 1.5, 33.0, 1.6), (40.0, 36.5, 1.75, 37.5, 1.85), (50.0, 45.8, 2.0, 47.0, 2.15),
}  # fmt: skip
#: Cheapest first.
MATERIALS = ("Steel", "Stainless Steel")
PACKS = {10, 50, 100}

#: A build large enough to reach every row in every material and pack.
LARGE_LINES = 39000
#: What the default build holds: a move is a change to the table or its share.
DEFAULT_SKUS = 82
#: USD for one pack, any size, material, pack and brand tier. Not a fit: a
#: price outside it is a broken ladder (ten small steel rings for cents, or a
#: hundred large stainless ones for thousands), not a wrong estimate.
SANITY_BAND = (0.50, 1500.0)

MM = table_gates.MM


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
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_type_does_not_also_exist_as_a_breadth_row():
    from synthetic_industrial_products.catalog import breadth

    assert [row.key for row in breadth.rows() if row.key == KEY] == []


def test_the_default_build_holds_the_declared_count():
    assert len(_default_docs()) == DEFAULT_SKUS


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert same_product_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in published_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_published_dimension_came_from(large_docs):
    problems, checked = type_gates.provenance_problems(large_docs, DIMENSIONAL, COLUMNS)
    assert problems == [], problems[:10]
    assert checked > 20, f"only {checked} dimensional claims were checked"


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


# --- the table ----------------------------------------------------------------------


def test_every_row_of_the_table_is_built_and_nothing_else(large_docs):
    assert {table_gates.row(doc, COLUMNS) for doc in large_docs} == ROWS


def test_every_material_and_pack_is_built_and_nothing_else(large_docs):
    published = [table_gates.values(doc) for doc in large_docs]
    assert {v["Material"]["value"] for v in published} == set(MATERIALS)
    assert {int(v[table_gates.PACK]["value_canonical"]) for v in published} == PACKS


def test_a_size_off_the_table_is_a_row_rewritten_by_an_injected_defect():
    """The build with its defects on shows more distinct sizes than the table
    has rows (14 against 12). Each extra one is a row's size rewritten in
    inches to four places, which reads back within a hundredth of a
    millimetre of that row: a defect the catalog injects on purpose, not a
    size the table lacks."""
    docs = table_gates.docs(table_gates.catalog(KEY, LARGE_LINES, defects=True))
    sizes = {row[0] for row in ROWS}
    read = [float(table_gates.values(doc)[COLUMNS[0]]["value_canonical"]) for doc in docs]
    assert sorted({round(size, 2) for size in read} - sizes) == []
    rewritten = [size for size in read if size not in sizes]
    assert len(rewritten) == 3, rewritten


# --- the declared price keeps its orders --------------------------------------------


def test_larger_dearer_material_and_bigger_pack_each_cost_more(large_docs):
    wrong, compared = table_gates.price_order(large_docs, KEY, COLUMNS[0], MATERIALS)
    assert wrong == [], f"{len(wrong)} wrong, e.g. {wrong[:4]}"
    assert min(compared.values()) > 20, f"too few pairs compared: {compared}"


def test_every_price_is_inside_the_sanity_band(large_docs):
    low, high = SANITY_BAND
    outside = [
        (doc["sku"], doc["price_usd"]) for doc in large_docs if not low <= doc["price_usd"] <= high
    ]
    assert outside == [], outside[:5]


# --- the drawing ---------------------------------------------------------------------


def test_every_row_has_a_drawing_and_no_two_rows_share_one(drawn):
    assert set(drawn) == ROWS
    assert len({svg for _, svg in drawn.values()}) == len(ROWS)


def test_each_drawing_is_scaled_from_its_row(drawn):
    """The ring's bore is the row's ``d3``, its edge view ``s`` thick, and the
    shaft under it ``d1`` across with a groove ``d2`` across and ``m`` wide."""
    for (d1, d3, s, d2, m), (figure, _) in drawn.items():
        assert figure.source == "record", (d1, figure.source)
        face, edge, shaft = (shape for shape in figure.figure.shapes if isinstance(shape, Poly))
        (floor,) = (shape for shape in figure.figure.shapes if isinstance(shape, Lines))
        bore = min((x * x + y * y) ** 0.5 for x, y in face.points)
        assert 2 * bore == pytest.approx(d3 / MM, rel=1e-6), d1
        edge_x = [x for x, _ in edge.points]
        assert max(edge_x) - min(edge_x) == pytest.approx(s / MM, rel=1e-6), d1
        shaft_y = sorted({round(y, 9) for _, y in shaft.points})
        assert shaft_y[-1] - shaft_y[0] == pytest.approx(d1 / MM, rel=1e-6), d1
        # The groove's far wall is the cut in the shaft's outline, its near
        # wall the line across the shaft.
        ((left, right),) = floor.segments
        assert shaft_y[1] - left[1] == pytest.approx(d2 / MM, rel=1e-6), d1
        assert right[0] - left[0] == pytest.approx(m / MM, rel=1e-6), d1


def test_no_drawing_carries_text_and_the_largest_is_small(drawn):
    assert [problem for _, svg in drawn.values() for problem in svg_problems(svg)] == []
    assert max(len(svg) for _, svg in drawn.values()) < 8000


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
