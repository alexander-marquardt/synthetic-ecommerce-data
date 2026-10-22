"""The industrial attribute clean-up of #497: one key per concept, no key that
repeats the product type, and no value of the wrong kind.

Read from the committed ``golden-catalog/nested.jsonl``, which
``tests/test_catalog_golden.py`` holds equal to a fresh default build, so this
guard sees every industrial type and needs no build of its own.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core.config import GeneratorConfig

GOLDEN = Path(__file__).resolve().parent.parent / "golden-catalog" / "nested.jsonl"


def _products() -> list[dict]:
    return [json.loads(line) for line in GOLDEN.read_text("utf-8").splitlines()]


def _entries(product: dict):
    yield from product["attributes"]
    for variant in product["variants"]:
        yield from variant["attributes"]


@pytest.fixture(scope="module")
def products() -> list[dict]:
    return _products()


@pytest.fixture(scope="module")
def keys(products) -> set[str]:
    return {entry["key"] for product in products for entry in _entries(product)}


def test_a_measurement_system_is_one_attribute_with_one_vocabulary(products):
    values = {
        entry["value"]
        for product in products
        for entry in _entries(product)
        if entry["key"] == "measurement_system"
    }
    assert values == {"Fractional Inch", "Metric", "Inch", "Decimal Inch"}


def test_a_type_value_never_restates_the_product_type(products):
    restated = {
        (product["product_type_label"], entry["value"])
        for product in products
        for entry in _entries(product)
        if entry["key"] == "type"
        and entry["value"].lower() == product["product_type_label"].lower()
    }
    named = {
        entry["value"]
        for product in products
        for entry in _entries(product)
        if entry["key"] == "type"
        and entry["value"] in {"Socket Head Cap Screw", "Set Screw", "Socket Flat Head Cap Screw"}
    }
    assert restated == set()
    assert named == set()


def test_a_standard_is_published_once_per_product(products):
    """One value is never listed twice by the build's merge of ``Meets/Exceeds`` into
    ``Standards`` (#497). The one exception is the stated defect of #1: at its rate a parent
    publishes one ``Standards`` value a second time, a single extra copy."""
    extra = {
        product["product_id"]: len(values) - len(set(values))
        for product in products
        for values in [[e["value"] for e in product["attributes"] if e["key"] == "standards"]]
    }
    assert [pid for pid, copies in extra.items() if copies > 1] == []
    repeating = sum(1 for copies in extra.values() if copies)
    assert repeating <= 3 * GeneratorConfig().defect_repeated_pair * len(products)


def test_grade_and_wheel_grade_are_two_kinds(products):
    kinds = defaultdict(set)
    for product in products:
        for entry in _entries(product):
            if entry["key"] in {"grade", "wheel_grade"}:
                kinds[entry["key"]].add(entry["value"])
    assert kinds["wheel_grade"] == {"Fine", "Medium", "Coarse"}
    assert kinds["grade"].isdisjoint(kinds["wheel_grade"])
    assert kinds["grade"]


def test_key_stock_tolerance_class_is_stock_fit_not_fit(keys, products):
    assert "fit" not in keys
    stock = {
        entry["value"]
        for product in products
        for entry in _entries(product)
        if entry["key"] == "stock_fit"
    }
    assert stock == {"Oversized", "Undersized"}


def test_an_angle_holds_no_length(products):
    bad = {
        entry["value"]
        for product in products
        for entry in _entries(product)
        if entry["key"] in {"helix_angle", "point_angle"} and not entry["value"].isdigit()
    }
    assert bad == set()


def test_an_arbor_hole_has_one_spelling(products):
    values = {
        entry["value"]
        for product in products
        for entry in _entries(product)
        if entry["key"] == "arbor_hole"
    }
    assert "0.875" not in values
    assert "7/8" in values


def test_a_head_type_has_one_spelling_for_flat(products):
    values = {
        entry["value"]
        for product in products
        for entry in _entries(product)
        if entry["key"] == "head_type"
    }
    assert "Countersunk Head" not in values
    assert "Flat" in values
