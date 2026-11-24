# The direct-dependency allowlist (#1106)

`.github/dependency_allowlist.json` names every direct dependency of every `pyproject.toml` and
`package.json` in this repository, by manifest and group. Each dependency brings its transitive
tree and its advisories with it, so the list only shrinks unless the maintainer approves.

## What the check refuses

Every pull request and every push to main runs `dependency-allowlist`
(`.github/workflows/dependency-allowlist.yaml`). On every event it fails on:

- a dependency a manifest declares that the list does not name;
- a stale entry (on the list, in no manifest), so a removal shortens the list in the same PR.

On a pull request it also compares the tree with the base's and fails on a new entry, on more
entries than the base's list, and on a `uv.lock` (or `package-lock.json`) with more packages than
the base's, unless the PR carries the label `dependency-approved`. The label is the maintainer's
approval: the maintainer adds it, or an agent the maintainer asked adds it. Adding or removing it
runs the check again. Until main holds the list there is no base to compare with, so the PR that
added it passed on the first two rules alone.

The list records no lock total: two PRs that each drop a package would record the same total and
merge into a lock with one fewer (elastic/prism#16760). The job counts the locks of both trees and
its summary prints them beside the number of entries.

`dependency-allowlist` is a required check: `.github/required-checks.json` names it, so agent-ops'
shared gate refuses a merge until it is green at the pull request's head. Its first run on main
took 14 seconds. `merge_pr.sh` does not add it to its own `REQUIRED_CI`, which is `ci.yaml`'s jobs.
A head last pushed before the workflow reached main has no run and is refused as absent: a push,
a merge of main into it, a reopen or a label added or removed starts one.

## Clearing a red

- **You removed a dependency:** run `python3 .github/scripts/check_dependency_allowlist.py --write`
  and commit the shorter list.
- **You need a new one:** first ask whether the standard library or a listed dependency does the
  job. If not, add it, run `--write`, state the reason in the PR body and ask the maintainer for
  the label.

A version range, URL or git pin is not listed, so changing one passes. A bump that pulls in new
transitive packages raises the lock's count and needs the label.

## Where it comes from

The check is elastic/prism's (elastic/prism#16448, its `contributing/dependency-allowlist.md`).
This public repository cannot call a private repository's workflow, so it runs a copy:

- `.github/scripts/check_dependency_allowlist.py` is core's script byte for byte. It imports only
  the standard library. Ruff skips it (`extend-exclude` in `pyproject.toml`).
- The workflow's last step is the check step of core's `reusable-dependency-gate.yaml`, word for
  word. The step before it links the script, and the `retry.sh` of the vulnerability gate's copy
  ([docs/vulnerability-gate.md](vulnerability-gate.md)), to the paths core's step reads.

`tests/test_dependency_allowlist_1106.py` holds both to the core commit it names and runs the
committed steps against a throwaway repository. `merge_pr.sh --local-ci` skips the workflow
(`NOT_A_CHECK` in `scripts/local_ci_jobs.py`): it reads the pull request's labels from the event.

### Update it

In a checkout of elastic/prism at the commit to copy, take
`.github/scripts/check_dependency_allowlist.py` and the last step of
`.github/workflows/reusable-dependency-gate.yaml` together, since the step passes the script's own
flags. Set `CORE_COMMIT`, `CORE_BLOB` (`git ls-tree <commit> -- <script>`) and `STEP_SHA256` in the
test, and name the commit in the commit message. Then run `--write`.
