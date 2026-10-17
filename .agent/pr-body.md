Closes #449

Grocery, home and garden decoys and copy tell the truth (the rule of #444). Builds on #59 (the hex socket set screws pilot, which named #449) and on the WIP of the earlier dispatch on this branch; it overlaps gen#445 only in `decoy_rows.py`, which this change edits in the carafe, cake, apple and yogurt rows.

## What changed, by class

- F11 carafe: `Glass Wine Carafe, 1L`, clear glass, no color field, drawn by a new `carafe` kind of the tableware `drinking_glass`.
- F11 sponge cake: a color the decoy table does not know is now a `KeyError` (no grey fallback); the lemon sponge is yellow.
- F11 apples and yogurt: `Pink Lady Apples` is "four to a net" and drawn as a net of four; `Fruit Yogurt, 4 Pack` carries `units_per_pack=4` and is drawn as four pots (`kit.tub(count)`).
- F11 mug cake: a `cake_mix` kind drawn as a `box`, not the celebration cake.
- F11 punnet: `kit.punnet(produce=...)` draws strawberry, tomato, mushroom, carrot, bean or herb; the grocery VEG family passes the produce of its variety.
- F12: `Corded Grass Trimmer, 10 m Cable`, `Corded Hedge Trimmer, 10 m Cable`, `Center Pole Parasol with Tilt` (the absent word now sits in the copy; the garden test reads title or copy), the mini-me knit tops (womens, mens and the mens depth rows) read `... Mini-Me <noun>, Kids' Version Sold Separately`. The throw reads `Quilted Throw with Batting`, not the issue's `with Wadding`: the product-word decoy of #326 must hold its query noun "batting" in the title (`test_every_title_is_short_and_holds_the_noun_and_the_query`), and "quilted throw with batting" is a real listing phrase.
- F13: a grocery description is one authored sentence per product type (`grocery_rows.INTRO`, `INTRO_MULTI`), then `Available as ...`, then the storage and allergen lines. Pasta, rice, ready meals and cheese carry a `variety`, not a `flavor`.

Not changed: the other `absent` rows ("Not Cordless: Petrol Grass Trimmer", "Petrol Free Cordless Lawn Mower", ...) keep their negation titles; the issue names only DCTA02, DCGA02 and DCPA02.

## Guards

One test per class in `tests/test_retail_truthful_decoys_449.py` (red commit 64333a44 with its 20 `Red-Test:` ids), plus `test_every_food_product_type_has_a_sentence_of_its_own`. Mutation rows `truthful decoys:` in `scripts/mutation_rows_truthful_449.py`.

## Generated files

`docs/retail-catalog-batch-1.md` and `docs/retail-product-word-decoys.md` (one table row each, generated), `golden-retail/stats.json` (`python prototypes/retail_drawings/retail_figures.py`: the measured grocery "named but not carried" counts moved because the new sentences name product words such as milk and cheese).

Docs-Impact: `docs/retail-garden.md` absent-class row updated; the generated tables above regenerated; no integrator-facing change.

File-Size-Exception: `scripts/mutation_check.py` - grew from 4937 to 4943 lines, over the cap of 1750; the split waits because it is the one registry of every mutation row and the new rows already live in their own file mutation_rows_truthful_449.py, six lines are only the import and the registering block.

## Verification

Filled in below from the commands run.
