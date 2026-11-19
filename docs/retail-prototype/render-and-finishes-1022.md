# One draw call, two finishes, real proportions, and five storage shapes (gen#1022, slice 2)

A loader outside the generator (elastic/prism-wands#1) needs to draw a home or furniture product
from the attributes it already holds, without importing the generator's internals. This slice
adds that call, `synthetic_ecommerce_data.drawings.render`, and the five storage types the kit
could not draw. No generator product uses them yet.

## The call

```python
from synthetic_ecommerce_data import drawings

svg = drawings.render(
    "sideboard",
    {"color": "#8a5a3a", "width": 72, "height": 32, "doors": "3", "drawers": "3"},
    "unbranded",
    product_id="any-stable-id",
)
```

`render(type, attributes, finish, *, product_id, brand=None)` returns one standalone SVG. The
same arguments return the same bytes on every call and every machine.

## The attributes

The attributes are a closed vocabulary. Any other key or value raises a `ValueError` that names
it:

- `color`: the fill, as `#rrggbb`. The caller maps its own color words to a hex value.
- `width`, `height`, `depth`: the piece's size in inches, a positive number, for a type in
  `drawings.PROPORTIONS`. A dimension left out takes the type's nominal size. A type with no
  entry refuses any dimension.
- The type's own params, each one of the values its kit shape draws (the tables below, and
  [slice 1's](home-furniture-drawings-1022.md) for the home furniture shapes).

An unknown type, an unknown finish, and a `brand` finish with no brand (or a brand with no house
style) are each refused.

## One figure, two finishes

`drawings.figure(type, attributes)` is the figure alone: the shape, its params, the color and the
proportions, in one `<g class="figure">`. Both finishes draw that identical figure; only what is
around it changes.

| Finish | What it draws |
|---|---|
| `unbranded` | Keyed only by `product_id` (`drawings.unbranded_look`): one of five frame treatments (`thin`, `double`, `rounded`, `heavy`, `ticks`), the frame's margin, the line weight, a dash or none, and a grey frame accent. No mark, no wordmark, no text, and no tinted accent, since a tinted sheet once read as a search signal (#849). The frame sits in `<g class="frame">`. |
| `brand` | The brand's house style, as the generator's own products draw it (`house_styles.HOUSE_STYLES`): mark, wordmark, frame, ink and outline hand. |

In both finishes, the figure is turned by the product's angle (`product_look.angle_of`), as every
generator drawing is.

## Proportions

`drawings.PROPORTIONS` gives each type its view and its nominal width, height and depth in
inches. A `front` type draws its width against its height. A `top` type (a rug) draws its width
against its depth. The figure is scaled about its bottom center (`kit.figure_at`), with the
larger axis kept at full size and neither axis squeezed below 40%. So a 90-inch sideboard draws
longer for its height than a 60-inch one and stands on the same floor.

| Type | View | Width | Height | Depth |
|---|---|---|---|---|
| `sideboard` | front | 60 | 32 | 18 |
| `bar_cabinet` | front | 36 | 60 | 18 |
| `storage_cabinet` | front | 30 | 66 | 16 |
| `shoe_storage` | front | 32 | 22 | 12 |
| `wall_shelf` | front | 24 | 16 | 8 |
| `bar_stool` | front | 17 | 41 | 17 |
| `desk` | front | 48 | 30 | 24 |
| `office_chair` | front | 26 | 42 | 26 |
| `tv_stand` | front | 60 | 22 | 16 |
| `kitchen_island` | front | 48 | 36 | 30 |
| `bookcase` | front | 32 | 72 | 12 |
| `wardrobe` | front | 40 | 72 | 22 |
| `chest_of_drawers` | front | 32 | 44 | 18 |
| `sofa` | front | 80 | 34 | 36 |
| `rug` | top | 96 | 0.5 | 60 |
| `tile`, `vanity`, `cabinet_pull`, `sink_faucet`, `bath_storage`, `canister` | front | see [slice 4](bath-kitchen-drawings-1022.md) | | |

## The five storage shapes

`src/synthetic_ecommerce_data/domains/retail/kit_storage_furniture.py` adds the shapes below.
`kit_storage_furniture.PARAMS` is each shape's table of params and the values it draws:

| Shape | Draws | Params (values) |
|---|---|---|
| `sideboard` | a long low cabinet: drawers over doors (no door: an open bay), on legs | `doors` (0 to 4), `drawers` (0 to 4), `legs` (tapered, plinth, hairpin) |
| `bar_cabinet` | a drinks cabinet: a bottle rack over its doors, glasses hung from a rack, and the stools of a bar set in front | `doors` (0 to 2), `glass_rack` (yes, no), `stools` (0 to 3) |
| `storage_cabinet` | a tall office cabinet: files on its shelves, open or behind glass doors, filing drawers under them, a lock | `front` (open, glass), `shelves` (1 to 5), `drawers` (0 to 3), `lock` (no, yes) |
| `shoe_storage` | tiers of shoes on an open rack, or under the cushioned seat of a bench | `tiers` (2 to 5), `form` (rack, bench), `frame` (wood, metal) |
| `wall_shelf` | boards on a wall, floating, on brackets or on rails, stacked or staggered | `shelves` (1 to 4), `mount` (floating, bracket, rail), `layout` (stacked, staggered) |

Each is `upright` in `orientations/storage_furniture.py` (#1045).
`tests/test_storage_furniture_drawings_1022.py` checks slice 1's promises for them:

- Every value of every param draws a picture of its own, as a well-formed SVG.
- A value outside the table is refused.
- The drawn count is the stated count: doors, drawers, shelves, tiers and stools.
- A bracket shelf draws two brackets per shelf, a bench has a seat and a rack has none, a glass
  front shows its shelves, a lock is drawn only when the cabinet locks, and glasses hang only
  from a glass rack.
- A White piece reads white (gen#226).

`tests/test_drawings_render_1022.py` checks the call: the finishes, the proportions and the
refusals.

## How many products share a picture

`drawings.picture_share(rows)` counts how many products of a set share their picture with
another, for the figure alone and in each finish. `scripts/picture_share_1022.py <rows.json>`
prints the counts. On the fixture `tests/fixtures/drawings_1022/sideboards_200.json` (200
sideboards from the generator's own vocabulary):

```
drawings: 200 of sideboard (sideboards_200.json)
figure: 45 of 200 share a picture (22.5%)
unbranded: 0 of 200 share a picture (none)
brand: 0 of 200 share a picture (none)
```

Products whose attributes match draw the same figure, and the finish (the angle and the frame,
keyed by the product id) tells them apart.

## What comes next

[Slice 3](picture-products-1022.md) adds the manifest loader and the combined writer.
[Slice 4](bath-kitchen-drawings-1022.md) adds the bath and kitchen types (tile, vanity, pulls,
faucet, bath storage, canisters) as kit shapes drawn through `render`. Slice 6 adds the décor types
(wall art, decorative objects, statues, florals, fountains) and the rug, wall light and bench
variants. Slice 5 ships a home type in a generator build with its own products.
