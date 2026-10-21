# Retail product types the failure classes need (gen#329)

A demo probe found types that a general retailer's failure classes need and the catalogue lacked.
`prototypes/retail_drawings/needs_rows.py` holds them, built on the floor and decoy builders of
`mens_depth_rows.py` (see [retail-mens-depth.md](retail-mens-depth.md)); the floors and the decoys
are pinned by `tests/test_retail_elasticated_waist_329.py`; the lingerie and lamp-shade slice by
`tests/test_retail_needs_329.py`.

## Status of each type in the issue

| Type | State |
|---|---|
| chinos | already in the catalogue (gen#310, `Mens/Trousers/Chinos`) |
| elasticated waist | done: leaf `Mens/Trousers/Elasticated Waist Trousers` |
| lamp shades as a leaf | done: five "Lamp Shade" titles in `Home/Lighting/Lampshades` (`lighting_rows.py`); lamps with "Shade" in a title were already there as the decoys |
| mastectomy, post-surgery and nursing bras | done: the new leaf `Womens/Lingerie/Bras/Mastectomy Bras` and more post-surgery and nursing bras (`needs_rows.BRAS`) |
| period pants | done: leaf `Womens/Lingerie/Period Pants` (`type_specs/period_pants.py`) |
| plimsolls | done in gen#216: kind `plimsoll`, leaf `Shoes/Plimsolls` |
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
| 1 color | a trim names another color | "Mens White Elasticated Trousers with Red Waistband" is white |
| 2 category word | another category's noun as a modifier | "Mens Shirt Collar Elasticated Trousers" |
| 3 audience word | a sibling cut | "Mens Boyfriend Fit Elasticated Trousers" |
| 4 feature absent | the word "elasticated" on a product whose waist is not elastic | "Mens Elasticated Cuff Cargo Trousers" has a belted waist |
| 5 shade in the description | a fancy title, the shade in the text | "Mens Moonbeam Elasticated Trousers" are Ivory |
| 6 incidental word | a range name, carried as a `range` attribute | "Mens Kettle Hill Elasticated Trousers" are not kettles; a range is a place, never a color (#446) |
| 7 invented brand | a brand holding a color or category word | "Black Curlew", "Yellow Plover", "Jacket Wren" |

`needs_rows.TABLE` lists every decoy with its class, the misleading word, the query it targets and
the policy that repairs it. The rows are templates: `scale.derivable` leaves them out
(`scale.NEEDS_IDS`), so the seeded derivation is what it was.

## Medical and nursing bras

`needs_rows.BRAS` holds ten bras: four Mastectomy (each says "mastectomy" in its title and has
pocketed cups for a breast form), three Post-Surgery (two of them name the mastectomy they follow)
and three Nursing. `Mastectomy Bras` is a purpose node that stays under Bras
(`facet_leaves.PURPOSE_BRAS`, `BRA_LEAVES`). Each bra states its own straps and fastening
(`scale_rows.Bra.fitting`). They sit in `needs_rows`, not in `scale_rows`, because a `scale_rows`
row has to open a wiring value its leaf lacked and a medical bra is non-wired by nature; they are
templates, so no derived "Wired Mastectomy Bra" exists.

## Period pants

`type_specs/period_pants.py` is a type spec of ten products with an `absorbency` attribute
(Light, Medium, Heavy, Overnight). The decoys are the apparel family `u` plan of
`decoy_apparel.py`, with the compounds Bikini, Boyshort and Thong Period Pants.

## Lamp shades

Five rows in `lighting_rows.LAMPSHADES` spell the type as shoppers type it, "Lamp Shade", one
per form (drum, empire, tapered, scalloped, pleated). They stay derivable like every lighting row.

## Adding the next type

Add a `Kind` and a `Leaf` to `needs_rows.py` and the decoys follow from the kind. A type outside
Mens needs `mens_depth_rows._decoys` to take its audience word (the titles say "Mens" today).
