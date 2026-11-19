# Bath and kitchen drawings: tile, vanities, pulls, faucets, bath storage, canisters (gen#1022, slice 4)

The kit could not draw floor and wall tile, a bathroom vanity, a cabinet or drawer pull, a
bathroom sink faucet, bathroom storage or a kitchen canister. These are the largest bath and
kitchen classes the WANDS persona still lacked a drawing for, in order of product count. This
slice adds them as kit shapes in
`src/synthetic_ecommerce_data/domains/retail/kit_bath_kitchen.py`. Each one draws through
`drawings.render` ([slice 2](render-and-finishes-1022.md)) in both finishes, at a product's own
width, height and depth. No generator product uses them yet.

Each shape is drawn from the attributes a record states. `kit_bath_kitchen.PARAMS` is each
shape's table of params and the values it draws:

| Shape | Draws | Params (values) |
|---|---|---|
| `tile` | a panel of tiles set in grout | `form` (square, subway, hexagon), `pattern` (plain, veined, motif), `surface` (matte, gloss), `grout` (light, dark) |
| `vanity` | vessel basins on a worktop, drawers over doors (neither: an open shelf of towels) | `sinks` (1, 2), `doors` (0 to 4), `drawers` (0 to 3), `mount` (floor, wall) |
| `cabinet_pull` | one pull on a cabinet door | `style` (bar, cup, knob, ring, edge), `size` (small, medium, large), `backplate` (no, yes) |
| `sink_faucet` | a basin tap on a worktop, or on the wall over a wall-hung basin | `handles` (1, 2), `spout` (arc, straight, waterfall), `mount` (deck, wall) |
| `bath_storage` | a bathroom unit with open shelves of towels and bottles, under a cabinet | `form` (tower, over_toilet, wall), `shelves` (2 to 4), `cabinet` (none, door, mirror) |
| `canister` | a row of kitchen canisters, tallest first | `count` (1 to 4), `body` (ceramic, glass, metal), `lid` (flat, dome, wood) |

The record's color fills the product itself. What it is drawn against stays light: grout, a
worktop, a cabinet door, a toilet or a wall-hung basin. What stands on a shelf, or shows through
a glass canister, is drawn in the kit's book colors.

`tests/test_bath_kitchen_drawings_1022.py` checks what the picture promises:

- Every value of every param draws a picture of its own, as a well-formed SVG.
- A value outside the table is refused with a `ValueError` naming the param.
- The drawn count is the stated count: one `class="basin"` per sink, one `class="door"` per door,
  one `class="drawer"` per drawer, one `class="handle"` per handle, one `class="shelf"` per shelf
  and one `class="canister"` per canister.
- A vanity with neither doors nor drawers shows an open shelf. A gloss tile catches a highlight
  and a matte one does not. A pull draws a backplate only when it has one. A cabinet has a mirror
  only when it says so. A glass canister shows what it holds.
- A White piece reads white (gen#226).
- Each type draws through `drawings.render` in both finishes, at its own dimensions.

`drawings.PROPORTIONS` gives each shape its nominal width, height and depth in inches. A canister
row is measured as a set:

| Shape | View | Width | Height | Depth |
|---|---|---|---|---|
| `tile` | front | 12 | 12 | 0.4 |
| `vanity` | front | 36 | 34 | 21 |
| `cabinet_pull` | front | 5 | 1.25 | 1.25 |
| `sink_faucet` | front | 6 | 10 | 5 |
| `bath_storage` | front | 24 | 60 | 9 |
| `canister` | front | 16 | 9 | 5 |

`canister` is `level` in `orientations/bath_kitchen.py` (#1045), as a set drawn as several items
is (#884). The other five are `upright`.

## What comes next

[Slice 6](decor-drawings-1022.md) adds the décor types (wall art, decorative objects, garden
statues, faux florals and fountains). Slice 7 adds the `rug`, `wall_light` and bench variants.
Slice 5 ships a home type in a generator build with its own products.
