"""The cleaning and beauty vocabularies share no word (gen#666).

Apart from ``tests/test_retail_scale_care_666.py`` because the vocabularies are checked when
``line_grammar`` is imported (``line_grammar_families.families()`` raises), so a module that
imports ``line_grammar`` at the top fails to collect and the mutant harness reads that as
NOT-TESTED. Here the import sits in the test body and a failure there is an assertion.
"""

from __future__ import annotations

import pytest


def test_the_family_vocabularies_share_no_word_with_each_other_or_a_name():
    """Guard (gen#666): a lead word in two families is one word under two kinds of product, and
    a first name reads as a brand. Metric: the words in two vocabularies, and the lead words that
    are also name words or that fall in both halves a build deals."""
    try:
        from synthetic_ecommerce_data.domains.retail import line_grammar, line_grammar_families
    except ValueError as err:
        pytest.fail(f"the vocabularies do not load: {err}")
    leads = {n: f.leads for n, f in line_grammar_families.families().items()}
    seen: dict[str, str] = {}
    twice = {
        w: (seen[w], fam)
        for fam, words in leads.items()
        for w in words
        if seen.setdefault(w, fam) != fam
    }
    assert twice == {}
    assert {w for words in leads.values() for w in words} & set(line_grammar.NAME_WORDS) == set()
    for fam in line_grammar.CARE:
        scale_half = set(leads[fam][line_grammar.HALVES["scale"] :: 2])
        grocery_half = set(leads[fam][line_grammar.HALVES["grocery"] :: 2])
        assert scale_half and grocery_half and not scale_half & grocery_half


def test_the_scale_and_grocery_deals_of_a_care_family_share_no_word():
    """Guard (gen#666): the scale and the grocery build deal a care family's lead words from
    different halves, so no word is one brand's in one build and another's in the other (the #642
    failure). Metric: the words both builds' ``Deal`` of one family hands out."""
    from synthetic_ecommerce_data.domains.retail import line_grammar

    brands = ["Alba", "Brio", "Cora", "Dune"]
    for fam in line_grammar.CARE:
        scale = line_grammar.Deal(fam, brands, {})
        grocery = line_grammar.Deal(fam, brands, {}, "grocery")
        scale_words = {w for b in brands for w in scale.of(b)}
        grocery_words = {w for b in brands for w in grocery.of(b)}
        assert scale_words and grocery_words
        assert scale_words & grocery_words == set()
