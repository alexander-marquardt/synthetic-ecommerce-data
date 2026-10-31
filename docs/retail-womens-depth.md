# Retail clothing depth: the Womens slice (gen#310)

`src/synthetic_ecommerce_data/domains/retail/womens_depth_rows.py` adds Womens dresses, blouses and shirts, coats
and jackets, skirts and tops (camisoles, vest tops, tunics) as distinct products, each with fit,
material and, where it applies, neckline and sleeve length. The floors are pinned by
`tests/test_retail_womens_depth_310.py` over `scale.templates()`. The Mens slice is
[retail-mens-depth.md](retail-mens-depth.md); knitwear is gen#309; the Kids slice is [retail-kids-depth.md](retail-kids-depth.md).

| Group | Leaves | Floor |
|---|---|---|
| dresses | Midi, Maxi, Mini, Wrap, Shirt, Tea, T-Shirt, Slip, Jumper, Shift, Bodycon, Occasion | 200 |
| blouses and shirts | Shirts & Blouses, and Tops/Shirts (Linen, Oxford, Denim, Flannel) | 80 |
| coats and jackets | Wool Coats, Trench Coats, Rain Macs, Puffer, Bomber, Denim, Blazers | 80 |
| skirts | Skirts (A-line, pleated, pencil, wrap, tiered at mini, midi and maxi) | 80 |
| tops | Camisoles, Vest Tops, Tunics, Jersey, Long Sleeve, T-Shirts, Bodysuits | 80 |
| nightwear and lingerie beyond bras | already met (about 140) | 60 |

## How a title and a description are written

A title is what a shop would write ("Womens Pure Linen Relaxed Fit Midi Dress"): the fit is a
value of the `fit` facet (Boxy, Classic, Fitted, Oversized, Regular, Relaxed, Slim; the rows add
none), written "Regular Fit" or, for Fitted, the one word "Fitted"; a feature such as Belted,
Hooded or Double Breasted is a title word and a description phrase, never a fit. The neckline word
"Collar" reads "Collared" before a sleeve. The description's last phrase follows the product, and
is derived per kind and leaf in `womens_depth_rows.py`: a dress says "a fitted waist" only when it
is Fitted (a shift hangs straight), a top says "stretchy" only for a fabric that stretches, and a
skirt closes the way its shape does (a wrap ties, a pleated or tiered skirt has an elastic waist,
an A-line or pencil skirt a zip) and states `waist_type` and `lining` as the older skirts do.

## Dress multipacks (gen#727)

`_PACKS` adds two styles, each as a pack of 2 and a pack of 3: four products, 40 SKUs, every one
sold in Red. The maintainer asked for adult packs of red dresses beside the
[Kids range](retail-kids-depth.md#dress-multipacks-gen727), which shares the mechanism: `PackRow`,
the `2 pack` or `3 pack` of the one vocabulary (gen#246), `underwear_rows._packs` and the
`pack_copies` drawing (gen#728).

| Title | Colors | Leaf |
|---|---|---|
| "Womens Cotton Jersey T-Shirt Dresses, Pack of 2" and "Pack of 3" | Red, Navy, Black | T-Shirt Dresses |
| "Womens Red Stretch Jersey Midi Dresses, Pack of 2" and "Pack of 3" | Red | Midi Dresses |

A title says Red only where the pack sells in nothing else, so the title stays true to every SKU.
Each size's price is 22.00, the cheapest full-price single, times the multibuy factor: 39.60 for
two and 56.10 for three. Each description opens "A pack of two ..." and says every dress of a pack
is one color. `tests/test_retail_adult_dress_packs_727.py` pins all of this.

## Floors count real products

The per-leaf floors (`LEAF_FLOORS` in the test) and the real-product floors count products that
are not text-match decoys, so a named leaf cannot pass on decoys alone. Puffer Jackets and Tea
Dresses had none or few real products and now carry rows of their own.

## Text-match decoys (gen#294)

The new rows add no decoys of their own. Their product types (Dress, Blouse, Shirt, Coat,
Suit Jacket, Skirt, Top) are planned in `decoy_apparel` (gen#311), which clones a real style of
each type into three decoys of each of six classes, so the decoy table
(`retail-apparel-decoys.md`, a generated page that is not in git) lists them and
`tests/test_retail_apparel_decoys_311.py` pins them. A decoy keeps the structured fields of the
style it clones, so a policy that reads the fields still answers right.

## Not in this slice

* Kids dresses and coats: see [retail-kids-depth.md](retail-kids-depth.md).
* Roots are still Womens, Mens and Kids as the tree names them; the rows are templates only, so
  `scale.derivable` leaves them out (`scale.source_ids("womens_depth_rows")`) and the seeded derivation is what
  it was.
