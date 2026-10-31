"""Industrial sizes draw apart: a measured figure by its own dimension, a fixed shape by its rank.

A bolt or an end mill is drawn from the SKU's own values at one true scale per type, so a longer
bolt is already a longer drawing and a rank on top would shrink it twice. A breadth product is one
fixed shape, so its sizes shared a picture until ``breadth_rungs`` put them on the ladder retail
reads (gen#719). These tests read the committed catalog.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import bundle, size_rungs
from synthetic_ecommerce_data.core.drawing import FIGURES, draw_product
from synthetic_ecommerce_data.domains.industrial import breadth
from synthetic_ecommerce_data.domains.industrial.drawing import breadth_rungs

GOLDEN = Path(__file__).resolve().parent.parent / "golden-catalog"
FACETS = bundle.flat_facets(GOLDEN)
PARENTS = [json.loads(line) for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines()]
ROWS = {row.key: row for row in breadth.rows()}
#: The size attributes the census must reach: the one each kind of value is sold by.
LADDERS = [p for p in PARENTS if p["product_type"] in ROWS and len(p["variants"]) > 1
           and ROWS[p["product_type"]].size_attr not in breadth_rungs.NOT_SIZES]  # fmt: skip


def _parent(product_type: str) -> dict:
    return next(p for p in PARENTS if p["product_type"] == product_type and len(p["variants"]) > 2)


def _height(product_type: str, record: dict) -> float:
    _, y0, _, y1 = FIGURES[product_type][0](dict(record)).figure.bounds()
    return y1 - y0


def _inches(text: str) -> float:
    """A bolt length in millimeters, for the order only: "25mm", '1-1/4"'."""
    if text.endswith("mm"):
        return float(text[:-2]) / 25.4
    whole, _, fraction = text.rstrip('"').rpartition("-")
    if "/" not in fraction:
        return float(fraction)
    top, bottom = fraction.split("/")
    return float(whole or 0) + float(top) / float(bottom)


def _ratios(product_type: str, records: list[dict]) -> list[float]:
    """``ratios``, where a record it cannot read fails the test rather than erroring it."""
    try:
        return breadth_rungs.ratios(product_type, records)
    except (KeyError, ZeroDivisionError) as exc:
        raise AssertionError(f"{product_type}: {exc!r}") from exc


def test_each_length_of_a_bolt_draws_a_longer_bolt():
    bolts = [p for p in PARENTS if p["product_type"] == "bolt_hex" and len(p["variants"]) > 2]
    assert bolts
    for parent in bolts:
        records = sorted(bundle.records(parent, FACETS), key=lambda r: _inches(r["Length"]))
        heights = [_height("bolt_hex", r) for r in records]
        assert heights == sorted(set(heights)), parent["product_id"]
        svgs = {data for data, _ in draw_product("bolt_hex", parent["brand"], records)}
        assert len(svgs) == len(records), parent["product_id"]


def test_each_diameter_of_an_end_mill_draws_its_own_picture():
    parent = _parent("end_mill_square")
    records = bundle.records(parent, FACETS)
    assert len({r["Milling Dia."] for r in records}) > 1
    assert len({d for d, _ in draw_product("end_mill_square", parent["brand"], records)}) > 1


@pytest.mark.parametrize("product_type", ["bolt_hex", "end_mill_square"])
def test_a_measured_figure_stays_at_its_true_scale(product_type):
    records = bundle.records(_parent(product_type), FACETS)
    assert breadth_rungs.ratios(product_type, records) == [1.0] * len(records)


def test_the_census_of_breadth_ladders_is_not_empty():
    assert len(LADDERS) > 50


def test_each_size_of_a_breadth_product_draws_apart():
    for parent in LADDERS:
        attr = ROWS[parent["product_type"]].size_attr
        records = bundle.records(parent, FACETS)
        drawn = draw_product(parent["product_type"], parent["brand"], records)
        by_size: dict[str, set[bytes]] = {}
        for record, (data, _) in zip(records, drawn, strict=True):
            by_size.setdefault(record[attr], set()).add(data)
        images = [d for shared in by_size.values() for d in shared]
        assert len(images) == len(set(images)), parent["product_id"]


def test_a_breadth_ladder_runs_from_the_smallest_rung_to_the_full_drawing():
    for parent in LADDERS:
        records = bundle.records(parent, FACETS)
        attr = ROWS[parent["product_type"]].size_attr
        if len({r[attr] for r in records}) < 2:
            continue
        ratios = breadth_rungs.ratios(parent["product_type"], records)
        assert min(ratios) == pytest.approx(size_rungs.BOTTOM / size_rungs.TOP)
        assert max(ratios) == 1.0


def test_a_rung_is_read_from_the_size_not_the_order_of_the_records():
    row = next(r for r in ROWS.values() if r.size_attr == "Diameter")
    records = [{"Diameter": "2 in"}, {"Diameter": "1/2 in"}, {"Diameter": "1 in"}]
    ratios = breadth_rungs.ratios(row.key, records)
    assert ratios[1] < ratios[2] < ratios[0] == 1.0


def test_a_published_sentence_case_name_reads_the_same_rung():
    row = next(r for r in ROWS.values() if r.size_attr == "Container Size")
    authored = [{"Container Size": "4 oz"}, {"Container Size": "10 oz"}]
    published = [{"Container size": "4 oz"}, {"Container size": "10 oz"}]
    assert _ratios(row.key, published) == _ratios(row.key, authored)


@pytest.mark.parametrize("attr", sorted(breadth_rungs.NOT_SIZES))
def test_a_kind_a_count_or_a_rating_shares_one_picture(attr):
    row = next(r for r in ROWS.values() if r.size_attr == attr)
    records = [{attr: value} for value in row.size_values]
    assert len(records) > 1
    assert breadth_rungs.ratios(row.key, records) == [1.0] * len(records)


def test_a_product_of_one_size_is_not_scaled():
    row = next(r for r in ROWS.values() if r.size_attr == "Diameter")
    records = [{"Diameter": "1 in", "Material": "Steel"}, {"Diameter": "1 in", "Material": "Brass"}]
    assert _ratios(row.key, records) == [1.0, 1.0]


def test_a_sku_drawn_alone_reads_no_size():
    row = next(r for r in ROWS.values() if r.size_attr == "Diameter")
    assert _ratios(row.key, [{"Material": "Steel"}]) == [1.0]


@pytest.mark.parametrize(
    "values",
    [
        pytest.param(["#8-32", "1/4-20", "M8x1.25", "1/2-13"], id="gauge-fraction-metric-threads"),
        pytest.param(["3/4 in", "1 in", "1-1/2 in", "4-1/2 in", "64-1/2 in"], id="mixed-numbers"),
        pytest.param(["400 g", "1 kg"], id="grams-under-a-kilo"),
        pytest.param(["1.3 mm", "10 mm"], id="metric-decimals"),
        pytest.param(["Small", "Medium", "Large", "X-Large"], id="words"),
        pytest.param(["3/4 in to 2 in", "1 in to 2-1/2 in"], id="a-range-by-its-lower-end"),
        pytest.param(["M3 to M12", "M6 to M20"], id="a-metric-range"),
        pytest.param(["6 Slots", "12 Slots"], id="what-it-holds"),
        pytest.param(["4 oz", "10 oz"], id="ounces"),
    ],
)
def test_sizes_rank_by_what_they_measure(values):
    measures = [breadth_rungs.measure(v) for v in values]
    assert measures == sorted(set(measures))


@pytest.mark.parametrize("value", ["Huge", "3 parsecs"])
def test_a_value_with_no_place_on_a_ladder_is_refused(value):
    with pytest.raises(ValueError, match="no place on a size ladder"):
        breadth_rungs.measure(value)


def test_every_size_a_row_sells_has_a_place():
    for row in ROWS.values():
        if row.size_attr not in breadth_rungs.NOT_SIZES:
            for value in row.size_values:
                try:
                    breadth_rungs.measure(value)
                except ValueError as exc:
                    raise AssertionError(f"{row.key}: {exc}") from exc
