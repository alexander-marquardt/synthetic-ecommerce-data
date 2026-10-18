"""Per-type gates for ``turnbuckles``, a table-driven type (#101).

The template's gates (uniqueness, census names, provenance, byte-determinism
under two hash seeds, a golden slice, independence from every other type), and
on top of them what a table type promises (:mod:`table_gates`): every size it
builds is a row of its table, its declared price rises with the size, and
every row has a drawing scaled from that row.

A turnbuckle's closed length and working load limit depend on its end fitting
as well as its size, so the table is restated here per end fitting, not read
from the module: a figure typed wrong in the module goes red. It is the chart
at http://www.chicagohardware.com/catalog/04_07_Fturnbuckles.pdf as the
module's author read it on 2026-10-07; the pages say the turnbuckles meet
ASTM F1145 and the standard was not read.

No price LEVEL is asserted beyond one declared base and a wide sanity band:
the prices are declared estimates, and ``tests/test_price.py`` lists the type
as not measured. A turnbuckle is sold singly, so there is no pack order to
hold, and the ladder has no end-fitting term.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import table_gates
import type_gates
from published import authored_attributes
from synthetic_ecommerce_data.core import brands, emit, typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.dimensions import parse_length
from synthetic_ecommerce_data.core.drawing import FIGURES, draw_sku, svg_problems
from synthetic_ecommerce_data.domains.industrial import names, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from synthetic_ecommerce_data.domains.industrial.product_types.fasteners import turnbuckles
from synthetic_ecommerce_data.domains.industrial.vocab import MEASUREMENT_SYSTEM_NAMES
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "turnbuckles"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

DIMENSIONAL = {"ASTM F1145"}
#: The published lengths, the size first.
LENGTHS = ("Thread Size", "Take Up", "Closed Length")
#: ``(thread diameter, take-up)`` in inches: the chart's eight diameters, each
#: at one take-up.
SIZES = (
    (0.25, 4.0), (0.3125, 4.5), (0.375, 6.0), (0.5, 6.0),
    (0.625, 6.0), (0.75, 6.0), (0.875, 6.0), (1.0, 6.0),
)  # fmt: skip
#: Each end-fitting pair's closed length (inches) and working load limit
#: (pounds), in the order of ``SIZES``. The eye's limit is the jaw's; the
#: pair with a hook carries the hook's, which is lower at every size.
CLOSED = {
    "Eye and Eye": (8.0, 9.0, 11.5, 13.0, 13.5, 14.75, 18.0, 17.0),
    "Jaw and Jaw": (8.5, 9.25, 11.5, 13.5, 15.75, 16.5, 19.5, 20.1875),
    "Hook and Eye": (8.25, 9.25, 11.75, 13.625, 14.125, 15.75, 18.5, 19.5),
}
LIMIT = {
    "Eye and Eye": (500, 800, 1200, 2200, 3500, 5200, 7200, 10000),
    "Jaw and Jaw": (500, 800, 1200, 2200, 3500, 5200, 7200, 10000),
    "Hook and Eye": (400, 700, 1000, 1500, 2250, 3000, 3200, 5000),
}
#: Every ``(end fitting, thread diameter, take-up, closed length, limit)``.
CELLS = {
    (end, dia, take_up, CLOSED[end][i], LIMIT[end][i])
    for end in CLOSED
    for i, (dia, take_up) in enumerate(SIZES)
}

#: A build large enough to reach every size with every end fitting.
LARGE_LINES = 39000
#: What the default build holds: a move is a change to the table or its share.
DEFAULT_PRODUCTS = 42
DEFAULT_SKUS = 87
#: USD each, any size and brand tier. Not a fit: a price outside it is a
#: broken ladder, not a wrong estimate.
SANITY_BAND = (5.0, 400.0)
#: The drawn height, in thread diameters: nominal, the chart gives none.
HEIGHT = 3.0


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _cell(doc: dict) -> tuple:
    """A document's end fitting and table figures, lengths in inches."""
    published = table_gates.values(doc)
    inches = [
        round(float(published[name]["value_canonical"]) / table_gates.MM, 4) for name in LENGTHS
    ]
    return (
        published["End Style"]["value"],
        *inches,
        int(published["Load Capacity"]["value_canonical"]),
    )


@pytest.fixture(scope="module")
def large():
    return table_gates.catalog(KEY, LARGE_LINES)


@pytest.fixture(scope="module")
def large_docs(large) -> list[dict]:
    return table_gates.docs(large)


@pytest.fixture(scope="module")
def drawn(large) -> dict[tuple, tuple]:
    """One drawing per end fitting and size the build reaches: the figure, and
    the SVG in ONE brand's house style, so two differ only by their geometry."""
    figure, _ = FIGURES[KEY]
    found: dict[tuple, tuple] = {}
    brand = large.lines[0].brand
    for line, child in large.all_skus():
        record = emit.drawing_record(large, line, child)
        cell = (
            record["End Style"],
            *(round(parse_length(record[name]).inches, 4) for name in LENGTHS),
        )
        if cell not in found:
            svg, _ = draw_sku(KEY, brand, record)
            found[cell] = (figure(dict(record)), svg)
    return found


# --- the template's gates ---------------------------------------------------------


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_type_does_not_also_exist_as_a_breadth_row():
    from synthetic_ecommerce_data.domains.industrial import breadth

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
    emitted = {a["name"] for doc in _default_docs() for a in authored_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_published_dimension_came_from(large_docs):
    problems, checked = type_gates.provenance_problems(large_docs, DIMENSIONAL, LENGTHS)
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
    """Regenerate with ``uv run python tests/test_type_turnbuckles.py``."""
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


def test_the_module_states_the_chart_as_restated_here():
    assert turnbuckles.ROWS == SIZES
    assert turnbuckles.CLOSED_IN == CLOSED
    assert turnbuckles.LIMIT_LB == LIMIT
    assert turnbuckles.TABLE.unit == "in"


def test_every_size_is_built_with_every_end_fitting_and_nothing_else(large_docs):
    assert len(CELLS) == 24
    assert {_cell(doc) for doc in large_docs} == CELLS


def test_a_hook_end_carries_less_than_an_eye_at_every_size():
    pairs = list(zip(LIMIT["Hook and Eye"], LIMIT["Eye and Eye"], strict=True))
    assert len(pairs) == 8
    assert [hook for hook, eye in pairs if not hook < eye] == []


def test_one_material_one_finish_and_sold_singly(large_docs):
    published = [table_gates.values(doc) for doc in large_docs]
    assert {v["Material"]["value"] for v in published} == {"Steel"}
    assert {v["Finish"]["value"] for v in published if "Finish" in v} == {"Hot Dip Galvanized"}
    assert {int(v[table_gates.PACK]["value_canonical"]) for v in published} == {1}


def test_one_product_publishes_exactly_its_row(large_docs):
    """The 1/2" jaw and jaw, whichever brand's: every attribute but the ones
    a feed may leave out (the finish, the standards claim, the measurement
    system), and the load limit in the bearing's spelling."""
    docs = [doc for doc in large_docs if _cell(doc)[:2] == ("Jaw and Jaw", 0.5)]
    assert len(docs) > 5, len(docs)
    for doc in docs:
        published = table_gates.values(doc)
        published.pop("Finish", None)
        for name, _ in MEASUREMENT_SYSTEM_NAMES:
            published.pop(name, None)
        claimed = published.pop("Standards", None)
        assert claimed is None or claimed["value"] == "ASTM F1145"
        measured = {n: a["value_canonical"] for n, a in published.items() if "unit_code" in a}
        assert measured == {
            "Units per Pack": 1.0,
            "Thread Size": 12.7,
            "Take Up": 152.4,
            "Closed Length": 342.9,
            "Load Capacity": 2200.0,
        }
        assert {name: a["value"] for name, a in published.items() if "unit_code" not in a} == {
            "Material": "Steel",
            "End Style": "Jaw and Jaw",
        }
        assert published["Load Capacity"]["unit_code"] == "C78"
        assert "Jaw and Jaw" in doc["title"], doc["title"]


# --- the declared price rises with the size -----------------------------------------


def test_a_larger_thread_costs_more_at_every_brand_tier(large_docs):
    wrong, compared = table_gates.price_order(large_docs, KEY, "Thread Size", ("Steel",))
    assert wrong == [], f"{len(wrong)} wrong, e.g. {wrong[:4]}"
    assert compared["size"] > 13, f"too few pairs compared: {compared}"


def test_the_smallest_costs_the_declared_base_at_the_standard_tier(large_docs):
    """The declared 15.50, moved a cent: the ending rule keeps a table price
    off the .50 class."""
    prices = {
        doc["price_usd"]
        for doc in large_docs
        if _cell(doc)[1] == 0.25 and brands.tier_of(doc["brand"], KEY) == "standard"
    }
    assert prices == {15.51}


def test_every_price_is_inside_the_sanity_band(large_docs):
    low, high = SANITY_BAND
    outside = [
        (doc["sku"], doc["price_usd"]) for doc in large_docs if not low <= doc["price_usd"] <= high
    ]
    assert outside == [], outside[:5]


# --- the drawing ---------------------------------------------------------------------


def test_every_cell_has_a_drawing_and_no_two_share_one(drawn):
    assert set(drawn) == {cell[:4] for cell in CELLS}
    assert len({svg for _, svg in drawn.values()}) == 24


def test_each_drawing_is_scaled_from_its_row(drawn):
    """It is the row's closed length long and three thread diameters high."""
    for (end, dia, _, closed), (figure, _) in drawn.items():
        assert figure.source == "record", (end, dia, figure.source)
        x0, y0, x1, y1 = figure.figure.bounds()
        assert x1 - x0 == pytest.approx(closed, rel=1e-6), (end, dia)
        assert y1 - y0 == pytest.approx(HEIGHT * dia, rel=1e-6), (end, dia)


def test_the_largest_drawing_fits_the_declared_extent(drawn):
    boxes = [figure.figure.bounds() for figure, _ in drawn.values()]
    assert max(x1 - x0 for x0, _, x1, _ in boxes) == pytest.approx(20.1875)
    assert max(y1 - y0 for _, y0, _, y1 in boxes) == pytest.approx(3.0)
    assert turnbuckles.TABLE.extent == (20.3, 3.1)


def test_a_record_without_its_closed_length_is_drawn_from_the_tables():
    figure, _ = FIGURES[KEY]
    record = {"Thread Size": '1/2"', "Take Up": '6"', "End Style": "Hook and Eye"}
    partial = figure(record)
    assert partial.source == "partial"
    x0, _, x1, _ = partial.figure.bounds()
    assert x1 - x0 == pytest.approx(13.625)
    whole = figure({**record, "Closed Length": '13-5/8"'})
    assert whole.source == "record"
    assert whole.figure == partial.figure


def test_each_end_fitting_is_drawn_differently():
    values = {"Thread Size": 0.5, "Take Up": 6.0, "Closed Length": 13.5}
    figures = [turnbuckles.draw(values, end).shapes for end in CLOSED]
    assert len(figures) == 3
    assert figures[0] != figures[1] != figures[2] != figures[0]


def test_no_drawing_carries_text_and_the_largest_is_small(drawn):
    assert [problem for _, svg in drawn.values() for problem in svg_problems(svg)] == []
    assert max(len(svg) for _, svg in drawn.values()) < 8000


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
