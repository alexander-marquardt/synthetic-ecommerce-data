# The review-verdict check

A pull request merges only on an independent review verdict that is bound to its
head commit (agent-ops#111). This is the same check
elastic/prism runs. The file `.github/scripts/check_review_binding.py` is
byte-identical in each repository that carries it; only the tier routes differ.

## The comment

The reviewer posts one comment (or a review body) with three lines. Bold is
allowed; the colon sits inside it. A line that starts with `>` is a quote, not a
verdict.

```
Review-Verdict: ARM
Reviewed-Head: <the full 40-character sha>
Tier: <docs | ui | gate-or-test | rulebook | production-runtime>
```

The newest verdict by a non-bot author decides. `FIX` and `BLOCK` fail the check.

## What passes

- the verdict is `ARM` and `Reviewed-Head` is the PR head; or the head moved but
  the PR's own diff did not (a rebase has the same patch id), or the only files
  that differ are listed as `generated` in the tiers file and exist at the merge base;
- `Tier` is at or above what the changed paths need.

## Tiers

`.github/review_verdict_tiers.json` lists the tiers shallow to deep and the path
patterns of each (`*` crosses `/`). A path takes the deepest tier of any pattern
naming it. A path no pattern names is charged the deepest tier, so a new source
directory needs no edit to be safe. The file's `generated` list names the files a
build writes: only those, never a lock file, a combined file or a whole data directory.

Changed paths are read with `git diff --name-only --no-renames -z` and
`--literal-pathspecs`. A name with a non-ASCII byte or a glob character is therefore
the file it is, and a rename counts as both of its paths. A diff that differs while no
path accounts for it is a changed diff, never a generated-only one; a path list git
cannot produce is "could not judge". A review with no submit time is the oldest entry,
and a pending review is not a verdict.

## The workflow

`.github/workflows/review-verdict.yaml` has two jobs:

- `review-verdict` runs on `pull_request` and `merge_group`. It checks out the
  repository and runs the script with read-only scopes. Exit 0 passes, 1 fails, 3
  means the check could not judge (a read failed), which is also red.
- `review-verdict-rerun` runs when a comment or review containing `Review-Verdict:`
  is posted. A comment does not start a `pull_request` run, so this job re-runs the
  latest run on the PR head. It holds `actions: write`, checks nothing out and runs
  nothing the pull request wrote.

## Making it required

The workflow does not make the check required. That is a branch-protection or
ruleset edit by an admin, after the check has run on `main` once. Until then the
check reports on every pull request and blocks none.

## Tests

`tests/test_review_verdict_check.py` covers the comment grammar, the judge rules,
the tier routes of this repository, the delta against a temporary git repository,
the exit codes, `load_facts` against a fake `gh` and a local origin, and the shape of the
workflow (triggers, token scopes, pinned actions). `tests/test_review_verdict_tiers_pin.py`
pins this repository's routes and its `generated` list.
