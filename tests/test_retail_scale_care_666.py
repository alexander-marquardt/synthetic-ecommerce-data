"""Cleaning and beauty line grammar guards over the ceiling build (gen#666, gen#513).

Moved out of ``tests/test_retail_scale.py``, the registry file: a title that leads with its
brand and a model of the family's words, the one-brand lead words, and the two halves of a family's
lead list the scale and grocery builds deal.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

from retail_ceiling import ceiling_build

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import line_grammar  # noqa: E402
import line_grammar_families  # noqa: E402
import scale  # noqa: E402


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


#: The kinds whose styles led with a range name before gen#666, by department.
CARE_KINDS = {
    "Cleaning": (
        "Laundry Detergent", "Floor Cleaner", "Bathroom Cleaner", "Dish Soap", "Glass Cleaner",
        "Air Freshener", "Fabric Softener", "Kitchen Cleaner", "Toilet Cleaner",
    ),
    "Beauty": (
        "Hand Wash", "Shower Gel", "Lipstick", "Foundation", "Hand Cream", "Body Cream",
        "Eye Cream", "Foot Cream", "Body Lotion", "Moisturiser", "Conditioner", "Shampoo",
        "Wash Bag", "Make-Up Bag", "Lip Balm", "Eyeliner", "Perfume",
    ),
}  # fmt: skip


def _care_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The cleaning and beauty styles of :data:`CARE_KINDS` that name a model (gen#666)."""
    return [
        r for r in records
        if r["category_path"][0] in CARE_KINDS
        and r["product_type"] in CARE_KINDS[r["category_path"][0]]
        and scale._line(r)
    ]  # fmt: skip


def test_every_cleaning_and_beauty_kind_is_in_a_family():
    """Guard (gen#666): a kind outside ``line_grammar.FAMILIES`` keeps a range name that leads its
    title like a second brand ("Foxmere Orange Laundry Liquid"). Metric: kinds with no family."""
    kinds = [k for each in CARE_KINDS.values() for k in each]
    off = [k for k in kinds if k not in line_grammar.FAMILIES]
    assert off == []
    assert {line_grammar.FAMILIES[k] for k in CARE_KINDS["Cleaning"]} == {"cleaning"}
    assert {line_grammar.FAMILIES[k] for k in CARE_KINDS["Beauty"]} == {"beauty"}


def test_a_cleaning_or_beauty_title_leads_with_its_brand(ceiling):
    """Guard (gen#666): public listings lead with the brand ("Persil Bio Laundry Liquid"), so a
    title that opens on a model word reads as a second brand. Metric: the model-named cleaning
    and beauty titles that do not start with their brand, and the styles checked."""
    care = _care_records(ceiling.records)
    assert len(care) > 800
    off = [
        (r["product_id"], r["title"]) for r in care if not r["title"].startswith(f"{r['brand']} ")
    ]
    assert off[:10] == [], len(off)


def test_a_cleaning_or_beauty_model_is_built_from_its_family_vocabulary(ceiling):
    """Guard (gen#666): the model of a cleaning or beauty style is a plain word of its family, a
    sub-model and a code, never a coined range name. Metric: the styles whose model is not."""
    off = [
        (r["product_id"], r["brand"], scale._line(r))
        for r in _care_records(ceiling.records)
        if not line_grammar.is_model(
            line_grammar.FAMILIES.get(r["product_type"], ""), r["brand"], scale._line(r)
        )
    ]
    assert off[:10] == [], len(off)


def test_the_family_vocabularies_share_no_word_with_each_other_or_a_name():
    """Guard (gen#666): a lead word in two families is one word under two kinds of product, and
    a first name reads as a brand. Metric: the words in two vocabularies, and the lead words that
    are also name words or that fall in both halves a build deals."""
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


def test_a_cleaning_or_beauty_lead_word_belongs_to_one_brand(ceiling):
    """Guard (gen#666, gen#642): a lead word under two brands reads as a range of neither.
    Metric: the lead words of cleaning and beauty styles with the brands that carry them."""
    brands: dict[str, set[str]] = {}
    for r in _care_records(ceiling.records):
        brands.setdefault(scale._line(r).split()[0], set()).add(r["brand"])
    assert {w: sorted(b) for w, b in brands.items() if len(b) > 1} == {}


#: Pairs of one brand's models that differ in a single token ("Defence 6", "Defence Ultra 6").
#: The build holds 52; without the stepping of the sub-model and the generation (``Deal.owned``)
#: it holds 153, and the grocery near-duplicate share leaves its 4.0% cap.
CEILING_ONE_TOKEN_PAIRS = 100


def test_a_care_brands_models_seldom_differ_in_one_token(ceiling):
    """Guard (gen#666): two models of one brand that differ in a single token make titles that
    read as one listing, which is what the grocery near-duplicate cap counts. Metric: the pairs
    of one brand's models whose token sets differ in under two tokens, against
    :data:`CEILING_ONE_TOKEN_PAIRS`."""
    models: dict[str, set[str]] = {}
    for r in _care_records(ceiling.records):
        models.setdefault(r["brand"], set()).add(scale._line(r))
    assert sum(len(m) for m in models.values()) > 300
    close = [
        (brand, a, b)
        for brand, each in models.items()
        for a in sorted(each)
        for b in sorted(each)
        if a < b and len(set(a.split()) ^ set(b.split())) < 2
    ]
    assert len(close) <= CEILING_ONE_TOKEN_PAIRS, close[:5]
