"""The step 3 text of scripts/merge_pr.sh and docs/ci-sharding.md name the README size test (#700).

This file is apart from tests/test_merge_pr.py on purpose: a test that reads
``docs/ci-sharding.md`` is selected by a document change, and test_merge_pr.py
and its importers are about a quarter of the suite's seconds, which the
selection guard in tests/test_ci_select_495.py refuses. This file imports
nothing from them, so a document change selects only this cheap file.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_step_3_wording_names_the_readme_size_test_not_a_count() -> None:
    """The step 3 text and the sharding doc name the size test and no count (#700).

    Step 3 runs the README size test too, so "drift, golden and seam" alone and
    "the four" are claims the entry in CHECKS made false.
    """
    script = (REPO / "scripts" / "merge_pr.sh").read_text(encoding="utf-8")
    doc = (REPO / "docs" / "ci-sharding.md").read_text(encoding="utf-8")
    assert "golden and seam tests" not in script
    assert "golden and seam" not in doc
    assert "the four drift" not in doc
    assert "README size" in doc
