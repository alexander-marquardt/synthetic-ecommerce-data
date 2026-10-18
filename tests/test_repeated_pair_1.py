"""Some parents publish the same (name, value) pair twice, at a stated rate (#1).

The `reverse_nested` over-count needs a repeated PAIR on one parent, not a
repeated name: ``Standards = [ISO, DIN]`` gives every bucket the right count
with or without `reverse_nested`, ``Standards = [ISO, ISO]`` over-reports ISO.
A catalog whose multi-valued attribute never repeats a value passes that check
while the defect it targets is absent, so the rate is generated, recorded
beside the other measured rates in ``stats.json`` and pinned here.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.emit import nested_document
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.measure import measure
from synthetic_ecommerce_data.domains.industrial.vocab import STANDARDS_NAME

ROW = "parent repeats a (name, value) pair"
GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"


def _repeated(entries: list[dict]) -> list[tuple[str, str]]:
    """The (name, value) pairs a parent's entries publish more than once."""
    counts = Counter((e["name"], e["value"]) for e in entries)
    return sorted(pair for pair, n in counts.items() if n > 1)


def _config(defect_scale: float) -> GeneratorConfig:
    return GeneratorConfig(lines=600, seed=99, defect_scale=defect_scale)


@pytest.fixture(scope="module")
def dialled_up():
    """Rate x 10, so a 600-line build holds enough repeats to assert on."""
    config = _config(10.0)
    catalog = generate(config)
    return catalog, measure(catalog, config)


def test_the_rate_is_a_stated_config_value():
    rate = GeneratorConfig().defect_repeated_pair
    assert 0.0 < rate < 0.05, rate


def test_some_parents_repeat_a_pair_and_it_is_the_multivalued_attribute(dialled_up):
    catalog, _ = dialled_up
    repeating = {}
    for line in catalog.lines:
        pairs = _repeated(nested_document(catalog, line)["attributes"])
        if pairs:
            repeating[line.product_id] = pairs
    assert repeating, "no parent publishes the same (name, value) twice"
    assert {name for pairs in repeating.values() for name, _ in pairs} == {STANDARDS_NAME}


def test_the_multivalued_attribute_stays_with_distinct_values(dialled_up):
    """A repeat is not what makes Standards multi-valued: distinct values stay."""
    catalog, stats = dialled_up
    distinct = sum(
        1
        for line in catalog.lines
        for a in line.attributes
        if a.name == STANDARDS_NAME and len(set(a.values or (a.value,))) > 1
    )
    assert distinct > 0
    assert stats["standards_multivalued"] > 0
    assert stats["multivalued_attribute_names"].get(STANDARDS_NAME, 0) > 0


def test_a_repeated_value_is_not_counted_as_a_second_value(dialled_up):
    """``[ISO, ISO]`` is one value published twice: not multi-valued in the report."""
    catalog, stats = dialled_up
    distinct = repeat_only = 0
    for line, child in catalog.all_skus():
        for a in catalog.merged_attributes(line, child):
            if a.name != STANDARDS_NAME:
                continue
            values = a.values or (a.value,)
            distinct += len(set(values)) > 1
            repeat_only += len(set(values)) == 1 and len(values) > 1
    assert repeat_only > 0, "no parent repeats a value of a one-value Standards"
    assert stats["standards_multivalued"] == distinct


def test_the_report_row_counts_what_the_documents_publish(dialled_up):
    catalog, stats = dialled_up
    row = next(c for c in stats["comparisons"] if c.name == ROW)
    published = sum(
        1 for line in catalog.lines if _repeated(nested_document(catalog, line)["attributes"])
    )
    carrying = sum(
        1 for line in catalog.lines if any(a.name == STANDARDS_NAME for a in line.attributes)
    )
    assert row.numerator == published > 0
    assert row.denominator == carrying
    assert row.target == GeneratorConfig().defect_repeated_pair


def test_defects_at_zero_publish_no_repeated_pair():
    """The control: ``--defects 0`` is a catalog with no contradictions at all."""
    config = _config(0.0)
    catalog = generate(config)
    row = next(c for c in measure(catalog, config)["comparisons"] if c.name == ROW)
    assert row.denominator > 0, "no parent carries Standards, so a zero proves nothing"
    assert row.numerator == 0
    assert not any(
        _repeated(nested_document(catalog, line)["attributes"]) for line in catalog.lines
    )


def test_the_committed_catalog_carries_the_rate_in_stats_json():
    """Removing the repeat from the generator turns this red after a rebuild."""
    stats = json.loads((GOLDEN / "stats.json").read_text(encoding="utf-8"))
    row = next((c for c in stats["comparisons"] if c["name"] == ROW), None)
    assert row is not None, f"stats.json has no {ROW!r} row"
    parents = [
        json.loads(text) for text in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines()
    ]
    repeating = sum(1 for p in parents if _repeated(p["attributes"]))
    carrying = sum(1 for p in parents if any(e["name"] == STANDARDS_NAME for e in p["attributes"]))
    assert row["numerator"] == repeating
    assert row["denominator"] == carrying
    assert row["target"] == GeneratorConfig().defect_repeated_pair
    assert 0.003 <= row["achieved"] <= 0.02, row
