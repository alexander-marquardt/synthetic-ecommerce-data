"""A derived range name carries no number, and a color is a SKU, not a product (#851).

The line grammar named a derived cup set "Supper 6" and its next one "Supper 9": a lead word and a
generation number, which no retailer puts on a cup set. And a style its template already shows
in every title-shown value differed from it by its hero color alone, so it was a product of one
SKU titled with that color ("Brackenmere Home Supper 9 Set of 4 Porcelain Espresso Cups in Gift
Box, Green"), beside the brand's own grouped product. A derived model of a non-care family is now
its lead word alone, and such a style carries the template's colors as its SKUs, so a brand sells
one of it. The cleaning and beauty models keep their numbers until the grocery build drops them
too (the issue's Remaining line).
"""

from __future__ import annotations

import collections
import re

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import line_grammar, scale, scale_measures

#: A bare number, or a number after a modifier ("Plus 2", "Mini 8"), as a word of a range name.
BARE_NUMBER = re.compile(r"\b\d+\b")


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def _derived(ceiling) -> list[dict]:
    return [r for r in ceiling.records if r["product_id"] in ceiling.template_of]


def test_a_derived_range_name_has_no_bare_number(ceiling):
    """Guard (#851): "Supper 6" and "Spread Mini 8" read as synthetic. Metric: derived styles
    outside the care families whose range name has a word that is a number."""
    numbered = [
        (r["product_type"], scale._line(r))
        for r in _derived(ceiling)
        if line_grammar.family(r) not in line_grammar.CARE
        and BARE_NUMBER.search(scale._line(r) or "")
    ]
    assert numbered == [], f"{len(numbered)}: {sorted(set(numbered))[:10]}"


def test_a_grammar_model_outside_care_is_its_lead_word():
    """Guard (#851): every slot a brand of a non-care, non-food family deals is one of its lead
    words, so no number or sub-model word ("Mini", "Plus") follows it. Metric: off-list models."""
    for fam in line_grammar.NUMBERED:
        deal = line_grammar.Deal(fam, ["Brand A", "Brand B"], {})
        if fam in line_grammar.CARE or deal.spec.bare:
            continue
        for brand in deal.brands:
            models = {deal.owned(brand, slot) for slot in range(scale.RANGE_SLOTS)}
            assert models <= set(deal.of(brand)), (fam, sorted(models - set(deal.of(brand))))


@pytest.mark.parametrize("kind", ["Cup Set", "Travel Cup"])
def test_a_brand_sells_one_of_each_cup_with_its_colors_as_skus(ceiling, kind):
    """Guard (#851): the ceiling's cup sets were seven products, six of them one color each,
    three from one brand. Metric: products per brand of the kind, and one-SKU products."""
    cups = [r for r in ceiling.records if r["product_type"] == kind]
    per_brand = collections.Counter(r["brand"] for r in cups)
    assert len(per_brand) > 1, per_brand
    assert max(per_brand.values()) == 1, per_brand
    assert [r["title"] for r in cups if r["sku_count"] < 2] == []


def test_no_derived_title_names_a_color_it_alone_carries(ceiling):
    """Guard (#851): ", Green" at the end of a one-color style's title was how a color became
    a product. Metric: derived styles of one color, from a template of several, whose title
    ends with that color."""
    tpls = {r["product_id"]: r for r in ceiling.records}
    named = [
        r["title"]
        for r in _derived(ceiling)
        if len(r.get("color_options", ())) == 1
        and len(tpls[ceiling.template_of[r["product_id"]]].get("color_options", ())) > 1
        and r["title"].endswith(line_grammar.color_suffix(r, r["color_options"][0]["color"]))
    ]
    assert named == [], f"{len(named)}: {named[:5]}"


def test_the_report_names_the_kinds_most_of_whose_products_have_one_sku(ceiling):
    """Guard (#851): the issue asks for every kind where most products have one SKU although a
    color or size axis exists. Metric: the cups among them."""
    single = scale_measures.single_sku_kinds(ceiling.records)
    assert all(row["single"] * 2 > row["products"] for row in single.values())
    assert {"Cup Set", "Travel Cup"}.isdisjoint(single)
