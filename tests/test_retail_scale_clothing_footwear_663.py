"""The line grammar for the other clothing and footwear kinds (gen#663).

Bras, jeans, tees, trainers, boots and casual shoes were named by a range of the generic pool
("Treadmoor Pace Max 3"), which reads as a second brand. Each is now a module of
``line_grammar_families/`` (gen#513), so a model reads "<lead> [<sub>] <number>" from a
vocabulary of its own, with its brand first. These are the guards over that, and over the
brand-doubling a drawn brand could cause ("Treadmoor Treadmoor Pace Max 3").
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import line_grammar  # noqa: E402
import line_grammar_families  # noqa: E402
import scale  # noqa: E402

from retail_ceiling import ceiling_build  # noqa: E402

#: The six families of this feature, by module name.
NEW_FAMILIES = ("bra", "jeans", "tee", "trainers", "boots", "casual")

#: The clothing and footwear kinds #662 left out (#663): each reads its model from a vocabulary of
#: public retail listings, as the running shoes and the loafers do.
LINE_KINDS = (
    "Bra", "Jeans", "Tee", "T-Shirt", "Trainers", "Platform Trainers", "Plimsolls",
    "Barefoot Shoes", "Walking Boots", "Chelsea Boots", "Ankle Boots", "Chukka Boots",
    "Knee High Boots", "Wellies", "Safety Boots", "Espadrilles", "Slippers", "Wedges", "Mules",
    "Sandals", "Clogs", "Jelly Shoes",
)  # fmt: skip


@pytest.fixture(scope="module")
def ceiling():
    """Every template exhausted: the build where most derived styles exist (gen#513: shared)."""
    return ceiling_build()


def _all_families() -> dict[str, line_grammar_families.Family]:
    return line_grammar_families.families(
        core_kinds=line_grammar._CORE, reserved=line_grammar.NAME_WORDS
    )


def _family_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The styles of a family the line grammar names, the real-brand rows and the decoys aside
    (a class 8 decoy is named for a village street on purpose)."""
    return [
        r
        for r in records
        if line_grammar.family(r)
        and r["product_id"] not in scale.NIKE_IDS
        and not r["product_id"].startswith("PLT-D")
    ]


def test_a_vocabulary_model_is_one_of_its_leads_then_a_number_and_nothing_else():
    """#663: each new family's model reads "<lead> [<sub>] <number>" (a sub-model or a number, at
    least one); the bare lead, a lead the family does not hold or a stray word is no model."""
    fams = _all_families()
    assert set(NEW_FAMILIES) <= set(fams)
    for fam in NEW_FAMILIES:
        vocab = fams[fam]
        lead, number = vocab.leads[0], str(vocab.numbers[0])
        assert line_grammar.is_model(fam, "Brand", f"{lead} {number}")
        assert not line_grammar.is_model(fam, "Brand", lead)  # no number
        sub = vocab.subs[0]
        assert line_grammar.is_model(fam, "Brand", f"{lead} {sub} {number}")
        assert not line_grammar.is_model(fam, "Brand", f"Quibble {number}")  # no family leads
        assert not line_grammar.is_model(fam, "Brand", f"{lead} Quibble {number}")  # a stray word


def test_a_model_named_title_leads_with_its_brand(ceiling):
    """Guard (gen#662, #663): no title starts with a model or range name its brand does not
    precede, or the shopper reads the model as a brand ("Speed 4 Neutral Road Running Shoes").
    A title leads with its brand, after an optional "Kids' ", in every family but the appliances
    (whose series follow the brand by their own guard). Metric: the model-named titles that do
    not."""
    off = [
        (r["product_id"], r["title"])
        for r in _family_records(ceiling.records)
        if line_grammar.family(r) != "appliance"
        and scale._line(r)  # a style that names a model; a plain authored title has none
        and not r["title"].removeprefix("Kids' ").startswith(f"{r['brand']} ")
    ]
    assert off[:10] == [], len(off)


def test_every_clothing_and_footwear_kind_outside_662_has_a_line_grammar_family():
    """#663: Bra, Jeans, T-Shirt, Espadrilles, Slippers, Wedges, Mules, Trainers, Platform
    Trainers, Sandals, the boots and the plimsolls were named by a range of the generic pool
    ("Treadmoor Pace Max 3"), which reads as a second brand. Metric: the kinds with no family."""
    assert [k for k in LINE_KINDS if k not in line_grammar.FAMILIES] == []


def test_each_family_vocabulary_has_a_lead_for_every_brand_and_no_lead_is_shared(ceiling):
    """#663 (#642): a family deals its lead words over its brands, so it needs one per brand
    (else the deal divides by zero), and a lead belongs to one brand across every family. Metric:
    the families short of leads, and the leads two families hold."""
    fams = _all_families()
    assert {line_grammar.FAMILIES.get(k) for k in LINE_KINDS} == set(NEW_FAMILIES)
    brands: dict[str, set[str]] = collections.defaultdict(set)
    for r in _family_records(ceiling.records):
        brands[line_grammar.family(r)].add(r["brand"])
    short = {
        f: (len(fams[f].leads), len(brands[f]))
        for f in NEW_FAMILIES
        if len(fams[f].leads) < len(brands[f])
    }
    assert short == {}
    held = [w for v in fams.values() for w in v.leads] + list(line_grammar.NAME_WORDS)
    assert [w for w, n in collections.Counter(held).items() if n > 1] == []


def test_no_family_lead_is_a_first_name():
    """#663: a model word must not sound like a brand, and a given name does (the maintainer ruling
    of #663). Metric: the leads that are a common given name."""
    names = {
        "Grace", "Hope", "Faith", "Joy", "Ruby", "Daisy", "Rose", "Olive", "Willow", "Ivy",
        "Amber", "Pearl", "Violet", "Lily", "Stella", "Sienna", "Chloe", "Emma", "Mia", "Eva",
        "Ella", "Nora", "Iris", "Jade", "Luna", "Maya", "Hazel", "Sophie", "Sam",
    }  # fmt: skip
    held = [w for v in _all_families().values() for w in v.leads]
    assert sorted(set(held) & names) == []


def test_a_style_of_a_new_kind_names_a_model_of_its_family_after_its_brand(ceiling):
    """#663: every authored or derived style of these kinds that names a model names one made of
    its family's words, with its brand directly before it. Metric: the styles that do not."""
    styles = [r for r in _family_records(ceiling.records) if r["product_type"] in LINE_KINDS]
    assert {r["product_type"] for r in styles} == set(LINE_KINDS)
    derived = [r for r in styles if r["product_id"] in ceiling.template_of]
    assert {r["product_type"] for r in derived} == set(LINE_KINDS)
    off = [
        (r["product_id"], r["title"])
        for r in styles
        if (line := scale._line(r))
        and not (
            line_grammar.is_model(line_grammar.family(r), r["brand"], line)
            and r["title"].removeprefix("Kids' ").startswith(f"{r['brand']} {line} ")
        )
    ]
    assert off[:10] == [], len(off)
    assert all(scale._line(r) for r in derived)


def test_no_title_repeats_its_brand_back_to_back(ceiling):
    """#663: a derived running shoe read "Treadmoor Treadmoor Pace Max 3 ..." when the template's
    own brand was left in the title under the drawn brand. Metric: the titles that say a brand
    twice in a row."""
    off = [
        (r["product_id"], r["title"])
        for r in ceiling.records
        if re.search(rf"\b{re.escape(r['brand'])} {re.escape(r['brand'])}\b", r["title"])
    ]
    assert off[:10] == [], len(off)
