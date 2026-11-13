# Office & school, slice 1 (gen#969)

The store had no office or school department, so a search for `gel pens`, `HB pencils` or an
`A4 notebook` found nothing. `Office & school` is now on the closed list of retail departments
(`core/departments.RETAIL`), and its first three types are specs of their own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Pen | `type_specs/pen.py` | Office & School > Pens & Pencils > Pens | Ballpoint, Gel, Rollerball | color x pack of 4, 10, 20 |
| Pencil | `type_specs/pencil.py` | Office & School > Pens & Pencils > Pencils | HB, 2B, 4B, 2H | color x pack of 6, 12, 24 |
| Spiral Notebook | `type_specs/spiral_notebook.py` | Office & School > Paper & Notebooks > Spiral Notebooks | A4 lined, A5 squared, B5 dotted | color x pack of 1, 3, 5 |

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

**Decoys.** Each type carries two text-match decoys: class 4 (a color word for a part, such as
a red grip on a black-ink pen) and class 6 (a color word in a range name, such as `Green Park`).

**Measured** (ceiling build, seed 0): 1,560 SKUs in 108 styles under Office & school (Pens 29
styles, Pencils 50, Spiral Notebooks 29; 16 authored with the decoys, 92 derived), about 35% of the department's
4,500 target in `docs/catalogue-mix-837.md`. Binders and folders, backpacks and the
rest of the department are later slices of gen#969. The guards are in
`tests/test_retail_office_969.py`.
