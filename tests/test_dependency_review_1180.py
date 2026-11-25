"""The committed dependency review has a verdict on each declared dependency (#1180).

Core's ``dependency_review.py`` writes the table and tests itself in elastic/prism; these tests
read this repository's files only. Docs: docs/internals/dependency-review.md.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "scripts" / "dependency_review_data.json"
DOC = ROOT / "docs" / "internals" / "dependency-review.md"
TABLE = ROOT / "docs" / "internals" / "appendix" / "dependency-review-table.md"
VERDICTS = {"keep", "replace", "drop"}


def _declared() -> set[str]:
    """Every direct dependency of ``pyproject.toml``, by its canonical name."""
    doc = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = doc["project"]
    groups = [
        project["dependencies"],
        *project.get("optional-dependencies", {}).values(),
        *doc["dependency-groups"].values(),
    ]
    return {
        re.match(r"[A-Za-z0-9._-]+", requirement).group(0).lower().replace("_", "-")
        for group in groups
        for requirement in group
    }


def test_every_declared_dependency_has_a_use_a_verdict_and_a_rule():
    reviews = json.loads(DATA.read_text(encoding="utf-8"))["dependencies"]
    assert set(reviews) == {f"PyPI:{name}" for name in _declared()}
    for key, review in reviews.items():
        assert review["verdict"] in VERDICTS, key
        assert review["rule"], key
        assert review["use"], key


def test_the_table_has_one_reviewed_row_for_each_declared_dependency():
    lines = TABLE.read_text(encoding="utf-8").splitlines()
    for name in sorted(_declared()):
        rows = [line for line in lines if line.startswith(f"| `{name}` ")]
        assert len(rows) == 1, name
        assert "not reviewed" not in rows[0], name
        assert "not fetched" not in rows[0], name


def test_the_method_page_links_the_table():
    assert f"(appendix/{TABLE.name})" in DOC.read_text(encoding="utf-8")
