"""Price is held to the price census (#52), like every other realism row."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog import brands, price
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
    expected = 3 * len(price.CENSUS) + len(price.LENGTH_CENSUS) + len(price.BRAND_CENSUS) + 1 + 4
    assert len(price_rows) == expected == 53
    out = [row for row in price_rows if not row.within]
    assert not out, "\n".join(f"{row.name}: {row.achieved:.4f} outside {row.band}" for row in out)


def test_every_monotonicity_row_counts_pairs(price_rows):
    """A share over no pairs is 0.0 whatever the generator does."""
    empty = [row.name for row in price_rows if "costs more" in row.name and row.denominator < 20]
    assert not empty, empty


@pytest.mark.parametrize("type_key", sorted(price.ENDINGS))
def test_each_type_endings_mix_is_the_census_mix(census, type_key):
    """The generator draws endings from this table and the endings rows aim
    at it, so only this pin catches a table that leaves the census."""
    assert price.ENDINGS[type_key] == census["deep_types"][type_key]["endings"]["class_share"]


@pytest.mark.parametrize("key", sorted(price.BREADTH_CENSUS))
def test_each_breadth_census_figure_is_the_census_figure(census, key):
    q = census["breadth_categories"][key]["price_quantiles_usd"]
    assert price.BREADTH_CENSUS[key] == (q["p10"], q["p50"], q["p90"])


def test_the_length_figures_are_the_census_figures(census):
    measured = {
        k: v["price_vs_length_at_fixed_diameter"]
        for k, v in census["deep_types"].items()
        if (v.get("price_vs_length_at_fixed_diameter") or {}).get("n_pairs", 0) >= 100
    }
    assert set(price.LENGTH_CENSUS) == set(measured)
    for type_key, row in measured.items():
        stated = price.LENGTH_CENSUS[type_key]
        assert (stated.slope, stated.longer_costs_more, stated.n_pairs) == (
            row["loglog_slope"],
            row["share_larger_costs_more"],
            row["n_pairs"],
        )


def test_the_brand_spread_figures_are_the_census_figures(census):
    measured = {
        k: v["brand_spread_same_spec"]
        for k, v in census["deep_types"].items()
        if (v.get("brand_spread_same_spec") or {}).get("max_over_min_ratio")
    }
    assert set(price.BRAND_CENSUS) == set(measured)
    for type_key, row in measured.items():
        stated = price.BRAND_CENSUS[type_key]
        assert (stated.spread_p50, stated.n_specs, stated.low_confidence) == (
            row["max_over_min_ratio"]["p50"],
            row["n_specs_with_2plus_brands"],
            row["low_confidence"],
        )


#: Each family's value brands and premium makers. A tier is no field on the
#: record and a swap of two brands' tiers keeps every price distribution, so
#: no band row can see one: the names are pinned here.
TIERS_BY_FAMILY = {
    "cutting_tool": ({"Tervasko", "Wendlow Tool"}, {"Quillon Carbide", "Varrick Precision"}),
    "fastener": ({"Tervasko", "Morvennick", "Stone Wicket"}, {"Cobbet & Pryce"}),
    "abrasive": ({"Tervasko", "Salt Meadow Works", "Stone Wicket"}, {"Grisenne"}),
    "hand_tool": ({"Tervasko", "Stone Wicket"}, {"Ashcombe Forge"}),
    "motion": ({"Tervasko", "Harnell"}, {"Quennick"}),
}


@pytest.mark.parametrize("family", sorted(TIERS_BY_FAMILY))
def test_each_family_keeps_its_named_price_tiers(family):
    makers = [b for b in brands.BRAND_BOOK if family in b.families]
    economy = {b.name for b in makers if b.tier == "economy"}
    premium = {b.name for b in makers if b.tier == "premium"}
    assert (economy, premium) == TIERS_BY_FAMILY[family]
    assert 2 <= len(economy) <= 3 and 1 <= len(premium) <= 2
