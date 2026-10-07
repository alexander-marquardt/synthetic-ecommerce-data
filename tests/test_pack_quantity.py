"""Bolts and socket screws publish the pack their shown price is for (#65)."""

from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog import price, price_report
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate

CENSUS_FILE = (
    Path(__file__).resolve().parent.parent / "reference-statistics" / "P2_price_census.json"
)

#: The types whose builder draws the pack, and the census type each one's
#: counts and price model are (the socket family borrows the socket's).
PACKED = {
    "bolt_hex": "bolt_hex",
    "screw_socket_head": "screw_socket_head",
    "screw_button_head": "screw_socket_head",
    "screw_flat_head": "screw_socket_head",
    "screw_low_head": "screw_socket_head",
}


@pytest.fixture(scope="module")
def census() -> dict:
    return json.loads(CENSUS_FILE.read_text())


@pytest.fixture(scope="module")
def packs() -> dict[str, list[tuple[float, float | None]]]:
    """Per packed type, every SKU's (key dimension, published pack), read off
    the default build's published records."""
    catalog = generate(GeneratorConfig())
    type_of = price_report.collect(catalog).type_of
    out: dict[str, list[tuple[float, float | None]]] = {t: [] for t in PACKED}
    for line, child in catalog.all_skus():
        type_key = type_of.get(child.sku)
        if type_key not in PACKED:
            continue
        facts = {a.name: a for a in catalog.merged_attributes(line, child)}
        key = price.KEYS[PACKED[type_key]](facts)
        pack = facts["Package Quantity"].value_num if "Package Quantity" in facts else None
        assert key is not None
        out[type_key].append((key, pack))
    return out


@pytest.mark.parametrize("type_key", sorted(price.PACK_SLOPES))
def test_each_pack_slope_is_the_census_figure(census, type_key):
    pack = census["deep_types"][type_key]["pack_vs_each"]
    assert price.PACK_SLOPES[type_key] == pack["pooled_loglog_slope_price_on_pack_qty"]


@pytest.mark.parametrize("type_key", sorted(price.PACK_COUNTS))
def test_each_pack_count_is_the_census_count(census, type_key):
    counts = census["deep_types"][type_key]["pack_vs_each"]["pack_quantity_counts"]
    assert price.PACK_COUNTS[type_key] == {int(qty): n for qty, n in counts.items()}


def test_the_drawn_packs_are_the_bolts_and_the_socket_screws():
    assert set(price.PACK_COUNTS) == {"bolt_hex", "screw_socket_head"}
    assert set(PACKED.values()) == set(price.PACK_COUNTS)


@pytest.mark.parametrize("type_key", sorted(PACKED))
def test_each_packed_type_prices_its_pack_on_the_census_slope(type_key):
    model = price.model_for(type_key)
    assert model.pack_attribute == "Package Quantity"
    assert model.pack_slope == price.PACK_SLOPES[PACKED[type_key]]


@pytest.mark.parametrize("type_key", sorted(PACKED))
def test_every_packed_sku_publishes_a_census_pack(packs, type_key):
    census_packs = set(price.PACK_COUNTS[PACKED[type_key]])
    published = [pack for _, pack in packs[type_key]]
    assert len(published) > 0
    assert [p for p in published if p is None or int(p) not in census_packs] == []


@pytest.mark.parametrize("type_key", sorted(price.PACK_COUNTS))
def test_the_pack_never_grows_with_the_size(type_key):
    for sizes in (6, 9, 15):
        for u in (0.0, 0.3, 0.7, 0.999):
            drawn = [price.pack_quantity(type_key, rank, sizes, u) for rank in range(sizes)]
            assert drawn == sorted(drawn, reverse=True), (sizes, u, drawn)


@pytest.mark.parametrize("type_key", sorted(price.PACK_COUNTS))
def test_an_even_spread_over_the_sizes_publishes_the_census_counts(type_key):
    """Every size's slice, sampled evenly, gives back each census share to
    within one step of the grid."""
    sizes, steps = 15, 400
    drawn = Counter(
        price.pack_quantity(type_key, rank, sizes, (i + 0.5) / steps)
        for rank in range(sizes)
        for i in range(steps)
    )
    counts = price.PACK_COUNTS[type_key]
    total = sum(counts.values())
    for qty, n in counts.items():
        assert abs(drawn[qty] / (sizes * steps) - n / total) <= 1.0 / steps, qty


@pytest.mark.parametrize("type_key,census_median", [("bolt_hex", 25), ("screw_socket_head", 100)])
def test_the_builds_median_pack_is_the_census_median(packs, type_key, census_median):
    published = [pack for _, pack in packs[type_key] if pack is not None]
    assert len(published) == len(packs[type_key])
    assert statistics.median_low(published) == census_median


def test_the_builds_bolt_pack_falls_as_the_diameter_grows(packs):
    rows = sorted((key, pack) for key, pack in packs["bolt_hex"] if pack is not None)
    assert len(rows) == len(packs["bolt_hex"])
    third = len(rows) // 3
    small = statistics.median(pack for _, pack in rows[:third])
    large = statistics.median(pack for _, pack in rows[-third:])
    assert small >= 4 * large, (small, large)


def test_the_bolt_slope_is_no_longer_cut():
    assert "bolt_hex" not in price.SLOPE_CUTS
    assert price.MODELS["bolt_hex"].slope == price.CENSUS["bolt_hex"].slope
    assert price.MODELS["bolt_hex"].length_slope == price.LENGTH_CENSUS["bolt_hex"].slope
