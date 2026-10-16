"""The hex bolt's pack is drawn per group page and priced within a size (#86).

#65 ranked the pack by size, which left a census cell (one pack) holding few
size pairs and the shown price spread by a pack the census does not measure
that way. The census measures, within one spec, how the per-piece price falls
when the pack grows (``same_spec_larger_pack_per_piece_ratio``, p50 0.5778),
so the pack is drawn per page, independent of the size, and priced on the
elasticity that ratio gives.
"""

from __future__ import annotations

import itertools
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import price
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import price_report
from synthetic_ecommerce_data.domains.industrial.generate import generate

CENSUS_FILE = (
    Path(__file__).resolve().parent.parent / "reference-statistics" / "P2_price_census.json"
)


@pytest.fixture(scope="module")
def census() -> dict:
    return json.loads(CENSUS_FILE.read_text())


def _median_pair_ratio(counts: dict[int, int]) -> float:
    """The median larger/smaller ratio over two different census packs, each
    pair weighed by how many census SKUs sell in both."""
    pairs = sorted(
        (big / small, counts[small] * counts[big])
        for small, big in itertools.combinations(sorted(counts), 2)
    )
    half = sum(weight for _, weight in pairs) / 2
    seen = 0.0
    for ratio, weight in pairs:
        seen += weight
        if seen >= half:
            return ratio
    raise AssertionError("no pairs")


def test_the_bolt_pack_elasticity_is_the_census_ratio_over_the_median_pack_pair(census):
    pack = census["deep_types"]["bolt_hex"]["pack_vs_each"]
    discount = pack["same_spec_larger_pack_per_piece_ratio"]["quantiles"]["p50"]
    pair = _median_pair_ratio(price.PACK_COUNTS["bolt_hex"])
    assert pair == 5.0
    elasticity = price.PACK_ELASTICITY["bolt_hex"]
    assert elasticity == round(1 + math.log(discount) / math.log(pair), 3) == 0.659
    # The elasticity gives back the census discount on the median pair of packs.
    assert pair ** (elasticity - 1) == pytest.approx(discount, abs=0.005)


def test_the_bolt_prices_its_pack_on_that_elasticity():
    model = price.MODELS["bolt_hex"]
    assert model.pack_attribute == "Package Quantity"
    assert model.pack_slope == price.PACK_ELASTICITY["bolt_hex"]
    assert "bolt_hex" not in price.PACK_SLOPES


def test_a_page_pack_follows_the_census_counts_and_never_falls_as_the_draw_rises():
    steps = 1000
    drawn = [price.page_pack("bolt_hex", (i + 0.5) / steps) for i in range(steps)]
    assert drawn == sorted(drawn)
    counts = price.PACK_COUNTS["bolt_hex"]
    total = sum(counts.values())
    for qty, n in counts.items():
        assert abs(drawn.count(qty) / steps - n / total) <= 1.0 / steps + 1e-9, qty


def test_a_page_pack_draw_is_its_pages_own_stream():
    page = (("Finish", "Zinc Plated"), ("Grade", "Grade 5"))
    draw = price.page_pack_draw(7, "bolt_hex", "Acme", page)
    assert draw == price.page_pack_draw(7, "bolt_hex", "Acme", page)
    assert 0.0 <= draw < 1.0
    others = {
        price.page_pack_draw(8, "bolt_hex", "Acme", page),
        price.page_pack_draw(7, "bolt_hex", "Other", page),
        price.page_pack_draw(7, "bolt_hex", "Acme", (("Finish", "Black Oxide"),)),
    }
    assert draw not in others
    assert len(others) == 3


@pytest.fixture(scope="module")
def bolt_lines():
    """Every default-build bolt line as (page, size, pack): a page is a brand
    and the non-number line attributes every bolt line carries."""
    catalog = generate(GeneratorConfig())
    lines = [line for line in catalog.lines if line.type_key == "bolt_hex"]
    carried = set.intersection(
        *({a.name for a in line.attributes if price.holds_equal("bolt_hex", a)} for line in lines)
    )
    carried.discard("Package Quantity")
    out = []
    for line in lines:
        values = {a.name: a.value for a in line.attributes}
        page = (line.brand, tuple(sorted((n, values[n]) for n in carried)))
        child = line.children[0]
        facts = {a.name: a for a in catalog.merged_attributes(line, child)}
        key = price.KEYS["bolt_hex"](facts)
        out.append((page, key, facts["Package Quantity"].value_num))
    return out


def test_every_line_of_a_page_shares_one_pack(bolt_lines):
    by_page = defaultdict(set)
    for page, _, pack in bolt_lines:
        by_page[page].add(pack)
    assert len(by_page) < len(bolt_lines)
    assert all(len(packs) == 1 for packs in by_page.values())


def test_the_bolt_pack_is_not_ranked_by_size(bolt_lines):
    """#65's ranked pack correlated -0.96 with the key, in logs."""
    r = statistics.correlation(
        [math.log(key) for _, key, _ in bolt_lines], [math.log(pack) for _, _, pack in bolt_lines]
    )
    assert abs(r) < 0.25, r


def test_most_sizes_are_offered_in_more_than_one_pack(bolt_lines):
    by_size = defaultdict(set)
    for _, key, pack in bolt_lines:
        by_size[round(key, 4)].add(pack)
    several = sum(len(packs) > 1 for packs in by_size.values())
    assert several / len(by_size) >= 0.8, (several, len(by_size))


def test_a_cell_pairs_every_size_of_a_page_again(bolt_lines):
    """The pack is a page's, so holding it equal no longer splits a page: the
    bolt's order row counts its pairs again (#65 left 8 of 30)."""
    catalog = generate(GeneratorConfig())
    pairs = price_report.collect(catalog).pairs["bolt_hex"]
    assert len(pairs) >= 20, len(pairs)
