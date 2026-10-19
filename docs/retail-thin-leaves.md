# Retail thin leaves (gen#434)

`prototypes/retail_drawings/thin_leaf_rows.py` brings three leaves that a retail class names, and a
query reads, up to a floor of fifteen products. They held a handful, so the ranking had nothing to
choose between.

| Leaf | Held | Added |
|---|---|---|
| Food & Drink / Frozen Food / Chips & Potatoes | 1 | fourteen chips, fries, wedges, hash browns and roast potatoes |
| Home / Furniture / Beds | 6 | ten frames, each made in the bed sizes it is sold in |
| Womens / Coats & Jackets / Bomber Jackets | 3 | thirteen check bombers (`pattern = check`, a check swatch) |

- Every bed states `bed_size` on each SKU, from the shared `class_model.BED_SIZE_DIMS`.
- A check bomber's title names its check ("Small Check Bomber Jacket"), so the text and the stored
  `pattern` agree; the text-claim validator in `core/standard.py` refuses a title that names a
  value the leaf does not hold.
- The rows are templates only. `scale.derivable` leaves them out, so the seeded derivation is what
  it was.

The floors, the bed sizes and the check swatch are pinned by `tests/test_retail_thin_leaves_434.py`;
`scripts/mutation_rows_thin_leaves_434.py` plants a defect in each and names the test that must go
red.

## Class 8 fit and shape word decoys

`decoy_apparel.py` adds a class 8 to the gen#311 decoys for jeans and bras: a product line named
for a fit or shape the product is not ("Balloon Lane Skinny Jeans"). The line carries the word, the
true attribute is kept, and no decoy sits on a product that holds the same word. Balloon and barrel
are read as one by the ranker's synonym, so neither is planted on the other.
`tests/test_retail_fit_word_decoys_434.py` pins three decoys per value and that each reaches the
top ten of its own query.
