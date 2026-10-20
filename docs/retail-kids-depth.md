# Retail clothing depth: the Kids slice (gen#310)

`prototypes/retail_drawings/kids_depth_rows.py` adds Kids dresses and coats as distinct products,
each with fit, material and sleeve length (and, on a dress, a neckline). The floors are pinned by
`tests/test_retail_kids_depth_310.py` over `scale.templates()`. The other slices are
[retail-womens-depth.md](retail-womens-depth.md) and [retail-mens-depth.md](retail-mens-depth.md);
knitwear is gen#309.

The issue asks for school uniform "plus dresses and coats" for Kids and gives no number for the
two, so the floor of each leaf is the slice's own: thirty real products, the size the issue calls
thin when a leaf holds fewer.

| Leaf | Before | After | Added |
|---|---|---|---|
| Kids/Girls/Dresses | 1 | 31 | party, summer, skater, smocked, tiered, pinafore, jumper, wrap, T-shirt and shirt dresses |
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

## Text-match decoys (gen#294)

The new rows add no decoys of their own. Dress and Coat are planned in `decoy_apparel` (gen#311),
three per class for each of seven classes. The new rows are not exemplars for those decoys
(`decoy_apparel.build`): a type's decoys clone the first exemplars of its pool in product-id order,
and with the new ids in the pool the Womens dress decoys moved into the Kids leaves.

## Not in this slice

* Kids polo shirts, school jumpers and cardigans (gen#205).
* The rows are templates only, so `scale.derivable` leaves them out (`scale.KIDS_DEPTH_IDS`) and
  the seeded derivation is what it was. `scale.templates` also runs the main-color pass and the
  sale share without them, so every other template, and the fillers drawn from them, is as it was.
  The new rows then take a sale pass of their own, so each of the three leaves holds products on
  sale and the Kids department keeps its sale share.
