# CI sharding and `merge_pr.sh --github-ci` (#348)

The merge chain is serial (each merge changes main and the generated golden files), so how
fast a pull request lands is how long one merge takes. The suite is about 27 minutes of work
on one core; this repository is public, so GitHub-hosted runners cost nothing.

## The tests job is a matrix of shards

`.github/workflows/ci.yaml` job `tests` runs `shard: [1 .. N]` on `ubuntu-latest`. Each
shard runs `pytest` with `PYTEST_ADDOPTS="-n auto --dist loadgroup"` over the files
`scripts/ci_shards.py --plan K --of N` prints (a pull request's files are the selected ones, below). That script deals the collected test files
longest-first, each to the lightest shard, by the seconds in `scripts/ci_shard_weights.json`;
a file with no entry weighs 20 s, so a new test file needs no edit anywhere.

| Change | Where |
|---|---|
| more or fewer shards | the matrix list in `ci.yaml` (nothing else: `--of` is `strategy.job-total`) |
| refresh the weights | download the `junit-*` artifacts of a green run, then `python3 scripts/ci_shards.py --refresh junit-*.xml` |
| run one shard here | `python3 scripts/ci_shards.py --shard 3 --of 16` prints its files |

A file too heavy for one shard is split: `SPLIT_FILES` in `scripts/ci_shards.py` (now
`tests/test_merge_pr.py` and `tests/test_merge_pr_github_ci_348.py`, about 75 minutes of
independent tests) is printed for every shard,
weighs a N-th of its seconds in each, and `tests/ci_shard_split.py` keeps only the tests whose
position in the file's collection order is the shard's (`CI_SHARD`/`CI_SHARDS`, set by the
workflow's tests step; unset or `CI_SHARDS=1` keeps all). Each test id runs in exactly one
shard. The junit path is added to `PYTEST_ADDOPTS` in the Tests step's own `env`: the `runner`
context is not available in a job-level `env`.

`tests/test_ci_shards_348.py` is the guard: every collected test file is in exactly one
shard (a split file's test ids are), the matrix is `1..N`, no CI job runs pytest on one worker, and the shards stay
balanced by the weights. A module's tests stay on one worker (`--dist loadgroup`,
`tests/xdist_groups.py`), so one module is the floor of a shard's time.

## A pull request runs the tests its change reaches (#495)

The runner cap is about 20 concurrent jobs and one full run of this workflow is 22 jobs, about
93 job-minutes (mean of the 6 newest pull-request runs of 2026-10-18), so runs queued behind each other
for 43 to 59 minutes on average and the merge train timed out waiting. A pull request, and a
dispatched run (`merge_pr.sh --github-ci`), now runs only the test files its change reaches;
a push to `main` runs every test file, so the whole suite still runs once after each merge.

* `scripts/ci_select.py --base B --head H [--why]` prints the selected test files (and, with
  `--why`, the changed path that reached each). `--changed PATH...` does the same for named
  paths. It reads the import and mention graph of the checkout: a test is selected when a
  changed Python file is in its import closure (an import, a script it runs by path, a console
  script of `pyproject.toml`, every module of a directory whose code imports by computed name,
  every module of a package a registry walks by dotted name), or when a changed data file is
  named in the text of its closure or is a data file of a package one of its modules belongs to.
  It over-selects on purpose: a missed test is a correctness bug, an extra test is minutes.
* `FULL_RUN` in the script lists the changes that select every test: `.github/`, `pyproject.toml`,
  `uv.lock`, `vendor/`, the files pytest loads before any test, and the selector and sharding
  scripts themselves. An unreadable diff selects every test. `SMOKE` lists the guards of the
  selection and of the sharding, which every pull request runs. `CONTENT_INSENSITIVE` lists the two
  `test_merge_pr` files, which name the golden files as fixtures: a modified golden or docs path
  does not select them (an added or deleted one does).
* `python3 scripts/ci_shards.py --plan K --of N --base B --head H` prints `shards=<n>`, then shard
  K's files. A selection is dealt to as few shards as keep each under `SCOPED_SHARD_SECONDS`
  (1800 s of the weights); a shard past that count prints no file, and its job ends after the
  checkout without installing anything. With no base and head, `--plan` is `--shard`: every file
  on every shard. `--plan all` prints every file, for a local run. A full run deals 182 files to
  9 shards of up to 1800 s of the weights each, against the job's `timeout-minutes: 25`.
* The guard is `tests/test_ci_select_495.py`: each rule on a throwaway tree; every test that
  imports a module is selected when it changes (an independent oracle); every file a mutation
  row plants in selects `tests/test_mutation_bed.py`; the plan's shards are disjoint and add up
  to the selection.

To check what a change runs before pushing: `python3 scripts/ci_select.py --base origin/main --head HEAD --why`.

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
