One line per directive; the detail is behind each pointer. This file loads on every agent call, so add a pointer, not a paragraph.

- README.md is about 95 KB and docs/adding-a-type.md about 49 KB: `grep -n '^## '` for the section you need and read only that range.
- Run the tests your change touches, not the whole suite (about 27 minutes serially; CI runs it): [README → Contributing](README.md#contributing).
- A test that outlives the per-test timeout fails rather than growing; raise it for that test alone with `@pytest.mark.timeout(<s>)` (README → Contributing).
- US spelling (`color`, `colorway`); `tests/test_us_spelling.py` refuses the British spelling in any tracked file.
- Lint as CI does: `uv run --locked ruff check .`.
- Before review run `scripts/prepush.sh [--pr-body-file BODY]` (the pre-push hook runs it too): the cheap CI jobs, in seconds: [docs/pre-push-gate.md](docs/pre-push-gate.md).
- Add a retail type (one spec file, `scripts/new_type.py`; at most three types per issue): [docs/new-type-quick-path.md](docs/new-type-quick-path.md).
- Add or move an industrial product type: [docs/adding-a-type.md](docs/adding-a-type.md).
- Until #127 merges, the shared core (`src/synthetic_ecommerce_data/core/`) lives on branch `extract-core-125`: base core work on it, not on `main`.
- Merge with `scripts/merge_pr.sh <PR>`, never the GitHub button: README → Contributing.
- No AI or bot credit in a commit message; the commit-msg hook and CI refuse it: README → Contributing.
- A file over 1,750 lines may not grow (`scripts/file_size_gate.py`, core's gate): split it, or add a `File-Size-Exception:` line to the PR body: [docs/file-size-budget.md](docs/file-size-budget.md).
- A fix starts with a red commit (`Red-Test:` trailer, proven by CI's `red-commit-proof` job), and its changed lines get mutants from core's vendored runner: [docs/red-commit-and-mutants.md](docs/red-commit-and-mutants.md).
