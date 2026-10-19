"""The mutation harness stays under the file-size cap, and the rows live in their own files (#363).

``scripts/mutation_check.py`` held the whole table of planted defects: 4,796 lines against a cap of
1,750, and every retail pull request that added a row grew it. The table now lives in
``scripts/mutation_rows_<area>.py`` files that ``mutation_row.discover`` finds by glob, so the
harness is the runner only. The cap is read from ``scripts/file_size_cap.txt``, the number the
file-size gate checks, so a raised cap moves this test with it.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"


def _cap() -> int:
    text = (SCRIPTS / "file_size_cap.txt").read_text(encoding="utf-8")
    match = re.search(r"^cap\s+(\d+)\s*$", text, re.MULTILINE)
    assert match, "scripts/file_size_cap.txt names no cap"
    return int(match.group(1))


def _lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def test_the_harness_is_under_the_cap() -> None:
    harness = SCRIPTS / "mutation_check.py"
    assert _lines(harness) <= _cap(), (
        f"{harness.name} has {_lines(harness)} lines against a cap of {_cap()}: "
        "a row belongs in scripts/mutation_rows_<area>.py, not in the harness"
    )


def test_no_row_file_is_over_the_cap() -> None:
    over = {
        p.name: _lines(p) for p in sorted(SCRIPTS.glob("mutation_rows_*.py")) if _lines(p) > _cap()
    }
    assert not over, f"split these row files by area: {over}"
