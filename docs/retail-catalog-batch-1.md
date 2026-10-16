# Retail catalog batch 1: ingredient base, text-match decoys, grocery nodes

The retail prototype's own reference is [retail-prototype.md](retail-prototype.md); the
facts this batch adds to it are here. Each section names the issue, the data and the test
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

`prototypes/retail_drawings/decoy_rows.py` holds `TABLE`: one row per planted product, with its
class (1 color names a part, 2 type names an accessory or a toy, 3 audience names a sibling
version, 4 a color word that is also a product or a shade, 5 guard, 7 the word is only an
ingredient) and the query it targets. The proof and the table below read that table, so no count
is kept by hand. Each decoy keeps its own color, category path and audience; only the title and
description carry the misleading word. Titles are short and sales and reviews above typical. The
ids are left out of `scale.derivable()` and out of the color completion of `main_colors`, so a
copy or a completion never gives a decoy the query's color.

Queries covered by rows: red sofa, blue sofa, red bra, blue shirt, black trainers, mens puffer
jacket (with two true men's puffer jackets, the leaf is new), boys grey socks, face cream, gold
top and red wine; guard rows for green tea, black pepper, red velvet cake and pink lady apples;
class 7 rows for oranges, lemons, strawberries, coconut and lavender (the word is in the
`ingredients` and the description, not in the title).

Queries covered by rows that already exist (`class_rows.py`, no new row): cups (class 6: bras whose
titles say "Cup" lead a bare "cups", the drinkware node keeps none; "d cup bra" stays in
lingerie both ways) and oranges (the orange flavour of a bake, a biscuit or a drink leads the
fruit). `tests/test_retail_text_match_decoys_294.py` holds, on the 10**6-SKU build: without
interpretation at least three decoys in the baseline top 10 and one in the top 3 for every color,
category and audience query, and with interpretation (the intended color, type and audience read
from the fields) no decoy is a hit. The prototype baseline reads the title and the description,
not the ingredients, so for class 7 only the rows that win on the description (lavender) reach its
top 10; the live search reads the ingredients too, and that run on a loaded catalogue, like the
with-persona run, is the ingest batch's check, not this PR's.

| Query | Class | Product id | Title | Kind |
|---|---|---|---|---|
| red sofa | 1 color names a part | PLT-DXS01 | Blue 3 Seater Sofa with Red Piping | decoy |
| red sofa | 1 color names a part | PLT-DXS02 | Grey Sofa with Red Scatter Cushions | decoy |
| red sofa | 1 color names a part | PLT-DXS03 | Navy Corner Sofa, Contrast Red Stitching | decoy |
| red sofa | 1 color names a part | PLT-DXS04 | Grey Sofa with Red Legs | decoy |
| red sofa | 2 type names an accessory or a toy | PLT-DXS05 | Red Sofa Cushion | decoy |
| red sofa | 2 type names an accessory or a toy | PLT-DXS06 | Red Sofa Cushion Cover, Set of 2 | decoy |
| red sofa | 2 type names an accessory or a toy | PLT-DXS07 | Dolls House Red Sofa | decoy |
| blue sofa | 1 color names a part | PLT-DXS11 | Red 3 Seater Sofa with Blue Piping | decoy |
| blue sofa | 1 color names a part | PLT-DXS12 | Cream Sofa with Blue Scatter Cushions | decoy |
| blue sofa | 1 color names a part | PLT-DXS13 | Grey Corner Sofa, Contrast Blue Stitching | decoy |
| blue sofa | 2 type names an accessory or a toy | PLT-DXS14 | Blue Sofa Cushion | decoy |
| blue sofa | 2 type names an accessory or a toy | PLT-DXS15 | Dolls House Blue Sofa | decoy |
| red bra | 1 color names a part | PLT-DXB01 | Black Bra with Red Lace Trim | decoy |
| red bra | 1 color names a part | PLT-DXB02 | White Bra with Red Bow | decoy |
| red bra | 1 color names a part | PLT-DXB03 | Pink Bra with Red Straps | decoy |
| red bra | 1 color names a part | PLT-DXB04 | Navy Bra with Red Stitching | decoy |
| blue shirt | 1 color names a part | PLT-DXH01 | White Shirt with Blue Collar and Cuffs | decoy |
| blue shirt | 1 color names a part | PLT-DXH02 | Black Shirt with Blue Buttons | decoy |
| blue shirt | 1 color names a part | PLT-DXH03 | Grey Shirt with Blue Check Pocket | decoy |
| blue shirt | 2 type names an accessory or a toy | PLT-DXH04 | Blue Shirt Hangers, Pack of 10 | decoy |
| blue shirt | 2 type names an accessory or a toy | PLT-DXH05 | Blue Shirt Dress | decoy |
| black trainers | 1 color names a part | PLT-DXT01 | White Trainers with Black Sole | decoy |
| black trainers | 1 color names a part | PLT-DXT02 | Grey Trainers with Black Laces | decoy |
| black trainers | 1 color names a part | PLT-DXT03 | Red Trainers with Black Stripe | decoy |
| black trainers | 2 type names an accessory or a toy | PLT-DXT04 | Black Trainer Cleaning Kit | decoy |
| mens puffer jacket | 0 a true hit, kept for the proof | PLT-DXP01 | Mens Puffer Jacket | true hit |
| mens puffer jacket | 0 a true hit, kept for the proof | PLT-DXP02 | Mens Hooded Puffer Jacket | true hit |
| mens puffer jacket | 3 audience names a sibling version | PLT-DXP03 | Kids Mini-Me Puffer Jacket | decoy |
| mens puffer jacket | 3 audience names a sibling version | PLT-DXP04 | Boys Mini-Me Mens Puffer Jacket | decoy |
| mens puffer jacket | 3 audience names a sibling version | PLT-DXP05 | Womens Puffer Jacket, Mens-Style Fit | decoy |
| mens puffer jacket | 3 audience names a sibling version | PLT-DXP06 | Womens Boyfriend Puffer Jacket | decoy |
| boys grey socks | 3 audience names a sibling version | PLT-DXK01 | Grey Socks 5 Pack | decoy |
| boys grey socks | 3 audience names a sibling version | PLT-DXK02 | Grey Ankle Socks 5 Pack | decoy |
| boys grey socks | 3 audience names a sibling version | PLT-DXK03 | Grey Boot Socks, Boys Style | decoy |
| boys grey socks | 0 a true hit, kept for the proof | PLT-DXK04 | Boys Grey Socks 5 Pack | true hit |
| face cream | 4 color word is also a product or a shade | PLT-DXF01 | Cream Face Cloths 4 Pack | decoy |
| face cream | 4 color word is also a product or a shade | PLT-DXF02 | Cream Face Towel | decoy |
| face cream | 4 color word is also a product or a shade | PLT-DXF04 | Cream Cushion Cover with Face Print | decoy |
| gold top | 4 color word is also a product or a shade | PLT-DXG01 | Gold Top Handle Bag | decoy |
| gold top | 4 color word is also a product or a shade | PLT-DXG02 | Gold Top Zip Clutch Bag | decoy |
| gold top | 1 color names a part | PLT-DXG03 | Brown Top Handle Bag with Gold Hardware | decoy |
| gold top | 0 a true hit, kept for the proof | PLT-DXG04 | Gold Sequin Top | true hit |
| red wine | 2 type names an accessory or a toy | PLT-DXW01 | Red Wine Glasses, Set of 4 | decoy |
| red wine | 4 color word is also a product or a shade | PLT-DXW02 | Red Wine Scented Candle | decoy |
| red wine | 2 type names an accessory or a toy | PLT-DXW03 | Red Wine Stain Remover | decoy |
| red wine | 2 type names an accessory or a toy | PLT-DXW04 | Red Wine Carafe | decoy |
| green tea | 5 guard: a real product whose name holds a color word | PLT-DXU01 | Green Tea, 40 Bags | true hit |
| black pepper | 5 guard: a real product whose name holds a color word | PLT-DXU02 | Black Pepper, Whole Peppercorns | true hit |
| red velvet cake | 5 guard: a real product whose name holds a color word | PLT-DXU03 | Red Velvet Cake | true hit |
| pink lady apples | 5 guard: a real product whose name holds a color word | PLT-DXU04 | Pink Lady Apples | true hit |
| oranges | 7 word only in the ingredients | PLT-DXI01 | Earl Grey Tea, 40 Bags | decoy |
| oranges | 7 word only in the ingredients | PLT-DXI02 | Afternoon Blend Tea | decoy |
| oranges | 7 word only in the ingredients | PLT-DXI03 | Rich Fruit Cake | decoy |
| oranges | 7 word only in the ingredients | PLT-DXI04 | Cranberry Sauce | decoy |
| lemons | 7 word only in the ingredients | PLT-DXI05 | Kitchen Surface Spray | decoy |
| lemons | 7 word only in the ingredients | PLT-DXI06 | Baked Cod Fillets | decoy |
| lemons | 7 word only in the ingredients | PLT-DXI07 | Sponge Cake | decoy |
| strawberries | 7 word only in the ingredients | PLT-DXI08 | Fruit Yogurt, 4 Pack | decoy |
| strawberries | 7 word only in the ingredients | PLT-DXI09 | Oat Bar Multipack | decoy |
| strawberries | 7 word only in the ingredients | PLT-DXI10 | Cream Biscuits | decoy |
| coconut | 7 word only in the ingredients | PLT-DXI11 | Thai Green Curry | decoy |
| coconut | 7 word only in the ingredients | PLT-DXI12 | Nourishing Body Lotion | decoy |
| coconut | 7 word only in the ingredients | PLT-DXI13 | Chickpea Dhal | decoy |
| lavender | 7 word only in the ingredients | PLT-DXI14 | All Butter Shortbread | decoy |
| lavender | 7 word only in the ingredients | PLT-DXI15 | Relaxing Bath Salts | decoy |
| lavender | 7 word only in the ingredients | PLT-DXI16 | Soy Wax Candle | decoy |

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

The #294 decoys cover the demo queries. `prototypes/retail_drawings/decoy_apparel.py` plants the
same kind of decoy on every product type of the Womens, Mens and Kids clothing, footwear and
lingerie, in seven classes (a color word naming a part, another category's noun as a modifier, an
audience word of a sibling version, a material the product does not hold, a shade only in the
description, a range name holding a color or category word, an invented brand holding one). The
structured fields stay true, so a plain text search is misled and the color, category and audience
policies, which read the fields, are right. The generated table of every row, with its policy, is
[retail-apparel-decoys.md](retail-apparel-decoys.md).
