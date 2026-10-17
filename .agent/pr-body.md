Refs #445

## What this does

A raw (interpretation off) search for a fresh plural such as `oranges` returned only fresh oranges, because titles name an ingredient in the singular. It now meets believable products of other categories whose title carries the exact plural.

- 42 class 9 decoy rows (`prototypes/retail_drawings/decoy_plural_rows.py`, wired in `decoy_rows.py`) for 12 plurals: oranges, lemons, limes, apples, strawberries, raspberries, tomatoes, onions, potatoes, carrots, bananas, cherries. Three or four rows each, from at least two categories (Drinks, Chocolate & Sweets, Food Cupboard, Frozen, Biscuits & Snacks, Dairy & Alternatives, Breakfast). Titles are six tokens or fewer; each title reads like a retail title (juice pressed from oranges, sun-dried tomatoes in oil), the ingredients and drawing say what the product is, and no title claims it is fresh (gen#444).
- Six new fresh depth families (`TOM`, `ONI`, `POT`, `CAR`, `BAN`, `CHY` in `grocery_rows.py`, drawings in `kit_produce.py`) so tomatoes, onions, potatoes, carrots, bananas and cherries each have a fresh leaf with grade/variety titles. They are appended last, so no earlier depth draw moves; the `VEG` family gives up its cherry tomatoes and baby carrots (sweet peppers and baby spinach take the slots) so each word lives in one leaf.
- `golden-retail/stats.json` regenerated with the repo's own script; docs section and decoy table in `docs/retail-catalog-batch-1.md`.
- The policy that separates them is the category-node reading of the fresh word; no `special:` policy.

## Evidence

- Red commit `aa9d99f9871360a9c1e2e8a968013a733d8d4303`: `tests/test_grocery_plural_decoys_445.py`, 48 ids (4 tests x 12 plurals), each failing on an assertion, listed as `Red-Test:` trailers.
- `agent_pytest` over `tests/test_grocery_ingredient_base_295.py tests/test_retail_scale.py tests/test_retail_drawing_honesty.py tests/test_grocery_plural_decoys_445.py tests/test_retail_text_match_decoys_294.py`: 191 passed.
- Measured with `.agent/t4.py` over `grocery.build` and `decoy_rows.TABLE`: median title tokens, fresh 3 to 4 against decoys 4 to 5 for every plural (the limit is 2).
- `python scripts/mutation_check.py --only "plural decoys:"` (new rows in `scripts/mutation_rows_plural_445.py`): 6 of 6 caught by the test they name (a singular title, a decoy that no longer matches the raw search, a plural left with two decoys, a "Fresh" title, a decoy with no fruit in its ingredients, a seven-word title). The first draft of the raw-search row (singular `Lime` in a title) was not caught because the baseline stems; it was replaced by a title with no lime word. The fresh-title-length test (`test_the_fresh_products_are_as_long_as_the_decoys`) has no mutant: a single-line change cannot move a median by three tokens.

## Not done (the issue stays open)

- Comment 2 of the issue asks, for each plural, at least one decoy from a non-food department (an "Oranges Print T-Shirt"). The existing print range already gives five plurals one (oranges, lemons, apples, strawberries, cherries: tea towels, a tea dress, a duvet cover; read with `.agent/nonfood.py` over `scale.build(10**6)`). Limes, raspberries, tomatoes, onions, potatoes, carrots and bananas have none: they need new print motifs and a believable garment or home line each, which is a separate slice, and the test does not yet assert it.
- With interpretation on, the fresh product ranking first for each word is checked on Iowa after the next load (coordinator); not run here.
- The fresh Oranges, Lemons, Limes and Apples titles are still a brand and the noun (median 3 tokens), inside the two-token limit but not lengthened with variety words.

Docs-Impact: none needed beyond `docs/retail-catalog-batch-1.md`, which this PR updates.
