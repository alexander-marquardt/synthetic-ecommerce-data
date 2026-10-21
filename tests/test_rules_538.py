"""Realism as rules: every rule of ``rules.py`` runs over every row it applies to (gen#538).

The rules of how the catalogue reads (a range name holds no color, ``Blue and White``, a dress
style beside the neckline and length it allows, sentence case, one key per concept, orange shoes,
two-word seeds) were a test file per issue, each building its own catalogue. They are functions of
``prototypes/retail_drawings/rules.py`` now. This file runs each over each row set it is declared
for, against the explicit allow-list ``rules_allow.toml``, a minimum count of rows examined, and
a planted breach of each rule that the rule must find.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import colorwords  # noqa: E402 -- the prototype's own directory is its import root
import rules  # noqa: E402

CASES = [(r, name) for r in rules.RULES for name in r.minimum]

#: The seven rules the issue names, one function each.
NAMED = {
    "color_in_range_name": "#444",
    "blue_and_white": "#514",
    "dress_neckline_by_length": "#511",
    "sentence_case": "#499",
    "one_key_per_concept": "#497",
    "orange_shoes": "#420",
    "two_word_seeds": "#460, #461",
}


@cache
def rowset(name: str) -> list[dict[str, Any]]:
    return rules.ROWSETS[name]()


@pytest.fixture(scope="module")
def reports() -> dict[tuple[str, str], rules.Report]:
    return rules.run_all()


def _id(case: tuple[rules.Rule, str]) -> str:
    return f"{case[0].name}-{case[1]}"


def test_the_rules_the_issue_names_exist_as_functions_with_their_issue():
    assert {r.name: r.issue for r in rules.RULES} == NAMED
    assert all(r.check.__doc__ and r.issue.split(",")[0] in r.check.__doc__ for r in rules.RULES)


def test_every_row_set_a_rule_names_has_a_loader():
    assert {name for r in rules.RULES for name in r.minimum} <= set(rules.ROWSETS)


@pytest.mark.parametrize("case", CASES, ids=_id)
def test_a_rule_holds_over_every_row_it_applies_to(reports, case):
    rule, name = case
    seen, found = reports[(rule.name, name)]
    assert seen >= rule.minimum[name], f"{rule.name} examined {seen} rows of {name}"
    excused = rules.allowed().get(rule.name, set())
    assert [f for f in found if f[0] not in excused] == []


def test_the_allow_list_names_rules_and_findings_that_exist_and_says_why(reports):
    table = rules.allow_table()
    assert set(table) <= {r.name for r in rules.RULES}
    for rule, body in table.items():
        raw = {f[0] for (name, _), (_, found) in reports.items() if name == rule for f in found}
        for entry in body["allow"]:
            assert entry["why"].strip(), (rule, entry["id"])
            assert entry["id"] in raw, f"{rule}: the allowed {entry['id']!r} is no longer found"


# --- A planted breach of each rule is found ------------------------------------------------------


def _find(templates: list[dict[str, Any]], pid: str) -> dict[str, Any]:
    return next(d for d in templates if d["product_id"] == pid)


def _range_title() -> list[dict[str, Any]]:
    docs = rowset("templates")
    ids = rules.range_ids()
    out = []
    for d in docs:
        out.append(dict(d, title=f"Red {d['title']}") if d["product_id"] in ids else d)
    return out


def _range_text() -> list[dict[str, Any]]:
    ids = rules.range_ids()
    return [
        dict(d, description=d["description"] + " Finished in purple.")
        if d["product_id"] in ids
        else d
        for d in rowset("templates")
    ]


def _coat_dress() -> list[dict[str, Any]]:
    dress = next(d for d in rowset("templates") if d["product_type"] == "Dress")
    return [dict(dress, title="Red Coat Dress", neckline="boat")]


def _color_doc(value: str) -> list[dict[str, Any]]:
    return [{"product_id": "X", "attributes": [{"key": "color", "name": "Color", "value": value}]}]


def _no_orange() -> list[dict[str, Any]]:
    return [
        dict(d, color_options=[o for o in d["color_options"] if o["color"] != "Orange"])
        for d in rowset("templates")
        if "color_options" in d
    ]


def _brown_orange() -> list[dict[str, Any]]:
    return [
        dict(
            d,
            color_options=[
                dict(o, hex="#3b2f2f") if o["color"] == "Orange" else o for o in d["color_options"]
            ],
        )
        for d in rowset("templates")
        if "color_options" in d
    ]


def _seed_without_its_word() -> list[dict[str, Any]]:
    seed, rows = next(iter(sorted(rules.seed_rows().items())))
    pid = f"PLT-{rows[0].code}"
    return [
        dict(d, title="Plain Thing", description="Nothing of it.") if d["product_id"] == pid else d
        for d in rowset("templates")
    ]


def _key_doc(*entries: tuple[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "product_id": "X",
            "attributes": [{"key": k, "name": n, "value": "v"} for k, n in entries],
            "variants": [],
        }
    ]


PLANTS: list[tuple[str, Callable[[], list[dict[str, Any]]], str]] = [
    ("color_in_range_name", _range_title, "holds a color word"),
    ("color_in_range_name", _range_text, "the description states"),
    ("blue_and_white", lambda: _color_doc("Blue / White"), "slash or an ampersand"),
    ("blue_and_white", lambda: _color_doc("Blue & White"), "slash or an ampersand"),
    ("blue_and_white", lambda: _color_doc("Blue, White"), "is a list"),
    ("blue_and_white", lambda: _color_doc("blue and white"), "is not written"),
    ("dress_neckline_by_length", _coat_dress, "coat:"),
    (
        "sentence_case",
        lambda: [{"product_id": "X", "category_path": ["Home", "Kitchen And Dining"]}],
        "is not 'Kitchen and dining'",
    ),
    (
        "sentence_case",
        lambda: [
            {
                "product_id": "X",
                "category_path": ["Home"],
                "attributes": [{"key": "k", "name": "Handle Material"}],
            }
        ],
        "is not 'Handle material'",
    ),
    ("one_key_per_concept", lambda: _key_doc(("item", "Item")), "is retired"),
    ("one_key_per_concept", lambda: _key_doc(("wheel_dia", "Wheel dia")), "is retired"),
    ("one_key_per_concept", lambda: _key_doc(("a", "Same"), ("b", "Same")), "has keys"),
    (
        "one_key_per_concept",
        lambda: _key_doc(("a", "One")) + _key_doc(("a", "Two")),
        "has display names",
    ),
    ("orange_shoes", _no_orange, "at least 3 wanted"),
    ("orange_shoes", _brown_orange, "is not a solid orange"),
    ("two_word_seeds", _seed_without_its_word, "lacks a word of the seed"),
]


@pytest.mark.parametrize(
    ("name", "plant", "note"), PLANTS, ids=[f"{n}-{note}" for n, _, note in PLANTS]
)
def test_a_planted_breach_of_a_rule_is_found(name, plant, note):
    check = next(r.check for r in rules.RULES if r.name == name)
    _, found = check(plant())
    assert any(note in f[1] for f in found), found


def test_every_key_a_merge_kept_is_published_in_the_golden_catalog():
    """The merged-away keys are gone because their values moved: the keys they moved to exist
    (anti-vacuity for ``one_key_per_concept``, #497)."""
    published = {e["key"] for d in rowset("golden") for e in rules.entries(d) if "key" in e}
    assert set(rules.MERGED_AWAY.values()) <= published


def test_a_seed_with_too_few_rows_is_found(monkeypatch):
    monkeypatch.setattr(rules, "MIN_ROWS_PER_SEED", 99)
    _, found = rules.two_word_seeds(rowset("templates"))
    assert any("decoy rows, at least 99 wanted" in f[1] for f in found)


def test_a_place_range_with_a_color_is_found(monkeypatch):
    import place_ranges

    monkeypatch.setattr(
        place_ranges, "PLACE_RANGES", (("Red Fell", "a fell"), *place_ranges.PLACE_RANGES)
    )
    _, found = rules.color_in_range_name(rowset("templates"))
    assert any(f[0] == "Red Fell" for f in found)


# --- The splitter the color rule reads (moved from the #514 test) --------------------------------


def test_the_splitter_writes_a_wash_with_a_second_color_in_words():
    assert colorwords.split("Mid Wash and Yellow") == ("Blue and Yellow", "Mid Wash")


def test_a_dangling_and_is_not_a_plain_color():
    """``and`` is a qualifier of a two-color value, so it cannot end one."""
    assert colorwords.is_plain("Blue and White")
    assert not colorwords.is_plain("Blue and")


def test_the_exported_retail_build_holds_the_three_ruled_two_color_values():
    """The live catalogue held three values with a slash and the maintainer ruled how each reads."""
    values = {
        e["value"] for d in rowset("retail") for e in rules.entries(d) if e.get("key") == "color"
    }
    assert values >= {"Blue and White", "Blue and Yellow", "Navy and White"}
