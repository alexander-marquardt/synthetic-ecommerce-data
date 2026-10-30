"""A food or drink title reads like a real product: no generation number, no empty word (gen#729).

``Deal.owned`` used to build a food model as a lead word, a sub-model and a number ("Finest
Reserve 2") so that every model was unique, which suits a running shoe and no food: of 3,000
grocery styles on the shared cluster, 2,697 carried the pattern. A model is now a lead word and
at most one style word of the kind, and a brand past those words sells fewer lines.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    grocery,
    line_grammar,
    scale,
)
from synthetic_ecommerce_data.domains.retail.retail_figures import TIER_SKUS

FOOD = ("pantry", "drink", "alcohol")
SPECS = {name: line_grammar._NUMBERED[name] for name in FOOD}
#: Words the sub-model list used to hold: they name no property of a food.
EMPTY_WORDS = {"Reserve", "Special", "Deluxe", "Edition", "Batch", "Series"}
#: "Small Batch" is a phrase a label uses; the empty word was "Batch" on its own.
PHRASES = {"Small Batch"}
GENERATION = re.compile(r"\b(Reserve|Special|Deluxe|Edition|Batch|Series) [2-9]\b")


def _food(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The Food & Drink styles the line grammar names, the decoy rows aside."""
    skip = scale.source_ids("seasonal_rows") | scale.source_ids("color_word_brand_rows")
    return [
        r
        for r in records
        if r["category_path"][0] == "Food & Drink"
        and line_grammar.family(r) in FOOD
        and scale._line(r)
        and r["product_id"] not in skip
    ]


@pytest.fixture(scope="module", params=["grocery", "tier", "ceiling"])
def styles(request):
    if request.param == "grocery":
        return _food(grocery.build())
    if request.param == "tier":
        return _food(grocery.build(TIER_SKUS))
    return _food(ceiling_build().records)


def test_no_food_or_drink_model_carries_a_number(styles):
    """Guard (gen#729): the issue's own count of 2,498 in 3,000. Metric: the models with a digit,
    and the titles that still show the old pattern, in the 10K build, the 50K tier and the
    ceiling build."""
    assert len(styles) > 300
    assert [scale._line(r) for r in styles if re.search(r"\d", scale._line(r))][:10] == []
    assert [r["title"] for r in styles if GENERATION.search(r["title"])][:10] == []


def test_a_food_model_is_its_lead_word_and_at_most_one_style_word_of_its_kind(styles):
    """Guard (gen#729): "Finest Greek Style" is a yogurt, so "Finest Greek Style" on crisps, or a
    word from no row, is what the issue calls a meaningless word. Metric: the models that are
    not a lead word of the family plus a style word of the style's own kind."""
    bad = []
    for r in styles:
        spec = line_grammar._NUMBERED[line_grammar.family(r)]
        lead, _, rest = scale._line(r).partition(" ")
        if lead not in (*spec.leads, *spec.grocery_leads) or (
            rest and rest not in spec.styles[r["product_type"]]
        ):
            bad.append((r["product_type"], scale._line(r)))
    assert bad[:10] == []


def test_a_title_says_a_style_word_once(styles):
    """Guard (gen#729): a style row reaches every flavor of its kind, so a word the product
    already says would double it ("Chunky Beer Battered Chunky Chips"). Metric: the titles that
    repeat a word of their model's style."""
    bad = []
    for r in styles:
        rest = scale._line(r).split()[1:]
        words = re.findall(r"[\w']+", r["title"])
        if any(w != "&" and words.count(w) > 1 for w in rest):
            bad.append(r["title"])
    assert bad[:10] == []


def test_the_numbers_that_belong_to_a_product_stay(styles):
    """Guard (gen#729): the issue keeps a pack count and a percentage. Metric: the styles whose
    title or pack attribute still states one."""
    percent = [r for r in styles if re.search(r"\d%", r["title"])]
    packs = [
        a["value"]
        for r in styles
        for a in r["attributes"]
        if a["key"] == "pack_size" and re.search(r"\d", str(a["value"]))
    ]
    assert percent and packs


def test_every_food_kind_has_a_row_of_real_style_words():
    """Guard (gen#729): ``Deal.owned`` reads a row per kind, and a row may hold no number, no
    empty word, no food lead word (a model would read "Finest Crisp Fried") and no duplicate.
    Metric: the kinds short of a row, and the words a row may not hold."""
    leads = {w for s in SPECS.values() for w in (*s.leads, *s.grocery_leads)}
    for name, spec in SPECS.items():
        assert spec.bare and spec.numbers == (), name
        assert sorted(set(spec.kinds) ^ set(spec.styles)) == [], name
        for kind, row in spec.styles.items():
            assert len(row) >= 6 and len(row) == len(set(row)), kind
            words = {w for phrase in row for w in phrase.split()}
            assert sorted(w for w in words if re.search(r"\d", w)) == [], kind
            assert sorted(words & leads) == [], kind
            assert sorted(p for p in row if EMPTY_WORDS & set(p.split()) and p not in PHRASES) == []


def test_a_brand_past_its_style_words_repeats_a_model_and_gains_nothing():
    """Guard (gen#729): "a brand sells fewer lines; it does not gain a number or a meaningless
    word". Every slot past the row names a model the row already named, so the build's twin check
    refuses the title. Metric: the models of 2,000 slots against lead words times the row."""
    deal = line_grammar.Deal("pantry", ["Acme", "Bolt"], {}, "grocery")
    row = deal.spec.styles["Yogurt"]
    got = {deal.owned("Acme", slot, "Yogurt") for slot in range(2000)}
    leads = deal.of("Acme")
    assert got == {*leads, *(f"{w} {s}" for w in leads for s in row)}
    assert line_grammar.is_model("pantry", "Acme", f"{leads[0]} {row[0]}")
    assert not line_grammar.is_model("pantry", "Acme", f"{leads[0]} {row[0]} 2")
    assert not line_grammar.is_model("pantry", "Acme", f"{leads[0]} 2")


@pytest.mark.parametrize("fam", ["trainers", "cleaning", "toys"])
def test_a_numbered_model_keeps_its_generation(fam):
    """Guard (gen#729): "Tempo 3" stays; only the food families lost their number. Metric: the
    models of a numbered family's first slots, each with a digit."""
    deal = line_grammar.Deal(fam, ["Acme"], {})
    got = [deal.owned("Acme", slot) for slot in range(10)]
    assert all(any(c.isdigit() for c in model) for model in got), got
    assert deal.spec.numbers and not deal.spec.bare
    assert line_grammar.is_model(fam, "Acme", got[0])
