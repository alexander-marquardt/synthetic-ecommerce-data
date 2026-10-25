"""The cleaning and beauty vocabularies share no word (gen#666).

Apart from ``tests/test_retail_scale_care_666.py`` because the vocabularies are checked when
``line_grammar`` is imported (``line_grammar_families.families()`` raises), so a module that
imports ``line_grammar`` at the top fails to collect and the mutant harness reads that as
NOT-TESTED. Here the import sits in the test body and a failure there is an assertion.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))


def test_the_family_vocabularies_share_no_word_with_each_other_or_a_name():
    """Guard (gen#666): a lead word in two families is one word under two kinds of product, and
    a first name reads as a brand. Metric: the words in two vocabularies, and the lead words that
    are also name words or that fall in both halves a build deals."""
    try:
        import line_grammar
        import line_grammar_families
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
