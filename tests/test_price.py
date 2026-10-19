"""Price is held to the price census (#52), like every other realism row."""

from __future__ import annotations

import json
import math
import random
import re
import statistics
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import brands, price
from synthetic_ecommerce_data.core.config import LARGE_BUILD_LINES, GeneratorConfig
from synthetic_ecommerce_data.core.dimensions import (
    DimensionParseError,
    parse_length,
    parse_thread,
)
from synthetic_ecommerce_data.core.model import Attribute, Catalog
from synthetic_ecommerce_data.domains.industrial import (
    breadth,
    hammers,
    newtypes,
    price_report,
    tabletype,
)
from synthetic_ecommerce_data.domains.industrial.generate import Generator, generate
from synthetic_ecommerce_data.domains.industrial.measure import measure
from synthetic_ecommerce_data.domains.industrial.price_report import (
    BRAND_ROW,
    EQUAL_ROW,
    LENGTH_ROW,
    ORDER_ROW,
    SPREAD_ROW,
)

CENSUS_FILE = (
    Path(__file__).resolve().parent.parent / "reference-statistics" / "P2_price_census.json"
)


@pytest.fixture(scope="module")
def census() -> dict:
    return json.loads(CENSUS_FILE.read_text())


KIT = "kit_assortment"

#: One kit SKU as its price was drawn: its shown price, the facts it was
#: drawn from, and its brand.
KitSku = tuple[float, dict[str, Attribute], str]


def _recorded_build(config: GeneratorConfig) -> tuple[Catalog, list[KitSku]]:
    """A build, and each kit SKU with the facts its price was drawn from.
    Those are read as the draw reads them, not off the published record:
    sparsity may drop a kit's ``Material`` or ``Sizes Included``, and never
    moves its price."""
    drawn: dict[str, tuple[dict[str, Attribute], str]] = {}
    original = Generator._price_draw

    def recording(self, type_key, brand, attributes, line_attributes, sku, sku_u):
        if type_key == KIT:
            drawn[sku] = ({a.name: a for a in attributes}, brand)
        return original(self, type_key, brand, attributes, line_attributes, sku, sku_u)

    Generator._price_draw = recording  # type: ignore[method-assign]
    try:
        catalog = generate(config)
    finally:
        Generator._price_draw = original  # type: ignore[method-assign]
    shown = {child.sku: child.price_usd for _, child in catalog.all_skus()}
    kits = [(shown[sku], *drawn[sku]) for sku in sorted(drawn) if sku in shown]
    return catalog, kits


@pytest.fixture(scope="module")
def recorded() -> tuple[Catalog, list[KitSku]]:
    return _recorded_build(GeneratorConfig())


@pytest.fixture(scope="module")
def catalog(recorded):
    return recorded[0]


@pytest.fixture(scope="module")
def kits(recorded) -> list[KitSku]:
    return recorded[1]


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
    "lock_nuts_nylon_insert",
    "nut_hex",
    "screw_socket_head",
    "set_screws_hex_socket",
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
        + 2 * len(price.DEEPENED_CENSUS)
    )
    assert len(price_rows) == expected == 72
    out = [
        row for row in price_rows if not row.within and row.name not in price.PINNED_SHORTFALLS
    ]
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
    "price brand spread, same spec (median max/min): wheel_depressed_center": (
        "above",
        "brand tiers alone give",
    ),
    "price p90/p10: kit_assortment": ("below", "#76"),
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
    if _recorded(name)[0] is None:
        assert row.within, (row.achieved, row.band)
    elif side == "below":
        assert row.achieved < row.band[0], (row.achieved, row.band)
    else:
        assert row.achieved > row.band[1], (row.achieved, row.band)
    assert set(price.PINNED_FIGURES) == set(price.PINNED_SHORTFALLS)
    assert price_report.pin_holds(row, 0), (row.achieved, price.PINNED_FIGURES[name])


def test_a_pin_reason_quotes_the_figures_the_pin_records():
    """The wheel reason states how far apart a spec's brands land at each
    build; those are the pinned figures themselves, so they are read, not
    retyped (it read 6.8 once the figure was 3.24)."""
    name = BRAND_ROW.format("wheel_depressed_center")
    quoted = re.findall(r"(\d+(?:\.\d+)?)x apart", price.PINNED_SHORTFALLS[name])
    figures = [f for f in _recorded(name) if f is not None]
    assert quoted == [f"{f:.2f}" for f in figures] == ["1.75"]


def test_the_wheel_brand_spread_lands_in_band_on_the_default_build(price_rows):
    """#272: the wheel's group noise (0.70, drawn per brand) spread one spec's
    sampled brands 4.3x apart against a band top of 1.71, and the figure moved
    each time the wheel product ids did. The p90/p10 is carried by noise one
    spec shares across its brands instead, so the default build lands in band
    and only the 100K build stays pinned."""
    name = BRAND_ROW.format("wheel_depressed_center")
    (row,) = [row for row in price_rows if row.name == name]
    assert row.within, (row.achieved, row.band)
    assert _recorded(name)[0] is None
    assert _recorded(name)[1] is not None
    model = price.MODELS["wheel_depressed_center"]
    assert model.size_sigma > model.group_sigma, (model.size_sigma, model.group_sigma)


def _recorded(name: str) -> tuple[float | None, float | None]:
    """A pinned row's recorded (default, 100K) figures; ``None`` for a build
    the row lands in band on (#272)."""
    recorded = price.PINNED_FIGURES[name]
    assert isinstance(recorded, tuple), f"{name}: {recorded!r} is one figure for two builds"
    return recorded


@pytest.mark.parametrize("name", sorted(PINNED_SIDES))
@pytest.mark.parametrize("build", [0, 1])
def test_a_pin_may_land_no_further_out_than_its_figure_for_that_build(price_rows, name, build):
    """Each build is held to its own recorded figure, within the tolerance:
    exactly there, on the pin's side. A pin that read the default figure at
    100K let the wheel spread rise 19% and the bearing p90/p10 fall 8%."""
    (row,) = [row for row in price_rows if row.name == name]
    edge = _recorded(name)[build]
    if edge is None:
        assert row.within
        assert price_report.pin_holds(row, build)
        assert not price_report.pin_holds(replace(row, achieved=row.band[1] * 1.001), build)
        assert not price_report.pin_holds(replace(row, achieved=row.band[0] * 0.999), build)
        return
    if PINNED_SIDES[name][0] == "below":
        edge /= 1 + price.PIN_TOLERANCE
        inside, outside = edge * 1.0001, edge * 0.9999
    else:
        edge *= 1 + price.PIN_TOLERANCE
        inside, outside = edge * 0.9999, edge * 1.0001
    assert price_report.pin_holds(replace(row, achieved=inside), build)
    assert not price_report.pin_holds(replace(row, achieved=outside), build)


@pytest.mark.parametrize("name", sorted(PINNED_SIDES))
@pytest.mark.parametrize("build", [0, 1])
def test_a_pin_five_percent_further_out_than_its_record_fails(price_rows, name, build):
    """The tolerance is 2%, written out here: a figure 5% past its record on
    the pin's side is a worse shortfall than the record, whatever the tolerance
    is set to. A build recorded ``None`` has no figure to be past."""
    (row,) = [row for row in price_rows if row.name == name]
    recorded = _recorded(name)[build]
    if recorded is None:
        return
    outward = recorded / 1.05 if PINNED_SIDES[name][0] == "below" else recorded * 1.05
    assert price_report.pin_holds(replace(row, achieved=recorded), build)
    assert not price_report.pin_holds(replace(row, achieved=outward), build)


def test_a_pin_whose_shortfall_worsens_fails(monkeypatch):
    """The wheel's default build lands in band (its record is ``None``), so
    group noise three times louder spreads one spec's brands out of it, and
    the pin, which holds a recorded-``None`` build in band, fails (#272)."""
    name = BRAND_ROW.format("wheel_depressed_center")
    model = price.MODELS["wheel_depressed_center"]
    louder = replace(model, group_sigma=model.group_sigma * 3)
    monkeypatch.setitem(price.MODELS, "wheel_depressed_center", louder)
    (row,) = [
        row
        for row in price_report.price_comparisons(generate(GeneratorConfig()))
        if row.name == name
    ]
    assert row.achieved > row.band[1]
    assert not price_report.pin_holds(row, 0)


def test_a_pin_whose_shortfall_worsens_below_its_band_fails(monkeypatch, price_rows):
    """No committed pin is below its band since #64, so a planted one holds
    the below-band side: further below its record than the tolerance fails,
    as does a row back in band."""
    (row,) = [r for r in price_rows if r.name == SPREAD_ROW.format("bearing_radial_ball")]
    floor = row.band[0]
    monkeypatch.setitem(price.PINNED_FIGURES, row.name, (floor * 0.5, floor * 0.5))
    monkeypatch.setitem(price.PINNED_SHORTFALLS, row.name, "below band: planted")
    edge = floor * 0.5 / (1 + price.PIN_TOLERANCE)
    assert price_report.pin_holds(replace(row, achieved=edge * 1.001), 0)
    assert not price_report.pin_holds(replace(row, achieved=edge * 0.999), 0)
    assert not price_report.pin_holds(replace(row, achieved=floor * 1.001), 0)


def test_the_bearing_bores_alone_spread_price_into_the_census_band(catalog, price_rows):
    """#64: the census slope on the bore, with no noise at all, reaches the
    floor of the census p90/p10 band. A 10-35 mm ladder spread the bores 3.0x,
    which the slope (1.167) carries to 3.6x against a floor of 12.1x, and the
    census's own same-spec brand spread (1.38) leaves no group noise to make
    up the rest."""
    read = price.KEYS["bearing_radial_ball"]
    bores = [
        read({a.name: a for a in catalog.merged_attributes(line, child)})
        for line in catalog.lines
        if line.type_key == "bearing_radial_ball"
        for child in line.children
    ]
    assert None not in bores
    spread = price_report._quantile(bores, 0.9) / price_report._quantile(bores, 0.1)
    (row,) = [r for r in price_rows if r.name == SPREAD_ROW.format("bearing_radial_ball")]
    carried = spread ** price.CENSUS["bearing_radial_ball"].slope
    assert carried >= row.band[0], (spread, carried, row.band)


def test_the_bearing_price_spread_is_in_band_and_not_pinned(price_rows):
    """#64: once the bores span the series, the bearing p90/p10 needs no pin."""
    name = SPREAD_ROW.format("bearing_radial_ball")
    assert name not in price.PINNED_SHORTFALLS
    assert name not in price.PINNED_FIGURES
    (row,) = [r for r in price_rows if r.name == name]
    assert row.band[0] <= row.achieved <= row.band[1], (row.achieved, row.band)


def _census_models() -> dict[str, price.PriceModel]:
    return {type_key: price.model_for(type_key) for type_key in price.CENSUS}


def test_every_slope_off_the_census_has_a_recorded_cut():
    """``scripts/fit_price_model.py`` cuts a slope only with a SLOPE_CUTS
    reason, but no test runs the fit: this holds the committed literals to
    the same rule."""
    assert price.slope_cut_mismatch(_census_models(), price.SLOPE_CUTS) == set()
    assert set(price.SLOPE_CUTS) == {
        "bolt_hex",
        "end_mill_ball",
        "end_mill_square",
        "lock_nuts_nylon_insert",
        "set_screws_hex_socket",
    }
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
    counted = {
        row.name: row.denominator
        for row in price_rows
        if "costs more" in row.name or "costs 2x+" in row.name
    }
    empty = [name for name, n in counted.items() if n < 20]
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


@pytest.mark.parametrize("key", sorted(price.DEEPENED_CENSUS))
def test_each_deepened_census_figure_is_the_census_figure(census, key):
    """A deepened category leaves the breadth table but keeps its census row."""
    row = census["breadth_categories"][key]
    q = row["price_quantiles_usd"]
    assert price.DEEPENED_CENSUS[key] == (row["n"], q["p10"], q["p50"], q["p90"])
    assert key not in price.BREADTH_CENSUS


@pytest.mark.parametrize("key", sorted(price.DEEPENED_CENSUS))
def test_each_deepened_types_endings_mix_is_the_census_mix(census, key):
    expected = census["breadth_categories"][key]["endings"]["class_share"]
    assert dict(price.model_for(key).endings) == expected


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
            stated.brands_indexed,
        ) == (
            ratio["p50"],
            row["n_specs_with_2plus_brands"],
            row["low_confidence"],
            ratio["p25"],
            ratio["p75"],
            row["n_brands_indexed"],
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


def test_the_hex_nut_takes_the_drills_tiers_though_the_census_measures_its_spread(census):
    """The one type with a census brand spread but no tier figures of its
    own: on its 6 shared specs the house label is the DEARER brand, so it
    gives no economy figure, and the nut prices with the drill's tiers."""
    assert set(price.BRAND_CENSUS) - set(price.TYPE_TIER_CENSUS) == {"nut_hex"}
    house = census["deep_types"]["nut_hex"]["brand_spread_same_spec"][
        "house_label_over_other_brands"
    ]
    assert (house["n_specs"], house["quantiles"]["p50"]) == (6, 5.5752)
    assert price.model_for("nut_hex").tiers == price.TIER_FACTORS


def test_only_the_size_noise_types_draw_a_size_noise():
    """A size noise is fitted only for a type SIZE_NOISE gives a reason for."""
    sized = {t for t in price.CENSUS if price.model_for(t).size_sigma}
    assert sized == set(price.SIZE_NOISE) == {
        "screw_socket_head",
        "set_screws_hex_socket",
        "tap_spiral_point",
        "wheel_depressed_center",
    }


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


# --- every row bites in both directions it can fail -------------------------


def _above(rows: dict, names) -> None:
    missing = sorted(set(names) - set(rows))
    assert not missing, missing
    for name in names:
        assert rows[name].achieved > rows[name].band[1], (name, rows[name].achieved)


def _held_to_band(template: str, type_keys) -> list[str]:
    """The rows a band holds: a pinned row is out already, so it cannot
    newly break."""
    exempt = set(price.PINNED_SHORTFALLS)
    return [template.format(t) for t in type_keys if template.format(t) not in exempt]


@pytest.mark.parametrize(("factor", "check"), [(2.0, _above), (0.5, _below)])
def test_scaling_every_price_breaks_every_p50_row(scored, factor, check):
    """The p50 band is x0.8 to x1.25 of the census: a catalog priced twice or
    half as high leaves it on every type."""
    _, base = scored
    prices = {sku: p * factor for sku, p in base.items()}
    check(_newly_out(scored, prices), _held_to_band("price p50 (USD): {}", price.CENSUS))


@pytest.mark.parametrize(("power", "check"), [(2.0, _above), (0.2, _below)])
def test_widening_or_narrowing_each_types_spread_breaks_its_spread_row(scored, power, check):
    """Each type's prices move about its own median, in logs: squared, the
    p90/p10 squares; to the fifth root, it falls to its fifth root. The
    pinned bearing row is out already, and squared lands in band (its pin
    test catches that)."""
    collected, base = scored
    by_type: dict[str, list[str]] = defaultdict(list)
    for sku, type_key in collected.type_of.items():
        by_type[type_key].append(sku)
    prices = dict(base)
    for skus in by_type.values():
        middle = statistics.median(base[s] for s in skus)
        prices.update({s: middle * (base[s] / middle) ** power for s in skus})
    expected = _held_to_band(SPREAD_ROW, price.CENSUS)
    if power > 1:
        expected = [n for n in expected if "bearing_radial_ball" not in n]
    check(_newly_out(scored, prices), expected)


def test_one_brand_priced_100x_on_every_spec_breaks_the_brand_spread_rows(scored):
    """On every spec two or more brands make, each brand costs 100x the one
    before it by name: any two brands of a spec sit 100x apart or more, so
    whichever a row samples, no spec's max/min falls under 10, above every
    band."""
    collected, base = scored
    prices = dict(base)
    for by_brand in collected.specs.values():
        if len(by_brand) >= 2:
            for rank, brand in enumerate(sorted(by_brand)):
                prices.update({s: base[s] * 100.0**rank for s in by_brand[brand]})
    _above(_newly_out(scored, prices), _held_to_band(BRAND_ROW, price.BRAND_CENSUS))


#: The brand-spread types whose census median is measured on so few specs
#: that its standard-error band is wider than x0.75 to x1.33.
BRAND_BAND_FROM_ERROR = ("end_mill_ball", "nut_hex")


@pytest.mark.parametrize("type_key", sorted(price.BRAND_CENSUS))
def test_the_brand_spread_band_is_x075_to_x133_unless_the_census_error_is_wider(type_key):
    """The band's edges, exactly: x0.75 and x1.33 of the census median, or
    3 standard errors of that median where those are wider (a ball end
    mill's 5 specs, a hex nut's 6). A band widened at either edge moves them."""
    figure = price.BRAND_CENSUS[type_key]
    low, high = price_report.brand_spread_band(figure)
    if type_key in BRAND_BAND_FROM_ERROR:
        sigma = math.log(figure.spread_p75 / figure.spread_p25) / 1.349
        width = 3.0 * math.sqrt(math.pi / 2) * sigma / math.sqrt(figure.n_specs)
        assert width > math.log(1.33), width
        assert (low, high) == pytest.approx(
            (figure.spread_p50 * math.exp(-width), figure.spread_p50 * math.exp(width))
        )
    else:
        assert (low, high) == pytest.approx((figure.spread_p50 * 0.75, figure.spread_p50 * 1.33))


def test_a_specs_brand_sample_is_k_of_its_brands_and_fixed_per_spec():
    names = [f"Brand {i:02d}" for i in range(13)]
    spec = ("drill_jobber", 0.25, "High Speed Steel")
    chosen = price_report.sampled_brands(spec, names, 3)
    assert len(chosen) == len(set(chosen)) == 3
    assert set(chosen) < set(names)
    assert price_report.sampled_brands(spec, reversed(names), 3) == chosen
    assert price_report.sampled_brands(spec, names[:3], 3) == names[:3]
    others = {tuple(price_report.sampled_brands((*spec[:2], m), names, 3)) for m in "abcdefgh"}
    assert len(others) > 1


def test_each_brand_spread_row_samples_the_census_brands_per_spec():
    """At most the brands a census spec can hold (a socket screw's 2), and
    never more than :data:`price_report.BRAND_SAMPLE_CAP`."""
    sampled = {t: price_report.brand_sample(f) for t, f in price.BRAND_CENSUS.items()}
    assert sampled == {
        "bearing_radial_ball": 3,
        "drill_jobber": 3,
        "end_mill_ball": 3,
        "nut_hex": 3,
        "screw_socket_head": 2,
        "tap_spiral_point": 3,
        "wheel_depressed_center": 3,
    }


def _spec_spreads(brands_per_spec: int, k: int) -> float:
    """The median over 2,000 specs of one model's brand spread: each brand's
    log price on a spec is its tier plus a normal draw, as the generator's
    group noise is, whatever the number of brands."""
    rng = random.Random(52)
    tiers = [math.log(f) for f in price.TIER_FACTORS.values()]
    names = [f"Brand {i:02d}" for i in range(brands_per_spec)]
    spreads = []
    for spec in range(2000):
        logs = {name: rng.choice(tiers) + rng.gauss(0.0, 0.4) for name in names}
        chosen = [logs[b] for b in price_report.sampled_brands(("t", spec, ""), names, k)]
        spreads.append(math.exp(max(chosen) - min(chosen)))
    return statistics.median(spreads)


def test_the_brand_spread_reads_one_model_alike_at_3_and_at_13_brands_per_spec():
    """One unchanged model, scored on specs of 3 brands (a default drill's
    median) and of 13 (a 100K drill's): max/min over every brand grows with
    the brands per spec, max/min over the sampled brands does not."""
    k = price_report.BRAND_SAMPLE_CAP
    every_brand = _spec_spreads(13, 13) / _spec_spreads(3, 3)
    sampled = _spec_spreads(13, k) / _spec_spreads(3, k)
    assert every_brand > 1.8, every_brand
    assert abs(math.log(sampled)) < 0.05, sampled


def test_the_drill_brand_spread_reads_alike_at_the_default_size_and_at_100k(
    price_rows, hundred_k_rows
):
    """The case the row was red on: a drill spec holds a median 3 brands at
    the default size and 13 at 100K, and the brands' prices are drawn the
    same way at both."""
    name = BRAND_ROW.format("drill_jobber")
    (default,) = [row.achieved for row in price_rows if row.name == name]
    assert abs(math.log(hundred_k_rows[name].achieved / default)) < math.log(1.15), (
        default,
        hundred_k_rows[name].achieved,
    )


WHEEL = "wheel_depressed_center"
ABRASIVES = {"Aluminum Oxide", "Ceramic", "Silicon Carbide", "Zirconia Alumina"}

#: :data:`price.BRAND_CENSUS` types whose built specs hold no material, and
#: why each may not.
SPEC_WITHOUT_MATERIAL: dict[str, str] = {}


def _keyword(value: str) -> Attribute:
    return Attribute(name="x", value=value)


def test_a_wheel_spec_holds_its_abrasive_as_its_material(scored):
    """The census spec is the key dimension plus the material. A wheel
    publishes no "Material"; its material is its abrasive, so a spec that
    read "Material" held none and set a ceramic wheel's brands against an
    aluminum oxide one's (#66)."""
    collected, _ = scored
    assert {spec[2] for spec in collected.specs if spec[0] == WHEEL} == ABRASIVES
    assert price.material_of(WHEEL, {"Abrasive Material": _keyword("Ceramic")}) == "Ceramic"
    assert price.material_of("drill_jobber", {"Material": _keyword("Cobalt")}) == "Cobalt"
    assert price.material_of(WHEEL, {"Material": _keyword("Cobalt")}) is None


def test_every_brand_census_types_spec_holds_a_material_or_names_why_not(scored):
    """A type whose spec reads an attribute it never publishes has specs of
    the key alone, so its brand-spread row compares brands across
    materials and nothing else says so (#66)."""
    collected, _ = scored
    assert price_report.types_without_material(collected) == set(SPEC_WITHOUT_MATERIAL)


def test_a_spec_read_off_an_attribute_the_type_never_publishes_is_caught(catalog, monkeypatch):
    """Plant: the wheel's spec read "Material", as it did before #66."""
    monkeypatch.setattr(price, "MATERIAL_ATTRIBUTES", {})
    assert price_report.types_without_material(price_report.collect(catalog)) == {WHEEL}


def test_the_wheel_pin_reason_quotes_what_the_brand_tiers_alone_give(monkeypatch):
    """The wheel's pinned cause is measured, not asserted: at 100K, with its
    noise off, the brand tiers alone spread a spec's sampled brands past the
    band top, because the row samples an economy brand on most specs (the
    default build, 1.49 the same way, is in band)."""
    quiet = replace(price.MODELS[WHEEL], group_sigma=0.0, sku_sigma=0.0, size_sigma=0.0)
    monkeypatch.setitem(price.MODELS, WHEEL, quiet)
    catalog = generate(GeneratorConfig(lines=LARGE_BUILD_LINES))
    (row,) = [
        row
        for row in price_report.price_comparisons(catalog)
        if row.name == BRAND_ROW.format(WHEEL)
    ]
    specs = {
        spec: by
        for spec, by in price_report.collect(catalog).specs.items()
        if spec[0] == WHEEL and len(by) > 1
    }
    k = price_report.brand_sample(price.BRAND_CENSUS[WHEEL])
    economy = {b for by in specs.values() for b in by if brands.tier_of(b, WHEEL) == "economy"}
    sampling = [
        spec
        for spec, by in specs.items()
        if economy & set(price_report.sampled_brands(spec, by, k))
    ]
    makers = {b for by in specs.values() for b in by}
    reason = price.PINNED_SHORTFALLS[row.name]
    assert f"brand tiers alone give {row.achieved:.2f} at 100K" in reason, reason
    assert f"band top of {row.band[1]:.2f}" in reason, reason
    assert f"{len(economy)} of the {len(makers)} wheel brands are economy" in reason, reason
    assert f"on {len(sampling)} of its {len(specs)} specs" in reason, reason
    k = price_report.BRAND_SAMPLE_CAP
    assert f"row's {k} sampled brands" in reason, reason


def test_economy_brands_priced_as_dear_as_the_rest_breaks_the_economy_row(scored):
    """The census's house labels cost 0.52 of the other brands on a drill
    spec; doubled, an economy drill costs about what the rest do."""
    collected, base = scored
    prices = dict(base)
    for (type_key, _, _), by_brand in collected.specs.items():
        if type_key != price.BRAND_SPREAD_TYPE:
            continue
        for brand, skus in by_brand.items():
            if brands.tier_of(brand, type_key) == "economy":
                prices.update({s: base[s] * 2 for s in skus})
    name = f"price economy brands over others, same spec (median): {price.BRAND_SPREAD_TYPE}"
    _above(_newly_out(scored, prices), [name])


def test_a_smaller_sku_priced_3x_the_bigger_breaks_the_2x_rows(scored):
    """In every same-product pair, the smaller SKU costs three times the
    bigger or more: the 2x share is 1.0, over any band short of the whole
    range. Along one product's axis the order is total, so a SKU priced 3
    to the power of how many SKUs are bigger than it costs 3x or more than
    each of them."""
    collected, base = scored
    prices = dict(base)
    bigger_than: dict[str, int] = defaultdict(int)
    for pairs in collected.product_pairs.values():
        for bigger, smaller, _ in pairs:
            bigger_than[bigger] += 0
            bigger_than[smaller] += 1
    prices.update({sku: 3.0**n for sku, n in bigger_than.items()})
    rows = [f"price smaller costs 2x+, same product: {t}" for t in TWICE_SCORED]
    _above(_newly_out(scored, prices), rows)


def test_a_quarter_of_pairs_at_2x_breaks_the_2x_rows(scored):
    """Every other paired SKU (by SKU id) costs 4x: a pair whose smaller
    member is one of them and whose bigger is not costs 2x or more, a tenth
    to a third of each type's pairs (washers 0.14). That is out of every 2x band, and inside
    one whose floor (:data:`price_report.TWICE_BAND_FLOOR`) were widened to
    0.5: the plant lands where only the floor's width decides."""
    collected, base = scored
    prices = dict(base)
    paired = sorted({s for pairs in collected.product_pairs.values() for p in pairs for s in p[:2]})
    prices.update({sku: base[sku] * 4 for sku in paired[1::2]})
    rows = [f"price smaller costs 2x+, same product: {t}" for t in TWICE_SCORED]
    out = _newly_out(scored, prices)
    _above(out, rows)
    for name in rows:
        assert 0.1 < out[name].achieved < 0.4, (name, out[name].achieved)


#: The 2x rows whose census band is narrower than the floor on the default
#: build, so the floor alone sets the band: each implies a share under 0.001.
TWICE_FLOORED = (
    "bolt_hex",
    "drill_jobber",
    "hex_key",
    "lock_nuts_nylon_insert",
    "nut_hex",
    "screw_socket_head",
    "set_screws_hex_socket",
)


def test_the_twice_band_floor_is_two_pairs_in_a_hundred_above_a_near_zero_target(price_rows):
    """Where the census implies a 2x share near 0, the band is the floor's
    0.02 above the target and runs down to 0: exactly, so a floor widened
    to any other width moves these edges. The tap and washer bands are wider
    than the floor and are the census's own."""
    rows = {row.name: row for row in price_rows if row.name.startswith("price smaller costs 2x+")}
    assert len(rows) == len(TWICE_SCORED) == 9
    for type_key in TWICE_SCORED:
        row = rows[f"price smaller costs 2x+, same product: {type_key}"]
        floored = type_key in TWICE_FLOORED
        assert (row.band[1] - row.target == pytest.approx(0.02, abs=1e-12)) is floored, (
            type_key,
            row.target,
            row.band,
        )
        assert (row.band[0] == 0.0) is floored, (type_key, row.band)


def test_breaking_every_tie_breaks_the_equal_price_row(scored):
    """Review plant M2: a list-price ladder makes the census's tap ties. With
    each tap SKU moved by its own millionth of a dollar, no pair ties."""
    collected, base = scored
    prices = dict(base)
    taps = sorted(s for s, t in collected.type_of.items() if t in price.EQUAL_PRICE_TYPES)
    prices.update({s: base[s] + (i + 1) * 1e-6 for i, s in enumerate(taps)})
    _below(_newly_out(scored, prices), [EQUAL_ROW.format(t) for t in price.EQUAL_PRICE_TYPES])


def test_tying_every_pair_breaks_the_equal_price_row(scored):
    collected, base = scored
    prices = {s: 10.0 if collected.type_of.get(s) in price.EQUAL_PRICE_TYPES else p
              for s, p in base.items()}  # fmt: skip
    _above(_newly_out(scored, prices), [EQUAL_ROW.format(t) for t in price.EQUAL_PRICE_TYPES])


# --- the declared exceptions ------------------------------------------------

#: The types whose placeholder model keeps the level the catalog had,
#: declared ``measured=False``: the ball-pein hammer's archived pages are
#: script shells, and the other hammer kinds (#305) have no census row either.
#: The price census has no key stock at all, so its model is
#: hand-set from surveyed listings (#108). Every table type (#101) joins them,
#: read from the registry and not listed: its price is a declared ladder
#: nobody measured. No row scores any of them.
NOT_MEASURED = frozenset({*hammers.KINDS, "key_stock", *tabletype.tables()})


def test_the_rows_score_every_priced_type_but_the_declared_exceptions(scored):
    """A type no row scores is either declared not measured, or borrows a
    census type's model (the button, flat and low head screws). A deepened
    breadth category is scored on its census p50 and p90/p10."""
    collected, _ = scored
    built = set(collected.type_of.values())
    unscored = {t for t in built if t not in price.CENSUS and t not in price.DEEPENED_CENSUS}
    assert unscored == NOT_MEASURED | set(price.BORROWS)
    assert {t for t in built if not price.model_for(t).measured} == NOT_MEASURED
    assert set(price.BORROWS.values()) <= set(price.CENSUS)


# --- a kit is priced from what it holds (#71) --------------------------------

#: What each kit kind holds, from the kit table.
KIT_PART = {kit.item: kit.part_type for kit in newtypes.KITS}

#: How far a kit's price may land from its contents' price times its material
#: and tier factors: the fitted kit factor (1.009) moved by its SKU noise
#: (sigma 0.022, about 5 sigma either way) and its ending. The default build
#: lands every kit within 0.969 to 1.059, the 100K one within 0.944 to 1.080.
OVER_CONTENTS = (0.9, 1.12)


def _inches(size: str) -> float:
    """A published size in inches: a thread's major diameter, else a length."""
    try:
        return parse_thread(size).major.inches
    except DimensionParseError:
        return parse_length(size).inches


def _pieces_price(facts: dict[str, Attribute], census: dict) -> float:
    """What a kit's pieces cost, worked from the census: each size it holds on
    its part type's own curve (standard tier, no material, no noise), at the
    census's per-piece share of that part's shown price, times how many of
    each size the kit holds."""
    part = KIT_PART[facts["Type"].value]
    model = price.model_for(part)
    row = census["deep_types"][part]
    share = row["per_piece_quantiles_usd"]["p50"] / row["price_quantiles_usd"]["p50"]
    sizes = facts["Sizes Included"].values or (facts["Sizes Included"].value,)
    pieces = facts["Piece Count"].value_num
    assert pieces is not None
    curve = sum(
        model.anchor * math.exp(price.structure(model, _inches(size), None, "standard"))
        for size in sizes
    )
    return curve * share * pieces / len(sizes)


def _over_contents(shown: float, facts: dict[str, Attribute], brand: str, contents: float) -> float:
    """A kit's price over its contents' price times its material and tier."""
    factor = price.MATERIAL_FACTORS.get(facts["Material"].value, 1.0)
    factor *= price.model_for(KIT).tiers[brands.tier_of(brand, KIT)]
    return shown / (contents * factor)


def test_a_kits_contents_are_its_pieces_priced_on_their_own_curves(census, kits):
    """:func:`price.kit_contents` is the census-worked price of what the kit
    holds, for every kit the default build makes, of every kind."""
    assert {facts["Type"].value for _, facts, _ in kits} == set(KIT_PART)
    for _, facts, _ in kits:
        assert price.kit_contents(facts) == pytest.approx(_pieces_price(facts, census), rel=1e-9)


def test_a_15_piece_hex_key_set_costs_what_its_keys_do(census, kits):
    """The inch set of ASME B18.3 keys, 0.028" to 3/8": its keys come to about
    $98 on the hex key curve. Priced as one group draw per page, with no
    reference to them, the default build's five sold for $9.55 to $1,525.45."""
    sets = [
        (shown, facts, brand)
        for shown, facts, brand in kits
        if facts["Type"].value == "Hex Key Set" and facts["Piece Count"].value_num == 15
    ]
    assert len(sets) == 5
    ratios = [
        (shown, round(_over_contents(shown, facts, brand, _pieces_price(facts, census)), 3))
        for shown, facts, brand in sets
    ]
    out = [r for r in ratios if not OVER_CONTENTS[0] < r[1] < OVER_CONTENTS[1]]
    assert not out, out


def test_each_kit_part_is_priced_at_its_census_per_piece_share(census):
    """A part's shown price may be a pack (every census socket screw is), and
    a kit holds pieces: the share is the census per-piece p50 over its shown
    p50, read here from the census itself."""
    assert set(price.PER_PIECE) == set(KIT_PART.values())
    for part, (each, shown) in price.PER_PIECE.items():
        row = census["deep_types"][part]
        assert each == row["per_piece_quantiles_usd"]["p50"], part
        assert shown == row["price_quantiles_usd"]["p50"], part


def test_the_kit_parts_are_the_kit_tables_kinds():
    assert price.KIT_PARTS == {
        "Hex Key Set": "hex_key",
        "Jobber Drill Set": "drill_jobber",
        "Socket Head Cap Screw Assortment": "screw_socket_head",
        "Tap Set": "tap_spiral_point",
    }


def test_a_kit_is_its_contents_at_one_factor_with_no_group_noise():
    """Group noise is one draw per page; loud enough to reach the census kit
    p90/p10 (about 2.2), it alone spreads kit prices about 79x against the
    2.8x their contents span, which is the price #71 replaces. The kit
    p90/p10 is pinned below its band instead (#76)."""
    model = price.model_for(KIT)
    assert KIT in price.CONTENTS_PRICED
    assert model.group_sigma == 0.0
    assert model.slope == price.CONTENTS_SLOPE == 1.0
    assert model.size_sigma == 0.0


def _build_kits(request, build: str) -> list[KitSku]:
    return (
        request.getfixturevalue("kits")
        if build == "default"
        else request.getfixturevalue("hundred_k")[1]
    )


@pytest.mark.parametrize(("build", "count"), [("default", 59), ("100K", 695)])
def test_each_kit_price_tracks_its_contents_at_both_builds(request, build, count):
    """Every kit, at either size, costs its contents' price times its
    material and tier, within its SKU noise and ending."""
    kits = _build_kits(request, build)
    assert len(kits) == count
    ratios = []
    for shown, facts, brand in kits:
        contents = price.kit_contents(facts)
        assert contents is not None, facts
        ratios.append(round(_over_contents(shown, facts, brand, contents), 3))
    out = [r for r in ratios if not OVER_CONTENTS[0] < r < OVER_CONTENTS[1]]
    assert not out, (len(out), out[:10])


def _kind_of(facts: dict[str, Attribute]) -> int:
    """The kit table row a kit SKU was built from: its kind, its piece count
    and its first size (inch and metric sets of one kind may hold as many)."""
    first = _inches(facts["Sizes Included"].values[0])
    (index,) = [
        i
        for i, kit in enumerate(newtypes.KITS)
        if kit.item == facts["Type"].value
        and kit.per_size * len(kit.designations or kit.sizes) == facts["Piece Count"].value_num
        and math.isclose(
            _inches(kit.designations[0]) if kit.designations else kit.sizes[0], first, rel_tol=0.01
        )
    ]
    return index


#: Each pair of kit table rows (larger, smaller) where the larger set holds
#: every size the smaller does and more: the metric and inch hex key sets and
#: the fractional drill indexes.
NESTED_KITS = 7


@pytest.mark.parametrize("build", ["default", "100K"])
def test_a_kit_holding_more_of_the_same_sizes_costs_more(request, build):
    """Where one set holds every size another does and more (the 15-piece
    inch hex set holds the 9-piece's keys), its contents are dearer and its
    kits cost more: the median kit price over material and tier, per kind."""
    kits = _build_kits(request, build)
    contents: dict[int, float] = {}
    priced: dict[int, list[float]] = defaultdict(list)
    for shown, facts, brand in kits:
        kind = _kind_of(facts)
        value = price.kit_contents(facts)
        assert value is not None
        contents.setdefault(kind, value)
        priced[kind].append(_over_contents(shown, facts, brand, 1.0))
    table = newtypes.KITS
    nested = [
        (big, small)
        for big in contents
        for small in contents
        if table[big].item == table[small].item
        and table[big].sizes
        and set(table[small].sizes) < set(table[big].sizes)
    ]
    assert len(nested) == NESTED_KITS
    for big, small in nested:
        assert contents[big] > contents[small], (table[big], table[small])
        dearer = statistics.median(priced[big]) > statistics.median(priced[small])
        assert dearer, (table[big].item, len(table[big].sizes), len(table[small].sizes))


# --- the 100K catalog (#52: "within tolerance at default size and at 100K") --

#: Every price row's name, as :func:`price_report.price_rows` writes it.
ROW_NAMES = sorted(
    [f"price p50 (USD): {t}" for t in price.CENSUS]
    + [SPREAD_ROW.format(t) for t in price.CENSUS]
    + [ORDER_ROW.format(t) for t in price.CENSUS]
    + [LENGTH_ROW.format(t) for t in price.LENGTH_CENSUS]
    + [EQUAL_ROW.format(t) for t in price.EQUAL_PRICE_TYPES]
    + [f"price smaller costs 2x+, same product: {t}" for t in TWICE_SCORED]
    + [BRAND_ROW.format(t) for t in price.BRAND_CENSUS]
    + [f"price economy brands over others, same spec (median): {price.BRAND_SPREAD_TYPE}"]
    + [f"price ending {cls}" for cls in price_report.ENDING_CLASSES]
    + [f"price p50 (USD): {t}" for t in price.DEEPENED_CENSUS]
    + [SPREAD_ROW.format(t) for t in price.DEEPENED_CENSUS]
)


@pytest.fixture(scope="module")
def hundred_k() -> tuple[Catalog, list[KitSku]]:
    """The 100K build and its kits (about 35 s)."""
    return _recorded_build(GeneratorConfig(lines=LARGE_BUILD_LINES))


@pytest.fixture(scope="module")
def hundred_k_rows(hundred_k) -> dict:
    """Every price row of the 100K build, by name."""
    return {row.name: row for row in price_report.price_comparisons(hundred_k[0])}


def test_the_row_names_are_the_rows_the_default_build_scores(price_rows):
    assert sorted(row.name for row in price_rows) == ROW_NAMES


def test_the_100k_build_scores_every_row_the_default_build_scores(hundred_k_rows):
    assert sorted(hundred_k_rows) == ROW_NAMES


@pytest.mark.parametrize("name", ROW_NAMES)
def test_each_price_row_is_within_its_band_or_its_pin_holds_at_100k(hundred_k_rows, name):
    """The band is the census's, whatever the catalog's size; a pin may not
    worsen at 100K any more than at the default size."""
    row = hundred_k_rows[name]
    if name in price.PINNED_SHORTFALLS:
        assert price_report.pin_holds(row, 1), (row.achieved, row.band, price.PINNED_FIGURES[name])
    else:
        assert row.within, f"{row.achieved:.4f} outside {row.band[0]:.4f}-{row.band[1]:.4f}"


@pytest.mark.parametrize("name", sorted(PINNED_SIDES))
@pytest.mark.parametrize("build", [0, 1])
def test_each_recorded_figure_is_the_figure_its_build_produces(
    price_rows, hundred_k_rows, name, build
):
    """A pin bound is only as tight as its record, so each
    record is the build's own figure, to the precision it is written at
    (each build is one seed, so this is exact). A record loosened by hand,
    or left loose after the row improves, is red here."""
    row = {r.name: r for r in price_rows}[name] if build == 0 else hundred_k_rows[name]
    recorded = _recorded(name)[build]
    built = None if row.within else round(row.achieved, price_report.recorded_digits(name))
    assert recorded == built, f"{name}: recorded {recorded} at build {build}, built {built}"


# --- the measured breadth categories ----------------------------------------

#: Where a breadth draw's ``u`` lands: the middle of twenty equal slices.
U_GRID = tuple((i + 0.5) / 20 for i in range(20))


@pytest.mark.parametrize("key", sorted(price.BREADTH_CENSUS))
def test_each_measured_breadth_categorys_p50_is_within_its_census_band(key):
    """A breadth category builds one line of one or two SKUs at any catalog
    size, so a p50 over its built SKUs reads where the size rotation landed.
    The row is over what :func:`price.breadth_price` draws at every size and
    ``u``, standard tier, held to the deep types' p50 band."""
    row = breadth.row_for(key)
    drawn = [
        price.breadth_price(row, size, "standard", u, 0.0)
        for size in row.size_values
        for u in U_GRID
    ]
    census_p50 = price.BREADTH_CENSUS[key][1]
    low, high = (census_p50 * f for f in price_report.P50_BAND)
    assert low <= statistics.median(drawn) <= high, (statistics.median(drawn), low, high)


@pytest.mark.parametrize("tier", ["economy", "premium"])
def test_a_measured_breadth_skus_tier_scales_its_price_by_the_tier_factor(tier):
    """Same row, size and draws: the tier moves the price by its factor, to
    within the cent an "other" ending rounds to (under 1% at these prices)."""
    for key in sorted(price.BREADTH_CENSUS):
        row = breadth.row_for(key)
        size = row.size_values[len(row.size_values) // 2]
        ratio = price.breadth_price(row, size, tier, 0.5, 0.0) / price.breadth_price(
            row, size, "standard", 0.5, 0.0
        )
        assert abs(ratio / price.TIER_FACTORS[tier] - 1) < 0.01, (key, ratio)
