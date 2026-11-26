# Sewing and knitting: thread, yarn, fabric, the tools and the notions (gen#1118)

The retail build held no sewing machine, thread, fabric, yarn or needle, so a shopper's `thread`
found only the industrial catalogue's threaded rods, thread taps and fastener thread sizes. This
cut adds the three types the issue names first. Each type is a spec of its own, under a new node
beside Art Supplies:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Sewing Thread | `type_specs/sewing_thread.py` | Office & School > Sewing & Knitting > Sewing Thread | 500 m all purpose, 250 m quilting, 100 m topstitch, 1000 m embroidery cone | color, a spool sold singly |
| Yarn | `type_specs/yarn.py` | Office & School > Sewing & Knitting > Yarn | DK merino wool, Aran cotton, Chunky acrylic, DK cotton | color x single ball, 5 pack, 10 pack |
| Fabric | `type_specs/fabric.py` | Office & School > Sewing & Knitting > Fabric | cotton poplin, cotton canvas, polyester crepe, polyester jersey | color x fat quarter, 1 meter, 2 meters |

Every style offers the six main colors of gen#275. The build record's `department` is
`Office & Stationery`, the department of `office_rows.py`. The shared pieces (the paths, the
brands, `row()`) are in `sewing_rows.py`. Two invented brands are the range's own: Bobbinmere
(thread, fabric) and Purlwick (yarn). They are appended to the scale range-name roster
(`range_ownership.SCALE.added`), so no other brand's range names move. Calderby & Lune and
Lanternby, the stationery brands, sell the range too.

**Units.** A thread's spool length is measured: `spool_length` is in meters (`MTR`), and its
canonical value is in millimeters. The title reads it (`500 m All Purpose Sewing Thread`), and
the scaled build never changes it. A thread's fiber is an attribute and is named in the
description, not in the title. A yarn states its `yarn_weight` (4 Ply, DK, Aran, Chunky) and its
fiber. A fabric is sold by the cut: `fabric_cut` is the SKU axis that the spec declares
(`Option("fabric_cut", ...)`). A fat quarter costs less than a meter, and a meter less than two.
The cut is in `size_axes.NOT_SIZES`, because the picture shows the same folded fabric whatever
the cut.

**Drawings.** `kit_sewing.py` draws three shapes. `sewing_thread` draws a spool between two
flanges, or a cone from 1000 m up, as tall as its length. Its windings are spaced by `style`, and
`material` adds a sheen. `yarn` is a ball under a paper ball band: the strand is as thick as its
`yarn_weight`, with a fuzzy halo for a wool and a sheen for an acrylic. `fabric` is three folded
layers with the weave of `style` (poplin, canvas, jersey, crepe) on each face. Each param is the
lower-cased attribute value, so a derived style that swaps it is drawn true (gen#512). The
orientations are in `orientations/sewing.py`.

**Decoys.** Each type carries a part-color decoy (class 4) and a range-name decoy (class 6).
`red sewing thread` meets white thread on a red spool; `yellow sewing thread` meets the Yellow
Rose quilting range in red. `green yarn` meets a blue yarn with a green ball band; `black yarn`
meets the Black Sheep range in white. `yellow fabric` meets a blue poplin with a yellow selvage;
`red fabric` meets the Red Robin range in green.

**Measured at cut 1** (ceiling build, seed 0): the cut made 591 SKUs in 66 styles. Sewing Thread had
141 SKUs in 28 styles (22 derived), Yarn had 240 in 20 (14 derived), and Fabric had 210 in 18 (12
derived). The issue's target is about +900 SKUs for its eight types, and this cut is three of
them. The first draft of the cut, with eight colors, three brands per type, thread fiber in the
title and four fabric cuts, made 4,003 SKUs at the ceiling. The test's floor is 340
(`tests/test_retail_sewing_1118.py`, `FLOOR`).

## Cut 2: sewing machines, knitting needles and crochet hooks

Cut 1 gave a knitter yarn and nothing to knit it with, and gave a sewer thread and no machine.
Cut 2 adds three tools, each a spec of its own, drawn by `kit_sewing_tools.py`:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Sewing Machine | `type_specs/sewing_machine.py` | Office & School > Sewing & Knitting > Sewing Machines | mechanical, computerized, heavy duty, mini | color, a machine sold singly |
| Knitting Needles | `type_specs/knitting_needles.py` | Office & School > Sewing & Knitting > Knitting Needles | aluminum straight, plastic circular, aluminum double pointed, plastic straight | color x 4, 5, 6 mm |
| Crochet Hook | `type_specs/crochet_hook.py` | Office & School > Sewing & Knitting > Crochet Hooks | inline aluminum, soft grip aluminum, soft grip plastic, inline plastic | color x 3.5, 4, 5 mm |

**Units.** A needle and a hook are sold by their size in millimeters. Each spec declares its
measured SKU axis: `Option("needle_mm", "needle_size", "Needle size", "MMT")` and
`Option("hook_mm", "hook_size", "Hook size", "MMT")`. Both keys are size axes in `size_axes.AXES`,
so `size_ladder` draws a 6 mm needle larger than a 4 mm one. Each size costs a little more than
the one below it. A machine states its `built_in_stitches` as an attribute and in its
description, not in its title, so a derived machine type never carries a count its template made
up.

**Colors.** A machine style offers the six main colors. A needle or hook style offers three of
them, at three sizes, and the four styles of each type carry all six between them (gen#275). Six
colors at three sizes would have doubled the size of a style.

**Drawings.** `sewing_machine` draws the bed, the pillar and the arm in the body color. The head
holds the needle over the plate, with a handwheel and a spool pin. The pillar shows the
`machine_type`: two dials for a mechanical machine, a screen and buttons for a computerized one,
and a steel face plate and a large handwheel for a heavy duty one. A mini is drawn at two thirds
of the size, with one dial. `knitting_needles` draws a crossed straight pair, two tips on a looped
cable for circular needles, or a set of four double pointed needles. `crochet_hook` draws the
hook's notch and its thumb rest, and adds a ribbed soft grip handle for a soft grip hook. A metal
needle or hook shines. The orientations are in `orientations/sewing_tools.py`: needles and hooks
have no up, and a machine stands level.

**Decoys.** Each type carries a part-color decoy (class 4) and a range-name decoy (class 6).
`yellow sewing machine` meets a white machine with a yellow stitch dial. `blue sewing machine`
meets the Blue Ribbon range in green. `green knitting needles` meets a blue pair with green end
caps. `white knitting needles` meets the White Swan range in red. `yellow crochet hook` meets a
green hook with a yellow thumb rest. `black crochet hook` meets the Black Cat range in blue.

**Measured** (ceiling build, seed 0): each new type is derived as well as authored. The new
templates also move the department's derivation draw, so Yarn gains styles and cut 1's figures
above are cut 1's own. With cut 2 the node passes the issue's +900 target. The counts move with
every slice, so they are measured at run time and not restated here: the test's floor for cut 2
is in `tests/test_retail_sewing_cut2_1118.py` (`FLOOR`). No decoy or row uses a lead word of
another family's model grammar (`line_grammar_families/`), because a word the text uses leaves
that family's deal and moves its styles.

## Cut 3: sewing needles, sewing pins and embroidery kits

Cut 2 left a sewer with thread and a machine but no needle to sew by hand and no pin to hold a
hem, and an embroiderer with floss and nothing to stitch it into. Cut 3 adds the last three types
the issue names, each a spec of its own, drawn by `kit_sewing_notions.py`:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Sewing Needles | `type_specs/sewing_needles.py` | Office & School > Sewing & Knitting > Sewing Needles | sharps, embroidery, tapestry, quilting | color of the needle book x single, 3 pack |
| Sewing Pins | `type_specs/sewing_pins.py` | Office & School > Sewing & Knitting > Sewing Pins | ball head dressmaker, glass head quilting, flat head quilting, ball head tailoring | color of the heads x single, 2 pack |
| Embroidery Kit | `type_specs/embroidery_kit.py` | Office & School > Sewing & Knitting > Embroidery Kits | floral and heart, cross stitch and stamped | floss color, a kit sold singly |

**Counts kept out of the title.** A needle book states how many needles it holds and a pin card
how many pins (`needle_count`, `pin_count`), as an attribute and in the description, never in
the title. The pack drawing reads a count from the title, so a "20" there would draw twenty books.

**Colors.** A needle or a pin style offers three of the six main colors in two packs, and the four
styles of each type carry all six between them (gen#275). A kit offers the six floss colors.

**Drawings.** `sewing_needles` draws the needle book open on its felt page, its steel needles by
kind: five with a round eye (sharps), five with a long eye (embroidery), four thick ones with a
large eye (tapestry) or seven short ones (quilting). `sewing_pins` draws a card with two rows of
pins whose heads are the SKU's color: small round heads, larger glass heads with a shine, or flat
discs. `embroidery_kit` draws the wooden hoop on its linen, the motif (a flower or a heart) worked
as a grid of crosses or a satin stitched shape, and two skeins of the floss. The orientations are
in `orientations/sewing_notions.py`: a needle book and a pin card turn a little, and a hoop is
level.

**Decoys.** Each type carries a part-color decoy (class 4) and a range-name decoy (class 6).
`red sewing needles` meets a blue needle book with a red threader. `green sewing needles` meets
the Green Finch range in yellow. `white sewing pins` meets red-headed pins on a white card.
`yellow sewing pins` meets the Yellow Rose range with blue heads. `black embroidery kit` meets a
green kit with a black hoop. `red embroidery kit` meets the Red Robin range in blue.

**Measured** (ceiling build, seed 0): each new type is derived as well as authored, and cuts 1 and
2's figures do not move. The test's floor for cut 3 is in `tests/test_retail_sewing_cut3_1118.py`
(`FLOOR`); the PR states the measured count.

## The count, and the `thread` demo queries

**The count** (ceiling build, seed 0, main `ee42285d`): the nine types make 1,102 SKUs in 145
products under Office & School > Sewing & Knitting. The issue's target was about +900. The rows are in
[catalogue-mix-837.md](../catalogue-mix-837.md), and #837 holds the table
([comment](https://github.com/alexander-marquardt/synthetic-ecommerce-data/issues/837#issuecomment-7184103726)).

**The queries.** `thread` is a spool of sewing thread and also the thread size of the industrial
catalogue's rods, nuts and bolts. The issue compares `sewing thread white` with `m6 thread`, and
`m6` also names the retail Mervane M6 phone. The three queries are `clash_queries.THREADS`. Each
has a policy, a filter or a x10 boost on a structured field, as in
[clash-queries-1116.md](clash-queries-1116.md). `color` is met by any of a product's SKUs. Measured
by `uv run python -m synthetic_ecommerce_data.clash_queries --thread --ceiling` at main
`ee42285d`: the ceiling retail build and the default industrial build, counted in products:

| Query | Expected | Families found without a policy | Top 10 without a policy | Policy | Families found with it | Top 10 with it |
|---|---|---|---|---|---|---|
| `thread` | Both families; a policy can rank by department intent. | sewing thread 28 (first at 89), industrial thread 5446 (first at 1) | threaded_rod 8, thread_plug_gages 2 | product_type = Sewing Thread x10 | sewing thread 28 (first at 1), industrial thread 5446 (first at 29) | Sewing Thread 10 |
| `sewing thread white` | Sewing thread only (color). | sewing thread 28 (first at 1) | Sewing Thread 10 | filter product_type = Sewing Thread, color = White | sewing thread 25 (first at 1) | Sewing Thread 10 |
| `m6 thread` | Fasteners only (thread size). | industrial thread 5466 (first at 1), the M6 phone 4 (first at 2) | washer_flat 5, Phone Case 3, sems_bolts 1, Smartphone 1 | filter product_type = (industrial) | industrial thread 5466 (first at 1), the M6 phone none | washer_flat 9, sems_bolts 1 |

**On the served index.** `catalog_combined_2026-11-25-1902` (the `catalog_combined` alias on
2026-11-26) carries cuts 1 and 2: 905 sewing SKUs in `Office & school`. Cut 3 arrives with the next
load. Each document there is a SKU. The same three queries ran as a plain BM25 `match` on `text`,
which is not the Engine's query. A boost is a `function_score` of weight 10 that multiplies the
score, and a filter is a `bool` filter. "Industrial" is the departments Hardware, Tools and
Workshop & Safety:

| Query | Hits without | Families without | Top 10 without | Policy | Hits with | Families with | Top 10 with |
|---|---:|---|---|---|---:|---|---|
| `thread` | 28,590 | sewing thread 141 (first at 373), industrial 28,241 (first at 1) | All-thread rods 8, Thread chasers 2 | product_type = Sewing Thread x10 | 28,590 | sewing thread 141 (first at 1), industrial 28,241 (first at 142) | Sewing Thread 10 |
| `sewing thread white` | 72,536 | sewing thread 141 (first at 1), industrial 28,241 (first at 1,122) | Sewing Thread 10 | filter product_type = Sewing Thread, color = White | 25 | sewing thread 25 (first at 1) | Sewing Thread 10 |
| `m6 thread` | 31,269 | sewing thread 141 (first at 3,259), industrial 30,897 (first at 1) | All-thread rods 6, Hex nuts 2, Nylon insert lock nuts 1, Hex head bolts 1 | filter department = Hardware, Tools or Workshop & Safety | 30,897 | industrial 30,897 (first at 1) | All-thread rods 6, Hex nuts 2, Nylon insert lock nuts 1, Hex head bolts 1 |

**What it shows.**

* **The clash is in the data.** Without a policy, the top ten of a bare `thread` is threaded rods,
  and the first spool is at 89 in the build and at 373 on the served index. The boost puts every
  spool first and drops no other product.
* `sewing thread white` finds sewing thread first with no policy. In the template build, the rest
  of its top ten is sewing machines, needles and the dressmaker pins "on a White Card", the cut 3
  decoy. The filter leaves the white thread only.
* `m6 thread` finds fasteners first. In the generator's build, the Mervane M6 phone and its cases
  are at place 2. The served index holds 20 of their SKUs. They score below the fasteners, whose
  `text` states the thread size more than once, so none is in the top ten. The filter to the
  industrial catalogue takes them out.

`tests/test_retail_thread_queries_1118.py` holds the first table: every family is present, each
policy does what its row says on the template build, and the Query, Expected and Policy cells are
the code's. The counts are a record. A product added later moves them, so run the command again
before you quote one.
