# Sports & Outdoors: the tree, its filters and what is not built (gen#290)

The department is built by `prototypes/retail_drawings/sports_rows.py` (gen#265, first increment,
PR #288; the remainder, gen#368, adds seventeen types: yoga blocks, straps and bands, lanterns,
roll mats, bike pumps, baseball, swimming, team and racket sports). This note records, per leaf,
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

Leaf depth is mixed on purpose for now: Dome Tents, Tunnel Tents, Yoga Mats, Yoga Blocks, Yoga
Straps, Dumbbells, Kettlebells sit under a group (four levels); the other leaves sit directly under
their family (three). The Yoga group now holds three leaves (mats, blocks and straps). The tree
guard's rules hold on the subtree either way.

## Not built

Every type the issue listed that neither increment has shipped has a disposition. "Not
reached" is not one: it is scope, not a reason. A type is either scheduled in an open issue or
carries a reason.

| Type | Family | Disposition |
| --- | --- | --- |
| Bicycles | Cycling | #352 |
| Bike helmets | Cycling | #352 |
| Bike lights | Cycling | #352 |
| Bike locks | Cycling | #352 |
| Camping stoves | Camping | #352 |
| Kayaks | Water sports | #352 |
| Kick scooters | Wheeled sports | #352 |
| Skateboards | Wheeled sports | #352 |
| Swimsuits and trunks | Swimming | Clothing already has them: reused, not duplicated (gen#265) |
| Balance bikes | Cycling | Stay in Toys (gen#265) |
