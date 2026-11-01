"""The grouped pass (#710, #766): threaded fasteners carry a run of lengths and end-mill and
drill lines a run of diameters, as most of each type's products, so a search page has products
to group.

These tests build the grouped types alone, once with the pass and once without, and hold
the pass to its per-type tables, to its targets, to its SKU total, and to the flat products
that stay: they are the first of the flat build's, unchanged. The reference-query coverage
is held on the COMMITTED catalog.
"""

from __future__ import annotations

import functools
import json
import re
from dataclasses import replace
from pathlib import Path
from statistics import median

import pytest

from synthetic_ecommerce_data.core import bundle
from synthetic_ecommerce_data.core.config import LARGE_BUILD_LINES, GeneratorConfig
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


_END_MILLS = ("end_mill_square", "end_mill_ball")
#: The attribute a run walks, for the types whose sizes are all one number.
_SIZE_AXES = {
    "end_mill_square": "Milling Dia.",
    "end_mill_ball": "Milling Dia.",
    "drill_jobber": "Size",
}


def _size_pool(key: str, axis: str, added, *, metric: bool) -> list[float]:
    """Every size of ``axis`` the type's run lines offer, in one system, ascending."""
    return sorted(
        {
            a.value_num
            for line in added[key]
            for child in line.children
            for a in child.attributes
            if a.name == axis and ("mm" in a.value) == metric
        }
    )


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
def large():
    """The build whose figures issue #766 states."""
    return generate(replace(GeneratorConfig(), lines=LARGE_BUILD_LINES), types=TYPES)


@pytest.fixture(scope="module")
def large_flat():
    return generate(replace(GeneratorConfig(), lines=LARGE_BUILD_LINES, grouped=False), types=TYPES)


@pytest.fixture(scope="module")
def added(flat, full):
    """Type -> the products the grouped pass added."""
    before = {line.product_id for line in flat.lines}
    out: dict[str, list] = {key: [] for key in TYPES}
    for line in full.lines:
        if line.product_id not in before:
            out[line.type_key].append(line)
    return out


def _own(catalog, key: str) -> list:
    return [line for line in catalog.lines if line.type_key == key]


@pytest.mark.parametrize("key", TYPES)
def test_the_flat_products_that_stay_are_the_flat_builds_first(key, large_flat, large):
    """Each is the flat build's product at the same place, unchanged: id, title, SKUs."""
    # A draft the type refuses leaves its place empty, so a few fewer than the share stayed.
    kept = int(grouped.flat_products(LARGE_BUILD_LINES, len(_own(large_flat, key))) * 0.9)
    assert kept >= 5
    assert _own(large, key)[:kept] == _own(large_flat, key)[:kept]


@pytest.mark.parametrize("key", TYPES)
def test_most_products_are_run_lines(key, large):
    """Issue #766: a run of 6 or more is most of the type, and it stays a mixture."""
    sizes = [len(line.children) for line in _own(large, key)]
    assert sum(size >= 6 for size in sizes) / len(sizes) > 0.5, key
    assert sum(size == 1 for size in sizes) / len(sizes) >= 0.05, key


@pytest.mark.parametrize("key", _END_MILLS)
def test_end_mill_runs_go_past_the_nine_matching_shanks(key, added):
    """Issue #766: a line stopped at 9 diameters, the size of the matching-shank pool."""
    assert max(len(line.children) for line in added[key]) > 9


@pytest.mark.parametrize(("key", "axis"), _SIZE_AXES.items())
def test_a_run_line_sells_neighboring_sizes(key, axis, added):
    """A line reads 1/8", 3/16", 1/4", never 1", 1-1/2", 1/16", 3/32": no window wraps round
    the series and no shuffled pool scatters it. A rejected SKU may leave one small hole."""
    lines = [line for line in added[key] if len(line.children) >= 6]
    assert lines
    for line in lines:
        sizes = [next(a for a in child.attributes if a.name == axis) for child in line.children]
        metric = sum("mm" in a.value for a in sizes) * 2 > len(sizes)
        pool = _size_pool(key, axis, added, metric=metric)
        # A unit-mixing defect states one SKU in the other system: not a place in this pool.
        places = sorted(pool.index(a.value_num) for a in sizes if a.value_num in pool)
        assert max(b - a for a, b in zip(places, places[1:], strict=False)) <= 5, line.product_id


@pytest.mark.parametrize("key", TYPES)
def test_each_type_draws_its_own_table(key, added):
    """The grouped products follow the type's table: a run of 6 or more, median near the
    table's."""
    table = grouped.VARIANTS[key]
    sizes = [len(line.children) for line in added[key]]
    assert sizes, f"{key}: the pass added no product"
    smallest, largest = min(c for c, _ in table), max(c for c, _ in table)
    # The series pool caps a draw (a small thread offers only a few lengths), so the median
    # may sit below the table's, never below its smallest count, and never above its own.
    # A small build's few products may land a little above it.
    assert smallest <= median(sizes) <= _table_median(table) + 2, (key, sorted(sizes))
    assert max(sizes) <= largest
    assert max(sizes) > max(c for c, _ in GeneratorConfig().variants_per_product)
    singles = sum(size == 1 for size in sizes) / len(sizes)
    assert singles <= 0.05, f"{key}: {singles:.0%} of its grouped products are single-SKU"


@pytest.mark.parametrize("key", TYPES)
def test_the_pass_stops_at_the_types_budget(key, large_flat, large, monkeypatch):
    """The budget is what stops the pass, and it moves the type's SKUs instead of adding to
    them: half the scale builds about half the run SKUs."""
    before = sum(len(line.children) for line in _own(large_flat, key))
    after = sum(len(line.children) for line in _own(large, key))
    assert 0.8 <= after / before <= 1.35, (key, before, after)
    monkeypatch.setattr(grouped, "SKU_SCALE", grouped.SKU_SCALE / 2)
    config = replace(GeneratorConfig(), lines=LARGE_BUILD_LINES)
    halved = sum(len(line.children) for line in generate(config, types=[key]).lines)
    assert halved < after * 0.65, (key, after, halved)


def test_the_sku_total_holds(large_flat, large):
    """Issue #766: the SKUs move into runs, and the total stays within about 10%."""
    before = sum(len(line.children) for line in large_flat.lines)
    after = sum(len(line.children) for line in large.lines)
    assert 0.9 <= after / before <= 1.2, (before, after)
    assert len(large.lines) < len(large_flat.lines) / 2


@pytest.mark.parametrize("key", TYPES)
def test_a_small_build_keeps_every_flat_product(key, flat, full):
    """A run line is one size, so a small build keeps its flat products and only adds runs."""
    # The tail is the must-stock lines, which draw the type's table in a grouped build.
    kept = int(len(_own(flat, key)) * 0.9)
    assert _own(full, key)[:kept] == _own(flat, key)[:kept]
    assert grouped.flat_products(grouped.RUN_BUILD_LINES - 1, 4000) == 4000


def test_a_large_build_keeps_its_share_above_the_floor():
    assert grouped.flat_products(grouped.RUN_BUILD_LINES, 4000) == 400
    assert grouped.flat_products(grouped.RUN_BUILD_LINES, 1000) == grouped.FLAT_FLOOR
    assert grouped.flat_products(grouped.RUN_BUILD_LINES, 20) == 20


def test_a_type_with_no_table_builds_flat_alone():
    """A type outside the table keeps every product: the pass moves nothing there."""
    plain = generate(GeneratorConfig(), types=["hex_key"]).lines
    assert plain == generate(replace(GeneratorConfig(), grouped=False), types=["hex_key"]).lines


def test_a_product_title_names_no_sku_value(full):
    """Issue #766: the title heads a grouped card, so it may not name a value on which the
    product's SKUs differ, such as a diameter."""
    for line in full.lines:
        seen: dict[str, set[str]] = {}
        for child in line.children:
            for a in child.attributes:
                seen.setdefault(a.name, set()).add(a.value)
        for name, values in seen.items():
            if len(values) == 1:
                continue
            for value in values:
                named = re.search(rf"(?<![\w./-]){re.escape(value)}(?![\w/-])", line.title)
                assert not named, (line.product_id, line.title, name, value)


@pytest.mark.parametrize("entry", grouped.TARGETS, ids=lambda e: e.example)
def test_every_target_has_its_grouped_products(entry, added):
    carried = [line for line in added[entry.types[0]] if _carries(entry, line)]
    # A brand's spec space can cut a line down to one SKU, so the count is of the runs.
    assert sum(len(line.children) > 1 for line in carried) >= grouped.TARGET_PRODUCTS, entry.example


def test_no_target_no_grouped_products_for_it(monkeypatch, flat):
    """Planted regression: with no SKUs to fill and without its target, the R8 hex bolt has
    no grouped product."""
    r8 = next(e for e in grouped.TARGETS if e.example.startswith("hex head cap screw"))
    monkeypatch.setattr(grouped, "TARGETS", tuple(e for e in grouped.TARGETS if e is not r8))
    monkeypatch.setattr(grouped, "SKU_SCALE", 0.0)
    before = {line.product_id for line in flat.lines}
    built = generate(replace(GeneratorConfig(), must_stock=False), types=["bolt_hex"])
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
    assert refused and all("the knob" in p for p in refused)


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
