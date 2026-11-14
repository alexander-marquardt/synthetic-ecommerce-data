# Cleaning, slice 1: paper goods (gen#962)

The Cleaning department held mostly sprays and detergents, so a search for `toilet paper`,
`paper towels` or `tissues` found little or nothing. Slice 1 of gen#962 adds the paper goods a
shopper expects there. Each one is a spec type of its own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Toilet Paper | `type_specs/toilet_paper.py` | Cleaning > Paper Goods > Toilet Paper | Ultra Soft 2-Ply Double, Quilted 3-Ply Mega, Ultra Strong 4-Ply Regular, Recycled 2-Ply Regular | pack of 4, 6, 9, 12, 18, 24 rolls |
| Paper Towels | `type_specs/paper_towels.py` | Cleaning > Paper Goods > Paper Towels | Extra Absorbent Full Sheet Double, Ultra Strong Half Sheet Triple, Embossed Half Sheet Regular, Recycled Full Sheet Regular | pack of 2, 4, 6, 8, 12 rolls |
| Facial Tissues | `type_specs/facial_tissues.py` | Cleaning > Paper Goods > Facial Tissues | Lotion 3-Ply Cube, Aloe Vera 2-Ply Flat, Extra Soft 2-Ply Cube, Menthol 3-Ply Flat | color x pack of 1, 4, 8, 12 boxes |

The build record's `department` is `Cleaning & Janitorial`, from the retail closed list
(`domains/retail/departments.py`), which keys the brand pools. The shared pieces (the paths, the
six main colors of gen#275, `packs()`, `row()` and `decoy()`) are in `paper_rows.py`. A SKU's
pack size is its `pack_size` axis, so a pack of twelve rolls is drawn as twelve rolls.

**Colors.** A roll of toilet paper or paper towels is white paper and is sold without a color
(`colorless`): its SKUs are its packs only. That is the type's declared exception to the six main
colors of gen#275. A tissue box is sold in all six main colors (red, blue, green, yellow, black,
white), times its packs.

**Brands.** Every brand is invented (gen#720). Featherlee, Mossdown and Hollinsby are new, and
each has its own mark and house style in `paper_brand_styles.py`: Featherlee has a feather in a
lockup, Mossdown three cloud puffs, and Hollinsby two leaves in a ring. The department's
existing brands, Clearbrook Household and Soapwell, join them in the derived styles' brand pools
(`scale.EXTRA_BRANDS`), so no template names them.

**Drawings.** `kit_paper.py` draws three shapes, each upright. `toilet_roll` takes `roll_size`,
`ply` and `finish` (a quilted surface, or a leaf on a recycled roll). `paper_towel_roll` takes
`roll_size`, `sheet` (full or half sheet, drawn as the spacing of the perforations) and `finish`
(an embossed surface, or a leaf on a recycled roll). `tissue_box` takes `box` (cube or flat) and
`ply`. Each param is the lower-cased attribute value, so a derived style that swaps the value is
drawn true (gen#512).

**Breadth.** The three types are derivable: the scaled build draws more styles from the four
templates of each type by the values their titles show (finish, ply or sheet, and roll size or
box), across the department's brands.

**Decoys.** Each type carries two text-match decoys: class 4 (the shopper's word used for
something else, such as a smooth roll whose description says it has no quilted pattern, or a red
trim on a box of another color) and class 6 (the word in a range name, such as `Quilted
Hill` or `Blue Bay`).

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the
authored and derived split are read from the build (`retail_figures`), never typed here. The
slice's floor is 2,800 Cleaning SKUs at the ceiling build, against the department's 9,000 target
in `docs/catalogue-mix-837.md`. Trash bags, food storage and food wrap (slice 2), and cloths,
tablets, laundry and power (slice 3) are later slices of gen#962. The guards are in
`tests/test_retail_cleaning_paper_962.py`.
