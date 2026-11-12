"""The 500K mix in ``docs/catalogue-mix-837.md`` adds up and names real departments (gen#837).

The family issues and the sized release build are measured against that table's ``Target``
column. So the table has to sum to about 500K, its total row has to equal its rows, and each
department has to be one that ``core/departments.py`` lists, in the domain the row names.
A department not on that list yet is marked ``new``. Each row that grows names its own family
issue (gen#837 Done-when 2), and a row that does not grow names ``none``.
"""

from __future__ import annotations

import re
from pathlib import Path

from synthetic_ecommerce_data.core import departments

DOC = Path(__file__).resolve().parents[1] / "docs" / "catalogue-mix-837.md"
TARGET = 500_000
#: The issue asks for "about 500K"; its sized build is held to within 5%.
TOLERANCE = 0.05
DOMAIN_DEPARTMENTS = {"retail": departments.RETAIL, "industrial": departments.INDUSTRIAL}


def _count(cell: str) -> int:
    return int(cell.strip("* ").replace(",", ""))


def _table() -> tuple[list[dict[str, str]], dict[str, str]]:
    lines = DOC.read_text(encoding="utf-8").splitlines()
    start = lines.index("## The mix")
    rows = [line for line in lines[start:] if line.startswith("| ")]
    header = [cell.strip() for cell in rows[0].strip("|").split("|")]
    parsed = [
        dict(zip(header, (cell.strip() for cell in row.strip("|").split("|")), strict=True))
        for row in rows[1:]
        if not row.startswith("|---")
    ]
    body = [row for row in parsed if row["Department"] != "**Total**"]
    total = next(row for row in parsed if row["Department"] == "**Total**")
    return body, total


def test_the_targets_sum_to_about_500k_and_the_total_row_is_their_sum() -> None:
    rows, total = _table()
    for column in ("Today", "Target", "Growth"):
        assert sum(_count(row[column]) for row in rows) == _count(total[column]), column
    assert abs(_count(total["Target"]) - TARGET) <= TARGET * TOLERANCE
    for row in rows:
        assert _count(row["Target"]) - _count(row["Today"]) == _count(row["Growth"]), row


def test_each_row_names_its_domain_and_a_listed_department_or_a_new_one() -> None:
    rows, _ = _table()
    for row in rows:
        listed = row["Department"] in DOMAIN_DEPARTMENTS[row["Domain"]]
        assert row["Status"] == ("existing" if listed else "new"), row["Department"]
        if row["Status"] == "new":
            assert row["Department"] not in departments.DEPARTMENTS, row["Department"]
            assert _count(row["Today"]) == 0, row["Department"]


def test_every_growing_row_names_its_own_family_issue() -> None:
    """gen#837 Done-when 2: one family issue per department that grows, linked from its row."""
    rows, _ = _table()
    issues = []
    for row in rows:
        cell = row.get("Family issue", "")
        if _count(row["Growth"]) > 0:
            assert re.fullmatch(r"gen#\d+", cell), row["Department"]
            issues.append(cell)
        else:
            assert cell == "none", row["Department"]
    assert len(issues) == len(set(issues))


def test_every_listed_department_has_a_row() -> None:
    rows, _ = _table()
    assert {row["Department"] for row in rows} >= departments.DEPARTMENTS
