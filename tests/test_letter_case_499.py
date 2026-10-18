"""One letter case: every category node and attribute display name is sentence case (gen#499).

Industrial authored Title Case ("Handle Material", "Bore Dia.", "Seals & Gaskets > O-Ring
Seals"), retail sentence case ("Handle material"), and one key was shown under both. The
normaliser (:mod:`synthetic_ecommerce_data.core.letter_case`) runs at export on both domains;
this file is its guard: the rule on hand-written strings (the mutant surface), then the shipped
output of both builds and the committed golden, nested and flat.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.letter_case import PROPER_NOUNS, apply, sentence_case
from synthetic_ecommerce_data.domains.industrial.generate import generate

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402  -- the prototype's own directory is its import root


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("Handle Material", "Handle material"),
        ("Bore Dia.", "Bore dia."),
        ("Number of Pieces", "Number of pieces"),
        ("Hose, Tube, Fittings & Valves", "Hose, tube, fittings & valves"),
        ("Seals & Gaskets", "Seals & gaskets"),
        ("O-Ring Seals", "O-ring seals"),
        ("Cut-Resistant Gloves", "Cut-resistant gloves"),
        ("Depressed-Center Wheels", "Depressed-center wheels"),
        # An acronym, a code or a lone capital letter keeps its capitals.
        ("ER Collets", "ER collets"),
        ("Max. RPM", "Max. RPM"),
        ("Size (UK)", "Size (UK)"),
        ("Standard V-Belts", "Standard V-belts"),
        ("Steel C-Clamps", "Steel C-clamps"),
        ("T-Slot Nuts", "T-slot nuts"),
        ("T-Shirts", "T-shirts"),
        ("AS568 Dash Number", "AS568 dash number"),
        ("Thread M12x1", "Thread M12x1"),  # a code with a lower-case tail, after the first word
        # The exception list: a trade name keeps its capital wherever it falls.
        ("Hex & Torx Keys", "Hex & Torx keys"),
        ("Nike Trainers", "Nike trainers"),
        # A word with its own inner capital is a brand spelling.
        ("iPhone Cases", "iPhone cases"),
        # A string that is already sentence case is unchanged.
        ("Handle material", "Handle material"),
        ("Dowel dia. (mm)", "Dowel dia. (mm)"),
        ("", ""),
    ],
)
def test_sentence_case_of_a_string(before: str, after: str) -> None:
    assert sentence_case(before) == after
    assert sentence_case(after) == after  # idempotent


def test_the_exception_list_is_spelled_in_one_way() -> None:
    for lower, spelling in PROPER_NOUNS.items():
        assert spelling.lower() == lower
        assert spelling != lower  # an entry that is already lower case is dead


def _doc() -> dict[str, Any]:
    entry = {"key": "handle_material", "name": "Handle Material", "value": "Hickory"}
    return {
        "category_path": ["Hand Tools", "Hammers"],
        "category_leaf": "Hammers",
        "attributes": [entry],
        "variants": [{"sku": "S1", "attributes": [dict(entry)]}, {"sku": "S2"}],
        "attribute_names": ["Handle Material"],
    }


def test_apply_renames_the_names_and_leaves_keys_values_and_the_input_alone() -> None:
    doc = _doc()
    out = apply(doc)
    assert out["category_path"] == ["Hand tools", "Hammers"]
    assert out["category_leaf"] == "Hammers"
    assert out["attributes"][0] == {
        "key": "handle_material",
        "name": "Handle material",
        "value": "Hickory",
    }
    assert out["variants"][0]["attributes"][0]["name"] == "Handle material"
    assert out["variants"][1] == {"sku": "S2"}
    assert out["attribute_names"] == ["Handle material"]
    assert doc == _doc()  # the build's own records are not rewritten under it


def test_apply_takes_the_leaf_from_the_cased_path() -> None:
    doc = {"category_path": ["Tools", "Ball End Mills"], "category_leaf": "Ball End Mills"}
    assert apply(doc)["category_leaf"] == "Ball end mills"


def _names(doc: dict[str, Any]) -> list[tuple[str, str]]:
    """Every (key, display name) pair on a nested or flat document."""
    rows = [*doc.get("attributes", ())]
    for variant in doc.get("variants", ()):
        rows.extend(variant.get("attributes", ()))
    return [(row["key"], row["name"]) for row in rows]


def _findings(docs: list[dict[str, Any]]) -> list[str]:
    """Each category node and display name that is not its own sentence-case form."""
    found: set[str] = set()
    for doc in docs:
        strings = [*doc["category_path"], doc["category_leaf"]]
        strings += [name for _, name in _names(doc)] + list(doc.get("attribute_names", ()))
        found.update(s for s in strings if sentence_case(s) != s)
    return sorted(found)


def _one_name_per_key(docs: list[dict[str, Any]]) -> dict[str, set[str]]:
    names: dict[str, set[str]] = defaultdict(set)
    for doc in docs:
        for key, name in _names(doc):
            names[key].add(name)
    return {key: held for key, held in names.items() if len(held) > 1}


def _golden(name: str) -> list[dict[str, Any]]:
    path = ROOT / "golden-catalog" / name
    return [json.loads(line) for line in path.read_text("utf-8").splitlines()]


@pytest.fixture(scope="module")
def industrial_nested() -> list[dict[str, Any]]:
    return list(emit.iter_nested(generate(SMALL)))


@pytest.fixture(scope="module")
def industrial_flat() -> list[dict[str, Any]]:
    return list(emit.iter_flat(generate(SMALL)))


@pytest.fixture(scope="module")
def retail_nested() -> list[dict[str, Any]]:
    return export.documents()


def test_no_industrial_category_node_or_name_breaks_the_rule(
    industrial_nested: list[dict[str, Any]], industrial_flat: list[dict[str, Any]]
) -> None:
    assert _findings(industrial_nested) == []
    assert _findings(industrial_flat) == []


def test_no_retail_category_node_or_name_breaks_the_rule(
    retail_nested: list[dict[str, Any]],
) -> None:
    assert _findings(retail_nested) == []
    assert _findings(export.flat_documents()) == []


@pytest.mark.parametrize("name", ["nested.jsonl", "flat.jsonl"])
def test_the_committed_golden_catalog_keeps_the_rule(name: str) -> None:
    assert _findings(_golden(name)) == []


def test_one_key_has_one_display_name_across_both_catalogues(
    industrial_nested: list[dict[str, Any]], retail_nested: list[dict[str, Any]]
) -> None:
    assert _one_name_per_key([*industrial_nested, *retail_nested, *_golden("nested.jsonl")]) == {}


def test_the_attribute_the_issue_names_has_one_display_name() -> None:
    names = {name for doc in _golden("nested.jsonl") for key, name in _names(doc)
             if key == "handle_material"}
    assert names == {"Handle material"}


def test_the_category_the_issue_names_is_in_sentence_case() -> None:
    paths = {tuple(doc["category_path"]) for doc in _golden("nested.jsonl")}
    assert ("Hose, tube, fittings & valves", "Seals & gaskets", "O-ring seals") in paths


def test_the_searchable_text_carries_the_cased_category(
    industrial_flat: list[dict[str, Any]],
) -> None:
    for row in industrial_flat[:200]:
        for node in row["category_path"]:
            assert node in row["text"]
