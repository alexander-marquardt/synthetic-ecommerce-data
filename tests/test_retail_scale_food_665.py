"""Food and drink line grammar guards over the ceiling build (gen#665, gen#513).

Moved out of ``tests/test_retail_scale.py``, the registry file: the guards for the Food & Drink
families, the brand-led mixture, the one-brand lead words and the documented example.
"""

from __future__ import annotations

import collections
import re
from typing import Any

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    line_grammar,
    line_grammar_families,
    scale,
)


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def _family_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The styles of a family the line grammar names, the real-brand and decoy rows aside."""
    skip = (scale.source_ids("nike_rows") | scale.source_ids("seasonal_rows")
            | scale.source_ids("color_word_brand_rows"))
    return [r for r in records if line_grammar.family(r) and r["product_id"] not in skip]


def _food(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The Food & Drink styles."""
    return [r for r in records if r["category_path"][0] == "Food & Drink"]


def test_every_food_and_drink_kind_is_mapped_to_a_line_grammar_family(ceiling):
    """Guard (gen#665): a food or drink kind outside ``line_grammar.FAMILIES`` keeps the coined
    range names of :mod:`range_ownership` ("Larkrise Jam"). Metric: the Food & Drink kinds
    with no family."""
    kinds = {r["product_type"] for r in _food(ceiling.records)}
    assert len(kinds) >= 70
    assert sorted(k for k in kinds if k not in line_grammar.FAMILIES) == []


def test_a_food_or_drink_title_leads_with_its_brand_in_a_mixture(ceiling):
    """Guard (gen#665): of the food titles that name a range, most lead with the brand, so the
    range reads as the brand's model ("Hollin Finest Slow Cooked Strawberry Jam"), not as a second
    brand ("Larkrise Jam"), and some do not, as the maintainer ruled on #665: "we can always make
    some of the real products not have their brand in their title .. they don't all need it ..
    we can have a mixture". The decoy rows keep their authored titles. Metric: the share of
    range-named food titles led by the brand (between a half and nine tenths), and the
    brand-less ones that name another brand."""
    decoys = scale.source_ids("seasonal_rows") | scale.source_ids("color_word_brand_rows")
    rows = [r for r in _food(ceiling.records) if scale._line(r) and r["product_id"] not in decoys]
    led = [r for r in rows if r["title"].startswith(f"{r['brand']} ")]
    assert 0.5 <= len(led) / len(rows) <= 0.9, (len(led), len(rows))
    brands = {r["brand"] for r in ceiling.records}
    bare = [r for r in rows if r not in led]
    assert [(r["product_id"], r["title"]) for r in bare
            if any(r["title"].startswith(f"{b} ") for b in brands)][:10] == []  # fmt: skip


def test_a_food_range_word_belongs_to_one_brand_and_to_no_other_vocabulary(ceiling):
    """Guard (gen#665, #642): the lead words of the food families are no sub-model, name, sport
    lead or brand, no word is in two families or in both builds' halves, and in the catalogue
    one brand holds a lead word. Metric: the shared words, and the lead words of two brands."""
    specs = [line_grammar._NUMBERED[f] for f in ("pantry", "drink", "alcohol")]
    halves = [w for s in specs for w in (*s.leads, *s.grocery_leads)]
    assert len(halves) == len(set(halves))
    subs = {w for s in specs for w in s.subs}
    sport = line_grammar_families.families()["sport"].leads
    others = subs | set(line_grammar.NAME_WORDS) | set(sport)
    brands = {r["brand"] for r in ceiling.records}
    assert sorted(set(halves) & (others | brands)) == []
    # A word that leads another product's title would read as a range two brands share (#623).
    leads = {r["title"].removeprefix("The ").split()[0] for r in ceiling.records
             if r["category_path"][0] != "Food & Drink"}  # fmt: skip
    assert sorted(set(halves) & leads) == []
    owner: dict[str, set[str]] = collections.defaultdict(set)
    for r in _family_records(_food(ceiling.records)):
        if line := scale._line(r):
            owner[line.split()[0]].add(r["brand"])
    assert owner and sorted(w for w, b in owner.items() if len(b) > 1) == []


def test_the_documented_food_example_words_are_real_lead_words():
    """Guard (gen#665): the model word in the pantry module's docstring example is one of the
    food lead words, so the docs do not teach a word the build never draws. Metric: the example
    words ("Basics", "Finest") and the docstring title's model word that are in no lead list."""
    doc = line_grammar_families.pantry.__doc__ or ""
    spec = line_grammar._NUMBERED["pantry"]
    leads = {*spec.leads, *spec.grocery_leads}
    quoted = re.search(r"own-label word \(``(\w+)``, ``(\w+)``\)", doc)
    title = re.search(r'"Hollin (\w+) Slow Cooked Strawberry Jam', doc)
    assert quoted and title
    missing = [w for w in (*quoted.groups(), title.group(1)) if w not in leads]
    assert missing == []
