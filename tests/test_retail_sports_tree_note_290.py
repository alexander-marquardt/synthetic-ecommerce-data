"""Sports & Outdoors follow-ups from the first increment (gen#290).

Three things the review of #288 left open:

* ``docs/retail-sports-tree.md`` states, per leaf, the filters and whether a retailer's tree was
  compared, and it names every leaf of :mod:`sports_rows` (and no leaf that is gone);
* every type the issue listed and the first increment did not ship has a disposition there, an
  open issue or a reason, and never "not reached";
* no test pins the number of departments as a literal, so a new department does not red it.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import sports_rows  # noqa: E402

NOTE = ROOT / "docs" / "retail-sports-tree.md"
SEP = " > "
DEPARTMENT_LISTS = {"DEPARTMENTS", "RETAIL", "SHARED", "INDUSTRIAL"}


def _table(heading: str) -> list[list[str]]:
    """The body rows of the first table under ``## heading``, as lists of cell text."""
    lines = NOTE.read_text(encoding="utf-8").splitlines()
    start = lines.index(f"## {heading}")
    table: list[list[str]] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        if line.startswith("|"):
            table.append([c.strip() for c in line.strip().strip("|").split("|")])
    return table[2:]  # the header and the separator line


def _leaf_rows() -> dict[str, list[str]]:
    return {r[0]: r for r in _table("Leaves")}


def _built_leaves() -> set[str]:
    return {SEP.join(row.path) for row in sports_rows.ROWS}


def test_the_note_names_every_leaf_of_the_rows_and_no_other() -> None:
    assert set(_leaf_rows()) == _built_leaves()


def test_every_leaf_line_states_filters_a_guidance_example_and_a_tree_verdict() -> None:
    rows = _leaf_rows()
    assert rows, "the Leaves table is empty"
    for leaf, cells in rows.items():
        assert len(cells) == 4, leaf
        assert all(cells), leaf


def test_a_leaf_never_claims_a_retailer_tree_that_was_not_compared() -> None:
    # The only verdicts are "none" or a named tree; a bare "yes"/"matches" says nothing a
    # reviewer can check (gen#290: say which leaves have no mapping).
    for leaf, cells in _leaf_rows().items():
        verdict = cells[3].lower()
        assert verdict == "none" or len(verdict) > 12, (leaf, cells[3])


def test_the_filters_named_for_a_leaf_are_keys_the_rows_export() -> None:
    import export

    by_leaf: dict[str, set[str]] = {}
    for row in sports_rows.ROWS:
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        by_leaf.setdefault(SEP.join(row.path), set()).update(keys)
    for leaf, cells in _leaf_rows().items():
        named = {k.strip() for k in cells[1].split(",")}
        assert named <= by_leaf.get(leaf, set()), (leaf, named - by_leaf.get(leaf, set()))


def test_every_type_not_built_has_an_open_issue_or_a_reason() -> None:
    rows = _table("Not built")
    assert len(rows) >= 20
    for cells in rows:
        assert len(cells) == 3 and all(cells), cells
        disposition = cells[2]
        assert "not reached" not in disposition.lower(), cells
        assert re.fullmatch(r"#\d+", disposition) or len(disposition) >= 20, cells


def test_a_type_the_rows_build_is_not_listed_as_not_built() -> None:
    built = {row.product_type.lower() for row in sports_rows.ROWS}
    built |= {t + "s" for t in built}
    for cells in _table("Not built"):
        assert cells[0].lower() not in built, cells


def _pinned_counts(source: str) -> list[int]:
    """Line numbers of each ``len(<department list>) == <literal>`` comparison in ``source``."""
    lines = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Compare) or len(node.comparators) != 1:
            continue
        left, right = node.left, node.comparators[0]
        for call, other in ((left, right), (right, left)):
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Name)
                and call.func.id == "len"
                and len(call.args) == 1
                and isinstance(call.args[0], ast.Name)
                and call.args[0].id in DEPARTMENT_LISTS
                and isinstance(other, ast.Constant)
            ):
                lines.append(node.lineno)
    return lines


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("assert len(DEPARTMENTS) == 21", 1),
        ("assert 3 == len(RETAIL)", 1),
        ("assert len(DEPARTMENTS) == len(set(DEPARTMENTS))", 0),
        ("assert len(rows) == 21", 0),
    ],
)
def test_the_scan_finds_a_pinned_department_count_and_only_that(source: str, expected: int) -> None:
    assert len(_pinned_counts(source)) == expected


def test_no_test_pins_the_department_count_as_a_literal() -> None:
    found = [
        f"{path.relative_to(ROOT)}:{line}"
        for path in [*ROOT.glob("tests/*.py"), *RETAIL.glob("test_*.py")]
        for line in _pinned_counts(path.read_text(encoding="utf-8"))
    ]
    assert found == []
