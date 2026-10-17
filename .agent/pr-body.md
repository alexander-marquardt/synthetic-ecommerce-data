Refs #452. Builds on #284 (nested each type under its generic category; it names #452 but changes none of the exemption).

## What changed

`scale.TEXT_EXEMPT` was a union written in `scale.py` that named only the `Toys` department, so every new department had to remember to add itself. It is now `scale.text_exempt()`, computed from the registry:

- `type_registry.text_match_decoy_ids()` with no department returns the class 1 to 7 spec decoys of every department (`department` still filters).
- `PLT-RQHOOP` is not a registry decoy (it is a `class_rows.py` style, not a spec), so it moves into `type_registry.ONE_OFF_TEXT_EXEMPT` with its reason.
- `scale.exempt_problems()` finds an exempt id the catalog no longer builds, a one-off with no reason, and a one-off the registry already knows.
- The legacy decoy modules (`decoy_rows`, `decoy_apparel`, `garden_rows`, `decoy_product_words`) are not registry types and stay as the other terms of the union.

Remainder vs the issue's done-when: all four items are done here. #432 (the Depends-On) is still open; this PR does not touch its global `decoy_ids()` question, and after #432 registers its four accessory types they are exempt without any edit to `scale.py`.

## Evidence

- Red commit 759d8a7: six tests fail on assertions against the stub (`AGENT_PYTEST collected=8 passed=2 failed=6`), listed in its `Red-Test:` trailer.
- Green: `pytest -q -n 8` over `tests/test_retail_text_exempt_452.py`, `test_retail_scale.py`, `test_merchandising_score_182.py`, `test_retail_audience.py`, `test_retail_product_word_decoys_326.py`, `test_retail_type_specs_351.py`, `test_retail_text_match_decoys_294.py`: rc=0, 267 passed. Widening the exemption to every department broke none of them.
- Each fix line fails its test when reverted alone: `scripts/mutation_check.py --only "text exempt:"` reports `7 of 7 mutations caught by EVERY test they name` (rows in `scripts/mutation_rows_text_exempt_452.py`).
- The planting test (`test_a_registered_decoy_of_any_department_joins_the_exemption_without_editing_scale`) registers a type of a department no list names and finds its decoy in `scale.text_exempt()`.

Docs-Impact: `docs/new-type-quick-path.md` says a class 1 to 7 decoy is exempt by registering and where a one-off is declared.
