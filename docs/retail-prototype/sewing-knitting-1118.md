# Sewing and knitting: thread, yarn, fabric and the tools (gen#1118)

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

**Left for the next cut:** needles and pins, and embroidery kits; #837's department count; and
the `thread` demo queries (`sewing thread white` against `m6 thread`, without and with a policy)
on an index that carries the range.
