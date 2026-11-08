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
# The flow is below: take the lock, fetch, merge main into a work tree, run CI on that tree,
# squash. Why each step is there, and every environment knob: docs/merge-pr.md. The steps'
# code is in scripts/merge_pr/, and a step's number here is its number there.
set -euo pipefail

die() {
  echo "merge_pr.sh: $*" >&2
  exit 1
}
# A step's start, timed, on stderr: the log of a test that times out names the step (#912).
started() { echo "merge_pr.sh: $(date -u +%Y-%m-%dT%H:%M:%SZ) +$((SECONDS - merge_started))s step $1 started: $2" >&2; }

# True when $1 is one of the remaining arguments.
listed() {
  local want=$1 item
  shift
  for item in "$@"; do [ "$item" = "$want" ] && return 0; done
  return 1
}

here=$(cd "$(dirname "$0")/.." && pwd)
# Every command the local CI runs goes through this (#366): one local CI run at a time on
# the machine, and the run's whole process tree held to workers x 4,500 MB.
# --project, not --directory: the latter moves the job out of the merged tree ($work) into this checkout.
guarded() { uv run -q --locked --project "$here" python "$here/scripts/local_ci_guard.py" "$@"; }
for part in config lock tree ci land; do
  # shellcheck source=/dev/null
  . "$here/scripts/merge_pr/$part.sh"
done

merge_started=$SECONDS
merge_started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
dry_run=0
local_ci=0
github_ci=0
[ "${GEN_LOCAL_CI:-}" = 1 ] && local_ci=1
[ "${GEN_GITHUB_CI:-}" = 1 ] && github_ci=1
label=""
case "${1:-}" in
  --print-checks) printf '%s\n' "${CHECKS[@]}"; exit 0 ;;
  --print-generated) printf '%s\n' "${GENERATED[@]}"; exit 0 ;;
  --print-freshness) printf '%s\n' "${FRESHNESS_TESTS[@]}"; exit 0 ;;
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

# The lock comes before the PR is read: a run that waited merges the main that run left.
if [ "$dry_run" -eq 0 ]; then acquire_merge_lock; fi

# 0. Refuse what can never merge, before anything is cloned.
started 0 "read #$pr"
fields=$(gh pr view "$pr" -R "$slug" \
  --json state,isCrossRepository,headRefName,headRefOid,baseRefName,isDraft \
  --jq '[.state, (.isCrossRepository|tostring), .headRefName, .headRefOid, .baseRefName, (.isDraft|tostring)] | @tsv')
IFS=$'\t' read -r state cross head_ref head_sha base_ref draft <<<"$fields"
[ "$state" = OPEN ] || die "#$pr is $state, not OPEN"
# GitHub refuses to merge a draft, and learns it only at step 6: after the clone, the build
# and the CI wait (about 45 minutes, #70). Say so before any of that.
[ "$draft" = false ] || die "#$pr is a draft; mark it ready first"
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
  release_merge_lock
}
trap cleanup EXIT

started clone "clone $head_ref and fetch $base_ref"
git clone -q --branch "$head_ref" "$origin_url" "$work"
[ "$(git -C "$work" rev-parse HEAD)" = "$head_sha" ] ||
  die "#$pr head moved while cloning; re-run"
git -C "$work" fetch -q origin "$base_ref"
base_sha=$(git -C "$work" rev-parse "origin/$base_ref")
echo "#$pr: head $head_sha, $base_ref $base_sha"

merge_main_into_head
rebuild_merged_tree
check_merged_tree

final_sha=$(git -C "$work" rev-parse HEAD)
pushed_sha=$head_sha
if [ "$dry_run" -eq 1 ]; then
  dry_run_ci_and_report
  exit 0
fi

if [ "$github_ci" -eq 1 ]; then
  # With --github-ci the push waits for the green run: a red tree never lands on the PR.
  run_local_ci_regenerating
  echo "5. every GitHub CI job is green on $final_sha"
  push_merged_tree
elif [ "$local_ci" -eq 1 ]; then
  push_merged_tree
  run_local_ci_and_push_regenerated
else
  push_merged_tree
  wait_for_pr_checks
fi
squash_merge
