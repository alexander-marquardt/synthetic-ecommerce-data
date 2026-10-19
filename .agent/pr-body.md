<!-- pr-body-for: branch=issue-376 -->
Closes #376

Builds on #32 (the 45-brand realistic catalog, which made the 10K grocery build and its `ATTEMPTS` rule). The remainder named here: the 50K tier's range names and new invented brands (item 1 of #273).

## What changed

A grocery build of more than the 10K target is a tier. It draws range names from `LINES` plus 242 new ones (`grocery_rows.TIER_LINES`), and brands from the family's own plus 22 new invented brands per family group (`grocery_rows.TIER_BRANDS`). Each new brand has an `OWNERS` entry and a `house_styles` row with its own mark (`grocery_brand_styles.py`, imported last by `house_styles.py` as the luggage and color-word brands are). The tier shares the target over every family (depth families included, so the total is the target), gives a family 400 attempts instead of 40, and draws from a stream of its own. `docs/retail-prototype.md` (Grocery) names the tier and the command `python3 prototypes/retail_drawings/grocery.py --skus 50000 --out DIR`.

## Claims, each with the command that showed it

- 50K is reached and every family is at budget: seed 0 gave 50,105 SKUs (0.21% over) and 0 short families, from `.agent/probe1.py 50000` (before the change: 45,832 SKUs, 33 families short).
- The 10K build did not move: `.agent/digest.py` printed the same sha256 of `json.dumps(build(), sort_keys=True)`, of `build(2000, seed=3)` and of `build(10000, seed=1)` on main and on this branch (`da60e7b7...`, `d606ca64...`, `26e64e9e...`). The test `test_the_10k_build_does_not_read_the_tier_data` holds it by emptying the tier data.
- Tests: `agent_pytest tests/test_grocery_50k_tier_376.py tests/test_retail_figures_162.py prototypes/retail_drawings/test_house_styles.py tests/test_grocery_154.py tests/test_grocery_scent_depth_154.py` gave 109 passed, 1 failed with the stats file rolled by `scripts/roll_stats.py` (not committed, gen#373). The one failure, `test_house_styles.py::test_no_two_brands_share_a_mark`, names 10 pairs of marks shared by brands that are not in this PR (`diamond_grid`, `bubbles`, `fold` and seven more); `.agent/dup.py` printed the same 10 with the 22 new brands left out, so it is on main already.
- Red commit `aa06378a`: 6 tests fail on an assertion against a stub with the old formula and empty tier tables.
- Mutants: `scripts/mutation_check.py --only "grocery tier:"` killed 8 of the 10 first rows and `--only "figures measure"` killed the reworded 9th; the row that drops the tier's own stream survives (any stream gives a valid build; no output property tells them apart), so it is removed. Final file: 9 rows, 9 killed.

## Docs

`docs/retail-prototype.md` (Grocery) is changed. `golden-retail/stats.json` is not committed (gen#373): `retail_figures.tier_figures()` adds `grocery_tier_50k`, and `test_retail_figures_162.py` skips its family counts in the quoted-total guard like `grocery_families`.
