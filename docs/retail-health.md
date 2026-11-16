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
| 2 | `Plasters`, `First Aid Kits`, `Thermometers`, `Blood Pressure Monitors`, drawn in `kit_health.py` | built |
| 3 | eye care, incontinence, mobility aids, then depth to 4,750 SKUs | to do |

The ceiling build (`retail_figures.ceiling()`, seed 0) holds 363 `Health` SKUs in 168 styles after
slice 1: 213 vitamins and 150 minerals. Its 162 derivable styles are above the floor every
department holds (`breadth_rows.DEPARTMENT_FLOOR`, 150, `tests/test_retail_scale.py`). Slice 2
raises this to 482 SKUs in 245 styles, adding 47 plasters, 34 first-aid kits, 22 thermometers and
16 blood-pressure monitors. With those four templates, Clothing's share of derived styles fell to
40.6% against its 44% target, past the 3-point drift `tests/test_retail_stable_ids_626.py`
allows, so `scale.DEPARTMENT_RATE` for Clothing is recomputed (0.01227 to 0.01328, the old rate
times 44 / 40.6). The Health counts above do not move with it.

## Tree

`Health > Vitamins & Supplements > {Vitamins, Minerals}`. Each type is a spec in
`domains/retail/type_specs/` (`vitamins.py`, `minerals.py`): a tub of tablets or capsules
(shape `tub`, `colorless`), sold by count. The SKU axis is `piece_count` (30, 60, 90, 120 or 180),
and each count is dearer than the last. A row carries the active ingredient (`nutrient` or
`mineral`) and the `form` (Tablets or Capsules), and its title names both, so the tub drawing's
label is honest (`tests/test_retail_drawing_honesty.py`). Both types are `derivable`: the scaled
build draws more tubs by swapping the ingredient and the form.

`Health > First Aid > {Plasters, First Aid Kits}` and `Health > Health Monitors > {Thermometers,
Blood Pressure Monitors}` (slice 2) share `domains/retail/health_rows.py`: the paths, the brands
and a `row` helper. Each type has its own spec (`plasters.py`, `first_aid_kits.py`,
`thermometers.py`, `blood_pressure_monitors.py`) and its own shape in `domains/retail/kit_health.py`:

| Type | Shape | Param, from the attribute | SKUs |
|---|---|---|---|
| Plasters | `plaster_box`: a carton with one plaster in front | `plaster` (`plaster_type`: Fabric, Waterproof, Clear, Blister, Sensitive) | a box of 6 to 80 (`piece_count`) |
| First Aid Kits | `first_aid_kit`, in green with the white cross of the first-aid sign | `case` (Soft Pouch, Hard case) | the kit's piece count |
| Thermometers | `thermometer` | `kind` (`thermometer_type`: Digital Stick, Ear, Forehead) | one per style |
| Blood Pressure Monitors | `bp_monitor`: a desk unit with an arm cuff, or a wrist unit | `fit` (Upper Arm, Wrist) | one per style |

A row's drawing param is the lower-cased value of its attribute. A derived style that swaps the
value therefore draws what it states (gen#512), and each value draws a different figure
(`tests/test_retail_health_first_aid_968.py`). The rows are `colorless`: the box, case or body color
appears in the drawing only. A first-aid kit's cross is white on green, never a red one.

## Over the counter only, and no claims

Every product is one a shopper can take off the shelf: no prescription medicine. No title or
description claims an effect: no word that cures, treats, prevents, boosts, heals, relieves,
protects or supports, and no "clinically" or "immunity". A description says how the product is
taken and packed (one a day with a meal, a resealable tub, vegan). `tests/test_retail_health_vitamins_968.py`
refuses a claim word in any `Health` title or description.

Every brand is invented. Velling Apothecary, Ledwick Botanics and Mirefield Naturals are
third-party brands already sold elsewhere in the build, and Vitamin C Orchard appears on one
decoy. Slice 2 adds three third-party brands, Quellmoor Care, Halvering and Thrennick, which sell
first aid and monitors alongside Velling Apothecary. Their marks and house styles are in
`domains/retail/health_brand_styles.py`; none of the marks is a cross. A description says what is in the kit or how the
device reads; it makes no claim about a condition. A spec declares its brands' owner (`owners=`), the same owner the rest of the build gives them.

## Decoys

Each type plants text-match decoys inside the department (classes 4, 6 and 7): a title holds the
query's ingredient as a color or range word, or the brand holds it (Vitamin C Orchard), while the
fields say another ingredient, so `iron tablets` meets "Iron Grey Tub Zinc Tablets". Only a policy
that reads the `mineral` or `nutrient` field puts the real tubs first. Slice 2's decoys are class 6: a range name
holds the query's word, so `waterproof plasters` meets "Waterproof Walker Fabric Plasters" and
`wrist blood pressure monitor` meets "Wrist Ease Upper Arm Blood Pressure Monitor". The decoys are in each spec's
`DECOYS`, and the output standard's text check leaves them out (`scale.TEXT_EXEMPT`).

## The four per-type gates

The issue's Done-when asks each added type to pass four gates. For a retail spec they are read as four
checks in the type's own test file (`tests/test_retail_health_vitamins_968.py` for slice 1,
`tests/test_retail_health_first_aid_968.py` for slice 2):

- **uniqueness**: no `product_id`, SKU or title is shared within the type in the ceiling build;
- **census**: the spec is registered in its department and tree, plants its decoys, and its documents
  pass the output standard (`core/standard.check_catalog`);
- **byte-determinism**: two processes under two hash seeds build byte-identical documents;
- **a golden slice**: the committed `tests/data/golden_slices_retail/<key>.jsonl` (apart from `golden_slices/`, which `scripts/golden_pins.py` rebuilds as industrial types) equals a fresh build.
  Rewrite the slices by running the slice's test file as a script (`uv run python tests/test_retail_health_first_aid_968.py`).
