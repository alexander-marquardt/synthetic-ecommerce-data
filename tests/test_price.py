"""Price is held to the price census (#52), like every other realism row."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog import price
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.catalog.measure import measure

CENSUS_FILE = (
    Path(__file__).resolve().parent.parent / "reference-statistics" / "P2_price_census.json"
)


@pytest.fixture(scope="module")
def census() -> dict:
    return json.loads(CENSUS_FILE.read_text())


@pytest.fixture(scope="module")
def price_rows() -> list:
    stats = measure(generate(GeneratorConfig()), GeneratorConfig())
    return [row for row in stats["comparisons"] if row.band is not None]


@pytest.mark.parametrize("type_key", sorted(price.CENSUS))
def test_each_restated_figure_is_the_census_figure(census, type_key):
    row = census["deep_types"][type_key]
    stated = price.CENSUS[type_key]
    quantiles = row["price_quantiles_usd"]
    slope = row["price_vs_key_dimension"]
    assert (stated.n, stated.p10, stated.p50, stated.p90) == (
        row["n"],
        quantiles["p10"],
        quantiles["p50"],
        quantiles["p90"],
    )
    assert (stated.slope, stated.larger_costs_more, stated.n_pairs) == (
        slope["loglog_slope"],
        slope["share_larger_costs_more"],
        slope["n_pairs"],
    )


def test_every_type_with_30_census_rows_is_restated(census):
    measured = {k for k, v in census["deep_types"].items() if v["n"] >= 30}
    assert set(price.CENSUS) == measured


def test_the_pooled_and_brand_figures_are_the_census_figures(census):
    assert census["pooled_endings_all_types"]["class_share"] == price.POOLED_ENDINGS
    drills = census["deep_types"]["drill_jobber"]["brand_spread_same_spec"]
    assert drills["max_over_min_ratio"]["p50"] == price.BRAND_SPREAD_MEDIAN
    assert (
        drills["house_label_over_other_brands"]["quantiles"]["p50"]
        == price.ECONOMY_OVER_OTHERS_MEDIAN
    )
    assert drills["brand_price_index_quantiles"]["p90"] == price.PREMIUM_BRAND_INDEX_P90


@pytest.mark.parametrize(
    "shown,cls",
    [
        (12.99, ".99"),
        (3.0, ".00"),
        (7.5, ".50"),
        (4.95, ".95"),
        (4.49, ".49"),
        (4.98, ".98"),
        (4.97, ".97"),
        (4.35, "other .x5"),
        (4.39, "other .x9"),
        (4.31, "other"),
        (0.1, "other"),
    ],
)
def test_an_ending_is_classed_as_the_census_classes_it(shown, cls):
    assert price.ending_class(shown) == cls


def test_every_price_row_is_within_its_band_at_the_default_size(price_rows):
    assert len(price_rows) == 3 * len(price.CENSUS) + 1 + 4
    out = [row for row in price_rows if not row.within]
    assert not out, "\n".join(f"{row.name}: {row.achieved:.4f} outside {row.band}" for row in out)


def test_every_monotonicity_row_counts_pairs(price_rows):
    """A share over no pairs is 0.0 whatever the generator does."""
    empty = [row.name for row in price_rows if "costs more" in row.name and row.denominator < 20]
    assert not empty, empty
