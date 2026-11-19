# Retail Automotive: car care, fluids, electrics and interior (gen#970, slices 1 to 3)

The retail catalogue had no `Automotive` department: `core/departments.RETAIL` did not list it and
no `category_path` started with it. gen#970 adds it in three slices of about 2,000 SKUs in all
(`docs/catalogue-mix-837.md`). Slice 1 adds the department and its first family,
`Automotive > Car Care`: nine types whose rows are in `automotive_rows.py` and whose spec files are
in `type_specs/` (`car_shampoo.py` to `microfiber_towel.py`). Slice 2 adds fluids and
electrics, and slice 3 adds the interior and moves Jump Leads and Car Boot Organiser from `Home`
(sections below).

| Type | Path | Style axis | SKU axis | Key attributes |
|---|---|---|---|---|
| Car Shampoo | Automotive > Car Care > Car Shampoo | brand and formula (pH neutral, wash and wax, snow foam, waterless, ceramic) | bottle size (ml) | formula |
| Car Wax | Automotive > Car Care > Car Wax | brand, wax type and form (paste, liquid, spray) | net weight (g) | wax type, wax form |
| Car Polish | Automotive > Car Care > Car Polish | brand and polish type | bottle size (ml) | polish type |
| Windshield Washer Fluid | Automotive > Car Care > Windshield Washer Fluid | brand, blend and form (ready to use, concentrate) | bottle size (ml) | blend, fluid form |
| Car Interior Cleaner | Automotive > Car Care > Car Interior Cleaners | brand and surface | bottle size (ml) | surface |
| Wiper Blade | Automotive > Car Care > Wiper Blades | brand, blade type (conventional, flat, hybrid, rear, winter) | blade length (in) | blade type, connector, season, wiper position |
| Car Air Freshener | Automotive > Car Care > Car Air Fresheners | brand, format and scent | pack size | freshener format, scent |
| Wash Mitt | Automotive > Car Care > Wash Mitts | brand and material | size | material |
| Microfiber Towel | Automotive > Car Care > Microfiber Towels | brand and towel type | dimensions | material, towel type |

The templates hold 194 styles and 756 SKUs. Every brand is invented (`automotive_brand_styles.py`:
Glossmere, Kestrova, Drayfield and Ostrel), each with a mark of its own and a house style.

## Color

A liquid, a wax, a blade and an air freshener carry no color: the bottle's color is not what a
shopper picks, so the row is `colorless` and its drawing takes the brand's pack color. A wash mitt
and a microfiber towel are sold by color and come in the six main colors (gen#275); a lambswool
mitt is sold in its natural cream.

## Drawings

`kit_automotive.py` draws five new shapes: `wiper_blade`, `fluid_jug`, `air_freshener`,
`wash_mitt` and `microfiber_towel`. The bottled types reuse the kit's bottle and trigger-spray
shapes.

## Text-match decoys

Each type carries two decoys (`automotive_rows.DECOY_ROWS`), copies of an authored row whose title
or description misleads while its structured fields tell the truth.

## Tests

`tests/test_retail_automotive_970.py` holds the slice's Done-when: the ceiling build holds at least
600 SKUs under `Automotive`, no Automotive product id or SKU id repeats, the department's templates
are the same bytes on every build, and the first style of each type is pinned to
`tests/data/retail_automotive_970_golden.json`. A change to the rows that moves the golden slice
regenerates that fixture by hand, so the diff shows it.

## Slice 2: fluids and electrics

Slice 2 adds two families, `Automotive > Fluids` and `Automotive > Electrics`: six types whose rows
are in `automotive_fluids_rows.py` and whose spec files are in `type_specs/` (`motor_oil.py`,
`coolant.py`, `jump_starter.py`, `tire_inflator.py`, `phone_mount.py`, `car_charger.py`).

| Type | Path | Style axis | SKU axis | Key attributes |
|---|---|---|---|---|
| Motor Oil | Automotive > Fluids > Motor Oil | brand, base (full synthetic, synthetic blend, high mileage, conventional) and viscosity grade | jug size (ml; a 20 L drum for full synthetic and conventional) | viscosity grade, oil type |
| Coolant | Automotive > Fluids > Coolant | brand, chemistry (universal, extended life, hybrid, Asian, European, heavy duty, small engine) and form | jug size (ml) | coolant chemistry, fluid form |
| Jump Starter | Automotive > Electrics > Jump Starters | brand, build and peak current | one SKU | battery type, peak current |
| Tire Inflator | Automotive > Electrics > Tire Inflators | brand and build (digital auto-stop, cordless, dual power, battery clamp, mini) | one SKU | power source, maximum pressure (psi) |
| Phone Mount | Automotive > Electrics > Phone Mounts | brand, mount position and hold | pack size (single, 2 pack) | mount position, hold type |
| Car Charger | Automotive > Electrics > Car Chargers | brand, ports and output | pack size (single, 2 pack) | ports, power output (W) |

With slice 1 the templates hold 425 Automotive styles and 1,301 SKUs (Motor Oil 242, Coolant 132,
Jump Starter 47, Tire Inflator 20, Phone Mount 52, Car Charger 52). The new brands are invented
(`automotive_fluids_brand_styles.py`): Corvane (motor oil and coolant, mark `oil_can`), Ampwick
(mark `spark_bolt`) and Holtvane (mark `clamp_arc`) sell the electrics; Kestrova and Drayfield
come from slice 1. `max_pressure` and `power_output` reuse the names other types already give
those keys (`Maximum pressure (psi)`, `Power output (W)`, a bare number), so the catalogue has one
name per key.

All six types are `colorless`: a shopper picks an oil by its grade and a charger by its ports, not
by the color of the jug or the plastic, so each drawing takes the brand's pack color.

`kit_automotive_electrics.py` draws three new shapes, `jump_starter`, `tire_inflator` and
`phone_mount` (each `UPRIGHT`, in `orientations/automotive_electrics.py`). Motor oil and coolant reuse slice 1's `fluid_jug`;
a car charger reuses the electronics `charger` shape with `kind=car`. Each type carries two
text-match decoys (`automotive_fluids_rows.DECOY_ROWS`).

`tests/test_retail_automotive_fluids_970.py` holds slice 2's Done-when: the ceiling build holds at
least 1,250 SKUs under `Automotive`, each of the six types sits under its family, no Automotive
product id or SKU id repeats, the six types' templates are the same bytes on every build, and the
first style of each is pinned to `tests/data/retail_automotive_fluids_970_golden.json`. Slice 1's
golden test pins only its nine Car Care types, so a later slice does not move its fixture.

## Slice 3: interior, and two types moved from Home

Slice 3 adds the family `Automotive > Interior`: five types whose rows are in
`automotive_interior_rows.py` and whose spec files are in `type_specs/` (`seat_cover.py`,
`floor_mat.py`, `trunk_liner.py`, `steering_wheel_cover.py`, `sun_shade.py`).

| Type | Path | Style axis | SKU axis | Key attributes |
|---|---|---|---|---|
| Seat Cover | Automotive > Interior > Seat Covers | brand and material (neoprene, faux leather, mesh, canvas, faux sheepskin, rear bench, pet hammock) | color x set (front pair, full set; solid or 60/40 split bench; standard, XL) | material, seat cover type |
| Floor Mat | Automotive > Interior > Floor Mats | brand and build (all-weather rubber, trim-to-fit rubber, deep dish liner, carpet, premium carpet) | color x set (front pair, 4-piece set) | material, floor mat type |
| Trunk Liner | Automotive > Interior > Trunk Liners | brand and build (rubber tray, waterproof fabric, fabric with bumper flap) | color x vehicle size (sedan trunk, midsize SUV, full-size SUV) | material, liner type |
| Steering Wheel Cover | Automotive > Interior > Steering Wheel Covers | brand and material (faux leather, microfiber suede, silicone, sport grip) | color x rim size (standard, large) | material |
| Sun Shade | Automotive > Interior > Sun Shades | brand and build (accordion, reflective bubble, twist-fold, umbrella, side window) | size (standard, large, jumbo) or pack size | shade type |

Two existing types move out of `Home` (`decoy_word_kinds.py`, `footwear_rows.py` and their spec
files): Jump Leads to `Automotive > Electrics > Jump Leads`, beside the jump starters, and Car
Boot Organiser to `Automotive > Interior > Car Boot Organisers`, beside the trunk liners. Their
rows, brand and decoys are unchanged; only the department and the path move. The boots
distractor (`BOOTORG`) still answers no footwear word: it is now a car item instead of a Home one.

With slices 1 and 2 the templates hold 521 Automotive styles and 2,101 SKUs (Seat Cover 225, Floor
Mat 190, Trunk Liner 180, Steering Wheel Cover 148, Sun Shade 45, Car Boot Organiser 8, Jump Leads
4), above the issue's 1,900. No brand is new: Drayfield, Holtvane and Ostrel sell all five types,
and Kestrova also sells floor mats and trunk liners.

Seat covers, floor mats, trunk liners and steering wheel covers are sold by color, and each type
offers the six main colors (gen#275) across its styles. A rubber mat or tray comes in black, grey
and beige, the colors rubber mats are made in, and a faux sheepskin cover adds its natural cream. A
sun shade is `colorless`: its reflective face is what it is, so its drawing takes the brand's pack
color for the trim.

`kit_automotive_interior.py` draws five new shapes, `seat_cover` (bucket, bench), `floor_mat`
(rubber, carpet), `trunk_liner` (tray, fabric), `steering_wheel_cover` (stitched, grip) and
`sun_shade` (accordion, twist, umbrella, side), each `UPRIGHT` in
`orientations/automotive_interior.py`. Each type carries two text-match decoys
(`automotive_interior_rows.DECOY_ROWS`): a range name that holds the query words (class 6), and a
vocabulary or brand decoy (class 4 or 7).

`tests/test_retail_automotive_interior_970.py` holds the issue's Done-when: the ceiling build holds
at least 1,900 SKUs under `Automotive`, each new type sits under `Automotive > Interior`, the two
moved types sit under `Automotive`, no product id or SKU id repeats, the color-bearing types offer
the six main colors, each new type carries two decoys, the new types' templates are the same bytes
on every build, and the first style of each new type is pinned to
`tests/data/retail_automotive_interior_970_golden.json`.
