#!/usr/bin/env bash
#
# Run one network-fetching command with a bounded retry (#10272).
#
#     bash .github/scripts/retry.sh [--timeout SECONDS] [--backoff SECONDS] <command> [args...]
#
# WHY: a package download that timed out once evicted a green required PR from
# the head of the merge queue (2026-10-03). A fetch is the one step a retry
# cannot make wrong, so every fetch in the workflows goes through this script
# (tests/test_ci_network_steps_retry_10272.py derives the list from the YAML).
#
# THE FAILURE STAYS A FAILURE: the command runs at most RETRY_ATTEMPTS times
# (default 3), and after the last attempt the script exits with the command's
# OWN exit code. Never wrap a test run in this: a retried test hides the flake
# it should report. Never wrap a write that is not idempotent (a POST that
# creates something): a retry after a timed-out success writes it twice.
#
# A HANG IS A FAILURE TOO: each attempt is killed after --timeout seconds
# (default 300), so a connection that stalls is retried instead of eating the
# step's timeout-minutes. The census test refuses a call whose worst case
# (every attempt timing out, plus the waits) does not fit its step's cap. A
# command that legitimately runs longer than 300 s passes a larger --timeout:
# the image builds pass 1800.
#
# THE WAITS: --backoff is the first wait (default 5 s, or RETRY_BACKOFF_SECONDS,
# which the tests set to 0), and each later wait is three times the one before:
# 5 s then 15 s by default, 30 s then 90 s with --backoff 30.
#
# OUTPUT: each attempt's stdout goes to a temporary file, and only the LAST
# attempt's is printed to stdout. A caller that captures stdout (``x=$(...)``,
# ``> file``) therefore sees one complete answer, never a failed attempt's
# partial page in front of it. Stderr is NOT buffered: it streams live, every
# attempt's, so a step the runner kills at its timeout-minutes still shows what
# the hung command had said, and a long build's progress is visible while it
# runs. The retry's own ::warning:: lines go to stderr too.
#
# EVERY ATTEMPT'S STDOUT IS KEPT (#11169): a failed attempt's stdout is replayed
# to stderr, in a log group headed by the attempt number, its exit code and its
# elapsed seconds, so the log holds all of them and not only the last. A
# ``docker pull`` writes its per-layer lines to stdout, and three stalled pulls
# once left only the third attempt's lines, with no word on which layer stopped.
# After an attempt that TIMED OUT, the wrapper also prints, per layer line
# (``<12 hex>: <state> <bytes>``) the LAST state that attempt reached, and marks
# each layer not yet at ``Download complete``, ``Pull complete`` or ``Already
# exists``. That names the layer a stall stopped on and how far it got. Neither
# changes the attempt count or the time limit.

set -u

attempts="${RETRY_ATTEMPTS:-3}"
delay="${RETRY_BACKOFF_SECONDS:-5}"
limit=300
# Seconds between the polite stop and the kill, for a command that ignores TERM.
grace=5

while [ "$#" -gt 0 ]; do
  case "$1" in
    --timeout | --backoff)
      case "${2:-}" in
        '' | *[!0-9]*)
          echo "::error::retry.sh: $1 needs a whole number of seconds, got '${2:-}'" >&2
          exit 2
          ;;
      esac
      if [ "$1" = --timeout ]; then limit="$2"; else delay="$2"; fi
      shift 2
      ;;
    *) break ;;
  esac
done
if [ "$#" -eq 0 ]; then
  echo "::error::retry.sh: no command to run" >&2
  exit 2
fi

out="$(mktemp)"
err="$(mktemp)"
trap 'rm -f "$out" "$err"' EXIT

# Both forms stop the command's whole process group, so a git or gh child it
# started (git fetch runs ssh) stops too. coreutils ``timeout`` (every Linux
# runner) does it when not given --foreground. A host without it (a macOS laptop
# running the tests) gets the perl form below, which runs the command as its own
# process group, signals that group TERM at the limit and KILL after the grace,
# forwards TERM/INT/HUP it receives, and exits 124 on a timeout as coreutils does.
bounded() {
  if command -v timeout > /dev/null 2>&1; then
    timeout -k "$grace" "$limit" "$@"
  else
    perl -e '
      my ($limit, $grace) = splice @ARGV, 0, 2;
      my $pid = fork // die "retry.sh: fork: $!\n";
      if ($pid == 0) {
        setpgrp(0, 0);
        exec { $ARGV[0] } @ARGV or do { print STDERR "$ARGV[0]: $!\n"; exit 127 };
      }
      setpgrp($pid, $pid);
      my $timed_out = 0;
      $SIG{$_} = sub { kill $_[0], -$pid } for qw(TERM INT HUP);
      $SIG{ALRM} = sub {
        $timed_out = 1;
        kill "TERM", -$pid;
        $SIG{ALRM} = sub { kill "KILL", -$pid };
        alarm $grace;
      };
      alarm $limit;
      waitpid $pid, 0;
      my $st = $?;
      alarm 0;
      exit 124 if $timed_out;
      exit($st & 127 ? 128 + ($st & 127) : $st >> 8);
    ' "$limit" "$grace" "$@"
  fi
}

# One line per layer: the last state this attempt printed for it, and "not
# complete" on a layer that never reached a finished state. A carriage return
# (a progress bar redrawn in place) ends a line, so the byte count shown is the
# last redraw. Plain awk: no interval expressions, which older awks lack.
layer_report() {
  tr '\r' '\n' < "$1" | awk '
    index($0, ": ") == 13 && substr($0, 1, 12) ~ /^[0-9a-f]+$/ {
      id = substr($0, 1, 12)
      if (!(id in state)) order[++n] = id
      state[id] = substr($0, 15)
    }
    END {
      for (i = 1; i <= n; i++) {
        s = state[order[i]]
        done = (s ~ /^(Download complete|Pull complete|Already exists)/)
        printf "retry.sh:   layer %s: %s%s\n", order[i], s, (done ? "" : "  <- not complete")
      }
    }'
}

# One line per FAILED attempt, for any command (#11169; a docker buildx bake failed
# on a Docker Hub token request with no registry in the log): the step, the exit
# code, the elapsed seconds, and every registry host the attempt or its arguments
# named, then the last five lines of stderr (or of stdout when stderr is empty).
# ``GITHUB_JOB`` and ``GITHUB_ACTION`` name the step the runner is in.
# Everything this script prints about a failed attempt passes through redact():
# URL userinfo (scheme://user:token@host), Authorization and Bearer values, and
# token / password / secret style key=value or "key": "value" pairs. A registry's
# anonymous bearer token is not a registered secret, so the runner would not mask it.
redact() {
  perl -pe '
    $| = 1;
    s~(://)[^/@\s]+@~$1<redacted>@~g;
    s~(authorization["\x27]?\s*[:=]\s*).*~$1<redacted>~ig;
    s~(bearer\s+)[^\s"\x27,}]+~$1<redacted>~ig;
    s~\b((?:access_|id_|refresh_|auth_|api_|private_)?(?:token|password|passwd|secret|apikey|api_key|client_secret)["\x27]?\s*[:=]\s*["\x27]?)[^"\x27&\s,}]+~$1<redacted>~ig;
    s~\b(gh[pousr]_|github_pat_)[A-Za-z0-9_]{8,}~$1<redacted>~g;
  '
}

# Why the attempt failed, from its exit code and output: rate-limit, auth,
# timeout, or other. First match wins, in that order.
classify_cause() {
  local text sep='(^|[^0-9A-Za-z.])'
  text="$(cat "$out" "$err")"
  if printf '%s\n' "$text" | grep -Eiq "toomanyrequests|too many requests|rate limit|${sep}429([^0-9A-Za-z.]|\$)"; then
    echo rate-limit
  elif printf '%s\n' "$text" | grep -Eiq "unauthorized|denied|forbidden|${sep}(401|403)([^0-9A-Za-z.]|\$)"; then
    echo auth
  elif [ "$rc" -eq 124 ] || printf '%s\n' "$text" | grep -Eiq 'timed out|timeout|deadline exceeded'; then
    echo timeout
  else
    echo other
  fi
}

# ``GITHUB_JOB`` and ``GITHUB_ACTION`` name the step the runner is in. Hosts are
# read from the argument list and from the redacted output (any dotted name ending
# in a common registry suffix, so one seen only in the output is found too).
attempt_report() {
  local hosts last
  hosts="$( { printf '%s\n' "$*" | redact | tr ' ' '\n' | sed -n 's|^\([A-Za-z0-9.-]*\.[A-Za-z0-9.-]*\)/.*|\1|p'
    cat "$out" "$err" | redact | grep -Eo 'https?://[A-Za-z0-9._-]+' | sed 's|^https\{0,1\}://||'
    cat "$out" "$err" | redact | grep -Eo '[A-Za-z0-9.-]+\.(io|com|co|org|net|dev|cloud)\b' ; } | sort -u | tr '\n' ',' | sed 's/,$//')"
  echo "retry.sh: attempt-report attempt=$attempt/$attempts command='$1 ${2:-}' step=${GITHUB_JOB:-?}/${GITHUB_ACTION:-?} exit=$rc elapsed=${elapsed}s cause=$(classify_cause) registries=${hosts:-<none seen>}" | redact >&2
  last="$(tr '\r' '\n' < "$err" | grep -v '^$' | tail -n 5)"
  [ -n "$last" ] || last="$(tr '\r' '\n' < "$out" | grep -v '^$' | tail -n 5)"
  echo "retry.sh: last error lines:" >&2
  printf '%s\n' "${last:-<no output>}" | redact | sed 's/^/  | /' >&2
}

# Replay an attempt's stdout to stderr so a failed attempt's output is not lost.
replay_attempt() {
  echo "::group::'$1' attempt $2 of $attempts: stdout (exit code $3, elapsed ${4}s)" >&2
  tr '\r' '\n' < "$out" | redact >&2
  echo "::endgroup::" >&2
  if [ "$3" -eq 124 ]; then
    echo "retry.sh: attempt $2 of $attempts timed out after ${limit}s (elapsed ${4}s); per layer, the last state it reached:" >&2
    layer_report "$out" | redact >&2
  fi
}

attempt=1
while true; do
  started=$SECONDS
  # stderr to a pipe that tee streams live and keeps for the warning below;
  # stdout to this attempt's file. PIPESTATUS[0] is the command's own code.
  bounded "$@" 2>&1 > "$out" | tee "$err" | redact >&2
  rc="${PIPESTATUS[0]}"
  elapsed=$((SECONDS - started))
  if [ "$rc" -eq 0 ] || [ "$attempt" -ge "$attempts" ]; then
    if [ "$rc" -ne 0 ]; then attempt_report "$@"; fi
    if [ "$rc" -eq 124 ]; then
      echo "retry.sh: attempt $attempt of $attempts timed out after ${limit}s (elapsed ${elapsed}s); per layer, the last state it reached:" >&2
      layer_report "$out" | redact >&2
    fi
    cat "$out"
    if [ "$rc" -ne 0 ]; then
      echo "::error::'$1' failed after $attempts attempts (last exit code $rc)" >&2
    fi
    exit "$rc"
  fi
  case "$rc" in
    124) why="timed out after ${limit}s" ;;
    *) why="failed with exit code $rc" ;;
  esac
  replay_attempt "$1" "$attempt" "$rc" "$elapsed"
  attempt_report "$@"
  last="$(tail -n 1 "$err" | tr -d '\r' | redact)"
  echo "::warning::'$1' $why (attempt $attempt of $attempts); retrying in ${delay}s. Its last stderr line: ${last:-<none>}" >&2
  sleep "$delay"
  delay=$((delay * 3))
  attempt=$((attempt + 1))
done
