"""Every SKU of a product agrees on the product's own attributes (gen#63).

A product is what search results group by; its SKUs are the sizes. Each type declares which
attributes are product-constant (``vocab.product_constant_names``: its ``line``-scope
vocabulary and the measurement system) and which are variant (``vocab.variant_names``).
The gate runs over the DEFAULT build and is shown to red on a planted mixed metric and inch
product, so a gate that stopped looking would fail here too.
"""

from __future__ import annotations

import dataclasses

import pytest

from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.model import Catalog, ProductLine, keyword_attribute
from synthetic_ecommerce_data.domains.industrial.generate import all_type_keys, generate
from synthetic_ecommerce_data.domains.industrial.product_split import (
    disagreements,
    distribution_problems,
    skus_per_product,
    split_products,
)
from synthetic_ecommerce_data.domains.industrial.vocab import (
    MEASUREMENT_SYSTEM_SPELLINGS,
    product_constant_names,
    variant_names,
)


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return generate()


def _with_children(catalog: Catalog, line: ProductLine, children) -> Catalog:
    planted = dataclasses.replace(line, children=tuple(children))
    return Catalog(lines=tuple(planted if x is line else x for x in catalog.lines))


def _system_name(line: ProductLine) -> str | None:
    for child in line.children:
        for a in child.attributes:
            if a.name in MEASUREMENT_SYSTEM_SPELLINGS:
                return a.name
    return None


def _stated_two_skus(catalog: Catalog) -> ProductLine:
    """A product of two or more SKUs that states its measurement system on every SKU."""
    for line in catalog.lines:
        name = _system_name(line)
        if len(line.children) >= 2 and name:
            return line
    raise AssertionError("the default build has no multi-SKU product stating a system")


def test_the_default_build_has_no_product_whose_skus_disagree(catalog: Catalog) -> None:
    split = split_products(catalog)
    assert not split, (
        f"{len(split)} product(s) mix a product-constant attribute: {dict(list(split.items())[:5])}"
    )


def test_a_planted_mixed_metric_and_inch_product_reds(catalog: Catalog) -> None:
    line = _stated_two_skus(catalog)
    name = _system_name(line)
    assert name is not None
    first, *rest = line.children
    other = "Metric" if "Metric" not in {a.value for a in first.attributes} else "Fractional Inch"
    mixed = dataclasses.replace(
        first,
        attributes=tuple(
            keyword_attribute(name, other) if a.name == name else a for a in first.attributes
        ),
    )
    planted = _with_children(catalog, line, [mixed, *rest])
    assert disagreements(line, catalog) == []
    assert name in split_products(planted).get(line.product_id, [])


def test_a_sibling_that_drops_a_product_constant_attribute_reds(catalog: Catalog) -> None:
    line = _stated_two_skus(catalog)
    name = _system_name(line)
    first, *rest = line.children
    bare = dataclasses.replace(
        first, attributes=tuple(a for a in first.attributes if a.name != name)
    )
    planted = _with_children(catalog, line, [bare, *rest])
    assert name in split_products(planted).get(line.product_id, [])


def test_a_product_constant_on_the_line_cannot_vary(catalog: Catalog) -> None:
    """Wheel Grade (#497 renamed the wheel's Grade) is the product's: a wheel product holds one."""
    wheels = [x for x in catalog.lines if x.type_key == "wheel_depressed_center"]
    assert wheels
    assert "Wheel Grade" in product_constant_names("wheel_depressed_center")
    assert "Wheel Grade" not in variant_names("wheel_depressed_center")
    assert all(not disagreements(w, catalog) for w in wheels)


@pytest.mark.parametrize("type_key", all_type_keys())
def test_every_type_declares_a_disjoint_split(type_key: str) -> None:
    assert not product_constant_names(type_key) & variant_names(type_key)
    assert product_constant_names(type_key) >= MEASUREMENT_SYSTEM_SPELLINGS


def test_the_skus_per_product_follow_the_knob(catalog: Catalog) -> None:
    config = GeneratorConfig()
    distribution = skus_per_product(catalog)
    assert distribution_problems(distribution, config) == []
    assert max(row["max"] for row in distribution.values()) <= 5
    assert all(sum(row["histogram"].values()) == row["products"] for row in distribution.values())


def test_a_type_that_leaves_the_knob_reds() -> None:
    config = GeneratorConfig()
    too_many = {"nut_hex": {"products": 100, "median": 1, "max": 6, "histogram": {6: 100}}}
    assert distribution_problems(too_many, config)
    too_fat = {"nut_hex": {"products": 100, "median": 4, "max": 5, "histogram": {4: 100}}}
    assert distribution_problems(too_fat, config)
    one_row = {"threaded_rod": {"products": 1, "median": 3, "max": 3, "histogram": {3: 1}}}
    assert distribution_problems(one_row, config) == []
