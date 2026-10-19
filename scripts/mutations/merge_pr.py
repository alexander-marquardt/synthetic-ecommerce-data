"""Mutations that plant a defect in ``scripts/merge_pr.sh``, the serial squash merge and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob and the harness plants each
entry of ``MUTATIONS`` in turn (``--only`` filters by a substring of the name). Moved out of
``scripts/mutation_check.py`` unchanged (gen#539).
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    Mutation(
        "ci workers: the merge check step runs on one worker",
        "scripts/merge_pr.sh",
        'pytest -q -p no:cacheprovider "${parallel[@]}"',
        "pytest -q -p no:cacheprovider",
        "tests/test_ci_tests_job_parallel_348.py -k checks_step_runs_on_the_same_workers",
        "",
        "the merge check step uses the same options",
        root=".",
    ),
    # ---- merge_pr.sh merges only a checked tree (#54) ----------------------
    # Every name starts "merge_pr:", so `--only "merge_pr:"` re-runs them. The
    # round-3 review's four survivors are the first four (the fourth, `--ours`
    # turned `--theirs`, is gone with the side-taking: a generated conflict is
    # now left for the rebuild, whose markers guard is its row here).
    *(
        Mutation(name, "scripts/merge_pr.sh", old, new, tests, "", prop, root=".")
        for name, old, new, tests, prop in (
            (
                "merge_pr: no base re-check before a merge attempt",
                '[ "$now_base" = "$base_sha" ] ||\n    die',
                "true ||\n    die",
                (
                    "tests/test_merge_pr.py::"
                    "test_main_that_moves_during_the_checks_is_not_merged_onto",
                    "tests/test_merge_pr.py::"
                    "test_main_that_moves_between_merge_attempts_is_not_merged_onto",
                ),
                "main is the base the checks ran on, at every merge attempt",
            ),
            (
                "merge_pr: every conflict auto-resolved",
                'listed "$path" "${GENERATED[@]}" || by_hand+=',
                "true || by_hand+=",
                (
                    "tests/test_merge_pr.py::"
                    "test_a_conflict_outside_the_generated_files_is_handed_back",
                    "tests/test_merge_pr.py::"
                    "test_a_conflict_in_a_file_the_build_does_not_write_is_handed_back",
                ),
                "only a conflict the rebuild resolves is resolved by it",
            ),
            (
                "merge_pr: no head-moved check after clone",
                '[ "$(git -C "$work" rev-parse HEAD)" = "$head_sha" ] ||',
                "true ||",
                "tests/test_merge_pr.py::test_a_head_that_moves_while_cloning_is_refused",
                "the tree checked is the head GitHub named",
            ),
            (
                "merge_pr: a generated file the rebuild left conflicted is accepted",
                "    if grep -q '^<<<<<<< ' \"$work/$path\"; then",
                "    if false; then",
                "tests/test_merge_pr.py::"
                "test_a_generated_file_the_rebuild_left_conflicted_is_refused",
                "only a conflict the rebuild resolves is resolved by it",
            ),
            (
                "merge_pr: base re-checked once, not before every attempt",
                '  [ "$now_base" = "$base_sha" ] ||',
                '  [ "$attempt" -gt 1 ] || [ "$now_base" = "$base_sha" ] ||',
                "tests/test_merge_pr.py::"
                "test_main_that_moves_between_merge_attempts_is_not_merged_onto",
                "main is the base the checks ran on, at every merge attempt",
            ),
            (
                "merge_pr: any path under golden-catalog/ counts as generated",
                'listed "$path" "${GENERATED[@]}" || by_hand+=',
                '[[ $path == golden-catalog/* ]] || listed "$path" "${GENERATED[@]}" || by_hand+=',
                "tests/test_merge_pr.py::"
                "test_a_conflict_in_a_file_the_build_does_not_write_is_handed_back",
                "only a conflict the rebuild resolves is resolved by it",
            ),
            (
                "merge_pr: no head re-check before a merge attempt",
                '[ "$now_head" = "$final_sha" ] ||',
                "true ||",
                "tests/test_merge_pr.py::test_a_head_that_moves_with_nothing_to_push_is_not_merged",
                "the head is the commit that was checked, at every merge attempt",
            ),
            (
                "merge_pr: the push is forced",
                'push -q origin "HEAD:refs/heads/$head_ref" ||\n      die "the push of $final_sha',
                'push -q -f origin "HEAD:refs/heads/$head_ref" ||\n      die "the push of $final_sha',
                "tests/test_merge_pr.py::"
                "test_a_head_that_moves_during_the_checks_is_neither_overwritten_nor_merged",
                "the head is the commit that was checked, at every merge attempt",
            ),
            (
                "merge_pr: the push of the regenerated commit is forced",
                'push -q origin "HEAD:refs/heads/$head_ref" ||\n      die "the push of the regenerated',
                'push -q -f origin "HEAD:refs/heads/$head_ref" ||\n      die "the push of the regenerated',
                "tests/test_merge_pr.py::"
                "test_a_head_that_moves_during_the_second_run_is_neither_overwritten_nor_merged",
                "the head is the commit that was checked, at every merge attempt",
            ),
            (
                "merge_pr: any failed id counts as freshness",
                'listed "$id" "${FRESHNESS_TESTS[@]}" || return 1',
                "true || return 1",
                "tests/test_merge_pr.py::test_a_local_ci_red_on_another_test_alone_is_not_regenerated",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: a red with no FAILED line counts as freshness",
                '[ -n "$ids" ] || return 1',
                "true || return 1",
                "tests/test_merge_pr.py::test_a_red_with_no_pytest_failure_line_is_not_taken_for_a_stale_golden",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: every red is regenerated",
                "only_stale_generated_files_red ||\n    die",
                "true ||\n    die",
                (
                    "tests/test_merge_pr.py::test_a_local_ci_red_on_another_test_alone_is_not_regenerated",
                    "tests/test_merge_pr.py::test_a_red_with_no_pytest_failure_line_is_not_taken_for_a_stale_golden",
                ),
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: only the first red job is read",
                "  for job in $local_ci_failed; do\n    ids=",
                "  for job in $(set -- $local_ci_failed; echo $1); do\n    ids=",
                "tests/test_merge_pr.py::test_a_freshness_red_beside_a_red_job_that_is_not_pytest_is_not_regenerated",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: a second red does not stop the merge",
                '$run_ci ||\n    die "$ci_name is red on $final_sha after the golden regeneration',
                '$run_ci ||\n    echo "$ci_name is red on $final_sha after the golden regeneration',
                "tests/test_merge_pr.py::test_a_golden_that_is_still_red_after_the_regeneration_is_regenerated_once_only",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: an empty regeneration is committed",
                'if git -C "$work" diff --cached --quiet; then\n    die "a golden freshness',
                'if false; then\n    die "a golden freshness',
                "tests/test_merge_pr.py::test_a_freshness_red_a_rebuild_does_not_change_is_not_merged",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: the regeneration commit message",
                '-m "regenerate golden on main"',
                '-m "wip"',
                "tests/test_merge_pr.py::test_a_local_ci_red_that_is_only_the_golden_freshness_test_is_regenerated_and_merged",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: the checked sha is not moved to the regenerated commit",
                '  final_sha=$(git -C "$work" rev-parse HEAD)\n  echo "5a.',
                '  echo "5a.',
                "tests/test_merge_pr.py::test_a_local_ci_red_that_is_only_the_golden_freshness_test_is_regenerated_and_merged",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: the regenerated commit is not pushed",
                'if [ "$final_sha" != "$pushed_sha" ]; then',
                "if false; then",
                "tests/test_merge_pr.py::test_a_local_ci_red_that_is_only_the_golden_freshness_test_is_regenerated_and_merged",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: a dry run does not regenerate",
                '    run_local_ci_regenerating\n    echo "5. every local CI job is green on $final_sha"\n  elif',
                '    run_local_ci\n    echo "5. every local CI job is green on $final_sha"\n  elif',
                "tests/test_merge_pr.py::test_a_dry_run_regenerates_the_golden_but_pushes_and_merges_nothing",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: the first run's log is not kept",
                'mv -f "$(local_ci_log "$job")" "$(local_ci_log "$job").before-regenerate"',
                'rm -f "$(local_ci_log "$job")"',
                "tests/test_merge_pr.py::test_a_local_ci_red_that_is_only_the_golden_freshness_test_is_regenerated_and_merged",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: the drift test is not a freshness test",
                "  tests/test_prism_field_map_drift.py::test_committed_field_map_matches_a_fresh_derivation\n",
                "",
                "tests/test_merge_pr.py::test_the_stale_yaml_signature_of_the_incident_is_regenerated",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: the stats test is not a freshness test",
                "  tests/test_catalog_golden.py::test_stats_reports_the_catalog_that_was_committed\n",
                "",
                "tests/test_merge_pr.py::test_a_red_on_the_field_map_or_the_stats_freshness_test_is_regenerated",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: the regeneration stages nothing",
                "  rebuild_generated\n  stage_generated\n  if git",
                "  rebuild_generated\n  if git",
                "tests/test_merge_pr.py::test_a_local_ci_red_that_is_only_the_golden_freshness_test_is_regenerated_and_merged",
                "a stale golden is regenerated once, on a green second run (#440)",
            ),
            (
                "merge_pr: the rebuild runs unlocked",
                'uv run -q --locked --directory "$work" ecom-generate',
                'uv run -q --directory "$work" ecom-generate',
                "tests/test_merge_pr.py::test_a_stale_lock_is_refused_not_relocked_and_committed",
                "the rebuild commits only the generated files",
            ),
            (
                "merge_pr: the rebuild stages everything",
                'git -C "$work" add -- "${GENERATED[@]}"',
                'git -C "$work" add -A',
                "tests/test_merge_pr.py::"
                "test_a_change_the_rebuild_makes_outside_the_generated_files_is_refused",
                "the rebuild commits only the generated files",
            ),
            (
                "merge_pr: a change outside the generated files is left behind",
                '[ -z "$stray" ] ||',
                "true ||",
                "tests/test_merge_pr.py::"
                "test_a_change_the_rebuild_makes_outside_the_generated_files_is_refused",
                "the rebuild commits only the generated files",
            ),
            (
                "merge_pr: a check run in which no test passed is green",
                '[ "$passed" -gt 0 ] ||',
                "true ||",
                "tests/test_merge_pr.py::test_a_check_run_in_which_no_test_passed_is_not_green",
                "a check run is green only when a test passed",
            ),
            (
                "merge_pr: CI read on the PR head, not the pushed commit",
                "commits/$final_sha/check-runs",
                "commits/$head_sha/check-runs",
                "tests/test_merge_pr.py::"
                "test_a_merge_waits_for_every_check_on_the_pushed_tree[head-only]",
                "every CI check on the commit that merges is green",
            ),
            (
                "merge_pr: a failed check is green",
                'elif [ "$conclusion" != success ]; then',
                "elif false; then",
                "tests/test_merge_pr.py::"
                "test_a_merge_waits_for_every_check_on_the_pushed_tree[red]",
                "every CI check on the commit that merges is green",
            ),
            (
                "merge_pr: any skipped check is green",
                'listed "${name%% (*}" "${SKIPPED_BY_DESIGN_CI[@]}" ||',
                "true ||",
                "tests/test_merge_pr.py::"
                "test_a_merge_waits_for_every_check_on_the_pushed_tree[skipped]",
                "every CI check on the commit that merges is green",
            ),
            (
                "merge_pr: a missing required check is not waited for",
                'listed "$name" ${seen[@]+"${seen[@]}"} || listed',
                "true || listed",
                "tests/test_merge_pr.py::"
                "test_a_merge_waits_for_every_check_on_the_pushed_tree[missing]",
                "every CI check on the commit that merges is green",
            ),
            (
                "merge_pr: a running check counts as finished",
                'pending+=" $name"',
                ":",
                "tests/test_merge_pr.py::"
                "test_a_merge_waits_for_every_check_on_the_pushed_tree[pending]",
                "every CI check on the commit that merges is green",
            ),
        )
    ),
]
