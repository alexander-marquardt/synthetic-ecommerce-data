"""The retail ceiling build, made once per process for every test file that needs it (gen#513).

``tests/test_retail_scale.py`` was a registry: its ``ceiling`` fixture was the only way to a
build where most derived styles exist, so each feature's guard over the ceiling build was a test
appended to that one file, and the open PRs of 2026-10-25 (synth#671 to #674) conflicted in all 6
pairs. A feature's guard is now ``tests/test_retail_scale_<topic>_<issue>.py``, a file of its own
that takes the build from here::

    from retail_ceiling import ceiling_build

    @pytest.fixture(scope="module")
    def ceiling():
        return ceiling_build()

The build is cached, so the files of one pytest process share a single build, not one each.
A test reads it and never edits it.
"""

from __future__ import annotations

import functools
import sys
from pathlib import Path

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402
from retail_figures import figures  # noqa: E402


@functools.cache
def ceiling_build() -> scale.Scaled:
    """Every template exhausted: the build where most derived styles exist (seed 0)."""
    return scale.build(figures()["ceiling"]["skus"] * 2)
