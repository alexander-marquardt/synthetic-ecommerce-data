"""The generator writes what the Combined projection used to make downstream (gen#125, slice 4).

The catalogue repo's ``combined_catalog.py`` reshaped each export before loading it. These
are the parts with one answer, now written here so the composed asset needs less of that:

- an industrial flat document states ``price`` in ``currency`` and ``in_stock`` as its nested
  variant already does (``price_usd`` and ``stock`` stay beside them for the industrial loader);
- a retail ``rating`` carries its number as ``value_canonical``, with no unit: a score is
  neither a count nor a measurement (``retail_scored``, ind#333);
- a shoe's fit width is ``fit_width``, never a bare ``width`` label beside industrial's measured
  ``width`` (``RENAMED_RETAIL_KEYS``, #286).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from synthetic_ecommerce_data.core import emit, standard

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "golden-catalog"


@pytest.fixture(scope="module")
def golden_flat() -> list[dict[str, Any]]:
    text = (GOLDEN / "flat.jsonl").read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines()]


@pytest.fixture(scope="module")
def retail_docs() -> list[dict[str, Any]]:
    from synthetic_ecommerce_data.domains.retail import export  # noqa: PLC0415

    return export.documents()


def _entries(doc: dict[str, Any]) -> list[dict[str, Any]]:
    return doc["attributes"] + [e for v in doc["variants"] for e in v["attributes"]]


def test_an_industrial_flat_document_states_price_currency_and_in_stock(golden_flat):
    assert golden_flat
    wrong = [
        d["sku"]
        for d in golden_flat
        if (d.get("price"), d.get("currency"), d.get("in_stock"))
        != (d["price_usd"], "USD", d["stock"] > 0)
    ]
    assert wrong == []
    assert any(not d["in_stock"] for d in golden_flat)


def test_the_flat_mapping_declares_price_currency_and_in_stock():
    properties = emit.FLAT_MAPPING["mappings"]["properties"]
    assert {k: properties.get(k) for k in ("price", "currency", "in_stock")} == {
        "price": {"type": "double"},
        "currency": {"type": "keyword"},
        "in_stock": {"type": "boolean"},
    }


def test_a_retail_rating_carries_its_number_and_no_unit(retail_docs):
    ratings = [e for d in retail_docs for e in _entries(d) if e["key"] == "rating"]
    assert ratings
    assert [e for e in ratings if "unit_code" in e] == []
    assert [e for e in ratings if e.get("value_canonical") != float(e["value"])] == []
    assert standard.check_catalog(retail_docs) == []


@pytest.mark.parametrize(
    ("entry", "problem"),
    [
        ({"key": "rating", "name": "Rating", "value": "4.2", "value_canonical": 4.5},
         "is not its value"),
        ({"key": "review_count", "name": "Review count", "value": "12", "value_canonical": 12.0},
         "unit_code or value_canonical alone"),
    ],
)  # fmt: skip
def test_the_standard_takes_a_unitless_number_only_on_a_score_that_equals_it(entry, problem):
    found = standard.check_entry("doc", entry)
    assert any(problem in p for p in found), found


def test_a_shoe_fit_width_is_fit_width_never_a_bare_width_label(retail_docs):
    entries = [e for d in retail_docs for e in _entries(d)]
    assert [e for e in entries if e["key"] == "width" and "unit_code" not in e] == []
    fits = {e["value"] for e in entries if e["key"] == "fit_width"}
    assert {"Standard", "Wide", "F"} <= fits
    assert {e["name"] for e in entries if e["key"] == "fit_width"} == {"Fit width"}
    axes = {a for d in retail_docs for a in d.get("variant_axes", ())}
    assert "fit_width" in axes
    assert "width" not in axes
