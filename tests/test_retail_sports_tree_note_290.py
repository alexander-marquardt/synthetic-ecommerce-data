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


# A leaf says "none" until someone compares it; a comparison is recorded in a form a reviewer can
# check: the tree's name, the page compared and the date, so "matches the <retailer> tree" alone
# is refused (r369: the old rule only refused short text).
VERDICT_FORM = re.compile(r"compared with [^()]+ \(https?://\S+, \d{4}-\d{2}-\d{2}\)")
GUIDANCE_EXAMPLES = {
    "none",
    "tent capacity, season rating",
    "season rating",
    "mat thickness",
    "dumbbell weight",
}


def _verdict_accepted(verdict: str) -> bool:
    return verdict == "none" or VERDICT_FORM.fullmatch(verdict) is not None


@pytest.mark.parametrize(
    ("verdict", "accepted"),
    [
        ("none", True),
        ("compared with Decathlon (https://www.decathlon.es/es/tents, 2026-10-16)", True),
        ("matches the Decathlon tree", False),
        ("matches", False),
        ("yes", False),
        ("see the issue tracker later", False),
        ("compared with Decathlon", False),
        ("None", False),
    ],
)
def test_the_retailer_tree_verdict_has_a_checkable_form(verdict: str, accepted: bool) -> None:
    assert _verdict_accepted(verdict) is accepted


def test_a_leaf_never_claims_a_retailer_tree_that_was_not_compared() -> None:
    for leaf, cells in _leaf_rows().items():
        assert _verdict_accepted(cells[3]), (leaf, cells[3])


def test_a_guidance_example_is_one_the_guidance_names_and_sits_on_its_own_leaf() -> None:
    rows = _leaf_rows()
    for leaf, cells in rows.items():
        assert cells[2] in GUIDANCE_EXAMPLES, (leaf, cells[2])
    assert [name for name, c in rows.items() if c[2] == "dumbbell weight"] == [
        "Sports & Outdoors > Yoga & Fitness > Weights > Dumbbells"
    ]


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


# Every type gen#265 lists that neither increment shipped (the second, gen#368, built seventeen;
# gen#352 built bikes, bike helmets, kayaks, scooters and skateboards; its optional lights,
# locks and stoves are left out). Building one moves
# its name to the Leaves table, which test_a_type_the_rows_build_is_not_listed_as_not_built forces.
EXPECTED_NOT_BUILT = frozenset(
    {
        "Bike lights", "Bike locks", "Camping stoves", "Swimsuits and trunks", "Balance bikes",
    }
)  # fmt: skip


def _not_built_problems(rows: list[list[str]]) -> list[str]:
    """What is wrong with the Not built rows: the set must equal EXPECTED_NOT_BUILT exactly."""
    problems = []
    names = [r[0] for r in rows]
    for name in sorted(EXPECTED_NOT_BUILT - set(names)):
        problems.append(f"{name}: no row")
    for name in sorted(set(names) - EXPECTED_NOT_BUILT):
        problems.append(f"{name}: not an expected type")
    for name in sorted({n for n in names if names.count(n) > 1}):
        problems.append(f"{name}: listed twice")
    for cells in rows:
        if len(cells) != 3 or not all(cells):
            problems.append(f"{cells[0]}: a row needs a type, a family and a disposition")
            continue
        disposition = cells[2]
        if "not reached" in disposition.lower():
            problems.append(f"{cells[0]}: 'not reached' is scope, not a reason")
        elif not (re.fullmatch(r"#\d+", disposition) or len(disposition) >= 20):
            problems.append(f"{cells[0]}: neither an issue nor a reason")
    return problems


def test_every_type_not_built_has_an_open_issue_or_a_reason() -> None:
    assert _not_built_problems(_table("Not built")) == []


@pytest.mark.parametrize("dropped", ["Bike lights", "Camping stoves", "Balance bikes"])
def test_a_dropped_not_built_row_is_seen(dropped: str) -> None:
    rows = [r for r in _table("Not built") if r[0] != dropped]
    assert any(dropped in p for p in _not_built_problems(rows))


def test_an_added_or_dispositionless_not_built_row_is_seen() -> None:
    rows = _table("Not built")
    assert _not_built_problems([*rows, ["Hockey sticks", "Team", "#368"]])
    assert _not_built_problems([*rows[:-1], [rows[-1][0], rows[-1][1], "not reached"]])
    assert _not_built_problems([*rows[:-1], [rows[-1][0], rows[-1][1], "later"]])


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
