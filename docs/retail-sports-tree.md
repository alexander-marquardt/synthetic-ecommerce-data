# Sports & Outdoors: the tree, its filters and what is not built (gen#290)

The department is built from one spec file per type in `src/synthetic_ecommerce_data/domains/retail/type_specs/`
(gen#265, first increment, PR #288, moved there by gen#455; `sports_rows.py` lists their rows; the remainder, gen#368, adds seventeen types: yoga blocks, straps and bands, lanterns,
roll mats, bike pumps, baseball, swimming, team and racket sports; gen#352 adds bicycles, bike
helmets, kayaks, kick scooters and skateboards, in three new families: Cycling's bikes and
helmets, Water Sports and Wheeled Sports; gen#625 numbers the bikes and adds four cycling
accessories: chain lube, bike bottles, bike saddles and bike pedals). This note records, per leaf,
what a shopper filters on and whether a reference retailer's tree was compared; and, per type not
yet built, where it is scheduled.
`tests/test_retail_sports_tree_note_290.py` keeps both tables equal to the rows: a new leaf
without a line here, or a line for a leaf that is gone, fails it.

## Leaves

The shape is department > family > (group) > leaf. The guidance on gen#265 asked for the shape of
large sports retailers' trees and for their leaves to be noted. **No leaf was compared with a
retailer's tree** (not compared, which is not the same as no mapping existing): the last column
reads `none` on every line rather than claiming a match. A comparison, when made, is written
`compared with <tree> (<page url>, <YYYY-MM-DD>)`; `tests/test_retail_sports_tree_note_290.py`
refuses any other verdict. What does trace to a source is
the filter: the guidance on gen#265 named tent capacity and season rating (camping), mat
thickness (yoga) and weight (dumbbells), and those leaves carry them. A leaf whose filters have
no guidance example says `none` there too.

| Leaf | Filters (export keys) | Guidance example | Retailer tree |
| --- | --- | --- | --- |
| Sports & Outdoors > Camping > Tents > Dome Tents | berth, season_rating, hydrostatic_head, tent_type, material, color | tent capacity, season rating | none |
| Sports & Outdoors > Camping > Tents > Tunnel Tents | berth, season_rating, hydrostatic_head, tent_type, material, color | tent capacity, season rating | none |
| Sports & Outdoors > Camping > Sleeping Bags | season_rating, item_length, bag_shape, fill, material, color | season rating | none |
| Sports & Outdoors > Camping > Camping Chairs | frame_material, max_load_kg, arms, color | none | none |
| Sports & Outdoors > Yoga & Fitness > Yoga > Yoga Mats | thickness, material, surface, color | mat thickness | none |
| Sports & Outdoors > Yoga & Fitness > Weights > Dumbbells | weight, head_shape, sold_as, material, color | dumbbell weight | none |
| Sports & Outdoors > Yoga & Fitness > Weights > Kettlebells | weight, material, color | none | none |
| Sports & Outdoors > Yoga & Fitness > Foam Rollers | item_length, surface, material, color | none | none |
| Sports & Outdoors > Camping > Lanterns | power, brightness, material, color | none | none |
| Sports & Outdoors > Camping > Picnic Blankets | waterproof_backing, dimensions, material, color | none | none |
| Sports & Outdoors > Camping > Roll Mats | thickness, fold, material, color | none | none |
| Sports & Outdoors > Yoga & Fitness > Yoga > Yoga Blocks | item_height, sold_as, material, color | none | none |
| Sports & Outdoors > Yoga & Fitness > Yoga > Yoga Straps | item_length, closure, material, color | none | none |
| Sports & Outdoors > Yoga & Fitness > Resistance Bands | resistance_level, band_type, material, color | none | none |
| Sports & Outdoors > Cycling > Bike Pumps | pump_type, valve_type, max_pressure, color | none | none |
| Sports & Outdoors > Baseball > Baseball Bats | item_length, material, barrel_diameter, color | none | none |
| Sports & Outdoors > Baseball > Baseball Gloves | glove_size, position, material, color | none | none |
| Sports & Outdoors > Baseball > Baseballs | cover, level, sold_as, color | none | none |
| Sports & Outdoors > Baseball > Batting Helmets | head_circumference, ear_flaps, material, color | none | none |
| Sports & Outdoors > Swimming > Swimming Goggles | lens, anti_fog, strap_material, color | none | none |
| Sports & Outdoors > Swimming > Swim Caps | material, latex_free, color | none | none |
| Sports & Outdoors > Swimming > Kickboards | item_length, grips, material, color | none | none |
| Sports & Outdoors > Swimming > Swim Armbands | max_load_kg, chambers, material, color | none | none |
| Sports & Outdoors > Team & Racket Sports > Footballs | ball_size, cover, construction, color | none | none |
| Sports & Outdoors > Team & Racket Sports > Tennis Rackets | grip_size, head_size, material, color | none | none |
| Sports & Outdoors > Team & Racket Sports > Badminton Sets | players, net_included, material, color | none | none |
| Sports & Outdoors > Cycling > Bikes > Road Bikes | bike_type, frame_material, gears, wheel_size, brake_type, frame_size, color | none | none |
| Sports & Outdoors > Cycling > Bikes > Mountain Bikes | bike_type, frame_material, gears, wheel_size, brake_type, frame_size, color | none | none |
| Sports & Outdoors > Cycling > Bikes > Electric Bikes | bike_type, frame_material, gears, wheel_size, brake_type, frame_size, color | none | none |
| Sports & Outdoors > Cycling > Bikes > Kids Bikes | bike_type, frame_material, gears, brake_type, wheel_size, color | none | none |
| Sports & Outdoors > Cycling > Bike Helmets | helmet_type, impact_protection, visor, size, color | none | none |
| Sports & Outdoors > Cycling > Chain Lube | lube_type, application, volume, color | none | none |
| Sports & Outdoors > Cycling > Bike Bottles | bottle_type, insulated, capacity, color | none | none |
| Sports & Outdoors > Cycling > Bike Saddles | saddle_type, padding, color | none | none |
| Sports & Outdoors > Cycling > Bike Pedals | pedal_type, material, color | none | none |
| Sports & Outdoors > Water Sports > Kayaks > Sit-on-Top Kayaks | kayak_type, seats, max_load_kg, material, item_length, color | none | none |
| Sports & Outdoors > Water Sports > Kayaks > Inflatable Kayaks | kayak_type, seats, max_load_kg, material, item_length, color | none | none |
| Sports & Outdoors > Wheeled Sports > Kick Scooters | scooter_type, wheel_size, max_load_kg, folds, color | none | none |
| Sports & Outdoors > Wheeled Sports > Skateboards | board_type, material, deck_width, color | none | none |

Leaf depth is mixed on purpose for now: Dome Tents, Tunnel Tents, Yoga Mats, Yoga Blocks, Yoga
Straps, Dumbbells, Kettlebells, the four Bikes leaves and the two Kayaks leaves sit under a group (four levels); the other leaves sit directly under
their family (three). The Yoga group now holds three leaves (mats, blocks and straps). The tree
guard's rules hold on the subtree either way.

## Bicycle model numbers and accessory decoys (gen#625)

Each bicycle title leads with its brand, its series and its model number, then the spec and the
bike: `Wrenfield Aero Elite RD28-22-26 28in 22 Speed Carbon Road Bike`, the title order of the
large appliances (gen#622). `src/synthetic_ecommerce_data/domains/retail/bicycle_model_numbers.py` holds each
brand's scheme and series. A code is built from the kind, the wheel inches, the gears and the
model year, and `decode` reads it back. The model number and the model year are attributes, the
series is exported as `series`, and every SKU carries its bike's code. The frame size (a kids'
bike's wheel size) is the SKU axis, so it is not part of the code: one code is one product.

The bike titles are long, so a plain text match for `bicycle` or `bike` ranks short accessory
titles above them: Bicycle Helmet, Bicycle Seat, Bicycle Water Bottle, Bicycle Chain Lube, Bike
Pedals and so on. Each is a real product of its own type in its own Cycling leaf, and
`kit_cycling.py` draws it. `tests/test_retail_bicycle_model_numbers_625.py` holds the scheme, the
rows and that ranking.

## A code-built bicycle range (gen#685)

`type_specs/bicycle.py` builds the bikes from a table of axes rather than listing them. Each of
the four kinds (Road, Mountain, Electric, Kids) has its trims: gears, wheel size, frame material
and brake. Road, Mountain and Electric have two trims each, and Kids has one. All three brands sell
every trim. For each trim, one brand in turn still sells last year's model (2025). That gives 21
bikes, and no two share brand, kind, gears, wheel and year. The build raises if two bikes ever do,
or if two share a code. Each bike keeps four colors times three frame sizes (three wheel sizes for a
kids' bike), so it has twelve SKUs and four images.

The price follows from the parts. The kind sets a base, and the frame material (steel, aluminum,
carbon), the brake (coaster, rim, disc) and each extra gear add to it. Last year's model sells at
85%, and the brand adds nothing. `tests/test_retail_bicycle_range_685.py` holds the count, the
round trip of every code, the unique axes and the price rules.

## Not built

Every type the issue listed that neither increment has shipped has a disposition. "Not
reached" is not one: it is scope, not a reason. A type is either scheduled in an open issue or
carries a reason.

| Type | Family | Disposition |
| --- | --- | --- |
| Bike lights | Cycling | Optional in #352 ("if cheap"), left out to hold the range to the listed types (gen#352) |
| Bike locks | Cycling | Optional in #352 ("if cheap"), left out to hold the range to the listed types (gen#352) |
| Camping stoves | Camping | Optional in #352 ("if cheap"), left out to hold the range to the listed types (gen#352) |
| Swimsuits and trunks | Swimming | Clothing already has them: reused, not duplicated (gen#265) |
| Balance bikes | Cycling | Stay in Toys (gen#265) |
