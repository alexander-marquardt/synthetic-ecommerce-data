"""Mutation rows for the runner reservation: main push, batch dispatch, first PR (agent-ops#189).

The batch dispatch is #1031; a red main's fix PR and a ci-first PR are #1027.

Each row plants one defect in the ``runs-on`` expression of one job in ``ci.yaml`` and names the
test that must go red. Found by ``mutation_row.discover``; ``--only "main runner:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import Row

PREFIX = "main runner"

_T = "tests/test_ci_runs_on_596.py::test_every_job_runs_on_the_one_expression"
# The routing rows evaluate the lint job's expression, so a defect planted there turns them red.
_ROUTE = (
    "tests/test_ci_runs_on_596.py::"
    "test_a_push_a_batch_dispatch_or_a_first_pull_request_asks_for_the_reserved_runners"
)
_HEAD = (
    "${{ vars.SYNTH_CI_SELF_HOSTED == 'true' && (github.event_name != 'pull_request' || "
    "github.event.pull_request.head.repo.full_name == github.repository) && "
)
_TITLE = "startsWith(github.event.pull_request.title, 'fix(main-red)')"
_FIX = "contains(github.event.pull_request.labels.*.name, 'main-red-fix')"
_FIRST = "contains(github.event.pull_request.labels.*.name, 'ci-first')"
_PR = "(github.event_name == 'pull_request' && (" + _TITLE + " || " + _FIX + " || " + _FIRST + "))"
_PUSH_OR_BATCH = (
    "github.event_name == 'push' || (github.event_name == 'workflow_dispatch' && "
    "startsWith(github.ref_name, 'ci/batch-'))"
)
_EVENT = "(" + _PUSH_OR_BATCH + " || " + _PR + ")"
_PICK = "fromJSON(" + _EVENT + " && vars.SYNTH_CI_MAIN_RUNNER == 'true' && "
_MAIN = '\'["self-hosted","synth-ci-main"]\''
_POOL = '\'["self-hosted","synth-ci"]\''
# `lint:` is the first job and `runs-on:` follows it directly, so its line is unique in the file.
_TESTS = "    name: tests (${{ matrix.shard }})\n    runs-on: " + _HEAD
_LINT = "  lint:\n    runs-on: " + _HEAD


def _row(name, old, new, prop, test=_T) -> Row:
    return Row(name, ".github/workflows/ci.yaml", old, new, test, prop, ".")


def rows() -> list[Row]:
    return [
        _row(
            "the push gate is dropped",
            _LINT + _PICK,
            _LINT + "fromJSON(vars.SYNTH_CI_MAIN_RUNNER == 'true' && ",
            "an ordinary pull request never asks for the reserved runners",
        ),
        _row(
            "the variable gate is dropped",
            _LINT + _PICK,
            _LINT + "fromJSON(" + _EVENT + " && ",
            "the repository variable is the switch for the reservation",
        ),
        _row(
            "the batch dispatch is dropped",
            _LINT + _PICK,
            _LINT + _PICK.replace(_PUSH_OR_BATCH, "github.event_name == 'push'"),
            "the merge train's batch run asks for the reserved runners (#1031)",
        ),
        _row(
            "every dispatch asks for the reserved runners",
            _LINT + _PICK,
            _LINT + _PICK.replace("'ci/batch-'", "''"),
            "merge_pr.sh's dispatch on ci/merge-<N> keeps the shared pool (#1031)",
        ),
        _row(
            "the main label is misspelt",
            _LINT + _PICK + _MAIN,
            _LINT + _PICK + _MAIN.replace("main", "mian"),
            "the label names the runners the VM registers",
        ),
        _row(
            "the pool is the fallback no more",
            _LINT + _PICK + _MAIN + " || " + _POOL,
            _LINT + _PICK + _MAIN + " || " + _MAIN,
            "everything but a main push stays on the shared pool",
        ),
        _row(
            "one job never asks for the reserved runners",
            _TESTS + _PICK,
            _TESTS + "fromJSON(false && ",
            "every job of a main run asks for the reserved runners",
        ),
        _row(
            "the fix(main-red) title is dropped",
            _LINT + _PICK,
            _LINT + _PICK.replace(_TITLE + " || ", ""),
            "a red main's fix titled fix(main-red) asks for the reserved runners (#1027)",
            _ROUTE,
        ),
        _row(
            "the main-red-fix label is dropped",
            _LINT + _PICK,
            _LINT + _PICK.replace(" || " + _FIX, ""),
            "a PR labelled main-red-fix asks for the reserved runners (#1027)",
            _ROUTE,
        ),
        _row(
            "the ci-first label is dropped",
            _LINT + _PICK,
            _LINT + _PICK.replace(" || " + _FIRST, ""),
            "a PR labelled ci-first asks for the reserved runners (agent-ops#1876, #1027)",
            _ROUTE,
        ),
        _row(
            "every pull request asks for the reserved runners",
            _LINT + _PICK,
            _LINT + _PICK.replace(_PR, "github.event_name == 'pull_request'"),
            "a PR with another label or title keeps the shared pool (#1027)",
            _ROUTE,
        ),
        _row(
            "any title containing fix(main-red) asks",
            _LINT + _PICK,
            _LINT + _PICK.replace(_TITLE, _TITLE.replace("startsWith", "contains")),
            "only a title that starts fix(main-red) is a red main's fix (#1027)",
            _ROUTE,
        ),
    ]
