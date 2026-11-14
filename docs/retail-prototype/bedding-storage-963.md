# Bedding and food storage, slice 2 (gen#963)

`Home > Bedding` held duvets and a single microfiber pillow pair, and `Home > Storage` held boxes
and baskets, so a search for `sheet set`, `memory foam pillow` or `food storage containers` found
little or nothing. Slice 2 adds two derivable types and deepens a third, each a spec of its own:

| Type | Spec | Path | Templates | Type values | Second axis | SKU axis |
|---|---|---|---|---|---|---|
| Sheet Set | `type_specs/bed_sheet.py` | Home > Bedding > Sheets | 13, one per brand, and 2 decoys | material: Cotton Percale, Cotton Sateen, Microfiber, Bamboo, Linen, Flannel (drawn) | pocket depth (Standard, Deep, Extra Deep Pocket) | the six main colors times four bed sizes (`bed_size`), each at its price |
| Pillow | `type_specs/pillow.py` | Home > Bedding > Pillows | 11 and 2 decoys, beside the microfiber pair that stays in `samples` | fill: Down Alternative, Memory Foam, Shredded Memory Foam, Cooling Gel, Feather | support (Plush, Soft, Medium, Firm, Extra Firm) | white only, times the standard and the king pillow, each stated in UK, EU and US sizes |
| Food Storage Container | `type_specs/food_storage_container.py` | Home > Storage > Food Storage | 13 and 2 decoys | material: Glass, Plastic, Stainless Steel, Silicone (drawn) | lid (Snap-Lock, Airtight, Leakproof, Vented) | the six main colors of the lids times three piece counts (`piece_count`), each at its price |

The shared pieces (the department, the brands, the six colors, `table()`, `ChartRow` and
`decoy()`) are in `bedding_storage_rows.py`. `table()` makes one template per brand and cycles
the type value and the second axis through the brands, so every value is on a template. The
brands are invented (ruling 2026-10-30, gen#720): Home brands other rows already carry, each
with an owner, a mark and a house style. The pillow brands are the bedding brands less
Wrenfield and Larkmoor, because the line grammar's soft family holds a model word for each of
the other eleven and no more. The scaled build makes one style per brand and title, so these
brands bound each type's depth. A sheet set and a container's lids are sold in red, blue, green,
yellow, black and white (ruling 2026-10-13, gen#275), the first color the hero the image shows;
a pillow keeps its natural white cover (`main_colors.EXCEPTIONS`). A pillow SKU states its size
in every system from core's bedding chart (`variants.BED`), as main's pillows already do.

The sheet leaf is `Sheets`, not `Bed Sheets`: the stable-id hash puts a `Bed Sheets` leaf at the
front of the Home ranking and moves the department shares `test_retail_stable_ids_626` guards.

**Drawings.** `kit_bedding_storage.py` draws two shapes, each taking `kind`, the lower-cased
material, so a derived style that swaps the material is drawn true (gen#512). `sheet_set`
draws a folded stack of three (the flat sheet, the fitted sheet, the pillowcases) in a paper
band, its texture set by the material: a crisp percale, a sheen for sateen, a brushed flannel,
a slubbed linen, a fine bamboo weave. `food_storage` draws two small containers on a large one,
each with its lid, the boxes clear glass, plastic, steel or ribbed silicone, the lids in the
record's color. A pillow keeps main's `pillow` shape, which draws every fill alike: the fill is
inside the cover. `sheet_set` is upright and `food_storage` level (`orientation.py`).

**Decoys.** Each type carries two text-match decoys (ruling 2026-10-14, gen#309): a word naming
something not sold apart in a title (`… with Two Pillowcases`, `… in a Zip Pillowcase Cover`,
`… for Lunch Box Packing`), and another type's name in a range name (`Duvet Lane` sheet set,
`Cushion Hill` pillow, `Breadbin Row` food storage). The structured fields tell the truth.

**Measured** (ceiling build, seed 0, without slice 1): `Home` grows from 14,059 SKUs on main. Sheet Set 3,272 SKUs, Food Storage Container 2,790, Pillow 424 (with the microfiber pair). Floor care and furniture
(slice 3: vacuum cleaners, desks, wall art) is the last slice of gen#963, which with slice 1
reaches its 23,750 floor. The guards are in `tests/test_retail_bedding_storage_963.py`.
