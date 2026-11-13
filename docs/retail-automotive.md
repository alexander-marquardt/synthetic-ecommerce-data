# Retail Automotive: car care (gen#970, slice 1)

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
| Wiper Blade | Automotive > Car Care > Wiper Blades | brand, blade type (conventional, beam, hybrid, rear, winter) | blade length (in) | blade type, connector, season, wiper position |
| Car Air Freshener | Automotive > Car Care > Car Air Fresheners | brand, format and fragrance | pack size | freshener format, fragrance |
| Wash Mitt | Automotive > Car Care > Wash Mitts | brand and material | size | material |
| Microfiber Towel | Automotive > Car Care > Microfiber Towels | brand and towel type | dimensions | material, towel type |

The templates hold 194 styles and 692 SKUs. Every brand is invented (`automotive_brand_styles.py`:
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
