# Sewing and knitting, cut 1: thread, yarn and fabric (gen#1118)

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

**Measured** (ceiling build, seed 0): the cut makes 591 SKUs in 66 styles. Sewing Thread has
141 SKUs in 28 styles (22 derived), Yarn has 240 in 20 (14 derived), and Fabric has 210 in 18 (12
derived). The issue's target is about +900 SKUs for its eight types, and this cut is three of
them. The first draft of the cut, with eight colors, three brands per type, thread fiber in the
title and four fabric cuts, made 4,003 SKUs at the ceiling. The test's floor is 340
(`tests/test_retail_sewing_1118.py`, `FLOOR`).

**Left for the next cut:** sewing machines, needles and pins, knitting needles and crochet hooks,
and embroidery kits; #837's department count; and the `thread` demo queries (`sewing thread
white` against `m6 thread`, without and with a policy) on an index that carries the range.
