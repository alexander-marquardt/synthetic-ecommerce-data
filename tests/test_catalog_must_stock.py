"""Every requirement example has a product to find (maintainer ruling, #103, 2026-09-28).

The inventory "must stock" a SKU for each requirement example the search
scorecard runs. These tests hold that on the COMMITTED catalog, prove it is the
must-stock pass that stocks the ones the random catalog misses, and prove the
pass moves nothing the main generation drew.
"""

from __future__ import annotations

import functools
import json
from dataclasses import replace
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog import bundle, muststock
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"


def _unstocked(catalog, entries) -> list[str]:
    records = [
        (line.type_key, {a.name: a.value for a in (*line.attributes, *child.attributes)})
        for line in catalog.lines
        for child in line.children
    ]
    return [e.example for e in entries if not any(e.matches(t, r) for t, r in records)]


@pytest.fixture(scope="module")
def full():
    return generate(GeneratorConfig())


@functools.cache
def _golden_records() -> tuple[tuple[str, dict[str, str]], ...]:
    # The published spelling comes from flat.jsonl, joined on sku: a nested
    # entry carries no spelling (#42).
    facets_by_sku = bundle.flat_facets(GOLDEN)
    out = []
    for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines():
        parent = json.loads(line)
        out.extend((parent["product_type"], r) for r in bundle.records(parent, facets_by_sku))
    return tuple(out)


@pytest.mark.parametrize("entry", muststock.MUST_STOCK, ids=lambda e: e.example)
def test_every_requirement_example_is_stocked_in_the_committed_catalog(entry):
    assert any(entry.matches(t, r) for t, r in _golden_records()), entry.example


def test_one_entry_per_requirement_example_and_none_twice():
    examples = [e.example for e in muststock.MUST_STOCK]
    assert len(examples) == len(set(examples)) == 24


def test_the_pass_is_what_stocks_the_examples_the_random_catalog_misses(full):
    """Without the pass, five examples have no product; with it, none are missing."""
    without = generate(replace(GeneratorConfig(), must_stock=False))
    missing = _unstocked(without, muststock.MUST_STOCK)
    assert (
        'hex head cap screw: 7/16-14, 1-3/4" length under head, grade 8 steel, zinc finish'
        in missing
    )
    assert _unstocked(full, muststock.MUST_STOCK) == []


def test_removing_an_entry_unstocks_its_example(monkeypatch):
    """Planted regression: drop the R8 entry and its product is gone again."""
    r8 = next(e for e in muststock.MUST_STOCK if e.example.startswith("hex head cap screw"))
    monkeypatch.setattr(
        "synthetic_industrial_products.catalog.generate.MUST_STOCK",
        tuple(e for e in muststock.MUST_STOCK if e is not r8),
    )
    assert _unstocked(generate(GeneratorConfig()), [r8]) == [r8.example]


def test_the_pass_moves_nothing_the_main_generation_drew(full):
    """Every line before the must-stock lines is byte-for-byte the unpinned generation's."""
    without = generate(replace(GeneratorConfig(), must_stock=False))
    assert full.lines[: len(without.lines)] == without.lines
    added = full.lines[len(without.lines) :]
    assert len(added) == full.stats["must_stock_lines"] == 5
    # The added lines obey the same 1-5 variant rule as every other line.
    assert all(1 <= len(line.children) <= 5 for line in added)


def test_the_pass_is_deterministic(full):
    assert generate(GeneratorConfig()).lines == full.lines


def test_an_entry_no_builder_can_reach_is_refused_loudly(monkeypatch):
    impossible = muststock.MustStock(
        "an end mill no series offers", ("end_mill_square",), {"Milling Dia.": "999mm"}
    )
    monkeypatch.setattr("synthetic_industrial_products.catalog.generate.MUST_STOCK", (impossible,))
    monkeypatch.setattr("synthetic_industrial_products.catalog.generate.MAX_ATTEMPTS", 50)
    with pytest.raises(muststock.MustStockUnmetError, match="999mm"):
        generate(GeneratorConfig())
