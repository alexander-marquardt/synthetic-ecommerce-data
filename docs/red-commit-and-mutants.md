# Red commit first, and mutants on the changed lines

Two checks from elastic/prism (elastic/prism#11680, lever #10028) that prove a
new test can fail. A test that cannot fail merges as coverage and tells nobody
anything.

## The red commit

A change that fixes a bug or adds behavior starts with a **red commit**: the
new or changed test plus the smallest stub that makes it fail on an
_assertion_ (not an import or collection error). The commit message ends with
`Refs #<issue>`, a blank line, then one `Red-Test: <test id>` line per test:

```
Refs elastic/prism#11680

Red-Test: tests/test_x.py::test_new_behavior
Red-Test: tests/test_x.py::test_case[one, two]
```

A parametrized case is named by its own id; the commas and blanks inside
`[...]` belong to the id. The fix follows in later commits. A refactor, a docs
change or the fix itself carries no trailer, or `Red-Test: none - <reason>`.

CI's `red-commit-proof` job (`scripts/red_commit_proof.py`) checks the claim
on every commit a pull request adds. For each commit that names tests it
checks the commit's tree out in a throwaway worktree, runs only those tests,
and is red unless each one failed on an assertion in its own call phase. It
names the id of a test that:

- passes, so it is not red;
- fails on anything else: a collection or import error, a fixture or teardown
  error, another exception, a timeout, or an assertion raised in the code
  under test rather than by the test;
- matches no test that ran (a typo, a skip, a missing file);

and a token that is not a `path.py::name` id (prose, a sha). A commit with no
trailer runs nothing, so a pull request that declares no red commit costs the
job a few seconds. Run it before you push:

```sh
uv run python scripts/red_commit_proof.py --range origin/main..HEAD
```

Exit 0: every declared red commit is proven, or none is declared. 1: a
refusal, with the id and why. 2: the range is empty or does not resolve. 3: a
commit could not be judged (pytest wrote no outcomes, or ran past 900 s).

A red commit made before the checker landed is grandfathered (gen#432). When
the commit is not a descendant of `CUTOFF` in `scripts/red_commit_proof.py`
(`e4813a393cfbc4cdd757adefac8258977f792990`, the commit that introduced the
checker), a named test that fails on anything, such as `StopIteration`,
`KeyError` or an error at setup, is accepted as red and the line says
`GRANDFATHERED`. The cutoff is ancestry, not an author date: a rebase or a
wrong clock moves a date and never moves ancestry. A test that passes or
matches no test is refused on either side of the cutoff, and a descendant of
the cutoff keeps the strict rule. A cutoff the clone does not hold grandfathers
nothing. `--cutoff <sha>` names another commit, for a test's throwaway repository.

The job does not _require_ a trailer: that a fix has a red commit is a review
question, as in elastic/prism. It makes a trailer that is there true.

`merge_pr.sh --local-ci` runs the job like every other job of the workflow.

## Mutants on the changed lines

After the fix is green, show that each changed line is held by a test: plant a
small defect on it, run the tests that should notice, and expect them to fail
on an assertion. The runner is elastic/prism's `scripts/mutant_run.py`, not a
second one; it sits under `vendor/prism/scripts/` with its two companions,
byte for byte (`vendor/prism/PIN.txt`). It starts the tree's tests with its
own interpreter, so start it with this repository's:

```sh
uv run python vendor/prism/scripts/mutant_run.py <mutants file> --root <clone>
```

`<mutants file>` is a Python file the runner reads and never executes. Keep it
out of the tree (`.agent/`, `/tmp`); it is the receipt a reviewer re-runs.

```python
TESTS = ["tests/test_commit_msg_check.py"]
MUTANTS = [
    # (path under --root, text to replace, replacement, name)
    ("scripts/check_commit_msg.py", "if skip_comment_lines:", "if not skip_comment_lines:", "skip-flag-inverted"),
]
```

A row whose `old` text occurs zero times or more than once is refused, never
applied. Each row ends `KILLED` (a test failed on an assertion), `SURVIVED`
(every test passed: add the test, or say why the line is equivalent), `ERROR`
or `NOT-TESTED` (no test judged it), or `REFUSED`. The last line reads
`N of M killed`. The file's full format, the guarantees (the file is restored
byte for byte; one run per checkout; a killed run leaves a journal the next run
reads) and the verdicts are the docstring of `vendor/prism/scripts/mutant_run.py`.

`tests/test_vendored_mutant_runner_11680.py` runs the vendored copy on a small
repository, so the one thing that is this repository's, starting it with the
right interpreter against another root, stays tested.

`scripts/mutation_check.py` is a different tool and stays: a curated bed of
defects planted in this generator's rules, guarded by
`tests/test_mutation_bed.py`. It is not a run over what a change touched.

## Resync

Both checks use files of the vendored copy: `mutant_run.py`,
`mutant_run_plugin.py` and `bounded_process.py`. They resync with the file-size
gate, in one step, from a core clone:
[Resync the vendored gate](file-size-budget.md#resync-the-vendored-gate).
