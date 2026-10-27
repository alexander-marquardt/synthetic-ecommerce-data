# CI sharding and `merge_pr.sh --github-ci` (#348)

The merge chain is serial (each merge changes main and the generated golden files), so how
fast a pull request lands is how long one merge takes. The suite is about 27 minutes of work
on one core; this repository is public, so GitHub-hosted runners cost nothing.

## The tests job is a matrix of shards

`.github/workflows/ci.yaml` job `tests` runs `shard: [1 .. N]` on `ubuntu-latest` (or, for this repository's own branches once the repository variable `SYNTH_CI_SELF_HOSTED` is `true`, on the self-hosted `synth-ci` runner of #596, below). Each
shard runs `pytest` with `PYTEST_ADDOPTS="-n auto --dist loadgroup"` over the files
`scripts/ci_shards.py --plan K --of N` prints (a pull request's files are the selected ones, below). That script deals the collected test files (`tests/` and `prototypes/retail_drawings/`:
`testpaths` of `pyproject.toml`, `TEST_DIRS` in the script) longest-first, each to the lightest shard, by the seconds in `scripts/ci_shard_weights.json`;
a file with no entry weighs 20 s, so a new test file needs no edit anywhere. The drawing tests run once, in the shard that is dealt them: there is no second child-process run of the same files (gen#486's test was removed for gen#362), and a test file outside the collected directories fails `tests/test_test_files_collected_362.py`.

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

A test file outside `testpaths` is never run (the drawing tests were not, until gen#362);
`tests/test_test_files_collected_362.py` fails on a tracked `test_*.py` or `*_test.py` file
outside it. A new directory of tests goes in `testpaths`, `TEST_DIRS` and `_TEST_ROOTS` in
`scripts/ci_select.py`.

`tests/test_ci_shards_348.py` is the guard: every collected test file is in exactly one
shard (a split file's test ids are), the matrix is `1..N`, no CI job runs pytest on one worker, and the shards stay
balanced by the weights. A module's tests stay on one worker (`--dist loadgroup`,
`tests/xdist_groups.py`), so one module is the floor of a shard's time.

## The order the files are listed in

`--dist loadgroup` gives a free worker the next module in the order pytest collected them, so
the order of the file list is the schedule. `ci_shards.py --plan` (the tests step's source of
files, in every shard and in the local run) prints the files heaviest first by the weights,
with the files whose tests xdist spreads (`XDIST_SPREAD = True`, `SPLIT_FILES`) last: they are
many small tests, the filler that levels the workers' ends. Alphabetical order left the
late-sorting heavy modules (`test_retail_scale.py` and two other retail modules, which start
at about 910-1020 s in the 13-worker replay) starting when the other workers were nearly done.
`tests/test_ci_run_order_348.py` replays xdist's rule over the committed weights (no timing):
at 8, 12, 13 and 24 workers the run ends within a tenth of perfect balance and under the
alphabetical order. `--shard` stays alphabetical.

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
  (1200 s of the weights, `SHARD_BUDGET_SECONDS`), checked against the deal itself: the
  longest-first deal can leave a shard a file over the average, so the count grows until the
  heaviest dealt shard, a split file's share included, is within the budget (#704). A shard past
  that count prints no file, and its job ends after the checkout without installing anything.
  With no base and head, `--plan` is `--shard`: every file on every shard. `--plan all` prints
  every file, for a local run. A full run deals the files to 16 shards of about 1117 s of the
  weights each.
* The budget is below the job's `timeout-minutes: 25` (1500 s) by the wall clock a weight second
  can take on a hosted runner, up to 0.99 s (measured on the 16 shards of one push run). An
  earlier 1800 s budget dealt a near-full selection to shards of 1767 s, which ran 25 minutes
  and were cancelled (#704). Do not raise the timeout: cut the budget or add shards.
  `tests/test_ci_shard_budget_704.py` holds it: no selection is dealt a shard past the budget,
  and the budget times the worst ratio fits four fifths of the timeout.
* The Tests step adds `--durations=10`, so the log of a slow or stalled shard names its ten
  slowest tests.
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

## Superseded runs are cancelled (#614)

`ci.yaml` has a `concurrency` block, so a merge batch queues one main run, not one per merge:

| Run | Group | Cancelled by a newer run of the group |
| --- | --- | --- |
| push to `main` | `ci-refs/heads/main` | yes: the newest main commit is the one that answers "is main green" |
| pull request | `ci-pr-<number>` | yes: only the newest head of a pull request matters |
| dispatched (`--github-ci`) | `ci-run-<run id>` | no: the group is the run's own, so a merge check is never cancelled |

A cancelled main run is a superseded run, not a red one. `tests/test_ci_runs_on_596.py` reads the
block and evaluates the group and `cancel-in-progress` for each kind of run.

The VM chain (`vm_genchain.sh` in agent-ops, run on the agent VM) calls
`bash scripts/merge_pr.sh --local-ci $n`; switching it is replacing `--local-ci` with
`--github-ci` on that line.

## The metric: `gen-merge-minutes`

Wall minutes from the start of `merge_pr.sh <N>` to the squash merge, printed as
`gen-merge-minutes: <m.d> (#N, <mode>, <start> to <end>)`. Before #348 a `--local-ci` merge
took about 55 minutes on the loaded VM. The target is under 15 for `--github-ci`.

The issue's target, a typical merge under 10 minutes, is for `--local-ci` on the agent VM; the
15 above is for `--github-ci`, whose shards queue behind the runner cap. They are two modes
with two targets, not two readings of one. Measured on the VM (2026-10-19, 5 of the heaviest
modules, 674 tests, `-n 2 --dist loadgroup`, one run): 358 s of wall for 696 s of test time,
which is 0.295 of the same modules' weights in `scripts/ci_shard_weights.json` (the hosted
runners' seconds; per module 0.19 to 0.57). Applying that ratio to the whole weight table, a
simulation of xdist's rule (each unit to the worker that frees first) gives a whole-suite run
of about 412 s on 13 workers in alphabetical order and 375 s in run order, and 268 s against
207 s on 24. That is a projection from a five-module sample, not a measured whole-suite run,
and it assumes the merge tests cost the same ratio; the last measured whole-suite runs
(637 to 729 s on 12 workers) were on a VM with a load average of 20 to 33. Three real merges
with their `gen-merge-minutes` lines are still the figure that closes the issue's first bullet.

## Where the jobs run (#596)

Every job's `runs-on` is one expression: `[self-hosted, synth-ci]` when the repository variable
`SYNTH_CI_SELF_HOSTED` is `true` and the run is a push, a dispatched run or a pull request whose
head branch is in this repository; `ubuntu-latest` otherwise, so a fork's pull request never runs
on the self-hosted runner. That runner (agent-ops `vm/ci_runner/`) runs each job in its own
throwaway container on the agent VM, `--cpus 8 --memory 16g`, one job at a time by default, so a
full run's jobs queue behind each other there. Unsetting the variable sends every job back to
hosted runners with no commit. A push to `main` can have its own runners. When the repository variable `SYNTH_CI_MAIN_RUNNER` is
`true`, a push event's jobs request `[self-hosted, synth-ci-main]` instead; pull requests and
dispatched runs (including `merge_pr.sh --github-ci`) keep `[self-hosted, synth-ci]`. The VM
registers the last `--main-jobs N` slots with the `synth-ci-main` label (agent-ops
`vm/ci_runner/README.md`), so a merge's main run no longer waits behind pull-request runs. A
full run is 23 jobs of roughly 135 to 165 job-minutes, so N sets its duration: about 135/N + 3
minutes (one runner is worse than the shared pool, four about 37 minutes). Set the variable
to `false` to send main pushes back to the shared pool with no commit. `tests/test_ci_runs_on_596.py` holds every job to the expression.

## A lost xdist worker is an infra failure, rerun once (#629)

Three pull requests had a `tests` shard end red with no test id: both workers went down within a
tenth of a second (`node down: Not properly terminated`), and the controller then raised
`INTERNALERROR> KeyError: <WorkerController gw2>` replacing them. The two worker crashes read
back were at 94 % and 98 % of the shard's items, on two different shards; main's same shards were
green. The runner's kernel log cannot be read from inside a job, so this change does not name the
cause: an out-of-memory kill (the container has `--memory 16g` while the VM was swapping) is the
first hypothesis and is not confirmed.

The Tests step runs `python3 scripts/ci_run_pytest.py -- uv run --locked pytest ...`. When the
output shows a lost worker the script prints `infra: worker lost` (a `::warning::` annotation),
then what a job can read: the job cgroup's `memory.events` OOM counts, `memory.peak` and
`memory.max`, the largest process's peak RSS, the host's MemAvailable and SwapFree, and the
kernel OOM lines when `dmesg` is readable. It then runs the shard once more (`--reruns N`, default
1). A shard that loses a worker on every attempt ends with exit code 75 and an `::error::infra:
worker lost` annotation, not a test's exit code. A run whose tests failed with every worker alive
is never rerun. The next occurrence therefore names its cause in the job log, and a first
occurrence no longer reds a pull request. If the evidence shows memory, lower `-n` for that shard
or split it (the matrix list in `ci.yaml`). `tests/test_ci_worker_lost_629.py` is the guard.
