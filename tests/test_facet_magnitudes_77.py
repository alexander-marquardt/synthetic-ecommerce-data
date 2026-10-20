"""The continuity test counts a quantity's MAGNITUDES, not its published spellings (gen#77).

A roller chain's pitch is one of ASME B29.1's 13 sizes, and four brand feeds write each one
four ways (``1/2"``, ``1/2 in``, ``0.500"``, ``1/2 in.``). Counted as spellings, 68 chains give
35 distinct values over 68 products, 0.51, and the series reads as a continuum. It is a standard
set, so the distinct value is the magnitude (``facets_num``), and a spelling is a way of writing it.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.prism.derive import (
    RANGE_DISPERSION,
    RANGE_MIN_DOCS,
    decide,
    measure,
    quantity_sources,
)
from synthetic_ecommerce_data.prism.field_map import render

SERIES = 13
#: How a brand feed writes the n-th size: four spellings of one magnitude.
SPELLINGS = ('{}"', "{} in", '{:.3f}"', "{} in.")
CHAIN_KEYS = ("chain_pitch", "roller_dia", "inside_width")


def _series_rows(products: int, spellings: int) -> list[dict]:
    """``products`` one-SKU products, each on one of 13 sizes, in one of ``spellings`` spellings.

    The size and the spelling advance independently, so every size is met in every spelling.
    """
    assert "Probe" not in quantity_sources(), "the series must stay undeclared: the ratio decides"
    rows = []
    for p in range(products):
        size = p % SERIES
        spelling = (p // SERIES) % spellings
        magnitude = (size + 1) / 16
        rows.append(
            {
                "product_id": f"P{p}",
                "product_type": "probe_type",
                "facets": {"probe_span": [f"{magnitude:.4f} spelled {spelling}"]},
                "facets_num": {"probe_span": magnitude},
                "attributes": [{"name": "Probe", "key": "probe_span", "value": "x"}],
            }
        )
    return rows


@pytest.mark.parametrize(("products", "spellings"), [(68, 4), (68, 6), (130, 8)])
def test_a_thirteen_size_series_in_several_spellings_has_thirteen_values(
    products: int, spellings: int
) -> None:
    """The issue's own case: 13 sizes over a small type's products, several spellings each."""
    stats = measure(_series_rows(products, spellings))["probe_span"]
    assert stats.cardinality > SERIES, "the probe must publish more spellings than sizes"
    assert stats.dispersion == pytest.approx(SERIES / products)
    assert stats.dispersion < RANGE_DISPERSION, (
        f"{stats.cardinality} spellings of {SERIES} sizes read as a continuum "
        f"({stats.dispersion:.2f}): the test counts spellings, not magnitudes"
    )


def test_a_standard_series_past_the_evidence_floor_is_a_discrete_list() -> None:
    """At the floor's product count, where the ratio decides, 20 spellings must not flip it."""
    stats = measure(_series_rows(RANGE_MIN_DOCS + 10, 20))["probe_span"]
    assert stats.products >= RANGE_MIN_DOCS
    assert not stats.is_continuous
    assert "a discrete standard set" in decide(stats).reason


def test_a_true_continuum_is_still_a_continuum() -> None:
    """Counting magnitudes must not turn every quantity into a ladder: unique values stay unique."""
    rows = _series_rows(RANGE_MIN_DOCS + 10, 1)
    for index, row in enumerate(rows):
        row["facets_num"]["probe_span"] = 1 + index / 7
        row["facets"]["probe_span"] = [f"{1 + index / 7:.3f}"]
    stats = measure(rows)["probe_span"]
    assert stats.is_continuous


@pytest.fixture(scope="module")
def default_rows() -> list[dict]:
    return list(emit.iter_flat(generate(GeneratorConfig())))


def test_chains_publish_brand_spellings_and_stay_discrete(default_rows: list[dict]) -> None:
    """The three chain dimensions take their brand's spelling again, and none reads as a range."""
    stats = measure(default_rows)
    for key in CHAIN_KEYS:
        found = stats[key]
        assert found.cardinality > found.magnitudes, (
            f"{key}: {found.cardinality} spellings of {found.magnitudes} sizes; "
            "one spelling means a brand's feed style is not reaching the chain"
        )
        assert found.dispersion < RANGE_DISPERSION, (key, found.dispersion)
        assert not decide(found).stats.is_continuous


def test_chain_dimensions_are_discrete_lists_in_the_field_map(default_rows: list[dict]) -> None:
    """No chain key is a numeric (range) entry, so none needs a place in ``filter_routing.hard``."""
    text = render(default_rows)
    for key in CHAIN_KEYS:
        block = text.split(f"- name: {key}\n", 1)[1].split("\n  # ", 1)[0]
        assert "type: numeric" not in block, key


def test_a_brand_feed_never_rounds_a_chain_dimension_into_a_second_magnitude(
    default_rows: list[dict],
) -> None:
    """A three-decimal feed writes B29.1's 3/16 as ``0.1875``, not ``0.188``.

    The chain's sizes are the table's, so each dimension's magnitude is one of the table's own.
    """
    from synthetic_ecommerce_data.domains.industrial.product_types.motion import roller_chain

    table = {
        "chain_pitch": {float(pitch) for _, pitch, _, _ in roller_chain.ANSI},
        "roller_dia": {float(roller) for _, _, roller, _ in roller_chain.ANSI if roller},
        "inside_width": {float(width) for _, _, _, width in roller_chain.ANSI},
    }
    chains = [row for row in default_rows if row["product_type"] == "roller_chain"]
    assert chains, "no roller chains in the default build"
    for key, sizes in table.items():
        published = {row["facets_num"][key] for row in chains if key in row["facets_num"]}
        assert published, key
        assert published <= sizes, (key, sorted(published - sizes))
