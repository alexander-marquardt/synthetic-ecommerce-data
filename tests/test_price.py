"""Price is held to the price census (#52), like every other realism row."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog import brands, price, price_report
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.catalog.measure import measure
from synthetic_industrial_products.catalog.price_report import LENGTH_ROW, ORDER_ROW

CENSUS_FILE = (
    Path(__file__).resolve().parent.parent / "reference-statistics" / "P2_price_census.json"
)


@pytest.fixture(scope="module")
def census() -> dict:
    return json.loads(CENSUS_FILE.read_text())


@pytest.fixture(scope="module")
def catalog():
    return generate(GeneratorConfig())


@pytest.fixture(scope="module")
def price_rows(catalog) -> list:
    stats = measure(catalog, GeneratorConfig())
    return [row for row in stats["comparisons"] if row.band is not None]


@pytest.fixture(scope="module")
def scored(catalog):
    """What :func:`price_report.price_rows` reads but the prices, and the
    default build's prices: a test edits the prices and scores them again."""
    prices = {child.sku: child.price_usd for _, child in catalog.all_skus()}
    return price_report.collect(catalog), prices


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


#: The census types whose smaller-costs-2x-or-more row the default build
#: scores: :data:`price_report.TWICE_TYPES` (20 or more census pairs) less
#: the types that build one SKU per line along their axis.
TWICE_SCORED = (
    "bolt_hex",
    "drill_jobber",
    "hex_key",
    "nut_hex",
    "screw_socket_head",
    "tap_spiral_point",
    "washer_flat",
)


def test_every_price_row_is_within_its_band_or_pinned_at_the_default_size(price_rows):
    expected = (
        3 * len(price.CENSUS)
        + len(price.LENGTH_CENSUS)
        + len(price.EQUAL_PRICE_TYPES)
        + len(TWICE_SCORED)
        + len(price.BRAND_CENSUS)
        + 1
        + len(price_report.ENDING_CLASSES)
    )
    assert len(price_rows) == expected == 61
    out = [row for row in price_rows if not row.within and row.name not in price.PINNED_SHORTFALLS]
    assert not out, "\n".join(f"{row.name}: {row.achieved:.4f} outside {row.band}" for row in out)


def test_the_twice_types_are_the_census_types_with_20_pairs(census, price_rows):
    """The 2x target is implied from the census pairs on the type's axis, so
    a type with fewer has no row (the end mills' 11 and 18); of the rest,
    the default build scores each type that builds same-product pairs."""
    axis_pairs = {
        k: (v.get("price_vs_length_at_fixed_diameter") or {}).get("n_pairs", 0)
        if k in price.LENGTH_CENSUS
        else v["price_vs_key_dimension"]["n_pairs"]
        for k, v in census["deep_types"].items()
        if k in price.CENSUS
    }
    assert set(price_report.TWICE_TYPES) == {k for k, n in axis_pairs.items() if n >= 20}
    scored = {
        row.name.rsplit(": ", 1)[1]
        for row in price_rows
        if row.name.startswith("price smaller costs 2x+")
    }
    assert scored == set(TWICE_SCORED)


#: Each pinned shortfall: the side of its band it falls on, and what its
#: reason must name (the cause, or the issue that fixes it).
PINNED_SIDES = {
    "price p90/p10: bearing_radial_ball": ("below", "#64"),
    "price brand spread, same spec (median max/min): wheel_depressed_center": (
        "above",
        "drawn independently per",
    ),
}


@pytest.mark.parametrize("name", sorted(PINNED_SIDES))
def test_each_pinned_shortfall_stays_out_of_band_on_its_side(price_rows, name):
    """A pin discloses a row the model cannot land; it must not drift to the
    other side, nor quietly come into band (the fit then calls the pin stale)."""
    assert set(price.PINNED_SHORTFALLS) == set(PINNED_SIDES)
    side, cause = PINNED_SIDES[name]
    reason = price.PINNED_SHORTFALLS[name]
    assert reason.startswith(f"{side} band"), reason
    assert cause in reason, reason
    (row,) = [row for row in price_rows if row.name == name]
    assert "PINNED SHORTFALL" in row.note
    if side == "below":
        assert row.achieved < row.band[0], (row.achieved, row.band)
    else:
        assert row.achieved > row.band[1], (row.achieved, row.band)
    assert set(price.PINNED_FIGURES) == set(price.PINNED_SHORTFALLS)
    assert price_report.pin_holds(row), (row.achieved, price.PINNED_FIGURES[name])


def test_a_pin_whose_shortfall_worsens_fails(monkeypatch):
    """Review plant M5: bearing noise off. Its p90/p10 falls from 4.55 to
    4.31, further below the band but still on its side, so only the
    recorded figure can catch it."""
    name = "price p90/p10: bearing_radial_ball"
    quiet = replace(price.MODELS["bearing_radial_ball"], group_sigma=0.0, sku_sigma=0.0)
    monkeypatch.setitem(price.MODELS, "bearing_radial_ball", quiet)
    (row,) = [
        row
        for row in price_report.price_comparisons(generate(GeneratorConfig()))
        if row.name == name
    ]
    assert round(row.achieved, 2) == 4.31
    assert row.achieved < row.band[0]
    assert not price_report.pin_holds(row)


def _census_models() -> dict[str, price.PriceModel]:
    return {type_key: price.model_for(type_key) for type_key in price.CENSUS}


def test_every_slope_off_the_census_has_a_recorded_cut():
    """``scripts/fit_price_model.py`` cuts a slope only with a SLOPE_CUTS
    reason, but no test runs the fit: this holds the committed literals to
    the same rule."""
    assert price.slope_cut_mismatch(_census_models(), price.SLOPE_CUTS) == set()
    assert set(price.SLOPE_CUTS) == {"bolt_hex", "end_mill_ball", "end_mill_square"}
    assert all(reason.strip() for reason in price.SLOPE_CUTS.values())


def test_a_slope_cut_by_hand_is_refused():
    """Review plant R2b: the tap slope hand-cut to 0.40 with no reason; and
    the other way, a reason left behind for a slope no longer cut."""
    models = _census_models()
    models["tap_spiral_point"] = replace(models["tap_spiral_point"], slope=0.40)
    assert price.slope_cut_mismatch(models, price.SLOPE_CUTS) == {"tap_spiral_point"}
    models = _census_models()
    models["bolt_hex"] = replace(
        models["bolt_hex"],
        slope=price.CENSUS["bolt_hex"].slope,
        length_slope=price.LENGTH_CENSUS["bolt_hex"].slope,
    )
    assert price.slope_cut_mismatch(models, price.SLOPE_CUTS) == {"bolt_hex"}
    models = _census_models()
    models["screw_socket_head"] = replace(models["screw_socket_head"], length_slope=0.2)
    assert price.slope_cut_mismatch(models, price.SLOPE_CUTS) == {"screw_socket_head"}
    blank = {**price.SLOPE_CUTS, "bolt_hex": " "}
    assert price.slope_cut_mismatch(_census_models(), blank) == {"bolt_hex"}


def _newly_out(scored, prices) -> dict:
    collected, base = scored
    before = {row.name for row in price_report.price_rows(collected, base) if not row.within}
    return {
        row.name: row
        for row in price_report.price_rows(collected, prices)
        if not row.within and row.name not in before
    }


def _below(rows: dict, names) -> None:
    missing = sorted(set(names) - set(rows))
    assert not missing, missing
    for name in names:
        assert rows[name].achieved < rows[name].band[0], (name, rows[name].achieved)


def test_swapping_a_products_first_and_last_price_breaks_the_order_rows(catalog, scored):
    """Review plant 1a: the first and last SKU of every product trade prices."""
    _, base = scored
    prices = dict(base)
    for line in catalog.lines:
        if len(line.children) >= 2:
            first, last = line.children[0].sku, line.children[-1].sku
            prices[first], prices[last] = base[last], base[first]
    _below(
        _newly_out(scored, prices),
        [ORDER_ROW.format(t) for t in ("drill_jobber", "hex_key", "nut_hex", "washer_flat")]
        + [LENGTH_ROW.format(t) for t in price.LENGTH_CENSUS],
    )


def test_a_price_that_falls_with_length_breaks_the_length_rows(catalog, scored):
    """Review plant 1b: on bolts and socket-family screws the longest SKU of
    a product gets its lowest price. The length rows catch it, not a
    diameter row by accident."""
    _, base = scored
    prices = dict(base)
    for line in catalog.lines:
        if line.type_key not in price.LENGTH_HELD:
            continue
        lengths = sorted(
            (price.length_of({a.name: a for a in catalog.merged_attributes(line, c)}) or 0.0, c.sku)
            for c in line.children
        )
        falling = sorted((base[sku] for _, sku in lengths), reverse=True)
        prices.update({sku: p for (_, sku), p in zip(lengths, falling, strict=True)})
    newly = _newly_out(scored, prices)
    _below(newly, [LENGTH_ROW.format(t) for t in price.LENGTH_CENSUS])


def test_dropping_the_99_endings_breaks_the_99_row(scored):
    """Review plant 2b: every .99 price ends .91 instead, an "other" ending."""
    _, base = scored
    prices = {
        sku: round(p - 0.08, 2) if price.ending_class(p) == ".99" else p for sku, p in base.items()
    }
    _below(_newly_out(scored, prices), ["price ending .99"])


def test_every_monotonicity_row_counts_pairs(price_rows):
    """A share over no pairs is 0.0 whatever the generator does."""
    empty = [
        row.name
        for row in price_rows
        if ("costs more" in row.name or "costs 2x+" in row.name) and row.denominator < 20
    ]
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
        ratio = row["max_over_min_ratio"]
        assert (
            stated.spread_p50,
            stated.n_specs,
            stated.low_confidence,
            stated.spread_p25,
            stated.spread_p75,
        ) == (
            ratio["p50"],
            row["n_specs_with_2plus_brands"],
            row["low_confidence"],
            ratio["p25"],
            ratio["p75"],
        )


@pytest.mark.parametrize("type_key", sorted(price.TYPE_TIER_CENSUS))
def test_each_types_tier_factors_are_its_census_figures(census, type_key):
    """Economy is the distributor's house label over the other brands
    (median), or the brand price index p10 where the census has no house
    label figure (the ball end mill); premium is the brand price index p90."""
    spread = census["deep_types"][type_key]["brand_spread_same_spec"]
    house = spread["house_label_over_other_brands"]
    index = spread["brand_price_index_quantiles"]
    economy = house["quantiles"]["p50"] if house else index["p10"]
    assert price.TYPE_TIER_CENSUS[type_key] == (economy, index["p90"])
    assert price.TYPE_TIERS[type_key] == {
        "economy": economy,
        "standard": 1.0,
        "premium": index["p90"],
    }
    assert price.model_for(type_key).tiers == price.TYPE_TIERS[type_key]


def test_only_the_size_noise_types_draw_a_size_noise():
    """A size noise is fitted only for a type SIZE_NOISE gives a reason for."""
    sized = {t for t in price.CENSUS if price.model_for(t).size_sigma}
    assert sized == set(price.SIZE_NOISE) == {"screw_socket_head", "tap_spiral_point"}


def test_each_familys_tiers_price_in_order(scored):
    """Per family, on specs it shares, an economy brand's median price is
    below a standard brand's and a premium brand's above it."""
    order = price_report.tier_order(*scored)
    assert set(order) == set(TIERS_BY_FAMILY)
    for family, (economy, premium) in order.items():
        assert economy < 1.0 < premium, (family, economy, premium)


def test_the_tier_exception_is_the_bearing_value_label():
    assert brands.TIER_EXCEPTIONS == {("Tervasko", "bearing_radial_ball"): "standard"}
    assert brands.tier_of("Tervasko", "bearing_radial_ball") == "standard"
    assert brands.tier_of("Tervasko", "drill_jobber") == "economy"
    assert brands.tier_of("Salt Meadow Works", "abrasive_flap_disc") == "economy"


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
