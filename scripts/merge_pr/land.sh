# Steps 4 and 6 of scripts/merge_pr.sh: the push to the PR branch and the squash merge.
# shellcheck shell=bash

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

# 6. Merge only the tree that was checked, against the main it was checked
#    on. GitHub recomputes mergeability after a push and refuses until it
#    has, so the merge is retried; main and the head are re-read before each.
#    A read is repeated (3 reads, MERGE_PR_HEAD_SLEEP s apart) before it counts
#    as a move: ls-remote right after a push can answer from before it (#383).
#    Sets seen_sha to the last read.
remote_ref_is() {
  local ref=$1 want=$2 try
  for try in 1 2 3; do
    seen_sha=$(git -C "$work" ls-remote origin "refs/heads/$ref" | cut -f1) || seen_sha=""
    [ "$seen_sha" = "$want" ] && return 0
    if [ "$try" -lt 3 ]; then sleep "${MERGE_PR_HEAD_SLEEP:-10}"; fi
  done
  return 1
}

squash_merge() {
  local attempt merge_seconds ci_mode
  seen_sha=""
  for attempt in 1 2 3 4 5 6; do
    remote_ref_is "$base_ref" "$base_sha" ||
      die "$base_ref moved to $seen_sha since it was merged in; NOT merged. Re-run to check against it"
    remote_ref_is "$head_ref" "$final_sha" ||
      die "$head_ref moved to $seen_sha since it was checked; NOT merged. Re-run to check it"
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
}
