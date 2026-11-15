# Office & school, slices 1 and 2 (gen#969)

The store had no office or school department, so a search for `gel pens`, `HB pencils` or an
`A4 notebook` found nothing. `Office & school` is now on the closed list of retail departments
(`core/departments.RETAIL`). Slice 1 added writing and paper, and slice 2 filing and desk; each
type is a spec of its own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Pen | `type_specs/pen.py` | Office & School > Pens & Pencils > Pens | Ballpoint, Gel, Rollerball | color x pack of 4, 10, 20 |
| Pencil | `type_specs/pencil.py` | Office & School > Pens & Pencils > Pencils | HB, 2B, 4B, 2H | color x pack of 6, 12, 24 |
| Spiral Notebook | `type_specs/spiral_notebook.py` | Office & School > Paper & Notebooks > Spiral Notebooks | A4 lined, A5 squared, B5 dotted | color x pack of 1, 3, 5 |
| Ring Binder | `type_specs/ring_binder.py` | Office & School > Binders & Folders > Ring Binders | A4 D-ring, A5 round ring, Letter slanted ring, Foolscap D-ring | color x single, pack of 4, 10 |
| Document Folder | `type_specs/document_folder.py` | Office & School > Binders & Folders > Document Folders | A4 elastic, A5 press stud, Foolscap zip, Letter press stud | color x pack of 5, 10, 25 |
| Calculator | `type_specs/calculator.py` | Office & School > Office Electronics > Calculators | 8 digit pocket, 12 digit desktop, 10 digit scientific, 10 digit basic | color x single, class pack of 5, 10 |

The build record's `department` is `Office & Stationery`, from the retail closed list
(`domains/retail/departments.py`), which keys the brand pools. The shared pieces (the paths, the
six main colors of gen#275, `packs()`, `row()` and `decoy()`) are in `office_rows.py`. A SKU's
pack size is its `pack_size` axis, and `pack_copies` draws a pack of ten as ten pens.

**Drawings.** `kit_office.py` draws six shapes. `pen` takes `style` (ballpoint, gel,
rollerball, felt tip), which draws the tip, and `mechanism` (retractable, capped), which draws a
click button or a cap. `pencil` takes `eraser` (yes, no): a ferrule and an eraser, or a dipped
end. `spiral_notebook` takes `binding` (side bound, top bound), which puts the coil on the side or
the top, and `ruling` (lined, squared, plain, dotted), printed on the cover panel.
`ring_binder` draws an open binder lying flat and takes `ring_type` (round ring, d-ring, slanted
ring), the shape of the mechanism's rings. `document_folder` takes `closure` (elastic, press stud,
zip): two elastic bands over the corners, a press stud on the flap, or a zip with its pull.
`calculator` takes `calculator_type` (pocket, basic, desktop, scientific), which sets the case and
its key grid, and `power` (solar, dual power, battery), a solar strip or none. Each param is
the lower-cased attribute value, so a derived style that swaps the value is drawn true (gen#512).

**Breadth.** Every type is derivable. A derived style's twin key is its leaf, brand and
title, so a type yields at most (title-shown value combinations x brands) styles per title
pattern. Two pen templates gave 4 combinations x 2 brands, so only 6 derived pens. The last
template of each type (Bold Rollerball Pens, 2H Technical Pencils, B5 Dotted Spiral Notebook,
each by Thistle & Wren) widens both the value pools and the brand pools. A template whose title
shows three values multiplies the combinations: a fourth binder template titled with its cover
too gave more than three times the binders of a two-value one, so slice 2's templates show two values each and the fourth template widens
one pool instead (Foolscap, Basic). A derived style keeps its template's price, so a type's
templates stay in one price band: a printing calculator at four times a pocket one would have
priced derived pocket calculators like printing ones.

**Decoys.** Each type carries two text-match decoys: class 4 (a color word for a part, such as
a red grip on a black-ink pen, a yellow spine label on a blue binder, red keys on a white
calculator) and class 6 (a color word in a range name, such as `Green Park`, `White Cliffs`,
`Red Fern` or `Blue Ridge`).

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the
authored and derived split are read from the build (`retail_figures`), never typed here. Slice 2's
floor is 2,850 SKUs, about two thirds of the department's 4,500 target in
`docs/catalogue-mix-837.md`. Backpacks, art supplies and desk organizers are slice 3 of gen#969.
The department now holds more styles than `breadth_rows.DEPARTMENT_FLOOR`, so
`tests/test_retail_scale.py` holds it to that floor like every other department. The guards are
in `tests/test_retail_office_969.py`.
