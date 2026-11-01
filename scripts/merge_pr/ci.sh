# Step 5 of scripts/merge_pr.sh: CI on exactly the tree that would merge, by one of three routes
# (the PR's own checks, --local-ci, --github-ci). Reads $work, $final_sha, $base_sha, $pr, $slug.
# shellcheck shell=bash

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
    # GEN_LOCAL_CI is dropped so a test that runs this script does not recurse. The guard's
    # own lines (a wait for the lock, a stop at the memory ceiling) go to fd 3, this script's
    # stderr, and not into the job's log (#366).
    if (cd "$work" && unset GEN_LOCAL_CI &&
      guarded --notice-fd 3 -- bash --noprofile --norc -eo pipefail -c "$script") 3>&2 >"$log" 2>&1; then
      verdict=PASS
    else
      verdict=FAIL
      local_ci_failed+=" $job"
    fi
    echo "   local CI $job: $verdict ($((SECONDS - started))s) log $log"
    if [ "$verdict" = FAIL ]; then report_red_job "$log"; fi
  done
  [ -z "$local_ci_failed" ]
}

# A red job (#453): its FAILED/ERROR summary lines (at most 20) go to this script's own
# output, and its log is copied into the directory the script keeps for inspection, so
# the failing test is named without a re-run even when the temp directory is swept.
# The copy sits under .git: a file beside the tree would be a stray change to the build.
report_red_job() {
  local log=$1 kept="$work/.git/ci-logs" total
  total=$(grep -cE '^(FAILED|ERROR) ' "$log" || true)
  grep -E '^(FAILED|ERROR) ' "$log" | head -20 | sed 's/^/     /' || true
  if [ "${total:-0}" -gt 20 ]; then
    echo "     ... $((total - 20)) more FAILED/ERROR lines in the log"
  fi
  if mkdir -p "$kept" && cp -f "$log" "$kept/"; then
    echo "   kept for inspection: $kept/$(basename "$log")"
  fi
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
    # gh refuses a log with terminal escapes unless told; an older gh has no such flag.
    { gh api --allow-escape-sequences "repos/$slug/actions/jobs/$job_id/logs" 2>/dev/null ||
      gh api "repos/$slug/actions/jobs/$job_id/logs" 2>/dev/null || true; } |
      sed -E 's/\x1b\[[0-9;]*[A-Za-z]//g; s/^[0-9T:.Z-]+ //' >"$(local_ci_log "$safe")"
    echo "   GitHub CI $name: $jconclusion $url"
    report_red_job "$(local_ci_log "$safe")"
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

# 5. The PR's own CI, on exactly the commit that will merge.
wait_for_pr_checks() {
  local ci_timeout ci_deadline runs seen seen_stems pending missing name status conclusion
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
}

# 5 (--local-ci). The local CI; a regenerated tree is pushed once it is green.
run_local_ci_and_push_regenerated() {
  run_local_ci_regenerating
  if [ "$final_sha" != "$pushed_sha" ]; then
    git -C "$work" push -q origin "HEAD:refs/heads/$head_ref" ||
      die "the push of the regenerated $final_sha to $head_ref was refused (has the PR head moved?); NOT merged"
    echo "5b. pushed the regenerated $final_sha to $head_ref"
  fi
  echo "5. every local CI job is green on $final_sha"
}

# --dry-run: CI here when a flag asked for it, then what a real run would do.
dry_run_ci_and_report() {
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
}
