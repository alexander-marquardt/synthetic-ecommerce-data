# Retail Automotive: car care, fluids and electrics (gen#970, slices 1 and 2)

The retail catalogue had no `Automotive` department: `core/departments.RETAIL` did not list it and
no `category_path` started with it. gen#970 adds it in three slices of about 2,000 SKUs in all
(`docs/catalogue-mix-837.md`). Slice 1 adds the department and its first family,
`Automotive > Car Care`: nine types whose rows are in `automotive_rows.py` and whose spec files are
in `type_specs/` (`car_shampoo.py` to `microfiber_towel.py`). Slices 2 (fluids and electrics) and 3
(interior, and the move of Jump Leads and Car Boot Organiser from `Home`) follow.

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
`phone_mount` (each on `orientation.UPRIGHT`). Motor oil and coolant reuse slice 1's `fluid_jug`;
a car charger reuses the electronics `charger` shape with `kind=car`. Each type carries two
text-match decoys (`automotive_fluids_rows.DECOY_ROWS`).

`tests/test_retail_automotive_fluids_970.py` holds slice 2's Done-when: the ceiling build holds at
least 1,250 SKUs under `Automotive`, each of the six types sits under its family, no Automotive
product id or SKU id repeats, the six types' templates are the same bytes on every build, and the
first style of each is pinned to `tests/data/retail_automotive_fluids_970_golden.json`. Slice 1's
golden test pins only its nine Car Care types, so a later slice does not move its fixture.
