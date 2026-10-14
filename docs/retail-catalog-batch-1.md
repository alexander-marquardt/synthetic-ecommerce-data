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
- **Spelling.** The label text uses British spelling ("natural flavouring"). An additive
  class such as "color (annatto)" keeps the US spelling, because
  `tests/test_us_spelling.py` refuses the British one in any tracked file.
