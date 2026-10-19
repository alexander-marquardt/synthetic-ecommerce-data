Closes #352

Sports & Outdoors gets the five types the maintainer's ask still lacked: bicycles (road, mountain, electric, kids), bike helmets (S, M, L), kayaks (sit-on-top and inflatable, one or two seats), kick scooters and skateboards. Tents, sleeping bags and bike pumps were already on main and are not rebuilt; toy bikes and ride-on scooters stay in Toys.

## Builds on

- #282 one root per department and no department attribute on a document
- #284 each type nests under its generic category, with a guard
- #286 toy vehicles and ride-ons, bikes in wheel sizes (the kids' bike here uses the same wheel-size axis)
- #369 the Sports & Outdoors tree note; the five types move from its Not-built table to its Leaves table
- #374 the second increment (tents, bike pumps and the sports decoy census this one joins)
- #545 derived files are no longer in git: this PR commits no `stats.json` and no apparel decoy table, and the template pin in `test_retail_pattern_facet_408.py` moves instead

## What changed

- Five specs in `prototypes/retail_drawings/type_specs/` (`bicycle`, `bike_helmet`, `kayak`, `kick_scooter`, `skateboard`), drawings in `kit_sports.py`, helpers in `cycling_helpers.py`.
- Two class 8 text-match decoys per type (a kids' tee, pyjamas, a beach towel and so on, printed with the word), `feature_decoys/cycling_wheeled.py`, ids DY3521 to DY3530.
- The six main colors on every type; the facets are in the test's `TYPES` table.
- Docs: `docs/retail-sports-tree.md` and `docs/retail-product-word-decoys.md`.
- Hardcoded lists moved with the types: the Not-built set in `test_retail_sports_tree_note_290.py`, the sports type list in `test_retail_sports_265.py`, the table in `test_retail_product_word_decoys_326.py`, and the template pin in `test_retail_pattern_facet_408.py`.

## Ceiling

`ceiling.skus` goes from 166,990 to 167,192 and the styles from 16,359 to 16,386 (27 new template styles: 17 rows of the five types and the 10 decoys; 101,460 to 101,662 template SKUs). Measured by `uv run python prototypes/retail_drawings/retail_figures.py` on the branch before the merge of #545, and held by `tests/test_retail_scale.py` and `tests/test_retail_figures_162.py` after it (both pass on the merged tree).

## Brands

No brand is new: every row sells under Wrenfield, Harbour & Pine or Larkmoor, which main already owns and draws. `tests/test_retail_scale.py -k house_style` passes (`test_every_brand_in_the_build_has_a_house_style`). I did not check the names on the web; they are the existing invented ones.

## Not built

Bike lights, locks and camping stoves (optional in the issue) stay in the tree note's Not-built table. A car roof "bike rack" decoy needs a car-accessory type that does not exist; that is a question for the maintainer, not built here.

## Evidence

- Red commit c3893af9: the new test file and the moved lists alone; `pytest` on that tree failed the ids named in its `Red-Test:` trailer on assertions (types not live, no rows, queries find nothing).
- The same files pass after the implementation commit: `pytest tests/test_retail_cycling_wheeled_352.py test_retail_product_word_decoys_326.py test_retail_sports_265.py test_retail_sports_tree_note_290.py test_retail_sports_decoys_368.py test_retail_scale.py test_retail_pattern_facet_408.py test_retail_figures_162.py test_retail_type_specs_351.py test_retail_main_colors_275.py test_retail_tree_nesting_283.py test_retail_departments_281.py test_retail_attribute_keys_227.py test_retail_apparel_decoys_311.py` on the merged tree, no failure.
- Mutants: `.venv/bin/python scripts/mutation_check.py --only "cycling:"` printed "5 of 5 mutations caught by EVERY test they name" (rows in `scripts/mutation_rows_cycling_wheeled_352.py`).
- The full suite was not run locally (CI runs it); the Elasticsearch-backed modules were not run (no Docker on this host).

Docs-Impact: updated `docs/retail-sports-tree.md` and `docs/retail-product-word-decoys.md` in this PR.
