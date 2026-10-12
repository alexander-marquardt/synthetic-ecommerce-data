"""Where a clone keeps its pull request body draft: one spelling (#11464).

``scripts/pr_open.py`` posts the draft, and the commit-time file-size step
(``scripts/check_file_size.py --warn-at-commit``) reads it, so a
``File-Size-Exception:`` line written there before the push counts at commit
time as it does at the push. Both take the path from here, so neither can drift
from the other. Standard library only: the size gate runs without an install.
"""

from __future__ import annotations

from pathlib import Path

#: The draft every brief and ``agent_clone`` name: ``<clone>/.agent/pr-body.md``.
DRAFT = Path(".agent") / "pr-body.md"
#: The older place, read only when the draft is absent.
OLDER_DRAFT = Path(".git") / "pr-body.md"


def draft_body_file(root: Path) -> Path:
    """The body file to read in ``root``: the draft, else the older file when only it exists."""
    draft = root / DRAFT
    older = root / OLDER_DRAFT
    if not draft.exists() and older.is_file():
        return older
    return draft
