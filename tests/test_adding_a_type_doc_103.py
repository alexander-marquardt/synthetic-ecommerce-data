"""The steps of docs/adding-a-type.md are named items, not a numbered list (#103).

A numbered list renumbers every item after an inserted step, so two PRs that each add a step
edit the same lines and the second is refused by ``scripts/merge_pr.sh``. A named item is one
line to add, and a reference to it is by name.
"""

from __future__ import annotations

import re
from pathlib import Path

DOC = Path(__file__).resolve().parents[1] / "docs" / "adding-a-type.md"
HEADING = "### A new type"


def _section() -> list[str]:
    lines = DOC.read_text("utf-8").splitlines()
    start = lines.index(HEADING)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("#"))
    return lines[start + 1 : end]


def test_the_steps_of_a_new_type_are_named_items() -> None:
    items = [line for line in _section() if line.startswith("- **")]
    assert len(items) >= 8, items
    assert [line for line in _section() if re.match(r"\d+\. ", line)] == []


def test_no_item_is_referred_to_by_its_number() -> None:
    text = DOC.read_text("utf-8")
    assert re.findall(r"\(steps? \d+[^)]*\)", text) == []
    assert re.findall(r"[Dd]o steps \d+", text) == []
