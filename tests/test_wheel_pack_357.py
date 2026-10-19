"""Depressed-center wheels publish no pack (#357, split from #65).

The census sells 98.6% of its wheels each (``pack_vs_each`` of
``wheel_depressed_center``: 3 pack-sold rows of 217, at 20 and 40), and the
wheel's price model carries no pack term, so a published ``Units per Pack`` of
10 or 25 named a quantity the shown price was not for.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import price
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import price_report
from synthetic_ecommerce_data.domains.industrial.generate import Generator, generate
from synthetic_ecommerce_data.domains.industrial.vocab import VOCAB

WHEEL = "wheel_depressed_center"

CENSUS_FILE = (
    Path(__file__).resolve().parent.parent / "reference-statistics" / "P2_price_census.json"
)


@pytest.fixture(scope="module")
def wheel_skus():
    """Every wheel SKU of the default build, with its merged attributes."""
    catalog = generate(GeneratorConfig())
    type_of = price_report.collect(catalog).type_of
    out = []
    for line, child in catalog.all_skus():
        if type_of.get(child.sku) == WHEEL:
            facts = {a.name: a for a in catalog.merged_attributes(line, child)}
            out.append((child, facts))
    return out


def test_the_census_sells_the_wheel_each():
    pack = json.loads(CENSUS_FILE.read_text())["deep_types"][WHEEL]["pack_vs_each"]
    assert pack["sale_unit_share"]["each"] == 0.986


def test_the_wheel_price_model_has_no_pack_term():
    model = price.model_for(WHEEL)
    assert model.pack_attribute is None
    assert WHEEL not in price.PACK_COUNTS


def test_the_wheel_vocabulary_has_no_pack_row():
    assert "Units per Pack" not in {spec.name for spec in VOCAB[WHEEL]}


def test_no_wheel_publishes_a_pack(wheel_skus):
    assert len(wheel_skus) > 100
    assert [c.sku for c, facts in wheel_skus if "Units per Pack" in facts] == []


def test_every_wheel_is_priced_each(wheel_skus):
    assert {c.pricing_unit for c, _ in wheel_skus} == {"Each"}


def test_no_two_wheels_of_a_brand_publish_the_same_spec(wheel_skus):
    """With the pack gone, two wheels that differed only by it are one product: the
    generator makes the first and not the second, so none reaches the catalog."""
    seen: dict[tuple, str] = {}
    twins = []
    for sku, facts in wheel_skus:
        spec = (
            sku.title.split(",")[0],
            tuple(
                sorted(
                    (name, a.value)
                    for name, a in facts.items()
                    if name not in Generator.NOT_SUBSTANCE
                )
            ),
        )
        if spec in seen:
            twins.append((seen[spec], sku.sku))
        seen[spec] = sku.sku
    assert twins == []
