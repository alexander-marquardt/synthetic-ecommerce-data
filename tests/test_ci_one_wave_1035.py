"""A full run's shards fit the runner slots at once, so the push run on main is one wave (#1035).

Generator CI runs on the Spot VM `alex-prism-generator-ci`, 12 slots (agent-ops
`vm/ci_runner/README.md`, "Two hosts"). At 20 shards, the push run of #1270's merge (run
45773051124) ran 13 shards at once and 7 in a second wave, and took 17.2 min. About 85 s of a
shard is fixed (job setup, pytest start, the worker tail), so more shards than slots costs a second
wave and more fixed seconds. As many shards as slots runs every shard at once. Fewer shards would
leave a slot idle and make each shard longer. The figures are in docs/ci-sharding.md.

It reads the workflow and the deal, and times nothing.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "ci.yaml"

#: The generator CI host's slots, `CI_MAX_JOBS` of `alex-prism-generator-ci` (agent-ops
#: `vm/ci_runner/README.md`). A change there changes this, the matrix and docs/ci-sharding.md.
RUNNER_SLOTS = 12


def test_a_full_run_has_as_many_shards_as_the_runner_has_slots() -> None:
    tests_job = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["tests"]
    shards = tests_job["strategy"]["matrix"]["shard"]
    assert len(shards) == RUNNER_SLOTS, (
        f"{len(shards)} test shards on {RUNNER_SLOTS} runner slots: a push run's shards do not all "
        "start at once (docs/ci-sharding.md, #1035)"
    )
