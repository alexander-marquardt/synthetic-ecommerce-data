"""The lock nuts and the hex socket set screws are scored against their own
census bands (#69 part B), as every other census type is."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import price
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.measure import measure
from synthetic_ecommerce_data.domains.industrial.price_report import (
    LENGTH_ROW,
    ORDER_ROW,
    P50_BAND,
    SPREAD_BAND,
    SPREAD_ROW,
)

CENSUS_FILE = (
    Path(__file__).resolve().parent.parent / "reference-statistics" / "P2_price_census.json"
)
TYPES = ("lock_nuts_nylon_insert", "set_screws_hex_socket")


@pytest.fixture(scope="module")
def rows() -> dict:
    stats = measure(generate(GeneratorConfig()), GeneratorConfig())
    return {row.name: row for row in stats["comparisons"] if row.band is not None}


@pytest.mark.parametrize("type_key", TYPES)
def test_each_type_is_restated_from_its_census_entry_and_fitted(type_key):
    entry = json.loads(CENSUS_FILE.read_text())["deep_types"][type_key]
    quantiles = entry["price_quantiles_usd"]
    slope = entry["price_vs_key_dimension"]
    assert type_key in price.CENSUS
    stated = price.CENSUS[type_key]
    assert (stated.n, stated.p10, stated.p50, stated.p90) == (
        entry["n"],
        quantiles["p10"],
        quantiles["p50"],
        quantiles["p90"],
    )
    assert (stated.slope, stated.larger_costs_more, stated.n_pairs) == (
        slope["loglog_slope"],
        slope["share_larger_costs_more"],
        slope["n_pairs"],
    )
    assert price.model_for(type_key).measured is True


@pytest.mark.parametrize("type_key", TYPES)
def test_each_types_rows_are_scored_against_its_own_census_band(rows, type_key):
    entry = json.loads(CENSUS_FILE.read_text())["deep_types"][type_key]
    q = entry["price_quantiles_usd"]
    assert f"price p50 (USD): {type_key}" in rows
    p50 = rows[f"price p50 (USD): {type_key}"]
    assert p50.band == (q["p50"] * P50_BAND[0], q["p50"] * P50_BAND[1])
    spread = rows[SPREAD_ROW.format(type_key)]
    target = q["p90"] / q["p10"]
    assert spread.band == (target * SPREAD_BAND[0], target * SPREAD_BAND[1])
    assert ORDER_ROW.format(type_key) in rows


def test_the_set_screws_length_row_is_scored_against_the_census_length_share(rows):
    entry = json.loads(CENSUS_FILE.read_text())["deep_types"]["set_screws_hex_socket"]
    length = entry["price_vs_length_at_fixed_diameter"]
    assert "set_screws_hex_socket" in price.LENGTH_CENSUS
    assert price.LENGTH_CENSUS["set_screws_hex_socket"].n_pairs == length["n_pairs"]
    assert LENGTH_ROW.format("set_screws_hex_socket") in rows
