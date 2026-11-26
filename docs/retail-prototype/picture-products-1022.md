# A product of our own around each picture, from a picture manifest (gen#1022, slice 3)

The combined catalogue takes the pictures drawn for the WANDS persona as inspiration and nothing
else. This slice adds step 2 of the two independent paths the issue asks for: it reads a picture
manifest and writes one new generator product per picture, with our own brand, range, title,
description, sizes and price. Step 1 (drawing the pictures from the benchmark's products) lives in
elastic/prism-wands#1 and calls the public `drawings.render` ([slice 2](render-and-finishes-1022.md)).
The two paths share the renderer and nothing else.

The code is the package `synthetic_ecommerce_data.picture_products`, over the manifest loader
`synthetic_ecommerce_data.picture_manifest` that [the drawing run](picture-drawings-1220.md) reads too. No generator build uses it
yet: slice 5 ships a home type in a build with its own products.

## The picture manifest

A manifest row is the spec one picture was drawn from, in the generator's own drawing vocabulary,
under an opaque image id. The manifest is a JSON list or JSON Lines:

```json
{
  "image_id": "2b5d454ad52f6674",
  "type": "sideboard",
  "color": "Natural",
  "parts": {"doors": 3, "drawers": 3, "legs": "tapered"},
  "proportions": {"height_per_width": 0.5, "depth_per_width": 0.27}
}
```

The schema is closed. No field holds free text, so no title, description or other prose can pass
through it.

| Field | Required | Value |
| --- | --- | --- |
| `image_id` | yes | 12 to 64 lower-case hex digits. A hand-over key only: no product, SKU or file name keeps it. |
| `type` | yes | A type `drawings.render` draws at proportions (`manifest.TYPES`, the 28 types of `drawings.PROPORTIONS`). |
| `color` | yes | A generator color word: the six main colors and the furniture tones (`manifest.COLORS`). |
| `parts` | no | The type's own params. A count (doors, drawers, shelves, tiers, stools) is an integer, and any other part is a word its shape draws. A part left out is drawn at the shape's default. |
| `proportions` | no | `height_per_width` and `depth_per_width`, each from 0.05 to 20 with at most two decimals. A ratio left out is the type's nominal one. |

`picture_manifest.load(rows)` and `picture_manifest.load_file(path)` return checked `Picture` and
`Fallback` rows. (`manifest` on this page is `synthetic_ecommerce_data.picture_manifest`.) Any other
field, an unknown type, color, part or value, a count that is not an integer, a ratio out of range
or with more decimals, a missing field or a repeated image id raises a `ValueError` that names the
row and the fault.

A row whose product is of no drawn type is a fallback row: `image_id` and `department` (a word of
`manifest.DEPARTMENTS`), and no other field. It is drawn as its department's own picture and makes
no product. A row of a type the book does not describe (`book.TYPES`) makes none either.

## The product written around a picture

`writer.write(pictures)` returns one `Product(doc, image_name, svg)` per picture:

- **Id.** `BRD-PC` plus eight hex digits, hashed from the image id. The image id itself appears in
  no product, SKU or file name. Two pictures that would share a product id are refused.
- **Brand and range.** One of the four furniture brands that have a house style (Brackenmere
  Home, Larchwood Living, Emberly Home, Cobble & Kiln), and one of that brand's own ranges
  (`book.RANGES`). The product id picks both.
- **Size.** Width, height and depth in centimeters, picked in the type's realistic range
  (`book.TYPES`) to fit the drawn proportions. Depth is not seen from the front, so it gives way
  first when the ranges and the proportions cannot all hold.
- **Title and description.** Worded only from the book, the brand book and the measured numbers,
  for example the fixture's first row gives `Saltrigg 3 Door 3 Drawer Sideboard` and "The
  Saltrigg Sideboard from Larchwood Living, 161 cm wide, 80 cm high and 43 cm deep, in natural.
  Features: 3 doors; 3 drawers; legs: tapered."
- **Attributes.** Each part the picture draws (a count as `<part>_count`), and `item_width`,
  `item_height` and `item_depth`.
- **Price.** The type's price for a mid-sized piece, scaled by the front's area, plus a step per
  door, drawer or other counted part. It is written through the catalog's own row
  (`breadth_row.Row`), as one SKU.
- **Picture.** Drawn again through `drawings.render` in the `brand` finish at the measured size,
  under the product id. The angle and the brand mark come from that id, so the bytes differ
  from the `unbranded` picture of the same figure. The file is named `<product id>.svg`.

## The command

```sh
uv run python -m synthetic_ecommerce_data.picture_products MANIFEST OUT_DIR
```

It writes `OUT_DIR/products.jsonl` and `OUT_DIR/images/<product id>.svg`, one per picture of a
type the book describes. Since gen#1093 the book describes every type the manifest names
([every type](picture-products-every-type-1093.md)).

## The separation

The package reads only the manifest. It never opens an image file or a catalogue, and it imports
nothing named after the benchmark. `drawings` does not import it. A test guards each of these.

## A renamed param: the bar stool's `seat_height`

The bar stool's height param (counter or bar) was called `height`. That is also the name of
`render`'s size attribute, so `render("bar_stool", {"height": "bar", ...})` was read as a size and
refused with "height must be a positive number of inches". The param is now `seat_height`
(see the table in [slice 1](home-furniture-drawings-1022.md)). A guard test fails if any shape names a
param after an attribute that `render` reads itself. No generator product used the old name.
elastic/prism-wands#1's map must write `seat_height`.

## What the tests pin

`tests/test_picture_products_1022.py` runs on a 12-row fixture manifest
(`tests/fixtures/picture_products_1022/manifest.json`) and pins issue Done-when 5, 7 and 8:

- each picture gives one product, whose attributes describe the picture and whose title,
  description and measured size are the generator's own;
- a row outside the closed schema, a missing field and a repeated image id are each refused;
- step 2 imports nothing named after the benchmark, and step 1 does not import step 2;
- no product, SKU or picture name holds an image id, and each product picture differs from the
  same figure's `unbranded` picture;
- the command writes the products and their pictures.

## What comes next

- Slice 4 adds the rest of the home types (tile, vanity, pulls, faucet, bath storage, canisters,
  wall art, decor objects, statues, florals, fountains, and rug, wall light and bench variants) as
  kit shapes drawn through `render`.
- Slice 5 meets Done-when 3: `sideboard` ships in the retail build with products of its own, and
  passes the product-split and non-copying audits
  ([a sideboard ships](sideboard-ships-1022.md)).
