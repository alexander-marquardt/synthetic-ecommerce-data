# Dependency review

<!-- audience: internals -->

What this repository's direct dependencies are for, and whether each is kept (#1180). The rows are in [the table](appendix/dependency-review-table.md), which core's `scripts/dependency_review.py` renders. The use, verdict and rule of a row are review, in `scripts/dependency_review_data.json`. The columns and the verdict rules are core's: `docs/internals/dependency-review.md` and `contributing/dependencies.md` in elastic/prism.

This repository has no Dockerfile, so it has no images page. The verdicts are those of 2026-11-25, when the table was first written.

## CI checks it

The `dependency-review` job of `.github/workflows/ci.yaml` is a required check. It installs the dev group and every extra `--extras` lists, then runs `--check`, which exits 1 when the committed table differs from what the tree renders. Core is private and this repository holds no secret that reads it, so CI cannot check core out as `../prism`. The job runs a copy of the review's scripts under `.github/dependency-review/` instead, pinned by its `PIN.json` (the core commit and each file's SHA-256), and checks the pin first, as `.github/vuln-gate/` does for the vulnerability gate.

The table counts the call sites of each dependency, so the check also goes red on a new or removed import of one, a new test file's `import pytest` included. Rerun `--write` and commit the page:

```bash
uv run python .github/dependency-review/scripts/dependency_review.py --root . --write
```

The copy's `--check` prints core's `../prism` command; the line above is the same render. The copy is never edited here. To take a newer core, run `python3 .github/dependency-review/verify_pin.py --update <a core checkout>` (add `--commit <rev>` for one revision), rerun `--write` and commit both.

## Rerun it

From this repository's root, with core checked out beside it as `../prism`:

```bash
uv sync --all-extras
uv run --project ../prism python ../prism/scripts/dependency_review.py --root . --refresh
uv run --project ../prism python ../prism/scripts/dependency_review.py --root . --images
uv run --project ../prism python ../prism/scripts/dependency_review.py --root . --write
uv run --project ../prism python ../prism/scripts/dependency_review.py --root . --check
```

`--refresh`, `--images`, `--write` and `--check` are one mode each. `--refresh` asks the OSV database and the package index, and `--images` builds each Dockerfile's image, so both need the network; `--write` and `--check` read only what is committed.

Rerun `--write` after a change to `pyproject.toml` or `uv.lock`, or to an import of a dependency, because the table counts the call sites. A new dependency also gets its use, verdict and rule in the data file first, and a version bump needs `--refresh`.
