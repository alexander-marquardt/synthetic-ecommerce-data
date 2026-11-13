# Food & Drink pantry staples (gen#964)

The ceiling build held 12,265 `Food & Drink` SKUs against the 17,000 that
`docs/catalogue-mix-837.md` plans, and none of them was a coffee pod, a granola or a bag of
flour, so a search for `coffee pods`, `granola` or `plain flour` found nothing. Three
pantry-staple types are now specs of their own on the quick path
([new-type-quick-path.md](../new-type-quick-path.md)):

| Type | Spec | Path | Templates | Title names | SKU axis |
|---|---|---|---|---|---|
| Coffee Pods | `type_specs/coffee_pods.py` | Food & Drink > Drinks > Coffee Pods | 10 | origin, roast, brew style (espresso, lungo, ...) | pods per box, 10 to 50 (`units_per_pack`) |
| Granola | `type_specs/granola.py` | Food & Drink > Breakfast > Granola | 10 | texture, grain, flavor | bag weight, 400 g to 1 kg (`net_weight_g`) |
| Flour | `type_specs/flour.py` | Food & Drink > Food Cupboard > Baking > Flour | 10 | milling, flour type | bag weight, 500 g to 5 kg (`net_weight_g`) |

The shared pieces (the department, the brands, the pack colors, `grams()`, `units()`, `row()`
and `decoy()`) are in `pantry_rows.py`. The brands are the department's existing invented ones
(Brewhollow Roasters, Pantry Mill, Hearth & Table, Crunchworth, Goldfield Farms, Wheatsheaf
Lane, Crofter's Bakehouse), so each already has its house style, and their owners are read from
`grocery_rows.OWNERS` rather than restated. Every brand is invented (ruling 2026-10-30, gen#720).

**Color.** Food carries no color (`colorless`), as Tea and Coffee already do: a style's one
color is its pack's print, which the drawing takes as its fill and the store does not sell as a
variant. A style's SKUs are its sizes alone.

**Drawings.** No new shape: a coffee pod style is drawn as a `box`, a granola or a flour as a
`bag`, both shapes the department's kit already draws.

**Breadth.** The three types are derivable: a derived style recombines the title-shown
attributes (origin, roast, brew style; texture, grain, flavor; milling, flour type) across the
templates. Derive swaps only the literal words of a title-shown value, so no description names
one: a description stays true for every style derived from its template.

**Decoys.** Each type carries two class 6 text-match decoys, a flavor or grain word in a range
name that the product is not: `Vanilla Wharf` and `Caramel Quay` unflavored coffee pods,
`Peanut Row` and `Protein Hill` granolas, and `Rice Hill` and `Coconut Lane` wheat and spelt
flours.

**Measured** (ceiling build, `retail_figures.ceiling()`, seed 0): Coffee Pods 2,422 SKUs in
712 styles, Granola 1,287 in 429 and Flour 560 in 160, 4,269 SKUs in all. `Food & Drink` goes from 12,265 SKUs to 16,534, above
the issue's floor of 16,150 (95% of the 17,000 target). The guards are in
`tests/test_retail_food_pantry_964.py`: the floor of the three types and of the department,
each type's leaf, unique ids, titles and twin keys, determinism, decoys and a golden slice.
