"""The pre-merge run runs every test file under ``prototypes/``, so none goes red unseen (gen#486).

``pytest`` is configured with ``testpaths = ["tests"]``, so the pre-merge run never collected
the ``test_*.py`` files that ``prototypes/retail_drawings`` keeps beside the code they test.
Seven of them failed on main for a day (gen#479 found the same for ``test_real_classes.py``;
gen#486 found the rest) because nothing ran them: every agent that did run them met failures
it had not caused.

This file is collected, and runs each prototype test file in its own pytest process (a file
imports its modules by bare name from its own directory and builds the whole corpus at
import, so one process per file is the shape they were written for). A new ``test_*.py`` file
under ``prototypes/`` is guarded the day it is added: the files are listed by a glob of the
tree, not by a list that someone has to extend.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PROTOTYPES = REPO / "prototypes"
FILES = sorted(p.relative_to(REPO).as_posix() for p in PROTOTYPES.rglob("test_*.py"))


def test_the_prototype_test_files_are_found() -> None:
    assert "prototypes/retail_drawings/test_house_styles.py" in FILES
    assert len(FILES) >= 9


@pytest.mark.parametrize("file", FILES, ids=[Path(f).name for f in FILES])
@pytest.mark.timeout(600)
def test_a_prototype_test_file_passes(file: str) -> None:
    # PYTEST_ADDOPTS is the CI job's ("-n auto ..." and a junit path): not this child's.
    env = {**os.environ, "PYTEST_ADDOPTS": ""}
    run = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", file],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    tail = "\n".join(run.stdout.splitlines()[-40:])
    assert run.returncode == 0, f"{file} fails:\n{tail}\n{run.stderr[-2000:]}"
