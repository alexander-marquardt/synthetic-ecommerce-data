# Retail catalog batch 1: ingredient base, text-match decoys, grocery nodes

The README is over the file-size cap and may not grow, so the facts this batch adds
to the retail prototype are here. Each section names the issue, the data and the test
that pins it.

## Base ingredients (gen#295)

Beside `facets.ingredients` (the label text, kept as it is) the flat grocery file
carries `facets.ingredient_base`: the head ingredient of each label row, from the
committed table `prototypes/retail_drawings/grocery_ingredients.py` (`BASE`, written
as one line per base ingredient). It is never a heuristic. "orange peel" and "orange
juice" are *oranges*, "sea salt" is *salt*, "emulsifier (soya lecithin)" is *soya*,
"roasted peanut" is *peanuts*.

- **One number form.** The plural for a countable (peanuts, almonds, oranges,
  raspberries), the mass noun otherwise (salt, sugar, milk, honey, cocoa).
- **An unmapped label keeps its own value.** `grocery.py` prints the label values with
  no row under `ingredients_unmapped`; `tests/test_grocery_ingredient_base_295.py` holds
  that list empty, and refuses a row for a label the build never writes.
- **Counts.** 425 distinct label values (`facets.ingredients`), 197 distinct base
  values (`facets.ingredient_base`); `grocery.py` prints both as
  `ingredients_distinct` and `ingredient_base_distinct`.
- **Spelling.** The label text keeps the US spelling ("natural flavoring"), as the repo does;
  `tests/test_us_spelling.py` refuses the British one in any tracked file.

## Text-match decoys: "chocolate without peanuts" (gen#294, class 8)

Text search ignores "without": a chocolate that holds the word "peanut" scores highest.
The grocery build plants 23 chocolate styles under Chocolate & Sweets > Chocolate Bars
(`grocery_rows.DECOY_ANCHORS`, families `PNT`, `PNH`, `PNF`, drawn from a stream of their
own, so no other grocery draw moves). The base ingredient is `peanuts` (plural, gen#295), so
the exclusion filters `peanuts` on `facets.ingredient_base`, `facets.contains` and
`facets.may_contain`.

| Kind | Styles | What the row holds |
|---|---|---|
| Peanut in the title (`PNT`) | 12 (6 products, 2 ranges) | `peanuts` in `ingredient_base` and `contains` |
| Peanut only in the ingredients (`PNH`) | 6 | no "peanut" in title or description, `peanuts` in `ingredient_base` |
| Peanut-free right answers (`PNF`) | 5 | "Peanut-Free" or "No Peanuts" in the title, no peanut in any field |

Existing rows complete the picture: chocolate with `may_contain: peanuts` (the CHB anchors),
and the guards, peanut butter and salted peanuts, which are not chocolate.

`tests/test_text_match_decoys_294.py` is the proof, on the built catalogue: the baseline top 10
for "chocolate without peanuts" holds at least 3 peanut chocolates, and the ingredient-field
exclusion keeps every "peanut-free" row and leaves at least 10 chocolate styles.

## One canonical allergen form (gen#294)

`facets.contains` and `facets.may_contain` use the value `facets.ingredient_base` uses for the
same ingredient: `peanuts`, `milk`, `eggs`, `soya` (the nested attribute and the description
keep the display text "Peanuts", "Soy"). Three allergens name a group of ingredients and so
have no single base value: `tree nuts`, `gluten`, `fish`
(`grocery_ingredients.ALLERGEN_GROUPS`). Singular and plural spellings are the vocabulary's
job (elastic/prism#12043), not the data's. The mapping is `grocery_ingredients.ALLERGEN_BASE`.

## One display name per key on a document (gen#256)

A skirt once exported `garment_length` (name "Length": Mini, Midi, Maxi) and a SKU axis
`length` (name "Length": Petite, Regular, Long), so a facet panel showed two facets with one
label. The axis has been `fit_length` ("Fit length", `export.OPTIONS`) since #280.
`name_guard.shared_name_findings` now refuses the class for every type: a document, nested or
flat, may not give one display name to two different keys.
`tests/test_retail_attribute_names_unique_256.py` feeds it the old skirt and runs it over the
ceiling build (no finding).

## Not done in this increment

The non-grocery decoy classes (color on a part, accessory or toy, audience sibling, color
word as a product, cups), the ingredient decoys of class 7, the oranges re-tune, #296 and
#181 are not built yet; issue #294 stays open.
