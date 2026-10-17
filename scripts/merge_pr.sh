#!/usr/bin/env bash
# Merge a pull request only on a green run of the tree it will make (#48, #54).
#
#     scripts/merge_pr.sh <N>                # merge PR <N>
#     scripts/merge_pr.sh --dry-run <N>      # everything but the push, the CI wait and the merge
#     scripts/merge_pr.sh --print-checks     # the tests it runs, for CI to reuse
#     scripts/merge_pr.sh --print-generated  # the files a conflict is resolved in by rebuilding
#     scripts/merge_pr.sh --print-freshness  # the tests whose red alone is regenerated (#440)
#     scripts/merge_pr.sh --print-ci         # the CI checks a merge waits for
#     scripts/merge_pr.sh --local-ci <N>     # step 5 runs the CI jobs here, not on GitHub
#     scripts/merge_pr.sh --github-ci <N>    # step 5 runs the CI workflow on a throwaway branch (#348)
#     scripts/merge_pr.sh --print-local-ci   # the jobs --local-ci runs (the workflows' jobs)
#
# This repository has no branch protection: on its plan the protection API
# answers 403, so GitHub offers no merge queue and no "require the branch to be
# up to date". A pull request's green is computed against main as of its last
# CI run. When another type PR lands after that run, the two can merge without
# a textual conflict and still leave main red: stats.json and the field-weights
# YAML auto-merge with wrong totals, and two types can take one part-number
# block. Only a tree holding both changes shows it, so this script builds that
# tree before it merges:
#
#   1. clones the PR head into a temporary directory and merges current main
#      into it. A conflict in a file the rebuild rewrites (GENERATED) is left
#      for step 2; any other conflict is refused, for the builder to resolve.
#   2. rebuilds the committed catalog (ecom-generate build --out golden-catalog)
#      and the retail totals (prototypes/retail_drawings/retail_figures.py,
#      golden-retail/stats.json, gen#343), and commits only GENERATED. A file
#      still conflicted, or any other change in the tree, is refused. uv runs
#      --locked, so a stale uv.lock is refused rather than re-locked into the
#      commit.
#   3. runs the drift, golden and seam tests (CHECKS) on that tree, on several
#      pytest workers (local_ci_jobs.py --pytest-options, #348), and
#      refuses a run in which no test passed (pytest exits 0 on all-skipped).
#   4. pushes the merged and rebuilt tree to the PR branch, if it differs from
#      the PR head. Not forced: a head that moved refuses the push.
#   5. waits for every CI check on exactly that commit (the PR's own CI: lint,
#      the whole suite, the commit messages) and refuses unless each is green,
#      or skipped by design (REQUIRED_CI, SKIPPED_BY_DESIGN_CI).
#      With --local-ci (or GEN_LOCAL_CI=1, which makes it the default) step 5
#      waits for nothing on GitHub: GitHub Actions here is billing-blocked, so
#      CI is run locally. It runs, on that same merged-and-rebuilt tree, every
#      job of .github/workflows/*.yml, each as the workflow runs it (the same
#      run: commands, in a bash -eo pipefail shell at the tree's root), found
#      by scripts/local_ci_jobs.py and not by a hand list. Every job runs;
#      each one's verdict, duration and log (outside the clone, named
#      <label>-<job>.log in $MERGE_PR_LOG_DIR, default /tmp; --label sets the
#      label, default the checkout's directory name) is printed; the merge is
#      refused unless every job passed. No GitHub check is read. Each job's
#      pytest runs on several workers, grouped by file (local_ci_jobs.py adds
#      -n and --dist loadgroup; LOCAL_CI_WORKERS sets the count): the suite
#      took 47 to 54 minutes on one core, and merges are serial (#348).
#      A local CI that is red only on the golden freshness tests (FRESHNESS_TESTS:
#      every FAILED or ERROR line of every red job names one of them, and no
#      other job is red) is not handed back for a fixer round (#440): the
#      generated files are rebuilt on the same tree (the step-2 build), committed
#      as "regenerate golden on main", every job runs again, and only a green
#      second run is pushed and merged. Once: a second red stops. Any other red,
#      or a freshness red the rebuild does not change, stops the merge as before.
#      With --github-ci (or GEN_GITHUB_CI=1; #348) step 5 runs the same workflow on
#      GitHub-hosted runners, where the tests job is sharded over several of them
#      (docs/ci-sharding.md): the merged tree is pushed to a throwaway branch
#      ci/merge-<N> (forced: it is ours alone), the workflow is dispatched on it
#      with the base, head and PR number as inputs, and the script waits for the
#      run. Each REQUIRED_CI job must have passed. A red run prints each failing
#      job, its URL and its FAILED/ERROR lines (the same freshness-only
#      regeneration as --local-ci applies, once). The throwaway branch is deleted
#      on every exit. Because the same four tests run in the shards, step 3 is
#      skipped, and step 4 (the push to the PR branch) comes AFTER the green run,
#      so a red tree never lands on the PR. --local-ci stays as the fallback for a
#      GitHub that is down or out of minutes. Either way the end prints the merge's
#      wall time (gen-merge-minutes).
#   6. squash-merges, re-checking before EVERY attempt that main has not moved
#      since step 1 and that the PR head is still the checked commit.
#
# Step 6 narrows the window but cannot close it: GitHub has no compare-and-swap
# on the base. The CI job "main-merged-tree" runs CHECKS on every push to main,
# so a merge that raced (or bypassed this script) shows red on main at once.
set -euo pipefail

#: The tests that see what a textually clean merge can still get wrong.
CHECKS=(
  tests/test_prism_field_map_drift.py
  tests/test_catalog_golden.py
  tests/test_type_seam.py
  tests/test_a_type_module_imported_first.py
)
# tests/test_merge_pr.py narrows them, to prove this script's control flow
# with one fast check; nothing else should set it.
if [ -n "${MERGE_PR_CHECKS:-}" ]; then
  read -r -a CHECKS <<<"$MERGE_PR_CHECKS"
fi

#: Exactly the files `ecom-generate build --out golden-catalog` and the retail
#: rebuild (RETAIL_REBUILD) rewrite, so a conflict in one is resolved by a
#: rebuild. Any other conflict, under golden-catalog/ or not, goes back to the
#: builder. Pinned to the builds by tests/test_merge_pr.py.
GENERATED=(
  golden-catalog/flat.jsonl
  golden-catalog/images.jsonl
  golden-catalog/mapping.flat.json
  golden-catalog/mapping.nested.json
  golden-catalog/nested.jsonl
  golden-catalog/render.jsonl
  golden-catalog/stats.json
  golden-retail/stats.json
  src/prism_synthetic_industrial/data/field_weights/synthetic_industrial_flat.yaml
)

#: The tests whose red means "a generated file is stale", as the test runner names
#: them in its FAILED/ERROR summary lines (parameters dropped). A local CI that is
#: red on these alone is regenerated (#440). Pinned to real tests by tests/test_merge_pr.py.
FRESHNESS_TESTS=(
  tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build
  tests/test_catalog_golden.py::test_golden_directory_holds_exactly_the_build_output
  tests/test_retail_figures_162.py::test_the_committed_figures_are_what_the_build_measures
  tests/test_prism_field_map_drift.py::test_committed_field_map_matches_a_fresh_derivation
  tests/test_catalog_golden.py::test_stats_reports_the_catalog_that_was_committed
)

#: The command that rewrites golden-retail/stats.json (gen#162, gen#343). It
#: is the one retail_figures.py names as REBUILD, which tests/test_merge_pr.py
#: pins. The retail build is the slower half, about 40 s.
RETAIL_REBUILD=(python prototypes/retail_drawings/retail_figures.py)

#: The jobs of .github/workflows/ci.yaml, by the check-run name GitHub gives
#: them (a matrix job's name carries its shard: ``tests (3)``, and a required name
#: stands for every ``<name> (...)``). A pull request's commit must carry each
#: REQUIRED_CI check, green; a SKIPPED_BY_DESIGN_CI check (a push-only job) may
#: also be skipped. Pinned to the workflow by tests/test_merge_pr.py.
REQUIRED_CI=(lint tests commit-messages file-size red-commit-proof customer-name-check)
SKIPPED_BY_DESIGN_CI=(main-merged-tree)

die() {
  echo "merge_pr.sh: $*" >&2
  exit 1
}

# True when $1 is one of the remaining arguments.
listed() {
  local want=$1 item
  shift
  for item in "$@"; do [ "$item" = "$want" ] && return 0; done
  return 1
}

merge_started=$SECONDS
merge_started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
dry_run=0
local_ci=0
github_ci=0
[ "${GEN_LOCAL_CI:-}" = 1 ] && local_ci=1
[ "${GEN_GITHUB_CI:-}" = 1 ] && github_ci=1
label=""
here=$(cd "$(dirname "$0")/.." && pwd)
case "${1:-}" in
  --print-checks)
    printf '%s\n' "${CHECKS[@]}"
    exit 0
    ;;
  --print-generated)
    printf '%s\n' "${GENERATED[@]}"
    exit 0
    ;;
  --print-freshness)
    printf '%s\n' "${FRESHNESS_TESTS[@]}"
    exit 0
    ;;
  --print-ci)
    printf 'required %s\n' "${REQUIRED_CI[@]}"
    printf 'skipped-by-design %s\n' "${SKIPPED_BY_DESIGN_CI[@]}"
    exit 0
    ;;
  --print-local-ci)
    uv run -q --locked --directory "$here" python "$here/scripts/local_ci_jobs.py" \
      --workflows "$here/.github/workflows" --list
    exit 0
    ;;
esac
while [ $# -gt 1 ]; do
  case "$1" in
    --dry-run) dry_run=1; shift ;;
    --local-ci) local_ci=1; github_ci=0; shift ;;
    --github-ci) github_ci=1; local_ci=0; shift ;;
    --label) [ $# -gt 2 ] || die "--label needs a value"; label=$2; shift 2 ;;
    *) break ;;
  esac
done
[ $# -eq 1 ] && [[ $1 =~ ^[0-9]+$ ]] ||
  die "usage: scripts/merge_pr.sh [--dry-run] [--local-ci | --github-ci] [--label NAME] <PR number>"
pr=$1
[ -n "$label" ] || label=$(basename "$here")

origin_url=$(git -C "$here" remote get-url origin)
slug=$(printf '%s\n' "$origin_url" | sed -E 's#^(https://[^/]+/|git@[^:]+:)##; s#\.git$##')

fields=$(gh pr view "$pr" -R "$slug" \
  --json state,isCrossRepository,headRefName,headRefOid,baseRefName \
  --jq '[.state, (.isCrossRepository|tostring), .headRefName, .headRefOid, .baseRefName] | @tsv')
IFS=$'\t' read -r state cross head_ref head_sha base_ref <<<"$fields"
[ "$state" = OPEN ] || die "#$pr is $state, not OPEN"
[ "$cross" = false ] || die "#$pr comes from a fork; this script pushes to the PR branch"

work=$(mktemp -d "${TMPDIR:-/tmp}/merge-pr-$pr.XXXXXX")
checks_log=$(mktemp "${TMPDIR:-/tmp}/merge-pr-$pr-checks.XXXXXX")
build_log=$(mktemp "${TMPDIR:-/tmp}/merge-pr-$pr-build.XXXXXX")
keep_work=1
ci_branch="ci/merge-$pr"
ci_branch_pushed=0
# shellcheck disable=SC2329  # invoked by the EXIT trap
cleanup() {
  rm -f "$checks_log" "$build_log"
  if [ "$ci_branch_pushed" -eq 1 ]; then
    git -C "$work" push -q origin --delete "$ci_branch" >/dev/null 2>&1 ||
      echo "merge_pr.sh: could not delete the throwaway branch $ci_branch; delete it by hand" >&2
  fi
  if [ "$keep_work" -eq 0 ]; then rm -rf "$work"; else echo "merge_pr.sh: left $work for inspection" >&2; fi
}
trap cleanup EXIT

git clone -q --branch "$head_ref" "$origin_url" "$work"
[ "$(git -C "$work" rev-parse HEAD)" = "$head_sha" ] ||
  die "#$pr head moved while cloning; re-run"
git -C "$work" fetch -q origin "$base_ref"
base_sha=$(git -C "$work" rev-parse "origin/$base_ref")
echo "#$pr: head $head_sha, $base_ref $base_sha"

# 1. Merge current main into the PR head.
conflicted=""
if git -C "$work" merge-base --is-ancestor "$base_sha" HEAD; then
  echo "1. $base_ref is already in the PR head"
elif git -C "$work" merge -q --no-edit -m "Merge $base_ref into $head_ref before merging #$pr" \
  "origin/$base_ref" >/dev/null 2>&1; then
  echo "1. merged $base_ref into the PR head without a conflict"
else
  conflicted=$(git -C "$work" diff --name-only --diff-filter=U)
  [ -n "$conflicted" ] || die "merging $base_ref into #$pr failed without a conflict (git identity?)"
  by_hand=""
  while IFS= read -r path; do
    listed "$path" "${GENERATED[@]}" || by_hand+="$path "
  done <<<"$conflicted"
  if [ -n "$by_hand" ]; then
    git -C "$work" merge --abort
    keep_work=0
    die "merging $base_ref into #$pr conflicts outside the generated files; merge it into the branch and resolve by hand: $by_hand"
  fi
  echo "1. merged $base_ref; conflicts only in generated files, left for the rebuild:"
  printf '%s\n' "$conflicted" | sed 's/^/     /'
fi

# Rebuild every generated file on the tree at $work. Two types on one
# part-number block are refused here, naming both.
rebuild_generated() {
  local build_rc=0 retail_rc=0
  uv run -q --locked --directory "$work" ecom-generate build --out golden-catalog \
    >/dev/null 2>"$build_log" || build_rc=$?
  cat "$build_log" >&2
  if [ "$build_rc" -ne 0 ]; then
    # A dropped lookup is not the tree's fault (#178): say so apart from the refusal.
    if grep -qiE 'dns error|failed to (lookup|fetch)|error sending request|network connectivity' "$build_log"; then
      echo "merge_pr.sh: the build failed on the network, not on the tree; retry when it is reachable (UV_OFFLINE=1 builds from uv's cache)" >&2
    fi
    die "the build refuses the merged tree of #$pr (the reason is above); NOT pushed, NOT merged"
  fi
  # The retail totals (golden-retail/stats.json) move with every retail PR as the
  # catalog's do, and conflict the same way; rebuild them on the same merged tree.
  uv run -q --locked --directory "$work" "${RETAIL_REBUILD[@]}" \
    >/dev/null 2>"$build_log" || retail_rc=$?
  cat "$build_log" >&2
  [ "$retail_rc" -eq 0 ] ||
    die "the retail rebuild refuses the merged tree of #$pr (the reason is above); NOT pushed, NOT merged"
}

# 2. Rebuild the committed catalog on the merged tree.
rebuild_generated
if [ -n "$conflicted" ]; then
  while IFS= read -r path; do
    if grep -q '^<<<<<<< ' "$work/$path"; then
      die "$path still holds conflict markers after the rebuild, so the rebuild did not write it; NOT pushed, NOT merged"
    fi
  done <<<"$conflicted"
fi
# Stage the generated files; the rebuild may change nothing else.
stage_generated() {
  local stray
  git -C "$work" add -- "${GENERATED[@]}"
  stray=$(git -C "$work" status --porcelain | grep -v '^[MADRC] ' || true)
  [ -z "$stray" ] ||
    die "the rebuild left changes outside the generated files; NOT pushed, NOT merged:
$stray"
}
stage_generated
if [ -n "$conflicted" ]; then
  git -C "$work" commit -q -m "Merge $base_ref into $head_ref before merging #$pr; generated files rebuilt"
  echo "2. the merge commit holds the rebuilt generated files"
elif ! git -C "$work" diff --cached --quiet; then
  git -C "$work" commit -q -m "Rebuild golden-catalog on the merge of $base_ref into $head_ref (#$pr)"
  echo "2. the rebuild changed: $(git -C "$work" show --stat --format= HEAD | tail -1)"
else
  echo "2. the rebuild changed nothing"
fi

# 3. The checks, on exactly the tree that would be pushed. Pytest exits 0
#    when every test is skipped, so a run must also have passed something.
# On several workers (#348), with the options the local CI jobs get: one source.
# --github-ci skips this: the same files run in the sharded tests job (#348).
if [ "$github_ci" -eq 0 ]; then
read -r -a parallel <<<"$(uv run -q --locked --directory "$here" python \
  "$here/scripts/local_ci_jobs.py" --pytest-options)"
[ "${#parallel[@]}" -gt 0 ] || die "scripts/local_ci_jobs.py --pytest-options printed nothing"
if ! uv run -q --locked --directory "$work" pytest -q -p no:cacheprovider "${parallel[@]}" \
  --junitxml="$checks_log" "${CHECKS[@]}"; then
  die "#$pr is red on the merged tree; NOT pushed, NOT merged"
fi
# The report's counts, not the summary line, which the -q in addopts drops.
count() { sed -nE "s/.*<testsuite[^>]*[[:space:]]$1=\"([0-9]+)\".*/\1/p" "$checks_log" | head -1; }
passed=$(($(count tests) - $(count skipped) - $(count failures) - $(count errors)))
[ "$passed" -gt 0 ] ||
  die "no test passed in the checks on the merged tree of #$pr (all skipped?); NOT pushed, NOT merged"
echo "3. drift, golden and seam tests green on the merged tree"
else
  echo "3. skipped: the drift, golden and seam tests run in the sharded tests job"
fi

# 5 (--local-ci). Every CI job of the workflows, on exactly the tree that
#    would merge. All of them run; any red one refuses.
# Sets local_ci_failed to the red jobs and returns 1 when there are any.
run_local_ci() {
  local jobs job script log started verdict required
  local_ci_failed=""
  jobs=$(uv run -q --locked --directory "$work" python "$here/scripts/local_ci_jobs.py" \
    --workflows "$work/.github/workflows" --list) ||
    die "a workflow job has no local equivalent (the reason is above); NOT merged"
  for required in "${REQUIRED_CI[@]}"; do
    listed "$required" $jobs || die "required check $required is not a job of the workflows; NOT merged"
  done
  for job in $jobs; do
    script=$(uv run -q --locked --directory "$work" python "$here/scripts/local_ci_jobs.py" \
      --workflows "$work/.github/workflows" --emit "$job" --base "$base_sha" --head "$final_sha") ||
      die "job $job has no local equivalent (the reason is above); NOT merged"
    log=$(local_ci_log "$job")
    started=$SECONDS
    # GEN_LOCAL_CI is dropped so a test that runs this script does not recurse.
    if (cd "$work" && env -u GEN_LOCAL_CI bash --noprofile --norc -eo pipefail -c "$script") >"$log" 2>&1; then
      verdict=PASS
    else
      verdict=FAIL
      local_ci_failed+=" $job"
    fi
    echo "   local CI $job: $verdict ($((SECONDS - started))s) log $log"
  done
  [ -z "$local_ci_failed" ]
}

local_ci_log() { echo "${MERGE_PR_LOG_DIR:-/tmp}/$label-$1.log"; }

# 5 (--github-ci, #348). The workflow on GitHub-hosted runners, on exactly the tree
#    that would merge: pushed to the throwaway branch, dispatched with the range
#    its PR jobs read, waited for. Sets local_ci_failed to the red jobs (named as
#    local_ci_log wants them) and returns 1 when there are any; every job's log is
#    in local_ci_log, so the freshness analysis reads it as it reads a local one.
run_github_ci() {
  local started=$SECONDS out run_id="" run_url="" status conclusion jobs_tsv job_id name jstatus \
    jconclusion url safe seen deadline required list_wait
  local_ci_failed=""
  git -C "$work" push -q --force origin "$final_sha:refs/heads/$ci_branch" ||
    die "could not push $final_sha to the throwaway branch $ci_branch; NOT merged"
  ci_branch_pushed=1
  out=$(gh workflow run "${MERGE_PR_WORKFLOW:-ci.yaml}" -R "$slug" --ref "$ci_branch" \
    -f base="$base_sha" -f head="$final_sha" -f pr="$pr" 2>&1) ||
    die "could not dispatch the CI workflow on $ci_branch: $out; NOT merged"
  run_url=$(printf '%s\n' "$out" | grep -Eo 'https://[^ ]+/actions/runs/[0-9]+' | tail -1 || true)
  run_id=${run_url##*/}
  if [ -z "$run_id" ]; then
    # An older gh prints no URL: the run is the newest dispatch of that branch on that sha.
    list_wait=0
    while [ -z "$run_id" ]; do
      run_id=$(gh run list -R "$slug" -w "${MERGE_PR_WORKFLOW:-ci.yaml}" -b "$ci_branch" \
        -e workflow_dispatch -L 10 --json databaseId,headSha \
        --jq "map(select(.headSha == \"$final_sha\")) | .[0].databaseId // empty")
      [ -n "$run_id" ] && break
      [ "$list_wait" -lt "${MERGE_PR_RUN_LOOKUP:-60}" ] ||
        die "the dispatched CI run on $ci_branch ($final_sha) did not appear; NOT merged"
      list_wait=$((list_wait + 5))
      sleep "${MERGE_PR_CI_POLL:-20}"
    done
    run_url="https://github.com/$slug/actions/runs/$run_id"
  fi
  echo "   GitHub CI run $run_url on $final_sha"
  ci_timeout=${MERGE_PR_CI_TIMEOUT:-2400}
  deadline=$((SECONDS + ci_timeout))
  while :; do
    IFS=$'\t' read -r status conclusion < <(gh run view "$run_id" -R "$slug" --json status,conclusion \
      --jq '[.status, (.conclusion // "-")] | @tsv')
    [ "$status" != completed ] || break
    [ "$SECONDS" -lt "$deadline" ] ||
      die "GitHub CI $run_url has not finished after ${ci_timeout}s; NOT merged"
    sleep "${MERGE_PR_CI_POLL:-20}"
  done
  jobs_tsv=$(gh run view "$run_id" -R "$slug" --json jobs \
    --jq '.jobs[] | [.databaseId, .name, .status, (.conclusion // "-"), .url] | @tsv')
  seen=""
  while IFS=$'\t' read -r job_id name jstatus jconclusion url; do
    [ -n "$name" ] || continue
    if [ "$jconclusion" = success ]; then seen+=" ${name%% (*}"; fi
    if [ "$jconclusion" = success ] || { [ "$jconclusion" = skipped ] && listed "${name%% (*}" "${SKIPPED_BY_DESIGN_CI[@]}"; }; then
      continue
    fi
    safe=$(printf '%s' "$name" | tr -c 'A-Za-z0-9._-' '_')
    local_ci_failed+=" $safe"
    gh api "repos/$slug/actions/jobs/$job_id/logs" 2>/dev/null |
      sed -E 's/^[0-9T:.Z-]+ //' >"$(local_ci_log "$safe")" || true
    echo "   GitHub CI $name: $jconclusion $url"
    grep -E '^(FAILED|ERROR) ' "$(local_ci_log "$safe")" | head -40 | sed 's/^/     /' || true
  done <<<"$jobs_tsv"
  for required in "${REQUIRED_CI[@]}"; do
    case " $seen " in
      *" $required "*) ;;
      *) if [ -z "$local_ci_failed" ]; then
           die "required check $required did not pass in the CI run $run_url (jobs seen:${seen:- none}); NOT merged"
         fi ;;
    esac
  done
  echo "   GitHub CI: $conclusion ($((SECONDS - started))s) $run_url"
  [ -z "$local_ci_failed" ] || return 1
  [ "$conclusion" = success ] || die "the CI run $run_url is $conclusion with no failing job to name; NOT merged"
}

# True when every red job of the last run is red on freshness tests alone: it
# printed at least one FAILED/ERROR summary line, and each names a FRESHNESS_TESTS
# test. A red job that printed none (lint, a crash, a collection error) is not.
only_stale_generated_files_red() {
  local job id ids
  for job in $local_ci_failed; do
    ids=$(sed -nE 's/^(FAILED|ERROR) ([^][ ]+).*/\2/p' "$(local_ci_log "$job")" | sort -u)
    [ -n "$ids" ] || return 1
    for id in $ids; do
      listed "$id" "${FRESHNESS_TESTS[@]}" || return 1
    done
  done
}

# The local CI, and, once, the regeneration of the generated files when its only
# red is a stale one (#440). The second run is the whole of it again, on the
# regenerated commit; its red stops the merge whatever it is.
run_local_ci_regenerating() {
  local job run_ci=run_local_ci ci_name="local CI"
  if [ "$github_ci" -eq 1 ]; then run_ci=run_github_ci ci_name="GitHub CI"; fi
  $run_ci && return 0
  only_stale_generated_files_red ||
    die "$ci_name is red on $final_sha (failed:$local_ci_failed); NOT merged"
  echo "   the only red is a stale generated file; rebuilding it on the merged tree"
  for job in $local_ci_failed; do mv -f "$(local_ci_log "$job")" "$(local_ci_log "$job").before-regenerate"; done
  rebuild_generated
  stage_generated
  if git -C "$work" diff --cached --quiet; then
    die "a golden freshness test is red but a rebuild changes nothing (a nondeterministic generator, or the test is red for another reason); NOT merged"
  fi
  git -C "$work" commit -q -m "regenerate golden on main"
  final_sha=$(git -C "$work" rev-parse HEAD)
  echo "5a. regenerated the golden files on the merged tree: $(git -C "$work" show --stat --format= HEAD | tail -1)"
  $run_ci ||
    die "$ci_name is red on $final_sha after the golden regeneration (failed:$local_ci_failed); NOT merged"
}

final_sha=$(git -C "$work" rev-parse HEAD)
pushed_sha=$head_sha
if [ "$dry_run" -eq 1 ]; then
  if [ "$local_ci" -eq 1 ]; then
    run_local_ci_regenerating
    echo "5. every local CI job is green on $final_sha"
  elif [ "$github_ci" -eq 1 ]; then
    run_local_ci_regenerating
    echo "5. every GitHub CI job is green on $final_sha"
  fi
  keep_work=0
  if [ "$final_sha" = "$head_sha" ]; then
    echo "dry run: would wait for every CI check on $head_sha, then squash-merge #$pr at it"
  else
    echo "dry run: would push $final_sha to $head_ref, wait for every CI check on it, then squash-merge #$pr at it"
  fi
  exit 0
fi

# 4. Push the merged tree, if it is not the PR head already. With --github-ci the
#    push waits for the green run, below: a red tree never lands on the PR.
push_merged_tree() {
  if [ "$final_sha" != "$head_sha" ]; then
    git -C "$work" push -q origin "HEAD:refs/heads/$head_ref" ||
      die "the push of $final_sha to $head_ref was refused (has the PR head moved?); NOT merged"
    pushed_sha=$final_sha
    echo "4. pushed $final_sha to $head_ref"
  else
    echo "4. nothing to push"
  fi
}
if [ "$github_ci" -eq 0 ]; then push_merged_tree; fi

# 5. The PR's own CI, on exactly the commit that will merge.
if [ "$github_ci" -eq 1 ]; then
  run_local_ci_regenerating
  echo "5. every GitHub CI job is green on $final_sha"
  push_merged_tree
elif [ "$local_ci" -eq 1 ]; then
  run_local_ci_regenerating
  if [ "$final_sha" != "$pushed_sha" ]; then
    git -C "$work" push -q origin "HEAD:refs/heads/$head_ref" ||
      die "the push of the regenerated $final_sha to $head_ref was refused (has the PR head moved?); NOT merged"
    echo "5b. pushed the regenerated $final_sha to $head_ref"
  fi
  echo "5. every local CI job is green on $final_sha"
else
ci_timeout=${MERGE_PR_CI_TIMEOUT:-3600}
ci_deadline=$((SECONDS + ci_timeout))
while :; do
  runs=$(gh api "repos/$slug/commits/$final_sha/check-runs?per_page=100" \
    --jq '.check_runs[] | [.name, .status, (.conclusion // "")] | @tsv')
  seen=() seen_stems=() pending=""
  while IFS=$'\t' read -r name status conclusion; do
    [ -n "$name" ] || continue
    seen+=("$name")
    seen_stems+=("${name%% (*}")
    if [ "$status" != completed ]; then
      pending+=" $name"
    elif [ "$conclusion" = skipped ]; then
      listed "${name%% (*}" "${SKIPPED_BY_DESIGN_CI[@]}" ||
        die "check $name on $final_sha was skipped, and it is not skipped by design; NOT merged"
    elif [ "$conclusion" != success ]; then
      die "check $name on $final_sha is $conclusion; NOT merged"
    fi
  done <<<"$runs"
  missing=""
  for name in "${REQUIRED_CI[@]}"; do
    listed "$name" ${seen[@]+"${seen[@]}"} || listed "$name" ${seen_stems[@]+"${seen_stems[@]}"} ||
      missing+=" $name"
  done
  [ -n "$pending$missing" ] || break
  [ "$SECONDS" -lt "$ci_deadline" ] ||
    die "CI on $final_sha has not finished after ${ci_timeout}s (still running:${pending:- none}; missing:${missing:- none}); NOT merged"
  sleep "${MERGE_PR_CI_POLL:-30}"
done
echo "5. every CI check on $final_sha is green"
fi

# 6. Merge only the tree that was checked, against the main it was checked
#    on. GitHub recomputes mergeability after a push and refuses until it
#    has, so the merge is retried; main and the head are re-read before each.
for attempt in 1 2 3 4 5 6; do
  now_base=$(git -C "$work" ls-remote origin "refs/heads/$base_ref" | cut -f1)
  [ "$now_base" = "$base_sha" ] ||
    die "$base_ref moved to $now_base since it was merged in; NOT merged. Re-run to check against it"
  now_head=$(git -C "$work" ls-remote origin "refs/heads/$head_ref" | cut -f1)
  [ "$now_head" = "$final_sha" ] ||
    die "$head_ref moved to $now_head since it was checked; NOT merged. Re-run to check it"
  if gh pr merge "$pr" -R "$slug" --squash --match-head-commit "$final_sha"; then
    keep_work=0
    echo "6. squash-merged #$pr at $final_sha"
    merge_seconds=$((SECONDS - merge_started))
    ci_mode=pr-checks
    if [ "$github_ci" -eq 1 ]; then ci_mode=github-ci; elif [ "$local_ci" -eq 1 ]; then ci_mode=local-ci; fi
    printf 'gen-merge-minutes: %d.%d (#%s, %s, %s to %s)\n' "$((merge_seconds / 60))" \
      "$((merge_seconds % 60 * 10 / 60))" "$pr" "$ci_mode" "$merge_started_at" \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    exit 0
  fi
  if [ "$attempt" -lt 6 ]; then sleep "${MERGE_PR_RETRY_SLEEP:-5}"; fi
done
die "gh pr merge refused #$pr six times; the checked tree is pushed, nothing is merged"
