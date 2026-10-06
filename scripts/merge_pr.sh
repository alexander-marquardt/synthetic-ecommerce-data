#!/usr/bin/env bash
# Merge a pull request only on a green run of the tree it will make (#48, #54).
#
#     scripts/merge_pr.sh <N>             # merge PR <N>
#     scripts/merge_pr.sh --dry-run <N>   # everything but the push and the merge
#     scripts/merge_pr.sh --print-checks  # the tests it runs, for CI to reuse
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
#      into it. A conflict only in generated output (golden-catalog/ and the
#      field-weights YAML) is resolved by taking the PR's side, because step 2
#      rewrites those files anyway; any other conflict is refused, for the
#      builder to resolve.
#   2. rebuilds the committed catalog: sip-generate build --out golden-catalog.
#   3. runs the drift, golden and seam tests (CHECKS below) on that tree.
#   4. pushes the merged and rebuilt tree to the PR branch, if it differs from
#      the PR head.
#   5. squash-merges, only if every check was green, main has not moved since
#      step 1, and the PR head is still the commit that was checked.
#
# The CI job "main-merged-tree" runs the same CHECKS on every push to main, so
# a merge that bypassed this script shows red on main at once.
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

#: Generated output: a conflict here is resolved by rebuilding, never by hand.
GENERATED_RE='^(golden-catalog/|src/prism_synthetic_industrial/data/field_weights/)'

die() {
  echo "merge_pr.sh: $*" >&2
  exit 1
}

dry_run=0
case "${1:-}" in
  --print-checks)
    printf '%s\n' "${CHECKS[@]}"
    exit 0
    ;;
  --dry-run)
    dry_run=1
    shift
    ;;
esac
[ $# -eq 1 ] && [[ $1 =~ ^[0-9]+$ ]] || die "usage: scripts/merge_pr.sh [--dry-run] <PR number>"
pr=$1

here=$(cd "$(dirname "$0")/.." && pwd)
origin_url=$(git -C "$here" remote get-url origin)
slug=$(printf '%s\n' "$origin_url" | sed -E 's#^(https://[^/]+/|git@[^:]+:)##; s#\.git$##')

fields=$(gh pr view "$pr" -R "$slug" \
  --json state,isCrossRepository,headRefName,headRefOid,baseRefName \
  --jq '[.state, (.isCrossRepository|tostring), .headRefName, .headRefOid, .baseRefName] | @tsv')
IFS=$'\t' read -r state cross head_ref head_sha base_ref <<<"$fields"
[ "$state" = OPEN ] || die "#$pr is $state, not OPEN"
[ "$cross" = false ] || die "#$pr comes from a fork; this script pushes to the PR branch"

work=$(mktemp -d "${TMPDIR:-/tmp}/merge-pr-$pr.XXXXXX")
keep_work=1
# shellcheck disable=SC2329  # invoked by the EXIT trap
cleanup() {
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
if git -C "$work" merge-base --is-ancestor "$base_sha" HEAD; then
  echo "1. $base_ref is already in the PR head"
elif git -C "$work" merge -q --no-edit -m "Merge $base_ref into $head_ref before merging #$pr" \
  "origin/$base_ref" >/dev/null 2>&1; then
  echo "1. merged $base_ref into the PR head without a conflict"
else
  conflicted=$(git -C "$work" diff --name-only --diff-filter=U)
  [ -n "$conflicted" ] || die "merging $base_ref into #$pr failed without a conflict (git identity?)"
  by_hand=$(printf '%s\n' "$conflicted" | grep -Ev "$GENERATED_RE" || true)
  if [ -n "$by_hand" ]; then
    git -C "$work" merge --abort
    keep_work=0
    die "merging $base_ref into #$pr conflicts outside the generated files; merge it into the branch and resolve by hand: $(echo "$by_hand" | tr '\n' ' ')"
  fi
  printf '%s\n' "$conflicted" | while IFS= read -r path; do
    git -C "$work" checkout --ours -- "$path"
    git -C "$work" add -- "$path"
  done
  git -C "$work" commit -q --no-edit
  echo "1. merged $base_ref; generated-file conflicts taken from the PR side, to be rebuilt:"
  printf '%s\n' "$conflicted" | sed 's/^/     /'
fi

# 2. Rebuild the committed catalog on the merged tree. Two types on one
#    part-number block are refused here, naming both.
uv run -q --directory "$work" sip-generate build --out golden-catalog >/dev/null ||
  die "the build refuses the merged tree of #$pr (the reason is above); NOT pushed, NOT merged"
if [ -n "$(git -C "$work" status --porcelain)" ]; then
  git -C "$work" add -A
  git -C "$work" commit -q -m "Rebuild golden-catalog on the merge of $base_ref into $head_ref (#$pr)"
  echo "2. the rebuild changed: $(git -C "$work" show --stat --format= HEAD | tail -1)"
else
  echo "2. the rebuild changed nothing"
fi

# 3. The checks, on exactly the tree that would be pushed.
if ! uv run -q --directory "$work" pytest -q -p no:cacheprovider "${CHECKS[@]}"; then
  die "#$pr is red on the merged tree; NOT pushed, NOT merged"
fi
echo "3. drift, golden and seam tests green on the merged tree"

final_sha=$(git -C "$work" rev-parse HEAD)
if [ "$dry_run" -eq 1 ]; then
  keep_work=0
  if [ "$final_sha" = "$head_sha" ]; then
    echo "dry run: would squash-merge #$pr at $head_sha (nothing to push)"
  else
    echo "dry run: would push $final_sha to $head_ref, then squash-merge #$pr at it"
  fi
  exit 0
fi

# 4. Push the merged tree, if it is not the PR head already. Not forced: a PR
#    head that moved since the clone refuses the push.
if [ "$final_sha" != "$head_sha" ]; then
  git -C "$work" push -q origin "HEAD:refs/heads/$head_ref"
  echo "4. pushed $final_sha to $head_ref"
else
  echo "4. nothing to push"
fi

# 5. Merge only the tree that was checked, against the main it was checked on.
now_base=$(git -C "$work" ls-remote origin "refs/heads/$base_ref" | cut -f1)
[ "$now_base" = "$base_sha" ] ||
  die "$base_ref moved to $now_base during the checks; NOT merged. Re-run to check against it"
# GitHub recomputes mergeability after a push, and refuses until it has.
for attempt in 1 2 3 4 5 6; do
  if gh pr merge "$pr" -R "$slug" --squash --match-head-commit "$final_sha"; then
    keep_work=0
    echo "5. squash-merged #$pr at $final_sha"
    exit 0
  fi
  if [ "$attempt" -lt 6 ]; then sleep 5; fi
done
die "gh pr merge refused #$pr six times; the checked tree is pushed, nothing is merged"
