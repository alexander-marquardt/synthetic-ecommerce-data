"""The grouped pass (#710): threaded fasteners carry a run of lengths and end-mill lines a run of
diameters, beside the flat products, so a search page has products to group.

These tests build the grouped types alone, once with the pass and once without, and hold
the pass to its per-type tables, to its targets, to its size, and to being additive: every
SKU the flat build makes is in the grouped build unchanged. The reference-query coverage is
held on the COMMITTED catalog.
"""

from __future__ import annotations

import functools
import json
from dataclasses import replace
from pathlib import Path
from statistics import median

import pytest

from synthetic_ecommerce_data.core import bundle
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import grouped, muststock
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.product_split import (
    distribution_problems,
    skus_per_product,
    split_products,
)

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"
TYPES = sorted(grouped.VARIANTS)

#: The reference queries the 2026-10-28 comment on #710 counts, each to have at least
#: :data:`.grouped.TARGET_PRODUCTS` matching products.
REFERENCE_ROWS = (
    "1/2 end mill",
    "3/8 square end mills",
    "3/16 square end mills",
    "1 inch square end mills",
    "1/8 ball end mills",
    "1/16 ball end mills",
    "4mm end mill",
    "11 mm end mills",
    "2.5mm end mill",
    "25mm end mill",
    "15 mm ball end mills",
    "4mm carbide end mill",
    "5/16-18 x 3/4 button head cap screw",
    "5/16-18x3/4 low socket head cap screw",
    "1/4 x 3 1/4 cap screws",
    "1/4-20 screws",
    "m12x1.75 socket cap screws",
    'hex head cap screw: 7/16-14, 1-3/4" length under head, grade 8 steel, zinc finish',
    "m6x1 set screws",
)
ENTRIES = {e.example: e for e in (*muststock.MUST_STOCK, *grouped.TARGETS)}


def _table_median(table) -> int:
    total = sum(weight for _, weight in table)
    running = 0.0
    for count, weight in sorted(table):
        running += weight / total
        if running >= 0.5:
            return count
    raise AssertionError("empty table")


def _carries(entry, line) -> bool:
    return any(
        entry.matches(line.type_key, {a.name: a.value for a in (*line.attributes, *c.attributes)})
        for c in line.children
    )


@pytest.fixture(scope="module")
def flat():
    return generate(replace(GeneratorConfig(), grouped=False), types=TYPES)


@pytest.fixture(scope="module")
def full():
    return generate(GeneratorConfig(), types=TYPES)


@pytest.fixture(scope="module")
def added(flat, full):
    """Type -> the products the grouped pass added."""
    before = {line.product_id for line in flat.lines}
    out: dict[str, list] = {key: [] for key in TYPES}
    for line in full.lines:
        if line.product_id not in before:
            out[line.type_key].append(line)
    return out


def test_the_pass_is_additive(flat, full):
    """Every product of the flat build is in the grouped build, unchanged: ids, titles, SKUs."""
    after = {line.product_id: line for line in full.lines}
    assert [after.get(line.product_id) for line in flat.lines] == list(flat.lines)
    assert len(full.lines) > len(flat.lines)


@pytest.mark.parametrize("key", TYPES)
def test_each_type_draws_its_own_table(key, added, full):
    """The grouped products follow the type's table (a run of 6 or more, median near the
    table's), and the type keeps its single-SKU products: the catalog stays a mixture."""
    table = grouped.VARIANTS[key]
    sizes = [len(line.children) for line in added[key]]
    assert sizes, f"{key}: the pass added no product"
    smallest, largest = min(c for c, _ in table), max(c for c, _ in table)
    # The series pool caps a draw (a small thread offers only a few lengths), so the median
    # may sit below the table's, never below its smallest count, and never above its own.
    assert smallest <= median(sizes) <= _table_median(table), (key, sorted(sizes))
    assert max(sizes) <= largest
    assert max(sizes) > max(c for c, _ in GeneratorConfig().variants_per_product)
    singles = sum(size == 1 for size in sizes) / len(sizes)
    assert singles <= 0.05, f"{key}: {singles:.0%} of its grouped products are single-SKU"
    everyone = [len(line.children) for line in full.lines if line.type_key == key]
    assert sum(size == 1 for size in everyone) / len(everyone) >= 0.35, key


@pytest.mark.parametrize("key", TYPES)
def test_the_pass_stays_modest(key, flat, added):
    """Its share of the type's products, plus what the targets the type owns want: no more."""
    own = [line for line in flat.lines if line.type_key == key]
    wanted = sum(
        grouped.wanted(sum(_carries(entry, line) for line in own))
        for entry in grouped.TARGETS
        if entry.types[0] == key
    )
    assert len(added[key]) <= round(len(own) * grouped.SHARE) + wanted


def test_the_sku_total_grows_by_a_modest_share(flat, full):
    before = sum(len(line.children) for line in flat.lines)
    after = sum(len(line.children) for line in full.lines)
    assert 1.0 < after / before <= 1.35, (before, after)


@pytest.mark.parametrize("entry", grouped.TARGETS, ids=lambda e: e.example)
def test_every_target_has_its_grouped_products(entry, added):
    carried = [line for line in added[entry.types[0]] if _carries(entry, line)]
    assert len(carried) >= grouped.TARGET_PRODUCTS, entry.example
    assert all(len(line.children) > 1 for line in carried), entry.example


def test_no_target_no_grouped_products_for_it(monkeypatch, flat):
    """Planted regression: without its target, the R8 hex bolt has no grouped product."""
    r8 = next(e for e in grouped.TARGETS if e.example.startswith("hex head cap screw"))
    monkeypatch.setattr(grouped, "TARGETS", tuple(e for e in grouped.TARGETS if e is not r8))
    before = {line.product_id for line in flat.lines}
    built = generate(GeneratorConfig(), types=["bolt_hex"])
    assert not [ln for ln in built.lines if ln.product_id not in before and _carries(r8, ln)]


def test_a_target_no_builder_reaches_fails_the_build(monkeypatch):
    impossible = grouped._target("no such thread", ("bolt_hex",), thread="9/16-99")
    monkeypatch.setattr(grouped, "TARGETS", (impossible,))
    monkeypatch.setattr(grouped, "MAX_ATTEMPTS", 50)
    with pytest.raises(grouped.GroupedUnmetError, match="no such thread"):
        generate(GeneratorConfig(), types=["bolt_hex"])


def test_product_constants_agree_and_the_distribution_check_reads_the_type_table(full):
    """gen#63 holds on the grouped products, and the build's own distribution check passes:
    a grouped type's maximum is its table's. Without the pass, the same maximum is refused."""
    assert split_products(full) == {}
    distribution = skus_per_product(full)
    assert distribution_problems(distribution, GeneratorConfig()) == []
    refused = distribution_problems(distribution, replace(GeneratorConfig(), grouped=False))
    assert refused and all("the knob's maximum is 5" in p for p in refused)


@functools.cache
def _golden_products() -> tuple[tuple[str, tuple[dict[str, str], ...]], ...]:
    """(type, the variants' published records) per committed product."""
    facets_by_sku = bundle.flat_facets(GOLDEN)
    out = []
    for text in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines():
        parent = json.loads(text)
        out.append((parent["product_type"], tuple(bundle.records(parent, facets_by_sku))))
    return tuple(out)


@pytest.mark.parametrize("example", REFERENCE_ROWS)
def test_every_reference_query_has_five_products_in_the_committed_catalog(example):
    entry = ENTRIES[example]
    products = sum(
        any(entry.matches(type_key, r) for r in records) for type_key, records in _golden_products()
    )
    assert products >= grouped.TARGET_PRODUCTS, (example, products)
