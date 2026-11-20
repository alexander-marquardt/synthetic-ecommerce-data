# Cleaning, slice 3: sponges, cloths, tablets and pods (gen#962)

After slice 2's bags and wraps ([cleaning-bags-wrap-962.md](cleaning-bags-wrap-962.md)), the
Cleaning department still had no sponge, dishcloth, dishwasher tablet or laundry pod type, so a
search for `scrub sponge` or `dishwasher tablets` found little or nothing. Slice 3 of gen#962 adds
them. Each one is a spec type of its own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Sponges & Cloths | `type_specs/sponges_cloths.py` | Cleaning > Cleaning Tools > Sponges & Cloths | Heavy Duty Kitchen Scrub Sponge, Everyday Bathroom Non-Scratch Sponge, Everyday All Purpose Microfiber Cloth, Everyday Kitchen Dish Cloth, Heavy Duty All Purpose Cellulose Sponge | color x pack of 1, 3, 6 |
| Dishwasher Tablets | `type_specs/dishwasher_tablets.py` | Cleaning > Kitchen & Surfaces > Dishwasher Tablets | Classic Spring Rain 30 Count, All in One Clean Breeze 50 Count, Max Clean Unscented 80 Count, Quick Wash Spring Rain 50 Count | pack of 1, 2, 3 boxes |
| Laundry Pods | `type_specs/laundry_pods.py` | Cleaning > Laundry > Laundry Pods | Deep Clean Spring Rain 42 Loads, Sensitive Skin Unscented 24 Loads, Oxi Boost Clean Breeze 64 Loads, Deep Clean Clean Breeze 24 Loads | pack of 1, 2, 3 tubs |

The paths and the attribute helpers are in `cleaning_care_rows.py`. The department
(`Cleaning & Janitorial`), the six main colors of gen#275, `packs()`, `row()` and `decoy()` are
slice 1's, in `paper_rows.py`; `lowered()` is slice 2's, in `bags_wrap_rows.py`. A SKU's pack size
is its `pack_size` axis, so a pack of six sponges is drawn as six (`pack_copies`).

**Colors.** A sponge or a cloth is sold in all six main colors (red, blue, green, yellow, black,
white), times its packs. A box of tablets and a tub of pods are sold without a color
(`colorless`): their own colors are the scent's and the formula's. That is the declared exception
to gen#275 that a roll of white paper takes in slice 1.

**Brands.** Every brand is invented (ruling 2026-10-30, gen#720). The templates use Featherlee,
Mossdown and Hollinsby, which already have their marks and house styles
(`paper_brand_styles.py`), so this slice adds no brand. The derived styles draw from the
department's brand pools.

**Drawings.** `kit_cleaning_care.py` draws three shapes, each upright. `sponge_cloth` is a sponge
block or a folded cloth in the SKU's color: `kind` draws a scrub sponge's dark green scourer, a
non-scratch sponge's pale blue one, a cellulose sponge's pores, a microfiber cloth's fine weave, or
a dish cloth's waffle grid and hanging loop. `tablet_box` is a box with one tablet stood before
it: `formula` draws the tablet's layers and its red ball, `scent` colors the band on the box, and
`tablet_count` sets the box's width. `pod_tub` is a tub with one pod before it: `formula` draws
the pod's chambers (three, one for sensitive skin, and rising bubbles for oxi boost), `scent`
colors the pod's liquid and the tub's lid, and `loads` sets the tub's height. Each param is the
lower-cased attribute value, so a derived style that swaps the value is drawn true (gen#512). A
sponge's `grade` and `use` are a feel and a room, not a look, and are not drawn.

**Breadth.** The three types are derivable: the scaled build draws more styles from the templates
of each type by the values their titles show (grade, use and kind; formula, scent and tablet
count; formula, scent and loads), across the department's brands. Each description names those
values in a sentence that stays true when a derived style swaps one.

**Decoys.** Each type carries two text-match decoys: class 4 (the shopper's word used for
something else: a microfiber cloth with no scrub side for `scrub sponge`, tablets with no rinse
aid in the box for `rinse aid`, softener-free pods for `fabric softener`) and class 6 (the word in
a range name: `Yellow Ridge` white sponges, `Classic Point` Max Clean tablets, `Sensitive Bay` Oxi
Boost pods).

**Measured** (ceiling build, seed 0): the department's size and its styles per type are read from
the build (`retail_figures`), never typed here. The issue's floor is 8,550 Cleaning SKUs at the
ceiling build, 95% of the department's 9,000 target in `docs/catalogue-mix-837.md`. Every
template is exhausted at the ceiling build, so `scale.DEPARTMENT_RATE` changes no ceiling figure,
and the department shares stay inside the drift `tests/test_retail_stable_ids_626.py` allows.
The guards are in `tests/test_retail_cleaning_care_962.py`.
