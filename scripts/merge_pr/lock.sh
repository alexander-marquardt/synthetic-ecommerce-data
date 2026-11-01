# The merge lock of scripts/merge_pr.sh. Reads $slug, $pr and die.
# shellcheck shell=bash

#: One merge at a time (#383). mkdir is the atomic step; the owner file names the holder's
#: pid, so a lock left by a killed run is told from a live one. Taking over a dead holder's
#: lock is a rename then a delete, and two waiters doing it at once can still delete a
#: lock a third has just taken: a window of microseconds, on a lock held for an hour.
lock_held=0
release_merge_lock() {
  if [ "$lock_held" -eq 1 ]; then
    lock_held=0
    rm -rf "$lock_dir"
  fi
}
acquire_merge_lock() {
  local waited_for=$SECONDS deadline owner_pid owner_pr announced=0
  lock_dir=${MERGE_PR_LOCK:-/tmp/merge-pr-$(printf '%s' "$slug" | tr -c 'A-Za-z0-9._-' _).lock}
  deadline=$((SECONDS + ${MERGE_PR_LOCK_WAIT:-14400}))
  until mkdir "$lock_dir" 2>/dev/null; do
    owner_pid="" owner_pr=""
    read -r owner_pid owner_pr 2>/dev/null <"$lock_dir/owner" || true
    if [ -n "$owner_pid" ] && ! kill -0 "$owner_pid" 2>/dev/null; then
      echo "merge_pr.sh: the merge lock's holder (pid $owner_pid, #$owner_pr) is gone; taking the lock over"
      if mv "$lock_dir" "$lock_dir.gone.$$" 2>/dev/null; then
        rm -rf "$lock_dir.gone.$$"
        continue
      fi
    fi
    [ "$SECONDS" -lt "$deadline" ] ||
      die "the merge lock $lock_dir is still held by pid ${owner_pid:-unknown} (#${owner_pr:-?}) after $((SECONDS - waited_for))s; NOT merged. Re-run when it is done"
    if [ "$announced" -eq 0 ]; then
      echo "waiting for the merge lock held by pid ${owner_pid:-unknown} (#${owner_pr:-?}); one merge runs at a time"
      announced=1
    fi
    sleep "${MERGE_PR_LOCK_POLL:-10}"
  done
  lock_held=1
  trap release_merge_lock EXIT
  printf '%s %s\n' "$$" "$pr" >"$lock_dir/owner"
  if [ "$announced" -eq 1 ]; then echo "took the merge lock after $((SECONDS - waited_for))s"; fi
}
