# `scripts/merge_pr.sh`: what it does, and why

`scripts/merge_pr.sh` is the short flow (its flags are in its first lines). The steps'
code is in `scripts/merge_pr/`, which it sources: `config.sh` (the lists), `lock.sh`,
`tree.sh` (steps 1 to 3), `ci.sh` (step 5) and `land.sh` (steps 4 and 6).

This repository has no branch protection: on its plan the protection API answers 403,
so GitHub offers no merge queue and no "require the branch to be up to date". A pull
request's green is computed against main as of its last CI run. When another type PR
lands after that run, the two can merge without a textual conflict and still leave main
red: stats.json and the field-weights YAML auto-merge with wrong totals, and two types
can take one part-number block. Only a tree holding both changes shows it, so the script
builds that tree before it merges.

## The steps

0. Refuses a PR that is not open, comes from a fork or is a draft (#70), before anything
   is cloned: GitHub refuses a draft's merge only at step 6.
1. Clones the PR head into a temporary directory and merges current main into it. A
   conflict in a file the rebuild rewrites (`GENERATED`) is left for step 2; any other
   conflict is refused, for the builder to resolve.
2. Rebuilds the committed catalog (`ecom-generate build --out golden-catalog`), the
   pinned price figures and the 100K build's sizes (`measured_builds.py`, gen#85) and the
   pins the tests read on the catalog (`measure_pins.py`, gen#513), and commits only
   `GENERATED`. A file still conflicted, or any other change in the tree, is refused. uv
   runs `--locked`, so a stale `uv.lock` is refused rather than re-locked into the commit.
   The retail totals are not here: nothing under `golden-retail/` is committed (gen#536),
   a test measures them.
3. Runs the drift, golden, seam and README size tests (`CHECKS`) on that tree, on several
   pytest workers (`local_ci_jobs.py --pytest-options`, #348), and refuses a run in which
   no test passed (pytest exits 0 on all-skipped).
4. Pushes the merged and rebuilt tree to the PR branch, if it differs from the PR head.
   Not forced: a head that moved refuses the push.
5. Waits for every CI check on exactly that commit (the PR's own CI: lint, the whole
   suite, the commit messages) and refuses unless each is green, or skipped by design
   (`REQUIRED_CI`, `SKIPPED_BY_DESIGN_CI`). `--local-ci` and `--github-ci` replace the
   wait: see below. Either way the end prints the merge's wall time (`gen-merge-minutes`).
6. Squash-merges, re-checking before EVERY attempt that main has not moved since step 1
   and that the PR head is still the checked commit. A read that is not the expected sha
   is repeated, up to 3 reads 10 s apart (`MERGE_PR_HEAD_SLEEP`), before the ref is called
   moved: `ls-remote` right after a push can answer from before it (#383).

## Step 5 with `--local-ci`

With `--local-ci` (or `GEN_LOCAL_CI=1`, which makes it the default) step 5 waits for
nothing on GitHub: GitHub Actions here is billing-blocked, so CI is run locally. It runs,
on that same merged-and-rebuilt tree, every job of `.github/workflows/*.yml`, each as the
workflow runs it (the same `run:` commands, in a `bash -eo pipefail` shell at the tree's
root), found by `scripts/local_ci_jobs.py` and not by a hand list.

Every job runs; each one's verdict, duration and log (outside the clone, named
`<label>-<job>.log` in `$MERGE_PR_LOG_DIR`, default `/tmp`; `--label` sets the label,
default the checkout's directory name) is printed; the merge is refused unless every job
passed. A red job also prints its FAILED/ERROR summary lines (at most 20) and its log is
copied to `<kept dir>/.git/ci-logs/`, so the failing test is named without a re-run
(#453). No GitHub check is read.

Each job's pytest runs on several workers, grouped by file (`local_ci_jobs.py` adds `-n`
and `--dist loadgroup`; `LOCAL_CI_WORKERS` sets the count): the suite took 47 to 54
minutes on one core, and merges are serial (#348). Each of those commands (the step-3
checks too) runs under `scripts/local_ci_guard.py` (#366): the process tree it starts is
held to workers x 4,500 MB (`LOCAL_CI_MEMORY_MB` replaces the ceiling) and the job is
stopped, and so red, when it passes it; and one local CI command runs at a time on the
machine (`LOCAL_CI_LOCK`), a second waiting, a `--dry-run` included.

A local CI that is red only on the golden freshness tests (`FRESHNESS_TESTS`: every
FAILED or ERROR line of every red job names one of them, and no other job is red) is not
handed back for a fixer round (#440): the generated files are rebuilt on the same tree
(the step-2 build), committed as "regenerate golden on main", every job runs again, and
only a green second run is pushed and merged. Once: a second red stops. Any other red, or
a freshness red the rebuild does not change, stops the merge as before.

## Step 5 with `--github-ci`

With `--github-ci` (or `GEN_GITHUB_CI=1`; #348) step 5 runs the same workflow on
GitHub-hosted runners, where the tests job is sharded over several of them
([ci-sharding.md](ci-sharding.md)): the merged tree is pushed to a throwaway branch
`ci/merge-<N>` (forced: it is ours alone), the workflow is dispatched on it with the base,
head and PR number as inputs, and the script waits for the run. Each `REQUIRED_CI` job
must have passed. A red run prints each failing job, its URL and its FAILED/ERROR lines
(the same freshness-only regeneration as `--local-ci` applies, once). The throwaway branch
is deleted on every exit.

Because the same tests run in the shards, step 3 is skipped, and step 4 (the push to the
PR branch) comes AFTER the green run, so a red tree never lands on the PR. `--local-ci`
stays as the fallback for a GitHub that is down or out of minutes.

## One merge at a time

One merge at a time (#383): a run takes a lock (a directory, `MERGE_PR_LOCK`, default
`/tmp/merge-pr-<repo>.lock`) before it reads the PR and main, and keeps it to its last
step, so a merge that lands during another's 11 to 47 minute CI run no longer moves main
under it and forces a rerun. A second run prints that it is waiting, polls every
`MERGE_PR_LOCK_POLL` seconds (default 10) and gives up after `MERGE_PR_LOCK_WAIT`
(default 14400, 4 h). A lock whose holder's pid is gone (a killed run) is taken over.
`--dry-run` pushes and merges nothing, so it takes no lock.

Step 6 narrows the window but cannot close it: GitHub has no compare-and-swap on the base.
The CI job `main-merged-tree` runs `CHECKS` on every push to main, so a merge that raced
(or bypassed the script) shows red on main at once.
`tests/test_merge_pr.py::test_main_merged_tree_job_is_red_on_a_broken_main` proves it: per planted
edit it runs the job's run line narrowed to the one check that catches that edit (`-n 0 -k`), and asks
for that check's `FAILED` line, so it costs seconds rather than two builds (#824).
