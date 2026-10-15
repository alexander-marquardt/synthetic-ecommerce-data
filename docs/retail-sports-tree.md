# Sports & Outdoors: the tree, its filters and what is not built (gen#290)

The department is built by `prototypes/retail_drawings/sports_rows.py` (gen#265, first increment,
PR #288). This note records, per leaf, what a shopper filters on and whether a reference
retailer's tree was compared; and, per type not yet built, where it is scheduled.
`tests/test_retail_sports_tree_note_290.py` keeps both tables equal to the rows: a new leaf
without a line here, or a line for a leaf that is gone, fails it.

## Leaves

The shape is department > family > (group) > leaf. The guidance on gen#265 asked for the shape of
large sports retailers' trees and for their leaves to be noted. **No leaf was checked against a
retailer's tree**: the author of the first increment had no tree to compare with, so the last
column reads `none` on every line rather than claiming a match. What does trace to a source is
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
| Sports & Outdoors > Yoga & Fitness > Weights > Kettlebells | weight, material, color | dumbbell weight | none |
| Sports & Outdoors > Yoga & Fitness > Foam Rollers | item_length, surface, material, color | none | none |

Leaf depth is mixed on purpose for now: Dome Tents, Tunnel Tents, Yoga Mats, Dumbbells and
Kettlebells sit under a group (four levels), Sleeping Bags, Camping Chairs and Foam Rollers sit
directly under their family (three). The Yoga group has one leaf until yoga blocks and straps
arrive (below), and a group with one leaf is kept rather than flattened so those leaves land
beside it. The tree guard's rules hold on the subtree either way.

## Not built

Every type the issue listed that the first increment did not ship has a disposition. "Not
reached" is not one: it is scope, not a reason. A type is either scheduled in an open issue or
carries a reason.

| Type | Family | Disposition |
| --- | --- | --- |
| Bicycles | Cycling | #352 |
| Bike helmets | Cycling | #352 |
| Bike lights | Cycling | #352 |
| Bike locks | Cycling | #352 |
| Bike pumps | Cycling | #368 |
| Camping stoves | Camping | #352 |
| Lanterns | Camping | #368 |
| Roll mats | Camping | #368 |
| Yoga blocks | Yoga & Fitness | #368 |
| Yoga straps | Yoga & Fitness | #368 |
| Resistance bands | Yoga & Fitness | #368 |
| Bats | Baseball | #368 |
| Gloves | Baseball | #368 |
| Balls | Baseball | #368 |
| Batting helmets | Baseball | #368 |
| Swimming goggles | Swimming | #368 |
| Swim caps | Swimming | #368 |
| Kickboards | Swimming | #368 |
| Armbands | Swimming | #368 |
| Footballs | Team and racket sports | #368 |
| Tennis rackets | Team and racket sports | #368 |
| Badminton sets | Team and racket sports | #368 |
| Kayaks | Water sports | #352 |
| Kick scooters | Wheeled sports | #352 |
| Skateboards | Wheeled sports | #352 |
| Swimsuits and trunks | Swimming | Clothing already has them: reused, not duplicated (gen#265) |
| Balance bikes | Cycling | Stay in Toys (gen#265) |
