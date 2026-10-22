"""Mutation rows for the main-push runner reservation (agent-ops#189).

Each row plants one defect in the ``runs-on`` expression of one job in ``ci.yaml`` and names the
test that must go red. Found by ``mutation_row.discover``; ``--only "main runner:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import Row

PREFIX = "main runner"

_T = "tests/test_ci_runs_on_596.py::test_every_job_runs_on_the_one_expression"
_HEAD = (
    "${{ vars.SYNTH_CI_SELF_HOSTED == 'true' && (github.event_name != 'pull_request' || "
    "github.event.pull_request.head.repo.full_name == github.repository) && "
)
_PICK = "fromJSON(github.event_name == 'push' && vars.SYNTH_CI_MAIN_RUNNER == 'true' && "
_MAIN = '\'["self-hosted","synth-ci-main"]\''
_POOL = '\'["self-hosted","synth-ci"]\''
# `lint:` is the first job and `runs-on:` follows it directly, so its line is unique in the file.
_TESTS = "    name: tests (${{ matrix.shard }})\n    runs-on: " + _HEAD
_LINT = "  lint:\n    runs-on: " + _HEAD


def _row(name, old, new, prop) -> Row:
    return Row(name, ".github/workflows/ci.yaml", old, new, _T, prop, ".")


def rows() -> list[Row]:
    return [
        _row(
            "the push gate is dropped",
            _LINT + _PICK,
            _LINT + "fromJSON(vars.SYNTH_CI_MAIN_RUNNER == 'true' && ",
            "a pull request never asks for the reserved runners",
        ),
        _row(
            "the variable gate is dropped",
            _LINT + _PICK,
            _LINT + "fromJSON(github.event_name == 'push' && ",
            "the repository variable is the switch for the reservation",
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
    ]
