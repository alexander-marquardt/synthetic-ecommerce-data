"""One letter case: every category node and attribute display name is sentence case (gen#499).

Industrial authored Title Case ("Handle Material", "Bore Dia.", "Seals & Gaskets > O-Ring
Seals"), retail sentence case ("Handle material"), and one key was shown under both. The
normaliser (:mod:`synthetic_ecommerce_data.core.letter_case`) runs at export on both domains;
this file is its guard: the rule on hand-written strings (the mutant surface), then the shipped
output of both builds and the committed golden, nested and flat.

It also guards the readers of an old name: a quoted old name in any ``scripts/`` file that is
not an authoring script, a ``name = <old>`` filter or a backticked old "field name" in the
docs, and (the one shape no text scan can see, a name that flows through a dict) the truth
``scripts/verify_elasticsearch.py`` compares a live cluster with, replayed offline against
the published names.
"""

from __future__ import annotations

import importlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest

from synthetic_ecommerce_data.core import emit, letter_case
from synthetic_ecommerce_data.core.config import SMALL, GeneratorConfig
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


# --- the readers of an old Title Case name (review of gen#505) --------------------------
#
# The export publishes sentence case, so a script that asks Elasticsearch for
# ``attributes.name: "Shank Dia."``, or a README that shows a published entry named
# ``Milling Dia.``, reads a name no document carries any more. The old names are computed
# from the build (the export with the rule off, minus what it still publishes), never typed.

#: Directories that hold no repository text.
_SKIP_DIRS = {".git", ".venv", ".agent", "node_modules", "__pycache__", ".pytest_cache"}

#: Outputs the build writes: their text is the build's, not a reader's.
_OUTPUTS = ("golden-catalog/", "golden-retail/", "tests/data/", "reference-statistics/")

#: Files that may name an old name as a ``"name"`` value, and why.
_AUTHORED_NAME_FIXTURES = {
    "tests/test_letter_case_499.py": "this guard: the rule's own before/after rows",
    "tests/test_nested_entry_contract.py": "a planted defect built by hand, never read back",
    "prototypes/retail_drawings/test_signals_and_paths.py": "reads the unexported class build",
}

#: Scripts and shipped config that read published documents or Elasticsearch: a quoted
#: old name there is a lookup that now matches nothing.
_READERS = ("scripts/", "src/prism_synthetic_industrial/")

#: Scripts under ``scripts/`` that quote an authored (Title Case) name on purpose, and why.
#: Every other script is a reader and may not.
_AUTHORED_NAME_SCRIPTS = {
    "scripts/mutation_": "mutants edit the authored source text, which keeps its casing",
    "scripts/new_type.py": "scaffolds an authored category literal",
    "scripts/contact_sheet.py": "reads the distributor census's own column names",
    "scripts/price_census_parse.py": "parses the distributor census's own column names",
}


def _display_strings(docs: list[dict[str, Any]]) -> set[str]:
    out: set[str] = set()
    for doc in docs:
        out.update(doc.get("category_path", ()))
        out.update(doc.get("attribute_names", ()))
        out.update(name for _, name in _names(doc))
    return out


@pytest.fixture(scope="module")
def old_display_names(
    industrial_nested: list[dict[str, Any]],
    industrial_flat: list[dict[str, Any]],
    retail_nested: list[dict[str, Any]],
) -> list[str]:
    """Each display name the export changes: what the build authored with the rule off,
    less what it still publishes under that spelling."""
    published = _display_strings([*industrial_nested, *industrial_flat, *retail_nested])
    published |= _display_strings(export.flat_documents())
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(letter_case, "apply", lambda doc: doc)
        catalog = generate(SMALL)
        authored = _display_strings([*emit.iter_nested(catalog), *emit.iter_flat(catalog)])
        authored |= _display_strings(export.documents())
        authored |= _display_strings(export.flat_documents())
    return sorted(name for name in authored - published if sentence_case(name) != name)


def _repo_text_files() -> list[tuple[str, str]]:
    found = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for file in files:
            path = Path(base) / file
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith(_OUTPUTS) or file.endswith((".ndjson", ".jsonl")):
                continue
            try:
                found.append((rel, path.read_text("utf-8")))
            except (UnicodeDecodeError, OSError):
                continue  # a binary file
    return found


def _alternation(names: list[str]) -> str:
    return "|".join(re.escape(name) for name in sorted(names, key=len, reverse=True))


def test_the_old_names_are_found_in_the_build(old_display_names: list[str]) -> None:
    """The list the two guards below search for is not empty (anti-vacuity)."""
    assert {"Shank Dia.", "Milling Dia.", "Handle Material"} <= set(old_display_names)


def test_no_text_shows_a_published_entry_under_an_old_display_name(
    old_display_names: list[str],
) -> None:
    pattern = r"""["']name["']\s*[:=]\s*["'](?:""" + _alternation(old_display_names) + r""")["']"""
    shown = re.compile(pattern)
    found = sorted(
        rel for rel, text in _repo_text_files()
        if rel not in _AUTHORED_NAME_FIXTURES and shown.search(text)
    )
    assert found == []


def test_no_reader_of_published_documents_quotes_an_old_display_name(
    old_display_names: list[str],
) -> None:
    quoted = re.compile(r"""["'](?:""" + _alternation(old_display_names) + r""")["']""")
    found = sorted(
        f"{rel}: {match.group(0)}"
        for rel, text in _repo_text_files()
        if rel.startswith(_READERS) and not rel.startswith(tuple(_AUTHORED_NAME_SCRIPTS))
        for match in quoted.finditer(text)
    )
    assert found == []


def test_no_prose_shows_an_old_display_name_as_a_field_name_or_a_name_filter(
    old_display_names: list[str],
) -> None:
    """A doc that tells a reader to filter ``name = Shank Dia.`` (unquoted, or in
    asterisks or backticks), or that calls a backticked ``Milling Dia.`` an Elasticsearch
    field name, shows a published entry under a name no document carries any more.
    Authored names in prose about the generator (``Length under Head`` in a table of the
    census's casing) are not this: only these two shapes are searched."""
    alt = _alternation(old_display_names)
    prose = re.compile(
        r"`(?:" + alt + r")`[^.]{0,40}field name|\bname\s*=\s*[*_`]*(?:" + alt + r")(?![\w.])"
    )
    found = sorted(
        f"{rel}: {match.group(0)}"
        for rel, text in _repo_text_files()
        if rel.endswith(".md") and rel not in _AUTHORED_NAME_FIXTURES
        for match in prose.finditer(text)
    )
    assert found == []


# --- a name that flows through a dict has no literal for the scans above to find ----------
#
# ``verify_elasticsearch.ground_truth`` builds the names a live cluster is checked against
# from ``attribute.name``. The cluster holds the published (sentence case) names, so a truth
# built from the authored ones differs by case alone. This replays the comparison of
# ``check_facet_discovery`` (and its flat twin) without a cluster.

_PUBLISHED_TYPES_SEED = GeneratorConfig(seed=42, lines=300)


def _verify_elasticsearch() -> Any:
    scripts = str(ROOT / "scripts")
    sys.path.insert(0, scripts)
    try:
        return importlib.import_module("verify_elasticsearch")
    finally:
        sys.path.remove(scripts)


@pytest.fixture(scope="module")
def truth_and_catalog() -> tuple[dict[str, Any], Any]:
    catalog = generate(_PUBLISHED_TYPES_SEED)
    return _verify_elasticsearch().ground_truth(catalog), catalog


def _published_names(docs: Any) -> dict[str, set[str]]:
    by_type: dict[str, set[str]] = defaultdict(set)
    for doc in docs:
        by_type[doc["product_type"]].update(a["name"] for a in doc["attributes"])
    return by_type


def test_the_live_facet_discovery_truth_equals_the_published_nested_names(
    truth_and_catalog: tuple[dict[str, Any], Any],
) -> None:
    truth, catalog = truth_and_catalog
    published = _published_names(emit.iter_nested(catalog))
    assert len(published) > 1 and any(
        " " in name for names in published.values() for name in names
    )  # anti-vacuity: several types, and a multi-word name
    assert {t: truth["names_by_type"][t] for t in published} == dict(published)


def test_the_live_truth_of_the_flat_names_equals_the_published_flat_names(
    truth_and_catalog: tuple[dict[str, Any], Any],
) -> None:
    truth, catalog = truth_and_catalog
    published = _published_names(emit.iter_flat(catalog))
    assert {t: truth["flat_names_by_type"][t] for t in published} == dict(published)
