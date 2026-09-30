"""Every attribute name the generator publishes passes the census gate.

The gate is :func:`synthetic_industrial_products.catalog.names.name_problems`.
It replaced a rule that forced one name per product type per concept -- see that
module's docstring and the audit on elastic/prism-industrial-products#103.
The planted regressions below are the reason to trust it: a gate that has never
been shown a name it refuses proves nothing.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog import names, taxonomy
from synthetic_industrial_products.catalog.config import SMALL
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.catalog.vocab import (
    MEASUREMENT_SYSTEM_NAMES,
    STANDARDS_NAME,
    VOCAB,
)

ROOT = Path(__file__).resolve().parent.parent / "reference-statistics"


def _census() -> frozenset[str]:
    census = json.loads((ROOT / "00_attribute_name_census.json").read_text("utf-8"))
    return frozenset(entry["name_verbatim"] for entry in census["names_by_frequency"])


CENSUS = _census()


def _observed() -> frozenset[str]:
    census = json.loads((ROOT / "00_attribute_name_census.json").read_text("utf-8"))
    reference = json.loads((ROOT / "R1_reference_spec_table_names.json").read_text("utf-8"))
    found = {entry["name_verbatim"] for entry in census["names_by_frequency"]}
    for family in reference["by_family"].values():
        found.update(family)
    return frozenset(found)


OBSERVED = _observed()


def _declared() -> set[str]:
    declared = {spec.name for specs in VOCAB.values() for spec in specs}
    declared.add(STANDARDS_NAME)
    declared.update(name for name, _ in MEASUREMENT_SYSTEM_NAMES)
    return declared


def test_the_census_is_the_whole_census():
    """The gate is only as good as the list it reads; 585 is the census's own count."""
    census = json.loads((ROOT / "00_attribute_name_census.json").read_text("utf-8"))
    assert len(census["names_by_frequency"]) == 585


def _nouns(type_key: str) -> tuple[str, ...]:
    (path,) = taxonomy.LEAVES[type_key]
    return names.own_nouns(path)


def test_every_declared_name_passes_the_gate():
    """Per type, against that type's OWN nouns; and the whole set for membership and casing."""
    assert names.name_problems(_declared(), OBSERVED, CENSUS, nouns=()) == []
    for type_key, specs in VOCAB.items():
        declared = {spec.name for spec in specs}
        assert names.name_problems(declared, OBSERVED, CENSUS, _nouns(type_key)) == [], type_key


def test_every_emitted_name_passes_the_gate():
    """The live check: what a generated catalog actually publishes."""
    catalog = generate(SMALL)
    by_type: dict[str, set[str]] = {}
    for line in catalog.lines:
        found = by_type.setdefault(line.type_key, set())
        found.update(a.name for a in line.attributes)
        found.update(a.name for child in line.children for a in child.attributes)
    assert by_type, "the catalog published nothing"
    everything = set().union(*by_type.values())
    assert names.name_problems(everything, OBSERVED, CENSUS, nouns=()) == []
    for type_key, emitted in by_type.items():
        assert names.name_problems(emitted, OBSERVED, CENSUS, _nouns(type_key)) == [], type_key


@pytest.mark.parametrize(
    "type_key,planted",
    [
        ("washer_flat", "Widget Material"),  # observed nowhere: membership refuses it
        ("end_mill_square", "End Mill Material"),  # census 3, its own noun
        ("drill_jobber", "Drill Bit Size"),  # census 4, its own noun
        ("wheel_depressed_center", "Wheel Type"),  # reference list, its own noun
        ("nut_hex", "Hex Nut Material"),  # its own noun, not at the start
        ("screw_socket_head", "Cap Screw Type"),  # census 1: refused, not allow-listed
        ("bolt_hex", "Toggle Bolt Type"),  # census 1
        ("screw_socket_head", "Machine Screw Head Type"),  # census 1
        ("screw_socket_head", "Fastener Finish"),  # its own root's noun
        ("screw_socket_head", "Length Under Head"),  # census "Length under Head", other casing
    ],
)
def test_a_planted_type_prefixed_name_reds_the_gate(type_key, planted):
    declared = {spec.name for spec in VOCAB[type_key]} | {planted}
    problems = names.name_problems(declared, OBSERVED, CENSUS, _nouns(type_key))
    assert problems and all(repr(planted) in problem for problem in problems), problems


@pytest.mark.parametrize(
    "type_key,relational",
    [
        ("washer_flat", "For Bolt Size"),  # the mating bolt's size, census 6
        ("tap_spiral_point", "Drill Size"),  # a tap's tap-drill size, census 12
        ("end_mill_square", "Insert Screw"),  # a contained part, census 13
        ("washer_flat", "For Bolt Thread Direction"),  # census 6
        ("washer_flat", "For Fastener Sizes"),  # relational, though "Fastener" is its root's noun
    ],
)
def test_a_mating_or_contained_part_noun_is_not_a_qualifier(type_key, relational):
    """The noun names ANOTHER part, so refusing it would steer the record to a wrong name."""
    declared = {spec.name for spec in VOCAB[type_key]} | {relational}
    assert names.name_problems(declared, OBSERVED, CENSUS, _nouns(type_key)) == []


def test_an_allow_listed_type_specific_name_passes():
    """The control: the census's own type-specific names are not refused."""
    assert names.name_problems({"End Mill Style", "Tap Style"}, OBSERVED, CENSUS) == []


def test_every_exception_is_really_unobserved_and_justified():
    """An exception that the census already carries is a stale entry."""
    for name, reason in names.NAME_EXCEPTIONS.items():
        assert name not in OBSERVED, f"{name!r} is observed; drop its exception"
        assert len(reason) > 20, name


def test_every_type_specific_entry_is_type_qualified():
    for name in names.TYPE_SPECIFIC:
        assert names.qualifying_noun(name) is not None, name


def test_every_category_leaf_ends_in_its_own_product_noun():
    """A new type must bring its noun, or its own '<Type> X' names pass the gate.

    The leaf's HEAD noun -- its last words, in the plural -- must be a
    registered noun. A leaf that merely contains an existing noun ("Tap
    Wrenches" contains "Tap") does not satisfy it; its head, "Wrench", must be
    registered.
    """
    for type_key, paths in taxonomy.LEAVES.items():
        for path in paths:
            leaf = path[-1].lower()
            heads = [
                noun
                for noun in names.PRODUCT_NOUNS
                if re.search(rf"\b{re.escape(noun.lower())}(e?s)$", leaf)
            ]
            assert heads, (type_key, leaf)


def test_the_head_noun_rule_bites():
    # "Tap" is registered but not at the HEAD; "Handle" (the head) is not
    # registered at all -- neither the breadth categories
    # (alexander-marquardt/synthetic-industrial-products#34) nor anything
    # before them use it, so this stays a genuine negative control.
    leaf = "tap handles"
    assert not any(
        re.search(rf"\b{re.escape(noun.lower())}(e?s)$", leaf) for noun in names.PRODUCT_NOUNS
    )


def test_two_names_that_differ_only_in_case_are_refused():
    problems = names.name_problems({"Overall Length", "overall length"}, OBSERVED, CENSUS)
    assert any("differ only in case" in p for p in problems), problems


def test_a_census_name_in_another_casing_is_refused_on_its_own():
    """Not only as a twin: "Length Under Head" is on the reference list, and still refused.

    The census casing wins, because a keyword facet is case-sensitive and the
    census is where the catalog's names come from.
    """
    problems = names.name_problems({"Length Under Head"}, OBSERVED, CENSUS)
    assert problems and "another casing" in problems[0], problems
