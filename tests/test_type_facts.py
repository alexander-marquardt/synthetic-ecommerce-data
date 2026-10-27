"""A new type states its facts in its own declaration, and the facts tests read them there (#61).

``test_catalog_facts`` used to hold its per-type tables (``MAY_CLAIM``,
``KEY``) by hand, and ``catalog_size`` its depth totals, so every new type
failed with a bare ``KeyError`` until someone added a row to each. Now every
type module declares them on its ``TypeSpec``, ``type_facts`` holds no table,
and these tests hold it so: a planted type is covered with no edit to any test
file, a type module that declares no fact is refused, and every modelled type
is covered.
"""

from __future__ import annotations

import collections
import dataclasses
import json
from collections.abc import Mapping
from pathlib import Path

import pytest

import type_facts
from published import authored_entries
from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.domains.industrial import conformance
from synthetic_ecommerce_data.domains.industrial.generate import all_type_keys
from test_catalog_facts import untitled_keys, wrong_claims

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"
BREADTH_QUALITY = "fast_and_cheap"
PLANTED = "planted_widget"


def _planted(**changes) -> typespec.TypeSpec:
    """The socket screw's spec under a key no table holds, with its facts declared.

    Its claim rule reaching ``conformance.applicable`` from the spec alone is
    ``test_type_registration``'s, which registers its planted type for real.
    """
    base = dataclasses.replace(
        typespec.modelled()["screw_socket_head"],
        key=PLANTED,
        module=f"planted.{PLANTED}",
        may_claim=frozenset({"ISO 4762", "DIN 912", "ASME B18.3", "ASTM A574"}),
        key_attributes=("Dia./Thread Size",),
    )
    return dataclasses.replace(base, **changes)


def _plant(monkeypatch: pytest.MonkeyPatch, spec: typespec.TypeSpec) -> None:
    real = typespec.modelled()
    monkeypatch.setattr(typespec, "modelled", lambda: {**real, spec.key: spec})


def _socket_screw_docs(count: int) -> list[dict]:
    """The first ``count`` socket screw records that claim a standard, from the
    committed catalog: a real record's shape, not one written for the test."""
    docs = []
    with (GOLDEN / "flat.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if '"screw_socket_head"' not in line:
                continue
            doc = json.loads(line)
            if doc["product_type"] == "screw_socket_head" and any(
                a["name"] == "Standards" for a in authored_entries(doc)
            ):
                docs.append(doc)
                if len(docs) == count:
                    break
    return docs


def test_a_planted_type_is_held_to_the_facts_it_declares(monkeypatch: pytest.MonkeyPatch) -> None:
    """A type declared only in its own module is covered by the facts tests
    and the size pins, with no edit to either."""
    _plant(monkeypatch, _planted())
    assert type_facts.may_claim().get(PLANTED) == _planted().may_claim
    assert type_facts.title_key().get(PLANTED) == ("Dia./Thread Size",)

    # The planted type has no authored-name map, so the names are mapped back before the rename.
    docs = [
        dict(doc, product_type=PLANTED, attributes=authored_entries(doc))
        for doc in _socket_screw_docs(80)
    ]
    assert len(docs) == 80
    outside = sorted(
        (doc["sku"], PLANTED, a["value"])
        for doc in docs
        for a in authored_entries(doc)
        if a["name"] == "Standards" and a["value"] not in _planted().may_claim
    )
    # The sample claims standards both inside and outside the planted set, so
    # the check is seen to pass the one and refuse the other.
    claimed = sum(1 for doc in docs for a in authored_entries(doc) if a["name"] == "Standards")
    assert 0 < len(outside) < claimed, (len(outside), claimed)
    assert sorted(wrong_claims(docs)) == outside

    assert untitled_keys(docs) == []
    untitled = [dict(doc, title="Planted Widget") for doc in docs]
    assert len(untitled_keys(untitled)) == len(docs)


def test_every_modelled_type_declares_its_facts_once() -> None:
    """Every type the facts tests read is covered, from its module or its row."""
    expected = set(all_type_keys("modelled")) | set(all_type_keys("new"))
    assert set(type_facts.may_claim()) == expected
    assert set(type_facts.title_key()) == expected
    assert set(type_facts.default_size()) == expected


@pytest.mark.parametrize(
    ("field", "unset", "read"),
    [
        ("may_claim", None, "may_claim"),
        ("key_attributes", (), "title_key"),
    ],
)
def test_a_type_module_that_declares_no_fact_is_refused_naming_it(
    monkeypatch: pytest.MonkeyPatch, field: str, unset: object, read: str
) -> None:
    _plant(monkeypatch, _planted(**{field: unset}))
    with pytest.raises(type_facts.TypeFactsError, match=rf"planted\.{PLANTED} declares no {field}"):
        getattr(type_facts, read)()


def test_each_types_declared_size_is_its_size_in_the_committed_catalog() -> None:
    """Per type, so a change that moves one type's count names that type, and
    two moves that cancel in the total still fail."""
    counted: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
    for slot, name in enumerate(("nested.jsonl", "flat.jsonl")):
        with (GOLDEN / name).open(encoding="utf-8") as handle:
            for line in handle:
                doc = json.loads(line)
                if doc["spec_quality"] != BREADTH_QUALITY:
                    counted[doc["product_type"]][slot] += 1
    assert {key: tuple(pair) for key, pair in counted.items()} == type_facts.default_size()


def test_type_facts_holds_no_per_type_table() -> None:
    """Every type's facts are on its own ``TypeSpec`` (#61): a table in
    ``type_facts`` keyed by type key is a second place to edit for a new type."""
    keys = set(all_type_keys())
    tables = sorted(
        name
        for name, value in vars(type_facts).items()
        if isinstance(value, Mapping) and keys & set(value)
    )
    assert tables == []


def test_every_modelled_and_newer_type_is_declared_in_its_own_module() -> None:
    """A type with no module is a type whose facts need a hand-kept row beside
    the derived ones."""
    declared = set(all_type_keys("modelled")) | set(all_type_keys("new"))
    assert sorted(declared - set(typespec.modelled())) == []


def test_a_type_claims_a_standard_through_its_own_claim_rule_or_none() -> None:
    """The ``conformance`` branch is derived too: a type that may claim a
    standard declares ``claims`` on its spec, so ``conformance.applicable`` has
    no per-type branch to edit and no type is claimed for by a shared one."""
    unruled = sorted(
        key for key, spec in typespec.modelled().items() if spec.may_claim and spec.claims is None
    )
    assert unruled == []
    assert not hasattr(conformance, "_shared_claims")
