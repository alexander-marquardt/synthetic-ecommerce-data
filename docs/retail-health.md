# Health: over-the-counter vitamins, first aid and monitors (gen#968)

`Health` is the retail catalogue's thirteenth department, on the closed list in
`core/departments.RETAIL` and the build's `domains/retail/departments.RETAIL`. The 500K mix
(`docs/catalogue-mix-837.md`) plans 5,000 SKUs for it: vitamins and supplements, first aid,
thermometers and blood-pressure monitors, eye care, incontinence and mobility aids. Before gen#968
a `terms` count on the top level of `category_path` found none, so a shopper's search for vitamins
or a first-aid kit found nothing.

## What is built

The issue grows the department in three slices (the gate comment on gen#968):

| Slice | Types | State |
|---|---|---|
| 1 | `Vitamins`, `Minerals` | built |
| 2 | plasters, first-aid kits, thermometers, blood-pressure monitors, drawn in a new `kit_health.py` | to do |
| 3 | eye care, incontinence, mobility aids, then depth to 4,750 SKUs | to do |

The ceiling build (`retail_figures.ceiling()`, seed 0) holds 363 `Health` SKUs in 168 styles after
slice 1: 213 vitamins and 150 minerals. That is 162 derivable styles, above the floor every
department holds (`breadth_rows.DEPARTMENT_FLOOR`, 150, `tests/test_retail_scale.py`).

## Tree

`Health > Vitamins & Supplements > {Vitamins, Minerals}`. Each type is a spec in
`domains/retail/type_specs/` (`vitamins.py`, `minerals.py`): a tub of tablets or capsules
(shape `tub`, `colorless`), sold by count. The SKU axis is `piece_count` (30, 60, 90, 120 or 180),
and each count is dearer than the last. A row carries the active ingredient (`nutrient` or
`mineral`) and the `form` (Tablets or Capsules), and its title names both, so the tub drawing's
label is honest (`tests/test_retail_drawing_honesty.py`). Both types are `derivable`: the scaled
build draws more tubs by swapping the ingredient and the form.

## Over the counter only, and no claims

Every product is one a shopper can take off the shelf: no prescription medicine. No title or
description claims an effect: no word that cures, treats, prevents, boosts, heals, relieves,
protects or supports, and no "clinically" or "immunity". A description says how the product is
taken and packed (one a day with a meal, a resealable tub, vegan). `tests/test_retail_health_vitamins_968.py`
refuses a claim word in any `Health` title or description.

Every brand is invented: Velling Apothecary, Ledwick Botanics and Mirefield Naturals,
each a third-party brand already sold elsewhere in the build, and Vitamin C Orchard on one
decoy. A spec declares its brands' owner (`owners=`), the same owner the rest of the build gives them.

## Decoys

Each type plants text-match decoys inside the department (classes 4, 6 and 7): a title holds the
query's ingredient as a color or range word, or the brand holds it (Vitamin C Orchard), while the
fields say another ingredient, so `iron tablets` meets "Iron Grey Tub Zinc Tablets". Only a policy
that reads the `mineral` or `nutrient` field puts the real tubs first. The decoys are in each spec's
`DECOYS`, and the output standard's text check leaves them out (`scale.TEXT_EXEMPT`).

## The four per-type gates

The issue's Done-when asks each added type to pass four gates. For a retail spec they are read as four
checks in the type's own test file (`tests/test_retail_health_vitamins_968.py` for slice 1):

- **uniqueness**: no `product_id`, SKU or title is shared within the type in the ceiling build;
- **census**: the spec is registered in its department and tree, plants its decoys, and its documents
  pass the output standard (`core/standard.check_catalog`);
- **byte-determinism**: two processes under two hash seeds build byte-identical documents;
- **a golden slice**: the committed `tests/data/golden_slices_retail/<key>.jsonl` (apart from `golden_slices/`, which `scripts/golden_pins.py` rebuilds as industrial types) equals a fresh build.
  Rewrite the slices with `uv run python tests/test_retail_health_vitamins_968.py`.
