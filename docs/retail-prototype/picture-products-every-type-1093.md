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

## The products ship in the retail build

The WANDS persona's full picture manifest (one row per persona picture, elastic/prism-wands#15)
is pinned byte for byte at `src/synthetic_ecommerce_data/picture_products/pictures.jsonl`. Its
sha256 is `picture_products.shipped.SHA256`, the one elastic/prism-wands records for its pinned
image set. It has 42,994 rows: 13,373 of a drawn type and 29,621 department fallbacks.

- `picture_products.shipped.docs()` writes the documents through `writer.docs()`, and draws no
  picture: the build draws each SKU's picture from the document's `drawing`.
- `domains/retail/picture_products.py` is a build source of its own, the `"picture_products"`
  entry in `type_registry.BUILD_SOURCES`, last before grocery. It is a source of 28 types, not a
  type, so no one spec could hold it. The 21 types that had no spec have one now, with no rows of
  their own; those 21 and the 7 that had one (bookcase, wardrobe, chest of drawers, sofa, rug,
  artificial flowers and sideboard) each name `Home("picture_products", False)`. The scaled build
  derives no style from them.
- The main-color and sale passes leave them out, and they take a pass of their own after, as the
  films do. A product takes a main color only where no other style completes the group, so no
  style above it loses a main color or a sale price.

**One product per spec, not per picture.** Many pictures repeat a drawn spec, most of all where a
type's size range pins the measured size (tiles, cabinet hardware, faucets, rugs). Two such
pictures that land on one brand and range would be two products that differ at most in color,
which the product-split audit refuses. `writer.docs()` makes them one product: the first
picture's, sold in each picture's color, first seen first, and its description names each color.
The counts are on [#837's page](../catalogue-mix-837.md). `writer.write()`, the step-2 command
of the combined demo, still writes one product and one picture per picture.

**What it adds.** At the ceiling build (seed 0) the build grows by the records and SKUs
[#837's page](../catalogue-mix-837.md) counts. Some
derived styles in the leaves the new products share are drawn again, because the
scaled build's duplicate guards (a title, a twin and a near-duplicate listing in the leaf) now
see the new products. Most of the changes are a range-name swap, and the derived styles lose 13
records and 111 SKUs.

**The audits.** `tests/test_picture_products_ship_1093.py` runs both on every wands-inspired
product in the ceiling build: the product-split audit and the non-copying audit of
[the sideboard page](sideboard-ships-1022.md#the-audits). It also holds the pinned sha256, the
spec homes and #837's per-type rows against the build.

## What comes next

elastic/prism-wands's own check of these products against the benchmark (its
`transform_wands.py --products`) finds no title and no run of five words. It refuses 70 products,
each for a whole-centimeter size whose number equals a WANDS inch figure, and so a different size.
elastic/prism-wands#40 makes that a count, not a refusal.
