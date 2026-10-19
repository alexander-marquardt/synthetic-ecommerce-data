<!-- pr-body-for: branch=issue-62 -->
Closes #62

## Overlap with #560 (read first, head 3d79c685)

#560 (issue-85) generates the large build's `lines`, `skus` and `skus_by_type` into `core/data/measured_builds.json` and turns the README table and totals into a pointer to it. That covers #62's second bullet (generated SKU figures) and, with `tests/test_measured_figures.py`, the third (a typed figure is refused). It does not rename the setting, and it leaves the "lands at about 100,000 SKUs" sentences and the SKU totals typed in `config.py`. Only that remainder is built here, branched from main.

Files shared with #560: `README.md` (my lines 20-21 and 305-307 are two lines from #560's hunk at 298-319; if git reports a conflict take #560's table paragraph and my two sentences), `scripts/fit_price_model.py` and `tests/test_price.py` (one-word rename, in import lines and one docstring/test each). Nothing else.

`HUNDRED_K_LINES` stays as an alias of `LARGE_BUILD_LINES` in `config.py`, because #560's `measured_builds.py` imports the old name and would break on import if this lands first. Whichever of the two lands second should drop the alias and switch that import.

## What changed

- `config.LARGE_BUILD_LINES = 39000` names the setting for what it holds. The comment above it no longer types SKU totals (99,929 to 122,324); the default-lines comment no longer types "about 4,700 SKUs". Both point to `skus` in a build's `stats.json`.
- README: the intro and "The 100K catalog" no longer promise a total and name `config.LARGE_BUILD_LINES` (also in the price-realism section). The heading keeps its name, because four places link to its anchor; see DID YOU MEAN.
- `tests/test_facet_control_rule.py`: a comment's typed "(122,324 SKUs)" removed.

## Evidence

- Red commit 52ef1c83 (`tests/test_large_build_name_62.py` only): `pytest tests/test_large_build_name_62.py` under `agent_heavy`: 4 failed on assertions (`None == 39000`; README names `HUNDRED_K_LINES`; config types `['4,700 SKUs', '100,000 SKUs', '99,929 SKUs']`; README promises `['about 100K SKUs', 'about 100,000 SKUs']`).
- Fix: the same file plus `tests/test_measured_figures.py`, `tests/test_facet_control_rule.py`, `tests/test_retail_figures_162.py`: 62 passed. `tests/test_price.py` was only collected (238 tests, imports resolve); its builds are heavy and the change there is a rename.
- `scripts/mutation_check.py --only "large build:"` under `agent_heavy`: 5 of 5 caught by every test they name (rows in `scripts/mutation_rows_large_build_62.py`).
- No SKU, style or price moved: no generator code changed; the only `src/` change is `core/config.py` comments and the new constant.

## DID YOU MEAN

- DID YOU MEAN: should the README heading "The 100K catalog" and its anchor `#the-100k-catalog` also be renamed (for example "The large build")? The anchor is linked from README (lines 21, 1003), `docs/adding-a-type.md` and `tests/test_retail_figures_162.py`, and #560 edits the same doc row, so it is left for after #560.

Docs-Impact: README changes in this PR (the intro, "The 100K catalog", the price section).
