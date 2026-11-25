"""No test file weighs over 3 minutes in the weights table, or it has a reason on file (#1035).

A module's tests stay on one xdist worker (``--dist loadgroup``), so the heaviest file is the
floor of its shard's time, and a file that builds what the shared catalogues already hold (the
ceiling-catalogue job's ceiling and 100K files) pays for it in every run that selects it. The
table is ``scripts/ci_shard_weights.json``, refreshed from a green run's junit reports
(docs/ci-sharding.md); it holds the seconds the runners of that run measured.

* every file over :data:`FILE_BUDGET_SECONDS` names its reason in :data:`REASONS`;
* every reason names a file still over it, so a reason goes when its file is cut and the table is
  refreshed, and a new heavy file is never excused by an old line.

It times nothing: it reads the committed table.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WEIGHTS = REPO / "scripts" / "ci_shard_weights.json"

#: Three minutes of the weights' seconds: the issue's target for one test file.
FILE_BUDGET_SECONDS = 180.0

#: Why each file over the budget is over it. The seconds are the table's (run 45347596547, the
#: full selection of #1227, on the self-hosted runners). A file #1035 cut keeps its line until a
#: refresh measures the cut; then the line goes, or says what is left.
REASONS = {
    "tests/test_merge_pr.py": (
        "1548 s: each case clones the repository and runs a real build of scripts/merge_pr.sh, "
        "which gen_train still calls for a conflicted PR. Selected only by a change to the merge "
        "path (#1037) and split over every shard (SPLIT_FILES)."
    ),
    "tests/test_merge_pr_github_ci_348.py": (
        "377 s: as tests/test_merge_pr.py, the --github-ci mode of the same script. Selected only "
        "by a change to the merge path (#1037) and split over every shard."
    ),
    "tests/test_type_seam.py": (
        "246 s: it builds the small catalogue whole once per worker, and again for each left-out, "
        "resized and edited case, since the difference between two builds is what it tests."
    ),
    "tests/test_ci_select_495.py": (
        "211 s before #1035's one search of each text per changed file (six of its tests took 23 "
        "to 36 s, selecting for many paths on the whole tree); the next refresh measures it."
    ),
    "tests/test_merge_pr_local_ci_guard_366.py": (
        "194 s: as tests/test_merge_pr.py, the --local-ci guard of the same script."
    ),
}


def _weights() -> dict[str, float]:
    return json.loads(WEIGHTS.read_text(encoding="utf-8"))


def over_budget(weights: dict[str, float]) -> dict[str, float]:
    return {name: s for name, s in sorted(weights.items()) if s > FILE_BUDGET_SECONDS}


def unexcused(weights: dict[str, float], reasons: dict[str, str]) -> dict[str, float]:
    """The files over the budget with no reason, and their seconds."""
    return {name: s for name, s in over_budget(weights).items() if name not in reasons}


def test_every_file_over_the_budget_has_a_reason() -> None:
    """Guard. Metric: each unexcused file and its seconds, in the message."""
    missing = unexcused(_weights(), REASONS)
    assert missing == {}, (
        f"over {FILE_BUDGET_SECONDS:.0f} s with no reason in REASONS: {missing}. Share the "
        "build it makes (tests/retail_ceiling.py, tests/retail_templates.py, "
        "tests/shared_builds.py) or split the file; a reason is for a cost that stays."
    )


def test_every_reason_names_a_file_still_over_the_budget() -> None:
    stale = sorted(set(REASONS) - set(over_budget(_weights())))
    assert stale == [], f"under {FILE_BUDGET_SECONDS:.0f} s now, or gone, drop the reason: {stale}"


def test_a_heavy_file_with_no_reason_is_caught() -> None:
    """The guard bites: a planted 200 s file is named, a 180 s one is not."""
    planted = {**_weights(), "tests/test_planted_heavy.py": 200.0, "tests/test_at_budget.py": 180.0}
    assert unexcused(planted, REASONS) == {"tests/test_planted_heavy.py": 200.0}
