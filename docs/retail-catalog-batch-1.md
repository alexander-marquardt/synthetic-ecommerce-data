# Retail catalog batch 1: ingredient base, text-match decoys, grocery nodes

The retail prototype's own reference is [retail-prototype.md](retail-prototype.md); the
facts this batch adds to it are here. Each section names the issue, the data and the test
that pins it.

## Base ingredients (gen#295)

Beside `facets.ingredients` (the label text, kept as it is) the flat grocery file
carries `facets.ingredient_base`: the head ingredient of each label row, from the
committed table `src/synthetic_ecommerce_data/domains/retail/grocery_ingredients.py` (`BASE`, written
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

## Grapes, a Steak parent and allergen coverage (gen#296)

- **Grapes.** `Food & Drink > Fruit & Vegetables > Fresh Fruit > Grapes` (family `GRP`: red,
  green and black seedless and sweet varieties, 250g, 500g and 1kg packs). The grape-flavoured
  products stay elsewhere as the natural decoys: red and white grape juice under Juice (`GJU`)
  and grape chews and jellies under Sweets (`GCH`).
- **Steak.** `Food & Drink > Meat & Fish > Fresh Meat > Steak` is a parent with eight children,
  one per cut, each named so it reads on its own: Sirloin Steak, Ribeye Steak, Rump Steak,
  Fillet Steak, Chuck Steak, T-Bone Steak, Flank Steak, Skirt Steak (families `SKS` to `SKW`,
  which replace the single `STK` family; Striploin and Minute Steaks are not kept). "Skirt"
  alone would be a garment. Steak knives (distractor rows), steak sauce (`SSA`, Sauces &
  Condiments) and steak seasoning (`SSN`, Herbs & Spices) stay in their own categories.
- **Dietary** comes from one closed list, `grocery_rows.DIETARY`: Vegan, Vegetarian, Gluten Free,
  Dairy Free, Nut Free, Organic. `Dairy Free` is new: no milk contained or traced.
- **Allergen coverage.** `grocery.py` prints `food_rows`, `contains_filled` and `contains_share`
  (`grocery.coverage_report`), the share of food rows whose `facets.contains` is filled.
- Proof: `tests/test_grocery_steak_grapes_296.py` (counts, children, a decoy in the plain top 10
  for "grapes" and for "steak").

## One display name per key on a document (gen#256)

A skirt once exported `garment_length` (name "Length": Mini, Midi, Maxi) and a SKU axis
`length` (name "Length": Petite, Regular, Long), so a facet panel showed two facets with one
label. The axis has been `fit_length` ("Fit length", `export.OPTIONS`) since #280.
`name_guard.shared_name_findings` now refuses the class for every type: a document, nested or
flat, may not give one display name to two different keys.
`tests/test_retail_attribute_names_unique_256.py` feeds it the old skirt and runs it over the
ceiling build (no finding).

## Text-match decoys for the color, category and audience queries (gen#294)

`src/synthetic_ecommerce_data/domains/retail/decoy_rows.py` holds `TABLE`: one row per planted product, with its
class (1 color names a part, 2 type names an accessory or a toy, 3 audience names a sibling
version, 4 a color word that is also a product or a shade, 5 guard, 7 the word is only an
ingredient, 9 the fresh plural is named in the title, 10 the phrase is an ingredient of another food) and the query it targets. The proof and the table below read that table, so no count
is kept by hand. Each decoy keeps its own color, category path and audience; only the title and
description carry the misleading word. Titles are short and sales and reviews above typical. The
ids are left out of `scale.derivable()` and out of the color completion of `main_colors`, so a
copy or a completion never gives a decoy the query's color.

## Fresh plurals: a raw "oranges" is not too clean (gen#445, class 9)

With interpretation off, a search for a fresh fruit or vegetable in the plural used to return only
the fresh products: titles name an ingredient in the singular ("Seville Orange Marmalade") and the
title field ranks the typed spelling first. Class 9 rows (`decoy_plural_rows.py`, 42 rows) are
believable products of another category whose title holds the exact plural as the ingredient or
source: a juice pressed from oranges, a chocolate with candied oranges, sun-dried tomatoes in oil,
a strawberries and cream biscuit. Twelve plurals are covered (oranges, lemons, limes, apples,
strawberries, raspberries, tomatoes, onions, potatoes, carrots, bananas, cherries), each with three
or four rows from at least two categories (Drinks, Chocolate & Sweets, Food Cupboard, Frozen,
Biscuits & Snacks, Dairy & Alternatives, Breakfast). A row's category, ingredients and drawing (a
carton, a bar, a tin) say what it is, no title or description claims the fresh fruit, and titles
are four tokens or three, six at most. The policy that separates them is the category-node reading of the
fresh word (the Oranges node keeps the fresh leaf and drops the rest); no `special:` policy is
needed.

The fresh products compete only if their titles are as long. With interpretation off the title field
is exact-token BM25 with no stemming, so the score of two titles with one hit each depends only on
the title's token count: the shorter title ranks first and equal lengths tie. The rule that keeps
a raw match honest is therefore on length: the fresh varieties of the twelve plural families end in the
grade `, Class 1` ("Fallowfield Oranges, Class 1", "Cranmore Baby Plum Tomatoes, Class 1"; the
grade is cut by `pack_label`, so no drawing label moves), the tinned chopped tomatoes carry basil,
and the decoys are four tokens, three where the wording stays natural ("Seville Oranges Marmalade"). On the 10**6-SKU baseline each plural then has three or more decoys that
are among the first twelve hits however ties fall (a tie counts against the decoy).

Six plurals had no fresh leaf of their
own, so the grocery build has depth families `TOM`, `ONI`, `POT`, `CAR`, `BAN` and `CHY` (leaves
Fresh Vegetables > Tomatoes, Onions, Carrots; Fruit & Vegetables > Potatoes, the leaf of the class 8
potato rows; Fresh Fruit > Bananas and Stone Fruit > Cherries, which the breadth tier's single cherries row used to hold and now leaves to this family, so the leaf has one owner and no sibling named for its head noun), each
variety named with a grade, a variety or a pack word ("Vine Ripened Tomatoes", "Maris Piper
Potatoes"). They are appended after the existing depth families, so no earlier draw moves, and the
`VEG` family no longer carries a tomato or a carrot (sweet peppers and baby spinach take their
slots), so each fresh word lives in one leaf. `tests/test_grocery_plural_decoys_445.py` holds, per
plural: at least three decoys from two categories, none claiming to be fresh, the median title
length of the fresh products and of the decoys within two tokens, and (on the 10**6-SKU baseline)
at least three decoys in the first twelve results. The with-interpretation check (the fresh product
ranks first) runs on a loaded catalogue and is the coordinator's after the next Iowa load.

The same twelve plurals also meet products of a non-food department, because the maintainer's
follow-up asked that `lemons`, `oranges` and `limes` show at least two non-food decoys in the
first twelve (`decoy_plural_nonfood_rows.py`, 16 class 9 rows). A row is one of two things a shopper
meets: a **brand** shown on the product ("Lucky Lemons Kids' Pyjamas", "Going Bananas Kids'
Pyjamas", "Couch Potatoes Kids' Sweatshirt"; the five brands are invented and the products carry
no fruit motif, as with the color-word brands of gen#312) or a **scent** (a `scent` attribute
that names the fruit: "Sicilian Lemons Hand Wash, 250ml", "Oranges and Cloves Scented Candle",
"Limes and Sea Salt Air Freshener"). `lemons` has three such rows, `oranges` and `limes` two,
every other plural one. `tests/test_grocery_plural_nonfood_decoys_445.py` holds the count, that a
row is a brand or a scent and never both, that no title or description says fresh, and (on the
10**6-SKU baseline) two non-food decoys in the first twelve for the three named plurals. Not in
this increment: the fruit print line (a lemons-print T-shirt or tea towel) for the seven plurals
that have no print motif yet (limes, raspberries, tomatoes, onions, potatoes, bananas and
carrots need motifs of their own), and the with-policy check that the non-food rows leave Best
when the produce policy is on, which runs on a loaded catalogue.

Queries covered by rows: red sofa, blue sofa, red bra, blue shirt, black trainers, mens puffer
jacket (with two true men's puffer jackets, the leaf is new), boys grey socks, face cream, gold
top, red wine (class 10, gen#500: two red wine vinegars, a red wine gravy and a beef in red wine casserole, groceries with no wine attribute) and olive oil (class 10, gen#686: pesto, fries, sardines, tuna, sun-dried tomatoes, a spread and crisps made with olive oil, none filed under Olive Oil); guard rows for green tea, black pepper, red velvet cake and pink lady apples;
class 7 rows for oranges, lemons, strawberries, coconut and lavender (the word is in the
`ingredients` and the description, not in the title).

Queries covered by rows that already exist (`class_rows.py`, no new row): cups (class 6: bras whose
titles say "Cup" lead a bare "cups", the drinkware node keeps none; since gen#508 bras and swimwear
titles also carry the plural, "with Removable Cups", in `cups_plural_rows.py`; "d cup bra" stays in
lingerie both ways) and oranges (the orange flavour of a bake, a biscuit or a drink leads the
fruit). `tests/test_retail_text_match_decoys_294.py` holds, on the 10**6-SKU build: without
interpretation at least three decoys in the baseline top 10 and one in the top 3 for every color,
category and audience query, and with interpretation (the intended color, type and audience read
from the fields) no decoy is a hit. The prototype baseline reads the title and the description,
not the ingredients, so for class 7 only the rows that win on the description (lavender) reach its
top 10; the live search reads the ingredients too, and that run on a loaded catalogue, like the
with-persona run, is the ingest batch's check, not this PR's.

"blood red dress" (gen#540, `feature_decoys/blood_red.py`) is the one query whose true hits lead:
five dresses titled "Blood Red ..." (color Red) rank first, and nine products that hold "blood
red" or "blood orange" in the title (a black dress with blood red roses, a dress shirt, dress
socks, dress hangers, a lipstick, a candle, a shower gel, a marmalade, a juice) follow, each with
fields that say it is not a red dress.

The rows are one built page, [retail-text-match-decoys-table.md](retail-text-match-decoys-table.md):
`scripts/build_derived.py` writes it from `decoy_rows.TABLE` (CI uploads it in the `derived`
artifact), and it is not in git. A feature adds its rows in `feature_decoys/<topic>.py` and pastes
no table here (gen#513); `scripts/check_no_registry_append.py` refuses a row or a heading on this
page, and a feature's section is its own page in [retail-prototype/](retail-prototype/).

## Not done in this increment

#298 (the Chocolate node), #299 (Juice children and the label-collision guard) and #181
(neckline) are not built yet; their issues stay open.

Of #294 this increment lands the generated decoy table, the class 7 rows, four guards and the
proofs for cups, "d cup bra" and oranges on the rows `class_rows.py` already plants. #294 stays
open for: the Iowa proof on a loaded catalogue with the counts quoted; the persona top-10 check
(no decoy with the Retail-and-Industrial persona); the guards that are missing (red onion has no product; red wine is a decoy query here; white wine and
brown rice already exist); the class 7
decoys of lemons, strawberries and coconut reaching the top 10 (only lavender does); and the
oranges re-tune on the loaded catalogue (flavour decoys, variety titles on the fresh-orange rows).

A decoy can appear on the page of a neighbouring query: "black pepper" ranks trainers and a shirt
with black parts at 2 to 4, "pink lady apples" has a pink bra at 2 and "green tea" has Thai Green
Curry at 6. These are true text matches, left in on purpose.

## Text-match decoys on every clothing, footwear and lingerie type (gen#311)

The #294 decoys cover the demo queries. `src/synthetic_ecommerce_data/domains/retail/decoy_apparel.py` plants the
same kind of decoy on every product type of the Womens, Mens and Kids clothing, footwear and
lingerie, in classes (a color word naming a part, another category's noun as a modifier, an
audience word of a sibling version, a material the product does not hold, a shade only in the
description (class 5, retired in #663), a range name holding a color or category word, an invented brand holding one), and
an eighth on Jeans and Bra (gen#434): a line named after a leg fit, a rise or a bra shape the
product is not ("Balloon Lane Straight Jeans"), three per value, so the leg fit, rise and bra
shape policies each have a product to remove. The structured fields stay true, so a plain text
search is misled and the color, category, audience and fit policies, which read the fields, are
right. The generated table of every row, with its policy, is
`retail-apparel-decoys.md` (a generated page, not in git).
