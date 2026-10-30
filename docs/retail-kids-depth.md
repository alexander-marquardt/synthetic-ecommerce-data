# Retail clothing depth: the Kids slice (gen#310)

`src/synthetic_ecommerce_data/domains/retail/kids_depth_rows.py` adds Kids dresses and coats as distinct products,
each with fit, material and sleeve length (and, on a dress, a neckline). The floors are pinned by
`tests/test_retail_kids_depth_310.py` over `scale.templates()`. The other slices are
[retail-womens-depth.md](retail-womens-depth.md) and [retail-mens-depth.md](retail-mens-depth.md);
knitwear is gen#309.

The issue asks for school uniform "plus dresses and coats" for Kids and gives no number for the
two, so the floor of each leaf is the slice's own: thirty real products, the size the issue calls
thin when a leaf holds fewer.

| Leaf | Before | After | Added |
|---|---|---|---|
| Kids/Girls/Dresses | 1 | 31, and 6 packs (gen#727) | party, summer, skater, smocked, tiered, pinafore, jumper, wrap, T-shirt and shirt dresses |
| Kids/Girls/Coats & Jackets | 0 | 30 | padded coats, parkas, rain macs, trench coats, pea coats, quilted jackets |
| Kids/Boys/Coats & Jackets | 10 (2 real) | 40 (32 real) | the same six |

School uniform already holds 103 products (`school_rows.py`, gen#205) against the issue's 80, so it
is not repeated here. Its polo shirts, jumpers and cardigans stay with gen#205.

## How a title and a description are written

A title is what a shop would write ("Girls Cotton Poplin Short Sleeve Summer Dress", "Boys Hooded
Wool Blend Pea Coat"): the fabric is the `material` value, the sleeve is the `sleeve_length`
value, a feature such as Hooded or Longline is a title word and a description phrase, and no word
appears twice. The fit is a value of the existing `fit` facet (Regular or Relaxed); the rows add
no value to it. Sizes are the school ages ("3-4 Yrs" to "15-16 Yrs"), six of them on a dress.

## Dress multipacks (gen#727)

No dress title was plural, so "red dresses" had no plural title to prefer. `_PACKS` adds three
girls' styles, each as a pack of 2 and a pack of 3: six products, 108 SKUs, every one sold in Red.
There is no Womens multipack, and the range stays this small.

| Part of a pack | How it is written |
|---|---|
| Title | The form the socks use: "Girls Cotton Jersey T-Shirt Dresses, Pack of 3" |
| Count | One product per count: `pack_size` is the `2 pack` or `3 pack` of the one vocabulary (gen#246), and each SKU states `units_per_pack` |
| Price | `underwear_rows._packs`: each size's dress price at 12.00 (the cheapest single) times the multibuy factor, 1.8 for two and 2.55 for three, so a pack costs less than that many singles |
| Picture | The `dress` shape's `count` param draws that many dresses, each a `pack-item` group, on one floor |
| Description | Opens "A pack of three ..." and says every dress of a pack is one color |

Each SKU has its own image file, as every SKU does (gen#706). The rows are `PackRow`, which is
`LRow`'s facts and `URow`'s pack, so no second pack mechanism exists.
`tests/test_retail_kids_dress_packs_727.py` pins all of this.

The ranking half needs elastic/prism#13599: until the plural boost stops firing on every dress's
category text, a plural title gains nothing from it.

## Text-match decoys (gen#294)

The new rows add no decoys of their own. Dress and Coat are planned in `decoy_apparel` (gen#311),
three per class for each of six classes. The new rows are not exemplars for those decoys
(`decoy_apparel.build`): a type's decoys clone the first exemplars of its pool in product-id order,
and with the new ids in the pool the Womens dress decoys moved into the Kids leaves.

## Not in this slice

* Kids polo shirts, school jumpers and cardigans (gen#205).
* The rows are templates only, so `scale.derivable` leaves them out (`scale.source_ids("kids_depth_rows")`) and
  the seeded derivation is what it was. `scale.templates` also runs the main-color pass and the
  sale share without them, so every other template, and the fillers drawn from them, is as it was.
  The new rows then take a sale pass of their own, so each of the three leaves holds products on
  sale and the Kids department keeps its sale share.
