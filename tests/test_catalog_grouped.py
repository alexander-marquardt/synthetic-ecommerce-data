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
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.emit import line_variant_axes
from synthetic_ecommerce_data.domains.industrial import grouped, muststock, newtypes, series
from synthetic_ecommerce_data.domains.industrial.generate import Generator, generate
from synthetic_ecommerce_data.domains.industrial.product_split import (
    distribution_problems,
    skus_per_product,
    split_products,
)
from synthetic_ecommerce_data.domains.industrial.vocab import product_constant_names

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
    "hex_key": "Size",
}
#: The types whose runs had to be shaped to fit their spec space (#770).
_SPEC_BOUND = ("hex_key", "nut_hex", "tap_spiral_point")


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


#: Twice the smallest build that moves SKUs, so the flat floor leaves a small type most runs.
RUN_LINES = 2 * grouped.RUN_BUILD_LINES


@pytest.fixture(scope="module")
def flat():
    return generate(replace(GeneratorConfig(), grouped=False, pack_axis=False), types=TYPES)


@pytest.fixture(scope="module")
def full():
    return generate(replace(GeneratorConfig(), pack_axis=False), types=TYPES)


@pytest.fixture(scope="module")
def large():
    """A build that moves SKUs into runs."""
    return generate(replace(GeneratorConfig(), lines=RUN_LINES), types=TYPES)


@pytest.fixture(scope="module")
def large_flat():
    return generate(replace(GeneratorConfig(), lines=RUN_LINES, grouped=False), types=TYPES)


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
    kept = int(grouped.flat_products(RUN_LINES, len(_own(large_flat, key))) * 0.9)
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


def _value(child, name: str) -> str | None:
    return next((a.value for a in child.attributes if a.name == name), None)


def _num(child, name: str) -> float | None:
    return next((a.value_num for a in child.attributes if a.name == name), None)


def _sizes(line) -> int:
    """A line's sizes: its SKUs, or for a :data:`grouped.REACH` type its diameters (#850),
    counted by value, so a defect's respelling of one diameter is not a size of its own."""
    if line.type_key not in grouped.REACH:
        return len(line.children)
    return len({_num(child, "Milling Dia.") for child in line.children})


def _at_each_diameter(lines) -> list[list]:
    """Each (product, milling diameter) pair's SKUs: what a tile groups for a diameter query.
    A pack line's quantities of one diameter are a pair each (:mod:`.pack`)."""
    pairs: dict[tuple, list] = {}
    for line in lines:
        for child in line.children:
            dia = _value(child, "Milling Dia.")
            if dia is not None:
                key = (line.product_id, dia, _value(child, "Units per Pack"))
                pairs.setdefault(key, []).append(child)
    return list(pairs.values())


@pytest.mark.parametrize("key", _END_MILLS)
def test_a_diameter_query_groups_several_lengths_of_one_line(key, large):
    """Issue #850: ``1/2 end mill`` names the diameter a line runs on, so a line of diameters
    alone groups one SKU per tile. Most run lines sell each diameter in more than one length
    class, so most products a diameter query reaches group several SKUs, told apart by their
    length of cut."""
    pairs = _at_each_diameter(_own(large, key))
    several = [skus for skus in pairs if len(skus) >= 2]
    assert len(several) / len(pairs) > 0.5, (key, len(several), len(pairs))
    for skus in several:
        cuts = [a.value for s in skus for a in s.attributes if a.name == "Length of Cut"]
        assert len(set(cuts)) == len(cuts), (key, cuts)


#: What a shopper picks on a line that sells each diameter at several lengths (#850). A milling
#: diameter and its shank determine each other, so either one names the size. A pack line
#: (:data:`.pack.AXES`) also offers its quantities.
_REACH_AXES = {"milling_dia", "shank_dia", "length_of_cut", "overall_length", "units_per_pack"}


@pytest.mark.parametrize("key", _END_MILLS)
def test_a_line_of_several_lengths_offers_a_diameter_and_a_length(key, large):
    """Issue #850: the shank, the corner radius and the neck follow the diameter or the length
    of cut, and are stated on every SKU or on none, so a product page offers no third choice.
    A defect (:mod:`.defects`) still leaves an odd line a stray axis."""
    lines = [line for line in _own(large, key) if len(line.children) > _sizes(line)]
    assert len(lines) >= 50, (key, len(lines))
    stray = [
        axes for line in lines if not set(axes := line_variant_axes(large, line)) <= _REACH_AXES
    ]
    assert len(stray) / len(lines) < 0.1, (key, len(stray), len(lines), stray[:5])


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
    sizes = [_sizes(line) for line in added[key]]
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
    them: half the scale builds about half the run SKUs. A reach line's sizes are what the
    budget counts (#850)."""
    before = sum(_sizes(line) for line in _own(large_flat, key))
    after = sum(_sizes(line) for line in _own(large, key))
    assert 0.8 <= after / before <= 1.35, (key, before, after)
    monkeypatch.setattr(grouped, "SKU_SCALE", grouped.SKU_SCALE / 2)
    monkeypatch.setattr(grouped, "SPEC_BOUND_SCALE", grouped.SPEC_BOUND_SCALE / 2)
    config = replace(GeneratorConfig(), lines=RUN_LINES)
    halved = sum(_sizes(line) for line in generate(config, types=[key]).lines)
    assert halved < after * 0.65, (key, after, halved)


def test_the_sku_total_holds(large_flat, large):
    """Issue #766: the SKUs move into runs, and the total stays within about 10%. The end
    mills' sizes do (#850): their length classes add SKUs, by about the mean reach."""
    before = sum(_sizes(line) for line in large_flat.lines)
    after = sum(_sizes(line) for line in large.lines)
    assert 0.9 <= after / before <= 1.2, (before, after)
    assert len(large.lines) < len(large_flat.lines) / 2
    for key in grouped.REACH:
        mean = sum(c * w for c, w in grouped.REACH[key]) / sum(w for _, w in grouped.REACH[key])
        skus = sum(len(line.children) for line in _own(large, key))
        sizes = sum(_sizes(line) for line in _own(large, key))
        assert 1.5 <= skus / sizes <= mean, (key, skus, sizes)


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


def test_a_spec_bound_types_share_is_of_the_products_it_keeps():
    assert grouped.flat_products(grouped.RUN_BUILD_LINES, 12000, 4000) == 400
    assert grouped.flat_products(grouped.RUN_BUILD_LINES - 1, 12000, 4000) == 12000


@pytest.fixture(scope="module")
def spec_bound():
    """Type -> its flat lines, its lines, and the SKUs its run lines drafted and kept."""
    tally = {key: [0, 0] for key in _SPEC_BOUND}
    own_finish = Generator._finish_line

    def counting(self, type_key, draft, index):
        in_run, drafted = self.in_run, len(draft.children)
        line = own_finish(self, type_key, draft, index)
        if in_run:
            tally[type_key][0] += drafted
            tally[type_key][1] += len(line.children) if line is not None else 0
        return line

    config = replace(GeneratorConfig(), lines=RUN_LINES)
    flat_config = replace(config, grouped=False)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(Generator, "_finish_line", counting)
        return {
            key: (
                generate(flat_config, types=[key]).lines,
                generate(config, types=[key]).lines,
                tally[key],
            )
            for key in _SPEC_BOUND
        }


@pytest.mark.parametrize("key", _SPEC_BOUND)
def test_a_spec_bound_type_has_a_run_shape(key, spec_bound):
    """Issue #770: the type's products hold a run, it stays a mixture, and its SKUs move."""
    flat_lines, lines, _ = spec_bound[key]
    sizes = [len(line.children) for line in lines]
    assert sum(size >= 6 for size in sizes) / len(sizes) > 0.5, key
    assert sum(size == 1 for size in sizes) / len(sizes) >= 0.05, key
    before = sum(len(line.children) for line in flat_lines)
    assert 0.9 <= sum(sizes) / before <= 1.1, (key, before, sum(sizes))


@pytest.mark.parametrize("key", _SPEC_BOUND)
def test_a_spec_bound_run_line_keeps_its_skus(key, spec_bound):
    """Issue #770: the rejection takes at most a fifth of what the run lines draft."""
    drafted, kept = spec_bound[key][2]
    assert drafted and kept / drafted >= 0.8, (key, drafted, kept)


@pytest.mark.parametrize("key", _SPEC_BOUND)
def test_a_spec_bound_run_line_states_its_whole_line(key, spec_bound):
    """A SKU of a line missing an attribute differs only by a drop from the same SKU of every
    line with a value there, and the rejection takes it."""
    flat_lines, lines, _ = spec_bound[key]
    flat_ids = {line.product_id for line in flat_lines}
    runs = [line for line in lines if line.product_id not in flat_ids and len(line.children) >= 6]
    assert runs
    assert all({"Material", "Finish"} <= {a.name for a in line.attributes} for line in runs)


@pytest.mark.parametrize("key", ("nut_hex", "tap_spiral_point"))
def test_a_threaded_run_walks_its_table_in_order(key, spec_bound):
    """A window of a thread table never wraps from 1" back to #6, and no shuffle scatters it."""
    tables = {
        "tap_spiral_point": {
            "UNC": series.TAP_SIZES_UNC,
            "UNF": series.TAP_SIZES_UNF,
            "Metric Coarse": series.TAP_SIZES_METRIC,
        },
        "nut_hex": {"UNC": newtypes._NUT_UNC, "Metric Coarse": newtypes._NUT_METRIC},
    }[key]
    flat_lines, lines, _ = spec_bound[key]
    flat_ids = {line.product_id for line in flat_lines}
    runs = [line for line in lines if line.product_id not in flat_ids and len(line.children) >= 6]
    assert runs
    for line in runs:
        kind = next(a.value for a in line.attributes if a.name == "Thread Type")
        order = [row[0] for row in tables[kind]]
        places = [
            order.index(a.value)
            for child in line.children
            for a in child.attributes
            if a.name == "Thread Size" and a.value in order
        ]
        assert places == sorted(places), line.product_id


def test_a_run_line_of_too_few_sizes_stays_flat():
    """Issue #770: a fine thread's table holds five sizes, so a line off it is no run."""
    assert not grouped.keeps_run("nut_hex", 5, 5)
    assert grouped.keeps_run("nut_hex", 6, 6)


def test_a_run_line_that_would_lose_its_skus_is_redrawn():
    assert not grouped.keeps_run("hex_key", 7, 10)
    assert grouped.keeps_run("hex_key", 8, 10)


def test_a_bearing_line_is_no_run():
    """Issue #770: a bearing number is the product and its closures its SKUs, three at most,
    so bearings stay on the knob. A run of numbers needs the number to be a SKU value."""
    assert "bearing_radial_ball" not in grouped.VARIANTS
    assert len(newtypes._CLOSURES) < min(count for count, _ in grouped.RUN)
    assert "Bearing Number" in product_constant_names("bearing_radial_ball")


def test_a_type_with_no_table_builds_flat_alone():
    """A type outside the table keeps every product: the pass moves nothing there."""
    key = "bearing_radial_ball"
    plain = generate(GeneratorConfig(), types=[key]).lines
    assert plain == generate(replace(GeneratorConfig(), grouped=False), types=[key]).lines


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
    refused = distribution_problems(
        distribution, replace(GeneratorConfig(), grouped=False, pack_axis=False)
    )
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
