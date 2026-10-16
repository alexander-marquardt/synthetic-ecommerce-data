#!/usr/bin/env bash
# Merge a pull request only on a green run of the tree it will make (#48, #54).
#
#     scripts/merge_pr.sh <N>                # merge PR <N>
#     scripts/merge_pr.sh --dry-run <N>      # everything but the push, the CI wait and the merge
#     scripts/merge_pr.sh --print-checks     # the tests it runs, for CI to reuse
#     scripts/merge_pr.sh --print-generated  # the files a conflict is resolved in by rebuilding
#     scripts/merge_pr.sh --print-ci         # the CI checks a merge waits for
#     scripts/merge_pr.sh --local-ci <N>     # step 5 runs the CI jobs here, not on GitHub
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
#      golden-retail/stats.json, gen#343) and the pinned price figures and the
#      100K build's sizes (measured_builds.py, gen#85), and commits only GENERATED. A file
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
  src/synthetic_ecommerce_data/core/data/measured_builds.json
  src/prism_synthetic_industrial/data/field_weights/synthetic_industrial_flat.yaml
)

#: The command that rewrites golden-retail/stats.json (gen#162, gen#343). It
#: is the one retail_figures.py names as REBUILD, which tests/test_merge_pr.py
#: pins. The retail build is the slower half, about 40 s.
RETAIL_REBUILD=(python prototypes/retail_drawings/retail_figures.py)

#: The command that rewrites the pinned price figures and the 100K build's sizes
#: (gen#85), the one measured_builds.py names as REBUILD, which
#: tests/test_merge_pr.py pins. It builds the default and the 100K catalog,
#: about a minute.
BUILDS_REBUILD=(python -m synthetic_ecommerce_data.domains.industrial.measured_builds)

#: The jobs of .github/workflows/ci.yaml, by the check-run name GitHub gives
#: them. A pull request's commit must carry each REQUIRED_CI check, green; a
#: SKIPPED_BY_DESIGN_CI check (a push-only job) may also be skipped. Pinned to
#: the workflow by tests/test_merge_pr.py.
REQUIRED_CI=(tests commit-messages file-size customer-name-check)
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

dry_run=0
local_ci=0
[ "${GEN_LOCAL_CI:-}" = 1 ] && local_ci=1
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
    --local-ci) local_ci=1; shift ;;
    --label) [ $# -gt 2 ] || die "--label needs a value"; label=$2; shift 2 ;;
    *) break ;;
  esac
done
[ $# -eq 1 ] && [[ $1 =~ ^[0-9]+$ ]] ||
  die "usage: scripts/merge_pr.sh [--dry-run] [--local-ci] [--label NAME] <PR number>"
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
# shellcheck disable=SC2329  # invoked by the EXIT trap
cleanup() {
  rm -f "$checks_log" "$build_log"
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

# 2. Rebuild the committed catalog on the merged tree. Two types on one
#    part-number block are refused here, naming both.
build_rc=0
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
retail_rc=0
uv run -q --locked --directory "$work" "${RETAIL_REBUILD[@]}" \
  >/dev/null 2>"$build_log" || retail_rc=$?
cat "$build_log" >&2
[ "$retail_rc" -eq 0 ] ||
  die "the retail rebuild refuses the merged tree of #$pr (the reason is above); NOT pushed, NOT merged"
# The pinned price figures and the 100K build's sizes move with every type PR too
# (gen#85): rebuild them on the same merged tree.
builds_rc=0
uv run -q --locked --directory "$work" "${BUILDS_REBUILD[@]}" \
  >/dev/null 2>"$build_log" || builds_rc=$?
cat "$build_log" >&2
[ "$builds_rc" -eq 0 ] ||
  die "the measured-builds rebuild refuses the merged tree of #$pr (the reason is above); NOT pushed, NOT merged"
if [ -n "$conflicted" ]; then
  while IFS= read -r path; do
    if grep -q '^<<<<<<< ' "$work/$path"; then
      die "$path still holds conflict markers after the rebuild, so the rebuild did not write it; NOT pushed, NOT merged"
    fi
  done <<<"$conflicted"
fi
git -C "$work" add -- "${GENERATED[@]}"
stray=$(git -C "$work" status --porcelain | grep -v '^[MADRC] ' || true)
[ -z "$stray" ] ||
  die "the rebuild left changes outside the generated files; NOT pushed, NOT merged:
$stray"
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

# 5 (--local-ci). Every CI job of the workflows, on exactly the tree that
#    would merge. All of them run; any red one refuses.
run_local_ci() {
  local jobs job script log started verdict failed="" required
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
    log="${MERGE_PR_LOG_DIR:-/tmp}/$label-$job.log"
    started=$SECONDS
    # GEN_LOCAL_CI is dropped so a test that runs this script does not recurse.
    if (cd "$work" && env -u GEN_LOCAL_CI bash --noprofile --norc -eo pipefail -c "$script") >"$log" 2>&1; then
      verdict=PASS
    else
      verdict=FAIL
      failed+=" $job"
    fi
    echo "   local CI $job: $verdict ($((SECONDS - started))s) log $log"
  done
  [ -z "$failed" ] || die "local CI is red on $final_sha (failed:$failed); NOT merged"
}

final_sha=$(git -C "$work" rev-parse HEAD)
if [ "$dry_run" -eq 1 ]; then
  if [ "$local_ci" -eq 1 ]; then
    run_local_ci
    echo "5. every local CI job is green on $final_sha"
  fi
  keep_work=0
  if [ "$final_sha" = "$head_sha" ]; then
    echo "dry run: would wait for every CI check on $head_sha, then squash-merge #$pr at it"
  else
    echo "dry run: would push $final_sha to $head_ref, wait for every CI check on it, then squash-merge #$pr at it"
  fi
  exit 0
fi

# 4. Push the merged tree, if it is not the PR head already.
if [ "$final_sha" != "$head_sha" ]; then
  git -C "$work" push -q origin "HEAD:refs/heads/$head_ref" ||
    die "the push of $final_sha to $head_ref was refused (has the PR head moved?); NOT merged"
  echo "4. pushed $final_sha to $head_ref"
else
  echo "4. nothing to push"
fi

# 5. The PR's own CI, on exactly the commit that will merge.
if [ "$local_ci" -eq 1 ]; then
  run_local_ci
  echo "5. every local CI job is green on $final_sha"
else
ci_timeout=${MERGE_PR_CI_TIMEOUT:-3600}
ci_deadline=$((SECONDS + ci_timeout))
while :; do
  runs=$(gh api "repos/$slug/commits/$final_sha/check-runs?per_page=100" \
    --jq '.check_runs[] | [.name, .status, (.conclusion // "")] | @tsv')
  seen=() pending=""
  while IFS=$'\t' read -r name status conclusion; do
    [ -n "$name" ] || continue
    seen+=("$name")
    if [ "$status" != completed ]; then
      pending+=" $name"
    elif [ "$conclusion" = skipped ]; then
      listed "$name" "${SKIPPED_BY_DESIGN_CI[@]}" ||
        die "check $name on $final_sha was skipped, and it is not skipped by design; NOT merged"
    elif [ "$conclusion" != success ]; then
      die "check $name on $final_sha is $conclusion; NOT merged"
    fi
  done <<<"$runs"
  missing=""
  for name in "${REQUIRED_CI[@]}"; do
    listed "$name" ${seen[@]+"${seen[@]}"} || missing+=" $name"
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
    exit 0
  fi
  if [ "$attempt" -lt 6 ]; then sleep "${MERGE_PR_RETRY_SLEEP:-5}"; fi
done
die "gh pr merge refused #$pr six times; the checked tree is pushed, nothing is merged"
