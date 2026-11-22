# Every product type's picture, measured for fill and flatness (gen#1129)

Before gen#1129, only the produce kit (gen#1111) and the kits redrawn after it (chocolate
gen#1125, bread gen#1126, drinks gen#1127, dairy gen#1128) had a fill measure. Nothing ranked the
other kits, so the next small, flat picture was found by eye in the served demo.
`scripts/picture_fill_1129.py` measures every retail product type's picture and ranks them
worst first. It is measurement only: it changes no drawing.

    uv run python scripts/picture_fill_1129.py --out .agent/fill-1129
    uv run python scripts/picture_fill_1129.py --out .agent/fill-1129 --skus 500000 --vcpus 8

## What it draws

It draws one SKU per (product type, shape) of the build: the templates, or with `--skus` the
scaled build of that many retail SKUs. The SKU is drawn through `image_release.render`, in its
house style as served. The SKU is the type's most common pack, read from the SKU's drawing spec
(size rung, pack scale, pack count and a `pack_size`, `pack` or `count` param). The type's
largest and smallest packs are drawn too when it has more than one. Pack amounts read their
units, so `1L` is more than `500ml` and `6 x 330ml` is 1980 ml.

## What it measures

The method is gen#1111's: the grid of `sheet_cover`, at a step of 4. The script reads two more
things on the measuring side only, as gen#1111's one-off sweep did:

- **Arcs**: `A` and `a` path commands are flattened into lines, which `sheet_cover` refuses (the
  tin, jar, tub and cake).
- **`<use>` copies**: each copy of a pack is inlined.

| column | meaning |
|---|---|
| whole % | the share of the served 400 x 400 image that `<g class="product">` paints (the brand band, mark and frame are not the product) |
| area % | the share of `house_styles.TURN_AREA` (344 x 334) that the plain-sheet drawing paints. Neither the paper nor the `ground` shadow counts. This is the measure behind gen#1111's 50% floor. |
| area range | the area % over the packs drawn (most common, largest, smallest) |
| flat | one solid color paints more than half of the figure, or the figure has no highlight and no shadow |
| empty | the most common pack's area % is under 35% |
| drawn to scale | a SKU drawing param the kit's own code reads is a dimension: its name is one (`diameter_cm`), or its values are lengths (a pizza's `pack_size`, `"12 inch"`) |
| in scope | yes for every retail type. The maintainer's drawn-to-scale rule (2026-11-21) scopes only the industrial types, which slice 2 adds. |

These count as a **highlight or shadow**:

- a gradient fill (it is both);
- a translucent fill (light is a highlight, dark is a shadow);
- a translucent white gloss stroke (`kit._highlight`);
- a `kit._shade` or `kit._tint` tone of another of the figure's colors, each covering at least
  2% of the figure.

A tone's base must be a color, not a grey. A tin's grey lid on its white label is two parts, not
a shade of one. A translucent fill over a color makes a new tone, so it is not that color's solid
share.

The **render cost** is the time `image_release.render` takes per SKU drawn, as the median and the
p95. The wall time to re-render the catalogue is the mean time × `--catalogue-skus` (default
500,000) ÷ `--vcpus` (default the machine's CPU count). The run prints which machine it ran on
only through those arguments: give the generator CI VM's vCPU count, or run it there.

## What it writes

| file | what it holds |
|---|---|
| `types.md` | one row per (kit, product type, shape), worst area first: kit, product type, shape, SKUs served, whole %, area %, area range, flat, empty, drawn to scale, in scope |
| `kits.md` | one row per kit module, worst median area first: product types, SKUs served, median whole % and area %, flat (most of its types are), empty (median area under 35%), drawn to scale, in scope, and its worst type. The kit modules whose shapes no served type draws are listed under the table. |
| `worst40.html` | the worst 40 type rows' served pictures, with their numbers |
| `rows.json` | every render's numbers, with the cost |

A kit is the module that defines the shape: `kit.shapes()[shape]`'s module, such as `kit`,
`kit_packs` or `belt`.

## At the templates (c1a8d103)

There were 1,182 renders over 736 (product type, shape) rows and 96 kit modules, in 21 s on 32
vCPUs. The median render took 0.6 ms and the p95 2.2 ms. Of the 736 rows, 481 are empty and 560
are flat. The produce kit paints a median of 72% of the area, matching gen#1111's 71%. The base
kit's tins paint 14-16% at their most common pack (a 0.63 pack scale) and 84% as a 4-pack. The
worst kits are `belt` (4%), `kit_footwear`, `kit_accessories` and `kit_garden` (8% each). The
posted tables, the industrial rows (slice 2) and the redraw order (slice 3) are on gen#1129.

Tests: `tests/test_picture_fill_1129.py` holds the readers to fixed SVGs:

- an arc circle, `<use>` copies, the paper, the ground and the brand band;
- a solid, a shaded, a gradient and a glossed figure;
- `kit._shade` and `kit._tint` tones;
- the base kit's tin, which `sheet_cover` alone refuses;
- the pack choice, the drawn-to-scale reading, the worst-first tables and the cost.
