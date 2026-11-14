# Office & school, slices 1 and 3 (gen#969)

The store had no office or school department, so a search for `gel pens`, `HB pencils` or an
`A4 notebook` found nothing. `Office & school` is now on the closed list of retail departments
(`core/departments.RETAIL`), and its first three types are specs of their own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Pen | `type_specs/pen.py` | Office & School > Pens & Pencils > Pens | Ballpoint, Gel, Rollerball | color x pack of 4, 10, 20 |
| Pencil | `type_specs/pencil.py` | Office & School > Pens & Pencils > Pencils | HB, 2B, 4B, 2H | color x pack of 6, 12, 24 |
| Spiral Notebook | `type_specs/spiral_notebook.py` | Office & School > Paper & Notebooks > Spiral Notebooks | A4 lined, A5 squared, B5 dotted | color x pack of 1, 3, 5 |
| School Backpack | `type_specs/school_backpack.py` | Office & School > Bags & Cases > School Backpacks | 20 L classic, 25 L laptop, 30 L rolling, 15 L mini | color, sold singly |
| Colored Pencils | `type_specs/colored_pencils.py` | Office & School > Art Supplies > Colored Pencils | 12 classic, 24 watercolor, 36 soft core, 48 erasable | tin color x pack of 1, 2, 3 tins |
| Desk Organizer | `type_specs/desk_organizer.py` | Office & School > Desk Accessories > Desk Organizers | 5 compartment mesh, 3 plastic, 4 felt, 6 metal | color x pack of 1, 2, 4 |

Slice 3 (the last three rows) adds the bag, art and desk types. School Backpack is its own
product type, apart from Clothing's `Backpack` accessories. A set of colored pencils holds many
colors, so its SKU's color is the tin's; the drawing shows the set's own count (its `count`
param), so a tin is one item and a 2 or 3 pack is that many tins.

The build record's `department` is `Office & Stationery`, from the retail closed list
(`domains/retail/departments.py`), which keys the brand pools. The shared pieces (the paths, the
six main colors of gen#275, `packs()`, `row()` and `decoy()`) are in `office_rows.py`. A SKU's
pack size is its `pack_size` axis, and `pack_copies` draws a pack of ten as ten pens.

**Drawings.** `kit_office.py` draws three shapes. `pen` takes `style` (ballpoint, gel,
rollerball, felt tip), which draws the tip, and `mechanism` (retractable, capped), which draws a
click button or a cap. `pencil` takes `eraser` (yes, no): a ferrule and an eraser, or a dipped
end. `spiral_notebook` takes `binding` (side bound, top bound), which puts the coil on the side or
the top, and `ruling` (lined, squared, plain, dotted), printed on the cover panel. Each param is
the lower-cased attribute value, so a derived style that swaps the value is drawn true (gen#512).

**Breadth.** The three types are derivable. A derived style's twin key is its leaf, brand and
title, so a type yields at most (title-shown value combinations x brands) styles per title
pattern. Two pen templates gave 4 combinations x 2 brands, so only 6 derived pens. The last
template of each type (Bold Rollerball Pens, 2H Technical Pencils, B5 Dotted Spiral Notebook,
each by Thistle & Wren) widens both the value pools and the brand pools.

Slice 3's drawings: `school_backpack` takes `backpack_style` (classic, laptop, rolling, mini): a
padded laptop panel, a telescopic handle and wheels, or a smaller bag with a reflective strip.
`colored_pencils` takes `pencil_type` (classic, watercolor, soft core, erasable) and `count`: up to
twelve pencils stand in the open tin, thicker for soft core, with a brush or an eraser before the
tin, and the count printed on its front. `desk_organizer` takes `compartments` (the number of
sections, stepped front to back) and `material` (mesh, plastic, felt, metal).

**Decoys.** Each type carries two text-match decoys: class 4 (a color word for a part, such as
a red grip on a black-ink pen) and class 6 (a color word in a range name, such as `Green Park`).

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the
authored and derived split are read from the build (`retail_figures`), never typed here. It is
Slice 1 held at least 1,400 SKUs and slice 3 holds at least 1,425 more on its own; with slice 2's
binders, folders and calculators (at least 1,450) the department meets the issue's 4,275, 95% of
its 4,500 target in `docs/catalogue-mix-837.md`. The guards are in
`tests/test_retail_office_969.py`.
