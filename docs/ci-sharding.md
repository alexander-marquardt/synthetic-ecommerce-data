# CI sharding and `merge_pr.sh --github-ci` (#348)

The merge chain is serial (each merge changes main and the generated golden files), so how
fast a pull request lands is how long one merge takes. The suite is about 27 minutes of work
on one core; this repository is public, so GitHub-hosted runners cost nothing.

## The tests job is a matrix of shards

`.github/workflows/ci.yaml` job `tests` runs `shard: [1 .. N]` on `ubuntu-latest`. Each
shard runs `pytest` with `PYTEST_ADDOPTS="-n auto --dist loadgroup"` over the files
`scripts/ci_shards.py --shard K --of N` prints. That script deals the collected test files
longest-first, each to the lightest shard, by the seconds in `scripts/ci_shard_weights.json`;
a file with no entry weighs 20 s, so a new test file needs no edit anywhere.

| Change | Where |
|---|---|
| more or fewer shards | the matrix list in `ci.yaml` (nothing else: `--of` is `strategy.job-total`) |
| refresh the weights | download the `junit-*` artifacts of a green run, then `python3 scripts/ci_shards.py --refresh junit-*.xml` |
| run one shard here | `python3 scripts/ci_shards.py --shard 3 --of 12` prints its files |

A file too heavy for one shard is split: `SPLIT_FILES` in `scripts/ci_shards.py` (now
`tests/test_merge_pr.py`, about an hour of independent tests) is printed for every shard,
weighs a N-th of its seconds in each, and `tests/ci_shard_split.py` keeps only the tests whose
position in the file's collection order is the shard's (`CI_SHARD`/`CI_SHARDS`, set by the
workflow's tests step; unset or `CI_SHARDS=1` keeps all). Each test id runs in exactly one
shard. The junit path is given on the pytest command line from `$RUNNER_TEMP`: the `runner`
context is not available in a job-level `env`.

`tests/test_ci_shards_348.py` is the guard: every collected test file is in exactly one
shard (a split file's test ids are), the matrix is `1..N`, no CI job runs pytest on one worker, and the shards stay
balanced by the weights. A module's tests stay on one worker (`--dist loadgroup`,
`tests/xdist_groups.py`), so one module is the floor of a shard's time.

## `merge_pr.sh --github-ci <N>`

Builds the merged tree exactly as `--local-ci` does (steps 1 and 2), pushes it to the
throwaway branch `ci/merge-<N>`, dispatches `ci.yaml` on it with `base`, `head` and `pr` as
inputs (the pull request jobs read their range and the PR text from them), waits for the run,
and merges as before (same head-moved checks, same lock). The PR branch is pushed only after
a green run. The throwaway branch is deleted on every exit. A red run prints each failing job
with its URL and its `FAILED`/`ERROR` lines; a run red only on the golden freshness tests is
regenerated once (#440), as under `--local-ci`. Step 3 (the four drift, golden and seam
tests) is skipped: the same files run in the shards. `GEN_GITHUB_CI=1` makes it the default.
`--local-ci` stays as the fallback when GitHub is down or out of minutes; both print
`gen-merge-minutes` at the end.

The VM chain (`vm_genchain.sh` in agent-ops, run on the agent VM) calls
`bash scripts/merge_pr.sh --local-ci $n`; switching it is replacing `--local-ci` with
`--github-ci` on that line.

## The metric: `gen-merge-minutes`

Wall minutes from the start of `merge_pr.sh <N>` to the squash merge, printed as
`gen-merge-minutes: <m.d> (#N, <mode>, <start> to <end>)`. Before #348 a `--local-ci` merge
took about 55 minutes on the loaded VM. The target is under 15 for `--github-ci`.
