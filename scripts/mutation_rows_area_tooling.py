"""Mutation rows for the release build's ceiling default, the commit-message check, the local CI workers, the merge script and the red-commit proof.

Moved out of ``mutation_check.py`` without a change to any row (#363): each row keeps its name,
so ``--only`` filters behave as before. ``mutation_row.discover`` finds this file by glob; its
``PREFIX`` only labels the file, because each name below is already the whole name.
"""

from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- the release build defaults to the ceiling (gen#536) ----
    Mutation(
        "release default: the export step asks for a number past the ceiling",
        ".github/workflows/release.yaml",
        'scale.py --skus "${RELEASE_SKUS:-ceiling}"',
        'scale.py --skus "${RELEASE_SKUS:-10000000}"',
        "tests/test_no_derived_files_536.py -k 'defaults_to_the_ceiling and export'",
        "",
        "the tag build asks for the ceiling",
        root=".",
    ),
    Mutation(
        "release default: the image step asks for a number past the ceiling",
        ".github/workflows/release.yaml",
        'image_release.py --skus "${RELEASE_SKUS:-ceiling}"',
        'image_release.py --skus "${RELEASE_SKUS:-10000000}"',
        "tests/test_no_derived_files_536.py -k 'defaults_to_the_ceiling and image'",
        "",
        "the image build asks for the ceiling",
        root=".",
    ),
    # ---- the commit-message check masks the agent-instructions file name (gen#117) ----
    Mutation(
        "commit msg: the file name is no longer masked before matching",
        "scripts/check_commit_msg.py",
        "    return _AGENT_FILE.sub(_MASK, text)",
        "    return text",
        "tests/test_commit_msg_check.py -k test_the_agent_file_name_passes",
        "A",
        "the agent-instructions file name passes",
        root=".",
    ),
    Mutation(
        "commit msg: the mask swallows the whole line, vendor prose with it",
        "scripts/check_commit_msg.py",
        '_AGENT_FILE = re.compile(r"(?<![\\w.-])CLAUDE\\.md(?![\\w-])")',
        '_AGENT_FILE = re.compile(r"^.*(?<![\\w.-])CLAUDE\\.md(?![\\w-]).*$", re.MULTILINE)',
        "tests/test_commit_msg_check.py -k prose-before-name",
        "B",
        "a vendor name beside the file name still fails",
        root=".",
    ),
    Mutation(
        "commit msg: a glued prefix counts as the file name",
        "scripts/check_commit_msg.py",
        '_AGENT_FILE = re.compile(r"(?<![\\w.-])CLAUDE',
        '_AGENT_FILE = re.compile(r"CLAUDE',
        "tests/test_commit_msg_check.py -k glued-prefix",
        "B",
        "only the exact file name is masked",
        root=".",
    ),
    Mutation(
        "commit msg: a longer extension counts as the file name",
        "scripts/check_commit_msg.py",
        '\\.md(?![\\w-])")',
        '\\.md")',
        "tests/test_commit_msg_check.py -k longer-extension",
        "B",
        "only the exact file name is masked",
        root=".",
    ),
    Mutation(
        "commit msg: the mask is matched case-blind, so a lower-case name is masked",
        "scripts/check_commit_msg.py",
        "    return _AGENT_FILE.sub(_MASK, text)",
        "    return re.sub(_AGENT_FILE.pattern, _MASK, text, flags=re.IGNORECASE)",
        "tests/test_commit_msg_check.py -k lowercase-name",
        "B",
        "only the exact file name is masked",
        root=".",
    ),
    Mutation(
        "commit msg: the mask is applied to every row, not the vendor-name row alone",
        "scripts/check_commit_msg.py",
        "pattern.search(masked if label == _MASKED_LABEL else text)",
        "pattern.search(masked)",
        "tests/test_commit_msg_check.py -k names-file",
        "B",
        "a shape row still reads the file name as the tool named",
        root=".",
    ),
    # ---- the local CI runs the suite on several workers, bounded by memory (gen#348) ----
    Mutation(
        "ci workers: the emitted steps stop carrying the xdist options",
        "scripts/local_ci_jobs.py",
        "    lines.append(\n        'export PYTEST_ADDOPTS=",
        "    (lambda _: None)(\n        'export PYTEST_ADDOPTS=",
        "tests/test_ci_tests_job_parallel_348.py -k runs_pytest_on_several_workers",
        "",
        "the tests job runs pytest on several workers",
        root=".",
    ),
    Mutation(
        "ci workers: the workers no longer keep a module together",
        "scripts/local_ci_jobs.py",
        'DIST = "loadgroup"',
        'DIST = "load"',
        "tests/test_ci_tests_job_parallel_348.py -k runs_pytest_on_several_workers",
        "",
        "the workers are grouped by module",
        root=".",
    ),
    Mutation(
        "ci workers: memory stops bounding the count",
        "scripts/local_ci_jobs.py",
        "    return max(MIN_WORKERS, min(cores, by_memory))",
        "    return max(MIN_WORKERS, cores)",
        "tests/test_ci_tests_job_parallel_348.py -k cores_or_what_the_memory_allows",
        "",
        "the worker count is bounded by memory",
        root=".",
    ),
    Mutation(
        "ci workers: the count ignores the cores",
        "scripts/local_ci_jobs.py",
        "    return max(MIN_WORKERS, min(cores, by_memory))",
        "    return max(MIN_WORKERS, by_memory)",
        "tests/test_ci_tests_job_parallel_348.py -k cores_or_what_the_memory_allows",
        "",
        "the worker count is bounded by cores",
        root=".",
    ),
    Mutation(
        "ci workers: the floor drops to the serial run",
        "scripts/local_ci_jobs.py",
        "MIN_WORKERS = 2",
        "MIN_WORKERS = 1",
        "tests/test_ci_tests_job_parallel_348.py -k cores_or_what_the_memory_allows",
        "",
        "never fewer than two workers",
        root=".",
    ),
    Mutation(
        "ci workers: a worker is budgeted below what it was measured to use",
        "scripts/local_ci_jobs.py",
        "WORKER_MB = 4500",
        "WORKER_MB = 3000",
        "tests/test_ci_tests_job_parallel_348.py -k budget_per_worker_is_above",
        "",
        "the budget is above the largest worker measured",
        root=".",
    ),
    Mutation(
        "ci workers: unreadable memory gives every core",
        "scripts/local_ci_jobs.py",
        "    if available is None:\n        return MIN_WORKERS",
        "    if available is None:\n        return cores",
        "tests/test_ci_tests_job_parallel_348.py -k cannot_be_read_gives_the_floor",
        "",
        "unreadable memory gives the floor",
        root=".",
    ),
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
    Mutation(
        "ci workers: a module's tests scatter over the workers",
        "tests/xdist_groups.py",
        "    return str(module.__name__)",
        "    return None",
        "tests/test_ci_tests_job_parallel_348.py -k share_a_group",
        "",
        "a module's tests share a group",
        root=".",
    ),
    Mutation(
        "ci workers: the collection hook stops marking the tests",
        "tests/conftest.py",
        "            item.add_marker(pytest.mark.xdist_group(group))",
        "            pass",
        "tests/test_ci_tests_job_parallel_348.py -k collection_hook_marks",
        "",
        "each test carries its module's group",
        root=".",
    ),
    Mutation(
        "ci workers: a module that asks to spread is grouped anyway",
        "tests/xdist_groups.py",
        '    if getattr(module, "XDIST_SPREAD", False):\n        return None\n',
        "",
        "tests/test_ci_tests_job_parallel_348.py -k share_a_group",
        "",
        "a spread module is not grouped",
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
                'true || return 1',
                'tests/test_merge_pr.py::test_a_local_ci_red_on_another_test_alone_is_not_regenerated',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: a red with no FAILED line counts as freshness",
                '[ -n "$ids" ] || return 1',
                'true || return 1',
                'tests/test_merge_pr.py::test_a_red_with_no_pytest_failure_line_is_not_taken_for_a_stale_golden',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: every red is regenerated",
                'only_stale_generated_files_red ||\n    die',
                'true ||\n    die',
                ('tests/test_merge_pr.py::test_a_local_ci_red_on_another_test_alone_is_not_regenerated', 'tests/test_merge_pr.py::test_a_red_with_no_pytest_failure_line_is_not_taken_for_a_stale_golden'),
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: only the first red job is read",
                '  for job in $local_ci_failed; do\n    ids=',
                '  for job in $(set -- $local_ci_failed; echo $1); do\n    ids=',
                'tests/test_merge_pr.py::test_a_freshness_red_beside_a_red_job_that_is_not_pytest_is_not_regenerated',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: a second red does not stop the merge",
                '$run_ci ||\n    die "$ci_name is red on $final_sha after the golden regeneration',
                '$run_ci ||\n    echo "$ci_name is red on $final_sha after the golden regeneration',
                'tests/test_merge_pr.py::test_a_golden_that_is_still_red_after_the_regeneration_is_regenerated_once_only',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: an empty regeneration is committed",
                'if git -C "$work" diff --cached --quiet; then\n    die "a golden freshness',
                'if false; then\n    die "a golden freshness',
                'tests/test_merge_pr.py::test_a_freshness_red_a_rebuild_does_not_change_is_not_merged',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: the regeneration commit message",
                '-m "regenerate golden on main"',
                '-m "wip"',
                'tests/test_merge_pr.py::test_a_local_ci_red_that_is_only_the_golden_freshness_test_is_regenerated_and_merged',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: the checked sha is not moved to the regenerated commit",
                '  final_sha=$(git -C "$work" rev-parse HEAD)\n  echo "5a.',
                '  echo "5a.',
                'tests/test_merge_pr.py::test_a_local_ci_red_that_is_only_the_golden_freshness_test_is_regenerated_and_merged',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: the regenerated commit is not pushed",
                'if [ "$final_sha" != "$pushed_sha" ]; then',
                'if false; then',
                'tests/test_merge_pr.py::test_a_local_ci_red_that_is_only_the_golden_freshness_test_is_regenerated_and_merged',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: a dry run does not regenerate",
                '    run_local_ci_regenerating\n    echo "5. every local CI job is green on $final_sha"\n  elif',
                '    run_local_ci\n    echo "5. every local CI job is green on $final_sha"\n  elif',
                'tests/test_merge_pr.py::test_a_dry_run_regenerates_the_golden_but_pushes_and_merges_nothing',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: the first run's log is not kept",
                'mv -f "$(local_ci_log "$job")" "$(local_ci_log "$job").before-regenerate"',
                'rm -f "$(local_ci_log "$job")"',
                'tests/test_merge_pr.py::test_a_local_ci_red_that_is_only_the_golden_freshness_test_is_regenerated_and_merged',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: the drift test is not a freshness test",
                '  tests/test_prism_field_map_drift.py::test_committed_field_map_matches_a_fresh_derivation\n',
                '',
                'tests/test_merge_pr.py::test_the_stale_yaml_signature_of_the_incident_is_regenerated',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: the stats test is not a freshness test",
                '  tests/test_catalog_golden.py::test_stats_reports_the_catalog_that_was_committed\n',
                '',
                'tests/test_merge_pr.py::test_a_red_on_the_field_map_or_the_stats_freshness_test_is_regenerated',
                'a stale golden is regenerated once, on a green second run (#440)',
            ),
            (
                "merge_pr: the regeneration stages nothing",
                '  rebuild_generated\n  stage_generated\n  if git',
                '  rebuild_generated\n  if git',
                'tests/test_merge_pr.py::test_a_local_ci_red_that_is_only_the_golden_freshness_test_is_regenerated_and_merged',
                'a stale golden is regenerated once, on a green second run (#440)',
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
    # ---- the red-commit proof judges the commits that declare (#11680) ------
    # Every name starts "red_commit_proof:", so `--only "red_commit_proof:"` re-runs it.
    Mutation(
        "red_commit_proof: a merge commit's trailer is judged",
        "scripts/red_commit_proof.py",
        '"rev-list", "--reverse", "--no-merges", args.spec',
        '"rev-list", "--reverse", args.spec',
        "tests/test_red_commit_proof_11680.py::"
        "test_a_merge_commit_is_never_judged_whatever_its_message_declares",
        "",
        "only the branch's own commits are judged, not a merge of main",
        root=".",
    ),
    Mutation(
        "red_commit_proof: the grandfather test is turned round",
        "scripts/red_commit_proof.py",
        '"--is-ancestor", cutoff, sha, check=False).returncode == 1',
        '"--is-ancestor", cutoff, sha, check=False).returncode == 0',
        (
            "tests/test_red_commit_proof_11680.py::"
            "test_a_red_commit_before_the_cutoff_may_fail_on_anything[StopIteration]",
            "tests/test_red_commit_proof_11680.py::"
            "test_a_red_commit_after_the_cutoff_that_fails_on_stop_iteration_is_refused",
        ),
        "",
        "a commit before the cutoff is grandfathered and one after it is not",
        root=".",
    ),
    Mutation(
        "red_commit_proof: a cutoff the clone lacks grandfathers",
        "scripts/red_commit_proof.py",
        "        return False\n    return _git(repo, \"merge-base\"",
        "        return True\n    return _git(repo, \"merge-base\"",
        "tests/test_red_commit_proof_11680.py::"
        "test_an_exception_that_is_not_an_assertion_is_refused",
        "",
        "a cutoff that is not in the clone grandfathers nothing",
        root=".",
    ),
]

# Found by ``mutation_row.discover``: the label of this file; the rows carry their own names.
PREFIX = "area: tooling"


def rows() -> list[Mutation]:
    return MUTATIONS
