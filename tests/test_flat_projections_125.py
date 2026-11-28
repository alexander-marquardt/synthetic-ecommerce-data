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
import re
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


# The 2026-11-20 ruling on #125 ("The generator should write the final shape"): (1) a retail size
# is written under its size system's key, and a lone ``size_uk`` passes the standard; (2) every
# industrial flat file writes ``product_type`` as the category leaf, the key kept in ``image_id``.


#: The bare ``size`` shapes the ceiling build writes (52,048 entries on main ``da8b44e4``), one
#: each, and the entry each becomes: elastic/prism-retail-and-industrial's ``retail_size_key``,
#: a length under gen#227's ``item_height`` / ``item_width``.
def _size(key: str, name: str, value: str) -> dict[str, Any]:
    return {"key": key, "name": name, "value": value}


def _cm(key: str, name: str, cm: str) -> dict[str, Any]:
    return _size(key, name, cm) | {"unit_code": "CMT", "value_canonical": float(cm) * 10}


SQUARE = {"item_width": "70", "item_length": "70", "shape": "Square"}
ROUND = {"item_width": "90", "item_height": "90", "shape": "Round"}
SIZE_ROWS = [
    ("M", "Womens", {}, _size("size_letter", "Size (letter)", "M")),
    ("Large", "Pets", {}, _size("size_letter", "Size (letter)", "Large")),
    ("L/XL", "Mens", {}, _size("size_letter", "Size (letter)", "L/XL")),
    ("3-4 Yrs", "Kids", {}, _size("size_age", "Size (age)", "3-4 Yrs")),
    ("0-3 Mths", "Kids", {}, _size("size_age", "Size (age)", "0-3 Mths")),
    ("Newborn", "Kids", {}, _size("size_age", "Size (age)", "Newborn")),
    ("12", "Womens", {}, _size("size_uk", "Size (UK)", "12")),
    ("32B", "Womens", {}, _size("size_uk", "Size (UK)", "32B")),
    ("Bath Sheet", "Home", {}, _size("size_towel", "Size (towel)", "Bath Sheet")),
    ("5 x 7 in", "Gifts", {}, _size("dimensions", "Dimensions", "5 x 7 in")),
    ("45 x 45cm", "Home", {}, _size("dimensions", "Dimensions", "45 x 45cm")),
    ("6 x 25g", "Food & drink", {}, _size("pack_size", "Pack size", "6 x 25g")),
    ("1kg", "Food & drink", {}, _size("pack_size", "Pack size", "1kg")),
    # A build row's department is cased as the row writes it, before letter case runs.
    ("150g", "Food & Drink", {}, _size("pack_size", "Pack size", "150g")),
    ("0.5 L", "Home", {}, _size("capacity_volume", "Capacity (volume)", "0.5 L")),
    ("60 cm", "Garden", {}, _cm("item_height", "Item height", "60")),
    ("1.2 m", "Garden", {}, _cm("item_height", "Item height", "120")),
    ("70 cm", "Home", SQUARE, _cm("item_width", "Item width", "70")),
    ("90 cm", "Home", ROUND, _cm("diameter", "Diameter", "90")),
]


def _id(*words: str) -> str:
    """A test id of plain words: a value's ``/``, ``&`` and blanks become ``_``."""
    return re.sub(r"[^A-Za-z0-9.]+", "_", "-".join(words))


@pytest.mark.parametrize(
    ("value", "department", "siblings", "entry"),
    SIZE_ROWS,
    ids=[_id(value, department) for value, department, _, _ in SIZE_ROWS],
)
def test_each_retail_size_shape_takes_its_size_system_key(value, department, siblings, entry):
    from synthetic_ecommerce_data.domains.retail import size_systems  # noqa: PLC0415

    assert size_systems.entry(value, department, siblings) == entry


@pytest.mark.parametrize(
    ("value", "department"),
    [
        ("S/XL", "Womens"),
        ("30 cm", "Home"),
        ("30 cm", "Womens"),
        ("250g", "Home"),
        ("Huge", "Pets"),
    ],
    ids=_id,
)
def test_a_size_no_row_names_is_refused_never_guessed(value, department):
    from synthetic_ecommerce_data.domains.retail import size_systems  # noqa: PLC0415

    with pytest.raises(ValueError, match="add its"):
        size_systems.entry(value, department, {})


def test_no_retail_document_writes_a_bare_size(retail_docs):
    entries = [e for d in retail_docs for e in _entries(d)]
    assert [e["value"] for e in entries if e["key"] == "size"] == []
    keys = {e["key"] for e in entries}
    assert {"size_letter", "size_age", "size_uk"} <= keys
    axes = {a for d in retail_docs for a in d.get("variant_axes", ())}
    assert "size" not in axes
    assert "size_letter" in axes
    assert standard.check_catalog(retail_docs) == []


def test_the_ceiling_build_writes_no_bare_size_and_passes_the_standard():
    from retail_ceiling import ceiling_build  # noqa: PLC0415
    from synthetic_ecommerce_data.domains.retail import export, scale  # noqa: PLC0415

    def sized(rec):
        return "size" in rec.get("size_options", {}) or any("size" in s for s in rec["skus"])

    docs = [export.standard_document(r) for r in ceiling_build().records if sized(r)]
    assert len(docs) > 1000
    entries = [e for d in docs for e in _entries(d)]
    assert [e["value"] for e in entries if e["key"] == "size"] == []
    flat = [row for d in docs for row in standard.flat_documents(d, export.NUMERIC_FACTS)]
    assert [r["sku"] for r in flat if "size" in r["facets"]] == []
    assert standard.check_catalog(docs, one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT) == []


@pytest.mark.parametrize(
    ("attributes", "found"),
    [
        ([{"key": "size_uk", "value": "12"}], None),
        ([{"key": "size_uk", "value": "32B"}], None),
        ([{"key": "size_eu", "value": "40"}], "without size_uk, size_us"),
        ([{"key": "size_uk", "value": "12"}, {"key": "size_us", "value": "8"}], "without size_eu"),
        ([{"key": "size_uk", "value": "12"}, {"key": "size_eu", "value": "40"},
          {"key": "size_us", "value": "9"}], "is no row of a core size chart"),
    ],
)  # fmt: skip
def test_a_lone_size_uk_passes_and_a_partial_or_unknown_triple_is_refused(attributes, found):
    from synthetic_ecommerce_data.core import size_charts  # noqa: PLC0415

    problems = size_charts.problems("v", attributes)
    if found is None:
        assert problems == []
    else:
        assert len(problems) == 1 and found in problems[0], problems


def test_an_industrial_flat_product_type_is_its_category_leaf_and_the_key_stays_in_image_id(
    golden_flat,
):
    wrong = [d["sku"] for d in golden_flat if d["product_type"] != d["category_path"][-1]]
    assert wrong == []
    nested = [json.loads(line) for line in (GOLDEN / "nested.jsonl").open(encoding="utf-8")]
    key_of = {v["sku"]: d["product_type"] for d in nested for v in d["variants"]}
    moved = [d["sku"] for d in golden_flat if d["image_id"].split("/")[0] != key_of[d["sku"]]]
    assert moved == []
    hammers = {key_of[d["sku"]] for d in golden_flat if d["product_type"] == "Hammers"}
    assert len(hammers) > 1, "one leaf holds several type keys"
