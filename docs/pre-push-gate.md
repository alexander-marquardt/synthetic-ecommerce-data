# Pre-push gate

`scripts/prepush.sh` runs this repository's cheap CI jobs on the branch before anyone
reviews it, so a red that CI would find costs seconds at the keyboard and not a CI round
plus a fix round of an agent's context (elastic/prism#11677, lever #10005 of #10032).

## Rows

Each row runs the command a job in `.github/workflows/ci.yaml` runs, read from the
workflow by `scripts/local_ci_jobs.py` when the gate starts (no copy is kept here), so a
stricter CI flag or `--locked` reaches the gate with no edit. `python3 scripts/prepush.py --list`
prints each row, its CI job and the command it runs, then what is left to CI.
`tests/test_prepush_gate_11677.py` fails when a job or step of the workflow is neither
claimed by a row nor named in `LEFT_TO_CI` in `scripts/prepush.py`.

| Row | CI job | What it judges |
|---|---|---|
| `commit-messages` | `commit-messages` | no AI or bot attribution in the commits since the merge base with `origin/main` |
| `customer-names` | `customer-name-check` | no customer name in the tree (every file's path and content), in the commit messages since the merge base, or in the draft PR body (`--pr-body-file`); [customer-name-check.md](customer-name-check.md) |
| `lint` | `lint` | `uv run --locked ruff check .` |
| `file-size` | `file-size` | no file over the cap grew; a growth needs the PR body (`--pr-body-file`), else the row is a `WARN` and the review packet says it was not judged |
| `tree-scans` | `tests` (Tests step, without its shard files) | the tests that read every tracked file: US spelling, the `.ignore` patterns, the vendored core pin (`python3 scripts/prepush.py --list-scans`) |

Left to CI, by name: the whole suite (about 27 minutes), and the golden catalog and the
merged-tree checks (the `main-merged-tree` job), which `scripts/merge_pr.sh` runs on the
merged tree, and the `red-commit-proof` job, which needs the pull request's base and head
(`docs/red-commit-and-mutants.md`). The review packet repeats this list.

## Running it

```
scripts/prepush.sh                          # by hand: blocking, prints a review packet
scripts/prepush.sh --pr-body-file BODY.md   # also judge the file-size row against the PR body
scripts/prepush.sh --only lint              # re-run one row after a fix
```

A row prints `    PASS|FAIL|WARN  <name>`; a failed row shows the tail of its output.
The last line is `PREPUSH rc=N failed=<rows> log=<path>`; the log and the review packet
are saved under the git directory (`prepush.log`, `prepush-packet.md`). A gate that could
not run (no `origin/main`: `git fetch origin main`; no `uv`; a scan set in which no test
ran) fails; it never reports a pass it did not earn. On a pass the packet lists what each
row judged, with three `<FILL` lines for the author: claims, repro commands, mutants.

## The hook

`pre-commit install` installs the `prepush-gate` hook (`bash scripts/prepush.sh --hook`).
It judges the checkout at HEAD, with unstaged edits stashed by pre-commit; untracked
files are in reach of `ruff check .` as in CI.

- A branch with an **open pull request**, and `main`, are blocked on a red row.
- A branch with none runs every row and ends `ADVISORY — NOT A PASS`, exit 0, no packet:
  a work-in-progress push is never refused.
- A pull-request lookup that fails blocks, and says why.
- A push to `wip/<task>` is a backup: the commit-message rule only, then
  `NOT JUDGED (wip backup)`. A branch delete is not judged.
- A push of a commit other than the checkout's HEAD fails the `pushed-commit` row: the
  gate judges the checkout, not the commit named on the command line.

A deliberate skip is `SKIP=prepush-gate git push`, which pre-commit prints; CI runs every job
regardless.
