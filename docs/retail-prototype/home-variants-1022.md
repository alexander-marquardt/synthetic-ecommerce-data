# Rug, wall light and bench variants: mats, kids' rugs, vanity lights, benches (gen#1022, slice 7)

Some of WANDS's large classes are variants of drawings the kit already makes: kitchen mats (353
products), doormats (280) and kids' rugs come from `rug`; vanity lighting (211) comes from
`wall_light`; benches (210) come from the dining-chair bench. This slice draws each of them. Each
one draws through `drawings.render` ([slice 2](render-and-finishes-1022.md)) in both finishes, at
a product's own width, height and depth. No generator product uses the new values or types yet.

## Kitchen mats, doormats and kids' rugs: new values of `rug`

A mat lies on the floor and is measured by width and depth, as a rug is. So mats fit the rug's
`drawings.PROPORTIONS` row (`top`, 96 x 60), and they are new values of the `rug` shape in
`src/synthetic_ecommerce_data/domains/retail/kit_softfurn.py`. `kit_softfurn.RUG_PARAMS` is the
table:

| Param | Values | What the new values draw |
|---|---|---|
| `form` | rectangle, round, runner, **doormat**, **kitchen_mat** | a doormat is a coir face in a dark rubber rim, its bristles drawn as `class="bristle"` strokes; a kitchen mat is a long cushioned mat whose beveled front edge is `class="bevel"` |
| `pile` | flat, shag, short | unchanged, and drawn on every form |
| `motif` | **none**, **road**, **hopscotch**, **stars** | a kids' rug's motif in one `class="motif"` group: a play road with two cars, a hopscotch court laid along the rug's longer side, or scattered stars |

`motif` defaults to `none`, and the three old forms draw as they did. So every rug product the
generator builds keeps its picture byte for byte, and the test pins those pictures' hashes. A value
outside the table is now refused with a `ValueError` naming the param. Before this slice, an
unknown form drew a rectangle without saying so.

## `vanity_light` and `bench`: types of their own

`drawings.PROPORTIONS` holds one row per type. A vanity bar is wide where a sconce is tall, and a
bench is wide where a chair is tall, so neither variant fits its kin's row. Each one is a type of
its own in `src/synthetic_ecommerce_data/domains/retail/kit_home_variants.py`, built from its
kin's parts: the wall light's plate, arm and drum, and the dining bench's padded seat
(`kit_furniture.BENCH_SEAT`, which `dining_chair` draws too). `kit_home_variants.PARAMS` is the
table:

| Shape | Draws | Params (values) |
|---|---|---|
| `vanity_light` | a bar of shades on one wall plate, over the top of a bathroom mirror | `lights` (1 to 5), `shade` (cone, drum, globe), `aim` (up, down), `finish` (the wall light's nine finishes) |
| `bench` | the bench seat on four legs, three-quarters front | `back` (no, yes), `seat` (upholstered, wood), `storage` (none, shelf, drawers) |

The record's color fills the shades and the bench. The plate and arms are drawn in the light's
finish (chrome when none is stated), and the mirror and a shelf's baskets keep colors of their own.

| Shape | View | Width | Height | Depth |
|---|---|---|---|---|
| `vanity_light` | front | 24 | 9 | 7 |
| `bench` | front | 48 | 18 | 16 |

Both are `upright` in `orientations/home_variants.py` (#1045).

## What the tests promise

`tests/test_home_variants_1022.py` checks:

- Every value of every param of `rug`, `vanity_light` and `bench` draws a picture of its own, as a
  well-formed SVG. On every rug form, each pile and each motif draws a picture of its own.
- A value outside the table is refused with a `ValueError` naming the param.
- Each rug the generator's rows draw (three forms by three piles) has the hash it had before this
  slice.
- A kids' rug draws its motif, and a rug with `motif="none"` draws none. A doormat shows its
  bristles and a kitchen mat its bevel, and the old forms show neither.
- The drawn count is the stated count: one `class="shade"` per light, and two `class="drawer"` on a
  bench with drawers. A bench draws a back (`class="back"`) and a shelf (`class="shelf"`) only
  when it says so.
- A White piece reads white (gen#226): a vanity light, a bench and a kitchen mat.
- A doormat, a kitchen mat, a kids' rug, a vanity light and a bench each draw through
  `drawings.render` in both finishes, at their own dimensions.

## What comes next

Slice 5 ships a home type in a generator build with its own products.
