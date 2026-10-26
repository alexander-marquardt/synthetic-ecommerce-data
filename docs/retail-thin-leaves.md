# Retail thin leaves (gen#434, gen#645)

Three leaves that a retail class names, and a query reads, held a handful of products, so the
ranking had nothing to choose between. Each is now a type spec (see
[adding a type](adding-a-type.md)) that brings the leaf up to a floor of fifteen products:

| Leaf | Spec | Held | Added |
|---|---|---|---|
| Food & Drink / Frozen Food / Chips & Potatoes | `type_specs/chips.py` | 1 | fourteen chips, fries, wedges, hash browns and roast potatoes |
| Home / Furniture / Beds | `type_specs/bed.py` | 6 | ten frames, each made in the bed sizes it is sold in |
| Womens / Coats & Jackets / Bomber Jackets | `type_specs/bomber_jacket.py` | 3 | thirteen check bombers (`pattern = check`, a check swatch) |

- The product types `Chips`, `Bed` and `Bomber Jacket` are specs that own their rows (they left the
  legacy type list, which gen#537 has since deleted). No row was appended to a registry module.
- Every bed states `bed_size` on each SKU, with the width and length of that size from the shared
  `class_model.BED_SIZE_DIMS`.
- A check bomber's title names its check ("Small Check Bomber Jacket"), so the text and the stored
  `pattern` agree; the text-claim validator in `core/standard.py` refuses a title that names a
  value the leaf does not hold.
- The spec rows are templates only (`derivable=False`). `scale.derivable` leaves them out, so the
  seeded derivation is what it was.
- The class rows already pinned by the committed ES proof stay in `class_rows.py` and are listed
  in `PROOF_PINNED_CLASS_ROWS`; any other chips, bed or bomber row registered outside its spec is
  refused by `tests/test_retail_type_specs_351.py`.

The floors, the bed sizes and the check swatch are pinned by `tests/test_retail_thin_leaves_434.py`;
`scripts/mutation_rows_thin_leaves_434.py` plants a defect in each and names the test that must go
red.
