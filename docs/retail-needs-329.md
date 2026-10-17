# Retail product types the failure classes need (gen#329)

A demo probe found types that a general retailer's failure classes need and the catalogue lacked.
`prototypes/retail_drawings/needs_rows.py` holds them, built on the floor and decoy builders of
`mens_depth_rows.py` (see [retail-mens-depth.md](retail-mens-depth.md)); the floors and the decoys
are pinned by `tests/test_retail_elasticated_waist_329.py`.

## Status of each type in the issue

| Type | State |
|---|---|
| chinos | already in the catalogue (gen#310, `Mens/Trousers/Chinos`) |
| elasticated waist | done: leaf `Mens/Trousers/Elasticated Waist Trousers` |
| lamp shades as a leaf | the leaf `Home/Lighting/Lampshades` exists; depth and decoys open |
| post-surgery, nursing and period-wear lingerie | one post-surgery and one nursing bra exist; the word "mastectomy" does not; open |
| plimsolls | open: needs a `kit_footwear` kind and `footwear_rows.TYPES` entry |
| Womens elasticated trousers | open |

## Elasticated waist trousers

Each product states `waist_type` Elastic, the name the joggers and the shorts already use, has
"Elasticated Waist" in its title, and is drawn with the gathered band
(`waist="elasticated"`), so the picture, the title and the attribute say the same thing. The
leaf offers the six main colors.

## Text-match decoys (gen#294)

Three decoys of each of the seven classes. Classes 1 to 3 and 5 to 7 are elasticated-waist
trousers whose title or description misleads on another word; the structured fields stay true.

| Class | Decoy | Example |
|---|---|---|
| 1 color | a trim names another color | "Mens White Elasticated Trousers with Red Stripes" is white |
| 2 category word | another category's noun as a modifier | "Mens Shirt Collar Elasticated Trousers" |
| 3 audience word | a sibling cut | "Mens Boyfriend Fit Elasticated Trousers" |
| 4 feature absent | the word "elasticated" on a product whose waist is not elastic | "Mens Elasticated Cuff Cargo Trousers" has a belted waist |
| 5 shade in the description | a fancy title, the shade in the text | "Mens Moonbeam Elasticated Trousers" are Ivory |
| 6 incidental word | a range name, carried as a `range` attribute | "Mens Red Tarn Elasticated Trousers" are not red |
| 7 invented brand | a brand holding a color or category word | "Black Curlew", "Yellow Plover", "Jacket Wren" |

`needs_rows.TABLE` lists every decoy with its class, the misleading word, the query it targets and
the policy that repairs it. The rows are templates: `scale.derivable` leaves them out
(`scale.NEEDS_IDS`), so the seeded derivation is what it was.

## Adding the next type

Add a `Kind` and a `Leaf` to `needs_rows.py` and the decoys follow from the kind. A type outside
Mens needs `mens_depth_rows._decoys` to take its audience word (the titles say "Mens" today).
