"""A derived range name carries no number, and a color is a SKU, not a product (#851).

The line grammar named a derived cup set "Supper 6" and its next one "Supper 9": a lead word and a
generation number, which no retailer puts on a cup set. And a style its template already shows
in every title-shown value differed from it by its hero color alone, so it was a product of one
SKU titled with that color ("Brackenmere Home Supper 9 Set of 4 Porcelain Espresso Cups in Gift
Box, Green"), beside the brand's own grouped product. A derived model is now its lead word alone,
and such a style carries the template's colors as its SKUs, so a brand sells one of it. A cleaning
or beauty model followed ("Keen Plus 4", "Total Plus 9"), and a beauty shade is a SKU of its
line too: a line is split by its finish or formula, never by its shade.
"""

from __future__ import annotations

import collections
import re

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    barry_plotter,
    line_grammar,
    scale,
    scale_measures,
)

#: A bare number, or a number after a modifier ("Plus 2", "Mini 8"), as a word of a range name.
BARE_NUMBER = re.compile(r"\b\d+\b")


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def _derived(ceiling) -> list[dict]:
    return [r for r in ceiling.records if r["product_id"] in ceiling.template_of]


def test_a_derived_range_name_has_no_bare_number(ceiling):
    """Guard (#851): "Supper 6", "Spread Mini 8" and "Keen Plus 4" read as synthetic. Metric:
    derived styles whose range name has a word that is a number."""
    numbered = [
        (r["product_type"], scale._line(r))
        for r in _derived(ceiling)
        if BARE_NUMBER.search(scale._line(r) or "")
    ]
    assert numbered == [], f"{len(numbered)}: {sorted(set(numbered))[:10]}"


def test_a_grammar_model_is_its_lead_word():
    """Guard (#851): every slot a brand of a non-food family deals in the scale build is one of its
    lead words, so no number or sub-model word ("Mini", "Plus") follows it. Metric: off-list
    models."""
    for fam in line_grammar.NUMBERED:
        deal = line_grammar.Deal(fam, ["Brand A", "Brand B"], {})
        if deal.spec.bare:
            continue
        for brand in deal.brands:
            models = {deal.owned(brand, slot) for slot in range(scale.RANGE_SLOTS)}
            assert models <= set(deal.of(brand)), (fam, sorted(models - set(deal.of(brand))))


def test_no_dealt_range_word_is_a_word_of_any_template_text():
    """Guard (#851): with no number after it, a range word that a description or title also
    says ("for toast, cake or a starter", "Bright Orange Crew Neck Tee") reads as that text's
    range, which ``check_catalog`` and ``review_range_names`` refuse. Metric: the words dealt to
    a brand that some template's text uses."""
    tpls = scale.templates()
    taken = line_grammar.text_words(tpls)
    deals = line_grammar.deals(tpls, scale.brand_pools(scale.derivable(tpls)))
    clash = sorted(
        (fam, w)
        for fam, deal in deals.items()
        if deal.spec and not deal.spec.bare
        for b in deal.brands
        for w in deal.of(b)
        if w.lower() in taken
    )
    assert clash == []


@pytest.mark.parametrize("kind", ["Cup Set", "Travel Cup"])
def test_a_brand_sells_one_of_each_cup_with_its_colors_as_skus(ceiling, kind):
    """Guard (#851): the ceiling's cup sets were seven products, six of them one color each,
    three from one brand. Metric: products per brand of the kind, and one-SKU products."""
    cups = [r for r in ceiling.records if r["product_type"] == kind]
    cups = [r for r in cups if r["product_id"] not in barry_plotter.ids()]  # gen#925
    per_brand = collections.Counter(r["brand"] for r in cups)
    assert len(per_brand) > 1, per_brand
    assert max(per_brand.values()) == 1, per_brand
    assert [r["title"] for r in cups if r["sku_count"] < 2] == []


def test_no_derived_title_names_a_color_it_alone_carries(ceiling):
    """Guard (#851): ", Green" at the end of a one-color style's title was how a color became
    a product, and ", Toffee" how a foundation shade did ("Orrin Skin Desire Soft Veil
    Foundation, Toffee"). Metric: derived styles of one color from a template of several, whose
    title ends with that color."""
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


def test_a_beauty_line_is_split_by_its_finish_or_formula_never_by_its_shade(ceiling):
    """Guard (#851, the ruling of 2026-11-07): a lipstick or foundation line sells its shades as
    SKUs and splits into products by finish (matte, satin) or formula (liquid, serum), as a
    beauty retailer lists them. Metric: the finishes and formulas the derived lipsticks and
    foundations name, and those of them that carry one shade."""
    for kind, key in (("Lipstick", "finish"), ("Foundation", "formula")):
        recs = [r for r in _derived(ceiling) if r["product_type"] == kind]
        values = {a["value"] for r in recs for a in r["attributes"] if a["key"] == key}
        assert len(values) > 2, (kind, values)
        assert [r["title"] for r in recs if len(r.get("color_options", ())) < 2] == []
