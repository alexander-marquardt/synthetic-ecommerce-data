"""Mutation rows for the local CI guard's memory ceiling and lock (gen#366).

Each row plants one defect on a changed line of ``local_ci_guard.py`` or of the lines of
``merge_pr.sh`` that run the local CI through it, and names the test that must go red.
Found by ``mutation_row.discover``; ``--only "local ci guard:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import Row

PREFIX = "local ci guard"

_G = "tests/test_local_ci_guard_366.py"
_M = "tests/test_merge_pr_local_ci_guard_366.py"
_GUARD = "local_ci_guard.py"
_MERGE = "merge_pr.sh"


def _row(name, file, old, new, test, prop) -> Row:
    return Row(name, file, old, new, test, prop, "scripts")


def rows() -> list[Row]:
    return [
        _row(
            "the ceiling is never reached",
            _GUARD,
            "if peak > ceiling:",
            "if peak > ceiling * 1000:",
            f"{_G}::test_a_command_that_passes_the_ceiling_is_stopped_and_fails",
            "a command past its ceiling is stopped",
        ),
        _row(
            "the ceiling is one worker's",
            _GUARD,
            "return workers * WORKER_MB",
            "return WORKER_MB",
            f"{_G}::test_the_ceiling_is_the_workers_times_the_budget_of_one_worker",
            "the ceiling is drawn for every worker",
        ),
        _row(
            "only the first process is measured",
            _GUARD,
            "if pid not in members and (ppid in members or pgid == root):",
            "if False:",
            f"{_G}::test_a_descendant_the_command_started_counts_toward_the_ceiling",
            "the whole tree under the command is measured",
        ),
        _row(
            "the lock is never taken",
            _GUARD,
            "fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)",
            "pass",
            (
                f"{_G}::test_a_second_run_waits_for_the_first_and_then_runs",
                f"{_G}::test_a_wait_that_runs_out_refuses_and_names_the_holder",
            ),
            "a second local CI run waits for the first",
        ),
        _row(
            "the guard's worker count is not handed on",
            _GUARD,
            "child_env[WORKERS_ENV] = str(workers)",
            'child_env[WORKERS_ENV] = "99"',
            f"{_G}::test_an_unset_worker_count_is_handed_to_the_command",
            "the run's -n is the one the ceiling was drawn for",
        ),
        _row(
            "a local CI job runs outside the guard",
            _MERGE,
            "      guarded --notice-fd 3 -- bash --noprofile",
            "      bash --noprofile",
            f"{_M}::test_a_local_job_that_passes_the_memory_ceiling_refuses_the_merge",
            "every job of the local CI is held to the ceiling",
        ),
        _row(
            "the guard moves the job out of the merged tree",
            _MERGE,
            'guarded() { uv run -q --locked --project "$here"',
            'guarded() { uv run -q --locked --directory "$here"',
            f"{_M}::test_a_local_job_runs_in_the_merged_tree_not_where_the_guard_lives",
            "a local CI job runs in the tree it is judging",
        ),
        _row(
            "the step-3 checks run outside the guard",
            _MERGE,
            'if ! guarded -- uv run -q --locked --directory "$work" pytest',
            'if ! uv run -q --locked --directory "$work" pytest',
            f"{_M}::test_the_step_3_checks_past_the_ceiling_refuse_the_merge",
            "the checks of step 3 are held to the ceiling",
        ),
    ]
