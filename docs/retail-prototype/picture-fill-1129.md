# Every product type's picture, measured for fill and flatness (gen#1129)

Before gen#1129, only the produce kit (gen#1111) and the kits redrawn after it (chocolate
gen#1125, bread gen#1126, drinks gen#1127, dairy gen#1128) had a fill measure. Nothing ranked the
other kits, so the next small, flat picture was found by eye in the served demo.
`scripts/picture_fill_1129.py` measures every product type's picture, retail and industrial,
and ranks them worst first. It is measurement only: it changes no drawing.

    uv run python scripts/picture_fill_1129.py --out .agent/fill-1129
    uv run python scripts/picture_fill_1129.py --out .agent/fill-1129 --skus 500000 --vcpus 8
    uv run python scripts/picture_fill_1129.py --out .agent/fill-1129 --no-industrial

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
| in scope | yes for every retail type. An industrial type is `out of scope (maintainer 11-21): drawn to scale` when its figure draws to a length, else yes; the hammers are the exception (see [The industrial rows](#the-industrial-rows)) |

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
The cost is given for the whole sweep and per domain (retail over `--catalogue-skus`, industrial
over the SKUs its default build serves).

## The industrial rows

`--no-industrial` leaves them out. Otherwise the sweep draws the industrial build (its default
size) too: one SKU per industrial type, through `core.drawing.draw_product` with its product's
siblings, so its size rung and angle are the served ones. The SKU is the type's most common
`Units per Pack`, plus its largest and smallest on a pack type. Its kit is the module of the
type's figure function, as `industrial/<module>`: a type module's own `figure` names its type as
the shape, and a shared drawing (`industrial/figures`, `industrial/breadth_shapes`,
`industrial/tabletype`) names its function.

An industrial sheet is 200 x 300 with a brand plate under the figure, so its two shares are:

- **whole %**: what the figure paints of `SHEET_FIGURE`, the strip above the brand plate, as a
  share of the whole sheet;
- **area %**: what it paints of `SHEET_AREA`, that strip inside the sheet's margins, which a
  type's largest extent fills (`sheet.type_scale`). It is the counterpart of `TURN_AREA`.

A fill in the paper's color is a hole, not paint: a sheet cuts its holes and the magnifier's lens
that way. Flat and empty read as for retail.

**Drawn to scale** is read from the type's figure code by running it. Each length the SKU
publishes (a value `core.dimensions.parse_length` reads, such as `3/8 in` or `25 mm`) is made 1.5
times longer (`LONGER`), and the figure is drawn again. The type is drawn to scale when the figure
changes and its source does not, so a `Dim` in a spec and a geometry reader count alike. A value
the figure refuses and replaces with a nominal one is not drawn to, and nor is a size rung alone.
Such a type is `out of scope (maintainer 11-21): drawn to scale`, by the maintainer's rule of
2026-11-21: "Any of the industrial products that we built to scale (length, width, etc.) don't
get a realistic drawing. But others such as hammers, screwdrivers, electric drill, etc. would get
realistic drawings."

The rule names hammers, screwdrivers and the electric drill as realistic, so a type whose key
starts `hammer_`, `screwdriver` or `electric_drill` (`NAMED_REALISTIC`) stays in scope even where
its code draws to a length. Its note says so: `yes (maintainer 11-21 names it realistic; its code
draws to scale)`. Other hand tools that the code draws to scale (levels, tape measures, utility
knives, combination wrenches, hand files, hex keys, stud finders) are out of scope by the rule as
written, so they get no redraw.

A kit that holds both kinds of type is split in `kits.md` by product type, into
`<kit> (in scope)` and `<kit> (drawn to scale)` rows.

## What it writes

| file | what it holds |
|---|---|
| `types.md` | one row per (kit, product type, shape), worst area first: kit, product type, shape, SKUs served, whole %, area %, area range, flat, empty, drawn to scale, in scope |
| `kits.md` | one row per kit module, worst median area first: product types, SKUs served, median whole % and area %, flat (most of its types are), empty (median area under 35%), drawn to scale, in scope, and its worst type. The kit modules whose shapes no served type draws are listed under the table. |
| `worst40.html` | the worst 40 in-scope type rows' served pictures, with their numbers (a drawn-to-scale type gets no redraw, so it is not among them) |
| `worst40.svg` | the same 40 pictures as one SVG contact sheet, five to a row, for a PNG on the issue (`rsvg-convert`). The one posted on gen#1129 is `docs/images/picture-fill-1129-worst40.png` |
| `rows.json` | every render's numbers, every type row, and the cost |

A kit is the module that defines the shape: `kit.shapes()[shape]`'s module, such as `kit`,
`kit_packs` or `belt`, or an industrial figure's module (`industrial/levels`).

## At the templates (c1a8d103)

There were 1,182 renders over 736 (product type, shape) rows and 96 kit modules, in 21 s on 32
vCPUs. The median render took 0.6 ms and the p95 2.2 ms. Of the 736 rows, 481 are empty and 560
are flat. The produce kit paints a median of 72% of the area, matching gen#1111's 71%. The base
kit's tins paint 14-16% at their most common pack (a 0.63 pack scale) and 84% as a 4-pack. The
worst kits are `belt` (4%), `kit_footwear`, `kit_accessories` and `kit_garden` (8% each).

## With the industrial rows (e79f1382)

There were 1,368 renders over 914 type rows, 174 of them industrial (every SKU of the default
industrial build), in 34 s on 32 vCPUs. Of the 914 rows, 642 are empty and 735 are flat. All 174
industrial rows are flat and 163 are empty; their median area is 7%. 65 industrial types are out
of scope as drawn to scale, and 109 are in scope: the breadth types and
`cut_resistant_gloves`, the 7 hammers, `household_tool_sets`, `kit_assortment`,
`picture_hangers` and `safety_glasses`. The worst in-scope industrial pictures are
`hammer_ball_pein` (3%), `picture_hangers` (3%) and `hammer_claw` (4%).

The render cost, measured on the agent VM (32 vCPU), is the same vCPU count as the generator CI
VM (`alex-prism-generator-ci`, `c4d-highcpu-32`), so it scales one to one. It was not timed
there, since no agent key runs a command on that VM. Retail took a median of 0.68 ms per SKU, a
p95 of 2.5 ms and a mean of 1.0 ms, so 500,000 SKUs re-render in 16 s of wall time. Industrial
took a median of 0.13 ms and a p95 of 0.36 ms, so the whole industrial build takes under a second. That is render
time only, not the build. A drawing in strokes only reads 0% by this fill method, such as the
clothes hangers and the snowflake.

The posted tables and the contact sheet are on gen#1129.

## The redraw order

    uv run python scripts/redraw_order_1129.py --rows .agent/fill-1129/rows.json

`scripts/redraw_order_1129.py` reads the sweep's `rows.json` and prints one row per group of kits,
in the order to redraw them. Each group has one redraw issue (`GROUPS`). A type is in the order
when it is in scope and fills under 50% of the product area (`FLOOR`, gen#1111's fill test). A
type drawn to scale is never in it. A row that no group holds stops the script, so no picture is
dropped. A test refuses a retail shape that is in no group and not in `NO_REDRAW`, which gives
each shape's reason to have no redraw (it already fills half, or no template draws it). So a new
kit joins a group in its own PR. The tiers:

1. the redraws the maintainer named (`NAMED`), in the order gen#1129 lists them;
2. the retail groups, by the top-12 slots their types fill, then by worst median area;
3. the realistic industrial groups, in the same way.

The top-12 slots are in `tests/data/seed_top12_1129.json`: the top 12 of each of the 60 seed
queries of the R&I demo (`src/prism_retail_and_industrial/data/seed_queries.json`), read once from
a read-only Engine on 2026-11-23. Of its 720 slots, 335 are types in the order, 344 are industrial
types drawn to scale, and 41 are types that already fill 50%.

The order at ddade9f3, with `kit_bath_shave` and `kit_baking` in their groups (the SKUs are the
templates', to the hundred from 1,000 up):

| # | redraw | issue | kits | types under 50% | SKUs | median area % | top-12 slots |
|---|---|---|---|---|---|---|---|
| 1 | Loose fruit and vegetables | gen#1111 | `kit_produce` | 0 | 0 | - | 0 |
| 2 | Chocolate | gen#1125 | `kit_chocolate` | 0 | 0 | - | 0 |
| 3 | Bread | gen#1126 | `kit_bread` | 0 | 0 | - | 0 |
| 4 | Wine, beer and soft drinks | gen#1127 | `kit`, `kit_beer`, `kit_drinks`, `kit_packs`, `kit_soft_drinks` | 11 | 1,000 | 22% | 11 |
| 5 | Milk and yoghurt | gen#1128 | `kit_dairy` | 0 | 0 | - | 0 |
| 6 | Dresses, tops, jeans and trousers | gen#1189 | `kit`, `kit_garments`, `kit_lowerbody`, `mens_pants` | 24 | 37,100 | 15% | 99 |
| 7 | Shoes and boots | gen#1190 | `kit_footwear` | 27 | 18,000 | 8% | 48 |
| 8 | Bedding, towels, soft furnishings, lipstick and eyeliner | gen#1191 | `kit_bedding_storage`, `kit_home`, `kit_softfurn` | 24 | 1,600 | 23% | 37 |
| 9 | Beds, plants, socks and the other kit_more shapes | gen#1192 | `kit_more` | 18 | 665 | 24% | 37 |
| 10 | Sweatshirts, pyjamas, sheets, mugs and aprons | gen#1193 | `kit_surfaces` | 7 | 1,200 | 39% | 36 |
| 11 | Gifts, party goods, spray bottles and outfit sets | gen#1194 | `kit_gifts`, `kit_party`, `kit_round4`, `stickers` | 32 | 758 | 33% | 13 |
| 12 | Grocery packs, cakes and trays | gen#1195 | `kit`, `kit_baking`, `kit_biscuits`, `kit_grocery`, `kit_punnet` | 39 | 5,000 | 40% | 13 |
| 13 | Bottles and jars (the shared packs) | gen#1196 | `kit_packs` | 51 | 3,100 | 27% | 12 |
| 14 | Picture motifs | gen#1197 | `kit_motifs` | 31 | 220 | 25% | 7 |
| 15 | Accessories, jewellery and luggage | gen#1198 | `belt`, `gloves`, `hat_cap`, `kit_accessories`, `kit_jewellery`, `kit_luggage`, `scarf`, `sunglasses`, `wallet` | 28 | 1,600 | 11% | 5 |
| 16 | Pets | gen#1199 | `kit_pet_care`, `kit_pet_gear`, `kit_pets` | 8 | 671 | 18% | 3 |
| 17 | Underwear and swimwear | gen#1200 | `kit`, `kit_swimwear`, `kit_underwear` | 18 | 28,800 | 9% | 0 |
| 18 | Garden and patio | gen#1201 | `kit_garden`, `kit_garden_care`, `kit_garden_yard`, `kit_outdoor`, `kit_patio` | 18 | 1,200 | 12% | 0 |
| 19 | Sports and outdoors | gen#1202 | `kit_cycling`, `kit_fishing_golf`, `kit_fitness_team`, `kit_outdoor_winter`, `kit_sports` | 56 | 2,100 | 15% | 0 |
| 20 | Baby clothes and baby gear | gen#1203 | `kit_baby`, `kit_baby_gear` | 15 | 1,600 | 18% | 0 |
| 21 | Coats, suits and school uniform | gen#1204 | `kit`, `kit_coats`, `kit_outerwear`, `kit_school`, `kit_suit_sets`, `kit_suits` | 31 | 11,500 | 19% | 0 |
| 22 | Lighting and decor | gen#1205 | `kit_decor`, `kit_lighting` | 12 | 459 | 21% | 0 |
| 23 | Car care and car accessories | gen#1206 | `kit_automotive`, `kit_automotive_electrics`, `kit_automotive_interior` | 13 | 1,500 | 22% | 0 |
| 24 | Tableware and kitchenware | gen#1208 | `kit_baking`, `kit_cups`, `kit_household`, `kit_tableware` | 28 | 670 | 22% | 0 |
| 25 | Beauty, hair, grooming and health | gen#1207 | `kit_bath_shave`, `kit_beauty`, `kit_beauty_cotton`, `kit_grooming`, `kit_hair`, `kit_health`, `kit_health_care`, `kit_health_feminine`, `kit_skin` | 35 | 1,200 | 24% | 0 |
| 26 | Toys | gen#1209 | `kit_toy_word_decoys`, `kit_toys`, `kit_toys_craft`, `kit_toys_learning`, `kit_toys_play` | 11 | 356 | 26% | 0 |
| 27 | Electronics and office | gen#1210 | `kit_audio`, `kit_electronics`, `kit_gadgets`, `kit_gaming`, `kit_office`, `kit_printers`, `kit_smart_home` | 37 | 3,400 | 29% | 0 |
| 28 | Appliances | gen#1211 | `kit_appliances`, `kit_kitchen_appliances`, `kit_large_appliances` | 16 | 460 | 30% | 0 |
| 29 | Household goods and sewing | gen#1212 | `kit_goods`, `kit_plain_goods`, `kit_sewing` | 17 | 186 | 35% | 0 |
| 30 | Cleaning and paper goods | gen#1213 | `kit_bags_wrap`, `kit_cleaning`, `kit_cleaning_care`, `kit_paper` | 14 | 622 | 35% | 0 |
| 31 | Furniture and sofas | gen#1214 | `kit_furniture`, `kit_seating`, `kit_storage_furniture` | 18 | 410 | 36% | 0 |
| 32 | Drills, hammers, tool sets and ladders | gen#1215 | `industrial/case_figures`, `industrial/figures`, `industrial/hammer_figures`, `industrial/household_tool_sets`, `industrial/picture_hangers`, `kit_drills` | 19 | 627 | 14% | 12 |
| 33 | Industrial breadth types (storage, workwear, hand tools, vises and the rest) | gen#1216 | `industrial/breadth_shapes` | 95 | 184 | 12% | 2 |
| 34 | Safety glasses and cut-resistant gloves | gen#1217 | `industrial/cut_resistant_gloves`, `industrial/safety_glasses` | 2 | 120 | 19% | 0 |

Row 31's first slice, the seven `kit_furniture` types, is redrawn ([furniture-fill-1214](furniture-fill-1214.md)); the table is the sweep's, before any redraw.

Tests: `tests/test_picture_fill_1129.py` holds the readers to fixed SVGs:

- an arc circle, `<use>` copies, the paper, the ground and the brand band;
- a solid, a shaded, a gradient and a glossed figure;
- `kit._shade` and `kit._tint` tones;
- the base kit's tin, which `sheet_cover` alone refuses;
- the pack choice, the drawn-to-scale reading, the worst-first tables and the cost;
- an industrial sheet: its figure counted, not its paper, a paper-colored hole or the brand plate;
- a published length made longer, a figure that draws to it, and `kit_assortment`'s figure, which
  draws to none;
- the out-of-scope rule with the named hammers, the split kit, and the contact sheet, which skips
  a drawn-to-scale type and keeps each cell's ids apart.

`tests/test_redraw_order_1129.py` holds the order to fixed rows: the tiers, the slots before the
area, the floor, a drawn-to-scale type left out, an ungrouped row refused, a kit split by shape,
the recorded 720 slots, one filed issue per group, the bath and shave and the baking kits in their
groups, and every retail shape in a group or in `NO_REDRAW`.
