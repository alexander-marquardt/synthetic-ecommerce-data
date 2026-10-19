<!-- pr-body-for: branch=issue-434 -->
Closes #434

## What it fixes

The issue names four gaps the policies read but the data could not answer. Three needed work here.

1. **UK sizes above 16**: no change. Main already carries the plus run (`grep -n UK_PLUS prototypes/retail_drawings/underwear_rows.py` shows `"8" ... "22"`).
2. **Knitwear sleeve length and neckline**: every Womens knit now states `sleeve_length`, and there are three quarter, short sleeve and cowl neck knits (`knit_sleeves.py`, `knitwear_rows.py`). Tests: `tests/test_retail_knitwear_sleeves_434.py`.
3. **Thin leaves**: Chips & Potatoes (1 held), Beds (6) and Womens Bomber Jackets (3) are brought to fifteen products each (`thin_leaf_rows.py`). Tests: `tests/test_retail_thin_leaves_434.py`.
4. **Attribute-word decoys**: a new class 8 in `decoy_apparel.py`, a product line named for a fit or shape the product is not ("Balloon Lane Skinny Jeans"), three decoys per value of leg_fit, rise and bra_shape. A bra now reads its title apart from its line (`facet_leaves.title_without_line`). Tests: `tests/test_retail_fit_word_decoys_434.py`.

## DID YOU MEAN

- (a) Roll neck is stored as `high` on main (#181), not as a separate value. Shown by `git grep -n '"Roll Neck"' origin/main -- prototypes/retail_drawings/knitwear_rows.py`, which gives `Style("Roll Neck", ..., "high", "roll_neck", ...)`. I kept `high` and did not add a `roll` value; the cowl neck is a new style on the same field.
- (b) The sleeve spelling is `Three quarter`, as the tops spell it. `samples.GARMENT_KEYS` says `Three-Quarter` (`grep -n Three-Quarter prototypes/retail_drawings/samples.py`, line 29). I followed the tops.
- Merged PR #156 is not built on here.

## SKU counts

Measured by `uv run python .agent/counts.py` (`len(scale.templates())` and the sum of `sku_count`; `scale.build(10**6)` for the ceiling), before and after.

| | Products | SKUs |
|---|---|---|
| Templates, main | 11,324 | 101,460 |
| Templates, this branch | 11,491 | 105,244 |
| Ceiling build, main | 16,359 | 166,990 |
| Ceiling build, this branch | 16,526 | 170,774 |

## Red first

Each gap has a red commit, with `Red-Test:` trailers, before its fix: gap 2 `1a424fa6`, gap 3 `d37044cf`, gap 4 `d33ff844`.

## Mutation checks

Each run is `scripts/mutation_check.py --only "<prefix>:"`, through `agent_heavy`:

- `knit sleeves:` 8 of 8 caught by every test they name.
- `thin leaves:` 6 of 6 caught.
- `fit word decoys:` 6 of 6 caught. The first run caught 5 of 6: `WORD_SYNONYMS = {}` survived, because placement avoids the other word by chance. `577e76bb` adds a direct test of `_same_word`, and the re-run caught it.

## Tests run

Two batches through `agent_heavy` with `-n 16` or fewer, covering the retail scale, figures, facet leaves, decoys, knitwear, thin leaves and output standards tests: all green. `agent_prepush` result is in the push step.

## Docs

`docs/retail-thin-leaves.md` (new: thin leaves and the class 8 decoys) and `docs/retail-knitwear-depth.md` (sleeve length and the cowl neck). No golden or stats outputs are committed (#536).

Docs-Impact: docs/retail-thin-leaves.md (new) and docs/retail-knitwear-depth.md (changed) are in this pull request.

Claims, each with the command that showed it: the SKU counts come from `uv run python .agent/counts.py`; each mutation count comes from `scripts/mutation_check.py --only "<prefix>:"`; `agent_prepush` rc=0 (tree-scans 14 passed, file-size against origin/main).
Repro commands: `uv run python scripts/mutation_check.py --only "knit sleeves:"` (and `"thin leaves:"`, `"fit word decoys:"`); `pytest tests/test_retail_knitwear_sleeves_434.py tests/test_retail_thin_leaves_434.py tests/test_retail_fit_word_decoys_434.py tests/test_retail_scale.py`.
Planted mutants: 20 planted (8 knit sleeves, 6 thin leaves, 6 fit word decoys), 20 killed.
