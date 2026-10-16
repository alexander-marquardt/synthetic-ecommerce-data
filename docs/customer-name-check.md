# Customer-name check

No customer name appears in this repository (alexander-marquardt/synthetic-ecommerce-data#393,
the generator half of elastic/prism-industrial-products#88). Before this check,
only a reviewer's grep kept a customer-derived token out, and a reviewer's grep
once called a surviving lockfile entry a false positive.

## What it scans

`scripts/check_customer_names.py` scans four surfaces and prints
`customer-name-check: HIT <place> [<row>]` for each hit:

| Surface                           | How it is read                                                                      |
| --------------------------------- | ----------------------------------------------------------------------------------- |
| The tree                          | every tracked file, and every untracked one `.gitignore` does not hide              |
| A file's path                     | the same list, by name                                                              |
| The commit messages of a range    | `--range <rev>..<rev>`; a path or a bare rev is refused (exit 2)                    |
| The pull request's title and body | `--pr <number or head branch>`, read live with `gh pr view` (CI); `--text-file` for a draft |

A file that is not text (it does not decode as UTF-8 and holds a NUL byte, as an
image does) is scanned by its path only, and the run names it. A file that
decodes and holds a NUL byte is text and is scanned. The report gives the place
and the row, not the line, so the log of a failed run does not carry the name.

Exit status: 0 clean, 1 a hit, 2 a usage error, 3 could not judge (a `gh` that
did not answer, a range git cannot resolve). A run that could not judge is never
a pass. A hit is a hard block with no justification line.

## One list, core's

The names are `CUSTOMER_NAME_SPECS` in elastic/prism's
`.github/scripts/audit_grep_diff.py`. This repository's CI cannot read the private
core repository, so the file sits under `vendor/prism/` byte for byte, with the
module it imports (`scripts/invisible_characters.py`), at the commit
`vendor/prism/PIN.txt` names. That is the same commit and the same two files
elastic/prism-industrial-products vendors, so there is one list.
`tests/test_vendored_core_pin_11683.py` refuses a copy that differs from the pin,
and `tests/test_customer_name_check_393.py` refuses a script that holds a pattern
of its own, or a row of core's list that has no planted sample there. To pick up
a new row, resync as [file-size-budget.md](file-size-budget.md#resync-the-vendored-gate)
describes (the file list includes `.github/scripts/audit_grep_diff.py` and
`scripts/invisible_characters.py`), and add a sample for the new label to
`SAMPLES` in the test. Resync both repositories to the same commit.

`scripts/check_customer_names.py` is a copy of elastic/prism-industrial-products's
script of the same name: a fix to one belongs in the other.

What the list does not match is a limit of the list, not of this check: a name
glued to a word with no separator (a package directory that joins the two words)
is not a row of core's list today.

## Where it runs

- CI: the `customer-name-check` job in `.github/workflows/ci.yaml`, on every pull
  request. It names the PR by its head branch, as the `file-size` job does, so
  `scripts/merge_pr.sh --local-ci` can run it: the local run takes only the base
  and head shas from the event, and exports the job's `GH_TOKEN` empty so the
  signed-in `gh` answers (`scripts/local_ci_jobs.py`). It reads the title and
  body when the job runs, so a body edited after the run is read on a re-run, not
  on the edit.
- The pre-push gate ([pre-push-gate.md](pre-push-gate.md)): the `customer-names`
  row runs CI's command over the branch's range, without `--pr` (there is no PR
  yet), and over the draft body when `--pr-body-file` is given. Without a body it
  says so: the PR text was not judged.
- Locally: `uv run python scripts/check_customer_names.py` scans the tree.
- Not a required check of `merge_pr.sh` (`REQUIRED_CI`), which names the checks a
  pull request must carry green on GitHub; `--local-ci` runs every job of the
  workflow, this one included.
