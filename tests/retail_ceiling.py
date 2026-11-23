"""The retail ceiling build, made once for every test file that needs it (gen#513, gen#539).

``tests/test_retail_scale.py`` was a registry: its ``ceiling`` fixture was the only way to a
build where most derived styles exist, so each feature's guard over the ceiling build was a test
appended to that one file, and the open PRs of 2026-10-25 (synth#671 to #674) conflicted in all 6
pairs. A feature's guard is now ``tests/test_retail_scale_<topic>_<issue>.py``, a file of its own
that takes the build from here::

    from retail_ceiling import ceiling_build

    @pytest.fixture(scope="module")
    def ceiling():
        return ceiling_build()

``retail_figures.ceiling`` builds it once for the run (in CI, once in the ``ceiling-catalogue``
job, and each worker loads that), so a test never builds past the ceiling itself
(``tests/test_ceiling_artifact_539.py``). A test reads it and never edits it: every file in a
worker shares the one object.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import retail_figures, scale


def ceiling_build() -> scale.Scaled:
    """Every template exhausted: the build where most derived styles exist (seed 0)."""
    return retail_figures.ceiling()
