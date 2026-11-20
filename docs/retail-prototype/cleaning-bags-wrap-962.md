# Cleaning, slice 2: bags and wraps (gen#962)

After slice 1's paper goods ([cleaning-paper-962.md](cleaning-paper-962.md)), the Cleaning
department still had no trash bags, zip bags, foil or plastic wrap, so a search for `trash bags`
or `aluminum foil` found nothing. Slice 2 of gen#962 adds them. Each one is a spec type of its
own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Trash Bags | `type_specs/trash_bags.py` | Cleaning > Bags & Wraps > Trash Bags | Heavy Duty Drawstring Kitchen, Everyday Tie Handle Bathroom, Tear Resistant Flap Tie Outdoor, Everyday Drawstring Bathroom | color x pack of 1, 2, 4 rolls |
| Food Storage Bags | `type_specs/food_storage_bags.py` | Cleaning > Bags & Wraps > Food Storage Bags | Zip Seal Freezer Large, Slider Sandwich Medium, Fold Top Snack Small, Zip Seal Sandwich Small | pack of 1, 2, 3, 4, 6 boxes |
| Food Wrap | `type_specs/food_wrap.py` | Cleaning > Bags & Wraps > Food Wrap | Heavy Duty Aluminum Foil Jumbo, Everyday Plastic Wrap Regular, Extra Wide Parchment Paper Large, Everyday Wax Paper Regular | pack of 1, 2, 3 rolls |

The paths and the attribute helpers are in `bags_wrap_rows.py`. The department
(`Cleaning & Janitorial`), the six main colors of gen#275, `packs()`, `row()` and `decoy()` are
slice 1's, in `paper_rows.py`. A SKU's pack size is its `pack_size` axis, so a pack of four rolls
is drawn as four (`pack_copies`).

**Colors.** A trash bag is sold in all six main colors (red, blue, green, yellow, black, white),
times its packs. A food storage bag is clear film and a roll of wrap takes its material's color,
so both are sold without a color (`colorless`): their SKUs are their packs only. That is each
type's declared exception to gen#275, the one a roll of white paper takes in slice 1.

**Brands.** Every brand is invented (gen#720). The templates are sold by slice 1's Featherlee,
Mossdown and Hollinsby, which already have their marks and house styles
(`paper_brand_styles.py`), so this slice adds no brand. The derived styles draw from the
department's brand pools.

**Drawings.** `kit_bags_wrap.py` draws three shapes, each upright. `trash_bag` is a full bag in
its color: `closure` closes its neck (a drawstring's two loops, a tie handle's two ears, a flap
tie's four flaps) and `use` sizes it (bathroom, kitchen, outdoor). `zip_bag` is clear film lying
flat: `closure` draws the seal (a zip seal's two tracks, a slider's tab, a fold top's flap), `kind`
what it holds (a freezer bag's write-on panel and snowflake, a sandwich bag's slice of bread, a
snack bag's crackers) and `bag_size` its size. `wrap_box` is a long box with a sheet pulled over its
cutting edge: `material` colors the sheet and the band on the box, `roll` sets the box's length,
and `grade` draws an extra wide roll as a deeper box (everyday and heavy duty are a feel, not a
look). Each param is the lower-cased attribute value, so a derived style that swaps the value is
drawn true (gen#512).

**Breadth.** The three types are derivable: the scaled build draws more styles from the four
templates of each type by the values their titles show (strength, closure and use; closure, kind
and size; grade, material and roll), across the department's brands. Each description names
those values in a sentence that stays true when a derived style swaps one.

**Decoys.** Each type carries two text-match decoys: class 4 (the shopper's word used for
something else: unscented bags whose description says they have no scented film, thin sandwich
bags that are not freezer bags, parchment paper used in place of aluminum foil) and class 6 (the
word in a range name: `Black Rock` white trash bags, `Freezer Point` snack bags, `Wax Lane`
aluminum foil).

**Measured** (ceiling build, seed 0): the department's size and its styles per type are read from
the build (`retail_figures`), never typed here. The slice's floor is 5,600 Cleaning SKUs at the
ceiling build, against the department's 9,000 target in `docs/catalogue-mix-837.md`. Every
template is exhausted at the ceiling build, so `scale.DEPARTMENT_RATE` changes no ceiling figure,
and the department shares stay inside the drift `tests/test_retail_stable_ids_626.py` allows.
Sponges and cloths, dishwasher tablets and laundry pods are slice 3, in
[cleaning-care-962.md](cleaning-care-962.md). The guards are in
`tests/test_retail_cleaning_bags_wrap_962.py`.
