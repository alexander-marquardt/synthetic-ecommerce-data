# A product for a picture of every drawn type (gen#1093, cut 1)

Step 2 ([the picture products](picture-products-1022.md)) makes one product of our own per manifest
picture of a type the book (`picture_products/book.py`) describes. The book described 10 of
the 28 types `drawings` draws, so a picture of a bookcase, a rug, a faucet or a fountain made no
product. This cut gives the book an entry for each of the other 18 types. Now every type that
`picture_manifest.TYPES` names makes products. A fallback row still shows nothing to describe and
makes none.

## The types and their departments

The store department is the top of the type's path, as the issue's 2026-11-21 table files it.
The build record's `department` (the closed list in `domains/retail/departments.py`) is `Home`
for every type: each one is a home good, sold by one of the book's home brands.

| Department | Types |
| --- | --- |
| Home | sideboard, bar_cabinet, storage_cabinet, shoe_storage, wall_shelf, bar_stool, desk, tv_stand, kitchen_island, bookcase, wardrobe, chest_of_drawers, sofa, bench, rug, wall_art, decor_object, faux_floral, canister, vanity, bath_storage, vanity_light |
| Hardware | sink_faucet, cabinet_pull, tile (under `Hardware > Home Hardware`) |
| Garden | garden_statue, fountain (under `Garden > Garden Decor`) |
| Office & School | office_chair (moved from `Home > Furniture > Office Furniture`) |

Each new entry gives the type's noun (by a part's value where the shape draws kinds: a bookcase's
`style`, a rug's `form`), its product type, its path, its realistic width, height and depth in
centimeters, and the price of a mid-sized piece.

## What the writer does differently

- **A count can be worded.** A count part listed in `book.TITLE_WORDS` takes the table's words in
  the title, not its number and noun: a vanity's `sinks` is *Single Sink* or *Double Sink*, a
  faucet's `handles` *Single Handle* or *Two Handle*, a canister set's `count` *3 Piece*. The
  description still states the number (`2 sinks`).
- **A picture with no parts** (a sofa) gets a description that ends at its color, with no empty
  `Features:` list.
- **A part's attribute key can be renamed.** A cabinet pull's `size` is stored as `pull_size`
  (`book.KEYS`), because `size` is a SKU's size option elsewhere in the catalog.

## What the tests pin

`tests/test_picture_products_1093.py` runs on a 56-row fixture manifest
(`tests/fixtures/picture_products_1093/manifest.jsonl`): two rows of each of the 28 types. One row
has every part at its last drawn value and the nominal proportions; the other has every part at
its first value and narrower proportions. It is written in the generator's drawing vocabulary
only. The tests pin:

- the book describes every type the manifest names, each under its mapped department;
- each row makes one product, filed under its type's path, with attributes that state each part;
- each measured size is in the type's range, and each title holds the words the book gives
  each part;
- every word of a title or a description is the book's own, a number or glue;
- each product's picture is drawn again in the `brand` finish.

## What comes next

The next cut ships the products of the full picture manifest (one row per WANDS persona picture,
elastic/prism-wands#15) in the retail and combined build. It also runs the non-copying and
product-split audits on that build and records the count per type and department on #837.
