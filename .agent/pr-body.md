<!-- pr-body-for: branch=issue-348-github-ci -->
Refs #348
Refs #453

DRAFT, HANDOFF: not finished. Head 4ac77ed on `issue-348-github-ci`.

What is on the branch (each shown by the command named):
- `.github/workflows/ci.yaml`: `lint` job split out; `tests` is a matrix of 6 shards on ubuntu-latest, each `pytest -n auto --dist loadgroup` over `scripts/ci_shards.py --shard K --of N`; the four PR jobs run on `workflow_dispatch` with `base`/`head`/`pr` inputs. Workflow enabled (`gh workflow enable CI`, done 10-17 ~14:55Z).
- `scripts/ci_shards.py` + `scripts/ci_shard_weights.json` (measured), `docs/ci-sharding.md` (defines `gen-merge-minutes`), guard `tests/test_ci_shards_348.py`.
- `scripts/merge_pr.sh --github-ci` (throwaway branch `ci/merge-<N>`, dispatch, wait, FAILED lines + run URL on red, PR branch pushed only after green, branch deleted on exit), tests `tests/test_merge_pr_github_ci_348.py`; `local_ci_jobs.py` reads the shard matrix as the `all` shard for `--local-ci`.

Measured (gh run 39043039568, first sharded run, default weights; `gh run view 39043039568 --json jobs`): shard wall times 4m22s, 5m16s, 7m29s, 10m10s (3 and 4 of 6) and 22m40s for the shard holding `tests/test_merge_pr.py` (3,562 s of test time by itself). Everything else sums to about 9,500 s of test time: 10 shards would be about 1,070 s each.

Not yet shown (next steps, in order):
1. Split `tests/test_merge_pr.py` across shards (its tests are independent; `XDIST_SPREAD = True`): e.g. a conftest hook deselecting that module's items by index modulo `CI_SHARD`/`CI_SHARDS` env set in the workflow, with `ci_shards.py` listing the file in every shard and the guard adjusted to "each test exactly once". Then pick N from a new run so the slowest shard is under 8 min (likely 8 to 10).
2. Run the new test files and `tests/test_merge_pr.py` through `agent_heavy` (none of the new tests has run yet: only CI's first run on an older commit); the fixes since that run (junit to runner temp, `a || b` in the pre-push gate, pins of the PR-job `if`/range text, the stale-lock case online on a runner, REQUIRED_CI gaining `lint`) are untested.
3. Red commit / mutants for the new guards (`scripts/mutation_check.py --only`), Guard:/Efficiency-Metric: lines below.
4. Three real merges through `--github-ci`, each under 15 min, with the `gen-merge-minutes:` lines. Then switch `~/Documents/agent-ops/coordinator/vm_genchain.sh` line 10 (`bash scripts/merge_pr.sh --local-ci $n` -> `--github-ci`; the copy the VM runs is `~/.prism/coord/vm_genchain.sh`).

Guard: tests/test_ci_shards_348.py (matrix covers every test file once; no CI job runs pytest without -n)
Efficiency-Metric: gen-merge-minutes (docs/ci-sharding.md), before about 55, target under 15

Docs-Impact: docs/ci-sharding.md, docs/pre-push-gate.md (rows now read the lint job)
