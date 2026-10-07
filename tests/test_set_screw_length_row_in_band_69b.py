"""The set screw's longer-costs-more row is reachable,
so it is held in band at both builds rather than pinned.

The census orders a set screw's sizes loosely (0.666 of 311 pairs, length
held) and its lengths tightly (0.834 of 692 pairs, diameter held), on slopes
that are close (0.324 and 0.363). Noise drawn per SKU inverts both kinds of
pair alike, so it cannot meet both shares; noise a diameter shares across its
lengths (``price.SIZE_NOISE``) inverts a size pair and leaves a length pair
alone. With that noise fitted, both rows land in band at both builds.
"""

from __future__ import annotations

import pytest

from synthetic_industrial_products.catalog import price, price_report
from synthetic_industrial_products.catalog.config import HUNDRED_K_LINES, GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.catalog.price_report import LENGTH_ROW, ORDER_ROW

SET_SCREW = "set_screws_hex_socket"


@pytest.fixture(scope="module", params=["default", "100K"])
def rows(request) -> dict:
    config = (
        GeneratorConfig() if request.param == "default" else GeneratorConfig(lines=HUNDRED_K_LINES)
    )
    return {row.name: row for row in price_report.price_comparisons(generate(config))}


def test_no_set_screw_row_is_pinned():
    pinned = {name for name in price.PINNED_SHORTFALLS if name.endswith(f": {SET_SCREW}")}
    assert pinned == set()
    assert {name for name in price.PINNED_FIGURES if name.endswith(f": {SET_SCREW}")} == set()


@pytest.mark.parametrize("row_name", [LENGTH_ROW, ORDER_ROW])
def test_a_set_screws_size_and_length_rows_are_both_in_band(rows, row_name):
    row = rows[row_name.format(SET_SCREW)]
    assert row.within is True, (row.name, row.achieved, row.band)
