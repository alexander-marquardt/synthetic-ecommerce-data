# Steps 1 to 3 of scripts/merge_pr.sh: the merged tree, its rebuild and its checks. Every
# function works on the clone at $work and reads the script's $pr, $base_ref and $head_ref.
# shellcheck shell=bash

# 1. Merge current main into the PR head. Sets conflicted to the files left for the rebuild.
merge_main_into_head() {
  local by_hand path
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
}

# Rebuild every generated file on the tree at $work. Two types on one
# part-number block are refused here, naming both.
rebuild_generated() {
  local build_rc=0 builds_rc=0 pins_rc=0
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
  # The pinned price figures and the 100K build's sizes move with every type PR too
  # (gen#85): rebuild them on the same merged tree.
  uv run -q --locked --directory "$work" "${BUILDS_REBUILD[@]}" \
    >/dev/null 2>"$build_log" || builds_rc=$?
  cat "$build_log" >&2
  [ "$builds_rc" -eq 0 ] ||
    die "the measured-builds rebuild refuses the merged tree of #$pr (the reason is above); NOT pushed, NOT merged"
  uv run -q --locked --directory "$work" "${PINS_REBUILD[@]}" \
    >/dev/null 2>"$build_log" || pins_rc=$?
  cat "$build_log" >&2
  [ "$pins_rc" -eq 0 ] ||
    die "the golden pins refuse the merged tree of #$pr (the reason is above); NOT pushed, NOT merged"
}

# Stage the generated files; the rebuild may change nothing else.
stage_generated() {
  local stray
  git -C "$work" add -- "${GENERATED[@]}"
  stray=$(git -C "$work" status --porcelain | grep -v '^[MADRC] ' || true)
  [ -z "$stray" ] ||
    die "the rebuild left changes outside the generated files; NOT pushed, NOT merged:
$stray"
}

# 2. Rebuild the committed catalog on the merged tree.
rebuild_merged_tree() {
  local path
  # A generated file the code reads at import (core/price.py reads the measured builds)
  # holds conflict markers after a conflicted merge, and the build that would rewrite it
  # cannot import them: drop it, so the build starts without it and writes it (gen#85).
  if [ -n "$conflicted" ]; then
    while IFS= read -r path; do
      listed "$path" "${READ_AT_IMPORT[@]}" && rm -f "$work/$path"
    done <<<"$conflicted"
  fi
  rebuild_generated
  if [ -n "$conflicted" ]; then
    while IFS= read -r path; do
      [ -e "$work/$path" ] ||
        die "$path was dropped for the rebuild and the rebuild did not write it back; NOT pushed, NOT merged"
      if grep -q '^<<<<<<< ' "$work/$path"; then
        die "$path still holds conflict markers after the rebuild, so the rebuild did not write it; NOT pushed, NOT merged"
      fi
    done <<<"$conflicted"
  fi
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
}

# The report's counts, not the summary line: they are exact and need no output parsing.
count() { sed -nE "s/.*<testsuite[^>]*[[:space:]]$1=\"([0-9]+)\".*/\1/p" "$checks_log" | head -1; }

# 3. The checks, on exactly the tree that would be pushed. Pytest exits 0
#    when every test is skipped, so a run must also have passed something.
# On several workers (#348), with the options the local CI jobs get: one source.
# --github-ci skips this: the same files run in the sharded tests job (#348).
check_merged_tree() {
  local parallel passed
  if [ "$github_ci" -eq 1 ]; then
    echo "3. skipped: the drift, golden, seam and README size tests run in the sharded tests job"
    return 0
  fi
  read -r -a parallel <<<"$(uv run -q --locked --directory "$here" python \
    "$here/scripts/local_ci_jobs.py" --pytest-options)"
  [ "${#parallel[@]}" -gt 0 ] || die "scripts/local_ci_jobs.py --pytest-options printed nothing"
  if ! guarded -- uv run -q --locked --directory "$work" pytest -q -p no:cacheprovider "${parallel[@]}" \
    --junitxml="$checks_log" "${CHECKS[@]}"; then
    die "#$pr is red on the merged tree; NOT pushed, NOT merged"
  fi
  passed=$(($(count tests) - $(count skipped) - $(count failures) - $(count errors)))
  [ "$passed" -gt 0 ] ||
    die "no test passed in the checks on the merged tree of #$pr (all skipped?); NOT pushed, NOT merged"
  echo "3. drift, golden, seam and README size tests green on the merged tree"
}
