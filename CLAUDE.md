One line per directive; the detail is behind each pointer. This file loads on every agent call, so add a pointer, not a paragraph.

- README.md is about 95 KB and docs/adding-a-type.md about 49 KB: `grep -n '^## '` for the section you need and read only that range.
- Run the tests your change touches, not the whole suite (about 27 minutes serially; CI runs it): [README → Contributing](README.md#contributing).
- A test that outlives the per-test timeout fails rather than growing; raise it for that test alone with `@pytest.mark.timeout(<s>)` (README → Contributing).
- Lint as CI does: `uv run --locked ruff check .`.
- Add or move a product type: [docs/adding-a-type.md](docs/adding-a-type.md).
- Merge with `scripts/merge_pr.sh <PR>`, never the GitHub button: README → Contributing.
- No AI or bot credit in a commit message; the commit-msg hook and CI refuse it: README → Contributing.
