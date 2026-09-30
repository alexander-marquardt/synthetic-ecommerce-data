"""Catalog BREADTH (alexander-marquardt/synthetic-industrial-products#34).

Light tests only, as the issue's own refinement asks: every row makes valid
SKUs, titles are unique, ``spec_quality`` is on every SKU and excluded from
both search text and facets, breadth is exempt from the realism truth tables
(``tests/test_catalog_facts.py``, ``tests/test_sku_drawings.py`` -- their own
exemptions are proven there, not re-proven here), and removing the table
removes every breadth SKU and nothing else.
"""

from __future__ import annotations

import pytest

from synthetic_industrial_products.catalog import breadth, emit
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.prism.field_map import STRUCTURAL_NAMES

#: A cheap config: the depth machinery still runs (must-stock needs it), but
#: at its smallest, so these tests spend their time on breadth, not on depth.
_CHEAP = GeneratorConfig(lines=1, new_type_share={})


@pytest.fixture(scope="module")
def catalog():
    return generate(_CHEAP)


@pytest.fixture(scope="module")
def breadth_lines(catalog):
    return [line for line in catalog.lines if line.spec_quality == "fast_and_cheap"]


def test_the_table_has_the_rows_the_issue_asks_for():
    assert len(breadth.ROWS) >= 45, "the issue asks for ~50 new categories"
    assert len({row.key for row in breadth.ROWS}) == len(breadth.ROWS), "duplicate row key"
    assert len({row.category for row in breadth.ROWS}) == len(breadth.ROWS), "dup category path"


def test_every_row_yields_valid_skus(catalog, breadth_lines):
    """Every row makes at least one line, its own SKUs, and nothing crashes
    building or emitting them (the nested and flat shapes, and every drawing)."""
    by_key = {line.type_key: line for line in breadth_lines}
    assert set(by_key) == {row.key for row in breadth.ROWS}
    for row in breadth.ROWS:
        line = by_key[row.key]
        expected = max(1, min(row.skus, len(row.size_values)))
        assert len(line.children) == expected, (row.key, len(line.children))
        for child in line.children:
            assert child.sku, row.key
            assert child.title, row.key
            assert child.price_usd > 0
            assert child.image_id == f"{row.key}/{line.product_id}/{child.sku}"

    # Every breadth SKU emits cleanly in both shapes, and its drawing is a
    # valid, text-free SVG (the same gate every other type's SKU passes).
    from synthetic_industrial_products.drawing import svg_problems

    flat = list(emit.iter_flat(catalog))
    assert sum(1 for row in flat if row["spec_quality"] == "fast_and_cheap") == sum(
        len(line.children) for line in breadth_lines
    )
    nested = list(emit.iter_nested(catalog))
    assert {row["product_id"] for row in nested if row["spec_quality"] == "fast_and_cheap"} == {
        line.product_id for line in breadth_lines
    }
    for line, child, data, _source in emit.iter_drawings(catalog):
        if line.spec_quality != "fast_and_cheap":
            continue
        assert svg_problems(data) == [], (line.type_key, child.sku)


def test_titles_are_unique(breadth_lines):
    titles = [child.title for line in breadth_lines for child in line.children]
    assert len(titles) == len(set(titles)), sorted({t for t in titles if titles.count(t) > 1})


def test_spec_quality_is_present_on_every_sku(catalog):
    flat = list(emit.iter_flat(catalog))
    assert flat, "the catalog emitted nothing"
    for row in flat:
        assert row["spec_quality"] in ("realistic", "fast_and_cheap"), row["sku"]
    nested = list(emit.iter_nested(catalog))
    assert nested
    for row in nested:
        assert row["spec_quality"] in ("realistic", "fast_and_cheap"), row["product_id"]

    breadth_flat = [row for row in flat if row["spec_quality"] == "fast_and_cheap"]
    assert breadth_flat, "no breadth SKU was found -- the exemption tests below prove nothing"
    depth_flat = [row for row in flat if row["spec_quality"] == "realistic"]
    assert depth_flat, "no depth SKU was found"


def test_spec_quality_is_a_top_level_field_not_a_nested_attribute(catalog):
    """The issue's explicit ruling: a nested attribute becomes searchable text
    and a facet on the industrial deployment, and ``spec_quality`` must be
    neither -- so it may not travel as one."""
    for line in catalog.lines:
        names = {a.name for a in line.attributes} | {
            a.name for child in line.children for a in child.attributes
        }
        assert "spec_quality" not in names, line.product_id
        assert "Spec Quality" not in names, line.product_id


def test_spec_quality_reaches_neither_search_text_nor_a_facet(catalog):
    """The maintainer's acceptance test, verbatim: a test that it appears in
    neither (2026-09-30 refinement)."""
    for row in emit.iter_flat(catalog):
        assert "spec_quality" not in row["text"], row["sku"]
        assert "fast_and_cheap" not in row["text"], row["sku"]
        assert "spec_quality" not in row["facets"], row["sku"]

    # The field map entry excludes it from both channels: no ``searchable``
    # (search text is built from an explicit allow-list in ``emit.py`` that
    # never includes it, so this is belt and braces) and ``facet: false``.
    from synthetic_industrial_products.prism.field_map import render

    field_map = render(emit.iter_flat(catalog))
    lines = field_map.splitlines()
    (index,) = (i for i, text in enumerate(lines) if text.strip() == "- name: spec_quality")
    entry = "\n".join(lines[index : index + 4])
    assert "source: spec_quality" in entry
    assert "facet: false" in entry
    assert "searchable" not in entry
    assert "spec_quality" in STRUCTURAL_NAMES, (
        "an attribute that happens to sanitise to 'spec_quality' must be namespaced, "
        "never collide with this column"
    )


def test_removing_the_table_removes_every_breadth_sku(monkeypatch):
    """The 'easy removal' property (maintainer, 2026-09-30): emptying the row
    table removes every breadth SKU and changes nothing else."""
    with_rows = generate(_CHEAP)
    depth_before = [line for line in with_rows.lines if line.spec_quality != "fast_and_cheap"]
    assert any(line.spec_quality == "fast_and_cheap" for line in with_rows.lines)

    monkeypatch.setattr(breadth, "ROWS", ())
    empty = generate(_CHEAP)
    assert not any(line.spec_quality == "fast_and_cheap" for line in empty.lines)
    assert [line.product_id for line in empty.lines] == [line.product_id for line in depth_before]
    assert [c.sku for _, c in empty.all_skus()] == [c.sku for _, c in _all_skus(depth_before)]


def _all_skus(lines):
    for line in lines:
        for child in line.children:
            yield line, child


def test_breadth_is_exempt_from_the_realism_truth_tables():
    """The exemption the maintainer asked for exists and actually filters
    something -- proven against a live catalog, not asserted in the abstract."""
    from test_catalog_facts import _realistic_only

    catalog = generate(GeneratorConfig())
    flat = list(emit.iter_flat(catalog))
    filtered = _realistic_only(flat)
    assert len(filtered) < len(flat), "the exemption filtered nothing"
    assert all(row["spec_quality"] != "fast_and_cheap" for row in filtered)
    assert any(row["spec_quality"] == "fast_and_cheap" for row in flat)


def test_every_breadth_row_publishes_material():
    """``tests/test_catalog_vocab.py``'s ``test_one_concept_is_one_name_across_types``
    requires every type but two named legacy abrasive ones to carry
    ``Material`` -- checked here at the row-table level, where a future editor
    is most likely to drop it by accident."""
    for row in breadth.ROWS:
        assert "Material" in row.attributes, row.key
