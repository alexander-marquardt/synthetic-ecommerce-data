# Retail clothing depth: the Womens slice (gen#310)

`prototypes/retail_drawings/womens_depth_rows.py` adds Womens dresses, blouses and shirts, coats
and jackets, skirts and tops (camisoles, vest tops, tunics) as distinct products, each with fit,
material and, where it applies, neckline and sleeve length. The floors are pinned by
`tests/test_retail_womens_depth_310.py` over `scale.templates()`. The Mens slice is
[retail-mens-depth.md](retail-mens-depth.md); knitwear is gen#309; Kids is a later slice.

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

## Floors count real products

The per-leaf floors (`LEAF_FLOORS` in the test) and the real-product floors count products that
are not text-match decoys, so a named leaf cannot pass on decoys alone. Puffer Jackets and Tea
Dresses had none or few real products and now carry rows of their own.

## Text-match decoys (gen#294)

The new rows add no decoys of their own. Their product types (Dress, Blouse, Shirt, Coat,
Suit Jacket, Skirt, Top) are planned in `decoy_apparel` (gen#311), which clones a real style of
each type into three decoys of each of seven classes, so the decoy table
(`retail-apparel-decoys.md`, a generated page that is not in git) lists them and
`tests/test_retail_apparel_decoys_311.py` pins them. A decoy keeps the structured fields of the
style it clones, so a policy that reads the fields still answers right.

## Not in this slice

* Kids dresses and coats (the school uniform already holds about 100 products).
* Roots are still Womens, Mens and Kids as the tree names them; the rows are templates only, so
  `scale.derivable` leaves them out (`scale.WOMENS_DEPTH_IDS`) and the seeded derivation is what
  it was.
