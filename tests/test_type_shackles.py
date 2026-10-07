"""Per-type gates for ``shackles``, a table-driven type (#101).

The template's gates (uniqueness, census names, provenance, byte-determinism
under two hash seeds, a golden slice, independence from every other type), and
on top of them what a table type promises (:mod:`table_gates`): every size it
builds is a row of its table, its declared prices rise with size, and every
row has a drawing scaled from that row.

The tables are restated here, not read from the module, so a figure typed
wrong in the module goes red. They are tables VIII, X and XIII of US Federal
Specification RR-C-271F (5 July 2011) as the module's author read them on
2026-10-07 in the copy at https://everyspec.com/FED_SPECS/R/RR-C-271F_35870/.

A shackle is sold each, in one material, so of a table type's three price
orders only the size order has pairs to compare. No price LEVEL is asserted
beyond a wide sanity band: the prices are declared estimates, and
``tests/test_price.py`` lists the type as not measured.
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
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "shackles"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

DIMENSIONAL = {"RR-C-271"}
#: The trade size, the width between the eyes (W) and the length inside (L)
#: under the names they are published as.
COLUMNS = ("Size", "Inside Width", "Inside Length")
LOAD = "Load Capacity"

MM = table_gates.MM

#: Inches and pounds, eleven trade sizes: ``(size, D min, P min, W, R max,
#: anchor L, anchor B, chain L, grade A working load limit)``. D is the body
#: diameter, P the pin diameter, R the outside diameter of the eye, B the
#: width of the bow. Tables X and XIII agree on D, P, W and R but for one R.
SPECIFICATION = (
    (0.25, 0.24, 0.30, 0.469, 0.875, 1.125, 0.75, 0.875, 1000),
    (0.3125, 0.30, 0.37, 0.531, 1.0, 1.250, 0.812, 1.031, 1500),
    (0.375, 0.36, 0.43, 0.656, 1.125, 1.438, 0.938, 1.125, 2000),
    (0.4375, 0.42, 0.49, 0.750, 1.25, 1.688, 1.062, 1.438, 3000),
    (0.5, 0.48, 0.61, 0.812, 1.375, 1.875, 1.188, 1.625, 4000),
    (0.625, 0.59, 0.73, 1.062, 1.875, 2.375, 1.5, 2.000, 6500),
    (0.75, 0.71, 0.85, 1.250, 2.125, 2.812, 1.75, 2.375, 9500),
    (0.875, 0.83, 0.98, 1.438, 2.375, 3.312, 2.0, 2.812, 13000),
    (1.0, 0.95, 1.10, 1.688, 2.625, 3.75, 2.312, 3.188, 17000),
    (1.125, 1.07, 1.22, 1.812, 2.875, 4.25, 2.625, 3.562, 19000),
    (1.25, 1.19, 1.34, 2.031, 3.25, 4.688, 2.875, 3.938, 24000),
)
#: Table XIII's eye for the 3/8 in chain shackle; table X prints 1.125.
CHAIN_EYE = {0.375: 1.25}


def _mm(*inches: float) -> tuple[float, ...]:
    """As ``table_gates.row`` reads a record. The product is cleaned to six
    places first: 7/16 in is 11.1125 mm exactly, and the float product falls
    just under it and would round the other way."""
    return tuple(round(float(f"{value * MM:.6f}"), 3) for value in inches)


#: The built row, in millimetres, of each body and trade size.
ANCHOR_ROWS = {_mm(s, w, length): s for s, _, _, w, _, length, _, _, _ in SPECIFICATION}
CHAIN_ROWS = {_mm(s, w, length): s for s, _, _, w, _, _, _, length, _ in SPECIFICATION}
ROWS = set(ANCHOR_ROWS) | set(CHAIN_ROWS)
BY_SIZE = {row[0]: row for row in SPECIFICATION}
#: ``(Type, size in millimetres)`` to the load in pounds, as published.
LOADS = {
    (body, _mm(row[0])[0]): str(row[8]) for row in SPECIFICATION for body in ("Anchor", "Chain")
}

MATERIALS = ("Forged Steel",)
PACKS = {1}

#: A build large enough to reach every row of both bodies.
LARGE_LINES = 39000
#: What the default build holds: a move is a change to the table or its share.
DEFAULT_SKUS = 132
DEFAULT_PRODUCTS = 74
#: The large build runs out of shackles: 22 rows from each of 17 brands.
LARGE_SKUS = 374
#: USD for one shackle, any size and brand tier. Not a fit: a price outside
#: it is a broken ladder, not a wrong estimate.
SANITY_BAND = (4.0, 500.0)
#: The drawn pin head and thread end, in pin diameters: nominal, since the
#: tables give the pin's diameter only. Collar plus tab, then the thread end.
HEAD = 0.3 + 0.9
THREAD_END = 0.15


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
    """Keyed as ``ROWS`` is. ``table_gates.drawings`` multiplies inches out
    itself, so its 7/16 in is 11.112 where a record reads 11.113: a key within
    two thousandths of a row is that row, and any other key is kept as built."""

    def row(key: tuple[float, ...]) -> tuple[float, ...]:
        near = [r for r in ROWS if all(abs(a - b) <= 0.002 for a, b in zip(r, key, strict=True))]
        return near[0] if len(near) == 1 else key

    built = table_gates.drawings(large, KEY, COLUMNS)
    keyed = {row(key): drawing for key, drawing in built.items()}
    assert len(keyed) == len(built)
    return keyed


# --- the template's gates ---------------------------------------------------------


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is not a modelled type"


def test_the_type_does_not_also_exist_as_a_breadth_row():
    from synthetic_industrial_products.catalog import breadth

    assert [row.key for row in breadth.rows() if row.key == KEY] == []


def test_the_default_build_holds_the_declared_count():
    docs = _default_docs()
    assert len(docs) == DEFAULT_SKUS
    assert len({doc["product_id"] for doc in docs}) == DEFAULT_PRODUCTS


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert same_product_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in published_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_published_figure_came_from(large_docs):
    problems, checked = type_gates.provenance_problems(large_docs, DIMENSIONAL, (*COLUMNS, LOAD))
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
    """Regenerate with ``uv run python tests/test_type_shackles.py``."""
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


# --- the tables ----------------------------------------------------------------------


def test_every_row_of_both_tables_is_built_and_nothing_else(large_docs):
    assert len(ROWS) == 22
    assert len(large_docs) == LARGE_SKUS
    assert {table_gates.row(doc, COLUMNS) for doc in large_docs} == ROWS


def test_each_body_is_built_at_its_own_tables_length(large_docs):
    """An anchor shackle is longer inside than the chain shackle of its size,
    so a row names its body."""
    wrong = []
    for doc in large_docs:
        published = table_gates.values(doc)
        rows = ANCHOR_ROWS if published["Type"]["value"] == "Anchor" else CHAIN_ROWS
        if table_gates.row(doc, COLUMNS) not in rows:
            wrong.append((doc["sku"], published["Type"]["value"]))
    assert wrong == []
    assert {table_gates.values(doc)["Type"]["value"] for doc in large_docs} == {"Anchor", "Chain"}
    assert {table_gates.values(doc)["Item"]["value"] for doc in large_docs} == {
        "Screw Pin Anchor Shackle",
        "Screw Pin Chain Shackle",
    }


def test_each_size_carries_the_grade_a_working_load_limit(large_docs):
    built = {}
    for doc in large_docs:
        published = table_gates.values(doc)
        size = round(float(published["Size"]["value_canonical"]), 3)
        built.setdefault((published["Type"]["value"], size), set()).add(published[LOAD]["value"])
        assert published[LOAD]["unit_code"] == "LBR", doc["sku"]
    assert built == {cell: {load} for cell, load in LOADS.items()}


def test_the_one_material_finish_and_pack_are_built_and_nothing_else(large_docs):
    published = [table_gates.values(doc) for doc in large_docs]
    assert {v["Material"]["value"] for v in published} == set(MATERIALS)
    assert {v["Finish"]["value"] for v in published if "Finish" in v} == {"Hot Dip Galvanized"}
    assert {int(v[table_gates.PACK]["value_canonical"]) for v in published} == PACKS


def test_one_product_publishes_exactly_these_attributes():
    """The first SKU of the default build: a 1/4 in anchor shackle."""
    doc = _default_docs()[0]
    assert {a["name"]: a["value"] for a in doc["attributes"]} == {
        "Item": "Screw Pin Anchor Shackle",
        "Type": "Anchor",
        "Material": "Forged Steel",
        "Finish": "Hot Dip Galvanized",
        "Package Quantity": "1",
        "Standards": "RR-C-271",
        "Size": "1/4",
        "Inside Width": "0.4690",
        "Inside Length": "1-1/8",
        "Load Capacity": "1000",
        "Dimension Type": "Fractional Inch",
    }
    assert doc["price_usd"] == 11.01
    assert doc["dimension_provenance"] == (
        "Size and Inside Width and Inside Length and Load Capacity read from the RR-C-271 table"
    )


def test_no_dimension_the_census_cannot_name_is_published(large_docs):
    """The pin, body, bow and eye diameters are drawn, not published."""
    published = {a["name"] for doc in large_docs for a in doc["attributes"]}
    assert sorted(published) == [
        "Dimension Type",
        "Finish",
        "Inside Length",
        "Inside Width",
        "Item",
        "Load Capacity",
        "Material",
        "Measurement System",
        "Package Quantity",
        "Size",
        "Standards",
        "System of Measurement",
        "Type",
    ]


def test_a_size_off_the_table_is_a_row_rewritten_by_an_injected_defect():
    """The build with its defects on shows two sizes no table has (9.52 mm and
    28.57 mm). Each is a row's size rewritten in millimetres to two places,
    which reads back within a hundredth of a millimetre of that row: a defect
    the catalog injects on purpose, not a size the table lacks."""
    docs = table_gates.docs(table_gates.catalog(KEY, LARGE_LINES, defects=True))
    sizes = [size * MM for size in BY_SIZE]
    read = [float(table_gates.values(doc)["Size"]["value_canonical"]) for doc in docs]
    nearest = [min(abs(size - row) for row in sizes) for size in read]
    assert [gap for gap in nearest if gap > 0.01] == []
    rewritten = sorted({size for size, gap in zip(read, nearest, strict=True) if gap > 1e-6})
    assert rewritten == [9.52, 28.57]


# --- the declared price keeps its order ----------------------------------------------


def test_a_larger_shackle_costs_more_at_every_brand_tier(large_docs):
    """Ten neighbouring pairs of sizes at each of three tiers. One material
    and one pack leave the other two orders nothing to compare."""
    wrong, compared = table_gates.price_order(large_docs, KEY, "Size", MATERIALS)
    assert wrong == [], f"{len(wrong)} wrong, e.g. {wrong[:4]}"
    assert compared == {"size": 30, "material": 0, "pack": 0}


def test_both_bodies_of_a_size_cost_the_same(large_docs):
    from synthetic_industrial_products.catalog import brands

    prices = {}
    for doc in large_docs:
        published = table_gates.values(doc)
        cell = (brands.tier_of(doc["brand"], KEY), published["Size"]["value"])
        prices.setdefault(cell, set()).add(doc["price_usd"])
    assert len(prices) == 33
    assert [cell for cell, seen in prices.items() if len(seen) != 1] == []


def test_every_price_is_inside_the_sanity_band(large_docs):
    low, high = SANITY_BAND
    outside = [
        (doc["sku"], doc["price_usd"]) for doc in large_docs if not low <= doc["price_usd"] <= high
    ]
    assert outside == [], outside[:5]
    assert min(doc["price_usd"] for doc in large_docs) == 5.72
    assert max(doc["price_usd"] for doc in large_docs) == 356.04


# --- the drawing ---------------------------------------------------------------------


def test_every_row_has_a_drawing_and_no_two_rows_share_one(drawn):
    assert set(drawn) == ROWS
    assert len({svg for _, svg in drawn.values()}) == len(ROWS)


def test_each_drawing_is_scaled_from_its_row(drawn):
    """Top to bottom: the eye below the pin's axis, half the pin, the length
    inside, the body. Side to side: the pin with its head on the left, or the
    bow where it bulges past the eyes."""
    for row, (figure, _) in drawn.items():
        chain = row in CHAIN_ROWS
        size, stock, pin, width, eye, anchor_length, bow, chain_length, _ = BY_SIZE[
            (CHAIN_ROWS if chain else ANCHOR_ROWS)[row]
        ]
        length = chain_length if chain else anchor_length
        if chain:
            bow, eye = width, CHAIN_EYE.get(size, eye)
        assert figure.source == "record", (row, figure.source)
        x0, y0, x1, y1 = figure.figure.bounds()
        assert y1 - y0 == pytest.approx(eye / 2 + pin / 2 + length + stock, rel=1e-6), row
        left = max(width / 2 + stock + HEAD * pin, bow / 2 + stock)
        right = max(width / 2 + stock + THREAD_END * pin, bow / 2 + stock)
        assert x1 - x0 == pytest.approx(left + right, rel=1e-6), row


def test_an_anchor_body_bulges_and_a_chain_body_has_straight_sides(drawn):
    """The right edge of the drawing is the bow on every anchor shackle and
    the pin's thread end on every chain shackle."""
    bulging = {"anchor": 0, "chain": 0}
    for row, (figure, _) in drawn.items():
        chain = row in CHAIN_ROWS
        _, stock, pin, width, *_ = BY_SIZE[(CHAIN_ROWS if chain else ANCHOR_ROWS)[row]]
        leg = width / 2 + stock + THREAD_END * pin
        if figure.figure.bounds()[2] > leg + 1e-9:
            bulging["chain" if chain else "anchor"] += 1
    assert bulging == {"anchor": 11, "chain": 0}


def test_no_drawing_carries_text_and_the_largest_is_small(drawn):
    assert [problem for _, svg in drawn.values() for problem in svg_problems(svg)] == []
    assert max(len(svg) for _, svg in drawn.values()) < 8000


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
