"""docs/retail-color-pattern.md states the pattern values the export writes (#397).

Since gen#255 the exported ``pattern`` value is lower case (``export.VALUE_CASE``), so a doc
that shows "Stripe" or "Grey Wash" as a value names a bucket the facet does not hold. The table
of the doc is read here against the splitter and the casing the export applies: nothing in this
file restates a pattern value that the code computes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import colorwords  # noqa: E402 -- the prototype's own directory is its import root
import export  # noqa: E402

DOC = ROOT / "docs" / "retail-color-pattern.md"


def _rows() -> list[tuple[list[str], str]]:
    """Each row of the doc's split table: (the authored shades, the pattern cell)."""
    out = []
    for line in DOC.read_text("utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        is_row = line.startswith("|") and len(cells) == 3
        if is_row and cells[0] != "Authored" and set(cells[0]) != {"-"}:
            out.append(([n.strip() for n in cells[0].split(",")], cells[2]))
    return out


def _exported(names: list[str]) -> set[str]:
    """The pattern values the export writes for ``names``: the split, then the one casing."""
    case = export.VALUE_CASE["pattern"]
    return {case(p) for n in names if (p := colorwords.split(n)[1])}


def test_the_table_has_a_row_per_kind_of_shade() -> None:
    assert len(_rows()) >= 6


@pytest.mark.parametrize(
    "names, cell", [pytest.param(n, c, id=n[0].replace(" ", "_")) for n, c in _rows()]
)
def test_a_pattern_cell_names_the_lower_case_values_the_export_writes(
    names: list[str], cell: str
) -> None:
    assert set(re.findall(r"`([^`]+)`", cell)) == _exported(names)


@pytest.mark.parametrize("anchor", ["drawn pattern", "is one pattern"])
def test_a_paragraph_that_names_a_pattern_value_quotes_no_title_case_one(anchor: str) -> None:
    hits = [p for p in DOC.read_text("utf-8").split("\n\n") if anchor in p]
    assert hits, f"no paragraph of {DOC.name} holds {anchor!r}"
    known = {"plain"} | _exported([n for names, _ in _rows() for n in names])
    quoted = [q for p in hits for q in re.findall(r'"([^"]+)"', p)]
    # An authored shade ("Red Tartan") is Title Case on purpose; a pattern value is not.
    assert [q for q in quoted if q.lower() in known and q != q.lower()] == []
