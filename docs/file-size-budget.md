# File-size budget

A code or prose file may hold at most **1,750 lines**, the one number in
[`scripts/file_size_cap.txt`](../scripts/file_size_cap.txt). The rule is
elastic/prism's (`contributing/file-size-budget.md` there), run on this tree
(elastic/prism#11683):

**A file over the cap may not have more lines than it had at the merge base.**

- A new file counts as zero lines at the merge base, so a new file over the
  cap is refused, and so is a file a change pushes across it.
- A file `main` already holds over the cap passes until a change grows it. No
  per-file size is checked in: the merge base records each one. On the day the
  gate landed three files were over it: `scripts/mutation_check.py` (3,468
  lines), `src/synthetic_ecommerce_data/domains/industrial/generate.py` (2,295)
  and `README.md` (2,095). `generate.py` is no longer one of them: it was
  split by concern (#266) into `generate.py` (the builders and the build loop,
  about 1,260 lines), `finishing.py` (line finishing and attribute assembly),
  `defects.py` (defect injection), `titles.py` (titles and descriptions) and
  `drafts.py` (the draft shapes and the tables they share). `Generator`
  inherits one mixin from each of the first three, so every method keeps its
  name and every importer keeps `from ...industrial.generate import ...`.
  `README.md` is now under the cap: its retail
  prototype reference moved to [`retail-prototype.md`](retail-prototype.md) (#240),
  where a retail type batch adds its listing line.

Why: an agent looking for one spot in a big file reads a large part of it, and
what it reads stays in its context for every later step.

## What it measures

Every tracked file, and every untracked one `.gitignore` does not hide, with a
code or prose suffix (`.py`, `.sh`, `.md`, `.js`, `.ts`, `.css` and their
kin), anywhere in the tree but `vendor/`. Data files (JSON, YAML, CSV, NDJSON)
are outside it. Lines are counted as `bytes.splitlines` counts them.

## When it reds

1. **Split the file** along a real seam, so it is no bigger than at the merge
   base. Split by responsibility, not by line count: a task should read an
   overview plus one part.
2. **Or declare the growth**: one line in the PR body per grown file,
   ``File-Size-Exception: `<path>` - <reason>``. Raising the cap needs
   `File-Size-Exception: cap - <reason>`. The body is read as GitHub renders
   it, so a line in a code block or an HTML comment does not count.

Where it runs:

- `python3 scripts/file_size_gate.py` measures from `origin/main`; `--list`
  prints every file over the cap. Its first line ends with core's "Reported,
  not gated" sizes of `CONTRIBUTING.md` and `contributing/`, which this
  repository does not have, so they read as 0 lines; nothing is gated on them.
- The `file-size-warning` pre-commit hook names, at commit time, each line the
  body will need. It refuses an agent commit (`AGENT_TMP` set) that grows an
  over-cap file with no body named by `PRISM_PR_BODY_FILE`.
- The `file-size` job in `.github/workflows/ci.yaml`, which
  `scripts/merge_pr.sh --local-ci` runs before a merge. It reads the PR body
  (`gh pr view`) only when something grew, and is red when the gate cannot
  judge (exit 3), for example with the cap file missing.

## Why a vendored copy

`scripts/file_size_gate.py` runs core's `scripts/check_file_size.py`; it sets
only the measured scope, since this tree's layout is not core's. Core is a
private repository that this repository's CI cannot read, so the gate cannot be
fetched at run time. It sits under `vendor/prism/` with the core modules it
imports, byte for byte, at the commit `vendor/prism/PIN.txt` names.
`tests/test_vendored_core_pin_11683.py` refuses a vendored file whose git blob
id differs from the pinned one, so the copy cannot drift from core in place.
The same directory holds the customer-name list the
[customer-name check](customer-name-check.md) reads
(`.github/scripts/audit_grep_diff.py` and `scripts/invisible_characters.py`).
`.ignore` hides `vendor/` from search.

## Resync the vendored gate

From a core clone at the new commit `C`, with `FILES` the paths `PIN.txt`
lists (add any module core's gate newly imports):

```sh
for f in $FILES; do mkdir -p "vendor/prism/$(dirname "$f")"; cp "<core>/$f" "vendor/prism/$f"; done
```

Then set `commit C` in `PIN.txt` and replace its listing with
`git -C <core> ls-tree C -- $FILES`, and run
`PRISM_CORE_CHECKOUT=<core> uv run pytest tests/test_vendored_core_pin_11683.py tests/test_file_size_gate_11683.py`.
