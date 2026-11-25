# Dependency review

<!-- audience: internals -->

What this repository's direct dependencies are for, and whether each is kept (#1180). The rows are in [the table](appendix/dependency-review-table.md), which core's `scripts/dependency_review.py` renders. The use, verdict and rule of a row are review, in `scripts/dependency_review_data.json`. The columns and the verdict rules are core's: `docs/internals/dependency-review.md` and `contributing/dependencies.md` in elastic/prism.

This repository has no Dockerfile, so it has no images page. The verdicts are those of 2026-11-25, when the table was first written.

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
