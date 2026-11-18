# Health: over-the-counter vitamins, first aid, monitors, eye care, incontinence and mobility aids (gen#968)

`Health` is the retail catalogue's thirteenth department, on the closed list in
`core/departments.RETAIL` and the build's `domains/retail/departments.RETAIL`. The 500K mix
(`docs/catalogue-mix-837.md`) plans 5,000 SKUs for it: vitamins and supplements, first aid,
thermometers and blood-pressure monitors, eye care, incontinence and mobility aids. Before gen#968
a `terms` count on the top level of `category_path` found none, so a shopper's search for vitamins
or a first-aid kit found nothing.

## What is built

The issue grows the department in four slices (the gate comments on gen#968):

| Slice | Types | State |
|---|---|---|
| 1 | `Vitamins`, `Minerals` | built |
| 2 | `Plasters`, `First Aid Kits`, `Thermometers`, `Blood Pressure Monitors`, drawn in `kit_health.py` | built |
| 3 (first cut) | `Eye Drops`, `Incontinence Pads`, `Walking Sticks`, drawn in `kit_health_care.py` | built |
| 4 | depth to 4,750 SKUs: more nutrients, minerals, forms and pack counts, six Health-wide brands, and `Herbal Supplements` and `Omega Oils` | built |

The ceiling build (`retail_figures.ceiling()`, seed 0) holds 363 `Health` SKUs in 168 styles after
slice 1: 213 vitamins and 150 minerals. Its 162 derivable styles are above the floor every
department holds (`breadth_rows.DEPARTMENT_FLOOR`, 150, `tests/test_retail_scale.py`). Slice 2
raises this to 482 SKUs in 245 styles, adding 47 plasters, 34 first-aid kits, 22 thermometers and
16 blood-pressure monitors.
The first cut of slice 3 raises it to 565 SKUs in 299 styles, adding 15 eye drops, 47 packs of
incontinence pads and 22 walking sticks (the seeded draw moves one thermometer, 22 to 21).
Slice 4 raises it to 4,953 SKUs in 1,686 styles, past the 4,750 (95% of the mix's 5,000) the
issue asks of the ceiling build: 1,988 vitamins, 1,248 minerals, 1,098 herbal supplements and 377
omega oils, with the seven slice 2 and 3 types holding 242 (`tests/test_retail_health_depth_968.py`).
A leaf's derived styles cap at its title's combinations times its brands, so the depth comes from
wider values (more nutrients and minerals, Softgels and Gummies beside Tablets and Capsules, a
third and fourth pack count on a row), the six brands that sell across the department
(`department_rates/health.py`'s `EXTRA_BRANDS`) and the two new bottle types.

Health draws its derived styles at a rate of its own, 0.002402 (`department_rates/health.py`):
at the default 0.008 its 102 derivable templates drew 5.89% of a sub-ceiling build's derived
styles, against the 1.85% its template count gives it. The rate moves no style of the ceiling
build, where every template is drawn until it is exhausted.

## Tree

`Health > Vitamins & Supplements > {Vitamins, Minerals, Herbal Supplements, Omega Oils}`. Each
type is a spec in `domains/retail/type_specs/` (`vitamins.py`, `minerals.py`, and slice 4's
`herbal_supplements.py` and `omega_oils.py`): a bottle of tablets, capsules, softgels or gummies
(shape `supplement_bottle`, `colorless`), sold by count. The SKU axis is `piece_count` (30 to
365), and each count is dearer than the last. A row carries the active ingredient (`nutrient`,
`mineral`, `herb` or `supplement_oil`) and the `form` (Tablets, Capsules, Softgels or Gummies),
and its title names both, so the bottle's
label is honest (`tests/test_retail_drawing_honesty.py`). Both types are `derivable`: the scaled
build draws more bottles by swapping the ingredient and the form.

The bottle (`kit_health.py`, gen#1028) replaced the retail `tub`, a tall open pot that read as a
paper cup. It is drawn in the colorway's base (white, amber, sage), with the cap in its accent.
Its wrapped label carries what tells two bottles of one brand apart: the nutrient's name, a band
colored by the nutrient, and a scored tablet or a two-tone capsule by `form`. The nutrient and
the form are the drawing's params, so a derived style that swaps them is redrawn. Within each leaf,
no brand draws two products alike (`tests/test_retail_supplement_bottle_1028.py`). That test also
lists every type still drawn as a `tub`.

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

`Health > Eye Care > Eye Drops`, `Health > Incontinence > Incontinence Pads` and
`Health > Mobility Aids > Walking Sticks` (the first cut of slice 3) reuse `health_rows.py`'s
brands and `row` helper. Each type has its own spec (`eye_drops.py`, `incontinence_pads.py`,
`walking_sticks.py`) and its own shape in `domains/retail/kit_health_care.py`:

| Type | Shape | Param, from the attribute | SKUs |
|---|---|---|---|
| Eye Drops | `eye_drop_bottle`: a carton with the pack in front | `pack` (`eye_care_pack`: Dropper Bottle, Single-Dose Vials, Eye Wash) | a box of 20 to 60 vials (`piece_count`), else one per style |
| Incontinence Pads | `pad_pack`: a soft pack with a pad on its front, one drop per absorbency step and a moon for overnight | `pad_absorbency` (Light, Medium, Heavy, Overnight) | a pack of 10 to 48 (`piece_count`) |
| Walking Sticks | `walking_stick` on its rubber tip | `handle` (`handle_style`, shown as Handle style: Crook, Derby, Offset, T-Handle) | one per style |

Each value of these params draws a different figure too (`tests/test_retail_health_care_968.py`).
No walking stick is white: a white cane signals sight loss and is not a product color.

## Over the counter only, and no claims

Every product is one a shopper can take off the shelf: no prescription medicine. No title or
description claims an effect: no word that cures, treats, prevents, boosts, heals, relieves,
protects or supports, and no "clinically" or "immunity". A description says how the product is
taken and packed (one a day with a meal, a resealable bottle, vegan). `tests/test_retail_health_vitamins_968.py`
refuses a claim word in any `Health` title or description.

Every brand is invented. Velling Apothecary, Ledwick Botanics and Mirefield Naturals are
third-party brands already sold elsewhere in the build, and Vitamin C Orchard appears on one
decoy. Slice 2 adds three third-party brands, Quellmoor Care, Halvering and Thrennick, which sell
first aid and monitors alongside Velling Apothecary. Slice 4 adds two chemist's own labels,
Corvane Pharmacy (a mortar mark) and Brannock Health (twin arcs), and lets all six of Velling
Apothecary, Quellmoor Care, Halvering, Thrennick, Corvane Pharmacy and Brannock Health carry a
derived style of any Health type (`department_rates/health.py`). Their marks and house styles are in
`domains/retail/health_brand_styles.py`; none of the marks is a cross. A description says what is in the kit or how the
device reads; it makes no claim about a condition. A spec declares its brands' owner (`owners=`), the same owner the rest of the build gives them.

## Decoys

Each type plants text-match decoys inside the department (classes 4, 6 and 7): a title holds the
query's ingredient as a color or range word, or the brand holds it (Vitamin C Orchard), while the
fields say another ingredient, so `iron tablets` meets "Iron Grey Bottle Zinc Tablets". Only a policy
that reads the `mineral` or `nutrient` field puts the real bottles first. Slice 2's decoys are class 6: a range name
holds the query's word, so `waterproof plasters` meets "Waterproof Walker Fabric Plasters" and
`wrist blood pressure monitor` meets "Wrist Ease Upper Arm Blood Pressure Monitor". Slice 3's are class 6
too: `derby walking stick` meets "Derby Lane Wooden Crook Walking Stick" and `overnight incontinence
pads` meets "Overnight Bag Light Incontinence Pads". Slice 4's: `garlic capsules` meets "Garlic
Lane Turmeric Capsules" and `krill oil softgels` meets "Krill Bay Fish Oil Softgels" (class 6), and
`ginger tablets` meets "Ginger Cap Bottle Echinacea Tablets" (class 4). The decoys are in each spec's
`DECOYS`, and the output standard's text check leaves them out (`scale.TEXT_EXEMPT`).

## The four per-type gates

The issue's Done-when asks each added type to pass four gates. For a retail spec they are read as four
checks in the type's own test file (`tests/test_retail_health_vitamins_968.py` for slices 1 and 4,
`tests/test_retail_health_first_aid_968.py` for slice 2, `tests/test_retail_health_care_968.py` for
slice 3):

- **uniqueness**: no `product_id`, SKU or title is shared within the type in the ceiling build;
- **census**: the spec is registered in its department and tree, plants its decoys, and its documents
  pass the output standard (`core/standard.check_catalog`);
- **byte-determinism**: two processes under two hash seeds build byte-identical documents;
- **a golden slice**: the committed `tests/data/golden_slices_retail/<key>.jsonl` (apart from `golden_slices/`, which `scripts/golden_pins.py` rebuilds as industrial types) equals a fresh build.
  Rewrite the slices by running the slice's test file as a script (`uv run python tests/test_retail_health_first_aid_968.py`).
