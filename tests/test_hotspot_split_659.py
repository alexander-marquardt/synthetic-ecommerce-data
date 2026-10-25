"""Shared hotspot files: a new type touches files of its own (gen#659).

Three hotspots were left after the registry guard of gen#513 and the derived figures of gen#536:
the per-feature sections of the decoy page, the ``TRUE_NODE`` rows of the class-8 test, and the
large-appliance family tables that the three appliance specs read from one module. Each is now one
file per topic, so two PRs that each add a type share no file.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RD = ROOT / "prototypes" / "retail_drawings"
DOC = ROOT / "docs" / "retail-product-word-decoys.md"
SECTIONS = ROOT / "docs" / "retail-product-word-decoys"
NODES = ROOT / "tests" / "decoy_true_nodes"
CLASS8_TEST = ROOT / "tests" / "test_retail_product_word_decoys_326.py"

#: The issues whose sections were once appended to the decoy page.
SECTION_ISSUES = (309, 332, 368, 425, 437, 460, 620, 625)
#: The family tables the large-appliance helpers module once held, with the spec that owns each now.
FAMILIES = (
    ("_FRIDGE_KINDS", "fridge_freezer"),
    ("_DISH_KINDS", "dishwasher"),
    ("_LAUNDRY_KINDS", "laundry_appliance"),
)


def test_the_decoy_page_holds_no_feature_section() -> None:
    sections = re.findall(r"^\*\*[^\n]*\(gen#\d+\)\.\*\*", DOC.read_text(encoding="utf-8"), re.M)
    assert sections == []


@pytest.mark.parametrize("issue", SECTION_ISSUES)
def test_each_feature_section_is_a_page_of_its_own(issue: int) -> None:
    pages = sorted(SECTIONS.glob(f"*-{issue}.md"))
    assert len(pages) == 1, f"docs/retail-product-word-decoys/<topic>-{issue}.md"
    assert f"gen#{issue}" in pages[0].read_text(encoding="utf-8")


def test_the_decoy_page_links_the_directory_and_no_single_page() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "](retail-product-word-decoys/)" in text
    assert re.findall(r"\]\(retail-product-word-decoys/[^)]+\.md\)", text) == []


def test_the_true_node_rows_are_not_in_the_class8_test() -> None:
    rows = re.findall(r'^\s+"[a-z]+": "[^"]+",', CLASS8_TEST.read_text(encoding="utf-8"), re.M)
    assert rows == []


def test_the_true_node_rows_are_in_modules_by_topic() -> None:
    modules = sorted(p for p in NODES.glob("*.py") if p.name != "__init__.py")
    assert len(modules) >= 6, "tests/decoy_true_nodes/<topic>.py"
    assert (NODES / "__init__.py").exists()


@pytest.mark.parametrize(("table", "spec"), FAMILIES)
def test_a_family_table_is_in_its_spec_and_not_in_the_shared_module(table: str, spec: str) -> None:
    shared = (RD / "large_appliance_rows.py").read_text(encoding="utf-8")
    own = (RD / "type_specs" / f"{spec}.py").read_text(encoding="utf-8")
    assert table not in shared
    assert re.search(rf"^{table} = \(", own, re.M), f"{spec}.py defines {table}"


def _topic_package(tmp_path: Path, name: str, **modules: dict[str, str]) -> Path:
    folder = tmp_path / name
    folder.mkdir()
    (folder / "__init__.py").write_text("", encoding="utf-8")
    for module, nodes in modules.items():
        (folder / f"{module}.py").write_text(f"NODES = {nodes!r}\n", encoding="utf-8")
    return folder


def test_the_nodes_of_two_topics_merge_and_a_repeated_agreeing_noun_is_one_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import decoy_true_nodes

    folder = _topic_package(
        tmp_path,
        "planted_merge",
        a={"cup": "Cups", "boot": "Boots"},
        b={"cup": "Cups", "sock": "Socks"},
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    try:
        merged: object = decoy_true_nodes._load(folder, "planted_merge")
    except ValueError as err:
        merged = str(err)
    assert merged == {"cup": "Cups", "boot": "Boots", "sock": "Socks"}


def test_a_noun_two_topics_map_differently_raises_and_names_both(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import decoy_true_nodes

    folder = _topic_package(tmp_path, "planted_conflict", a={"cup": "Cups"}, b={"cup": "Mugs"})
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(ValueError, match=r"'cup': a says 'Cups', b says 'Mugs'"):
        decoy_true_nodes._load(folder, "planted_conflict")
