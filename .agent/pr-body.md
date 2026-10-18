## One letter case for every category node and attribute display name (#499)

Refs #499. Builds on #19 (catalog and drawings coupling: `authored_names.json` rides beside `images.jsonl`), #59 and #81 (the identifier rule whose declaration this keeps in step).

Every category node and attribute display name is sentence case, retail and industrial (`Handle material`, `Bore dia.`, `Hose, tube, fittings & valves > Seals & gaskets > O-ring seals`). One normaliser, `core/letter_case.py`, runs at export on the finished document; the ~500 authored literals are not edited. Acronyms, codes and a lone capital letter keep their capitals; the exception list is `PROPER_NOUNS` (Torx, Nike, Apple). A machine key and a value are never touched. Docs: README "One letter case for names" and the `authored_names.json` row in the output table.

Pairs with the catalogue repo's category-path rewrite: do not merge until that PR is ready (issue ruling).

### Two real defects the move exposed, fixed here
- `prism/derive.py` `IDENTIFIER_ATTRIBUTES` held authored names, so the sidebar rule never matched a published `List number`.
- `prototypes/retail_drawings/grocery.py` `coverage_report` matched the root `Food & Drink`, which is now `Food & drink`, and counted zero food rows.

### Evidence (command that showed each)
- Red commit 2bd65e59: `tests/test_letter_case_499.py` plus an identity stub of `core/letter_case.py`. `pytest tests/test_letter_case_499.py -rfEp` on it: 21 failed on an assertion, 12 passed. The 12 that pass include the five output guards (`test_no_industrial_...`, `test_no_retail_...`, golden x2, `test_one_key_has_one_display_name...`): they use `sentence_case` to find breaches, so the identity stub finds none. Their bite is shown by the mutation rows below.
- Mutation rows: `.venv/bin/python scripts/mutation_check.py --only "letter case:"` -> `15 of 15 mutations caught by EVERY test they name` (each export's call, each branch of the rule, bundle lookup, derive, grocery, searchable text).
- Re-anchored: `--only "restate the identifier declaration instead of reading the generator's"` -> caught. `--only "drop attribute values out of the searchable text"` -> NOT CAUGHT, and the same on main df0eaf52 (run in a clean main clone): a gap that was there before this change.
- Tests: all 190 `tests/test_*.py` except `test_merge_pr.py`, three files per `agent_heavy` call, every call rc=0; nine files re-run after the second merge of main, rc=0. `golden-catalog/` and the 13 golden slices and the industrial field map are regenerated from `generate_cli build` and `python tests/test_type_<key>.py`, not hand-merged. `golden-retail/stats.json` re-measured with `retail_figures.py`: unchanged.

### Pre-existing, not ours
`prototypes/retail_drawings` tests are not collected by CI. Four fail identically on main df0eaf52 in a clean clone: `test_house_styles.py::test_no_two_brands_share_a_mark`, `test_signals_and_paths.py::test_every_doc_has_a_full_category_path_of_clean_shopper_terms`, `test_signals_and_paths.py::test_beer_carries_abv_as_an_attribute_and_only_some_titles_state_it`, `test_variants.py::test_every_brand_has_a_house_style_and_every_sample_draws`. All are assertion or KeyError failures on the data, not fonts. Main's CI on df0eaf52 and bfc3d467 is green; 475ac421 was cancelled.

Docs-Impact: README updated in this PR.

File-Size-Exception: `scripts/mutation_check.py` - grew from 5005 to 5011 lines, over the cap of 1750; the rows live in their own file (`mutation_rows_letter_case_499.py`) and only the import, the registration block and two re-anchored rows are added here; the chapter split of this file is its own change.
